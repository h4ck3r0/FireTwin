'use client';

import React from 'react';
import { Power, Clock, Zap } from 'lucide-react';
import { PumpStatus } from '@/lib/pumpRoomEngine';

interface PumpCardProps {
  name: string;
  pump: PumpStatus;
  onToggle?: () => void;
}

export function PumpCard({ name, pump, onToggle }: PumpCardProps) {
  const isRunning = pump.status === 'Running';
  const isFault = pump.status === 'Fault';

  const statusColor = isFault
    ? 'text-status-critical'
    : isRunning
      ? 'text-status-ready'
      : 'text-dark-text/70';

  const statusBgColor = isFault
    ? 'bg-status-critical/10'
    : isRunning
      ? 'bg-status-ready/10'
      : 'bg-dark-bg';

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-dark-text">{name}</h3>
        <button
          onClick={onToggle}
          className={`p-2 rounded-lg transition ${
            pump.mode === 'ON'
              ? 'bg-status-ready/20 text-status-ready hover:bg-status-ready/30'
              : 'bg-dark-bg text-dark-text/50 hover:bg-dark-border'
          }`}
        >
          <Power size={20} />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Mode and Status */}
        <div className="space-y-1">
          <p className="text-xs text-dark-text/60">Mode</p>
          <p className="text-sm font-semibold text-dark-text">{pump.mode}</p>
        </div>

        <div className="space-y-1">
          <p className="text-xs text-dark-text/60">Status</p>
          <div className={`inline-block px-2 py-1 rounded text-xs font-semibold ${statusBgColor} ${statusColor}`}>
            {pump.status}
          </div>
        </div>

        {/* Run Hours */}
        <div className="space-y-1 flex items-center gap-2">
          <Clock size={16} className="text-dark-text/50" />
          <div>
            <p className="text-xs text-dark-text/60">Run Hours</p>
            <p className="text-sm font-semibold text-dark-text">
              {pump.runHours.toFixed(1)}h
            </p>
          </div>
        </div>

        {/* Efficiency */}
        <div className="space-y-1 flex items-center gap-2">
          <Zap size={16} className="text-dark-text/50" />
          <div>
            <p className="text-xs text-dark-text/60">Efficiency</p>
            <p className="text-sm font-semibold text-dark-text">{pump.efficiency}%</p>
          </div>
        </div>
      </div>

      {/* Efficiency Bar */}
      <div className="pt-3 border-t border-dark-border">
        <div className="flex items-center justify-between mb-1">
          <p className="text-xs text-dark-text/60">Efficiency Level</p>
          <p className="text-xs font-semibold text-dark-text">{pump.efficiency}%</p>
        </div>
        <div className="w-full h-2 bg-dark-bg rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              pump.efficiency >= 95
                ? 'bg-status-ready'
                : pump.efficiency >= 80
                  ? 'bg-status-warning'
                  : 'bg-status-critical'
            }`}
            style={{ width: `${pump.efficiency}%` }}
          />
        </div>
      </div>

      {/* Maintenance Alert */}
      {pump.runHours > 5000 && (
        <div className="bg-status-warning/10 border border-status-warning rounded px-2 py-1">
          <p className="text-xs text-status-warning font-medium">
            ⚠️ Service Due: {pump.runHours.toFixed(0)} hours
          </p>
        </div>
      )}
    </div>
  );
}
