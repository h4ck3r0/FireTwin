'use client';

import React from 'react';
import { AlertCircle, Zap, Thermometer, Droplets, Wrench, Clock } from 'lucide-react';

interface AdvancedFeaturesProps {
  state: any;
}

export function AdvancedFeatures({ state }: AdvancedFeaturesProps) {
  const features = [
    {
      icon: Zap,
      title: 'Battery Backup',
      status: state.batteryHealth,
      color: state.batteryHealth === 'Healthy' ? 'text-green-500' : state.batteryHealth === 'Low' ? 'text-orange-500' : 'text-red-500',
      description: `Battery: ${state.batteryHealth}`,
    },
    {
      icon: Thermometer,
      title: 'Temperature Monitor',
      status: '45°C',
      color: 'text-green-500',
      description: 'Engine temp normal',
    },
    {
      icon: Droplets,
      title: 'Flow Rate Monitor',
      status: state.electricPump.mode === 'ON' ? '120 L/min' : '0 L/min',
      color: state.electricPump.mode === 'ON' ? 'text-blue-500' : 'text-gray-500',
      description: 'Current flow rate',
    },
    {
      icon: Wrench,
      title: 'Maintenance Alert',
      status: state.electricPump.runHours > 500 ? 'DUE' : 'OK',
      color: state.electricPump.runHours > 500 ? 'text-orange-500' : 'text-green-500',
      description: `Next service in ${Math.max(0, 500 - Math.floor(state.electricPump.runHours))} hours`,
    },
    {
      icon: Clock,
      title: 'System Runtime',
      status: `${Math.floor(state.electricPump.runHours)}h`,
      color: 'text-blue-500',
      description: 'Electric pump total runtime',
    },
  ];

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Advanced Monitoring</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {features.map((feature, idx) => {
          const Icon = feature.icon;
          return (
            <div key={idx} className="bg-dark-sidebar border border-dark-border rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <Icon className={`w-6 h-6 ${feature.color}`} />
                {feature.status === 'DUE' && (
                  <AlertCircle className="w-5 h-5 text-orange-500" />
                )}
              </div>
              <div>
                <p className="text-xs text-dark-text">{feature.title}</p>
                <p className={`text-sm font-bold ${feature.color}`}>{feature.status}</p>
              </div>
              <p className="text-xs text-dark-text/70">{feature.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
