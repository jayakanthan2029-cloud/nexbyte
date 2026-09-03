import React, { useState } from 'react';
import { AlertTriangle, Filter, Navigation, Calendar, CheckCircle } from 'lucide-react';

export default function Potholes({ events, onViewMap }) {
  const [timeFilter, setTimeFilter] = useState('ALL');

  // Filter for potholes & hazards
  const potholeEvents = events.filter(e => e.event_type === 'POTHOLE' || e.event_type === 'ROAD_HAZARD');

  const filteredPotholes = potholeEvents.filter(p => {
    if (timeFilter === 'ALL') return true;
    const date = new Date(p.timestamp);
    const now = new Date();
    const diffHours = (now - date) / (1000 * 60 * 60);

    if (timeFilter === 'TODAY') return diffHours <= 24;
    if (timeFilter === 'WEEK') return diffHours <= 24 * 7;
    if (timeFilter === 'MONTH') return diffHours <= 24 * 30;
    return true;
  });

  return (
    <div>
      <div className="glass-card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: '800' }}>Road Surface & Pothole Registry</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Mobile fleet detections registered across metropolitan transit corridors.
            </p>
          </div>

          {/* Time Filters */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Calendar size={15} color="var(--text-muted)" />
            {['ALL', 'TODAY', 'WEEK', 'MONTH'].map((f) => (
              <button
                key={f}
                className={`btn ${timeFilter === f ? 'btn-primary' : 'btn-outline'}`}
                style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                onClick={() => setTimeFilter(f)}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      {filteredPotholes.length === 0 ? (
        <div className="glass-card" style={{ padding: '60px', textAlign: 'center', color: 'var(--text-dark)' }}>
          <AlertTriangle size={48} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
          <h3>No Potholes Recorded For Selected Filter</h3>
          <p style={{ fontSize: '0.85rem', marginTop: '6px' }}>
            Press key 'p' in the edge AI engine to register a live demo road surface defect.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {filteredPotholes.map((p) => {
            const imageMedia = p.media?.find(m => m.media_type === 'IMAGE');

            return (
              <div key={p.id} className="glass-card" style={{ padding: '16px' }}>
                {/* Inspection Photo Preview */}
                <div style={{
                  height: '160px',
                  background: '#0e1320',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid var(--border-subtle)'
                }}>
                  {imageMedia ? (
                    <img
                      src={`/${imageMedia.file_path}`}
                      alt="Pothole Evidence"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <div style={{ textAlign: 'center', color: 'var(--text-dark)' }}>
                      <AlertTriangle size={32} style={{ margin: '0 auto 6px', opacity: 0.5 }} />
                      <div style={{ fontSize: '0.75rem' }}>Edge snapshot stored in media/potholes/</div>
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.88rem', fontWeight: '800', color: '#f97316' }}>
                    {p.event_type}
                  </span>
                  <span style={{ fontSize: '0.72rem', background: 'rgba(255,255,255,0.08)', padding: '2px 6px', borderRadius: '4px' }}>
                    {p.bus_id}
                  </span>
                </div>

                <p style={{ fontSize: '0.8rem', color: 'var(--text-main)', marginBottom: '10px' }}>
                  {p.description}
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                  <div>GPS: {p.latitude?.toFixed(4)}, {p.longitude?.toFixed(4)}</div>
                  <div>Confidence: <strong style={{ color: '#fff' }}>{Math.round((p.confidence || 0.88) * 100)}%</strong></div>
                  <div>Time: {new Date(p.timestamp).toLocaleTimeString()}</div>
                  <div>Status: <span style={{ color: 'var(--emerald-400)' }}>{p.status}</span></div>
                </div>

                <button
                  className="btn btn-outline"
                  style={{ width: '100%', fontSize: '0.78rem', justifyContent: 'center' }}
                  onClick={() => onViewMap(p.bus_id)}
                >
                  <Navigation size={13} /> View on GIS Map
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
