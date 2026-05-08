/**
 * AdaptPanel — Weather-aware itinerary adaptation controls.
 */

import { useState } from 'react';
import './AdaptPanel.css';

export default function AdaptPanel({ itinerary, onAdapt, adapting, adaptationResult }) {
  const [newBudget, setNewBudget] = useState('');
  const [reason, setReason] = useState('');

  if (!itinerary?.id) return null;

  const handleAdapt = (weatherOnly = false) => {
    onAdapt({
      itinerary_id: itinerary.id,
      weather_check: true,
      new_budget: newBudget ? parseFloat(newBudget) : null,
      reason: weatherOnly ? 'Check weather and adjust accordingly' : reason || null,
      excluded_places: [],
    });
  };

  return (
    <div className="adapt-panel card animate-fade-in" role="region" aria-label="Adapt itinerary">
      <h3 className="adapt-title">🔄 Adapt Your Plan</h3>
      <p className="adapt-desc">Conditions changed? Let AI re-optimize your itinerary.</p>

      <div className="adapt-actions">
        <button className="btn btn-warning btn-sm" onClick={() => handleAdapt(true)} disabled={adapting} aria-busy={adapting}>
          {adapting ? <><span className="spinner" /> Checking…</> : '🌦️ Check Weather & Adapt'}
        </button>
      </div>

      <div className="adapt-custom">
        <div className="input-group">
          <label htmlFor="new-budget">New Budget ({itinerary.currency})</label>
          <input id="new-budget" className="input" type="number" min="1" placeholder={String(itinerary.budget)} value={newBudget} onChange={(e) => setNewBudget(e.target.value)} />
        </div>
        <div className="input-group">
          <label htmlFor="adapt-reason">What changed?</label>
          <input id="adapt-reason" className="input" type="text" placeholder="e.g. It's raining, one person cancelled" value={reason} onChange={(e) => setReason(e.target.value)} />
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => handleAdapt(false)} disabled={adapting}>
          ✨ Re-optimize
        </button>
      </div>

      {/* Adaptation result */}
      {adaptationResult && (
        <div className="adapt-result">
          <h4>Changes Made</h4>
          <ul className="changes-list">
            {adaptationResult.changes?.map((change, i) => (
              <li key={i} className="change-item">
                <span className="change-icon">→</span>
                {change}
              </li>
            ))}
          </ul>
          {adaptationResult.reason && <p className="adapt-reason"><strong>Reason:</strong> {adaptationResult.reason}</p>}

          {/* Weather info */}
          {adaptationResult.weather_info?.forecasts && (
            <div className="weather-grid">
              <h4>Weather Forecast</h4>
              <div className="weather-cards">
                {adaptationResult.weather_info.forecasts.map((f, i) => (
                  <div key={i} className={`weather-card ${f.is_bad_weather ? 'bad' : ''}`}>
                    <span className="weather-date">{f.date}</span>
                    <span className="weather-condition">{f.condition}</span>
                    <span className="weather-temp">{f.temp_min}°–{f.temp_max}°C</span>
                    {f.rain_probability > 0 && <span className="weather-rain">🌧 {f.rain_probability}%</span>}
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
