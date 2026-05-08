/**
 * SkeletonLoader.jsx — Loading state UI with animated placeholders.
 *
 * Displays a skeleton layout that mirrors the final results view
 * structure, providing visual feedback while the AI generates the
 * itinerary.  Uses CSS pulse animations for a polished loading feel.
 *
 * Accessibility:
 *   - role="status" announces loading state to screen readers.
 *   - aria-label provides a text description of what's loading.
 *   - aria-live="polite" ensures screen readers announce status changes.
 *
 * @component
 * @returns {JSX.Element} Animated skeleton loading placeholder.
 */

import './SkeletonLoader.css';

export default function SkeletonLoader() {
  return (
    <div
      className="skeleton-container"
      role="status"
      aria-label="Loading itinerary"
      aria-live="polite"
    >
      {/* Skeleton Header — mimics the itinerary summary card */}
      <div className="skeleton-header">
        <div className="skeleton-pulse skeleton-title"></div>
        <div className="skeleton-pulse skeleton-subtitle"></div>
      </div>

      <div className="skeleton-layout">
        {/* Skeleton Sidebar — mimics Budget Tracker and Adapt Panel */}
        <div className="skeleton-sidebar" aria-hidden="true">
          <div className="skeleton-pulse skeleton-card" style={{ height: '200px' }}></div>
          <div className="skeleton-pulse skeleton-card" style={{ height: '150px' }}></div>
        </div>

        {/* Skeleton Main Content — mimics Map and Timeline */}
        <div className="skeleton-main" aria-hidden="true">
          {/* Map placeholder */}
          <div className="skeleton-pulse skeleton-map"></div>

          {/* Timeline placeholder — shows 3 skeleton day cards */}
          <div className="skeleton-timeline">
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton-day">
                <div className="skeleton-pulse skeleton-day-title"></div>
                <div className="skeleton-pulse skeleton-activity"></div>
                <div className="skeleton-pulse skeleton-activity"></div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Loading Overlay — centered spinner with status text */}
      <div className="skeleton-overlay">
        <div className="loading-spinner-lg" aria-hidden="true" />
        <div className="skeleton-status-text">
          <h3>Crafting your perfect trip…</h3>
          <p>Searching places, checking routes, and optimizing your schedule.</p>
        </div>
      </div>
    </div>
  );
}
