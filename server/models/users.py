from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, SerializerMixin):
     __tablename__ = 'users'

     id = db.Column(db.Integer, primary_key=True) 
     full_name = db.Column(db.String(50), nullable=False)  # removed unique=True
     email = db.Column(db.String(100), unique=True, nullable=False)
     password_hash = db.Column(db.Text, nullable=False)
     role = db.Column(db.String(20), default='Normal')
     receive_email_alerts = db.Column(db.Boolean, default=True)
     created_at = db.Column(db.DateTime, server_default=func.now())

     # Relationship to UserNotification
     notifications = db.relationship('UserNotification', back_populates='user', cascade='all, delete-orphan')

    # Password hashing
     def set_password(self, password):
        self.password_hash = generate_password_hash(password)

     def check_password(self, password):
        return check_password_hash(self.password_hash, password)

     def __repr__(self):
       return f"<User {self.full_name}, Role: {self.role}>"
