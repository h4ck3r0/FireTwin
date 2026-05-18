'use client';

import React from 'react';

interface RadialGaugeProps {
  value: number;
  max: number;
  unit: string;
  label: string;
  lowThreshold?: number;
  criticalThreshold?: number;
}

export function RadialGauge({
  value,
  max,
  unit,
  label,
  lowThreshold,
  criticalThreshold,
}: RadialGaugeProps) {
  const percentage = (value / max) * 100;
  const rotation = (percentage / 100) * 270 - 135; 

  let gaugeColor = '#10b981'; 
  if (criticalThreshold !== undefined && value < criticalThreshold) {
    gaugeColor = '#ef4444'; 
  } else if (lowThreshold !== undefined && value < lowThreshold) {
    gaugeColor = '#f59e0b'; 
  }

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-40 h-40">
        {/* Background circle */}
        <svg
          className="absolute inset-0"
          viewBox="0 0 120 120"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Background arc */}
          <circle
            cx="60"
            cy="60"
            r="45"
            fill="none"
            stroke="#3a4556"
            strokeWidth="8"
            pathLength="100"
            style={{
              strokeDasharray: '100 400',
              strokeDashoffset: '-100',
            }}
          />

          {/* Progress arc */}
          <circle
            cx="60"
            cy="60"
            r="45"
            fill="none"
            stroke={gaugeColor}
            strokeWidth="8"
            pathLength="100"
            style={{
              strokeDasharray: `${percentage} 400`,
              strokeDashoffset: '-100',
              transition: 'stroke-dasharray 0.5s ease-in-out, stroke 0.3s ease',
            }}
            strokeLinecap="round"
          />

          {/* Tick marks */}
          {Array.from({ length: 10 }).map((_, i) => {
            const angle = (i / 10) * 270 - 135;
            const rad = (angle * Math.PI) / 180;
            const x1 = 60 + 40 * Math.cos(rad);
            const y1 = 60 + 40 * Math.sin(rad);
            const x2 = 60 + 48 * Math.cos(rad);
            const y2 = 60 + 48 * Math.sin(rad);
            return (
              <line
                key={i}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="#3a4556"
                strokeWidth="1"
              />
            );
          })}
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className="text-4xl font-bold text-dark-text">{value.toFixed(1)}</p>
          <p className="text-sm text-dark-text/70">{unit}</p>
        </div>
      </div>

      <div className="text-center">
        <p className="text-sm font-medium text-dark-text">{label}</p>
        {lowThreshold !== undefined && (
          <p className="text-xs text-dark-text/50">
            Low Threshold: {lowThreshold} {unit}
          </p>
        )}
      </div>
    </div>
  );
}
