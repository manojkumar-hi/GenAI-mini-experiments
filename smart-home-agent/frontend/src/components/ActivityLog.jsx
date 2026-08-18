import React from 'react';
import { Terminal } from 'lucide-react';

/**
 * Scrollable list of simulator and agent action logs with timestamps.
 */
export default function ActivityLog({ logs }) {
  // Sort logs to show latest at the top
  const sortedLogs = [...logs].reverse();

  return (
    <div className="d-flex flex-column h-100">
      <div className="log-container flex-grow-1 p-2">
        {sortedLogs.length === 0 ? (
          <div className="d-flex align-items-center justify-content-center h-100 text-muted">
            No activity logged yet.
          </div>
        ) : (
          sortedLogs.map((log, idx) => (
            <div key={idx} className="log-item mb-3">
              <div className="d-flex align-items-center gap-2 mb-1">
                <span className="badge bg-secondary font-monospace" style={{ fontSize: '0.75rem', letterSpacing: '0.5px' }}>
                  {log.timestamp}
                </span>
                <span className="text-secondary" style={{ fontSize: '0.75rem' }}>
                  SYSTEM_LOG
                </span>
              </div>
              <div className="text-white-50" style={{ fontSize: '0.85rem', whiteSpace: 'pre-wrap' }}>
                {log.message}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
