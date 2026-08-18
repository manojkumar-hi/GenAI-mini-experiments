import React from 'react';

/**
 * Styled Card Wrapper utilizing Cyborg Dark Glassmorphism.
 */
export default function DashboardCard({ title, icon, children, className = "" }) {
  return (
    <div className={`dashboard-card d-flex flex-column ${className}`}>
      {(title || icon) && (
        <div className="d-flex align-items-center justify-content-between mb-4 border-bottom border-secondary pb-2">
          <h5 className="m-0 fw-semibold d-flex align-items-center gap-2">
            {icon && <span className="gradient-text-accent">{icon}</span>}
            {title}
          </h5>
        </div>
      )}
      <div className="flex-grow-1 d-flex flex-column justify-content-center">
        {children}
      </div>
    </div>
  );
}
