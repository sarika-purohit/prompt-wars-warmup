import { useState } from 'react';
import BudgetTracker from '../components/BudgetTracker';
import AdaptPanel from '../components/AdaptPanel';
import MapView from '../components/MapView';
import ItineraryView from '../components/ItineraryView';

export default function ResultsView({ itinerary, onReset, onAdapt, adapting, adaptationResult }) {
  const [selectedPlace, setSelectedPlace] = useState(null);

  return (
    <div className="results-layout">
      <div className="results-sidebar">
        <button className="btn btn-secondary btn-sm back-btn" onClick={onReset}>
          ← New Trip
        </button>
        <BudgetTracker itinerary={itinerary} />
        <AdaptPanel
          itinerary={itinerary}
          onAdapt={onAdapt}
          adapting={adapting}
          adaptationResult={adaptationResult}
        />
      </div>
      <div className="results-main">
        <MapView itinerary={itinerary} selectedPlace={selectedPlace} />
        <ItineraryView itinerary={itinerary} onSelectPlace={setSelectedPlace} />
      </div>
    </div>
  );
}
