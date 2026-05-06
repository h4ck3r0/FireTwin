'use client';

import React from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';

interface FireReadinessCardProps {
  readiness: 'READY' | 'NEEDS_ATTENTION' | 'CRITICAL';
  systemHealth: 'HEALTHY' | 'WARNING' | 'CRITICAL';
}

export function FireReadinessCard({ readiness, systemHealth }: FireReadinessCardProps) {
  const isReady = readiness === 'READY';
  const statusColors = {
    READY: {
      bg: 'bg-status-ready/10',
      border: 'border-status-ready',
      text: 'text-status-ready',
      icon: CheckCircle,
    },
    NEEDS_ATTENTION: {
      bg: 'bg-status-warning/10',
      border: 'border-status-warning',
      text: 'text-status-warning',
      icon: AlertCircle,
    },
    CRITICAL: {
      bg: 'bg-status-critical/10',
      border: 'border-status-critical',
      text: 'text-status-critical',
      icon: AlertCircle,
    },
  };

  const config = statusColors[readiness];
  const Icon = config.icon;

  return (
    <div
      className={`${config.bg} border-2 ${config.border} rounded-lg p-6 space-y-4`}
    >
      <div className="flex items-center gap-3">
        <Icon size={32} className={config.text} />
        <div>
          <p className="text-sm text-dark-text/70">Fire Readiness Status</p>
          <p className={`text-3xl font-bold ${config.text}`}>
            {readiness === 'READY' ? 'READY' : 'NEEDS ATTENTION'}
          </p>
        </div>
      </div>

      <div className="pt-4 border-t border-dark-border">
        <p className="text-xs text-dark-text/60 mb-2">System Health</p>
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              systemHealth === 'HEALTHY'
                ? 'bg-status-ready'
                : systemHealth === 'WARNING'
                  ? 'bg-status-warning'
                  : 'bg-status-critical'
            }`}
          />
          <span className="text-sm font-medium text-dark-text">
            {systemHealth}
          </span>
        </div>
      </div>
    </div>
  );
}
