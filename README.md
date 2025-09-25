# Fleet Management Software (FMS) — Full MVP
Run a complete fleet stack locally with Docker (FastAPI + Postgres + Redis + Next.js).

## Quick Start
1) Unzip, then copy `.env.example` to `.env`.
2) Run: `docker compose up --build`
3) Open API docs at http://localhost:8000/docs and Web at http://localhost:3000
4) On **Vehicles** page, use the signup/login controls, add a vehicle, click it to open details.

## Modules
- Auth & basic RBAC
- Vehicles, Drivers, Assignments
- Meter Readings (odometer/hours)
- Maintenance Schedules → PM alerts (trigger via `/internal/run-nightly`)
- Work Orders (+ tasks)
- Inspections & Defects (auto WO on failure)
- Fuel Logs
- Alerts inbox
- Alembic migrations + Postman collection
