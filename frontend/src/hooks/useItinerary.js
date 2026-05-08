/**
 * useItinerary.js — Custom React hook for itinerary state management.
 *
 * Encapsulates all state and async logic for:
 *   - Generating itineraries via the backend (Google Gemini AI).
 *   - Adapting itineraries based on weather or budget changes.
 *   - Error handling with user-friendly messages.
 *   - Loading/adapting state for UI feedback.
 *
 * @module useItinerary
 * @returns {Object} State and action handlers for itinerary operations.
 */

import { useState, useCallback } from 'react';
import { generateItinerary, adaptItinerary } from '../utils/api';

/**
 * Custom hook that manages the full itinerary lifecycle.
 *
 * @returns {Object} Hook return value containing:
 *   - itinerary: The current generated itinerary (or null).
 *   - adaptationResult: Result of the last adaptation (or null).
 *   - loading: True while generating an itinerary.
 *   - adapting: True while adapting an itinerary.
 *   - error: Error message string (or null).
 *   - generate: Async function to generate a new itinerary.
 *   - adapt: Async function to adapt the current itinerary.
 *   - reset: Function to clear all state and start over.
 */
export function useItinerary() {
  // Core state — the generated itinerary and adaptation result
  const [itinerary, setItinerary] = useState(null);
  const [adaptationResult, setAdaptationResult] = useState(null);

  // UI state — loading indicators and error messages
  const [loading, setLoading] = useState(false);
  const [adapting, setAdapting] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Generate a new itinerary from trip planning data.
   * Calls the backend which uses Google Maps + Gemini AI.
   *
   * @param {Object} tripData - Trip planning parameters from TripForm.
   * @returns {Promise<Object>} The generated itinerary.
   */
  const generate = useCallback(async (tripData) => {
    setLoading(true);
    setError(null);
    setItinerary(null);        // Clear previous results
    setAdaptationResult(null); // Clear previous adaptations

    try {
      // POST to /api/itinerary/generate — triggers Gemini AI
      const result = await generateItinerary(tripData);
      setItinerary(result);
      return result;
    } catch (err) {
      // Extract user-friendly error message from API response
      const message =
        err.response?.data?.detail || 'Failed to generate itinerary. Please try again.';
      setError(message);
      throw err;
    } finally {
      setLoading(false); // Always reset loading state
    }
  }, []);

  /**
   * Adapt the current itinerary based on changed conditions.
   * Supports weather-based re-optimization and budget changes.
   *
   * @param {Object} adaptData - Adaptation parameters (budget, weather, reason).
   * @returns {Promise<Object>} The adaptation result with changes list.
   */
  const adapt = useCallback(async (adaptData) => {
    setAdapting(true);
    setError(null);

    try {
      // POST to /api/adapt/ — triggers weather check + Gemini AI
      const result = await adaptItinerary(adaptData);
      setAdaptationResult(result);

      // Replace current itinerary with the adapted version
      if (result.adapted_itinerary) {
        setItinerary(result.adapted_itinerary);
      }
      return result;
    } catch (err) {
      const message =
        err.response?.data?.detail || 'Failed to adapt itinerary. Please try again.';
      setError(message);
      throw err;
    } finally {
      setAdapting(false); // Always reset adapting state
    }
  }, []);

  /**
   * Reset all state to return to the planning view.
   * Clears itinerary, adaptation, and error state.
   */
  const reset = useCallback(() => {
    setItinerary(null);
    setAdaptationResult(null);
    setError(null);
  }, []);

  return {
    itinerary,
    adaptationResult,
    loading,
    adapting,
    error,
    generate,
    adapt,
    reset,
  };
}
