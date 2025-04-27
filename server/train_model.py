import pandas as pd
import numpy as np  # Added this import
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
import joblib
from sklearn.model_selection import TimeSeriesSplit

def train_model():
    df = pd.read_csv("septic_tank_data.csv", parse_dates=["timestamp"])
    
    # Feature Engineering
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["prev_reading"] = df["sensor_cm"].shift(1).bfill()
    df["3h_avg"] = df["sensor_cm"].rolling(3, min_periods=1).mean().shift(1).bfill()
    df["roc_1h"] = df["sensor_cm"].diff().fillna(0)

    X = df[["hour", "sensor_cm", "prev_reading", "day_of_week", "3h_avg", "roc_1h"]]
    y = df["percent_full"]

    # Time-series cross validation
    tscv = TimeSeriesSplit(n_splits=5)
    maes = []
    
    model = HistGradientBoostingRegressor(
        max_iter=1000,
        learning_rate=0.015,
        max_depth=5,
        random_state=42,
        categorical_features=[0, 3],
        early_stopping=True,
        validation_fraction=0.2,
        n_iter_no_change=50
    )

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        maes.append(mean_absolute_error(y_test, preds))
    
    print(f"Cross-validated MAE: {np.mean(maes):.2f}% (±{np.std(maes):.2f})")
    
    # Final model on all data
    model.fit(X, y)
    joblib.dump(model, "tank_model.pkl")

if __name__ == "__main__":
    train_model()