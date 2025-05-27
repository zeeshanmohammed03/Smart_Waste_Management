from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import random
import time

app = Flask(__name__)

def init_db():
    import os
    db_exists = os.path.exists('waste_management.db')
    with sqlite3.connect('waste_management.db') as conn:
        if not db_exists:
            # Create tables only if database is new
            with open('sql/schema.sql', 'r') as f:
                conn.executescript(f.read())
        
        # Insert sample data only if bins table is empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bins")
        if cursor.fetchone()[0] == 0:
            conn.executescript('''
                INSERT INTO bins (location, area, type, capacity, fill_level, temperature, last_emptied)
                VALUES ('123 Main St', 'Downtown', 'recyclable', 100, 95, 25.5, '2025-05-24 10:00:00'),
                       ('456 Oak Ave', 'Suburb', 'organic', 80, 85, 30.0, '2025-05-25 08:00:00'),
                       ('789 Pine Rd', 'Downtown', 'general', 120, 92, 28.0, '2025-05-23 12:00:00');

                INSERT INTO trucks (driver_name, route, fuel_usage, distance_traveled, last_maintenance)
                VALUES ('John Doe', 'Downtown-Suburb', 15.5, 50.0, '2025-05-20 09:00:00'),
                       ('Jane Smith', 'Suburb-Industrial', 12.0, 40.0, '2025-05-22 11:00:00');

                INSERT INTO citizen_reports (bin_id, area, complaint_type, geolocation, status)
                VALUES (1, 'Downtown', 'overflow', '40.7128,-74.0060', 'open'),
                       (3, 'Downtown', 'smell', '40.7130,-74.0055', 'in_progress');

                INSERT INTO environmental_impact (area, emission_level, plastic_percentage, recycling_rate)
                VALUES ('Downtown', 200.5, 30.0, 60.0),
                       ('Suburb', 150.0, 25.0, 70.0);
            ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bins', methods=['GET'])
def get_bins():
    with sqlite3.connect('waste_management.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bins')
        bins = [dict(row) for row in cursor.fetchall()]
    return jsonify(bins)

@app.route('/api/bins', methods=['POST'])
def add_bin():
    data = request.json
    with sqlite3.connect('waste_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bins (location, area, type, capacity, fill_level, temperature, last_emptied)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['location'], data['area'], data['type'], data['capacity'], data['fill_level'], data['temperature'], data['last_emptied']))
        conn.commit()
        bin_id = cursor.lastrowid
    return jsonify({'bin_id': bin_id})

@app.route('/api/queries/critical_bins', methods=['GET'])
def critical_bins():
    with sqlite3.connect('waste_management.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bin_id, location, area, fill_level, last_emptied
            FROM bins
            WHERE fill_level > 90
            AND last_emptied < datetime('now', '-2 days')
        ''')
        bins = [dict(row) for row in cursor.fetchall()]
    return jsonify(bins)

@app.route('/api/queries/complaints_by_area', methods=['GET'])
def complaints_by_area():
    with sqlite3.connect('waste_management.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT area, COUNT(*) as complaint_count
            FROM citizen_reports
            GROUP BY area
            ORDER BY complaint_count DESC
        ''')
        areas = [dict(row) for row in cursor.fetchall()]
    return jsonify(areas)

@app.route('/api/queries/driver_performance', methods=['GET'])

def driver_performance():
    with sqlite3.connect('waste_management.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT driver_name, route, fuel_usage, distance_traveled,
                   (distance_traveled / fuel_usage) as efficiency
            FROM trucks
            ORDER BY efficiency DESC
        ''')
        drivers = [dict(row) for row in cursor.fetchall()]
    return jsonify(drivers)

@app.route('/api/queries/area_cleanliness', methods=['GET'])
def area_cleanliness():
    with sqlite3.connect('waste_management.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.area, AVG(e.recycling_rate) as avg_recycling_rate,
                   AVG(e.emission_level) as avg_emission,
                   COUNT(c.report_id) as complaint_count,
                   (AVG(e.recycling_rate) - AVG(e.emission_level) / 100 - COUNT(c.report_id)) as cleanliness_score
            FROM environmental_impact e
            LEFT JOIN citizen_reports c ON e.area = c.area
            GROUP BY e.area
            ORDER BY cleanliness_score DESC
        ''')
        areas = [dict(row) for row in cursor.fetchall()]
    return jsonify(areas)
@app.route('/api/bin_sensors/<int:bin_id>', methods=['GET'])
def get_bin_sensors(bin_id):
    with sqlite3.connect('waste_management.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT fill_level, recorded_at FROM bin_sensors WHERE bin_id = ? ORDER BY recorded_at DESC LIMIT 10', (bin_id,))
        sensors = [dict(row) for row in cursor.fetchall()]
    return jsonify(sensors)

@app.route('/api/queries/predict_overflow/<int:bin_id>', methods=['GET'])
def predict_overflow(bin_id):
    with sqlite3.connect('waste_management.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fill_level, recorded_at
            FROM bin_sensors
            WHERE bin_id = ?
            ORDER BY recorded_at DESC
            LIMIT 10
        ''', (bin_id,))
        data = [dict(row) for row in cursor.fetchall()]
    
    if len(data) < 2:
        return jsonify({'error': 'Insufficient data'})
    
    # Simple linear prediction based on fill rate
    fill_rates = []
    for i in range(len(data)-1):
        time_diff = (datetime.fromisoformat(data[i]['recorded_at'].replace('Z', '+00:00')) - 
                    datetime.fromisoformat(data[i+1]['recorded_at'].replace('Z', '+00:00'))).total_seconds() / 3600
        fill_diff = data[i]['fill_level'] - data[i+1]['fill_level']
        if time_diff > 0:
            fill_rates.append(fill_diff / time_diff)
    
    avg_fill_rate = sum(fill_rates) / len(fill_rates) if fill_rates else 0
    current_fill = data[0]['fill_level']
    hours_to_overflow = (100 - current_fill) / avg_fill_rate if avg_fill_rate > 0 else float('inf')
    overflow_date = datetime.now() + timedelta(hours=hours_to_overflow)
    
    return jsonify({'bin_id': bin_id, 'predicted_overflow': overflow_date.isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)