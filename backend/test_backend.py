import asyncio
import traceback
from dotenv import load_dotenv
load_dotenv()
from core.config import get_settings
from services.gemini_service import GeminiService
from services.maps_service import MapsService
from models.user_input import TripRequest

async def main():
    settings = get_settings()
    maps = MapsService(settings)
    gemini = GeminiService(settings)
    
    req = TripRequest(
        destination="Kyoto, Japan",
        start_date="2026-06-01",
        end_date="2026-06-05",
        budget=2000.0,
        group_size=2,
        currency="USD",
        interests=["culture"]
    )
    
    places_data = []
    print("Testing Maps...")
    try:
        places_data = await maps.search_places("top attractions in Kyoto", max_results=2)
        print("Maps OK:", len(places_data))
    except Exception as e:
        print("Maps Error:", repr(e))
        traceback.print_exc()
        
    print("Testing Gemini...")
    try:
        itin = await gemini.generate_itinerary(req, places_data)
        print("Gemini OK")
    except Exception as e:
        print("Gemini Error:", repr(e))
        traceback.print_exc()

asyncio.run(main())
