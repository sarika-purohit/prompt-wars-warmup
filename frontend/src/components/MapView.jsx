/**
 * MapView.jsx — Interactive Google Maps with itinerary markers.
 *
 * Renders an interactive Google Map using the @vis.gl/react-google-maps
 * SDK.  Each day's activities are shown as color-coded AdvancedMarkers,
 * with InfoWindows for place details on click.
 *
 * Google Services:
 *   - Google Maps JavaScript API — renders the interactive map.
 *   - AdvancedMarkers with custom Pin colors per day.
 *   - InfoWindow for place detail popups.
 *
 * Accessibility:
 *   - Map region has aria-label for screen readers.
 *   - Day legend helps users identify color coding.
 *   - Falls back to a helpful message if no API key is set.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.itinerary - The generated itinerary with place coordinates.
 * @param {Object} props.selectedPlace - Currently selected place for map focus.
 */

import { useMemo } from 'react';
import { APIProvider, Map, AdvancedMarker, Pin, InfoWindow } from '@vis.gl/react-google-maps';
import { useState } from 'react';
import './MapView.css';

// SECURITY: Maps key loaded from environment variable, never hardcoded
const MAPS_KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY || '';

// Color palette for day markers — each day gets a unique color
const DAY_COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#ec4899', '#38bdf8', '#8b5cf6', '#f97316'];

export default function MapView({ itinerary, selectedPlace }) {
  // Track which marker's InfoWindow is currently open
  const [activeMarker, setActiveMarker] = useState(null);

  // EFFICIENCY: Memoize marker extraction — only recalculate when itinerary changes
  const markers = useMemo(() => {
    if (!itinerary?.days) return [];
    const result = [];
    itinerary.days.forEach((day, dayIdx) => {
      // Combine activities and meals for unified marker placement
      const allPlaces = [...(day.activities || []), ...(day.meals || [])];
      allPlaces.forEach((place) => {
        // Only add markers for places with valid coordinates
        if (place.latitude && place.longitude) {
          result.push({
            ...place,
            dayIndex: dayIdx,
            color: DAY_COLORS[dayIdx % DAY_COLORS.length],
          });
        }
      });
    });
    return result;
  }, [itinerary]);

  // EFFICIENCY: Memoize center calculation — auto-centers on selected place or average
  const center = useMemo(() => {
    // Priority 1: Center on the selected place (from timeline click)
    if (selectedPlace?.latitude && selectedPlace?.longitude) {
      return { lat: selectedPlace.latitude, lng: selectedPlace.longitude };
    }
    // Priority 2: Center on the average of all markers
    if (markers.length > 0) {
      const avgLat = markers.reduce((s, m) => s + m.latitude, 0) / markers.length;
      const avgLng = markers.reduce((s, m) => s + m.longitude, 0) / markers.length;
      return { lat: avgLat, lng: avgLng };
    }
    // Priority 3: Default center (Jaipur, India)
    return { lat: 26.9124, lng: 75.7873 };
  }, [markers, selectedPlace]);

  // Fallback: Show helpful message if Google Maps API key is not configured
  if (!MAPS_KEY) {
    return (
      <div className="map-placeholder card" role="region" aria-label="Map placeholder">
        <div className="map-placeholder-content">
          <span className="map-placeholder-icon" aria-hidden="true">🗺️</span>
          <p>Add <code>VITE_GOOGLE_MAPS_KEY</code> to your <code>.env</code> to enable the interactive map.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="map-container card" role="region" aria-label="Interactive trip map">
      {/* Map Header with day color legend */}
      <div className="map-header">
        <h3>🗺️ Trip Map</h3>
        <div className="map-legend" aria-label="Day color legend">
          {itinerary?.days?.map((day, idx) => (
            <span key={idx} className="legend-item">
              <span
                className="legend-dot"
                style={{ background: DAY_COLORS[idx % DAY_COLORS.length] }}
                aria-hidden="true"
              />
              Day {day.day_number}
            </span>
          ))}
        </div>
      </div>

      {/* Google Maps API Provider — wraps all map components */}
      <APIProvider apiKey={MAPS_KEY}>
        <Map
          className="map-inner"
          defaultCenter={center}
          defaultZoom={12}
          gestureHandling="greedy"
          mapId="tripflow-map"
        >
          {/* Render color-coded AdvancedMarkers for each place */}
          {markers.map((m, idx) => (
            <AdvancedMarker
              key={idx}
              position={{ lat: m.latitude, lng: m.longitude }}
              onClick={() => setActiveMarker(idx)}
              title={m.name}
            >
              <Pin background={m.color} glyphColor="#fff" borderColor={m.color} />
            </AdvancedMarker>
          ))}

          {/* InfoWindow popup — shows place details on marker click */}
          {activeMarker !== null && markers[activeMarker] && (
            <InfoWindow
              position={{ lat: markers[activeMarker].latitude, lng: markers[activeMarker].longitude }}
              onCloseClick={() => setActiveMarker(null)}
            >
              <div className="info-window">
                <strong>{markers[activeMarker].name}</strong>
                <p>{markers[activeMarker].description}</p>
                <span className="info-time">{markers[activeMarker].time_slot}</span>
              </div>
            </InfoWindow>
          )}
        </Map>
      </APIProvider>
    </div>
  );
}
