import React from 'react';
import { 
  LayoutDashboard, 
  Map, 
  Bus, 
  Activity, 
  AlertOctagon, 
  AlertTriangle, 
  History, 
  Settings,
  Radio
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'map', label: 'GIS Live Map', icon: Map },
    { id: 'buses', label: 'Bus Fleet', icon: Bus },
    { id: 'traffic', label: 'Traffic Analysis', icon: Activity },
    { id: 'incidents', label: 'Incidents & Evidence', icon: AlertOctagon },
    { id: 'potholes', label: 'Potholes & Hazards', icon: AlertTriangle },
    { id: 'events', label: 'Event Timeline', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">
          <Radio size={20} color="#090d16" />
        </div>
        <div>
          <div className="sidebar-title">UrbanSenseAI</div>
          <div className="sidebar-subtitle">SIH26124 Mobile Edge</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      {/* Fleet Prototype Tag in sidebar footer */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)', background: 'rgba(0,0,0,0.2)' }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-dark)', textTransform: 'uppercase', marginBottom: '6px' }}>
          Edge Node Target
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--emerald-400)' }}>BUS-001</span>
          <span style={{ fontSize: '0.68rem', background: 'rgba(16,185,129,0.15)', color: 'var(--emerald-400)', padding: '2px 6px', borderRadius: '4px', fontWeight: '600' }}>
            PHYSICAL
          </span>
        </div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          RTX 4060 CUDA Active
        </div>
      </div>
    </aside>
  );
}
