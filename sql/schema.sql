CREATE TABLE bins (
    bin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    area TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('recyclable', 'organic', 'general')),
    capacity INTEGER NOT NULL,
    fill_level INTEGER NOT NULL CHECK(fill_level >= 0 AND fill_level <= 100),
    temperature REAL NOT NULL,
    last_emptied TIMESTAMP NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bin_sensors (
    sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id INTEGER NOT NULL,
    fill_level INTEGER NOT NULL CHECK(fill_level >= 0 AND fill_level <= 100),
    temperature REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bin_id) REFERENCES bins(bin_id)
);

CREATE TABLE collections (
    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id INTEGER NOT NULL,
    truck_id INTEGER NOT NULL,
    collection_date TIMESTAMP NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('scheduled', 'completed', 'missed')),
    FOREIGN KEY (bin_id) REFERENCES bins(bin_id),
    FOREIGN KEY (truck_id) REFERENCES trucks(truck_id)
);

CREATE TABLE trucks (
    truck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_name TEXT NOT NULL,
    route TEXT NOT NULL,
    fuel_usage REAL NOT NULL,
    distance_traveled REAL NOT NULL,
    last_maintenance TIMESTAMP NOT NULL
);

CREATE TABLE citizen_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id INTEGER,
    area TEXT NOT NULL,
    complaint_type TEXT NOT NULL CHECK(complaint_type IN ('overflow', 'smell', 'other')),
    geolocation TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open', 'in_progress', 'resolved')),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bin_id) REFERENCES bins(bin_id)
);

CREATE TABLE environmental_impact (
    impact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL,
    emission_level REAL NOT NULL,
    plastic_percentage REAL NOT NULL,
    recycling_rate REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE penalties (
    penalty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    violation_type TEXT NOT NULL CHECK(violation_type IN ('illegal_dumping', 'improper_disposal', 'other')),
    fine_amount REAL NOT NULL,
    location TEXT NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);