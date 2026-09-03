import React from 'react';
import { Cpu, HardDrive, Camera, Navigation, Database, Terminal, Shield } from 'lucide-react';

export default function Settings({ health }) {
  return (
    <div>
      <div className="glass-card" style={{ marginBottom: '20px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: '800' }}>System Architecture & Edge Node Configuration</h2>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          SIH 2026 Problem Statement SIH26124 Prototype Settings & Diagnostics.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Hardware & Acceleration Spec */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Cpu size={20} color="var(--emerald-400)" />
            <h3 style={{ fontSize: '0.95rem', fontWeight: '700' }}>Edge Compute & Hardware Specs</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Edge Platform:</span>
              <strong style={{ color: '#fff' }}>Windows 11 Laptop (Prototype)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>CPU:</span>
              <strong style={{ color: '#fff' }}>Intel Core i7-13650HX (14 Cores / 20 Threads)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Discrete GPU:</span>
              <strong style={{ color: 'var(--emerald-400)' }}>NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>CUDA Build:</span>
              <strong style={{ color: 'var(--cyan-400)' }}>PyTorch 2.11.0 + cu128 (Accelerated)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>System Memory:</span>
              <strong style={{ color: '#fff' }}>24GB DDR5 RAM</strong>
            </div>
          </div>
        </div>

        {/* Vision & Camera Configuration */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Camera size={20} color="var(--cyan-400)" />
            <h3 style={{ fontSize: '0.95rem', fontWeight: '700' }}>Camera Stream & Models</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Camera Source:</span>
              <strong style={{ color: 'var(--cyan-400)', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
                Configurable via .env (IP Camera / Webcam / File)
              </strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Primary Detector:</span>
              <strong style={{ color: '#fff' }}>YOLO11n (COCO Vehicles: Car, Bike, Bus, Truck)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Tracking Algorithm:</span>
              <strong style={{ color: '#fff' }}>ByteTrack (Persistent Track IDs)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Custom Urban Model:</span>
              <strong style={{ color: 'var(--amber-400)' }}>models/urban_model.pt (Graceful Adapter)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,0,0,0.2)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Primary Database:</span>
              <strong style={{ color: 'var(--emerald-400)' }}>PostgreSQL 18 (urbansense)</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Keyboard Controls & Demo Hotkeys */}
      <div className="glass-card" style={{ marginTop: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <Terminal size={20} color="var(--amber-400)" />
          <h3 style={{ fontSize: '0.95rem', fontWeight: '700' }}>Edge AI Interactive Hotkeys (OpenCV Window)</h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          <div style={{ padding: '12px', background: 'rgba(0,0,0,0.25)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <kbd style={{ background: '#374151', padding: '3px 8px', borderRadius: '4px', fontFamily: 'var(--font-mono)', fontWeight: 'bold' }}>Q</kbd>
            <div style={{ marginTop: '6px', fontWeight: '600', fontSize: '0.85rem' }}>Quit Application</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Releases camera stream and closes edge window.</div>
          </div>

          <div style={{ padding: '12px', background: 'rgba(0,0,0,0.25)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <kbd style={{ background: '#374151', padding: '3px 8px', borderRadius: '4px', fontFamily: 'var(--font-mono)', fontWeight: 'bold' }}>P</kbd>
            <div style={{ marginTop: '6px', fontWeight: '600', fontSize: '0.85rem', color: '#f97316' }}>Trigger Demo Pothole</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Annotates defect, saves to media/potholes/, logs event.</div>
          </div>

          <div style={{ padding: '12px', background: 'rgba(0,0,0,0.25)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <kbd style={{ background: '#374151', padding: '3px 8px', borderRadius: '4px', fontFamily: 'var(--font-mono)', fontWeight: 'bold' }}>W</kbd>
            <div style={{ marginTop: '6px', fontWeight: '600', fontSize: '0.85rem', color: '#3b82f6' }}>Trigger Demo Waterlogging</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Saves waterlogging snapshot and transmits GPS alert.</div>
          </div>

          <div style={{ padding: '12px', background: 'rgba(0,0,0,0.25)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <kbd style={{ background: '#374151', padding: '3px 8px', borderRadius: '4px', fontFamily: 'var(--font-mono)', fontWeight: 'bold' }}>C</kbd>
            <div style={{ marginTop: '6px', fontWeight: '600', fontSize: '0.85rem', color: 'var(--rose-400)' }}>Potential Collision Workflow</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Locks ~10s pre-buffer, records +15s, exports ~25s MP4 & 3 keyframes.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
