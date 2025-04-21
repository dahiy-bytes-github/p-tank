import re
from email.mime.text import MIMEText
import smtplib
from flask import Flask
from models import User, Notification, UserNotification

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def send_email_alert(message, recipient_email, sender_email, sender_password):
    """
    Send email alerts to users with critical notifications
    In a real app, this would use an email service like SendGrid or SMTP
    """
    try:
        msg = MIMEText(message)
        msg['Subject'] = "Critical Tank Alert"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        print(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
def check_tank_conditions(sensor_reading, app, db):
    """Check sensor readings and create notifications if critical conditions are met"""
    critical_notification = False
    notification_message = ""
    notification_type = ""

    # Check tank level
    if sensor_reading.tank_level_per > 90:
        critical_notification = True
        notification_type = "tank_level_high"
        notification_message = f"Tank level is at {sensor_reading.tank_level_per}%, approaching capacity"

    # Check if tank is predicted to be full
    if sensor_reading.predicted_full:
        critical_notification = True
        notification_type = "tank_full_predicted"
        notification_message = "Tank is predicted to reach full capacity soon"

    # If critical conditions were met, create notification
    if critical_notification:
        # Create the notification
        with app.app_context():
            notification = Notification(
                message=notification_message,
                severity="critical",
                notification_type=notification_type
            )
            db.session.add(notification)
            db.session.flush()  # To get the notification ID

            # Add notification for all users and send emails to those who opted in
            users = User.query.all()
            for user in users:
                # Create user notification
                user_notification = UserNotification(
                    user_id=user.id,
                    notification_id=notification.id
                )
                db.session.add(user_notification)

                # Send email alert if user has enabled them
                if user.receive_email_alerts:
                  sender_email = app.config['MAIL_USERNAME']
                  sender_password = app.config['MAIL_PASSWORD']
                  send_email_alert(notification_message, user.email, sender_email, sender_password)

            db.session.commit()
