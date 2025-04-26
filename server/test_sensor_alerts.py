#!/usr/bin/env python3
import os
import requests
import time

# Configure this to match your Flask app’s address
BASE_URL = os.getenv("FLASK_BASE_URL", "http://localhost:5555")

def post_reading(temp, ph, tank_level_per):
    payload = {
        "temp": temp,
        "ph": ph,
        "tank_level_per": tank_level_per
    }
    resp = requests.post(f"{BASE_URL}/sensor-readings", json=payload)
    print(f"\nPOST /sensor-readings → status {resp.status_code}")
    try:
        print(resp.json())
    except ValueError:
        print(resp.text)

if __name__ == "__main__":
    print("1) Sending a non-critical reading (tank_level_per=50) …")
    post_reading(temp=22.5, ph=7.1, tank_level_per=50)
    
    # Give your server a second to process/log
    time.sleep(1)
    
    print("\n2) Sending a critical reading (tank_level_per=95) …")
    post_reading(temp=23.0, ph=7.0, tank_level_per=95)
    
    print("\nDone. Check your Flask server logs for “Email sent successfully…” lines,")
    print("and look in the inbox of any opted-in user for the “Critical Tank Alert” email.")
