/**
 * TripFlow AI — API utility module.
 *
 * Centralises all HTTP communication with the backend.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60_000, // Gemini can be slow
  headers: { 'Content-Type': 'application/json' },
});

/* ── Itinerary ────────────────────────────────────────────── */

export async function generateItinerary(tripData) {
  const response = await api.post('/api/itinerary/generate', tripData);
  return response.data;
}

export async function getItinerary(id) {
  const response = await api.get(`/api/itinerary/${id}`);
  return response.data;
}

/* ── Adaptation ───────────────────────────────────────────── */

export async function adaptItinerary(adaptData) {
  const response = await api.post('/api/adapt/', adaptData);
  return response.data;
}

export async function getWeather(lat, lng, startDate, endDate) {
  const response = await api.get('/api/adapt/weather', {
    params: { lat, lng, start_date: startDate, end_date: endDate },
  });
  return response.data;
}

/* ── Places ───────────────────────────────────────────────── */

export async function searchPlaces(query, lat, lng) {
  const response = await api.get('/api/places/search', {
    params: { q: query, lat, lng },
  });
  return response.data;
}

export async function geocode(address) {
  const response = await api.get('/api/places/geocode', {
    params: { address },
  });
  return response.data;
}

/* ── Health ────────────────────────────────────────────────── */

export async function healthCheck() {
  const response = await api.get('/health');
  return response.data;
}

export default api;
