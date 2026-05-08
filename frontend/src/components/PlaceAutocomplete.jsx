/**
 * PlaceAutocomplete.jsx — Google Places Autocomplete input.
 *
 * Integrates with Google Maps Places Autocomplete API to provide
 * city-level destination suggestions as the user types.
 *
 * Google Services:
 *   - Google Places Autocomplete API — validates and suggests
 *     real cities/destinations from Google's database.
 *
 * Accessibility:
 *   - Input has aria-label for screen readers.
 *   - Falls back to raw text input if Google Maps is not loaded.
 *
 * @component
 * @param {Object} props
 * @param {Function} props.onPlaceSelect - Callback when a place is selected.
 * @param {string} props.defaultValue - Initial input value.
 */

import { useRef, useEffect, useState } from 'react';
import { useMapsLibrary } from '@vis.gl/react-google-maps';

export default function PlaceAutocomplete({ onPlaceSelect, defaultValue = '' }) {
  // Controlled input value for the destination field
  const [inputValue, setInputValue] = useState(defaultValue);
  const inputRef = useRef(null);

  // Load the Google Maps "places" library for Autocomplete
  const places = useMapsLibrary('places');
  const [autocomplete, setAutocomplete] = useState(null);

  // Initialize Google Places Autocomplete when the library loads
  useEffect(() => {
    if (!places || !inputRef.current) return;

    // Configure autocomplete to only suggest cities
    const options = {
      types: ['(cities)'],   // Restrict to city-level results
      fields: ['formatted_address', 'geometry', 'name', 'place_id'],
    };

    // Create the Autocomplete instance and attach it to the input
    const autocompleteInstance = new places.Autocomplete(inputRef.current, options);
    setAutocomplete(autocompleteInstance);
  }, [places]);

  // Listen for place selection events from the Autocomplete dropdown
  useEffect(() => {
    if (!autocomplete) return;

    const listener = autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      // Use formatted_address if available, fall back to name
      if (place.formatted_address) {
        setInputValue(place.formatted_address);
        onPlaceSelect(place.formatted_address);
      } else if (place.name) {
        setInputValue(place.name);
        onPlaceSelect(place.name);
      }
    });

    // Cleanup: remove the event listener on unmount
    return () => {
      window.google.maps.event.removeListener(listener);
    };
  }, [autocomplete, onPlaceSelect]);

  /**
   * Handle manual text input — allows typing without selecting
   * from the dropdown (fallback for when autocomplete isn't available).
   */
  const handleChange = (e) => {
    setInputValue(e.target.value);
    onPlaceSelect(e.target.value);
  };

  return (
    <input
      ref={inputRef}
      className="input"
      type="text"
      placeholder="e.g. Kyoto, Japan"
      value={inputValue}
      onChange={handleChange}
      required
      autoFocus
      id="destination"
      aria-label="Destination city"
      aria-autocomplete="list"
      aria-describedby="destination-help"
    />
  );
}
