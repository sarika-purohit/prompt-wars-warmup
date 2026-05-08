/**
 * App — Main application shell assembling all components.
 */

import { useState } from 'react';
import Header from './components/Header';
import PlanningView from './views/PlanningView';
import ResultsView from './views/ResultsView';
import SkeletonLoader from './components/SkeletonLoader';
import { useItinerary } from './hooks/useItinerary';
import './App.css';

export default function App() {
  const { itinerary, adaptationResult, loading, adapting, error, generate, adapt, reset } = useItinerary();
  const [selectedPlace, setSelectedPlace] = useState(null);

  return (
    <div className="app">
      <Header />
      <main className="main-content container">
        {error && (
          <div className="error-banner" role="alert">
            <span>⚠️</span>
            <span>{error}</span>
            <button className="btn btn-sm btn-secondary" onClick={reset}>Dismiss</button>
          </div>
        )}

        {loading ? (
          <SkeletonLoader />
        ) : !itinerary ? (
          /* ── Planning Mode ──────────────────────────────── */
          <PlanningView onGenerate={generate} loading={loading} />
        ) : (
          /* ── Results Mode ───────────────────────────────── */
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
