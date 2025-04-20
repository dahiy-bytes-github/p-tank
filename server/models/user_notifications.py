from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func
from database import db

class UserNotification(db.Model, SerializerMixin):
    __tablename__ = 'user_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='notifications')
    notification = db.relationship('Notification', back_populates='user_notifications')

    def __repr__(self):
        return f"<UserNotification user_id={self.user_id}, notification_id={self.notification_id}, is_read={self.is_read}>"