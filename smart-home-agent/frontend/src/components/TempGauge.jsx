import React from 'react';
import { Fan, Snowflake, Flame } from 'lucide-react';

/**
 * Animated SVG Radial Gauge displaying the current simulated temperature,
 * AC status, and dynamically adjusting theme colors to match the user's comfort limits.
 */
export default function TempGauge({ temperature, acStatus, targetMin = 22.0, targetMax = 26.0 }) {
  const tempVal = parseFloat(temperature) || 0.0;
  
  // Calculate percentage mapping (Min: 10°C, Max: 40°C)
  const minTemp = 10.0;
  const maxTemp = 40.0;
  const percentage = Math.min(Math.max((tempVal - minTemp) / (maxTemp - minTemp), 0.0), 1.0);
  
  // SVG Ring properties
  const radius = 75;
  const circumference = 2 * Math.PI * radius; // Approx 471.24
  const strokeDashoffset = circumference * (1 - percentage);
  
  // Determine color theme based on dynamic comfort limits
  let color = 'var(--color-cyan)';
  let label = 'COLD';
  let StatusIcon = Snowflake;
  
  if (tempVal >= targetMin && tempVal <= targetMax) {
    color = 'var(--color-emerald)';
    label = 'COMFORTABLE';
  } else if (tempVal > targetMax) {
    color = 'var(--color-rose)';
    label = 'HOT';
    StatusIcon = Flame;
  }
  
  return (
    <div className="d-flex flex-column align-items-center justify-content-center p-2 text-center position-relative">
      <div style={{ position: 'relative', width: '180px', height: '180px' }}>
        {/* Radial SVG Gauge */}
        <svg className="gauge-svg" width="180" height="180" viewBox="0 0 180 180">
          <circle
            className="gauge-track"
            cx="90"
            cy="90"
            r={radius}
            strokeWidth="12"
          />
          <circle
            className="gauge-fill"
            cx="90"
            cy="90"
            r={radius}
            strokeWidth="12"
            stroke={color}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ filter: `drop-shadow(0px 0px 6px ${color})` }}
          />
        </svg>
        
        {/* Center Readout */}
        <div 
          className="position-absolute top-50 start-50 translate-middle d-flex flex-column align-items-center justify-content-center"
          style={{ width: '120px', height: '120px' }}
        >
          {acStatus === "ON" ? (
            <Fan 
              className="fan-spin-fast text-info mb-1" 
              size={26} 
              style={{ filter: 'drop-shadow(0 0 8px #00f0ff)' }}
            />
          ) : (
            <Fan className="text-secondary mb-1" size={26} />
          )}
          <h2 className="m-0 fw-bold font-monospace" style={{ fontSize: '2rem' }}>
            {tempVal.toFixed(1)}°C
          </h2>
          <span 
            className="fw-bold px-2 py-0.5 mt-1 rounded-pill" 
            style={{ 
              fontSize: '0.65rem', 
              color: color, 
              background: `rgba(${color === 'var(--color-emerald)' ? '16, 185, 129' : color === 'var(--color-rose)' ? '244, 63, 94' : '0, 240, 255'}, 0.1)`,
              border: `1px solid ${color}` 
            }}
          >
            {label}
          </span>
        </div>
      </div>
      
      {/* Lower label */}
      <div className="mt-3">
        <div className="d-flex align-items-center gap-2">
          <span className={`status-indicator ${acStatus === "ON" ? "status-active-on" : "status-active-off"}`} />
          <span className="text-muted fw-medium" style={{ fontSize: '0.9rem' }}>
            Air Conditioner: <strong className={acStatus === "ON" ? "text-info" : "text-secondary"}>{acStatus}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
