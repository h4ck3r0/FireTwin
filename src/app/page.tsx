
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ControlPanel } from '@/components/ControlPanel';
import { FireReadinessCard } from '@/components/FireReadinessCard';
import { RadialGauge } from '@/components/RadialGauge';
import { SupportSystemRow } from '@/components/SupportSystemRow';
import { PumpCard } from '@/components/PumpCard';
import { PumpSystemRealistic } from '@/components/PumpSystemRealistic';
import { AdvancedFeatures } from '@/components/AdvancedFeatures';
import { SystemAlerts } from '@/components/SystemAlerts';
import { SystemPerformance } from '@/components/SystemPerformance';
import { EmergencyMode } from '@/components/EmergencyMode';
import { LiveGaugeReader } from '@/components/LiveGaugeReader';
import { PumpRoomEngine, PumpRoomState } from '@/lib/pumpRoomEngine';
import { Menu, X } from 'lucide-react';

// Phone camera stream component
function PhoneCameraFeed() {
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-dark-text">📷 Live Camera Feed</h3>
        <span className="text-xs text-green-400 animate-pulse">● LIVE</span>
      </div>
      <img
        src="http://192.168.1.191:8080/video"
        alt="Phone Camera Feed"
        className="w-full rounded-lg"
        style={{ maxHeight: '300px', objectFit: 'cover' }}
      />
    </div>
  );
}

export default function Dashboard() {
  const [engine] = useState(() => new PumpRoomEngine());
  const [state, setState] = useState<PumpRoomState>(engine.getState());
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);

  // Single useEffect — WebSocket + state refresh
  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket('wss://firetwin-server-production.up.railway.app');
      wsRef.current = ws;
      ws.onclose = () => setTimeout(connect, 2000);
    };
    connect();

    const poll = async () => {
      try {
        const res = await fetch('https://firetwin-server-production.up.railway.app/api/state');
        const data = await res.json();
        const ps = data.pumpState;
        engine.setPumpMode('electric', ps.electricPump.mode);
        engine.setPumpMode('diesel', ps.dieselPump.mode);
        engine.setPumpMode('jockey', ps.jockeyPump.mode);
        setState({ ...engine.getState() });
      } catch (e) { }
    };

    const interval = setInterval(poll, 500);
    return () => clearInterval(interval);
  }, [engine]);

  // Toggle pump via server (dashboard buttons)
  const handlePumpToggle = async (pump: 'electric' | 'diesel' | 'jockey') => {
    await fetch('https://firetwin-server-production.up.railway.app/api/toggle-pump', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pump }),
    });
  };

  // For non-pump controls (pressure, diesel, water, battery)
  const updateState = () => setState(engine.getState());

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div
          className={`${sidebarOpen ? 'w-80' : 'w-0'
            } bg-dark-sidebar border-r border-dark-border transition-all duration-300 overflow-hidden flex flex-col`}
        >
          <div className="p-6 border-b border-dark-border">
            <h1 className="text-2xl font-bold text-white">FireDesk</h1>
            <p className="text-sm text-dark-text/70 mt-1">Pump Room Controller</p>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            <ControlPanel
              state={state}
              onPressureChange={(pressure) => {
                engine.setHeaderPressure(pressure);
                updateState();
              }}
              onDieselChange={(level) => {
                engine.setDieselLevel(level);
                updateState();
              }}
              onWaterChange={(level) => {
                engine.setWaterLevel(level);
                updateState();
              }}
              onBatteryChange={(health) => {
                engine.setBatteryHealth(health);
                updateState();
              }}
              onPumpToggle={(pump) => {
                handlePumpToggle(pump);
              }}
            />
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-dark-sidebar border-b border-dark-border px-6 py-4 flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-dark-card rounded-lg transition text-dark-text"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <h2 className="text-xl font-semibold">Fire Safety Pump Room</h2>
            <div className="w-10" />
          </div>

          {/* Dashboard Content */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-6 max-w-7xl">

              {/* Top Row: Fire Readiness and Header Pressure */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <FireReadinessCard
                    readiness={state.fireReadiness}
                    systemHealth={state.systemHealth}
                  />
                </div>
                <div className="lg:col-span-2 bg-dark-card border border-dark-border rounded-lg p-6">
                  <div className="flex items-center justify-center h-full">
                    <RadialGauge
                      value={state.headerPressure}
                      max={12}
                      unit="bar"
                      label="Header Pressure"
                      lowThreshold={2.0}
                      criticalThreshold={1.5}
                    />
                  </div>
                </div>
              </div>

              {/* Support System Row */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-dark-text">Support Systems</h3>
                <SupportSystemRow
                  dieselLevel={state.dieselLevel}
                  waterLevel={state.waterLevel}
                  batteryHealth={state.batteryHealth}
                />
              </div>

              {/* Live Camera + Gauge Reader */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <PhoneCameraFeed />
                </div>
                <div className="lg:col-span-1">
                  <LiveGaugeReader pollInterval={500} />
                </div>
              </div>

              {/* Realistic 2D Pump System Visualization */}
              <div>
                <PumpSystemRealistic state={state} />
              </div>

              {/* Pump Availability Grid */}
              <div>
                <h3 className="text-lg font-semibold mb-4 text-dark-text">Pump Status</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <PumpCard
                    name="Electric Pump"
                    pump={state.electricPump}
                    onToggle={() => handlePumpToggle('electric')}
                  />
                  <PumpCard
                    name="Diesel Pump"
                    pump={state.dieselPump}
                    onToggle={() => handlePumpToggle('diesel')}
                  />
                  <PumpCard
                    name="Jockey Pump"
                    pump={state.jockeyPump}
                    onToggle={() => handlePumpToggle('jockey')}
                  />
                </div>
              </div>

              {/* System Diagnostics */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 text-dark-text">System Diagnostics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-dark-text/60">Fire Readiness</p>
                    <p className="font-semibold text-dark-text">{state.fireReadiness}</p>
                  </div>
                  <div>
                    <p className="text-dark-text/60">System Health</p>
                    <p className="font-semibold text-dark-text">{state.systemHealth}</p>
                  </div>
                  <div>
                    <p className="text-dark-text/60">Header Pressure</p>
                    <p className="font-semibold text-dark-text">{state.headerPressure.toFixed(2)} bar</p>
                  </div>
                  <div>
                    <p className="text-dark-text/60">Diesel Reserve</p>
                    <p className="font-semibold text-dark-text">{state.dieselLevel.toFixed(0)}L</p>
                  </div>
                </div>
              </div>

              {/* Advanced Features */}
              <div>
                <AdvancedFeatures state={state} />
              </div>

              {/* System Performance */}
              <div>
                <SystemPerformance state={state} />
              </div>

              {/* System Alerts and Logs */}
              <div>
                <SystemAlerts state={state} />
              </div>

              {/* Emergency Mode */}
              <div>
                <EmergencyMode
                  state={state}
                  onEmergencyStart={() => {
                    engine.setPumpMode('electric', 'ON');
                    engine.setPumpMode('diesel', 'ON');
                    updateState();
                  }}
                />
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}