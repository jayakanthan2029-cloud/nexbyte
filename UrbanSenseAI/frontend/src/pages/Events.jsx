import React from 'react';
import { History, AlertTriangle, Droplets, AlertOctagon, Activity, Navigation } from 'lucide-react';

export default function Events({ events, onViewMap }) {
  const getEventIcon = (type) => {
    switch (type) {
      case 'POTHOLE': return { icon: AlertTriangle, color: '#f97316', bg: 'rgba(249,115,22,0.15)' };
      case 'WATERLOGGING': return { icon: Droplets, color: '#3b82f6', bg: 'rgba(59,130,246,0.15)' };
      case 'ROAD_HAZARD': return { icon: AlertTriangle, color: 'var(--amber-400)', bg: 'rgba(245,158,11,0.15)' };
      case 'INCIDENT_DETECTED':
      case 'Potential Collision': return { icon: AlertOctagon, color: 'var(--rose-400)', bg: 'rgba(239,68,68,0.15)' };
      default: return { icon: Activity, color: 'var(--cyan-400)', bg: 'rgba(6,182,212,0.15)' };
    }
  };

  return (
    <div>
      <div className="glass-card" style={{ marginBottom: '20px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: '800' }}>Chronological Civic Event Timeline</h2>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Stream of real-time edge telemetry events captured by public transit buses.
        </p>
      </div>

      {events.length === 0 ? (
        <div className="glass-card" style={{ padding: '60px', textAlign: 'center', color: 'var(--text-dark)' }}>
          <History size={48} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
          <h3>No Events Recorded Yet</h3>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {events.map((evt) => {
            const config = getEventIcon(evt.event_type);
            const Icon = config.icon;

            return (
              <div
                key={evt.id}
                className="glass-card"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 20px',
                  borderLeft: `4px solid ${config.color}`
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '8px',
                    background: config.bg,
                    color: config.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <Icon size={20} />
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '0.92rem', fontWeight: '700', color: config.color }}>
                        {evt.event_type}
                      </span>
                      <span style={{ fontSize: '0.72rem', background: 'rgba(255,255,255,0.08)', padding: '2px 8px', borderRadius: '4px' }}>
                        {evt.bus_id}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--emerald-400)', fontWeight: '600' }}>
                        {evt.status}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginTop: '3px' }}>
                      {evt.description}
                    </div>

                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      GPS: {evt.latitude?.toFixed(5)}, {evt.longitude?.toFixed(5)}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: '600', fontFamily: 'var(--font-mono)' }}>
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dark)' }}>
                      {new Date(evt.timestamp).toLocaleDateString()}
                    </div>
                  </div>

                  <button
                    className="btn btn-outline"
                    style={{ padding: '6px 10px' }}
                    onClick={() => onViewMap(evt.bus_id)}
                    title="Locate on Map"
                  >
                    <Navigation size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
