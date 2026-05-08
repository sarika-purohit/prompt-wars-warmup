/**
 * api.js — Centralized API client for TripFlow AI.
 *
 * All HTTP communication with the FastAPI backend is routed through
 * this module.  Uses axios with a 60-second timeout to accommodate
 * Gemini AI generation times.
 *
 * Google Services accessed through these endpoints:
 *   - /api/itinerary/generate → Google Maps + Gemini 2.0 Flash
 *   - /api/places/search → Google Maps Places API (New)
 *   - /api/places/geocode → Google Maps Geocoding API
 *   - /api/adapt/ → Weather API + Gemini AI adaptation
 *
 * @module api
 */

import axios from 'axios';

// EFFICIENCY: Use environment variable for API URL, fallback to localhost
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Create a reusable axios instance with shared configuration
const api = axios.create({
  baseURL: API_BASE,
  timeout: 60_000, // 60s timeout — Gemini generation can take 10-30s
  headers: { 'Content-Type': 'application/json' },
});

/* ── Itinerary Endpoints ─────────────────────────────────────────── */

/**
 * Generate a new AI-powered travel itinerary.
 * Backend pipeline: Google Maps → Gemini 2.0 Flash → Firestore cache.
 *
 * @param {Object} tripData - Trip planning parameters (destination, dates, budget, interests).
 * @returns {Promise<Object>} The generated Itinerary object.
 */
export async function generateItinerary(tripData) {
  const response = await api.post('/api/itinerary/generate', tripData);
  return response.data;
}

/**
 * Retrieve a previously generated itinerary by ID from Firestore.
 *
 * @param {string} id - Unique 12-character hex itinerary identifier.
 * @returns {Promise<Object>} The stored Itinerary object.
 */
export async function getItinerary(id) {
  const response = await api.get(`/api/itinerary/${id}`);
  return response.data;
}

/* ── Adaptation Endpoints ────────────────────────────────────────── */

/**
 * Adapt an existing itinerary based on changed conditions.
 * Supports weather-based re-optimization and budget changes.
 *
 * @param {Object} adaptData - Adaptation parameters (itinerary_id, new_budget, reason).
 * @returns {Promise<Object>} AdaptationResult with changes list and weather data.
 */
export async function adaptItinerary(adaptData) {
  const response = await api.post('/api/adapt/', adaptData);
  return response.data;
}

/**
 * Fetch weather forecast for a location and date range.
 * Uses Open-Meteo API (no key required) via the backend.
 *
 * @param {number} lat - Latitude of the destination.
 * @param {number} lng - Longitude of the destination.
 * @param {string} startDate - Trip start date (YYYY-MM-DD).
 * @param {string} endDate - Trip end date (YYYY-MM-DD).
 * @returns {Promise<Object>} Weather forecast with daily conditions.
 */
export async function getWeather(lat, lng, startDate, endDate) {
  const response = await api.get('/api/adapt/weather', {
    params: { lat, lng, start_date: startDate, end_date: endDate },
  });
  return response.data;
}

/* ── Places Endpoints (Google Maps Platform) ─────────────────────── */

/**
 * Search for places using Google Maps Places API (New).
 * Supports optional location bias for destination-specific results.
 *
 * @param {string} query - Free-text search query (e.g., "restaurants in Kyoto").
 * @param {number} [lat] - Optional latitude for location bias.
 * @param {number} [lng] - Optional longitude for location bias.
 * @returns {Promise<Array>} Array of simplified place objects.
 */
export async function searchPlaces(query, lat, lng) {
  const response = await api.get('/api/places/search', {
    params: { q: query, lat, lng },
  });
  return response.data;
}

/**
 * Geocode an address to coordinates using Google Maps Geocoding API.
 *
 * @param {string} address - Human-readable address or place name.
 * @returns {Promise<Object>} Object with lat and lng properties.
 */
export async function geocode(address) {
  const response = await api.get('/api/places/geocode', {
    params: { address },
  });
  return response.data;
}

/* ── Health Check ────────────────────────────────────────────────── */

/**
 * Check if the backend API is healthy and responsive.
 * Used for Cloud Run liveness probes and client-side health monitoring.
 *
 * @returns {Promise<Object>} Health status object with version info.
 */
export async function healthCheck() {
  const response = await api.get('/health');
  return response.data;
}

export default api;
