import React from 'react';
import { 
  Bus, 
  Activity, 
  AlertTriangle, 
  ShieldAlert, 
  Navigation, 
  Droplets, 
  TrendingUp, 
  Zap,
  Radio,
  Clock
} from 'lucide-react';

export default function Dashboard({ 
  summary, 
  liveBus, 
  recentEvents, 
  recentTraffic, 
  onViewMap,
  onViewIncident 
}) {
  const kpis = [
    {
      label: 'Active Fleet Buses',
      value: summary.active_buses || 0,
      icon: Bus,
      color: 'var(--cyan-400)',
      bg: 'rgba(6, 182, 212, 0.12)'
    },
    {
      label: 'Live Civic Detections',
      value: summary.live_events_count || 0,
      icon: Activity,
      color: 'var(--emerald-400)',
      bg: 'rgba(16, 185, 129, 0.12)'
    },
    {
      label: 'Road Defects / Potholes',
      value: summary.potholes_count || 0,
      icon: AlertTriangle,
      color: 'var(--amber-400)',
      bg: 'rgba(245, 158, 11, 0.12)'
    },
    {
      label: 'Collision Evidence Logs',
      value: summary.critical_incidents_count || 0,
      icon: ShieldAlert,
      color: 'var(--rose-400)',
      bg: 'rgba(239, 68, 68, 0.12)'
    },
    {
      label: 'High Congestion Zones',
      value: summary.high_traffic_zones_count || 0,
      icon: TrendingUp,
      color: 'var(--purple-400)',
      bg: 'rgba(168, 85, 247, 0.12)'
    },
    {
      label: 'Waterlogging Alerts',
      value: summary.waterlogging_count || 0,
      icon: Droplets,
      color: 'var(--blue-500)',
      bg: 'rgba(59, 130, 246, 0.12)'
    }
  ];

  // Derive latest traffic telemetry strictly from backend (No synthetic fallbacks)
  const bus1Traffic = recentTraffic.find(t => t.bus_id === 'BUS-001') || null;

  // Real GPS check for BUS-001 (No fake fallback coordinates)
  const hasRealGPS = liveBus?.latitude != null && liveBus?.longitude != null;
  const gpsDisplay = hasRealGPS 
    ? `${liveBus.latitude.toFixed(5)}, ${liveBus.longitude.toFixed(5)}` 
    : 'UNAVAILABLE';
  const gpsStatusBadge = liveBus?.gps_status === 'LIVE_GPS' ? 'LIVE GPS' : 'GPS UNAVAILABLE';

  return (
    <div>
      {/* 1. Top KPI Summary Grid */}
      <div className="kpi-grid">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="glass-card kpi-card">
              <div className="kpi-icon-box" style={{ background: kpi.bg, color: kpi.color }}>
                <Icon size={22} />
              </div>
              <div>
                <div className="kpi-val" style={{ color: kpi.color }}>{kpi.value}</div>
                <div className="kpi-lbl">{kpi.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 2. Physical Edge Bus Live Panel (BUS-001) */}
      <div className="glass-card live-bus-panel">
        <div className="panel-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '1.2rem', fontWeight: '800', letterSpacing: '-0.01em' }}>
              BUS-001
            </span>
            <span className="bus-live-badge">
              <span className="status-dot pulse" /> LIVE PHYSICAL PROTOTYPE
            </span>
            <span className="gpu-badge">
              <Zap size={13} /> NVIDIA RTX 4060 Laptop GPU
            </span>
            <span style={{
              fontSize: '0.72rem',
              padding: '2px 8px',
              borderRadius: '4px',
              fontWeight: '700',
              background: hasRealGPS ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
              color: hasRealGPS ? 'var(--emerald-400)' : 'var(--rose-400)',
              border: `1px solid ${hasRealGPS ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`
            }}>
              GPS: {gpsStatusBadge}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button 
              className="btn btn-outline" 
              onClick={() => onViewMap('BUS-001')}
              disabled={!hasRealGPS}
              title={hasRealGPS ? "Track on GIS Map" : "GPS coordinate unavailable"}
            >
              <Navigation size={14} /> {hasRealGPS ? "Track on GIS Map" : "Awaiting GPS"}
            </button>
          </div>
        </div>

        {/* Data Provenance Bar */}
        <div style={{
          display: 'flex',
          gap: '16px',
          padding: '6px 12px',
          background: 'rgba(0,0,0,0.3)',
          borderRadius: '6px',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          marginBottom: '14px',
          flexWrap: 'wrap'
        }}>
          <div>DATA ORIGIN: <strong style={{ color: 'var(--cyan-400)' }}>LIVE EDGE AI (YOLO11n + ByteTrack)</strong></div>
          <div>CAMERA: <strong style={{ color: liveBus?.camera_status === 'CONNECTED' ? 'var(--emerald-400)' : 'var(--amber-400)' }}>{liveBus?.camera_status || 'CONNECTED'}</strong></div>
          <div>TRACKER: <strong style={{ color: '#fff' }}>ByteTrack Persistent IDs</strong></div>
          <div>GPS SOURCE: <strong style={{ color: hasRealGPS ? 'var(--emerald-400)' : 'var(--rose-400)' }}>{hasRealGPS ? 'Physical Phone GPS' : 'Phone GPS Not Locked'}</strong></div>
        </div>

        {/* Telemetry Grid */}
        <div className="telemetry-grid">
          <div className="telemetry-item">
            <div className="telem-label">Camera Stream</div>
            <div className="telem-val" style={{ color: liveBus?.camera_status === 'CONNECTED' ? 'var(--emerald-400)' : 'var(--amber-400)' }}>
              {liveBus?.camera_status || 'CONNECTED'}
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telem-label">AI Inference</div>
            <div className="telem-val" style={{ color: 'var(--cyan-400)' }}>
              YOLO11n CUDA
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telem-label">Total Vehicles (YOLO)</div>
            <div className="telem-val" style={{ color: bus1Traffic ? '#fff' : 'var(--text-dark)' }}>
              {bus1Traffic ? bus1Traffic.vehicle_count : 'Awaiting Feed'}
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telem-label">Cars / Bikes</div>
            <div className="telem-val" style={{ color: bus1Traffic ? '#fff' : 'var(--text-dark)' }}>
              {bus1Traffic ? `${bus1Traffic.cars} / ${bus1Traffic.motorcycles}` : '—'}
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telem-label">Buses / Trucks</div>
            <div className="telem-val" style={{ color: bus1Traffic ? '#fff' : 'var(--text-dark)' }}>
              {bus1Traffic ? `${bus1Traffic.buses} / ${bus1Traffic.trucks}` : '—'}
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telem-label">Movement Score</div>
            <div className="telem-val" style={{ color: bus1Traffic ? 'var(--cyan-400)' : 'var(--text-dark)' }}>
              {bus1Traffic ? bus1Traffic.movement_score : '—'}
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telem-label">Traffic Level</div>
            <div className="telem-val" style={{ 
              color: !bus1Traffic ? 'var(--text-dark)' : (
                bus1Traffic.traffic_level === 'HIGH' ? 'var(--rose-400)' : (
                  bus1Traffic.traffic_level === 'MEDIUM' ? 'var(--amber-400)' : 'var(--emerald-400)'
                )
              )
            }}>
              {bus1Traffic ? bus1Traffic.traffic_level : 'WAITING FOR AI'}
            </div>
          </div>

          <div className="telemetry-item">
            <div className="telem-label">GPS Location</div>
            <div className="telem-val" style={{ 
              fontSize: '0.82rem', 
              color: hasRealGPS ? 'var(--emerald-400)' : 'var(--rose-400)',
              fontFamily: 'var(--font-mono)'
            }}>
              {gpsDisplay}
            </div>
          </div>
        </div>

        {/* Probable Cause Reasoning Banner or Waiting State */}
        {bus1Traffic && bus1Traffic.probable_reasons && bus1Traffic.probable_reasons.length > 0 ? (
          <div style={{
            marginTop: '14px',
            padding: '8px 14px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: '6px',
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ fontWeight: '600', color: 'var(--amber-400)' }}>Traffic Intelligence:</span>
            <span>{bus1Traffic.probable_reasons.join(' • ')}</span>
          </div>
        ) : (
          !bus1Traffic && (
            <div style={{
              marginTop: '14px',
              padding: '8px 14px',
              background: 'rgba(6,182,212,0.05)',
              border: '1px dashed rgba(6,182,212,0.2)',
              borderRadius: '6px',
              fontSize: '0.78rem',
              color: 'var(--cyan-400)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Radio size={14} className="pulse" />
              <span>Waiting for Live Edge AI Stream... (Launch <code>python -m ai.main</code> to stream real YOLO11n inferences)</span>
            </div>
          )
        )}
      </div>

      {/* 3. Split Grid: Recent Events Feed & Digital Fleet Snapshot */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px' }}>
        {/* Recent Events Feed */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>Recent Mobile Civic Detections</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Auto-updating via WebSocket</span>
          </div>

          {recentEvents.length === 0 ? (
            <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-dark)' }}>
              <Clock size={32} style={{ margin: '0 auto 8px', opacity: 0.4 }} />
              <p style={{ fontSize: '0.85rem' }}>No events recorded yet. Press 'P' in AI engine for demo pothole.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {recentEvents.slice(0, 5).map((evt) => (
                <div key={evt.id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 14px',
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '6px',
                  borderLeft: `3px solid ${
                    evt.event_type === 'POTHOLE' ? 'var(--amber-400)' : (
                      evt.event_type === 'WATERLOGGING' ? 'var(--blue-500)' : 'var(--rose-400)'
                    )
                  }`
                }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: '700', fontSize: '0.85rem' }}>{evt.event_type}</span>
                      <span style={{ fontSize: '0.7rem', background: 'rgba(255,255,255,0.08)', padding: '1px 6px', borderRadius: '4px' }}>
                        {evt.bus_id}
                      </span>
                      <span style={{ fontSize: '0.68rem', color: evt.source_type === 'LIVE_EDGE_AI' ? 'var(--emerald-400)' : 'var(--amber-400)' }}>
                        [{evt.source_type || 'LIVE'}]
                      </span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {evt.description}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right', fontSize: '0.75rem', color: 'var(--text-dark)' }}>
                    <div>{new Date(evt.timestamp).toLocaleTimeString()}</div>
                    {evt.latitude && evt.longitude ? (
                      <div>{evt.latitude.toFixed(3)}, {evt.longitude.toFixed(3)}</div>
                    ) : (
                      <div style={{ color: 'var(--rose-400)' }}>No GPS Fix</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Fleet Provenance Snapshot */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>Fleet Topology & Origin</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>1 Live + 4 Simulated</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {['BUS-001', 'BUS-002', 'BUS-003', 'BUS-004', 'BUS-005'].map((bid) => {
              const isLive = bid === 'BUS-001';
              return (
                <div key={bid} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 14px',
                  background: isLive ? 'rgba(6,182,212,0.05)' : 'rgba(255,255,255,0.02)',
                  borderRadius: '6px',
                  border: isLive ? '1px solid rgba(6,182,212,0.25)' : '1px solid var(--border-subtle)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Bus size={18} color={isLive ? 'var(--cyan-400)' : 'var(--text-muted)'} />
                    <div>
                      <div style={{ fontWeight: '700', fontSize: '0.85rem' }}>{bid}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {isLive ? 'Physical Prototype (NVIDIA RTX 4060)' : 'Digital Fleet Simulation Node'}
                      </div>
                    </div>
                  </div>

                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: '700',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    background: isLive ? 'rgba(16,185,129,0.15)' : 'rgba(107,114,128,0.2)',
                    color: isLive ? 'var(--emerald-400)' : '#9ca3af'
                  }}>
                    {isLive ? 'LIVE' : 'SIMULATED'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
