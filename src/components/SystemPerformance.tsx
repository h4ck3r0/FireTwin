'use client';

import React from 'react';
import { TrendingUp, Activity } from 'lucide-react';

interface SystemPerformanceProps {
  state: any;
}

export function SystemPerformance({ state }: SystemPerformanceProps) {
  // Calculate efficiency percentage
  const calculateEfficiency = () => {
    const electricEfficiency = state.electricPump.efficiency;
    const dieselEfficiency = state.dieselPump.efficiency;
    const jockeyEfficiency = state.jockeyPump.efficiency;
    return Math.round((electricEfficiency + dieselEfficiency + jockeyEfficiency) / 3);
  };

  // Calculate system reliability
  const calculateReliability = () => {
    const pumpStatus = 
      (state.electricPump.status === 'Standby' || state.electricPump.status === 'Running' ? 1 : 0) +
      (state.dieselPump.status === 'Standby' || state.dieselPump.status === 'Running' ? 1 : 0) +
      (state.jockeyPump.status === 'Standby' || state.jockeyPump.status === 'Running' ? 1 : 0);
    return Math.round((pumpStatus / 3) * 100);
  };

  const efficiency = calculateEfficiency();
  const reliability = calculateReliability();

  const getHealthColor = (value: number) => {
    if (value >= 95) return 'text-green-500';
    if (value >= 80) return 'text-blue-500';
    if (value >= 60) return 'text-orange-500';
    return 'text-red-500';
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <TrendingUp className="w-5 h-5" />
        System Performance
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* System Efficiency */}
        <div className="bg-dark-sidebar border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-dark-text">Pump Efficiency</p>
            <Activity className="w-4 h-4 text-blue-500" />
          </div>
          <p className={`text-2xl font-bold ${getHealthColor(efficiency)}`}>{efficiency}%</p>
          <div className="mt-3 bg-dark-bg rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all ${
                efficiency >= 95
                  ? 'bg-green-500'
                  : efficiency >= 80
                  ? 'bg-blue-500'
                  : efficiency >= 60
                  ? 'bg-orange-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${efficiency}%` }}
            />
          </div>
          <p className="text-xs text-dark-text/70 mt-2">Average efficiency across all pumps</p>
        </div>

        {/* System Reliability */}
        <div className="bg-dark-sidebar border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-dark-text">System Reliability</p>
            <Activity className="w-4 h-4 text-green-500" />
          </div>
          <p className={`text-2xl font-bold ${getHealthColor(reliability)}`}>{reliability}%</p>
          <div className="mt-3 bg-dark-bg rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all ${
                reliability >= 95
                  ? 'bg-green-500'
                  : reliability >= 80
                  ? 'bg-blue-500'
                  : reliability >= 60
                  ? 'bg-orange-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${reliability}%` }}
            />
          </div>
          <p className="text-xs text-dark-text/70 mt-2">Pump status and availability</p>
        </div>

        {/* Fuel & Water Status */}
        <div className="bg-dark-sidebar border border-dark-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-dark-text">Resource Status</p>
            <Activity className="w-4 h-4 text-yellow-500" />
          </div>
          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>Water</span>
                <span className="font-bold">{(state.waterLevel / 300 * 100).toFixed(0)}%</span>
              </div>
              <div className="bg-dark-bg rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    state.waterLevel < 50
                      ? 'bg-red-500'
                      : state.waterLevel < 100
                      ? 'bg-orange-500'
                      : 'bg-blue-500'
                  }`}
                  style={{ width: `${(state.waterLevel / 300) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>Diesel</span>
                <span className="font-bold">{(state.dieselLevel / 200 * 100).toFixed(0)}%</span>
              </div>
              <div className="bg-dark-bg rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    state.dieselLevel < 50
                      ? 'bg-red-500'
                      : state.dieselLevel < 100
                      ? 'bg-orange-500'
                      : 'bg-yellow-600'
                  }`}
                  style={{ width: `${(state.dieselLevel / 200) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
