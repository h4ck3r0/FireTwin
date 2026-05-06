'use client';

import React from 'react';
import { Droplet, Battery } from 'lucide-react';

interface SupportSystemRowProps {
  dieselLevel: number;
  waterLevel: number;
  batteryHealth: 'Healthy' | 'Low' | 'Critical';
}

export function SupportSystemRow({
  dieselLevel,
  waterLevel,
  batteryHealth,
}: SupportSystemRowProps) {
  const dieselPercentage = (dieselLevel / 200) * 100;
  const waterPercentage = (waterLevel / 300) * 100;

  const getBatteryColor = () => {
    switch (batteryHealth) {
      case 'Healthy':
        return 'text-status-ready';
      case 'Low':
        return 'text-status-warning';
      case 'Critical':
        return 'text-status-critical';
    }
  };

  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Diesel Level Gauge */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-semibold text-dark-text">Diesel Level</h3>
        <div className="space-y-2">
          <div className="w-full bg-dark-bg rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all ${
                dieselLevel < 50 ? 'bg-status-warning' : 'bg-status-ready'
              }`}
              style={{ width: `${dieselPercentage}%` }}
            />
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-dark-text font-semibold">{dieselLevel.toFixed(0)}L</span>
            <span className="text-dark-text/60">200L</span>
          </div>
        </div>
        {dieselLevel < 50 && (
          <p className="text-xs text-status-warning font-medium">Low Fuel Warning</p>
        )}
      </div>

      {/* Water Level Circular Progress */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-4 flex flex-col items-center justify-center space-y-3">
        <div className="relative w-24 h-24">
          <svg
            className="absolute inset-0 transform -rotate-90"
            viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#3a4556"
              strokeWidth="6"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#3b82f6"
              strokeWidth="6"
              strokeDasharray={`${waterPercentage * 2.83} 283`}
              strokeLinecap="round"
              style={{ transition: 'stroke-dasharray 0.5s ease-in-out' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <p className="text-lg font-bold text-dark-text">
              {waterPercentage.toFixed(0)}%
            </p>
            <Droplet size={16} className="text-status-info" />
          </div>
        </div>
        <p className="text-xs text-dark-text/70">{waterLevel.toFixed(0)} kL / 300 kL</p>
      </div>

      {/* Battery Health */}
      <div className="bg-dark-card border border-dark-border rounded-lg p-4 flex flex-col items-center justify-center space-y-3">
        <Battery size={32} className={getBatteryColor()} />
        <div className="text-center space-y-1">
          <p className="text-sm font-semibold text-dark-text">Battery</p>
          <p className={`text-xs font-medium ${getBatteryColor()}`}>
            {batteryHealth}
          </p>
        </div>
        <div className="w-full h-1 bg-dark-bg rounded-full overflow-hidden">
          <div
            className={`h-full ${
              batteryHealth === 'Healthy'
                ? 'bg-status-ready'
                : batteryHealth === 'Low'
                  ? 'bg-status-warning'
                  : 'bg-status-critical'
            }`}
            style={{
              width:
                batteryHealth === 'Healthy'
                  ? '100%'
                  : batteryHealth === 'Low'
                    ? '50%'
                    : '20%',
            }}
          />
        </div>
      </div>
    </div>
  );
}
