import React from 'react';
import { Cpu } from 'lucide-react';

/**
 * Terminal Console visualising the AI Agent's cognitive loop (Perceive, Reason, Act).
 */
export default function AgentReasoning({ reasoning }) {
  if (!reasoning) {
    return (
      <div className="terminal-window h-100 d-flex align-items-center justify-content-center text-muted p-4">
        Waiting for agent cognitive state...
      </div>
    );
  }

  const { current_temp, goal, analysis, decision, action } = reasoning;

  return (
    <div className="terminal-window h-100 d-flex flex-column">
      {/* Terminal Header */}
      <div className="terminal-header justify-content-between">
        <div className="d-flex align-items-center gap-1.5">
          <span className="terminal-dot dot-red" />
          <span className="terminal-dot dot-yellow" />
          <span className="terminal-dot dot-green" />
          <span className="text-secondary ms-2 fw-medium" style={{ fontSize: '0.75rem' }}>
            agent_cognitive_engine.sh
          </span>
        </div>
        <Cpu className="text-info animate-pulse" size={16} />
      </div>
      
      {/* Terminal Content */}
      <div className="terminal-body flex-grow-1 font-monospace">
        <div className="mb-2 text-info">
          <span className="text-white">🤖 Agent Reasoning System</span>
          <span className="text-muted"> [v1.0.0-live]</span>
        </div>
        <div className="mb-2">
          <span className="text-secondary">&gt; </span>
          <span className="text-warning">Current Temperature : </span>
          <span className="text-white fw-bold">{current_temp}</span>
        </div>
        <div className="mb-2">
          <span className="text-secondary">&gt; </span>
          <span className="text-cyan">Goal : </span>
          <br />
          <span className="text-white ps-3">{goal}</span>
        </div>
        <div className="mb-2">
          <span className="text-secondary">&gt; </span>
          <span className="text-indigo">Analysis : </span>
          <br />
          <span className="text-white ps-3" style={{ color: '#e5e7eb' }}>{analysis}</span>
        </div>
        <div className="mb-2">
          <span className="text-secondary">&gt; </span>
          <span className="text-emerald">Decision : </span>
          <br />
          <span className="text-white ps-3">{decision}</span>
        </div>
        <div className="mb-0">
          <span className="text-secondary">&gt; </span>
          <span className="text-rose">Action : </span>
          <br />
          <span className="text-white ps-3">{action}</span>
        </div>
      </div>
    </div>
  );
}
