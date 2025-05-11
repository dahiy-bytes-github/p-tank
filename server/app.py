from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
    get_jwt,
)
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import timedelta
from sqlalchemy.sql import func
from models import User
from models import SensorReading
from models import Notification
from models import UserNotification

from database import db
import random 
from datetime import datetime, timedelta
from utils import is_valid_email, send_email_alert, check_tank_conditions, init_mail
from predictor import TankPredictor
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced CORS configuration
CORS(
    app,
    origins="*",
    supports_credentials=True,
    methods=["GET", "POST", "PUT","PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF for token auth
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Allow JWTs via headers and query string
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['JWT_QUERY_STRING_NAME'] = 'jwt'  # optional, default is already 'jwt'
app.json.compact = False

# Email Configuration
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com') #set default value
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465)) #set default value and convert to int
app.config['MAIL_USE_SSL'] = True # force to True, since we are using 465
app.config['MAIL_USE_TLS'] = False # force to False, since we are using 465


# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
jwt = JWTManager(app)

# Initialize Flask-Mail
mail = init_mail(app)  # Initialize flask-mail here
predictor = TankPredictor()


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "error": "authorization_required",
        "message": "Request does not contain an access token"
    }), 401


# JWT token blocklist (for logout)
blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist

class Register(Resource):
    def post(self):
        data = request.get_json()
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([full_name, email, password]):
            return {
                "error": "All fields are required",
                "missing": [
                    field for field in ['full_name', 'email', 'password'] 
                    if not data.get(field)
                ]
            }, 400

        if not is_valid_email(email):
            return {"error": "Invalid email format"}, 400

        if User.query.filter((User.full_name == full_name) | (User.email == email)).first():
            return {
                "error": "User already exists",
                "conflicts": [
                    *(['full_name'] if User.query.filter_by(full_name=full_name).first() else []),
                    *(['email'] if User.query.filter_by(email=email).first() else [])
                ]
            }, 409

        new_user = User(full_name=full_name, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "full_name": new_user.full_name,
                "email": new_user.email,
                "role": new_user.role
            }
        }, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {"error": "Email and password are required."}, 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {"error": "Invalid email or password."}, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role
            }
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role
            }
        )

        return {
            "message": "Login successful.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role
            }
        }, 200


class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        if jti in blacklist:
            return {"message": "Already logged out"}, 200
        
        blacklist.add(jti)
        return {"message": "Successfully logged out"}, 200


class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        claims = get_jwt()

        new_token = create_access_token(
            identity=user_id,
            additional_claims={
                "email": claims.get("email"),
                "role": claims.get("role")
            }
        )
        return {"access_token": new_token}, 200

class Protected(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return {"error": "User not found."}, 404

        return {
            "message": "Protected endpoint",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role
            }
        }, 200

class UsersList(Resource):
    @jwt_required()
    def get(self):
        # Get current user identity from JWT
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        # Check if user exists and is admin
        if not current_user:
            return {"error": "User not found"}, 404
            
        if current_user.role != 'Admin':
            return {"error": "Admin privileges required"}, 403
        
        # Get all users from database
        users = User.query.all()
        
        # Prepare response data
        users_data = [{
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        } for user in users]
        
        return {
            "message": "Users retrieved successfully",
            "users": users_data,
            "count": len(users_data)
        }, 200
class UserUpdateDelete(Resource):
    @jwt_required()
    def put(self, user_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user or current_user.role != 'Admin':
            return {"error": "Admin privileges required"}, 403

        user = User.query.get(int(user_id))
        if not user:
            return {"error": "User not found"}, 404

        data = request.get_json()
        full_name = data.get('full_name')
        email = data.get('email')
        role = data.get('role')
        password = data.get('password')

        if full_name:
            user.full_name = full_name
        if email:
            if not is_valid_email(email):
                return {"error": "Invalid email format"}, 400
            if User.query.filter(User.email == email, User.id != user.id).first():
                return {"error": "Email already in use"}, 409
            user.email = email
        if role:
            if role not in ['Admin', 'Normal']:
                return {"error": "Invalid role. Must be 'Admin' or 'Normal'"}, 400
            user.role = role
        if password:
            user.set_password(password)

        db.session.commit()

        return {
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role
            }
        }, 200

    @jwt_required()
    def delete(self, user_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))

        if not current_user or current_user.role != 'Admin':
            return {"error": "Admin privileges required"}, 403

        if int(current_user_id) == int(user_id):
            return {"error": "Cannot delete yourself"}, 400

        user = User.query.get(int(user_id))
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted successfully"}, 200

class SensorReadings(Resource):
    def get(self):
        # Get all possible filters
        filters = {
            'temp': request.args.get('temp', type=float),
            'ph': request.args.get('ph', type=float),
            'tank_level_min': request.args.get('tank_level_min', type=float),
            'tank_level_max': request.args.get('tank_level_max', type=float),
            # REMOVE predicted_full
            #'predicted_full': request.args.get('predicted_full', type=lambda x: x.lower() == 'true'),
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date')
        }

        # Start building query
        query = SensorReading.query

        # Apply filters
        if filters['temp']:
            query = query.filter(SensorReading.temp == filters['temp'])

        if filters['ph']:
            query = query.filter(SensorReading.ph == filters['ph'])

        if filters['tank_level_min']:
            query = query.filter(SensorReading.tank_level_per >= filters['tank_level_min'])

        if filters['tank_level_max']:
            query = query.filter(SensorReading.tank_level_per <= filters['tank_level_max'])

        # REMOVE predicted_full filter condition
        #if filters['predicted_full'] is not None:  # Explicit check for boolean
        #    query = query.filter(SensorReading.predicted_full == filters['predicted_full'])

        if filters['start_date']:
            query = query.filter(SensorReading.timestamp >= filters['start_date'])

        if filters['end_date']:
            query = query.filter(SensorReading.timestamp <= filters['end_date'])

        # Paginate and return
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 100)

        readings = query.order_by(SensorReading.timestamp.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )

        return {
            "readings": [
                {
                    "id": reading.id,
                    "timestamp": reading.timestamp.isoformat(),
                    "temp": reading.temp,
                    "ph": reading.ph,
                    "tank_level_per": reading.tank_level_per,
                    # REMOVE predicted_full from output
                    #"predicted_full": reading.predicted_full
                } for reading in readings.items],
            "pagination": {
                "page": page,
                "limit": limit,
                "total_pages": readings.pages,
                "total_items": readings.total
            }
        }, 200

class CreateSensorReading(Resource):
    def post(self):
        data = request.get_json()

        new_reading = SensorReading(
            temp=data.get('temp'),
            ph=data.get('ph'),
            tank_level_per=data.get('tank_level_per')
        )

        db.session.add(new_reading)
        db.session.commit()

        check_tank_conditions(new_reading, app, db)  # Call check_tank_conditions

        return {
            "message": "Sensor reading created successfully",
            "reading": {
                "id": new_reading.id,
                "timestamp": new_reading.timestamp.isoformat(),
                "temp": new_reading.temp,
                "ph": new_reading.ph,
                "tank_level_per": new_reading.tank_level_per,
            }
        }, 201


class UserNotifications(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        user_notifications = (
            UserNotification.query
            .join(Notification)
            .filter(UserNotification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .all()
        )
        
        notifications_data = []
        for un in user_notifications:
            notifications_data.append({
                "user_notification_id": un.id,  # Join table ID
                "notification_id": un.notification.id,
                "message": un.notification.message,
                "severity": un.notification.severity,
                "notification_type": un.notification.notification_type,
                "created_at": un.notification.created_at.isoformat(),
                "is_read": un.is_read,
                "read_at": un.read_at.isoformat() if un.read_at else None
            })
        
        return {
            "message": "Notifications retrieved successfully",
            "notifications": notifications_data
        }, 200

class MarkNotificationRead(Resource):
    @jwt_required()
    def patch(self, user_notification_id):  # Changed parameter name
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        user_notification = UserNotification.query.filter_by(
            id=user_notification_id,  # Using join table ID
            user_id=user.id
        ).first()
        
        if not user_notification:
            return {"error": "User notification not found"}, 404
        
        if not user_notification.is_read:
            user_notification.is_read = True
            user_notification.read_at = func.now()
            db.session.commit()
        
        return jsonify({
            "success": True,
            "user_notification_id": user_notification.id,
            "is_read": user_notification.is_read,
            "read_at": user_notification.read_at.isoformat() if user_notification.read_at else None
        })

class UnreadNotificationsCount(Resource):
    @jwt_required()
    def get(self):
        # Get current user identity
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        # Count unread notifications
        unread_count = (
            UserNotification.query
            .filter_by(user_id=user.id, is_read=False)
            .count()
        )
        
        return {
            "message": "Unread notifications count retrieved",
            "unread_count": unread_count
        }, 200
class MarkAllNotificationsRead(Resource):
    @jwt_required()
    def patch(self):
        # Get current user identity
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        try:
            # Get current timestamp
            current_time = func.now()
            
            # Update all unread notifications for this user
            updated = UserNotification.query.filter_by(
                user_id=user.id,
                is_read=False
            ).update({
                'is_read': True,
                'read_at': current_time
            })
            
            db.session.commit()
            
            return {
                "success": True,
                "message": f"Marked {updated} notifications as read",
                "marked_read": updated
            }, 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Database error"}, 500
class UserEmailAlerts(Resource):
    @jwt_required()
    def get(self):
        """Get current email alert preference"""
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        return {
            "receive_email_alerts": user.receive_email_alerts
        }, 200

    @jwt_required()
    def patch(self):
        """Toggle email alert preference"""
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        user.receive_email_alerts = not user.receive_email_alerts
        db.session.commit()
        
        return {
            "message": f"Email alerts {'enabled' if user.receive_email_alerts else 'disabled'}",
            "receive_email_alerts": user.receive_email_alerts
        }, 200

class UserNotificationsWithStatus(Resource):
    @jwt_required()
    def get(self):
        """
        Get all notifications with clear read/unread status
        Returns:
            - List of notifications with explicit status
            - Visual status indicators in response
            - Last read timestamp
        """
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=50, help='Limit results')
        args = parser.parse_args()

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        try:
            # Get both read and unread notifications
            notifications = db.session.query(
                Notification,
                UserNotification.is_read,
                UserNotification.read_at
            ).join(
                UserNotification,
                Notification.id == UserNotification.notification_id
            ).filter(
                UserNotification.user_id == user.id
            ).order_by(
                desc(Notification.created_at)
            ).limit(args['limit']).all()

            # Format response with explicit status
            notifications_data = []
            for notif, is_read, read_at in notifications:
                status = "read" if is_read else "unread"
                notifications_data.append({
                    "id": notif.id,
                    "message": notif.message,
                    "type": notif.notification_type,
                    "severity": notif.severity,
                    "created_at": notif.created_at.isoformat(),
                    "status": status,  # Explicit status field
                    "status_icon": "✓" if is_read else "✕",  # Visual indicator
                    "status_class": f"status-{status}",  # For CSS styling
                    "read_at": read_at.isoformat() if read_at else None,
                    "is_read": is_read  # Boolean flag for easy filtering
                })

            # Add summary stats
            unread_count = sum(1 for n in notifications if not n[1])
            
            return {
                "success": True,
                "notifications": notifications_data,
                "stats": {
                    "total": len(notifications),
                    "unread": unread_count,
                    "read": len(notifications) - unread_count
                }
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500
        
class AllNotificationsWithStatus(Resource):
    @jwt_required()
    def get(self):
        # Get current user and check admin privileges
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        if not current_user or current_user.role != 'Admin':
            return {"error": "Admin privileges required"}, 403

        # Query all UserNotifications, joining with User and Notification
        all_user_notifications = (
            db.session.query(UserNotification, User, Notification)
            .join(User, UserNotification.user_id == User.id)
            .join(Notification, UserNotification.notification_id == Notification.id)
            .order_by(Notification.created_at.desc())
            .all()
        )

        # Format response
        notifications_data = []
        for un, user, notification in all_user_notifications:
            notifications_data.append({
                "user_id": user.id,
                "user_email": user.email,
                "notification_id": notification.id,
                "message": notification.message,
                "severity": notification.severity,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat(),
                "is_read": un.is_read,
                "read_at": un.read_at.isoformat() if un.read_at else None
            })

        return {
            "message": "All notifications with user read status retrieved successfully",
            "notifications": notifications_data,
            "count": len(notifications_data)
        }, 200
class PredictionResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('sensor_cm', type=float, required=True,
                              help='Current sensor reading in cm (22-27)')
        
    def get(self):
        """GET endpoint for testing with query parameters"""
        args = self.parser.parse_args()
        return self._make_prediction(args['sensor_cm'])
    
    def post(self):
        """POST endpoint for regular JSON payloads"""
        data = request.get_json()
        if not data or 'sensor_cm' not in data:
            return {"error": "JSON body with sensor_cm required"}, 400
        return self._make_prediction(data['sensor_cm'])
    
    def _make_prediction(self, sensor_cm):
        """Shared prediction logic"""
        try:
            if not 22.0 <= sensor_cm <= 27.0:
                return {"error": "Invalid reading (must be 22-27cm)"}, 400
            
            current_level = predictor.calculate_level(sensor_cm)
            result = predictor.predict_critical(sensor_cm)
            
            return {
                "status": "success",
                "data": {
                    "current_level": current_level,
                    "prediction": result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "model_version": "1.1"
                }
            }
        except Exception as e:
            return {"error": str(e)}, 500

# Add resources
api.add_resource(Register, '/auth/register')
api.add_resource(Login, '/auth/login')
api.add_resource(Logout, '/auth/logout')
api.add_resource(RefreshToken, '/auth/refresh')
api.add_resource(Protected, '/protected')
api.add_resource(UsersList, '/users')
api.add_resource(UserUpdateDelete, '/users/<int:user_id>')
api.add_resource(SensorReadings, '/sensorreadings')
api.add_resource(CreateSensorReading, '/sensor-readings')
api.add_resource(UserNotifications, '/notifications')
api.add_resource(MarkNotificationRead, '/notifications/<int:user_notification_id>/read') 
api.add_resource(UnreadNotificationsCount, '/notifications/unread-count')
api.add_resource(MarkAllNotificationsRead, '/notifications/read-all')
api.add_resource(UserNotificationsWithStatus, '/user/notifications/status')
api.add_resource(UserEmailAlerts, '/user/email-alerts')
api.add_resource(AllNotificationsWithStatus, '/notifications/all')
api.add_resource(PredictionResource, '/predict')


if __name__ == '__main__':
    app.run()