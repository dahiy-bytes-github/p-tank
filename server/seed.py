from datetime import datetime, timedelta, timezone
import random

from database import db
from app import app 
from models import SensorReading, User, Notification, UserNotification

def seed_all():
    with app.app_context():
        db.drop_all()
        db.create_all()

        now = datetime.now(timezone.utc)

        # ---- Seed Users ----
        users = [
            User(full_name="Alice Admin", email="alice@example.com", role="Admin"),
            User(full_name="Bob User", email="bob@example.com"),
            User(full_name="Charlie Tester", email="charlie@example.com")
        ]
        for user in users:
            user.set_password("test123")
        db.session.add_all(users)
        db.session.commit()

        print("✅ Seeded users table.")

        # ---- Seed SensorReadings ----
        readings = []
        for i in range(20):
            reading = SensorReading(
                timestamp=now - timedelta(minutes=15 * i),
                temp=round(random.uniform(20.0, 30.0), 2),
                ph=round(random.uniform(6.5, 8.0), 2),
                tank_level_per=round(random.uniform(10.0, 100.0), 2),
                predicted_full=random.choice([True, False])
            )
            readings.append(reading)
        db.session.add_all(readings)
        db.session.commit()

        print("✅ Seeded sensor_readings table.")

        # ---- Seed Notifications ----
        messages = [
            ("pH anomaly detected", "warning", "ph_anomaly"),
            ("Temperature exceeds safe levels", "critical", "temp_anomaly"),
            ("Tank is nearly full", "info", "tank_full"),
            ("Sensor offline for 5+ minutes", "warning", "sensor_offline")
        ]
        notifications = []
        for msg, severity, ntype in messages:
            notifications.append(Notification(
                message=msg,
                severity=severity,
                notification_type=ntype,
                created_at=now - timedelta(hours=random.randint(1, 24))
            ))
        db.session.add_all(notifications)
        db.session.commit()

        print("✅ Seeded notifications table.")

        # ---- Seed UserNotifications ----
        user_notifications = []
        for user in users:
            for notif in random.sample(notifications, k=random.randint(1, len(notifications))):
                user_notifications.append(UserNotification(
                    user_id=user.id,
                    notification_id=notif.id,
                    is_read=random.choice([True, False]),
                    read_at=now - timedelta(minutes=random.randint(5, 120)) if random.choice([True, False]) else None
                ))
        db.session.add_all(user_notifications)
        db.session.commit()

        print("✅ Seeded user_notifications table.")

if __name__ == "__main__":
    seed_all()
