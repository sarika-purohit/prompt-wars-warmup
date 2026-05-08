/**
 * PlanningView.jsx — Trip planning page layout.
 *
 * Renders the TripForm alongside a hero section that highlights
 * the key features of TripFlow AI.  This is the first view users
 * see when they visit the application.
 *
 * @component
 * @param {Object} props
 * @param {Function} props.onGenerate - Callback to generate an itinerary.
 * @param {boolean} props.loading - Whether generation is in progress.
 */

import TripForm from '../components/TripForm';

export default function PlanningView({ onGenerate, loading }) {
  return (
    <section className="planning-layout" aria-label="Trip planning">
      {/* Left side: Trip planning form */}
      <TripForm onSubmit={onGenerate} loading={loading} />

      {/* Right side: Hero section with feature highlights */}
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

          {/* Feature list — highlights Google service integrations */}
          <div className="hero-features" role="list" aria-label="Key features">
            <div className="hero-feature" role="listitem">
              <span className="hero-feature-icon" aria-hidden="true">🗺️</span>
              <span>Real places from Google Maps</span>
            </div>
            <div className="hero-feature" role="listitem">
              <span className="hero-feature-icon" aria-hidden="true">🤖</span>
              <span>AI-optimized scheduling</span>
            </div>
            <div className="hero-feature" role="listitem">
              <span className="hero-feature-icon" aria-hidden="true">🌦️</span>
              <span>Weather-aware adaptation</span>
            </div>
            <div className="hero-feature" role="listitem">
              <span className="hero-feature-icon" aria-hidden="true">💰</span>
              <span>Budget tracking built-in</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
