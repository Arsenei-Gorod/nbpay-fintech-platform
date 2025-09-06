# Frontend (React + MUI)

Microservice frontend built with React 18, Vite, React Router and MUI (Material UI).

## Dev

Option A — run locally (recommended):

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API calls are proxied to http://localhost:8000 via Vite.

Option B — with Docker:

```
docker compose up -d frontend
```

This uses `host.docker.internal:8000` as the proxy target on macOS/Windows.

## Env

- `VITE_API_BASE_URL` — default `/api/v1` (hits Vite proxy). Change to full URL if you don’t use the proxy.
- `VITE_API_PROXY_TARGET` — Vite dev proxy backend, default `http://localhost:8000` (or `http://host.docker.internal:8000` in Docker).

## Routes

- `/` — Home
- `/login` — Login (OAuth2 password via form-encoded)
- `/register` — Registration
- `/profile` — Protected profile page (loads `/auth/me`)

## Backend endpoints used

- `POST /api/v1/auth/register` — body `{ email, full_name, password }`
- `POST /api/v1/auth/login` — form-encoded `username`, `password`
- `POST /api/v1/auth/refresh` — query param `refresh_token`
- `GET /api/v1/auth/me` — bearer access token
- `POST /api/v1/auth/logout` — query params `token` and optional `refresh_token`
