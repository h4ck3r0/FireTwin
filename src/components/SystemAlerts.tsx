'use client';

import React, { useState, useEffect } from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface SystemAlertsProps {
  state: any;
}

export function SystemAlerts({ state }: SystemAlertsProps) {
  const [logs, setLogs] = useState<Array<{ id: number; type: string; message: string; time: string }>>([]);

  useEffect(() => {
    // Add alerts based on system state
    const newLogs: typeof logs = [];
    
    if (state.headerPressure < 1.5) {
      newLogs.push({
        id: Date.now(),
        type: 'CRITICAL',
        message: 'Header pressure critically low - system may fail to respond',
        time: new Date().toLocaleTimeString(),
      });
    }
    
    if (state.headerPressure > 10) {
      newLogs.push({
        id: Date.now() + 1,
        type: 'CRITICAL',
        message: 'Header pressure exceeds safe limit - potential system damage',
        time: new Date().toLocaleTimeString(),
      });
    }
    
    if (state.waterLevel < 50) {
      newLogs.push({
        id: Date.now() + 2,
        type: 'CRITICAL',
        message: 'Water reserve critically low - insufficient for emergency',
        time: new Date().toLocaleTimeString(),
      });
    }
    
    if (state.dieselLevel < 50) {
      newLogs.push({
        id: Date.now() + 3,
        type: 'WARNING',
        message: 'Diesel fuel level low - refuel recommended',
        time: new Date().toLocaleTimeString(),
      });
    }

    if (state.batteryHealth === 'Critical') {
      newLogs.push({
        id: Date.now() + 4,
        type: 'CRITICAL',
        message: 'Battery health critical - replacement recommended',
        time: new Date().toLocaleTimeString(),
      });
    }

    if (newLogs.length > 0) {
      setLogs(prev => [...newLogs, ...prev.slice(0, 4)]);
    }
  }, [state.headerPressure, state.waterLevel, state.dieselLevel, state.batteryHealth]);

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'CRITICAL':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'WARNING':
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      default:
        return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
  };

  const getAlertBg = (type: string) => {
    switch (type) {
      case 'CRITICAL':
        return 'bg-red-900/20 border-red-500/50';
      case 'WARNING':
        return 'bg-orange-900/20 border-orange-500/50';
      default:
        return 'bg-green-900/20 border-green-500/50';
    }
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <AlertCircle className="w-5 h-5" />
        System Alerts & Logs
      </h3>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {logs.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="w-12 h-12 text-green-500/50 mx-auto mb-3" />
            <p className="text-dark-text/70">All systems operating normally</p>
          </div>
        ) : (
          logs.map(log => (
            <div key={log.id} className={`border rounded-lg p-3 ${getAlertBg(log.type)}`}>
              <div className="flex items-start gap-3">
                {getAlertIcon(log.type)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-white">{log.type}</p>
                  <p className="text-sm text-dark-text/80 line-clamp-2">{log.message}</p>
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs text-dark-text/60 mt-2 ml-8">
                <Clock className="w-3 h-3" />
                {log.time}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
