import numpy as np
import pandas as pd

EMPTY_READING = 22.0
TANK_DEPTH = 27.0
MAX_FILL_RANGE = TANK_DEPTH - EMPTY_READING
DAYS = 120  # 4 months for better seasonality

def generate_data():
    np.random.seed(42)
    timestamps = pd.date_range("2023-01-01", periods=DAYS, freq="D")
    data = []
    current_level = 0.0
    last_pumped = 0

    for day in range(DAYS):
        # Tank emptying simulation (every 30-45 days)
        if day - last_pumped > np.random.randint(30, 45):
            current_level = 0.0
            last_pumped = day
            
        seasonal_factor = 0.7 + 0.6*np.sin(2*np.pi*day/120)
        weekend_factor = 1.8 if day % 7 >= 5 else 1.0
        
        for hour in [6, 12, 18, 22]:
            # Base usage with realistic patterns
            base = np.random.uniform(0.03, 0.08) * seasonal_factor
            
            # Time-of-day effects
            if 6 <= hour <= 9:
                base *= 2.0  # Morning usage
            elif 18 <= hour <= 21:
                base *= 2.5  # Evening peak
                
            # Random spikes (15% chance)
            if np.random.random() < 0.15:
                base *= np.random.uniform(2, 5)
                
            current_level = min(current_level + base * weekend_factor, 1.0)
            reading = EMPTY_READING - (MAX_FILL_RANGE * current_level)
            reading += np.random.normal(0, 0.05)  # 5mm noise
            
            data.append({
                "timestamp": timestamps[day] + pd.Timedelta(hours=hour),
                "sensor_cm": round(reading, 2),
                "true_level": round(current_level, 4)
            })
    
    df = pd.DataFrame(data)
    df["percent_full"] = (df["true_level"] * 100).round(1)
    df.to_csv("septic_tank_data.csv", index=False)
    return df

if __name__ == "__main__":
    generate_data()