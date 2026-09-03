-- ============================================================
-- UrbanSenseAI Database Schema (PostgreSQL 18)
-- Strict Provenance & Source Attribution Architecture
-- ============================================================

DROP TABLE IF EXISTS media CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS traffic_analysis CASCADE;
DROP TABLE IF EXISTS incidents CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS buses CASCADE;

-- 1. BUSES TABLE (Physical & Simulated Fleet)
CREATE TABLE buses (
    id SERIAL PRIMARY KEY,
    bus_id VARCHAR(50) UNIQUE NOT NULL,
    registration_number VARCHAR(50),
    route_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE',          -- 'ACTIVE', 'INACTIVE', 'MAINTENANCE'
    camera_status VARCHAR(20) DEFAULT 'DISCONNECTED', -- 'CONNECTED', 'DISCONNECTED'
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    gps_status VARCHAR(30) DEFAULT 'UNAVAILABLE', -- 'LIVE_GPS', 'UNAVAILABLE', 'SIMULATED'
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. EVENTS TABLE (Potholes, Waterlogging, Hazards, Civic Alerts)
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    bus_id VARCHAR(50) NOT NULL REFERENCES buses(bus_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,              -- 'POTHOLE', 'WATERLOGGING', 'ROAD_HAZARD', 'OBSTRUCTION'
    source_type VARCHAR(30) DEFAULT 'LIVE_EDGE_AI',-- 'LIVE_EDGE_AI', 'DEMO_DETECTION', 'SIMULATED_EVENT'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    confidence DOUBLE PRECISION DEFAULT 0.0,
    description TEXT,
    status VARCHAR(20) DEFAULT 'NEW',             -- 'NEW', 'VERIFIED', 'RESOLVED', 'DISMISSED'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. TRAFFIC ANALYSIS TABLE (Periodic Aggregations & Causes)
CREATE TABLE traffic_analysis (
    id SERIAL PRIMARY KEY,
    bus_id VARCHAR(50) NOT NULL REFERENCES buses(bus_id) ON DELETE CASCADE,
    source_type VARCHAR(30) DEFAULT 'LIVE_EDGE_AI',-- 'LIVE_EDGE_AI', 'SIMULATED_AI'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    vehicle_count INTEGER DEFAULT 0,
    cars INTEGER DEFAULT 0,
    motorcycles INTEGER DEFAULT 0,
    buses INTEGER DEFAULT 0,
    trucks INTEGER DEFAULT 0,
    movement_score DOUBLE PRECISION DEFAULT 0.0,
    traffic_level VARCHAR(20) DEFAULT 'LOW',      -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    probable_reasons TEXT[],                      -- Array of identified causes
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

-- 4. INCIDENTS TABLE (Collisions & Accidents)
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(50) UNIQUE NOT NULL,
    bus_id VARCHAR(50) NOT NULL REFERENCES buses(bus_id) ON DELETE CASCADE,
    incident_type VARCHAR(50) DEFAULT 'Potential Collision',
    source_type VARCHAR(30) DEFAULT 'LIVE_EDGE_AI',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    confidence DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'PENDING_REVIEW',  -- 'PENDING_REVIEW', 'REVIEWED', 'ACTION_TAKEN'
    description TEXT,
    plate_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. MEDIA TABLE (Images, Keyframes, MP4 Evidence Videos)
CREATE TABLE media (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    media_type VARCHAR(20) NOT NULL,              -- 'IMAGE', 'VIDEO', 'KEYFRAME_PRE', etc.
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. LOCATIONS TABLE (High-Frequency GPS Breadcrumbs with Provenance)
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    bus_id VARCHAR(50) NOT NULL REFERENCES buses(bus_id) ON DELETE CASCADE,
    source_type VARCHAR(30) DEFAULT 'LIVE_GPS',   -- 'LIVE_GPS', 'SIMULATED_GPS'
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy DOUBLE PRECISION,
    speed DOUBLE PRECISION DEFAULT 0.0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PERFORMANCE INDEXES
-- ============================================================
CREATE INDEX idx_buses_bus_id ON buses(bus_id);
CREATE INDEX idx_events_bus_id ON events(bus_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_traffic_timestamp ON traffic_analysis(timestamp);
CREATE INDEX idx_traffic_bus_id ON traffic_analysis(bus_id);
CREATE INDEX idx_incidents_timestamp ON incidents(timestamp);
CREATE INDEX idx_locations_bus_id_time ON locations(bus_id, timestamp);
