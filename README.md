# Backend-for-RouteX

Backend for Intelligent Route Planning and Adaptive Optimization System (RouteX).

This repository contains the Member 2 backend work for RouteX/PathMatrix. It provides FastAPI endpoints that the frontend and optimization modules can call later.

## Current Status

* FastAPI backend structure is ready.
* Sightseeing route optimization API is available with placeholder logic.
* Ride-sharing insertion heuristic is implemented separately and tested.
* Distance matrix input is supported, with coordinate-based Euclidean distance as fallback.
* Current route state is stored in memory for development and demo use.

## Endpoints

```text
GET  /health
POST /optimize-route
POST /ride-request
GET  /current-route
POST /reset-route
```

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Run Tests

```bash
python -m unittest discover -s tests
```

## API Response Examples

### POST `/optimize-route`

```json
{
  "route": \\\[
    { "id": "College", "lat": 15.4589, "lng": 75.0078 },
    { "id": "Museum", "lat": 15.46, "lng": 75.01 },
    { "id": "Beach", "lat": 15.5, "lng": 75.08 }
  ],
  "total\\\_distance": 42.5,
  "total\\\_effective\\\_satisfaction": 18.72,
  "selected\\\_location\\\_ids": \\\["Museum"],
  "algorithm": "placeholder\\\_greedy\\\_by\\\_score",
  "message": "Backend contract is ready. Replace this placeholder with the final optimization algorithm."
}
```

### POST `/ride-request`

```json
{
  "accepted": true,
  "reason": "Request inserted using least-cost feasible insertion.",
  "route": \\\[
    {
      "location": { "id": "S", "lat": 0, "lng": 0 },
      "stop\\\_type": "start",
      "request\\\_id": null,
      "passenger\\\_delta": 0
    },
    {
      "location": { "id": "A", "lat": 0, "lng": 4 },
      "stop\\\_type": "pickup",
      "request\\\_id": "req-1",
      "passenger\\\_delta": 1
    },
    {
      "location": { "id": "C", "lat": 0, "lng": 6 },
      "stop\\\_type": "pickup",
      "request\\\_id": "req-2",
      "passenger\\\_delta": 1
    },
    {
      "location": { "id": "B", "lat": 0, "lng": 8 },
      "stop\\\_type": "drop",
      "request\\\_id": "req-1",
      "passenger\\\_delta": -1
    },
    {
      "location": { "id": "D", "lat": 0, "lng": 10 },
      "stop\\\_type": "drop",
      "request\\\_id": "req-2",
      "passenger\\\_delta": -1
    }
  ],
  "total\\\_distance": 13,
  "added\\\_distance": 4,
  "passenger\\\_trace": \\\[
    { "stop\\\_id": "S", "active\\\_passengers": 0 },
    { "stop\\\_id": "A", "active\\\_passengers": 1 },
    { "stop\\\_id": "C", "active\\\_passengers": 2 },
    { "stop\\\_id": "B", "active\\\_passengers": 1 },
    { "stop\\\_id": "D", "active\\\_passengers": 0 }
  ]
}
```

## Main Files

```text
app/main.py        FastAPI routes
app/models.py      Request and response schemas
app/distance.py    Distance matrix and coordinate distance helpers
app/optimizer.py   Placeholder sightseeing optimizer
app/rideshare.py   Ride-sharing insertion engine
app/state.py       Temporary in-memory route state
tests/             Unit tests
```

