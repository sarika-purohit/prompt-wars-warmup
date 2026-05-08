/**
 * Header.jsx — Application brand bar with gradient logo.
 *
 * Renders the TripFlow AI brand header using semantic HTML.
 * Uses role="banner" for accessibility landmark navigation.
 *
 * @component
 * @returns {JSX.Element} The application header bar.
 */

import './Header.css';

export default function Header() {
  return (
    /* Semantic <header> with role="banner" for screen reader navigation */
    <header className="header glass" role="banner">
      <div className="header-inner container">
        {/* Brand logo and title */}
        <div className="header-brand">
          <span className="header-logo" aria-hidden="true">✈️</span>
          <h1 className="header-title">
            <span className="gradient-text">TripFlow</span>
            <span className="header-ai-badge">AI</span>
          </h1>
        </div>
        {/* Tagline — describes the app purpose */}
        <p className="header-tagline">Smart itineraries that adapt to life</p>
      </div>
    </header>
  );
}
