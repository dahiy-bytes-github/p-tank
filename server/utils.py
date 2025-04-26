import re
import smtplib
from email.mime.text import MIMEText
from flask import current_app as app
from flask_mail import Mail

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def send_email_alert(message, recipient_email):
    """
    Send email alerts to users with critical notifications.
    Reads SMTP settings (server, port, username, password) from app.config
    and logs each step for debugging.
    """
    server   = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
    port     = int(app.config.get('MAIL_PORT', 465))
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']

    print("[DEBUG] MAIL_USERNAME:", username)
    print("[DEBUG] MAIL_PASSWORD starts with:", password[:4])

    print(f"[send_email_alert] Connecting to {server}:{port}")
    msg = MIMEText(message)
    msg['Subject'] = app.config.get('MAIL_SUBJECT', 'Critical Tank Alert')
    msg['From']    = username
    msg['To']      = recipient_email

    try:
        # Use SMTP_SSL directly; no TLS needed for port 465
        smtp = smtplib.SMTP_SSL(server, port, timeout=10)

        print("[send_email_alert] Logging in…")
        with smtp:
            smtp.login(username, password)
            print(f"[send_email_alert] Logged in as {username}, sending to {recipient_email}…")
            smtp.send_message(msg)

        print(f"[send_email_alert] Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        print(f"[send_email_alert] Error sending email to {recipient_email}: {e!r}")
        return False

def check_tank_conditions(sensor_reading, app, db):
    """
    Check sensor readings and create/send notifications if critical conditions are met.
    (Only checks tank_level_per since predicted_full is no longer a column.)
    """
    # 1) Determine if we have a critical condition
    if sensor_reading.tank_level_per <= 90:
        return  # nothing critical, exit early

    notification_message = f"Tank level is at {sensor_reading.tank_level_per}%, approaching capacity"
    notification_type    = "tank_level_high"

    # 2) Create the Notification record
    with app.app_context():
        from models import Notification, User, UserNotification  # Import here to avoid circular imports
        notification = Notification(
            message=notification_message,
            severity="critical",
            notification_type=notification_type
        )
        db.session.add(notification)
        db.session.flush()  # get its ID

        # 3a) In-app notifications for everyone
        all_users = User.query.all()
        for user in all_users:
            un = UserNotification(
                user_id=user.id,
                notification_id=notification.id
            )
            db.session.add(un)

        # 3b) Email alerts for opted-in users
        email_users = User.query.filter_by(receive_email_alerts=True).all()
        for user in email_users:
            send_email_alert(notification_message, user.email)

        # 4) Commit all of it
        db.session.commit()
def init_mail(app):
    mail = Mail(app)
    return mail
