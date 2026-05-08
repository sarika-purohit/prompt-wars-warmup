/**
 * AdaptPanel.jsx — Weather-aware itinerary adaptation controls.
 *
 * Allows users to re-optimize their itinerary when conditions change:
 *   - One-click weather check with automatic outdoor→indoor swaps.
 *   - Budget adjustment for revised spending limits.
 *   - Free-text reason for custom adaptation requests.
 *
 * Displays adaptation results including:
 *   - List of human-readable changes made by the AI.
 *   - Weather forecast cards (if weather data was fetched).
 *
 * Accessibility:
 *   - Panel uses role="region" with aria-label.
 *   - Buttons use aria-busy during async operations.
 *   - Form inputs have associated labels with htmlFor.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.itinerary - Current itinerary to adapt.
 * @param {Function} props.onAdapt - Callback to trigger adaptation.
 * @param {boolean} props.adapting - Whether adaptation is in progress.
 * @param {Object} props.adaptationResult - Result of last adaptation.
 */

import { useState } from 'react';
import './AdaptPanel.css';

export default function AdaptPanel({ itinerary, onAdapt, adapting, adaptationResult }) {
  // Local state for adaptation form inputs
  const [newBudget, setNewBudget] = useState('');
  const [reason, setReason] = useState('');

  // Guard: don't render without a valid itinerary ID
  if (!itinerary?.id) return null;

  /**
   * Trigger itinerary adaptation via the backend.
   * Weather-only mode just checks weather; custom mode includes user inputs.
   *
   * @param {boolean} weatherOnly - If true, only check weather and adapt.
   */
  const handleAdapt = (weatherOnly = false) => {
    onAdapt({
      itinerary_id: itinerary.id,
      weather_check: true,  // Always check weather for smart adaptation
      new_budget: newBudget ? parseFloat(newBudget) : null,
      reason: weatherOnly ? 'Check weather and adjust accordingly' : reason || null,
      excluded_places: [],
    });
  };

  return (
    <div className="adapt-panel card animate-fade-in" role="region" aria-label="Adapt itinerary controls">
      <h3 className="adapt-title">🔄 Adapt Your Plan</h3>
      <p className="adapt-desc">Conditions changed? Let AI re-optimize your itinerary.</p>

      {/* Quick Action: Weather-based adaptation */}
      <div className="adapt-actions">
        <button
          className="btn btn-warning btn-sm"
          onClick={() => handleAdapt(true)}
          disabled={adapting}
          aria-busy={adapting}
          aria-label="Check weather and adapt itinerary"
        >
          {adapting ? <><span className="spinner" aria-hidden="true" /> Checking…</> : '🌦️ Check Weather & Adapt'}
        </button>
      </div>

      {/* Custom Adaptation Form — budget change + reason */}
      <div className="adapt-custom">
        <div className="input-group">
          <label htmlFor="new-budget">New Budget ({itinerary.currency})</label>
          <input
            id="new-budget"
            className="input"
            type="number"
            min="1"
            placeholder={String(itinerary.budget)}
            value={newBudget}
            onChange={(e) => setNewBudget(e.target.value)}
            aria-label={`New budget in ${itinerary.currency}`}
          />
        </div>
        <div className="input-group">
          <label htmlFor="adapt-reason">What changed?</label>
          <input
            id="adapt-reason"
            className="input"
            type="text"
            placeholder="e.g. It's raining, one person cancelled"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            aria-label="Reason for itinerary adaptation"
          />
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => handleAdapt(false)}
          disabled={adapting}
          aria-label="Re-optimize itinerary with custom changes"
        >
          ✨ Re-optimize
        </button>
      </div>

      {/* Adaptation Results — displayed after successful adaptation */}
      {adaptationResult && (
        <div className="adapt-result" role="region" aria-label="Adaptation results">
          {/* List of changes made by the AI */}
          <h4>Changes Made</h4>
          <ul className="changes-list" role="list">
            {adaptationResult.changes?.map((change, i) => (
              <li key={i} className="change-item" role="listitem">
                <span className="change-icon" aria-hidden="true">→</span>
                {change}
              </li>
            ))}
          </ul>
          {/* Explanation of why changes were made */}
          {adaptationResult.reason && (
            <p className="adapt-reason"><strong>Reason:</strong> {adaptationResult.reason}</p>
          )}

          {/* Weather Forecast Cards — shows daily weather conditions */}
          {adaptationResult.weather_info?.forecasts && (
            <div className="weather-grid" role="region" aria-label="Weather forecast">
              <h4>Weather Forecast</h4>
              <div className="weather-cards">
                {adaptationResult.weather_info.forecasts.map((f, i) => (
                  <div
                    key={i}
                    className={`weather-card ${f.is_bad_weather ? 'bad' : ''}`}
                    aria-label={`${f.date}: ${f.condition}, ${f.temp_min}° to ${f.temp_max}°C`}
                  >
                    <span className="weather-date">{f.date}</span>
                    <span className="weather-condition">{f.condition}</span>
                    <span className="weather-temp">{f.temp_min}°–{f.temp_max}°C</span>
                    {f.rain_probability > 0 && (
                      <span className="weather-rain">🌧 {f.rain_probability}%</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
