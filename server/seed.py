# seed.py

from datetime import datetime, timedelta, timezone
import random

from database import db
from app import app 
from models import SensorReading

def seed_sensor_readings():
    with app.app_context():
        db.drop_all()
        db.create_all()

        now = datetime.now(timezone.utc)
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

        # ✅ These must be inside the app context
        db.session.add_all(readings)
        db.session.commit()
        print("✅ Seeded sensor_readings table with sample data.")

if __name__ == "__main__":
    seed_sensor_readings()
