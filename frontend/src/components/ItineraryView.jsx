/**
 * ItineraryView — Day-by-day timeline of the trip.
 */

import { useState } from 'react';
import './ItineraryView.css';

const ICONS = {
  culture: '🏛️', food: '🍜', adventure: '🧗', nature: '🌿',
  shopping: '🛍️', relaxation: '🧘', nightlife: '🌙', history: '📜', other: '📍',
};

export default function ItineraryView({ itinerary, onSelectPlace }) {
  const [expandedDay, setExpandedDay] = useState(0);
  if (!itinerary?.days?.length) return null;

  return (
    <div className="itinerary-view" role="region" aria-label="Trip itinerary">
      <div className="itinerary-summary card animate-fade-in">
        <h2 className="gradient-text">{itinerary.destination}</h2>
        <p className="itinerary-meta">
          {itinerary.total_days} days · {itinerary.group_size} traveler{itinerary.group_size > 1 ? 's' : ''} · {itinerary.start_date} → {itinerary.end_date}
        </p>
        {itinerary.summary && <p className="itinerary-desc">{itinerary.summary}</p>}
      </div>
      <div className="days-list">
        {itinerary.days.map((day, idx) => (
          <div key={day.day_number} className={`day-card card animate-fade-in ${expandedDay === idx ? 'expanded' : ''}`} style={{ animationDelay: `${idx * 0.1}s` }}>
            <button className="day-header" onClick={() => setExpandedDay(expandedDay === idx ? -1 : idx)} aria-expanded={expandedDay === idx}>
              <div className="day-header-left">
                <span className="day-number">Day {day.day_number}</span>
                <span className="day-date">{day.date}</span>
              </div>
              <div className="day-header-right">
                {day.theme && <span className="day-theme badge badge-info">{day.theme}</span>}
                <span className="day-cost">{itinerary.currency} {day.day_cost?.toLocaleString() || 0}</span>
                <span className={`day-chevron ${expandedDay === idx ? 'open' : ''}`}>▾</span>
              </div>
            </button>
            <div className="day-content" role="region">
              <div className="timeline">
                {[...(day.activities || []), ...(day.meals || [])].sort((a, b) => (a.time_slot || '').localeCompare(b.time_slot || '')).map((place, pIdx) => (
                  <div key={pIdx} className="timeline-item" onClick={() => onSelectPlace?.(place)} tabIndex={0} role="button" aria-label={`${place.name}`} onKeyDown={(e) => e.key === 'Enter' && onSelectPlace?.(place)}>
                    <div className="timeline-dot">{ICONS[place.category] || ICONS.other}</div>
                    <div className="timeline-content">
                      <div className="timeline-top">
                        <span className="timeline-time">{place.time_slot}</span>
                        {place.is_indoor && <span className="badge badge-success">Indoor</span>}
                      </div>
                      <h4 className="timeline-name">{place.name}</h4>
                      <p className="timeline-desc">{place.description}</p>
                      <div className="timeline-meta">
                        {place.duration_minutes > 0 && <span>⏱ {place.duration_minutes} min</span>}
                        {place.estimated_cost > 0 && <span>💰 {itinerary.currency} {place.estimated_cost.toLocaleString()}</span>}
                        {place.rating && <span>⭐ {place.rating}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {day.travel_tip && <div className="travel-tip"><span>💡</span><span>{day.travel_tip}</span></div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
