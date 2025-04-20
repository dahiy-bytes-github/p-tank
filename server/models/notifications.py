from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func
from database import db

class Notification(db.Model, SerializerMixin):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # info, warning, critical
    notification_type = db.Column(db.String(50), nullable=False)  # ph_anomaly, temp_anomaly, tank_full
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # Relationship to UserNotification
    user_notifications = db.relationship('UserNotification', back_populates='notification', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Notification id={self.id}, type={self.notification_type}, severity={self.severity}>"