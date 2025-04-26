from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func
from database import db

class SensorReading(db.Model, SerializerMixin):
    __tablename__ = 'sensor_readings'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    temp = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    tank_level_per = db.Column(db.Float, nullable=False)  # Percentage (0-100)

    def __repr__(self):
        return f"<SensorReading id={self.id}, timestamp={self.timestamp}, temp={self.temp}, ph={self.ph}>"