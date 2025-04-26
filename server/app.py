from flask import Flask, request, jsonify
from flask_restful import Api, Resource
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
# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced CORS configuration
CORS(
    app,
    origins=["http://localhost:3000"],
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

# ✅ Allow JWTs via headers and query string
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


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "error": "authorization_required",
        "message": "Request does not contain an access token"
    }), 401

# Create admin user if not exists
def create_admin():
    with app.app_context():
        existing_admin = User.query.filter_by(role='Admin').first()
        if not existing_admin:
            admin = User(
                full_name='Admin User',
                email='admin@example.com',
                role='Admin'
            )
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")

create_admin()

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
            return {"message": "Already logged out"}, 200  # ✅ Return success
        
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
        if role and role in ['Admin', 'User', 'Mentor', 'Mentee']:
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
                # REMOVE predicted_full
                # "predicted_full": new_reading.predicted_full
            }
        }, 201


class UserNotifications(Resource):
    @jwt_required()
    def get(self):
        # Get current user identity
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        # Query all notifications for this user
        user_notifications = (
            UserNotification.query
            .join(Notification)
            .filter(UserNotification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .all()
        )
        
        # Format the response
        notifications_data = []
        for un in user_notifications:
            notification = un.notification
            notifications_data.append({
                "id": un.id,
                "notification_id": notification.id,
                "message": notification.message,
                "severity": notification.severity,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat(),
                "is_read": un.is_read,
                "read_at": un.read_at.isoformat() if un.read_at else None
            })
        
        return {
            "message": "Notifications retrieved successfully",
            "notifications": notifications_data,
            "count": len(notifications_data)
        }, 200

class MarkNotificationRead(Resource):
    @jwt_required()
    def patch(self, notification_id):
        # Get current user identity
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        # Query the user notification
        user_notification = UserNotification.query.filter_by(
            id=notification_id,
            user_id=user.id
        ).first()
        
        if not user_notification:
            return {"error": "Notification not found"}, 404
        
        # Mark as read
        if not user_notification.is_read:
            user_notification.is_read = True
            user_notification.read_at = func.now()
            db.session.commit()
        
        return {"message": "Notification marked as read"}, 200

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

class ToggleEmailAlerts(Resource):
    @jwt_required()
    def patch(self):
        # Get current user identity
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        # Toggle the setting
        user.receive_email_alerts = not user.receive_email_alerts
        db.session.commit()
        
        return {
            "message": f"Email alerts {'enabled' if user.receive_email_alerts else 'disabled'}",
            "receive_email_alerts": user.receive_email_alerts
        }, 200
class PredictTankFull(Resource):
    def get(self):
        # Simulate a prediction
        current_level = round(random.uniform(60, 95), 2)  # Random tank level
        fill_rate_per_hour = round(random.uniform(0.1, 0.5), 2)  # Random fill rate

        # Calculate time until full and estimated full time
        hours_until_full = (100 - current_level) / fill_rate_per_hour
        estimated_full_time = datetime.now() + timedelta(hours=hours_until_full)

        return {
            "current_level": current_level,
            "fill_rate_per_hour": fill_rate_per_hour,
            "hours_until_full": hours_until_full,
            "estimated_full_time": estimated_full_time.isoformat(),
            "message": "Simulated prediction"
        }, 200
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
api.add_resource(MarkNotificationRead, '/notifications/<int:notification_id>/read')
api.add_resource(UnreadNotificationsCount, '/notifications/unread-count')
api.add_resource(ToggleEmailAlerts, '/user/toggle-email-alerts')
api.add_resource(PredictTankFull, '/predict-tank-full')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
