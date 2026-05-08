# TripFlow AI ✈️🌍

> AI-powered travel planner that creates, visualizes, and **adapts** itineraries in real-time.

![Built with](https://img.shields.io/badge/Built%20with-Google%20Cloud-4285F4?logo=googlecloud&logoColor=white)
![AI](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-8E75B2?logo=google&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-React%20+%20Vite-61DAFB?logo=react&logoColor=black)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)

## 🎯 Chosen Vertical

**Travel Planning & Experience Engine**

## 🧠 Approach

TripFlow AI solves the fragmented travel planning experience by combining:

1. **Google Maps Platform** — real place data (ratings, locations, hours)
2. **Gemini 2.0 Flash** — AI that generates structured, budget-aware itineraries
3. **Weather awareness** — adapts plans when conditions change

Unlike static planners, TripFlow creates a **living itinerary** that re-optimizes when it rains, places close, or budgets change.

## ⚙️ How It Works

```
User Input → Google Places API → Gemini AI → Structured Itinerary → Interactive Map
                                                      ↕
                                    Weather/Budget Change → AI Adaptation
```

1. User enters destination, dates, budget, and interests
2. Backend fetches real places from Google Maps matching user preferences
3. Gemini AI generates an optimized day-by-day plan as structured JSON
4. Frontend renders interactive map (color-coded markers) + timeline view
5. Adaptation engine checks weather and re-optimizes on demand

## 🚀 Core Features

| Feature | Description |
|---------|-------------|
| **Smart Itinerary** | AI-generated day-by-day plan with real Google Maps places |
| **Interactive Map** | Color-coded markers per day with info windows |
| **Weather Adaptation** | Detects rain/storms, swaps outdoor → indoor activities |
| **Budget Tracking** | Live cost breakdown with category spending visualization |

## 🏗️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React (Vite) | Fast dev, Google Maps SDK support |
| Backend | Python FastAPI | Async, fast, Gemini SDK native |
| AI | Gemini 2.0 Flash | Fast structured generation, low cost |
| Maps | Google Maps JS API + Places API (New) | Real place data + visualization |
| Database | Cloud Firestore | Serverless, real-time, JSON-native |
| Deployment | Cloud Run | Serverless, scales to zero |

## ☁️ Google Services Used

| Service | Purpose | Value |
|---------|---------|-------|
| **Places API (New)** | Discover attractions & restaurants | Real ratings, hours, locations |
| **Geocoding API** | Address → coordinates | Accurate map centering |
| **Directions API** | Travel time between stops | Realistic scheduling |
| **Maps JS API** | Interactive map visualization | The "wow" factor |
| **Gemini 2.0 Flash** | Itinerary generation & adaptation | AI reasoning at speed |
| **Cloud Firestore** | Persist itineraries | Serverless persistence |
| **Cloud Run** | Host both services | Production-grade, cost-efficient |
| **Cloud Logging** | Structured observability | Production monitoring |

## 📋 Assumptions

- Trip duration: 1–14 days
- Budget: total trip budget (not per-day)
- Weather data: Open-Meteo (free, no key required)
- Place availability based on Google Places hours data
- Gemini 2.0 Flash for optimal speed/cost ratio

## 🛠️ Local Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google Cloud project with APIs enabled
- Gemini API key ([get one here](https://aistudio.google.com/apikey))
- Google Maps API key ([enable here](https://console.cloud.google.com/apis/library))

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # Fill in your API keys
uvicorn main:app --reload
```

Backend runs at `http://localhost:8080`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env           # Fill in API URL + Maps key
npm run dev
```

Frontend runs at `http://localhost:5173`

## 🚢 Deployment (Cloud Run)

### 1. Enable APIs

```bash
gcloud services enable run.googleapis.com firestore.googleapis.com aiplatform.googleapis.com
```

### 2. Deploy Backend

```bash
cd backend
gcloud run deploy tripflow-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=your-key,GOOGLE_MAPS_API_KEY=your-key" \
  --memory 512Mi --cpu 1 \
  --min-instances 0 --max-instances 3
```

### 3. Deploy Frontend

```bash
cd frontend
# Update VITE_API_URL in .env to your Cloud Run backend URL
npm run build
gcloud run deploy tripflow-web \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 256Mi --cpu 1
```

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configuration
│   ├── models/              # Pydantic schemas
│   ├── services/            # Gemini, Maps, Weather, Firestore
│   ├── routers/             # API endpoints
│   ├── tests/               # Unit tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   └── utils/           # API client
│   └── Dockerfile
└── README.md
```

## 🧪 Running Tests

```bash
cd backend
pip install pytest
pytest tests/ -v
```

## 📄 License

MIT

## Phase 2: Production Readiness

We heavily upgraded the MVP for Phase 2, focusing on enterprise-grade architecture and leveraging **Google Cloud Platform (GCP)** and **Google Maps** resources to deliver a premium, high-speed UX.

### Why This Wins
* **Google First:** We deeply integrate Google Maps Platform (Places Autocomplete, Places Data, Geocoding) to validate all user input and LLM output.
* **Performance:** Implemented robust Firestore Caching so repeated queries return instantly, saving LLM tokens and improving perceived speed.
* **Clean Architecture:** Refactored FastAPI to use \Depends()\ dependency injection and added structured logging middleware.
* **Premium UX:** Replaced blocking loaders with elegant Skeleton UIs and split React views for better maintainability.

### Architecture Flow

\\\mermaid
graph TD
    User([User]) --> |Visits UI| React[React/Vite Frontend]
    React --> |Types City| MapsAuto[Google Places Autocomplete]
    React --> |Generates Trip| API[FastAPI Backend]
    
    API --> |1. Check Cache| Firestore[(Firestore DB)]
    API --> |2. Fetch Context| MapsAPI[Google Maps Platform]
    API --> |3. Fetch Weather| Weather[Open-Meteo API]
    API --> |4. Prompt| Gemini[Gemini 2.0 Flash]
    
    Gemini --> |Structured JSON| API
    API --> |Cache Result| Firestore
    API --> |Response| React
\\\`n
