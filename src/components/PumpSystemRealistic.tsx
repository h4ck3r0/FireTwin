'use client';

import React from 'react';
import { PumpRoomState } from '@/lib/pumpRoomEngine';
import { AlertCircle, AlertTriangle } from 'lucide-react';

interface PumpSystemRealisticProps {
  state: PumpRoomState;
}

export function PumpSystemRealistic({ state }: PumpSystemRealisticProps) {
  const getPressureStatus = () => {
    if (state.headerPressure < 1.5) return { level: 'CRITICAL_LOW', color: '#ef4444', label: 'CRITICAL LOW' };
    if (state.headerPressure < 2.0) return { level: 'LOW', color: '#f97316', label: 'LOW PRESSURE' };
    if (state.headerPressure > 10) return { level: 'CRITICAL_HIGH', color: '#ef4444', label: 'CRITICAL HIGH' };
    if (state.headerPressure > 8) return { level: 'HIGH', color: '#f97316', label: 'HIGH PRESSURE' };
    return { level: 'NORMAL', color: '#10b981', label: 'NORMAL' };
  };

  const pressureStatus = getPressureStatus();
  const isActivePump = (mode: string) => mode === 'ON';

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6 space-y-4">
      <h3 className="text-lg font-semibold text-white">Pump Room System (Realistic View)</h3>

      {/* Pressure Alert Box */}
      <div
        className={`p-4 rounded-lg border-2 flex items-start gap-3 ${
          pressureStatus.level.includes('CRITICAL')
            ? 'bg-red-900/20 border-red-500'
            : pressureStatus.level === 'LOW' || pressureStatus.level === 'HIGH'
            ? 'bg-orange-900/20 border-orange-500'
            : 'bg-green-900/20 border-green-500'
        }`}
      >
        <div className="mt-0.5">
          {pressureStatus.level.includes('CRITICAL') ? (
            <AlertCircle className="w-5 h-5 text-red-500" />
          ) : pressureStatus.level === 'LOW' || pressureStatus.level === 'HIGH' ? (
            <AlertTriangle className="w-5 h-5 text-orange-500" />
          ) : (
            <div className="w-5 h-5 bg-green-500 rounded-full"></div>
          )}
        </div>
        <div className="flex-1">
          <p className="font-bold text-white mb-1">{pressureStatus.label}</p>
          <p className="text-sm text-dark-text">
            {pressureStatus.level === 'CRITICAL_LOW'
              ? '🚨 CRITICAL: Pressure critically low! System may not respond to fire demands.'
              : pressureStatus.level === 'LOW'
              ? '⚠️ Warning: Pressure below recommended level. Jockey pump should maintain 2.0-2.5 bar.'
              : pressureStatus.level === 'CRITICAL_HIGH'
              ? '🚨 CRITICAL: Pressure exceeds safe limits (>10 bar)! Risk of system damage.'
              : pressureStatus.level === 'HIGH'
              ? '⚠️ Warning: Pressure above recommended range. Reduce flow or check diesel pump.'
              : '✓ Pressure within normal operating range (2.5-8 bar)'}
          </p>
        </div>
      </div>

      {/* Realistic System Diagram */}
      <svg
        viewBox="0 0 1200 500"
        className="w-full bg-dark-sidebar rounded-lg border border-dark-border"
        style={{ minHeight: '350px' }}
      >
        {/* Background */}
        <defs>
          <linearGradient id="tankGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#374151" />
            <stop offset="100%" stopColor="#1f2937" />
          </linearGradient>
          <linearGradient id="headerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4b5563" />
            <stop offset="100%" stopColor="#2d3748" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Water Tank (Left) */}
        <g id="waterTank">
          <rect x="50" y="80" width="140" height="280" fill="url(#tankGradient)" stroke="#3a4556" strokeWidth="2" rx="8" />
          {/* Water level */}
          <rect
            x="55"
            y={80 + (280 * (1 - state.waterLevel / 300))}
            width="130"
            height={280 * (state.waterLevel / 300)}
            fill={state.waterLevel < 50 ? '#ef4444' : state.waterLevel < 100 ? '#f97316' : '#3b82f6'}
            opacity="0.6"
            rx="6"
          />
          <text x="120" y="360" textAnchor="middle" fill="white" fontSize="13" fontWeight="bold">
            Water Tank
          </text>
          <text x="120" y="380" textAnchor="middle" fill="#9ca3af" fontSize="12">
            {state.waterLevel.toFixed(0)} kL
          </text>
        </g>

        {/* Diesel Tank (Right) */}
        <g id="dieselTank">
          <rect x="1010" y="80" width="140" height="280" fill="url(#tankGradient)" stroke="#3a4556" strokeWidth="2" rx="8" />
          {/* Diesel level */}
          <rect
            x="1015"
            y={80 + (280 * (1 - state.dieselLevel / 200))}
            width="130"
            height={280 * (state.dieselLevel / 200)}
            fill={state.dieselLevel < 50 ? '#ef4444' : state.dieselLevel < 100 ? '#f97316' : '#f59e0b'}
            opacity="0.6"
            rx="6"
          />
          <text x="1080" y="360" textAnchor="middle" fill="white" fontSize="13" fontWeight="bold">
            Diesel Tank
          </text>
          <text x="1080" y="380" textAnchor="middle" fill="#9ca3af" fontSize="12">
            {state.dieselLevel.toFixed(0)} L
          </text>
        </g>

        {/* Central Header Pressure Tank */}
        <g id="headerTank" filter="url(#glow)">
          <circle
            cx="600"
            cy="150"
            r="85"
            fill="url(#headerGradient)"
            stroke={pressureStatus.color}
            strokeWidth="4"
            opacity="0.9"
          />
          {/* Pressure indicator ring */}
          <circle cx="600" cy="150" r="75" fill="none" stroke={pressureStatus.color} strokeWidth="1" opacity="0.3" />
          <text x="600" y="130" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">
            Header Pressure
          </text>
          <text x="600" y="160" textAnchor="middle" fill={pressureStatus.color} fontSize="32" fontWeight="bold">
            {state.headerPressure.toFixed(2)}
          </text>
          <text x="600" y="180" textAnchor="middle" fill={pressureStatus.color} fontSize="12" fontWeight="bold">
            bar
          </text>
        </g>

        {/* Electric Pump (Top Left) */}
        <g id="electricPump">
          <rect
            x="150"
            y="30"
            width="100"
            height="80"
            fill="#1f2937"
            stroke={isActivePump(state.electricPump.mode) ? '#10b981' : '#6b7280'}
            strokeWidth="2.5"
            rx="8"
          />
          {isActivePump(state.electricPump.mode) && (
            <>
              <circle cx="165" cy="45" r="3" fill="#10b981" opacity="0.8" />
              <circle cx="165" cy="45" r="6" fill="none" stroke="#10b981" strokeWidth="1" opacity="0.5">
                <animate attributeName="r" values="6;12" dur="1.5s" repeatCount="indefinite" />
              </circle>
            </>
          )}
          <text x="200" y="55" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Electric
          </text>
          <text x="200" y="75" textAnchor="middle" fill={isActivePump(state.electricPump.mode) ? '#10b981' : '#9ca3af'} fontSize="13" fontWeight="bold">
            {state.electricPump.mode}
          </text>
        </g>

        {/* Diesel Pump (Top Right) */}
        <g id="dieselPump">
          <rect
            x="950"
            y="30"
            width="100"
            height="80"
            fill="#1f2937"
            stroke={isActivePump(state.dieselPump.mode) ? '#10b981' : '#6b7280'}
            strokeWidth="2.5"
            rx="8"
          />
          {isActivePump(state.dieselPump.mode) && (
            <>
              <circle cx="965" cy="45" r="3" fill="#10b981" opacity="0.8" />
              <circle cx="965" cy="45" r="6" fill="none" stroke="#10b981" strokeWidth="1" opacity="0.5">
                <animate attributeName="r" values="6;12" dur="1.5s" repeatCount="indefinite" />
              </circle>
            </>
          )}
          <text x="1000" y="55" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Diesel
          </text>
          <text x="1000" y="75" textAnchor="middle" fill={isActivePump(state.dieselPump.mode) ? '#10b981' : '#9ca3af'} fontSize="13" fontWeight="bold">
            {state.dieselPump.mode}
          </text>
        </g>

        {/* Jockey Pump (Bottom) */}
        <g id="jockeyPump">
          <rect
            x="550"
            y="380"
            width="100"
            height="80"
            fill="#1f2937"
            stroke={isActivePump(state.jockeyPump.mode) ? '#10b981' : '#6b7280'}
            strokeWidth="2.5"
            rx="8"
          />
          {isActivePump(state.jockeyPump.mode) && (
            <>
              <circle cx="565" cy="395" r="3" fill="#10b981" opacity="0.8" />
              <circle cx="565" cy="395" r="6" fill="none" stroke="#10b981" strokeWidth="1" opacity="0.5">
                <animate attributeName="r" values="6;12" dur="1.5s" repeatCount="indefinite" />
              </circle>
            </>
          )}
          <text x="600" y="415" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Jockey
          </text>
          <text x="600" y="435" textAnchor="middle" fill={isActivePump(state.jockeyPump.mode) ? '#10b981' : '#9ca3af'} fontSize="13" fontWeight="bold">
            {state.jockeyPump.mode}
          </text>
        </g>

        {/* Pipes/Connections */}
        {/* Water to Header */}
        <path
          d="M 190 220 Q 300 190 515 200"
          stroke="#3b82f6"
          strokeWidth="3"
          fill="none"
          opacity="0.7"
          strokeDasharray="5,3"
        />

        {/* Electric Pump to Header */}
        {isActivePump(state.electricPump.mode) && (
          <path
            d="M 200 110 Q 350 130 515 150"
            stroke="#10b981"
            strokeWidth="3"
            fill="none"
            strokeDasharray="5,3"
          >
            <animate attributeName="strokeDashoffset" values="0;8" dur="0.6s" repeatCount="indefinite" />
          </path>
        )}

        {/* Diesel Pump to Header */}
        {isActivePump(state.dieselPump.mode) && (
          <path
            d="M 1000 110 Q 850 130 685 150"
            stroke="#10b981"
            strokeWidth="3"
            fill="none"
            strokeDasharray="5,3"
          >
            <animate attributeName="strokeDashoffset" values="0;8" dur="0.6s" repeatCount="indefinite" />
          </path>
        )}

        {/* Jockey Pump to Header */}
        {isActivePump(state.jockeyPump.mode) && (
          <path
            d="M 600 380 Q 600 280 600 235"
            stroke="#10b981"
            strokeWidth="3"
            fill="none"
            strokeDasharray="5,3"
          >
            <animate attributeName="strokeDashoffset" values="0;8" dur="0.6s" repeatCount="indefinite" />
          </path>
        )}

        {/* System Status Info */}
        <g id="statusInfo">
          <rect x="50" y="410" width="280" height="70" fill="#1f2937" stroke="#3a4556" strokeWidth="1" rx="6" />
          <text x="190" y="430" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">
            Active Pumps:
          </text>
          <text
            x="190"
            y="450"
            textAnchor="middle"
            fill="#10b981"
            fontSize="11"
          >
            {[
              state.electricPump.mode === 'ON' && 'Electric',
              state.dieselPump.mode === 'ON' && 'Diesel',
              state.jockeyPump.mode === 'ON' && 'Jockey',
            ]
              .filter(Boolean)
              .join(', ') || 'None'}
          </text>
          <text x="190" y="468" textAnchor="middle" fill="#9ca3af" fontSize="10">
            {[
              state.electricPump.efficiency + '%',
              state.dieselPump.efficiency + '%',
              state.jockeyPump.efficiency + '%',
            ].join(' | ')}
          </text>
        </g>
      </svg>

      {/* Additional Info */}
      <div className="grid grid-cols-3 gap-4 mt-4">
        <div className="bg-dark-sidebar p-3 rounded border border-dark-border text-center">
          <p className="text-xs text-dark-text mb-1">Water Reserve</p>
          <p className={`text-lg font-bold ${state.waterLevel < 50 ? 'text-red-500' : state.waterLevel < 100 ? 'text-orange-500' : 'text-green-500'}`}>
            {(state.waterLevel / 300 * 100).toFixed(0)}%
          </p>
        </div>
        <div className="bg-dark-sidebar p-3 rounded border border-dark-border text-center">
          <p className="text-xs text-dark-text mb-1">Diesel Reserve</p>
          <p className={`text-lg font-bold ${state.dieselLevel < 50 ? 'text-red-500' : state.dieselLevel < 100 ? 'text-orange-500' : 'text-yellow-600'}`}>
            {(state.dieselLevel / 200 * 100).toFixed(0)}%
          </p>
        </div>
        <div className="bg-dark-sidebar p-3 rounded border border-dark-border text-center">
          <p className="text-xs text-dark-text mb-1">Pressure Status</p>
          <p className={`text-lg font-bold ${pressureStatus.color === '#ef4444' ? 'text-red-500' : pressureStatus.color === '#f97316' ? 'text-orange-500' : 'text-green-500'}`}>
            {pressureStatus.label}
          </p>
        </div>
      </div>
    </div>
  );
}
