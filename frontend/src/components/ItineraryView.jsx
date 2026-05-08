/**
 * ItineraryView.jsx — Day-by-day timeline of the trip itinerary.
 *
 * Renders an expandable accordion of daily plans, each containing
 * a chronologically sorted timeline of activities and meals.
 * Clicking a timeline item highlights it on the Google Map.
 *
 * Accessibility:
 *   - Accordion headers use aria-expanded for collapse state.
 *   - Timeline items are keyboard-navigable (tabIndex, onKeyDown).
 *   - Each item has role="button" and aria-label.
 *   - Region landmark with aria-label for screen readers.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.itinerary - The generated itinerary data.
 * @param {Function} props.onSelectPlace - Callback when a place is clicked.
 */

import { useState } from 'react';
import './ItineraryView.css';

// Category icons — maps activity categories to emoji icons
const ICONS = {
  culture: '🏛️', food: '🍜', adventure: '🧗', nature: '🌿',
  shopping: '🛍️', relaxation: '🧘', nightlife: '🌙', history: '📜', other: '📍',
};

export default function ItineraryView({ itinerary, onSelectPlace }) {
  // Track which day accordion is expanded (default: first day)
  const [expandedDay, setExpandedDay] = useState(0);

  // Guard: don't render if there are no days
  if (!itinerary?.days?.length) return null;

  return (
    <div className="itinerary-view" role="region" aria-label="Trip itinerary timeline">
      {/* Trip Summary Card */}
      <div className="itinerary-summary card animate-fade-in">
        <h2 className="gradient-text">{itinerary.destination}</h2>
        <p className="itinerary-meta">
          {itinerary.total_days} days · {itinerary.group_size} traveler{itinerary.group_size > 1 ? 's' : ''} · {itinerary.start_date} → {itinerary.end_date}
        </p>
        {/* AI-generated trip summary */}
        {itinerary.summary && <p className="itinerary-desc">{itinerary.summary}</p>}
      </div>

      {/* Day-by-Day Accordion */}
      <div className="days-list" role="list" aria-label="Daily plans">
        {itinerary.days.map((day, idx) => (
          <div
            key={day.day_number}
            className={`day-card card animate-fade-in ${expandedDay === idx ? 'expanded' : ''}`}
            style={{ animationDelay: `${idx * 0.1}s` }}
            role="listitem"
          >
            {/* Day Header — clickable accordion toggle */}
            <button
              className="day-header"
              onClick={() => setExpandedDay(expandedDay === idx ? -1 : idx)}
              aria-expanded={expandedDay === idx}
              aria-label={`Day ${day.day_number}: ${day.theme || day.date}`}
            >
              <div className="day-header-left">
                <span className="day-number">Day {day.day_number}</span>
                <span className="day-date">{day.date}</span>
              </div>
              <div className="day-header-right">
                {/* Day theme badge */}
                {day.theme && <span className="day-theme badge badge-info">{day.theme}</span>}
                {/* Daily cost */}
                <span className="day-cost">{itinerary.currency} {day.day_cost?.toLocaleString() || 0}</span>
                {/* Chevron indicator */}
                <span className={`day-chevron ${expandedDay === idx ? 'open' : ''}`} aria-hidden="true">▾</span>
              </div>
            </button>

            {/* Day Content — timeline of activities and meals */}
            <div className="day-content" role="region" aria-label={`Day ${day.day_number} activities`}>
              <div className="timeline">
                {/* Sort all activities + meals by time_slot for chronological order */}
                {[...(day.activities || []), ...(day.meals || [])]
                  .sort((a, b) => (a.time_slot || '').localeCompare(b.time_slot || ''))
                  .map((place, pIdx) => (
                    <div
                      key={pIdx}
                      className="timeline-item"
                      onClick={() => onSelectPlace?.(place)}
                      tabIndex={0}
                      role="button"
                      aria-label={`${place.name} — ${place.time_slot}`}
                      onKeyDown={(e) => e.key === 'Enter' && onSelectPlace?.(place)}
                    >
                      {/* Category icon */}
                      <div className="timeline-dot" aria-hidden="true">
                        {ICONS[place.category] || ICONS.other}
                      </div>
                      <div className="timeline-content">
                        {/* Time slot and indoor badge */}
                        <div className="timeline-top">
                          <span className="timeline-time">{place.time_slot}</span>
                          {place.is_indoor && <span className="badge badge-success">Indoor</span>}
                        </div>
                        {/* Place name and description */}
                        <h4 className="timeline-name">{place.name}</h4>
                        <p className="timeline-desc">{place.description}</p>
                        {/* Metadata: duration, cost, rating */}
                        <div className="timeline-meta">
                          {place.duration_minutes > 0 && <span>⏱ {place.duration_minutes} min</span>}
                          {place.estimated_cost > 0 && <span>💰 {itinerary.currency} {place.estimated_cost.toLocaleString()}</span>}
                          {place.rating && <span>⭐ {place.rating}</span>}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
              {/* Daily travel tip */}
              {day.travel_tip && (
                <div className="travel-tip" role="note">
                  <span aria-hidden="true">💡</span>
                  <span>{day.travel_tip}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
