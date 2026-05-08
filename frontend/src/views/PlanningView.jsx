import TripForm from '../components/TripForm';

export default function PlanningView({ onGenerate, loading }) {
  return (
    <div className="planning-layout">
      <TripForm onSubmit={onGenerate} loading={loading} />
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
  );
}
