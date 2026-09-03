import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Bus, AlertTriangle, AlertOctagon, Droplets, Filter, Eye } from 'lucide-react';

// Custom SVG HTML Markers
const createBusIcon = (isLive) => L.divIcon({
  className: 'custom-leaflet-marker',
  html: `
    <div style="
      width: 32px;
      height: 32px;
      background: ${isLive ? '#10b981' : '#06b6d4'};
      border: 2px solid #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 ${isLive ? '14px rgba(16,185,129,0.8)' : '10px rgba(6,182,212,0.6)'};
      color: #090d16;
    ">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M8 6v6m8-6v6M4 16h16M4 6h16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2zM6 18v2m12-2v2"/>
      </svg>
    </div>
  `,
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

const createHazardIcon = (type) => {
  let color = '#f59e0b';
  if (type === 'POTHOLE') color = '#f97316';
  if (type === 'WATERLOGGING') color = '#3b82f6';
  if (type === 'INCIDENT' || type === 'Potential Collision') color = '#ef4444';

  return L.divIcon({
    className: 'custom-hazard-marker',
    html: `
      <div style="
        width: 26px;
        height: 26px;
        background: ${color};
        border: 2px solid #fff;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 10px ${color};
        color: #fff;
      ">
        <span style="font-size: 13px; font-weight: bold;">!</span>
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  });
};

export default function GISMap({ buses, events, incidents, selectedBusId, onSelectIncident }) {
  const [activeFilter, setActiveFilter] = useState('ALL');

  // Center on Chennai
  const defaultCenter = [13.0827, 80.2707];

  const filteredEvents = events.filter(e => {
    if (activeFilter === 'ALL') return true;
    if (activeFilter === 'POTHOLES') return e.event_type === 'POTHOLE';
    if (activeFilter === 'WATERLOGGING') return e.event_type === 'WATERLOGGING';
    if (activeFilter === 'HAZARDS') return e.event_type === 'ROAD_HAZARD';
    return true;
  });

  const showIncidents = activeFilter === 'ALL' || activeFilter === 'INCIDENTS';

  return (
    <div>
      {/* Map Control Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>Active GIS Layers:</span>
          {['ALL', 'BUSES', 'POTHOLES', 'WATERLOGGING', 'INCIDENTS'].map((filter) => (
            <button
              key={filter}
              className={`btn ${activeFilter === filter ? 'btn-primary' : 'btn-outline'}`}
              style={{ padding: '4px 10px', fontSize: '0.78rem' }}
              onClick={() => setActiveFilter(filter)}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--emerald-500)' }} /> Live Bus (BUS-001)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--cyan-500)' }} /> Simulated Fleet
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: 10, height: 10, borderRadius: '2px', background: '#f97316' }} /> Potholes
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: 10, height: 10, borderRadius: '2px', background: 'var(--rose-500)' }} /> Collisions
          </span>
        </div>
      </div>

      {/* Real Phone GPS Notice for BUS-001 */}
      {(!buses.find(b => b.bus_id === 'BUS-001')?.latitude) && (
        <div style={{
          padding: '6px 14px',
          background: 'rgba(239,68,68,0.1)',
          border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: '6px',
          fontSize: '0.78rem',
          color: 'var(--rose-400)',
          marginBottom: '10px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span className="status-dot pulse" style={{ background: 'var(--rose-500)' }} />
          <span>BUS-001 Physical GPS: UNAVAILABLE (Marker will appear on GIS map only when real phone GPS coordinates are acquired)</span>
        </div>
      )}

      {/* Leaflet Map Frame */}
      <div className="map-container" style={{ height: 'calc(100vh - 210px)' }}>
        <MapContainer center={defaultCenter} zoom={12} scrollWheelZoom={true}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* 1. Fleet Bus Markers (Only buses with real or simulated coordinates) */}
          {(activeFilter === 'ALL' || activeFilter === 'BUSES') && buses
            .filter((bus) => bus.latitude != null && bus.longitude != null)
            .map((bus) => {
              const isLive = (bus.bus_id === 'BUS-001');
              const pos = [bus.latitude, bus.longitude];
              return (
                <Marker key={bus.bus_id} position={pos} icon={createBusIcon(isLive)}>
                  <Popup>
                    <div style={{ padding: '6px', minWidth: '200px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <strong style={{ fontSize: '1rem', color: isLive ? 'var(--emerald-400)' : 'var(--cyan-400)' }}>
                          {bus.bus_id}
                        </strong>
                        <span style={{
                          fontSize: '0.68rem',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          background: isLive ? 'rgba(16,185,129,0.2)' : 'rgba(6,182,212,0.2)',
                          color: isLive ? 'var(--emerald-400)' : 'var(--cyan-400)',
                          fontWeight: '700'
                        }}>
                          {isLive ? 'LIVE PROTOTYPE' : 'SIMULATED'}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#9ca3af', marginBottom: '4px' }}>
                        {bus.route_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>
                        Registration: <strong>{bus.registration_number}</strong>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#cbd5e1', marginTop: '2px' }}>
                        GPS: {pos[0].toFixed(5)}, {pos[1].toFixed(5)} ({bus.gps_status || (isLive ? 'LIVE' : 'SIMULATED')})
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#cbd5e1', marginTop: '2px' }}>
                        Camera: <span style={{ color: 'var(--emerald-400)' }}>{bus.camera_status}</span>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

          {/* 2. Civic Hazard Events (Potholes, Waterlogging) */}
          {filteredEvents
            .filter((evt) => evt.latitude != null && evt.longitude != null)
            .map((evt) => (
            <Marker
              key={`evt-${evt.id}`}
              position={[evt.latitude, evt.longitude]}
              icon={createHazardIcon(evt.event_type)}
            >
              <Popup>
                <div style={{ padding: '6px', minWidth: '220px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{
                      fontSize: '0.78rem',
                      fontWeight: '800',
                      color: evt.event_type === 'POTHOLE' ? '#f97316' : '#3b82f6'
                    }}>
                      {evt.event_type}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>{evt.bus_id}</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#f3f4f6', marginBottom: '6px' }}>
                    {evt.description || 'Road surface issue detected'}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>
                    Confidence: <strong>{Math.round((evt.confidence || 0.85) * 100)}%</strong>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af', marginTop: '2px' }}>
                    Time: {new Date(evt.timestamp).toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af', marginTop: '2px' }}>
                    Origin: <strong style={{ color: 'var(--amber-400)' }}>{evt.source_type || 'LIVE'}</strong>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* 3. Incidents / Potential Collisions */}
          {showIncidents && incidents
            .filter((inc) => inc.latitude != null && inc.longitude != null)
            .map((inc) => (
            <Marker
              key={`inc-${inc.id}`}
              position={[inc.latitude, inc.longitude]}
              icon={createHazardIcon('INCIDENT')}
            >
              <Popup>
                <div style={{ padding: '6px', minWidth: '220px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: '800', color: 'var(--rose-400)' }}>
                      POTENTIAL COLLISION
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>{inc.incident_id}</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#f3f4f6', marginBottom: '4px' }}>
                    {inc.description}
                  </div>
                  {inc.plate_number && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--amber-400)', fontWeight: '600' }}>
                      Plate: {inc.plate_number}
                    </div>
                  )}
                  <div style={{ fontSize: '0.72rem', color: '#9ca3af', marginTop: '2px' }}>
                    Status: <strong style={{ color: inc.status === 'REVIEWED' ? 'var(--emerald-400)' : 'var(--rose-400)' }}>
                      {inc.status}
                    </strong>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ marginTop: '8px', width: '100%', fontSize: '0.75rem', padding: '4px 8px' }}
                    onClick={() => onSelectIncident(inc)}
                  >
                    <Eye size={12} /> View Evidence Clip
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
