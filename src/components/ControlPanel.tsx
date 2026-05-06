'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { PumpRoomState } from '@/lib/pumpRoomEngine';

interface ControlPanelProps {
  state: PumpRoomState;
  onPressureChange: (pressure: number) => void;
  onDieselChange: (level: number) => void;
  onWaterChange: (level: number) => void;
  onBatteryChange: (health: 'Healthy' | 'Low' | 'Critical') => void;
  onPumpToggle: (pump: 'electric' | 'diesel' | 'jockey') => void;
}

export function ControlPanel({
  state,
  onPressureChange,
  onDieselChange,
  onWaterChange,
  onBatteryChange,
  onPumpToggle,
}: ControlPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const quickAdjust = (value: number, delta: number, min: number, max: number) => {
    return Math.max(min, Math.min(max, value + delta));
  };

  return (
    <div className="bg-dark-sidebar border border-dark-border rounded-lg p-4 space-y-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-dark-text hover:text-white transition"
      >
        <h3 className="text-lg font-semibold">Manual Controls</h3>
        {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>

      {isExpanded && (
        <div className="space-y-4">
          {/* Header Pressure Control */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-dark-text">
              Header Pressure: {state.headerPressure.toFixed(2)} bar
            </label>
            <input
              type="range"
              min="0"
              max="12"
              step="0.1"
              value={state.headerPressure}
              onChange={(e) => onPressureChange(parseFloat(e.target.value))}
              className="w-full h-2 bg-dark-card rounded-lg appearance-none cursor-pointer accent-status-info"
            />
            <div className="flex gap-2">
              <button
                onClick={() => onPressureChange(quickAdjust(state.headerPressure, -0.5, 0, 12))}
                className="flex-1 px-3 py-1 bg-dark-card hover:bg-dark-border text-dark-text text-sm rounded transition"
              >
                -0.5
              </button>
              <button
                onClick={() => onPressureChange(quickAdjust(state.headerPressure, 0.5, 0, 12))}
                className="flex-1 px-3 py-1 bg-dark-card hover:bg-dark-border text-dark-text text-sm rounded transition"
              >
                +0.5
              </button>
            </div>
          </div>

          {/* Diesel Level Control */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-dark-text">
              Diesel Level: {state.dieselLevel.toFixed(0)} L
            </label>
            <input
              type="range"
              min="0"
              max="200"
              step="1"
              value={state.dieselLevel}
              onChange={(e) => onDieselChange(parseFloat(e.target.value))}
              className="w-full h-2 bg-dark-card rounded-lg appearance-none cursor-pointer accent-status-info"
            />
            <div className="flex gap-2">
              <button
                onClick={() => onDieselChange(quickAdjust(state.dieselLevel, -10, 0, 200))}
                className="flex-1 px-3 py-1 bg-dark-card hover:bg-dark-border text-dark-text text-sm rounded transition"
              >
                -10L
              </button>
              <button
                onClick={() => onDieselChange(quickAdjust(state.dieselLevel, 10, 0, 200))}
                className="flex-1 px-3 py-1 bg-dark-card hover:bg-dark-border text-dark-text text-sm rounded transition"
              >
                +10L
              </button>
            </div>
          </div>

          {/* Water Level Control */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-dark-text">
              Water Level: {state.waterLevel.toFixed(0)} kL
            </label>
            <input
              type="range"
              min="0"
              max="300"
              step="1"
              value={state.waterLevel}
              onChange={(e) => onWaterChange(parseFloat(e.target.value))}
              className="w-full h-2 bg-dark-card rounded-lg appearance-none cursor-pointer accent-status-info"
            />
            <div className="flex gap-2">
              <button
                onClick={() => onWaterChange(quickAdjust(state.waterLevel, -10, 0, 300))}
                className="flex-1 px-3 py-1 bg-dark-card hover:bg-dark-border text-dark-text text-sm rounded transition"
              >
                -10kL
              </button>
              <button
                onClick={() => onWaterChange(quickAdjust(state.waterLevel, 10, 0, 300))}
                className="flex-1 px-3 py-1 bg-dark-card hover:bg-dark-border text-dark-text text-sm rounded transition"
              >
                +10kL
              </button>
            </div>
          </div>

          {/* Battery Health Control */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-dark-text">
              Battery Health: {state.batteryHealth}
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['Healthy', 'Low', 'Critical'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => onBatteryChange(status)}
                  className={`px-3 py-2 rounded text-sm font-medium transition ${
                    state.batteryHealth === status
                      ? 'bg-status-info text-white'
                      : 'bg-dark-card hover:bg-dark-border text-dark-text'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>

          {/* Pump Toggles */}
          <div className="pt-4 border-t border-dark-border">
            <p className="text-sm font-medium text-dark-text mb-3">Pump Controls</p>
            <div className="space-y-2">
              {(['electric', 'diesel', 'jockey'] as const).map((pump) => (
                <button
                  key={pump}
                  onClick={() => onPumpToggle(pump)}
                  className={`w-full px-4 py-2 rounded font-medium transition ${
                    (state[`${pump}Pump` as keyof PumpRoomState] as any).mode === 'ON'
                      ? 'bg-status-ready text-white'
                      : 'bg-dark-card text-dark-text hover:bg-dark-border'
                  }`}
                >
                  {pump.charAt(0).toUpperCase() + pump.slice(1)} Pump:{' '}
                  {(state[`${pump}Pump` as keyof PumpRoomState] as any).mode}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
