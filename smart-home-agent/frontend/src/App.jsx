import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Square, 
  RotateCcw, 
  Plus, 
  Minus, 
  Settings, 
  Activity, 
  Volume2, 
  VolumeX,
  Server,
  Terminal as TermIcon
} from 'lucide-react';
import DashboardCard from './components/DashboardCard';
import TempGauge from './components/TempGauge';
import TempChart from './components/TempChart';
import AgentReasoning from './components/AgentReasoning';
import ActivityLog from './components/ActivityLog';
import './App.css';

// Base API URL pointing to the FastAPI backend
const API_BASE = "http://localhost:8000/api";

export default function App() {
  // Application state variables
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [sliderVal, setSliderVal] = useState(25.0);
  const [targetMin, setTargetMin] = useState(22.0);
  const [targetMax, setTargetMax] = useState(26.0);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [backendError, setBackendError] = useState(null);
  
  // Track previous AC status for triggering TTS announcements
  const prevAcStatusRef = useRef(null);
  
  // Fetch status, history, and logs from backend API
  const fetchData = async () => {
    try {
      // 1. Fetch current status
      const resStatus = await fetch(`${API_BASE}/status`);
      if (!resStatus.ok) throw new Error("Failed to reach backend status API");
      const dataStatus = await resStatus.json();
      setStatus(dataStatus);
      setSliderVal(dataStatus.temperature);
      setTargetMin(dataStatus.target_min);
      setTargetMax(dataStatus.target_max);
      setBackendError(null);
      
      // Voice Alerts Logic - Trigger only on state transitions
      if (prevAcStatusRef.current !== null && prevAcStatusRef.current !== dataStatus.ac_status) {
        handleVoiceAnnouncement(dataStatus.ac_status, dataStatus.temperature);
      }
      prevAcStatusRef.current = dataStatus.ac_status;

      // 2. Fetch temperature history
      const resHistory = await fetch(`${API_BASE}/history`);
      if (resHistory.ok) {
        const dataHistory = await resHistory.json();
        setHistory(dataHistory);
      }

      // 3. Fetch activity logs
      const resLogs = await fetch(`${API_BASE}/logs`);
      if (resLogs.ok) {
        const dataLogs = await resLogs.json();
        setLogs(dataLogs);
      }
    } catch (err) {
      console.error(err);
      setBackendError("Cannot connect to Python FastAPI backend at http://localhost:8000. Ensure server is running.");
    }
  };

  // Poll backend every 1.5 seconds for fresh simulator states
  useEffect(() => {
    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 1500);
    return () => clearInterval(interval);
  }, [voiceEnabled]);

  // Voice Alert Triggers (Text-to-Speech)
  const handleVoiceAnnouncement = (newAcStatus, currentTemp) => {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    
    // Stop any existing spoken alerts to avoid queuing lag
    window.speechSynthesis.cancel();
    
    let phrase = "";
    if (newAcStatus === "ON") {
      phrase = `Warning. Room temperature is too high. Turning on the air conditioner.`;
    } else if (newAcStatus === "OFF") {
      phrase = `Room temperature is comfortable. Turning off the air conditioner.`;
    } else {
      phrase = `Temperature is within the comfort range. Monitoring continues.`;
    }
    
    const utterance = new SpeechSynthesisUtterance(phrase);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  // Trigger manual speech synthesis test
  const triggerManualVoiceTest = () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance("Voice engine connected and ready.");
    window.speechSynthesis.speak(utterance);
  };

  // API Call: Start simulation
  const startSimulation = async () => {
    try {
      await fetch(`${API_BASE}/simulation/start`, { method: 'POST' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // API Call: Stop simulation
  const stopSimulation = async () => {
    try {
      await fetch(`${API_BASE}/simulation/stop`, { method: 'POST' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // API Call: Reset simulation
  const resetSimulation = async () => {
    try {
      prevAcStatusRef.current = null;
      await fetch(`${API_BASE}/simulation/reset`, { method: 'POST' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // API Call: Set temperature
  const updateTemperature = async (targetVal) => {
    const val = parseFloat(targetVal);
    setSliderVal(val);
    try {
      await fetch(`${API_BASE}/temperature/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ temperature: val })
      });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  // API Call: Update target range
  const updateTargetRange = async (minVal, maxVal) => {
    try {
      const res = await fetch(`${API_BASE}/target-range`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_min: parseFloat(minVal), target_max: parseFloat(maxVal) })
      });
      if (res.ok) {
        fetchData();
      } else {
        const errorData = await res.json();
        alert(errorData.detail || "Failed to update target range");
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Helper adjustment incrementers
  const adjustTemp = (delta) => {
    if (!status) return;
    const current = status.temperature;
    const nextVal = Math.min(Math.max(current + delta, 10.0), 45.0);
    updateTemperature(nextVal);
  };

  return (
    <div className="container py-4">
      {/* Top Header */}
      <header className="d-flex flex-column flex-md-row align-items-md-center justify-content-between mb-4 border-bottom border-secondary pb-3">
        <div>
          <h1 className="gradient-text m-0 fw-bold">Smart Home Temperature Control Agent</h1>
          <p className="text-secondary m-0 fw-medium">
            B.Tech Agentic AI Laboratory Experiment — Hysteresis Control Model
          </p>
        </div>
        <div className="d-flex align-items-center gap-3 mt-3 mt-md-0">
          {/* Server Connection Status */}
          <div className="d-flex align-items-center gap-2 border border-secondary px-3 py-1.5 rounded-pill bg-dark">
            <Server size={14} className={backendError ? "text-danger animate-pulse" : "text-success"} />
            <span className="font-monospace text-muted" style={{ fontSize: '0.8rem' }}>
              HOST: <strong className={backendError ? "text-danger" : "text-success"}>{backendError ? "OFFLINE" : "CONNECTED"}</strong>
            </span>
          </div>
          {/* Audio toggle button */}
          <button 
            onClick={() => {
              setVoiceEnabled(!voiceEnabled);
              if(!voiceEnabled) triggerManualVoiceTest();
            }}
            className={`btn rounded-circle p-2 ${voiceEnabled ? 'btn-glow-cyan' : 'btn-outline-secondary'}`}
            title={voiceEnabled ? "Mute Voice Alerts" : "Unmute Voice Alerts"}
          >
            {voiceEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
          </button>
        </div>
      </header>

      {/* Backend connection warning alert */}
      {backendError && (
        <div className="alert alert-danger border-danger bg-danger bg-opacity-10 text-danger rounded-4 py-3 mb-4 shadow" role="alert">
          <div className="d-flex gap-2">
            <Activity className="flex-shrink-0" size={20} />
            <div>
              <h6 className="alert-heading fw-bold mb-1">Backend Server Disconnected</h6>
              <p className="m-0" style={{ fontSize: '0.9rem' }}>{backendError}</p>
              <code className="d-block mt-2 text-white-50">Run 'uvicorn backend.main:app --reload' in the project root folder.</code>
            </div>
          </div>
        </div>
      )}

      {/* Main Dashboard Layout */}
      <div className="row g-4">
        {/* Card 1: Virtual Temperature Gauge */}
        <div className="col-lg-4 col-md-6">
          <DashboardCard title="Virtual Temp Sensor" icon={<Settings size={18} />}>
            <TempGauge 
              temperature={status ? status.temperature : 25.0}
              acStatus={status ? status.ac_status : "OFF"}
              targetMin={targetMin}
              targetMax={targetMax}
            />
          </DashboardCard>
        </div>

        {/* Card 2: AI Reasoning Panel */}
        <div className="col-lg-4 col-md-6">
          <DashboardCard title="Cognitive Reasoning" icon={<TermIcon size={18} />}>
            <AgentReasoning reasoning={status ? status.agent_reasoning : null} />
          </DashboardCard>
        </div>

        {/* Card 3: Activity Log */}
        <div className="col-lg-4 col-md-12">
          <DashboardCard title="Agent Activity Log" icon={<Activity size={18} />}>
            <ActivityLog logs={logs} />
          </DashboardCard>
        </div>

        {/* Card 4: Simulation Controls, Comfort Config, and Override */}
        <div className="col-lg-4 col-md-12">
          <DashboardCard title="Environment Adjustments" icon={<Settings size={18} />}>
            {/* Simulation engines */}
            <div className="mb-4">
              <label className="text-secondary fw-semibold mb-2" style={{ fontSize: '0.85rem' }}>
                SIMULATION ENGINES
              </label>
              <div className="d-flex flex-wrap gap-2">
                {status && status.simulation_active ? (
                  <button onClick={stopSimulation} className="btn btn-glow-rose d-flex align-items-center gap-2 flex-grow-1 py-2 justify-content-center">
                    <Square size={14} fill="currentColor" /> Stop Drift
                  </button>
                ) : (
                  <button onClick={startSimulation} className="btn btn-glow-emerald d-flex align-items-center gap-2 flex-grow-1 py-2 justify-content-center">
                    <Play size={14} fill="currentColor" /> Start Drift
                  </button>
                )}
                <button onClick={resetSimulation} className="btn btn-outline-secondary d-flex align-items-center gap-2 py-2 justify-content-center">
                  <RotateCcw size={14} /> Reset
                </button>
              </div>
            </div>

            <hr className="border-secondary my-3" />

            {/* Comfort target configurations */}
            <div className="mb-4">
              <label className="text-secondary fw-semibold mb-2" style={{ fontSize: '0.85rem' }}>
                AGENT COMFORT RANGE GOALS
              </label>
              <div className="row g-2 mb-2">
                <div className="col-6">
                  <div className="p-2 border border-secondary rounded bg-dark bg-opacity-20 text-center">
                    <span className="text-muted d-block" style={{ fontSize: '0.7rem' }}>MIN LIMIT</span>
                    <div className="d-flex align-items-center justify-content-center gap-1 mt-1">
                      <button 
                        className="btn btn-sm btn-outline-secondary p-1"
                        onClick={() => updateTargetRange(targetMin - 0.5, targetMax)}
                        disabled={targetMin <= 15.0}
                      >
                        <Minus size={10} />
                      </button>
                      <span className="font-monospace fw-bold text-info" style={{ fontSize: '0.9rem' }}>{targetMin}°C</span>
                      <button 
                        className="btn btn-sm btn-outline-secondary p-1"
                        onClick={() => updateTargetRange(targetMin + 0.5, targetMax)}
                        disabled={targetMin >= targetMax - 1.0}
                      >
                        <Plus size={10} />
                      </button>
                    </div>
                  </div>
                </div>
                <div className="col-6">
                  <div className="p-2 border border-secondary rounded bg-dark bg-opacity-20 text-center">
                    <span className="text-muted d-block" style={{ fontSize: '0.7rem' }}>MAX LIMIT</span>
                    <div className="d-flex align-items-center justify-content-center gap-1 mt-1">
                      <button 
                        className="btn btn-sm btn-outline-secondary p-1"
                        onClick={() => updateTargetRange(targetMin, targetMax - 0.5)}
                        disabled={targetMax <= targetMin + 1.0}
                      >
                        <Minus size={10} />
                      </button>
                      <span className="font-monospace fw-bold text-rose" style={{ fontSize: '0.9rem' }}>{targetMax}°C</span>
                      <button 
                        className="btn btn-sm btn-outline-secondary p-1"
                        onClick={() => updateTargetRange(targetMin, targetMax + 0.5)}
                        disabled={targetMax >= 35.0}
                      >
                        <Plus size={10} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <small className="text-muted d-block" style={{ fontSize: '0.78rem', lineHeight: '1.4' }}>
                Hysteresis: AC turns **ON** above Max Limit ({targetMax}°C) and cools continuously until reaching the midpoint Setpoint (**{((targetMin + targetMax)/2).toFixed(1)}°C**), where it shuts **OFF**.
              </small>
            </div>

            <hr className="border-secondary my-3" />

            {/* Override slider */}
            <div>
              <label className="text-secondary fw-semibold mb-2" style={{ fontSize: '0.85rem' }}>
                MANUAL TEMPERATURE OVERRIDE
              </label>
              <div className="d-flex align-items-center gap-3 mb-3">
                <button 
                  onClick={() => adjustTemp(-1.0)} 
                  className="btn btn-outline-secondary p-2" 
                  disabled={!status}
                >
                  <Minus size={16} />
                </button>
                <input 
                  type="range"
                  min="10"
                  max="45"
                  step="0.5"
                  value={sliderVal}
                  onChange={(e) => setSliderVal(parseFloat(e.target.value))}
                  onMouseUp={(e) => updateTemperature(e.target.value)}
                  onTouchEnd={(e) => updateTemperature(e.target.value)}
                  className="custom-slider flex-grow-1"
                  disabled={!status}
                />
                <button 
                  onClick={() => adjustTemp(1.0)} 
                  className="btn btn-outline-secondary p-2" 
                  disabled={!status}
                >
                  <Plus size={16} />
                </button>
              </div>
              <div className="d-flex justify-content-between text-muted" style={{ fontSize: '0.8rem' }}>
                <span>10.0°C</span>
                <span className="text-info fw-bold font-monospace">{sliderVal}°C</span>
                <span>45.0°C</span>
              </div>
            </div>
          </DashboardCard>
        </div>

        {/* Card 5: Real-time Chart */}
        <div className="col-lg-8 col-md-12">
          <DashboardCard title="Live Temperature History" icon={<Activity size={18} />}>
            <TempChart 
              historyData={history} 
              targetMin={targetMin}
              targetMax={targetMax}
            />
          </DashboardCard>
        </div>
      </div>

      {/* Lab Experiment Details Footer */}
      <footer className="mt-5 text-center text-muted" style={{ fontSize: '0.85rem' }}>
        <p className="mb-1">
          Designed for B.Tech Agentic AI Laboratory Experiments. Demonstrates core agent properties:
        </p>
        <div className="d-flex justify-content-center gap-3 flex-wrap">
          <span className="badge bg-secondary">Perception (Sensor)</span>
          <span className="badge bg-secondary">Reasoning (Hysteresis model)</span>
          <span className="badge bg-secondary">Action (AC toggle)</span>
          <span className="badge bg-secondary">Environment (Simulation)</span>
        </div>
      </footer>
    </div>
  );
}
