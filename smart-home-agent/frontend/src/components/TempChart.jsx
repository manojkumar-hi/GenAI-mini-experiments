import React from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ReferenceArea 
} from 'recharts';

/**
 * Real-time Line Graph showing Temperature vs Time,
 * complete with dynamic comfort zone shading.
 */
export default function TempChart({ historyData, targetMin = 22.0, targetMax = 26.0 }) {
  // Format history for charting, ensuring correct values
  const formattedData = historyData.map(item => ({
    time: item.timestamp,
    temp: parseFloat(item.temperature) || 0.0,
    ac: item.ac_status
  }));

  // Custom tool-tip component matching the dark dashboard aesthetics
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="text-secondary mb-1">Time: <span className="text-white fw-bold">{data.time}</span></p>
          <p className="text-info mb-1 font-monospace">Temp: <span className="text-white fw-bold">{data.temp.toFixed(2)}°C</span></p>
          <p className="text-muted m-0">AC Status: <span className={data.ac === "ON" ? "text-cyan fw-bold" : "text-secondary fw-bold"}>{data.ac}</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height: '260px' }}>
      {formattedData.length === 0 ? (
        <div className="d-flex align-items-center justify-content-center h-100 text-muted">
          No temperature records available. Start simulation to collect data.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={formattedData}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            {/* Shaded Dynamic Comfort Range */}
            <ReferenceArea 
              y1={targetMin} 
              y2={targetMax} 
              fill="rgba(16, 185, 129, 0.08)" 
              stroke="rgba(16, 185, 129, 0.2)"
              strokeDasharray="3 3"
              label={{ 
                value: `Comfort Zone (${targetMin}°C - ${targetMax}°C)`, 
                fill: 'rgba(16, 185, 129, 0.6)', 
                position: 'insideLeft', 
                fontSize: 10,
                fontWeight: 600,
                offset: 10
              }} 
            />

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
            
            <XAxis 
              dataKey="time" 
              stroke="#9ca3af" 
              fontSize={10} 
              tickLine={false} 
              axisLine={false}
              dy={10}
            />
            
            <YAxis 
              domain={[10, 40]} 
              stroke="#9ca3af" 
              fontSize={10} 
              tickLine={false} 
              axisLine={false}
              dx={-5}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <Line 
              type="monotone" 
              dataKey="temp" 
              stroke="var(--color-cyan)" 
              strokeWidth={3}
              dot={{ r: 2, stroke: 'var(--color-indigo)', strokeWidth: 1, fill: 'var(--color-cyan)' }}
              activeDot={{ r: 6, stroke: '#ffffff', strokeWidth: 2, fill: 'var(--color-cyan)' }}
              style={{ filter: 'drop-shadow(0px 0px 4px rgba(0, 240, 255, 0.6))' }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
