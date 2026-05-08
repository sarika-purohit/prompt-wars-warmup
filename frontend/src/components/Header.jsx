/**
 * Header — App brand bar with gradient logo.
 */

import './Header.css';

export default function Header() {
  return (
    <header className="header glass" role="banner">
      <div className="header-inner container">
        <div className="header-brand">
          <span className="header-logo" aria-hidden="true">✈️</span>
          <h1 className="header-title">
            <span className="gradient-text">TripFlow</span>
            <span className="header-ai-badge">AI</span>
          </h1>
        </div>
        <p className="header-tagline">Smart itineraries that adapt to life</p>
      </div>
    </header>
  );
}
