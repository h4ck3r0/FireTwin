'use client';

import React, { useState } from 'react';
import { AlertTriangle, Zap } from 'lucide-react';

interface EmergencyModeProps {
  state: any;
  onEmergencyStart: () => void;
}

export function EmergencyMode({ state, onEmergencyStart }: EmergencyModeProps) {
  const [emergencyActive, setEmergencyActive] = useState(false);

  const handleEmergency = () => {
    setEmergencyActive(!emergencyActive);
    if (!emergencyActive) {
      onEmergencyStart();
    }
  };

  return (
    <div className={`border-2 rounded-lg p-6 transition-all ${
      emergencyActive
        ? 'bg-red-900/30 border-red-500'
        : 'bg-dark-card border-dark-border'
    }`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <AlertTriangle className={`w-6 h-6 ${emergencyActive ? 'text-red-500' : 'text-dark-text'}`} />
          <div>
            <h3 className="text-lg font-semibold text-white">Emergency Mode</h3>
            <p className="text-sm text-dark-text/70">Auto-start all pumps at maximum capacity</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-3 py-1 rounded ${
          emergencyActive
            ? 'bg-red-500/80 text-white animate-pulse'
            : 'bg-dark-border text-dark-text'
        }`}>
          {emergencyActive ? 'ACTIVE' : 'STANDBY'}
        </span>
      </div>

      <button
        onClick={handleEmergency}
        className={`w-full py-3 px-4 rounded font-bold transition-all ${
          emergencyActive
            ? 'bg-red-600 hover:bg-red-700 text-white'
            : 'bg-status-critical/20 hover:bg-status-critical/30 text-status-critical'
        }`}
      >
        {emergencyActive ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            EMERGENCY IN PROGRESS
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2">
            <Zap className="w-4 h-4" />
            ACTIVATE EMERGENCY MODE
          </span>
        )}
      </button>

      {emergencyActive && (
        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/50 rounded text-sm text-red-400 space-y-2">
          <p>🚨 <strong>FIRE EMERGENCY ACTIVATED</strong></p>
          <ul className="space-y-1 ml-4 list-disc">
            <li>All pumps running at maximum</li>
            <li>Main fire pump: ON</li>
            <li>Backup diesel pump: ON</li>
            <li>Jockey pump: Running maintenance</li>
          </ul>
        </div>
      )}
    </div>
  );
}
