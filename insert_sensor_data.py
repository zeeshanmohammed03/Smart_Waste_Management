import sqlite3
from datetime import datetime, timedelta

def insert_test_sensor_data():
    conn = sqlite3.connect('waste_management.db')
    cursor = conn.cursor()
    
    bin_id = 1
    base_time = datetime.now() - timedelta(days=1)
    fill_levels = [80, 82, 85, 87, 90, 92, 93, 94, 95, 96]  # Simulated trend
    temperatures = [25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5]
    
    for i in range(10):
        recorded_at = base_time + timedelta(hours=i*2)
        cursor.execute('''
            INSERT INTO bin_sensors (bin_id, fill_level, temperature, recorded_at)
            VALUES (?, ?, ?, ?)
        ''', (bin_id, fill_levels[i], temperatures[i], recorded_at))
    
    conn.commit()
    conn.close()
    print("Test sensor data inserted for bin_id 1")

if __name__ == '__main__':
    insert_test_sensor_data()