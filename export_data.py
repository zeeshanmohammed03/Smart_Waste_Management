import sqlite3
import pandas as pd

def export_to_csv():
    conn = sqlite3.connect('waste_management.db')
    
    # Export bins
    pd.read_sql_query('SELECT * FROM bins', conn).to_csv('bins.csv', index=False)
    # Export citizen reports
    pd.read_sql_query('SELECT * FROM citizen_reports', conn).to_csv('citizen_reports.csv', index=False)
    # Export environmental impact
    pd.read_sql_query('SELECT * FROM environmental_impact', conn).to_csv('environmental_impact.csv', index=False)
    # Export driver performance
    pd.read_sql_query('SELECT driver_name, route, fuel_usage, distance_traveled, (distance_traveled / fuel_usage) as efficiency FROM trucks', conn).to_csv('driver_performance.csv', index=False)
    
    conn.close()

if __name__ == '__main__':
    export_to_csv()