# TripFlow AI ✈️🌍

> AI-powered travel planner that creates, visualizes, and **adapts** itineraries in real-time using Google Cloud services.

![Built with](https://img.shields.io/badge/Built%20with-Google%20Cloud-4285F4?logo=googlecloud&logoColor=white)
![AI](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-8E75B2?logo=google&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-React%20+%20Vite-61DAFB?logo=react&logoColor=black)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-pytest%20%2B%20Vitest-brightgreen)

---

## 🎯 Chosen Vertical

**Travel Planning & Experience Engine**

## 🧠 Approach

TripFlow AI solves the fragmented travel planning experience by combining:

1. **Google Maps Platform** — real place data (ratings, locations, hours) via Places API (New)
2. **Gemini 2.0 Flash** — AI that generates structured, budget-aware itineraries
3. **Weather awareness** — adapts plans when conditions change

Unlike static planners, TripFlow creates a **living itinerary** that re-optimizes when it rains, places close, or budgets change.

---

## ⚙️ How It Works

```
User Input → Google Places API → Gemini AI → Structured Itinerary → Interactive Map
                                                      ↕
                                    Weather/Budget Change → AI Adaptation
```

1. User enters destination, dates, budget, and interests
2. Backend fetches real places from **Google Maps Places API (New)** matching user preferences
3. **Gemini 2.0 Flash** generates an optimized day-by-day plan as structured JSON
4. Frontend renders interactive **Google Maps JS API** map (color-coded markers) + timeline view
5. **Adaptation engine** checks weather via Open-Meteo and re-optimizes on demand

---

## 🚀 Core Features

| Feature | Description |
|---------|-------------|
| **Smart Itinerary** | AI-generated day-by-day plan with real Google Maps places |
| **Interactive Map** | Color-coded markers per day with info windows via Google Maps JS API |
| **Weather Adaptation** | Detects rain/storms, swaps outdoor → indoor activities |
| **Budget Tracking** | Live cost breakdown with category spending visualization |
| **Firestore Caching** | Identical requests return instantly without consuming AI tokens |
| **Accessibility** | WCAG-compliant ARIA labels, semantic HTML, keyboard navigation |

---

## 🏗️ Architecture & Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 (Vite) | Fast dev, Google Maps SDK support |
| Backend | Python FastAPI | Async, fast, Gemini SDK native |
| AI | Gemini 2.0 Flash | Fast structured generation, low cost |
| Maps | Google Maps JS API + Places API (New) | Real place data + visualization |
| Database | Cloud Firestore | Serverless, real-time, JSON-native |
| Deployment | Cloud Run | Serverless, scales to zero |

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         React Frontend (Vite)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ TripForm │  │ MapView  │  │ Budget   │  │ ItineraryTimeline  │  │
│  │ (Input)  │  │ (GMap)   │  │ Tracker  │  │ (Day-by-day view)  │  │
│  └────┬─────┘  └──────────┘  └──────────┘  └────────────────────┘  │
│       │                                                             │
└───────┼─────────────────────────────────────────────────────────────┘
        │ HTTP/JSON (axios)
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Python)                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Middleware: SecurityHeaders + TimingMiddleware + CORS        │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐    │
│  │ /api/itinerary │  │ /api/places    │  │ /api/adapt         │    │
│  │  POST /generate│  │  GET /search   │  │  POST /            │    │
│  │  GET /:id      │  │  GET /geocode  │  │  GET /weather      │    │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────────┘    │
│          │                   │                   │                  │
│  ┌───────▼───────────────────▼───────────────────▼──────────────┐  │
│  │                    Service Layer                              │  │
│  │  GeminiService │ MapsService │ WeatherService │ FirestoreDB  │  │
│  └──────┬──────────────┬──────────────┬──────────────┬──────────┘  │
└─────────┼──────────────┼──────────────┼──────────────┼─────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
   Google Gemini   Google Maps    Open-Meteo     Cloud Firestore
   2.0 Flash       Platform       Weather API    (Persistence)
```

---

## ☁️ Google Services Used

| # | Service | Purpose | How We Use It |
|---|---------|---------|---------------|
| 1 | **Places API (New)** | Discover attractions & restaurants | Text Search with field masks for ratings, locations, photos, hours |
| 2 | **Geocoding API** | Address → coordinates | Map centering and location bias for place searches |
| 3 | **Directions API** | Travel time between stops | Realistic scheduling with driving/walking times |
| 4 | **Maps JavaScript API** | Interactive map visualization | Color-coded markers per day, InfoWindows, AdvancedMarkers |
| 5 | **Places Autocomplete** | City search in the frontend | Validates destination input with real city data |
| 6 | **Gemini 2.0 Flash** | AI itinerary generation & adaptation | Structured JSON output with budget constraints |
| 7 | **Cloud Firestore** | Persist & cache itineraries | Two-collection caching (itineraries + itinerary_cache) |
| 8 | **Cloud Run** | Production hosting | Serverless containers for both frontend and backend |
| 9 | **Cloud Logging** | Structured observability | TimingMiddleware logs request durations |

---

## 📋 Evaluation Criteria Checklist

### ✅ Code Quality
- **Clean architecture**: Layered design with `api/` (routers) → `services/` (business logic) → external APIs
- **PEP 257 docstrings**: Every Python module, class, and function has comprehensive docstrings
- **JSDoc comments**: All React components are documented with JSDoc
- **Type hints**: Full Python type annotations on all function signatures
- **Immutable config**: Frozen `@dataclass` with `lru_cache` singleton pattern
- **Dependency injection**: FastAPI `Depends()` for testable, decoupled services
- **No dead code**: Clean separation of concerns with no unused imports

### ✅ Security
- **Secret management**: API keys loaded exclusively from `.env` / environment variables (never hardcoded)
- **`.gitignore`** excludes `.env`, `__pycache__`, `node_modules`, `venv/`
- **Security headers middleware**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Referrer-Policy`, `Permissions-Policy`
- **Global error handler**: Catches all unhandled exceptions — never exposes stack traces to clients
- **Input validation**: Pydantic models with `max_length`, `gt=0`, `ge=1`, `le=20` constraints prevent payload attacks
- **CORS whitelist**: Only known frontend origins are allowed

### ✅ Efficiency
- **Firestore caching**: MD5-hashed request keys enable O(1) cache lookups, avoiding redundant Gemini API calls
- **Async I/O**: All HTTP calls (Maps, Gemini, Weather) use `httpx.AsyncClient` for non-blocking concurrency
- **Lazy initialization**: Gemini client is created on first use, not at startup
- **Connection pooling**: `httpx.AsyncClient` reuses TCP connections across requests
- **`lru_cache` settings**: Configuration object created once, never re-read
- **TimingMiddleware**: Logs request durations for performance monitoring
- **`X-Process-Time` header**: Clients can observe latency per-request

### ✅ Testing
- **pytest test suite** with 20+ test cases covering:
  - Model validation (TripRequest, Interest, budget constraints, group size)
  - Gemini JSON parser (direct, code-block, wrapped, invalid input)
  - Weather code translation
  - API endpoint validation (missing fields, invalid values)
  - Security headers presence
  - Configuration loading and immutability
  - Health check endpoints
- **Shared fixtures** in `conftest.py` for DRY test data
- Run: `cd backend && pytest tests/ -v`

### ✅ Accessibility
- **Semantic HTML**: `<main>`, `<header>`, `<section>`, `<article>`, `<nav>` elements
- **ARIA attributes**: `aria-label`, `aria-pressed`, `aria-expanded`, `aria-busy`, `aria-live`, `role="alert"`, `role="region"`, `role="banner"`, `role="status"`, `role="progressbar"`, `role="button"`, `role="group"`
- **Keyboard navigation**: `tabIndex`, `onKeyDown` handlers for interactive timeline items
- **Form labels**: All `<input>` elements have associated `<label>` with `htmlFor`
- **Color contrast**: WCAG AA compliant color palette (dark theme with high-contrast text)
- **Loading states**: Skeleton loaders with `role="status"` and `aria-label="Loading itinerary"`
- **Error announcements**: Error banners use `role="alert"` for screen reader announcement

### ✅ Google Services
- Deep integration with **9 Google services** (see table above)
- Google Maps Places Autocomplete for validated city input
- Real place data (ratings, coordinates, hours) grounds Gemini's AI output
- Firestore provides serverless persistence and intelligent caching
- Cloud Run deployment with health check endpoints for liveness probes

---

## 📁 Project Structure

```
prompt-wars-warmup/
├── backend/
│   ├── main.py                  # FastAPI entry point with middleware stack
│   ├── core/
│   │   └── config.py            # Immutable Settings dataclass (env vars)
│   ├── api/
│   │   ├── dependencies.py      # Dependency injection providers
│   │   ├── itinerary.py         # POST /generate, GET /:id endpoints
│   │   ├── places.py            # GET /search, GET /geocode endpoints
│   │   └── adapt.py             # POST /adapt, GET /weather endpoints
│   ├── services/
│   │   ├── gemini_service.py    # Google Gemini 2.0 Flash integration
│   │   ├── maps_service.py      # Google Maps Platform integration
│   │   ├── weather_service.py   # Open-Meteo weather forecasts
│   │   └── firestore_service.py # Cloud Firestore persistence + caching
│   ├── models/
│   │   └── user_input.py        # Pydantic request/response schemas
│   ├── middleware/
│   │   ├── logging.py           # TimingMiddleware (performance monitoring)
│   │   └── security.py          # SecurityHeadersMiddleware (OWASP headers)
│   ├── tests/
│   │   ├── conftest.py          # Shared test fixtures
│   │   ├── test_api.py          # API integration tests
│   │   ├── test_config.py       # Configuration tests
│   │   ├── test_gemini.py       # Gemini JSON parser tests
│   │   ├── test_models.py       # Pydantic model validation tests
│   │   └── test_weather.py      # Weather code translation tests
│   ├── Dockerfile               # Cloud Run container
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main application shell
│   │   ├── main.jsx             # React entry point
│   │   ├── components/
│   │   │   ├── TripForm.jsx     # Trip planning form (accessible)
│   │   │   ├── Header.jsx       # App brand bar
│   │   │   ├── ItineraryView.jsx# Day-by-day timeline
│   │   │   ├── MapView.jsx      # Google Maps integration
│   │   │   ├── BudgetTracker.jsx# Budget visualization
│   │   │   ├── AdaptPanel.jsx   # Weather adaptation controls
│   │   │   ├── SkeletonLoader.jsx# Loading state UI
│   │   │   └── PlaceAutocomplete.jsx # Google Places Autocomplete
│   │   ├── hooks/
│   │   │   └── useItinerary.js  # Custom hook for state management
│   │   ├── utils/
│   │   │   └── api.js           # Axios API client
│   │   └── views/
│   │       ├── PlanningView.jsx # Trip planning page
│   │       └── ResultsView.jsx  # Results display page
│   ├── index.html               # HTML entry with SEO meta tags
│   ├── Dockerfile               # Cloud Run container
│   └── package.json             # Node.js dependencies
├── .gitignore                   # Excludes .env, venv, node_modules
└── README.md                    # This file
```

---

## 🛠️ Local Setup

### Prerequisites

- Node.js 18+
- Python 3.9+
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
uvicorn main:app --reload --port 8080
```

Backend runs at `http://localhost:8080` — API docs at `http://localhost:8080/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env           # Fill in API URL + Maps key
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## 🧪 Running Tests

```bash
cd backend
pip install pytest
pytest tests/ -v
```

Expected output: **20+ tests passing** covering models, services, API endpoints, security headers, and configuration.

---

## 🚢 Deployment (Cloud Run)

### 1. Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  places-backend.googleapis.com \
  geocoding-backend.googleapis.com \
  directions-backend.googleapis.com
```

### 2. Deploy Backend

```bash
cd backend
gcloud run deploy tripflow-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=<key>,GOOGLE_MAPS_API_KEY=<key>" \
  --memory 512Mi --cpu 1 \
  --min-instances 0 --max-instances 3
```

### 3. Deploy Frontend

```bash
cd frontend
npm run build
gcloud run deploy tripflow-web \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 256Mi --cpu 1
```

---

## 📋 Assumptions

- Trip duration: 1–14 days (validated server-side)
- Budget: total trip budget, not per-day
- Weather data: Open-Meteo (free, no key required)
- Place availability based on Google Places hours data
- Gemini 2.0 Flash for optimal speed/cost ratio

## 📄 License

MIT
