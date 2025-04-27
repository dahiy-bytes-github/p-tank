import joblib
import pandas as pd
from datetime import datetime
from flask_restful import Resource, reqparse
from flask import jsonify, request

class TankPredictor:
    def __init__(self):
        self.empty = 22.0
        self.max_range = 5.0  # 27cm - 22cm
        self.critical = 80
        self.model = joblib.load("tank_model.pkl")
        self.history = []
        self.max_history = 6

    def calculate_level(self, reading):
        fill_ratio = (self.empty - reading) / -self.max_range
        return round(max(0, min(100, fill_ratio * 100)), 1)

    def update_history(self, reading):
        self.history = ([reading] + self.history)[:self.max_history]

    def predict_critical(self, current_reading):
        self.update_history(current_reading)
        
        now = datetime.now()
        features = {
            'hour': now.hour,
            'sensor_cm': current_reading,
            'prev_reading': self.history[1] if len(self.history) > 1 else current_reading,
            'day_of_week': now.weekday(),
            '3h_avg': sum(self.history)/len(self.history) if self.history else current_reading,
            'roc_1h': self.history[0] - self.history[1] if len(self.history) > 1 else 0
        }

        forecast = []
        temp_features = features.copy()
        
        for _ in range(6):  # 6-hour forecast
            df = pd.DataFrame([temp_features], dtype=float)
            pred = self.model.predict(df)[0]
            forecast.append(pred)
            
            # Update features for next prediction
            temp_features['prev_reading'] = pred
            temp_features['hour'] = (temp_features['hour'] + 1) % 24
            temp_features['3h_avg'] = (temp_features['3h_avg']*2 + pred)/3
            temp_features['roc_1h'] = pred - temp_features['prev_reading']

        return {
            'critical': bool(max(forecast) >= self.critical),
            'forecast': [round(p,1) for p in forecast],
            'max_level': round(max(forecast),1),
            'next_3h': round(sum(forecast[:3])/3,1)
        }