/**
 * Custom hook for itinerary generation and adaptation.
 */

import { useState, useCallback } from 'react';
import { generateItinerary, adaptItinerary } from '../utils/api';

export function useItinerary() {
  const [itinerary, setItinerary] = useState(null);
  const [adaptationResult, setAdaptationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [adapting, setAdapting] = useState(false);
  const [error, setError] = useState(null);

  const generate = useCallback(async (tripData) => {
    setLoading(true);
    setError(null);
    setItinerary(null);
    setAdaptationResult(null);
    try {
      const result = await generateItinerary(tripData);
      setItinerary(result);
      return result;
    } catch (err) {
      const message =
        err.response?.data?.detail || 'Failed to generate itinerary. Please try again.';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const adapt = useCallback(async (adaptData) => {
    setAdapting(true);
    setError(null);
    try {
      const result = await adaptItinerary(adaptData);
      setAdaptationResult(result);
      // Replace current itinerary with adapted version
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
      setAdapting(false);
    }
  }, []);

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
