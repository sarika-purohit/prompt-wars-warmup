/**
 * App — Main application shell assembling all components.
 */

import { useState } from 'react';
import Header from './components/Header';
import TripForm from './components/TripForm';
import ItineraryView from './components/ItineraryView';
import MapView from './components/MapView';
import BudgetTracker from './components/BudgetTracker';
import AdaptPanel from './components/AdaptPanel';
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

        {!itinerary ? (
          /* ── Planning Mode ──────────────────────────────── */
          <div className="planning-layout">
            <TripForm onSubmit={generate} loading={loading} />
            <div className="hero-section">
              <div className="hero-content">
                <h2 className="hero-title">
                  Plan smarter.<br />
                  <span className="gradient-text">Travel better.</span>
                </h2>
                <p className="hero-desc">
                  TripFlow AI creates personalized, budget-aware itineraries powered by Google Maps
                  and Gemini AI — and adapts them when conditions change.
                </p>
                <div className="hero-features">
                  <div className="hero-feature">
                    <span className="hero-feature-icon">🗺️</span>
                    <span>Real places from Google Maps</span>
                  </div>
                  <div className="hero-feature">
                    <span className="hero-feature-icon">🤖</span>
                    <span>AI-optimized scheduling</span>
                  </div>
                  <div className="hero-feature">
                    <span className="hero-feature-icon">🌦️</span>
                    <span>Weather-aware adaptation</span>
                  </div>
                  <div className="hero-feature">
                    <span className="hero-feature-icon">💰</span>
                    <span>Budget tracking built-in</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* ── Results Mode ───────────────────────────────── */
          <div className="results-layout">
            <div className="results-sidebar">
              <button className="btn btn-secondary btn-sm back-btn" onClick={reset}>
                ← New Trip
              </button>
              <BudgetTracker itinerary={itinerary} />
              <AdaptPanel
                itinerary={itinerary}
                onAdapt={adapt}
                adapting={adapting}
                adaptationResult={adaptationResult}
              />
            </div>
            <div className="results-main">
              <MapView itinerary={itinerary} selectedPlace={selectedPlace} />
              <ItineraryView itinerary={itinerary} onSelectPlace={setSelectedPlace} />
            </div>
          </div>
        )}

        {/* Loading overlay */}
        {loading && (
          <div className="loading-overlay" role="status" aria-label="Generating itinerary">
            <div className="loading-card glass">
              <div className="loading-spinner-lg" />
              <h3>Crafting your perfect trip…</h3>
              <p>Searching places, checking routes, and optimizing your schedule.</p>
              <div className="loading-steps">
                <span className="loading-step active">📍 Finding places</span>
                <span className="loading-step">🧠 AI planning</span>
                <span className="loading-step">✅ Finalizing</span>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
