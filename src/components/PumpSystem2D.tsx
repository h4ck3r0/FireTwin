'use client';

import React from 'react';
import { PumpRoomState } from '@/lib/pumpRoomEngine';

interface PumpSystem2DProps {
  state: PumpRoomState;
}

export function PumpSystem2D({ state }: PumpSystem2DProps) {
  const getPumpColor = (mode: 'ON' | 'OFF', status: string) => {
    if (mode === 'ON') {
      return status === 'Running' ? '#10b981' : '#f59e0b'; 
    }
    return '#6b7280'; 
  };

  const getPressureColor = () => {
    if (state.headerPressure < 1.5) return '#ef4444'; 
    if (state.headerPressure < 2.0) return '#f97316'; 
    if (state.headerPressure > 10) return '#ef4444'; 
    if (state.headerPressure > 8) return '#f97316'; 
    return '#10b981'; 
  };

  const getWaterColor = () => {
    if (state.waterLevel < 50) return '#ef4444'; 
    if (state.waterLevel < 100) return '#f97316'; 
    return '#10b981'; 
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-6">Pump Room System (2D View)</h3>

      <svg
        viewBox="0 0 1000 600"
        className="w-full bg-dark-sidebar rounded-lg border border-dark-border"
        style={{ minHeight: '400px' }}
      >
        {/* Background grid */}
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="#374151"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="1000" height="600" fill="url(#grid)" />

        {/* Central Header Pressure Tank */}
        <g>
          <circle
            cx="500"
            cy="300"
            r="80"
            fill="#1f2937"
            stroke={getPressureColor()}
            strokeWidth="3"
          />
          <text
            x="500"
            y="280"
            textAnchor="middle"
            fill="white"
            fontSize="14"
            fontWeight="bold"
          >
            Header Pressure
          </text>
          <text
            x="500"
            y="305"
            textAnchor="middle"
            fill={getPressureColor()}
            fontSize="24"
            fontWeight="bold"
          >
            {state.headerPressure.toFixed(2)}
          </text>
          <text
            x="500"
            y="325"
            textAnchor="middle"
            fill="white"
            fontSize="12"
          >
            bar
          </text>
        </g>

        {/* Electric Pump - Left */}
        <g>
          <rect
            x="100"
            y="150"
            width="120"
            height="100"
            fill="#1f2937"
            stroke={getPumpColor(
              state.electricPump.mode,
              state.electricPump.status
            )}
            strokeWidth="2"
            rx="5"
          />
          <text
            x="160"
            y="175"
            textAnchor="middle"
            fill="white"
            fontSize="14"
            fontWeight="bold"
          >
            Electric Pump
          </text>
          <text
            x="160"
            y="200"
            textAnchor="middle"
            fill={getPumpColor(
              state.electricPump.mode,
              state.electricPump.status
            )}
            fontSize="16"
            fontWeight="bold"
          >
            {state.electricPump.mode}
          </text>
          <text
            x="160"
            y="220"
            textAnchor="middle"
            fill="#9ca3af"
            fontSize="11"
          >
            {state.electricPump.status}
          </text>
          <text
            x="160"
            y="237"
            textAnchor="middle"
            fill="#9ca3af"
            fontSize="10"
          >
            Eff: {state.electricPump.efficiency}%
          </text>
        </g>

        {/* Connection line from Electric Pump to Header */}
        {state.electricPump.mode === 'ON' && (
          <line
            x1="220"
            y1="200"
            x2="420"
            y2="280"
            stroke="#10b981"
            strokeWidth="3"
            strokeDasharray="5,5"
          >
            <animate
              attributeName="strokeDashoffset"
              values="0;10"
              dur="0.5s"
              repeatCount="indefinite"
            />
          </line>
        )}

        {/* Diesel Pump - Right */}
        <g>
          <rect
            x="780"
            y="150"
            width="120"
            height="100"
            fill="#1f2937"
            stroke={getPumpColor(state.dieselPump.mode, state.dieselPump.status)}
            strokeWidth="2"
            rx="5"
          />
          <text
            x="840"
            y="175"
            textAnchor="middle"
            fill="white"
            fontSize="14"
            fontWeight="bold"
          >
            Diesel Pump
          </text>
          <text
            x="840"
            y="200"
            textAnchor="middle"
            fill={getPumpColor(state.dieselPump.mode, state.dieselPump.status)}
            fontSize="16"
            fontWeight="bold"
          >
            {state.dieselPump.mode}
          </text>
          <text
            x="840"
            y="220"
            textAnchor="middle"
            fill="#9ca3af"
            fontSize="11"
          >
            {state.dieselPump.status}
          </text>
          <text
            x="840"
            y="237"
            textAnchor="middle"
            fill="#9ca3af"
            fontSize="10"
          >
            Eff: {state.dieselPump.efficiency}%
          </text>
        </g>

        {/* Connection line from Diesel Pump to Header */}
        {state.dieselPump.mode === 'ON' && (
          <line
            x1="780"
            y1="200"
            x2="580"
            y2="280"
            stroke="#10b981"
            strokeWidth="3"
            strokeDasharray="5,5"
          >
            <animate
              attributeName="strokeDashoffset"
              values="0;10"
              dur="0.5s"
              repeatCount="indefinite"
            />
          </line>
        )}

        {/* Jockey Pump - Bottom */}
        <g>
          <rect
            x="420"
            y="430"
            width="120"
            height="100"
            fill="#1f2937"
            stroke={getPumpColor(state.jockeyPump.mode, state.jockeyPump.status)}
            strokeWidth="2"
            rx="5"
          />
          <text
            x="480"
            y="455"
            textAnchor="middle"
            fill="white"
            fontSize="14"
            fontWeight="bold"
          >
            Jockey Pump
          </text>
          <text
            x="480"
            y="480"
            textAnchor="middle"
            fill={getPumpColor(state.jockeyPump.mode, state.jockeyPump.status)}
            fontSize="16"
            fontWeight="bold"
          >
            {state.jockeyPump.mode}
          </text>
          <text
            x="480"
            y="500"
            textAnchor="middle"
            fill="#9ca3af"
            fontSize="11"
          >
            {state.jockeyPump.status}
          </text>
          <text
            x="480"
            y="517"
            textAnchor="middle"
            fill="#9ca3af"
            fontSize="10"
          >
            Eff: {state.jockeyPump.efficiency}%
          </text>
        </g>

        {/* Connection line from Jockey Pump to Header */}
        {state.jockeyPump.mode === 'ON' && (
          <line
            x1="480"
            y1="430"
            x2="480"
            y2="380"
            stroke="#10b981"
            strokeWidth="3"
            strokeDasharray="5,5"
          >
            <animate
              attributeName="strokeDashoffset"
              values="0;10"
              dur="0.5s"
              repeatCount="indefinite"
            />
          </line>
        )}

        {/* Water Tank - Top Left */}
        <g>
          <rect
            x="50"
            y="30"
            width="100"
            height="80"
            fill="#1f2937"
            stroke={getWaterColor()}
            strokeWidth="2"
            rx="5"
          />
          <text
            x="100"
            y="55"
            textAnchor="middle"
            fill="white"
            fontSize="12"
            fontWeight="bold"
          >
            Water Tank
          </text>
          <text
            x="100"
            y="75"
            textAnchor="middle"
            fill={getWaterColor()}
            fontSize="14"
            fontWeight="bold"
          >
            {state.waterLevel.toFixed(0)} kL
          </text>
        </g>

        {/* Diesel Tank - Top Right */}
        <g>
          <rect
            x="850"
            y="30"
            width="100"
            height="80"
            fill="#1f2937"
            stroke={state.dieselLevel < 50 ? '#f97316' : '#10b981'}
            strokeWidth="2"
            rx="5"
          />
          <text
            x="900"
            y="55"
            textAnchor="middle"
            fill="white"
            fontSize="12"
            fontWeight="bold"
          >
            Diesel Tank
          </text>
          <text
            x="900"
            y="75"
            textAnchor="middle"
            fill={state.dieselLevel < 50 ? '#f97316' : '#10b981'}
            fontSize="14"
            fontWeight="bold"
          >
            {state.dieselLevel.toFixed(0)} L
          </text>
        </g>

        {/* Legend */}
        <g>
          <text
            x="50"
            y="580"
            fill="#9ca3af"
            fontSize="12"
          >
            Active Pumps: {[
              state.electricPump.mode === 'ON' && 'Electric',
              state.dieselPump.mode === 'ON' && 'Diesel',
              state.jockeyPump.mode === 'ON' && 'Jockey',
            ]
              .filter(Boolean)
              .join(', ') || 'None'}
          </text>
        </g>
      </svg>

      {/* Legend Below */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span className="text-dark-text">Normal</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-orange-500 rounded"></div>
          <span className="text-dark-text">Warning</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span className="text-dark-text">Critical</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-500 rounded"></div>
          <span className="text-dark-text">Off</span>
        </div>
      </div>
    </div>
  );
}
