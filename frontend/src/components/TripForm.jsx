/**
 * TripForm.jsx — User input form for trip planning.
 *
 * Collects destination, dates, budget, interests, and group size
 * from the user.  Validates required fields before submission.
 *
 * Accessibility:
 *   - All inputs have associated <label> elements with htmlFor.
 *   - Interest chips use aria-pressed for toggle state.
 *   - Submit button uses aria-busy during loading.
 *   - Form has aria-label for screen readers.
 *
 * Google Services:
 *   - Uses PlaceAutocomplete component (Google Places Autocomplete API)
 *     for validated destination input.
 *
 * @component
 * @param {Object} props
 * @param {Function} props.onSubmit - Callback when form is submitted with valid data.
 * @param {boolean} props.loading - Whether itinerary generation is in progress.
 */

import { useState } from 'react';
import PlaceAutocomplete from './PlaceAutocomplete';
import './TripForm.css';

// Available travel interest categories — each maps to a Google Maps query filter
const INTERESTS = [
  { value: 'culture',    label: '🏛️ Culture'    },
  { value: 'food',       label: '🍜 Food'       },
  { value: 'adventure',  label: '🧗 Adventure'  },
  { value: 'nature',     label: '🌿 Nature'     },
  { value: 'shopping',   label: '🛍️ Shopping'   },
  { value: 'relaxation', label: '🧘 Relaxation' },
  { value: 'nightlife',  label: '🌙 Nightlife'  },
  { value: 'history',    label: '📜 History'     },
];

// Supported currency codes for budget input
const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'THB', 'AED'];

export default function TripForm({ onSubmit, loading }) {
  // Calculate today's date for date picker minimum values
  const today = new Date().toISOString().split('T')[0];

  // Form state — all fields with sensible defaults
  const [form, setForm] = useState({
    destination: '',
    start_date: '',
    end_date: '',
    budget: '',
    currency: 'INR',
    interests: ['culture', 'food'], // Default interests
    group_size: 2,
    special_requirements: '',
  });

  /**
   * Update a single form field immutably.
   * @param {string} key - Field name to update.
   * @param {*} value - New value for the field.
   */
  const updateField = (key, value) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  /**
   * Toggle an interest on/off in the interests array.
   * @param {string} interest - Interest value to toggle.
   */
  const toggleInterest = (interest) => {
    setForm((prev) => {
      const current = prev.interests;
      return {
        ...prev,
        interests: current.includes(interest)
          ? current.filter((i) => i !== interest)  // Remove if already selected
          : [...current, interest],                 // Add if not selected
      };
    });
  };

  /**
   * Handle form submission — validates and passes data to parent.
   * @param {Event} e - Form submit event.
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    // SECURITY: Validate all required fields before submission
    if (!form.destination || !form.start_date || !form.end_date || !form.budget) return;
    onSubmit({
      ...form,
      budget: parseFloat(form.budget),        // Convert string to number
      group_size: parseInt(form.group_size, 10), // Ensure integer
    });
  };

  return (
    <form
      className="trip-form card"
      onSubmit={handleSubmit}
      aria-label="Trip planning form"
    >
      {/* Form Header */}
      <div className="form-header">
        <h2>Plan Your Trip</h2>
        <p className="form-subtitle">Tell us where you want to go</p>
      </div>

      {/* Destination — uses Google Places Autocomplete for validation */}
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

      {/* Date Range — start and end dates with min validation */}
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
            aria-required="true"
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
            aria-required="true"
          />
        </div>
      </div>

      {/* Budget + Currency — side by side for compact layout */}
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
            aria-required="true"
          />
        </div>
        <div className="input-group" style={{ flex: 1 }}>
          <label htmlFor="currency">Currency</label>
          <select
            id="currency"
            className="input"
            value={form.currency}
            onChange={(e) => updateField('currency', e.target.value)}
            aria-label="Select currency"
          >
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Group Size — number input with min/max constraints */}
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
          aria-describedby="group-size-help"
        />
      </div>

      {/* Interests — toggle chips with aria-pressed for accessibility */}
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
              aria-label={`Toggle ${value} interest`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Special Requirements — optional accessibility/dietary needs */}
      <div className="input-group">
        <label htmlFor="special_requirements">Special Requirements (optional)</label>
        <input
          id="special_requirements"
          className="input"
          type="text"
          placeholder="e.g. Vegetarian food, wheelchair accessible"
          value={form.special_requirements}
          onChange={(e) => updateField('special_requirements', e.target.value)}
          aria-label="Special requirements such as dietary needs or accessibility"
        />
      </div>

      {/* Submit Button — shows spinner during AI generation */}
      <button
        type="submit"
        className="btn btn-primary submit-btn"
        disabled={loading}
        aria-busy={loading}
        aria-label={loading ? 'Generating itinerary, please wait' : 'Generate travel itinerary'}
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
