# Backend API (FastAPI)

This directory hosts the RESTful API for the Wearable Health-Monitoring ARM System.

## Architecture
The API acts as a thin presentation layer on top of the standalone simulation core (`sim/`). It exposes endpoints for configuring parameters, running full-pipeline simulations, querying baseline defaults and validation boundaries, and executing automated verification suites.

## Endpoints
- `GET /api/health`: Health status.
- `GET /api/defaults`: Default parameters, validation bounds, and placeholder status.
- `GET /api/records`: Verified PhysioNet records and synthetic generator.
- `POST /api/run`: Main simulation endpoint. Validates payload and returns full COA subsystem outputs.
- `GET /api/verification`: Automated verification suite results.

## Running the API Server
Start the Uvicorn development server on port 8000:
```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger documentation is available at: [http://localhost:8000/docs](http://localhost:8000/docs).
