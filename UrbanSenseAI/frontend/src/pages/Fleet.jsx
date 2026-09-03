import React from 'react';
import { Bus, Video, Cpu, Navigation, Activity } from 'lucide-react';

export default function Fleet({ buses, onViewMap }) {
  return (
    <div>
      <div className="glass-card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: '800' }}>Public Transit Fleet Nodes</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Real-time monitoring of physical edge bus and digitally simulated fleet nodes.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <span className="bus-live-badge">1 REAL LIVE PROTOTYPE</span>
            <span style={{
              background: 'rgba(6,182,212,0.15)',
              border: '1px solid var(--cyan-500)',
              color: 'var(--cyan-400)',
              padding: '3px 10px',
              borderRadius: '12px',
              fontSize: '0.75rem',
              fontWeight: '700'
            }}>
              4 SIMULATED FLEET BUSES
            </span>
          </div>
        </div>
      </div>

      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        <table className="fleet-table">
          <thead>
            <tr>
              <th>Bus ID</th>
              <th>Node Type</th>
              <th>Registration</th>
              <th>Route Name</th>
              <th>Status</th>
              <th>Camera</th>
              <th>AI Engine</th>
              <th>GPS Coordinates</th>
              <th>Last Ping</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {buses.map((bus) => {
              const isLive = bus.bus_id === 'BUS-001';
              return (
                <tr key={bus.bus_id} style={{ background: isLive ? 'rgba(16,185,129,0.03)' : 'transparent' }}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Bus size={16} color={isLive ? 'var(--emerald-400)' : 'var(--cyan-400)'} />
                      <strong style={{ fontSize: '0.95rem', color: isLive ? 'var(--emerald-400)' : 'var(--text-main)' }}>
                        {bus.bus_id}
                      </strong>
                    </div>
                  </td>
                  <td>
                    {isLive ? (
                      <span className="bus-live-badge" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                        LIVE PROTOTYPE
                      </span>
                    ) : (
                      <span style={{
                        background: 'rgba(6,182,212,0.12)',
                        color: 'var(--cyan-400)',
                        padding: '2px 8px',
                        borderRadius: '6px',
                        fontSize: '0.68rem',
                        fontWeight: '700'
                      }}>
                        SIMULATED
                      </span>
                    )}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                    {bus.registration_number || 'N/A'}
                  </td>
                  <td>{bus.route_name || 'Downtown Route'}</td>
                  <td>
                    <span style={{
                      color: bus.status === 'ACTIVE' ? 'var(--emerald-400)' : 'var(--text-muted)',
                      fontWeight: '600'
                    }}>
                      ● {bus.status}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      color: bus.camera_status === 'CONNECTED' ? 'var(--emerald-400)' : 'var(--text-muted)'
                    }}>
                      {bus.camera_status}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: isLive ? 'var(--cyan-400)' : 'var(--text-muted)' }}>
                      {isLive ? 'YOLO11n CUDA' : 'Simulated AI'}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {bus.latitude ? `${bus.latitude.toFixed(4)}, ${bus.longitude.toFixed(4)}` : 'GPS OK'}
                  </td>
                  <td style={{ fontSize: '0.78rem', color: 'var(--text-dark)' }}>
                    {bus.last_seen ? new Date(bus.last_seen).toLocaleTimeString() : 'Just now'}
                  </td>
                  <td>
                    <button
                      className="btn btn-outline"
                      style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                      onClick={() => onViewMap(bus.bus_id)}
                    >
                      Locate
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
