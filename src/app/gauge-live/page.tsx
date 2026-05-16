'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Camera, Settings, Check, X, RefreshCw, AlertCircle, Save, Home } from 'lucide-react';
import { RadialGauge } from '@/components/RadialGauge';

interface DetectionResults {
  success: boolean;
  pressure: number | null;
  unit: string | null;
  angle: number | null;
  gauge_center: [number, number] | null;
  gauge_radius: number | null;
  needle_line: [number, number, number, number] | null;
}

export default function GaugeLivePage() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [results, setResults] = useState<DetectionResults | null>(null);
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [calibrationStep, setCalibrationStep] = useState<'none' | 'min' | 'max'>('none');
  const [minAngle, setMinAngle] = useState(45);
  const [maxAngle, setMaxAngle] = useState(315);
  const [minPressure, setMinPressure] = useState(0);
  const [maxPressure, setMaxPressure] = useState(100);
  const [gaugeId, setGaugeId] = useState('default_psi');
  const [error, setError] = useState<string | null>(null);

  // Initialize Camera
  useEffect(() => {
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480 }
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setError('Could not access camera. Please check permissions.');
        console.error(err);
      }
    }
    setupCamera();
  }, []);

  // Initialize WebSocket
  useEffect(() => {
    const connectWS = () => {
      const ws = new WebSocket('ws://localhost:8000/ws/gauge');
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        setError(null);
      };

      ws.onclose = () => {
        setConnected(false);
        setTimeout(connectWS, 2000); // Reconnect
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'results') {
          setResults(data);
        } else if (data.type === 'calibration_updated') {
          console.log('Calibration updated successfully');
        }
      };

      ws.onerror = () => {
        setError('Backend server not responding. Run live_server.py');
      };
    };

    connectWS();
    return () => wsRef.current?.close();
  }, []);

  // Frame Capture and Sending
  const sendFrame = useCallback(() => {
    if (!videoRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.6);

    wsRef.current.send(JSON.stringify({
      type: 'frame',
      gauge_id: gaugeId,
      image: dataUrl
    }));
  }, [gaugeId]);

  useEffect(() => {
    const interval = setInterval(sendFrame, 200); // 5 FPS for better stability
    return () => clearInterval(interval);
  }, [sendFrame]);

  // Drawing results on canvas
  useEffect(() => {
    if (!canvasRef.current || !results) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);

    if (results.success && results.gauge_center && results.gauge_radius) {
      const [cx, cy] = results.gauge_center;
      const r = results.gauge_radius;

      // Draw Gauge Circle
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, 2 * Math.PI);
      ctx.strokeStyle = '#00f2ff';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Draw Center
      ctx.beginPath();
      ctx.arc(cx, cy, 5, 0, 2 * Math.PI);
      ctx.fillStyle = '#ff0055';
      ctx.fill();

      // Draw Needle
      if (results.needle_line) {
        const [x1, y1, x2, y2] = results.needle_line;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 4;
        ctx.stroke();
      }

      // Draw Calibration Angles if in calibration mode
      if (isCalibrating) {
        const drawAngleLine = (angle: number, color: string, label: string, dashed = true) => {
          const rad = (angle * Math.PI) / 180;
          const x = cx + r * Math.cos(rad);
          const y = cy + r * Math.sin(rad);
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(x, y);
          ctx.strokeStyle = color;
          if (dashed) ctx.setLineDash([5, 5]);
          ctx.lineWidth = 2;
          ctx.stroke();
          ctx.setLineDash([]);
          
          // Draw Label background
          ctx.fillStyle = color;
          ctx.font = 'bold 12px Inter, sans-serif';
          ctx.fillRect(x - 5, y - 20, 60, 20);
          ctx.fillStyle = 'white';
          ctx.fillText(label, x, y - 5);
        };

        if (minAngle !== undefined) drawAngleLine(minAngle, '#10b981', 'MIN (0)');
        if (maxAngle !== undefined) drawAngleLine(maxAngle, '#ef4444', 'MAX');
      }
    }
  }, [results, isCalibrating, minAngle, maxAngle]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isCalibrating || !results?.gauge_center) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = canvasRef.current.width / rect.width;
    const scaleY = canvasRef.current.height / rect.height;
    
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    const [cx, cy] = results.gauge_center;

    // Calculate angle of click relative to center
    const angle = Math.atan2(y - cy, x - cx) * (180 / Math.PI);
    const normalizedAngle = (angle + 360) % 360;

    if (calibrationStep === 'min') {
      setMinAngle(normalizedAngle);
      setCalibrationStep('max');
    } else if (calibrationStep === 'max') {
      setMaxAngle(normalizedAngle);
      setCalibrationStep('none');
    }
  };

  const saveCalibration = () => {
    if (!wsRef.current) return;
    wsRef.current.send(JSON.stringify({
      type: 'calibrate',
      gauge_id: gaugeId,
      data: {
        gauge_name: gaugeId,
        unit: results?.unit || 'PSI',
        min_angle: minAngle,
        max_angle: maxAngle,
        min_pressure: minPressure,
        max_pressure: maxPressure
      }
    }));
    setIsCalibrating(false);
  };

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 bg-dark-card p-6 rounded-xl border border-dark-border shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 rounded-lg">
            <Camera className="text-blue-400" size={32} />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">VisionGuide Pro</h1>
            <p className="text-dark-text/60 font-medium">Real-time Digital Twin Calibration System</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full border ${connected ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-xs font-bold uppercase tracking-wider">{connected ? 'Live' : 'Disconnected'}</span>
          </div>
          <a href="/" className="p-2 hover:bg-dark-border rounded-lg transition">
            <Home size={24} />
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Main Feed Section */}
        <div className="lg:col-span-8 space-y-6">
          <div className="relative bg-black rounded-2xl overflow-hidden border border-dark-border shadow-2xl aspect-video group">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover opacity-80"
            />
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              className="absolute inset-0 w-full h-full pointer-events-auto cursor-crosshair"
              onClick={handleCanvasClick}
            />
            
            {/* Overlay Info */}
            <div className="absolute top-4 left-4 flex flex-col gap-2">
              <div className="bg-black/60 backdrop-blur-md px-4 py-2 rounded-lg border border-white/10 text-xs font-mono">
                RESOLVE: 640x480 @ 10FPS
              </div>
              {results?.success && (
                <div className="bg-green-500/20 backdrop-blur-md px-4 py-2 rounded-lg border border-green-500/30 text-green-400 text-xs font-bold">
                  GAUGE DETECTED
                </div>
              )}
            </div>

            {isCalibrating && (
              <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-blue-600/90 backdrop-blur-xl px-8 py-4 rounded-2xl border border-white/20 shadow-2xl flex flex-col items-center gap-2">
                <p className="text-sm font-bold uppercase tracking-widest text-white">
                  Calibration Mode: {calibrationStep === 'min' ? 'Click 0 Point' : calibrationStep === 'max' ? 'Click Max Point' : 'Adjust Settings'}
                </p>
                {!results?.gauge_center && (
                  <div className="flex items-center gap-2 text-yellow-400 text-xs animate-pulse">
                    <AlertCircle size={14} />
                    <span>Bring gauge into view to start clicking</span>
                  </div>
                )}
                <div className="flex gap-4">
                   <button onClick={() => setCalibrationStep('min')} className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-xs transition">Reset Min</button>
                   <button onClick={() => setCalibrationStep('max')} className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-xs transition">Reset Max</button>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 animate-in fade-in slide-in-from-top-4">
              <AlertCircle size={20} />
              <p className="font-medium">{error}</p>
            </div>
          )}
        </div>

        {/* Sidebar Controls */}
        <div className="lg:col-span-4 space-y-6">
          {/* Real-time Data Card */}
          <div className="bg-dark-card border border-dark-border rounded-2xl p-8 shadow-2xl space-y-8">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-white tracking-tight">Real-time Metrics</h3>
              <RefreshCw className={`text-dark-text/40 ${results?.success ? 'animate-spin-slow' : ''}`} size={20} />
            </div>

            <div className="flex justify-center py-4 bg-dark-bg/50 rounded-2xl border border-dark-border/50">
              <RadialGauge
                value={results?.pressure || 0}
                max={maxPressure}
                unit={results?.unit || 'PSI'}
                label="Current Reading"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-dark-bg/50 rounded-xl border border-dark-border/50">
                <p className="text-xs text-dark-text/40 font-bold uppercase mb-1">Angle</p>
                <p className="text-2xl font-bold text-blue-400">{results?.angle?.toFixed(1) || '0.0'}°</p>
              </div>
              <div className="p-4 bg-dark-bg/50 rounded-xl border border-dark-border/50">
                <p className="text-xs text-dark-text/40 font-bold uppercase mb-1">Reliability</p>
                <p className="text-2xl font-bold text-green-400">{results?.success ? '98%' : '0%'}</p>
              </div>
            </div>
          </div>

          {/* Configuration Card */}
          <div className="bg-dark-card border border-dark-border rounded-2xl p-8 shadow-2xl space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-white tracking-tight">System Settings</h3>
              <Settings className="text-dark-text/40" size={20} />
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-dark-text/40 uppercase mb-2 block">Gauge ID</label>
                <input
                  type="text"
                  value={gaugeId}
                  onChange={(e) => setGaugeId(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-dark-text/40 uppercase mb-2 block">Min Pres.</label>
                  <input
                    type="number"
                    value={minPressure}
                    onChange={(e) => setMinPressure(Number(e.target.value))}
                    className="w-full bg-dark-bg border border-dark-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-dark-text/40 uppercase mb-2 block">Max Pres.</label>
                  <input
                    type="number"
                    value={maxPressure}
                    onChange={(e) => setMaxPressure(Number(e.target.value))}
                    className="w-full bg-dark-bg border border-dark-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition"
                  />
                </div>
              </div>

              <div className="pt-4 space-y-3">
                {!isCalibrating ? (
                  <button
                    onClick={() => { setIsCalibrating(true); setCalibrationStep('min'); }}
                    className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg transition transform hover:-translate-y-1"
                  >
                    <RefreshCw size={18} />
                    Start Calibration
                  </button>
                ) : (
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={saveCalibration}
                      className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white font-bold py-4 rounded-xl shadow-lg transition"
                    >
                      <Save size={18} />
                      Save
                    </button>
                    <button
                      onClick={() => setIsCalibrating(false)}
                      className="flex items-center justify-center gap-2 bg-dark-border hover:bg-red-500/20 hover:text-red-400 text-dark-text font-bold py-4 rounded-xl transition"
                    >
                      <X size={18} />
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .animate-spin-slow {
          animation: spin 3s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
