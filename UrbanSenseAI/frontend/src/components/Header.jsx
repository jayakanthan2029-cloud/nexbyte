import React from 'react';
import { ShieldCheck, Cpu, Database, Camera, Navigation, Wifi, RefreshCw } from 'lucide-react';

export default function Header({ health, wsStatus, onRefresh, activeTab }) {
  const getBadgeClass = (status) => {
    if (status === 'online' || status === 'connected' || status === 'running' || status === 'available') {
      return 'status-badge online';
    }
    if (status === 'standby' || status === 'reconnecting' || status === 'fallback') {
      return 'status-badge warning';
    }
    return 'status-badge offline';
  };

  const formatTitle = (tab) => {
    switch (tab) {
      case 'dashboard': return 'Live City Command Center';
      case 'map': return 'Interactive GIS Road Infrastructure Map';
      case 'buses': return 'Public Transit Fleet Management';
      case 'traffic': return 'Real-Time Traffic Intelligence & Flow';
      case 'incidents': return 'Collision Evidence & Audit Registry';
      case 'potholes': return 'Road Defect & Pothole Registry';
      case 'events': return 'Real-Time Civic Event Timeline';
      case 'settings': return 'System Architecture & Edge Node Config';
      default: return 'UrbanSenseAI Platform';
    }
  };

  return (
    <header className="top-header">
      <div className="header-left">
        <h1 className="page-heading">{formatTitle(activeTab)}</h1>
      </div>

      <div className="header-status-bar">
        {/* System Backend */}
        <div className={getBadgeClass(health.backend)} title="FastAPI Backend Status">
          <ShieldCheck size={14} />
          <span>SYSTEM: {(health.backend || 'ONLINE').toUpperCase()}</span>
          <span className="status-dot pulse" />
        </div>

        {/* Edge AI */}
        <div className={getBadgeClass(health.ai_engine)} title="Edge AI Engine (RTX 4060 Laptop GPU)">
          <Cpu size={14} />
          <span>EDGE AI: {(health.ai_engine || 'STANDBY').toUpperCase()}</span>
          <span className="status-dot" />
        </div>

        {/* Database */}
        <div className={getBadgeClass(health.database)} title="PostgreSQL 18 Database">
          <Database size={14} />
          <span>DB: {(health.database || 'CONNECTED').toUpperCase()}</span>
        </div>

        {/* Camera */}
        <div className={getBadgeClass(health.camera)} title="Phone IP Camera Feed">
          <Camera size={14} />
          <span>CAM: {(health.camera || 'DISCONNECTED').toUpperCase()}</span>
        </div>

        {/* GPS */}
        <div 
          className={health.gps === 'LIVE_GPS' || health.gps === 'live' ? 'status-badge online' : 'status-badge offline'} 
          title="Physical Phone GPS Fix"
        >
          <Navigation size={14} />
          <span>GPS: {health.gps === 'LIVE_GPS' || health.gps === 'live' ? 'LIVE GPS' : 'UNAVAILABLE'}</span>
        </div>

        {/* WebSocket */}
        <div className={wsStatus === 'connected' ? 'status-badge online' : 'status-badge warning'} title="WebSocket Live Stream">
          <Wifi size={14} />
          <span>WS: {wsStatus === 'connected' ? 'LIVE' : 'POLLING'}</span>
        </div>

        {/* Refresh Button */}
        <button className="btn btn-outline" onClick={onRefresh} style={{ padding: '6px 10px' }} title="Sync Latest Data">
          <RefreshCw size={14} />
        </button>
      </div>
    </header>
  );
}
