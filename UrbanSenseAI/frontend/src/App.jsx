import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import GISMap from './pages/GISMap';
import Fleet from './pages/Fleet';
import Traffic from './pages/Traffic';
import Incidents from './pages/Incidents';
import Potholes from './pages/Potholes';
import Events from './pages/Events';
import Settings from './pages/Settings';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState({
    backend: 'online',
    database: 'connected',
    ai_engine: 'standby',
    camera: 'disconnected',
    gps: 'available'
  });
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [summary, setSummary] = useState({});
  const [buses, setBuses] = useState([]);
  const [events, setEvents] = useState([]);
  const [trafficRecords, setTrafficRecords] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [selectedBusId, setSelectedBusId] = useState(null);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Fetch initial system state
  const fetchData = async () => {
    try {
      const [liveRes, healthRes] = await Promise.all([
        axios.get('/api/dashboard/live'),
        axios.get('/api/health')
      ]);

      if (liveRes.data) {
        setSummary(liveRes.data.summary || {});
        setBuses(liveRes.data.buses || []);
        setEvents(liveRes.data.recent_events || []);
        setTrafficRecords(liveRes.data.recent_traffic || []);
        setIncidents(liveRes.data.recent_incidents || []);
      }

      if (healthRes.data) {
        setHealth(healthRes.data);
      }
    } catch (err) {
      console.warn('Initial data fetch notice:', err.message);
    }
  };

  // WebSocket Connection Management
  useEffect(() => {
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/live`;

      console.log('Connecting to Live WebSocket at:', wsUrl);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket Connected to UrbanSenseAI backend');
        setWsStatus('connected');
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const { type, data } = message;

          if (type === 'BUS_LOCATION') {
            setBuses((prevBuses) =>
              prevBuses.map((b) =>
                b.bus_id === data.bus_id
                  ? { ...b, latitude: data.latitude, longitude: data.longitude, speed: data.speed, last_seen: data.timestamp }
                  : b
              )
            );
          } else if (type === 'TRAFFIC_UPDATE') {
            setTrafficRecords((prev) => [data, ...prev.slice(0, 49)]);
          } else if (type === 'POTHOLE_DETECTED' || type === 'WATERLOGGING_DETECTED' || type === 'ROAD_HAZARD_DETECTED') {
            setEvents((prev) => [data, ...prev.slice(0, 49)]);
            // Increment summary count dynamically
            setSummary((prev) => ({
              ...prev,
              live_events_count: (prev.live_events_count || 0) + 1,
              potholes_count: type === 'POTHOLE_DETECTED' ? (prev.potholes_count || 0) + 1 : prev.potholes_count
            }));
          } else if (type === 'INCIDENT_DETECTED') {
            setIncidents((prev) => [data, ...prev]);
            setSummary((prev) => ({
              ...prev,
              critical_incidents_count: (prev.critical_incidents_count || 0) + 1
            }));
          }
        } catch (e) {
          console.error('Error handling WS message:', e);
        }
      };

      ws.onclose = () => {
        setWsStatus('disconnected');
        console.warn('WebSocket disconnected. Will retry in 3 seconds...');
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = () => {
        setWsStatus('fallback');
        ws.close();
      };
    };

    fetchData();
    connectWebSocket();

    // Fallback polling every 5 seconds to keep health and summary updated
    const pollingInterval = setInterval(() => {
      fetchData();
    }, 5000);

    return () => {
      clearInterval(pollingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleViewMap = (busId) => {
    setSelectedBusId(busId);
    setActiveTab('map');
  };

  const handleViewIncident = (incident) => {
    setActiveTab('incidents');
  };

  const liveBus = buses.find((b) => b.bus_id === 'BUS-001') || {
    bus_id: 'BUS-001',
    status: 'ACTIVE',
    camera_status: health.camera === 'connected' ? 'CONNECTED' : 'DISCONNECTED',
    latitude: null,
    longitude: null,
    gps_status: 'UNAVAILABLE'
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Viewport */}
      <div className="main-wrapper">
        {/* Real-Time Status Header */}
        <Header
          health={health}
          wsStatus={wsStatus}
          onRefresh={fetchData}
          activeTab={activeTab}
        />

        {/* Dynamic Page Views */}
        <main className="content-area">
          {activeTab === 'dashboard' && (
            <Dashboard
              summary={summary}
              liveBus={liveBus}
              recentEvents={events}
              recentTraffic={trafficRecords}
              onViewMap={handleViewMap}
              onViewIncident={handleViewIncident}
            />
          )}

          {activeTab === 'map' && (
            <GISMap
              buses={buses}
              events={events}
              incidents={incidents}
              selectedBusId={selectedBusId}
              onSelectIncident={() => setActiveTab('incidents')}
            />
          )}

          {activeTab === 'buses' && (
            <Fleet
              buses={buses}
              onViewMap={handleViewMap}
            />
          )}

          {activeTab === 'traffic' && (
            <Traffic
              trafficRecords={trafficRecords}
            />
          )}

          {activeTab === 'incidents' && (
            <Incidents
              incidents={incidents}
              onViewMap={handleViewMap}
              onRefresh={fetchData}
            />
          )}

          {activeTab === 'potholes' && (
            <Potholes
              events={events}
              onViewMap={handleViewMap}
            />
          )}

          {activeTab === 'events' && (
            <Events
              events={events}
              onViewMap={handleViewMap}
            />
          )}

          {activeTab === 'settings' && (
            <Settings
              health={health}
            />
          )}
        </main>
      </div>
    </div>
  );
}
