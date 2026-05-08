/**
 * ResultsView.jsx — Itinerary results display page.
 *
 * Shows the generated itinerary with four key sections:
 *   1. BudgetTracker — visual budget breakdown with progress bar.
 *   2. AdaptPanel — weather-aware adaptation controls.
 *   3. MapView — Google Maps with color-coded day markers.
 *   4. ItineraryView — day-by-day timeline of activities and meals.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.itinerary - The generated itinerary data.
 * @param {Function} props.onReset - Callback to return to planning view.
 * @param {Function} props.onAdapt - Callback to adapt the itinerary.
 * @param {boolean} props.adapting - Whether adaptation is in progress.
 * @param {Object} props.adaptationResult - Result of the last adaptation.
 */

import { useState } from 'react';
import BudgetTracker from '../components/BudgetTracker';
import AdaptPanel from '../components/AdaptPanel';
import MapView from '../components/MapView';
import ItineraryView from '../components/ItineraryView';

export default function ResultsView({ itinerary, onReset, onAdapt, adapting, adaptationResult }) {
  // Track which place the user selected in the timeline for map focus
  const [selectedPlace, setSelectedPlace] = useState(null);

  return (
    <section className="results-layout" aria-label="Trip results">
      {/* Sidebar — budget overview and adaptation controls */}
      <aside className="results-sidebar" aria-label="Trip controls">
        {/* Back button to start a new trip */}
        <button
          className="btn btn-secondary btn-sm back-btn"
          onClick={onReset}
          aria-label="Start a new trip"
        >
          ← New Trip
        </button>

        {/* Budget visualization with progress bar and category breakdown */}
        <BudgetTracker itinerary={itinerary} />

        {/* Weather-aware adaptation panel */}
        <AdaptPanel
          itinerary={itinerary}
          onAdapt={onAdapt}
          adapting={adapting}
          adaptationResult={adaptationResult}
        />
      </aside>

      {/* Main content — Google Maps and day-by-day timeline */}
      <div className="results-main">
        {/* Interactive Google Maps with color-coded markers per day */}
        <MapView itinerary={itinerary} selectedPlace={selectedPlace} />

        {/* Day-by-day itinerary timeline with activities and meals */}
        <ItineraryView itinerary={itinerary} onSelectPlace={setSelectedPlace} />
      </div>
    </section>
  );
}
