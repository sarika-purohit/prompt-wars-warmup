import './SkeletonLoader.css';

export default function SkeletonLoader() {
  return (
    <div className="skeleton-container" role="status" aria-label="Loading itinerary">
      {/* Skeleton Header */}
      <div className="skeleton-header">
        <div className="skeleton-pulse skeleton-title"></div>
        <div className="skeleton-pulse skeleton-subtitle"></div>
      </div>

      <div className="skeleton-layout">
        {/* Skeleton Sidebar (Budget/Adapt) */}
        <div className="skeleton-sidebar">
          <div className="skeleton-pulse skeleton-card" style={{ height: '200px' }}></div>
          <div className="skeleton-pulse skeleton-card" style={{ height: '150px' }}></div>
        </div>

        {/* Skeleton Main Content (Map & Itinerary) */}
        <div className="skeleton-main">
          <div className="skeleton-pulse skeleton-map"></div>
          
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
      
      {/* Loading Overlay with Status Text */}
      <div className="skeleton-overlay">
        <div className="loading-spinner-lg" />
        <div className="skeleton-status-text">
           <h3>Crafting your perfect trip…</h3>
           <p>Searching places, checking routes, and optimizing your schedule.</p>
        </div>
      </div>
    </div>
  );
}
