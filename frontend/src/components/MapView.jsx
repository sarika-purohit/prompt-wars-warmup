/**
 * MapView — Google Maps with itinerary markers and routes.
 */

import { useMemo } from 'react';
import { APIProvider, Map, AdvancedMarker, Pin, InfoWindow } from '@vis.gl/react-google-maps';
import { useState } from 'react';
import './MapView.css';

const MAPS_KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY || '';

const DAY_COLORS = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#ec4899', '#38bdf8', '#8b5cf6', '#f97316'];

export default function MapView({ itinerary, selectedPlace }) {
  const [activeMarker, setActiveMarker] = useState(null);

  const markers = useMemo(() => {
    if (!itinerary?.days) return [];
    const result = [];
    itinerary.days.forEach((day, dayIdx) => {
      const allPlaces = [...(day.activities || []), ...(day.meals || [])];
      allPlaces.forEach((place) => {
        if (place.latitude && place.longitude) {
          result.push({ ...place, dayIndex: dayIdx, color: DAY_COLORS[dayIdx % DAY_COLORS.length] });
        }
      });
    });
    return result;
  }, [itinerary]);

  const center = useMemo(() => {
    if (selectedPlace?.latitude && selectedPlace?.longitude) {
      return { lat: selectedPlace.latitude, lng: selectedPlace.longitude };
    }
    if (markers.length > 0) {
      const avgLat = markers.reduce((s, m) => s + m.latitude, 0) / markers.length;
      const avgLng = markers.reduce((s, m) => s + m.longitude, 0) / markers.length;
      return { lat: avgLat, lng: avgLng };
    }
    return { lat: 26.9124, lng: 75.7873 }; // Default: Jaipur
  }, [markers, selectedPlace]);

  if (!MAPS_KEY) {
    return (
      <div className="map-placeholder card">
        <div className="map-placeholder-content">
          <span className="map-placeholder-icon">🗺️</span>
          <p>Add <code>VITE_GOOGLE_MAPS_KEY</code> to your <code>.env</code> to enable the interactive map.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="map-container card" role="region" aria-label="Trip map">
      <div className="map-header">
        <h3>🗺️ Trip Map</h3>
        <div className="map-legend">
          {itinerary?.days?.map((day, idx) => (
            <span key={idx} className="legend-item">
              <span className="legend-dot" style={{ background: DAY_COLORS[idx % DAY_COLORS.length] }} />
              Day {day.day_number}
            </span>
          ))}
        </div>
      </div>
      <APIProvider apiKey={MAPS_KEY}>
        <Map
          className="map-inner"
          defaultCenter={center}
          defaultZoom={12}
          gestureHandling="greedy"
          mapId="tripflow-map"
        >
          {markers.map((m, idx) => (
            <AdvancedMarker
              key={idx}
              position={{ lat: m.latitude, lng: m.longitude }}
              onClick={() => setActiveMarker(idx)}
            >
              <Pin background={m.color} glyphColor="#fff" borderColor={m.color} />
            </AdvancedMarker>
          ))}
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
