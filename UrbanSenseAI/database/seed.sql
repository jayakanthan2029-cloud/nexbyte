-- ============================================================
-- UrbanSenseAI Database Seed Data
-- Strict Live / Simulated Separation
-- ============================================================

TRUNCATE TABLE media, locations, traffic_analysis, incidents, events, buses RESTART IDENTITY CASCADE;

-- 1. SEED FLEET BUSES
-- BUS-001 is the REAL PHYSICAL PROTOTYPE (No fake coordinates seeded).
-- BUS-002 through BUS-005 are DIGITALLY SIMULATED fleet nodes.
INSERT INTO buses (bus_id, registration_number, route_name, status, camera_status, latitude, longitude, gps_status)
VALUES 
    ('BUS-001', 'TN-01-AL-2026', 'Route 21G (Broadway - Tambaram)', 'ACTIVE', 'DISCONNECTED', NULL, NULL, 'UNAVAILABLE'),
    ('BUS-002', 'TN-02-SIM-101', 'Route 19B (T.Nagar - Kelambakkam)', 'ACTIVE', 'CONNECTED', 13.0418, 80.2341, 'SIMULATED'),
    ('BUS-003', 'TN-03-SIM-202', 'Route 23C (Ayanavaram - Besant Nagar)', 'ACTIVE', 'CONNECTED', 13.0012, 80.2565, 'SIMULATED'),
    ('BUS-004', 'TN-04-SIM-303', 'Route 570 (CMBT - Siruseri SIPCOT)', 'ACTIVE', 'CONNECTED', 12.9815, 80.2180, 'SIMULATED'),
    ('BUS-005', 'TN-05-SIM-404', 'Route 47A (ICF - Thiruvanmiyur)', 'ACTIVE', 'CONNECTED', 13.0850, 80.2100, 'SIMULATED');

-- 2. SEED LOCATIONS (ONLY FOR SIMULATED BUSES - NEVER FOR BUS-001)
INSERT INTO locations (bus_id, source_type, latitude, longitude, speed, timestamp)
VALUES
    ('BUS-002', 'SIMULATED_GPS', 13.0418, 80.2341, 18.2, CURRENT_TIMESTAMP - INTERVAL '2 minutes'),
    ('BUS-003', 'SIMULATED_GPS', 13.0012, 80.2565, 30.0, CURRENT_TIMESTAMP - INTERVAL '2 minutes'),
    ('BUS-004', 'SIMULATED_GPS', 12.9815, 80.2180, 15.0, CURRENT_TIMESTAMP - INTERVAL '2 minutes'),
    ('BUS-005', 'SIMULATED_GPS', 13.0850, 80.2100, 22.0, CURRENT_TIMESTAMP - INTERVAL '2 minutes');

-- 3. SEED TRAFFIC RECORDS (ONLY FOR SIMULATED BUSES - NEVER FOR BUS-001)
INSERT INTO traffic_analysis (bus_id, source_type, timestamp, vehicle_count, cars, motorcycles, buses, trucks, movement_score, traffic_level, probable_reasons, latitude, longitude)
VALUES
    ('BUS-002', 'SIMULATED_AI', CURRENT_TIMESTAMP - INTERVAL '8 minutes', 26, 16, 7, 2, 1, 0.18, 'HIGH', ARRAY['High vehicle density', 'Low movement', 'Signal bottleneck'], 13.0418, 80.2341),
    ('BUS-003', 'SIMULATED_AI', CURRENT_TIMESTAMP - INTERVAL '5 minutes', 7, 4, 2, 1, 0, 0.82, 'LOW', ARRAY['Free flowing traffic'], 13.0012, 80.2565),
    ('BUS-004', 'SIMULATED_AI', CURRENT_TIMESTAMP - INTERVAL '3 minutes', 31, 18, 9, 2, 2, 0.11, 'CRITICAL', ARRAY['High vehicle density', 'Road obstruction', 'Low movement'], 12.9815, 80.2180);
