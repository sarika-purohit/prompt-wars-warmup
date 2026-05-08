/**
 * App.jsx — Main application shell for TripFlow AI.
 *
 * Manages the top-level application state and renders the correct
 * view based on the current workflow stage:
 *   1. PlanningView — user fills in trip details
 *   2. SkeletonLoader — loading state while AI generates
 *   3. ResultsView — displays the generated itinerary
 *
 * @component
 * @returns {JSX.Element} The root application layout.
 */

import { useState } from 'react';
import Header from './components/Header';
import PlanningView from './views/PlanningView';
import ResultsView from './views/ResultsView';
import SkeletonLoader from './components/SkeletonLoader';
import { useItinerary } from './hooks/useItinerary';
import './App.css';

export default function App() {
  // Custom hook manages all itinerary state (generate, adapt, reset)
  const {
    itinerary,
    adaptationResult,
    loading,
    adapting,
    error,
    generate,
    adapt,
    reset,
  } = useItinerary();

  // Track which place the user clicked in the timeline (for map focus)
  const [selectedPlace, setSelectedPlace] = useState(null);

  return (
    <div className="app">
      {/* Accessible banner header with brand logo */}
      <Header />

      {/* Main content area — switches between Planning, Loading, and Results */}
      <main className="main-content container" role="main" aria-label="Trip planning workspace">

        {/* Error banner — uses role="alert" for screen reader announcement */}
        {error && (
          <div className="error-banner" role="alert" aria-live="assertive">
            <span aria-hidden="true">⚠️</span>
            <span>{error}</span>
            <button
              className="btn btn-sm btn-secondary"
              onClick={reset}
              aria-label="Dismiss error message"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Conditional rendering based on workflow stage */}
        {loading ? (
          /* Stage 2: Skeleton loader while Gemini AI generates the itinerary */
          <SkeletonLoader />
        ) : !itinerary ? (
          /* Stage 1: Planning form — user enters trip details */
          <PlanningView onGenerate={generate} loading={loading} />
        ) : (
          /* Stage 3: Results — map, timeline, budget, and adaptation */
          <ResultsView
            itinerary={itinerary}
            onReset={reset}
            onAdapt={adapt}
            adapting={adapting}
            adaptationResult={adaptationResult}
          />
        )}
      </main>
    </div>
  );
}
