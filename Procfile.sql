web: gunicorn app:app
worker: python scripts/simulate_sensors.py