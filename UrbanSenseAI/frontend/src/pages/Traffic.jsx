import React from 'react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid,
  Legend
} from 'recharts';
import { Activity, Car, Bike, Bus, Truck, AlertTriangle } from 'lucide-react';

export default function Traffic({ trafficRecords }) {
  // Sort chronologically for charts
  const sortedRecords = [...trafficRecords].reverse();

  // Chart data formatting
  const chartData = sortedRecords.slice(-15).map((t, idx) => ({
    time: new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    total: t.vehicle_count,
    cars: t.cars,
    bikes: t.motorcycles,
    buses: t.buses,
    trucks: t.trucks,
    movement: Math.round(t.movement_score * 100),
    bus_id: t.bus_id
  }));

  const latest = trafficRecords[0] || {
    vehicle_count: 18,
    cars: 10,
    motorcycles: 5,
    buses: 2,
    trucks: 1,
    movement_score: 0.22,
    traffic_level: 'MEDIUM',
    probable_reasons: ['High vehicle density', 'Low movement']
  };

  return (
    <div>
      {/* 1. Metric Cards */}
      <div className="kpi-grid">
        <div className="glass-card kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(6,182,212,0.12)', color: 'var(--cyan-400)' }}>
            <Activity size={22} />
          </div>
          <div>
            <div className="kpi-val" style={{ color: 'var(--cyan-400)' }}>{latest.vehicle_count}</div>
            <div className="kpi-lbl">Total Vehicles Count</div>
          </div>
        </div>

        <div className="glass-card kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(59,130,246,0.12)', color: 'var(--blue-500)' }}>
            <Car size={22} />
          </div>
          <div>
            <div className="kpi-val">{latest.cars}</div>
            <div className="kpi-lbl">Cars Detected</div>
          </div>
        </div>

        <div className="glass-card kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(16,185,129,0.12)', color: 'var(--emerald-400)' }}>
            <Bike size={22} />
          </div>
          <div>
            <div className="kpi-val">{latest.motorcycles}</div>
            <div className="kpi-lbl">Motorcycles / Bikes</div>
          </div>
        </div>

        <div className="glass-card kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(245,158,11,0.12)', color: 'var(--amber-400)' }}>
            <Bus size={22} />
          </div>
          <div>
            <div className="kpi-val">{latest.buses}</div>
            <div className="kpi-lbl">Buses Detected</div>
          </div>
        </div>

        <div className="glass-card kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(239,68,68,0.12)', color: 'var(--rose-400)' }}>
            <Truck size={22} />
          </div>
          <div>
            <div className="kpi-val">{latest.trucks}</div>
            <div className="kpi-lbl">Heavy Trucks</div>
          </div>
        </div>

        <div className="glass-card kpi-card">
          <div className="kpi-icon-box" style={{ background: 'rgba(168,85,247,0.12)', color: '#a855f7' }}>
            <Activity size={22} />
          </div>
          <div>
            <div className="kpi-val" style={{ color: '#a855f7' }}>{latest.movement_score}</div>
            <div className="kpi-lbl">Movement Score (0-1.0)</div>
          </div>
        </div>
      </div>

      {/* 2. Probable Reasons AI Intelligence Card */}
      <div className="glass-card" style={{ marginBottom: '20px', borderLeft: '4px solid var(--amber-500)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <AlertTriangle size={18} color="var(--amber-400)" />
          <h3 style={{ fontSize: '0.95rem', fontWeight: '700' }}>
            Traffic Bottleneck & Cause Analysis (Edge AI)
          </h3>
          <span style={{
            fontSize: '0.72rem',
            padding: '2px 8px',
            borderRadius: '4px',
            fontWeight: '700',
            background: latest.traffic_level === 'HIGH' ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)',
            color: latest.traffic_level === 'HIGH' ? 'var(--rose-400)' : 'var(--amber-400)'
          }}>
            LEVEL: {latest.traffic_level}
          </span>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {latest.probable_reasons && latest.probable_reasons.length > 0 
            ? latest.probable_reasons.join(', ')
            : 'Normal road conditions with steady kinetic displacement.'}
        </p>
      </div>

      {/* 3. Recharts Visualizations */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Chart 1: Vehicle Density Over Time */}
        <div className="glass-card">
          <h3 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '16px' }}>
            Vehicle Density Over Time (Edge Telemetry)
          </h3>
          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="totalColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="time" stroke="#6b7280" fontSize={11} />
                <YAxis stroke="#6b7280" fontSize={11} />
                <Tooltip contentStyle={{ background: '#0e1320', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="total" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#totalColor)" name="Total Vehicles" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Modal Split Breakdown */}
        <div className="glass-card">
          <h3 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '16px' }}>
            Modal Split Distribution (Cars, Bikes, Trucks)
          </h3>
          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="time" stroke="#6b7280" fontSize={11} />
                <YAxis stroke="#6b7280" fontSize={11} />
                <Tooltip contentStyle={{ background: '#0e1320', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="cars" fill="#3b82f6" name="Cars" stackId="a" />
                <Bar dataKey="bikes" fill="#10b981" name="Bikes" stackId="a" />
                <Bar dataKey="buses" fill="#f59e0b" name="Buses" stackId="a" />
                <Bar dataKey="trucks" fill="#ef4444" name="Trucks" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
