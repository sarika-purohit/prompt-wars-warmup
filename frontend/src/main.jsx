/**
 * main.jsx — React application entry point.
 *
 * Bootstraps the React 18 application using createRoot API.
 * StrictMode is enabled to catch potential issues during development.
 *
 * @module main
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';   // Global design system styles
import App from './App.jsx';

// SEO: Set the document title for search engines and browser tabs
document.title = 'TripFlow AI — Smart Travel Planner';

// Mount the React app to the #root DOM element
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
