import sqlite3
import random
from datetime import datetime, timedelta
import time

def simulate_sensor_data():
    with sqlite3.connect('waste_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT bin_id, fill_level FROM bins')
        bins = cursor.fetchall()
        
        for bin_id, current_fill in bins:
            # Simulate fill level change (+0 to +5%)
            fill_change = random.uniform(0, 5)
            new_fill = min(100, current_fill + fill_change)
            # Simulate temperature (20-35°C)
            temperature = random.uniform(20, 35)
            # Update bins table
            cursor.execute('''
                UPDATE bins
                SET fill_level = ?, temperature = ?, last_updated = ?
                WHERE bin_id = ?
            ''', (new_fill, temperature, datetime.now(), bin_id))
            # Log to bin_sensors
            cursor.execute('''
                INSERT INTO bin_sensors (bin_id, fill_level, temperature)
                VALUES (?, ?, ?)
            ''', (bin_id, new_fill, temperature))
        conn.commit()

if __name__ == '__main__':
    simulate_sensor_data()
    print("Sensor data updated")