import { useRef, useEffect, useState } from 'react';
import { useMapsLibrary } from '@vis.gl/react-google-maps';

export default function PlaceAutocomplete({ onPlaceSelect, defaultValue = '' }) {
  const [inputValue, setInputValue] = useState(defaultValue);
  const inputRef = useRef(null);
  const places = useMapsLibrary('places');
  const [autocomplete, setAutocomplete] = useState(null);

  useEffect(() => {
    if (!places || !inputRef.current) return;

    const options = {
      types: ['(cities)'],
      fields: ['formatted_address', 'geometry', 'name', 'place_id'],
    };

    const autocompleteInstance = new places.Autocomplete(inputRef.current, options);
    setAutocomplete(autocompleteInstance);
  }, [places]);

  useEffect(() => {
    if (!autocomplete) return;

    const listener = autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      if (place.formatted_address) {
        setInputValue(place.formatted_address);
        onPlaceSelect(place.formatted_address);
      } else if (place.name) {
        setInputValue(place.name);
        onPlaceSelect(place.name);
      }
    });

    return () => {
      window.google.maps.event.removeListener(listener);
    };
  }, [autocomplete, onPlaceSelect]);

  const handleChange = (e) => {
    setInputValue(e.target.value);
    onPlaceSelect(e.target.value); // Fallback to raw text if they don't select a dropdown item
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
      aria-label="Destination"
    />
  );
}
