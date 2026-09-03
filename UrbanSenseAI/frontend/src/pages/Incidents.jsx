import React, { useState } from 'react';
import { AlertOctagon, CheckCircle, Video, Image, Navigation, X } from 'lucide-react';
import axios from 'axios';

export default function Incidents({ incidents, onViewMap, onRefresh }) {
  const [selectedIncident, setSelectedIncident] = useState(null);

  const handleMarkReviewed = async (incidentId) => {
    try {
      await axios.put(`/api/incidents/${incidentId}/status?status=REVIEWED`);
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error('Error updating status:', e);
    }
  };

  return (
    <div>
      <div className="glass-card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: '800' }}>Collision Evidence & Incident Registry</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Potential collisions detected by vehicle trajectory intersections with rolling video buffers and OCR.
            </p>
          </div>
          <span style={{
            background: 'rgba(239,68,68,0.15)',
            border: '1px solid var(--rose-500)',
            color: 'var(--rose-400)',
            padding: '4px 12px',
            borderRadius: '12px',
            fontSize: '0.78rem',
            fontWeight: '700'
          }}>
            {incidents.filter(i => i.status !== 'REVIEWED').length} PENDING REVIEW
          </span>
        </div>
      </div>

      {incidents.length === 0 ? (
        <div className="glass-card" style={{ padding: '60px', textAlign: 'center', color: 'var(--text-dark)' }}>
          <AlertOctagon size={48} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
          <h3>No Collision Incidents Recorded</h3>
          <p style={{ fontSize: '0.85rem', marginTop: '6px' }}>
            When an event or demo collision (key 'c' in AI engine) is detected, evidence will appear here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
          {incidents.map((inc) => {
            const isPending = inc.status !== 'REVIEWED';
            const videoMedia = inc.media?.find(m => m.media_type === 'VIDEO');
            const keyframes = inc.media?.filter(m => m.media_type?.startsWith('KEYFRAME')) || [];

            return (
              <div key={inc.incident_id} className="glass-card" style={{
                borderTop: `4px solid ${isPending ? 'var(--rose-500)' : 'var(--emerald-500)'}`,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontSize: '0.9rem', fontWeight: '800', color: isPending ? 'var(--rose-400)' : 'var(--emerald-400)' }}>
                      {inc.incident_type || 'Potential Collision'}
                    </span>
                    <span style={{
                      fontSize: '0.7rem',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontWeight: '700',
                      background: isPending ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)',
                      color: isPending ? 'var(--rose-400)' : 'var(--emerald-400)'
                    }}>
                      {inc.status}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginBottom: '10px' }}>
                    {inc.description}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                    <div>Bus ID: <strong style={{ color: '#fff' }}>{inc.bus_id}</strong></div>
                    <div>Time: <strong style={{ color: '#fff' }}>{new Date(inc.timestamp).toLocaleTimeString()}</strong></div>
                    <div>GPS: {inc.latitude?.toFixed(4)}, {inc.longitude?.toFixed(4)}</div>
                    <div>Plate: <strong style={{ color: 'var(--amber-400)' }}>{inc.plate_number || 'Analyzing...'}</strong></div>
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '8px 12px',
                    background: 'rgba(0,0,0,0.25)',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    marginBottom: '16px'
                  }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--cyan-400)' }}>
                      <Video size={14} /> {videoMedia ? 'MP4 Evidence Ready' : 'Buffer Captured'}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--text-muted)' }}>
                      <Image size={14} /> {keyframes.length || 3} Keyframes
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    className="btn btn-primary"
                    style={{ flex: 1, fontSize: '0.78rem', justifyContent: 'center' }}
                    onClick={() => setSelectedIncident(inc)}
                  >
                    <Video size={14} /> View Evidence
                  </button>
                  <button
                    className="btn btn-outline"
                    style={{ padding: '6px 10px' }}
                    onClick={() => onViewMap(inc.bus_id)}
                    title="View on Map"
                  >
                    <Navigation size={14} />
                  </button>
                  {isPending && (
                    <button
                      className="btn btn-outline"
                      style={{ padding: '6px 10px', color: 'var(--emerald-400)' }}
                      onClick={() => handleMarkReviewed(inc.incident_id)}
                      title="Mark Reviewed"
                    >
                      <CheckCircle size={14} />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Embedded Evidence Viewer Modal */}
      {selectedIncident && (
        <div className="modal-backdrop" onClick={() => setSelectedIncident(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: 'var(--rose-400)' }}>
                  Collision Evidence Package: {selectedIncident.incident_id}
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {selectedIncident.description}
                </p>
              </div>
              <button className="btn btn-outline" onClick={() => setSelectedIncident(null)}>
                <X size={16} />
              </button>
            </div>

            {/* Video Player */}
            <div style={{ background: '#000', borderRadius: '8px', overflow: 'hidden', marginBottom: '20px' }}>
              {selectedIncident.media?.find(m => m.media_type === 'VIDEO') ? (
                <video
                  controls
                  autoPlay
                  style={{ width: '100%', maxHeight: '420px', display: 'block' }}
                  src={`/${selectedIncident.media.find(m => m.media_type === 'VIDEO').file_path}`}
                >
                  Your browser does not support HTML5 video playback.
                </video>
              ) : (
                <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <Video size={36} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
                  <p>Rolling buffer video is being compiled by edge thread...</p>
                </div>
              )}
            </div>

            {/* Keyframe Images Side-by-Side */}
            <h4 style={{ fontSize: '0.9rem', fontWeight: '700', marginBottom: '10px' }}>
              Event Keyframes (Pre-Collision, Impact Frame, Post-Collision)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              {['KEYFRAME_PRE', 'KEYFRAME_EVENT', 'KEYFRAME_POST'].map((kfType, i) => {
                const kfMedia = selectedIncident.media?.find(m => m.media_type === kfType);
                const title = i === 0 ? 'Pre-Event (-10s)' : (i === 1 ? 'Impact Event' : 'Post-Event (+15s)');
                return (
                  <div key={kfType} style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '6px', overflow: 'hidden', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ padding: '6px 8px', fontSize: '0.72rem', fontWeight: '600', color: 'var(--text-muted)' }}>
                      {title}
                    </div>
                    {kfMedia ? (
                      <img
                        src={`/${kfMedia.file_path}`}
                        alt={title}
                        style={{ width: '100%', height: '140px', objectFit: 'cover' }}
                      />
                    ) : (
                      <div style={{ height: '140px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dark)', fontSize: '0.75rem' }}>
                        Keyframe Pending
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
