/**
 * TripForm — User input form for trip planning.
 */

import { useState } from 'react';
import PlaceAutocomplete from './PlaceAutocomplete';
import './TripForm.css';

const INTERESTS = [
  { value: 'culture',    label: '🏛️ Culture',    },
  { value: 'food',       label: '🍜 Food',       },
  { value: 'adventure',  label: '🧗 Adventure',  },
  { value: 'nature',     label: '🌿 Nature',     },
  { value: 'shopping',   label: '🛍️ Shopping',   },
  { value: 'relaxation', label: '🧘 Relaxation', },
  { value: 'nightlife',  label: '🌙 Nightlife',  },
  { value: 'history',    label: '📜 History',     },
];

const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'THB', 'AED'];

export default function TripForm({ onSubmit, loading }) {
  const today = new Date().toISOString().split('T')[0];
  
  const [form, setForm] = useState({
    destination: '',
    start_date: '',
    end_date: '',
    budget: '',
    currency: 'INR',
    interests: ['culture', 'food'],
    group_size: 2,
    special_requirements: '',
  });

  const updateField = (key, value) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const toggleInterest = (interest) => {
    setForm((prev) => {
      const current = prev.interests;
      return {
        ...prev,
        interests: current.includes(interest)
          ? current.filter((i) => i !== interest)
          : [...current, interest],
      };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.destination || !form.start_date || !form.end_date || !form.budget) return;
    onSubmit({
      ...form,
      budget: parseFloat(form.budget),
      group_size: parseInt(form.group_size, 10),
    });
  };

  return (
    <form className="trip-form card" onSubmit={handleSubmit} aria-label="Trip planning form">
      <div className="form-header">
        <h2>Plan Your Trip</h2>
        <p className="form-subtitle">Tell us where you want to go</p>
      </div>

      {/* Destination */}
      <div className="input-group">
        <label htmlFor="destination">Destination</label>
        <div className="autocomplete-wrapper">
          <span className="location-icon" aria-hidden="true">📍</span>
          <PlaceAutocomplete
            defaultValue={form.destination}
            onPlaceSelect={(val) => updateField('destination', val)}
          />
        </div>
      </div>

      {/* Dates */}
      <div className="form-row">
        <div className="input-group">
          <label htmlFor="start_date">Start Date</label>
          <input
            id="start_date"
            className="input"
            type="date"
            min={today}
            value={form.start_date}
            onChange={(e) => updateField('start_date', e.target.value)}
            required
          />
        </div>
        <div className="input-group">
          <label htmlFor="end_date">End Date</label>
          <input
            id="end_date"
            className="input"
            type="date"
            min={form.start_date || today}
            value={form.end_date}
            onChange={(e) => updateField('end_date', e.target.value)}
            required
          />
        </div>
      </div>

      {/* Budget + Currency */}
      <div className="form-row">
        <div className="input-group" style={{ flex: 2 }}>
          <label htmlFor="budget">Total Budget</label>
          <input
            id="budget"
            className="input"
            type="number"
            min="1"
            placeholder="15000"
            value={form.budget}
            onChange={(e) => updateField('budget', e.target.value)}
            required
          />
        </div>
        <div className="input-group" style={{ flex: 1 }}>
          <label htmlFor="currency">Currency</label>
          <select
            id="currency"
            className="input"
            value={form.currency}
            onChange={(e) => updateField('currency', e.target.value)}
          >
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Group size */}
      <div className="input-group">
        <label htmlFor="group_size">Group Size</label>
        <input
          id="group_size"
          className="input"
          type="number"
          min="1"
          max="20"
          value={form.group_size}
          onChange={(e) => updateField('group_size', e.target.value)}
        />
      </div>

      {/* Interests */}
      <div className="input-group">
        <label id="interests-label">Interests</label>
        <div className="interests-grid" role="group" aria-labelledby="interests-label">
          {INTERESTS.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              className={`chip ${form.interests.includes(value) ? 'active' : ''}`}
              onClick={() => toggleInterest(value)}
              aria-pressed={form.interests.includes(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Special requirements */}
      <div className="input-group">
        <label htmlFor="special_requirements">Special Requirements (optional)</label>
        <input
          id="special_requirements"
          className="input"
          type="text"
          placeholder="e.g. Vegetarian food, wheelchair accessible"
          value={form.special_requirements}
          onChange={(e) => updateField('special_requirements', e.target.value)}
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        className="btn btn-primary submit-btn"
        disabled={loading}
        aria-busy={loading}
      >
        {loading ? (
          <>
            <span className="spinner" aria-hidden="true" />
            Generating your plan…
          </>
        ) : (
          <>✨ Generate Itinerary</>
        )}
      </button>
    </form>
  );
}
