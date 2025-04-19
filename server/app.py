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
from models import User
from database import db
from utils import is_valid_email

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced CORS configuration
CORS(
    app,
    origins=["http://localhost:3000"],
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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


# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
jwt = JWTManager(app)

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
        print(request.headers)  # For debugging
        jti = get_jwt()['jti']
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
# Add resources
api.add_resource(Register, '/auth/register')
api.add_resource(Login, '/auth/login')
api.add_resource(Logout, '/auth/logout')
api.add_resource(RefreshToken, '/auth/refresh')
api.add_resource(Protected, '/protected')
api.add_resource(UsersList, '/users')
api.add_resource(UserUpdateDelete, '/users/<int:user_id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)