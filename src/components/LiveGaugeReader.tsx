'use client';

import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { readGaugeStatus, GaugeReading } from '@/lib/gaugeReaderService';

interface LiveGaugeProps {
  pollInterval?: number; // ms between polls
  filepath?: string;
  serverUrl?: string;
}

export function LiveGaugeReader({ 
  pollInterval = 500,
  filepath = '/gauge_status.json',
  serverUrl
}: LiveGaugeProps) {
  const [reading, setReading] = useState<GaugeReading | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Poll gauge status
    const interval = setInterval(async () => {
      try {
        // 1. Try local file first (fastest for local development)
        let response = await fetch(filepath);
        
        // 2. Fallback to server if local fails or we are in remote mode
        if (!response.ok && serverUrl) {
          response = await fetch(`${serverUrl}/api/gauge-status`);
        }

        if (!response.ok) {
          if (response.status !== 404) {
            setConnected(false);
          }
          return;
        }
        
        const data = await response.json();
        setReading(data);
        setError(null);
        setConnected(true);
        setLoading(false);
      } catch (err) {
        // Silent error to prevent UI flickering during network shifts
        setConnected(false);
      }
    }, pollInterval);

    return () => clearInterval(interval);
  }, [pollInterval, filepath, serverUrl]);

  const getStatusColor = () => {
    if (!connected) return 'bg-gray-500';
    if (!reading?.detection_success) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusText = () => {
    if (!connected) return 'Disconnected';
    if (!reading?.detection_success) return 'No Gauge Detected';
    return 'Connected';
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-dark-text">Live Gauge Reader</h3>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getStatusColor()} animate-pulse`} />
          <span className="text-xs text-dark-text/60">{getStatusText()}</span>
        </div>
      </div>

      {loading && !reading ? (
        <div className="text-center py-8">
          <p className="text-dark-text/60">Waiting for gauge data...</p>
        </div>
      ) : error && !reading ? (
        <div className="flex items-center gap-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
          <AlertCircle size={16} className="text-yellow-500" />
          <p className="text-sm text-yellow-600">{error}</p>
        </div>
      ) : reading ? (
        <div className="space-y-4">
          {/* Pressure Display */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-xs text-dark-text/60">Pressure</p>
              <p className="text-3xl font-bold text-green-400">
                {typeof reading?.pressure === 'number' ? reading.pressure.toFixed(1) : '—'}
              </p>
              <p className="text-xs text-dark-text/60">{reading?.unit || 'PSI'}</p>
            </div>

            <div className="space-y-1">
              <p className="text-xs text-dark-text/60">Angle</p>
              <p className="text-3xl font-bold text-blue-400">
                {typeof reading?.angle_degrees === 'number' ? reading.angle_degrees.toFixed(1) : '—'}°
              </p>
              <p className="text-xs text-dark-text/60">Needle Position</p>
            </div>
          </div>

          {/* Detection Status */}
          <div className="flex items-center gap-2 p-2 bg-dark-bg rounded">
            {reading.detection_success ? (
              <>
                <CheckCircle2 size={16} className="text-green-500" />
                <span className="text-sm text-green-400">Gauge detected</span>
              </>
            ) : (
              <>
                <AlertCircle size={16} className="text-yellow-500" />
                <span className="text-sm text-yellow-400">Detection failed</span>
              </>
            )}
          </div>

          {/* Gauge Name */}
          <div className="text-xs text-dark-text/60">
            Source: {reading.gauge_name}
          </div>

          {/* Last Update */}
          <div className="text-xs text-dark-text/40">
            Updated: {new Date(reading.timestamp * 1000).toLocaleTimeString()}
          </div>
        </div>
      ) : null}
    </div>
  );
}
