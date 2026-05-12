'use client';

import React, { useEffect, useRef, useState } from 'react';
import { LiveGaugeReader } from '@/components/LiveGaugeReader';
import { AlertCircle, Home } from 'lucide-react';

export default function LivePage() {
  const frameRef = useRef<HTMLImageElement>(null);
  const [connected, setConnected] = useState(true);
  const [frameMissing, setFrameMissing] = useState(false);

  useEffect(() => {
    const frameInterval = setInterval(() => {
      if (frameRef.current) {
        frameRef.current.src = `/frames/current_frame.jpg?t=${Date.now()}`;
      }
    }, 200);

    return () => clearInterval(frameInterval);
  }, []);

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await fetch(`/frames/current_frame.jpg?t=${Date.now()}`);
        if (response.ok) {
          setConnected(true);
          setFrameMissing(false);
        } else {
          setConnected(false);
          setFrameMissing(true);
        }
      } catch {
        setConnected(false);
        setFrameMissing(true);
      }
    };

    testConnection();
    const connInterval = setInterval(testConnection, 3000);
    return () => clearInterval(connInterval);
  }, []);

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      <div className="bg-dark-card border-b border-dark-border p-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Live Gauge Monitoring</h1>
          <p className="text-dark-text/60 mt-1">Real-time pressure detection from the Python gauge reader</p>
        </div>
        <a
          href="/"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition text-white text-sm font-medium"
        >
          <Home size={18} />
          Back
        </a>
      </div>

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
              <div className="relative bg-black aspect-video flex items-center justify-center">
                <img
                  ref={frameRef}
                  src="/frames/current_frame.jpg"
                  alt="Live gauge"
                  className="w-full h-full object-contain"
                  onLoad={() => {
                    setConnected(true);
                    setFrameMissing(false);
                  }}
                  onError={() => {
                    setConnected(false);
                    setFrameMissing(true);
                  }}
                />

                {frameMissing && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 px-6 text-center pointer-events-none">
                    <AlertCircle className="text-red-500 mb-3" size={40} />
                    <p className="text-red-400 text-sm mb-2">Waiting for the camera frame</p>
                    <code className="text-yellow-400 text-xs bg-black/50 px-3 py-2 rounded">
                      cd gauge_reader && python firedesk_integration.py
                    </code>
                  </div>
                )}

                <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 px-3 py-1 rounded">
                  <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                  <span className="text-xs text-white">{connected ? 'Live' : 'Offline'}</span>
                </div>
              </div>

              {connected && (
                <div className="p-3 bg-green-500/10 border-t border-green-500/30 text-xs text-green-600">
                  ✓ Python gauge reader active
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-1">
            <LiveGaugeReader pollInterval={500} filepath="/gauge_status.json" />
          </div>
        </div>

        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 text-sm text-dark-text/80">
          <p className="font-semibold text-blue-400 mb-2">How it works:</p>
          <ol className="space-y-1 ml-4 list-decimal">
            <li>Python script captures the camera feed</li>
            <li>It detects the gauge, draws the result, and saves the current frame</li>
            <li>The web app displays that live frame and reads updated PSI values</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
