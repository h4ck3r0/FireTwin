'use client';

import React, { useEffect, useRef, useState } from 'react';
import { LiveGaugeReader } from '@/components/LiveGaugeReader';
import { AlertCircle, Home } from 'lucide-react';

export default function LivePage() {
  const [cameraUrl, setCameraUrl] = useState('');
  const [connected, setConnected] = useState(true);
  const [frameMissing, setFrameMissing] = useState(false);

  useEffect(() => {
    fetch('/shared_config.json')
      .then(res => res.json())
      .then(config => {
        if (config.camera_url) setCameraUrl(config.camera_url);
      })
      .catch(err => console.error('Failed to load camera config:', err));
  }, []);

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      <div className="bg-dark-card border-b border-dark-border p-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Live Stream Monitoring</h1>
          <p className="text-dark-text/60 mt-1">Direct stream from the pump room camera</p>
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
                  src={cameraUrl || "http://192.168.1.191:8080/video"}
                  alt="Live camera stream"
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

                {!cameraUrl && frameMissing && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 px-6 text-center pointer-events-none">
                    <AlertCircle className="text-red-500 mb-3" size={40} />
                    <p className="text-red-400 text-sm mb-2">Camera stream unavailable</p>
                    <code className="text-yellow-400 text-xs bg-black/50 px-3 py-2 rounded">
                      Check shared_config.json and camera connection
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
                  ✓ Streaming directly from camera source
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-1">
            <LiveGaugeReader pollInterval={500} filepath="/gauge_status.json" />
          </div>
        </div>

        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 text-sm text-dark-text/80">
          <p className="font-semibold text-blue-400 mb-2">Streaming Mode:</p>
          <ul className="space-y-1 ml-4 list-disc">
            <li>Direct connection to camera URL (no local processing)</li>
            <li>Zero disk usage (no images saved)</li>
            <li>Minimal latency direct from source</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
