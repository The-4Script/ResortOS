# Resort OS — Smart Resort 360

> AI-powered resort operations dashboard — hackathon MVP (PS4: Smart Resort 360)

An internal operations control tool for resort/hotel managers and staff. It connects room operations, predictive equipment maintenance, staff scheduling, AI guest concierge, and revenue/pricing into one unified dashboard with **connected intelligence** — modules affect each other, not siloed dashboards.

---

## What's Built (Day 1)

### Backend — FastAPI + SQLite
- [x] `backend/main.py` — FastAPI app with **6 API endpoints**:
  - `GET /api/rooms` — all 120 rooms with status + flagged-asset boolean
  - `GET /api/rooms/{id}` — single room detail with assets array + exclusion flag
  - `GET /api/staff` — occupancy-driven staffing recommendations per department
  - `POST /api/concierge` — AI concierge (keyword mock + optional Gemini fallback)
  - `GET /api/guest-requests` — feed of all guest requests with AI recommendations
  - `GET /api/revenue` — rule-based pricing recommendations per room type
  - `GET /api/dashboard` — aggregated overview stats
- [x] `backend/seed.py` — seeds database with realistic mock data:
  - 120 rooms across 4 floors (Standard / Deluxe / Deluxe AC / Suite / Penthouse)
  - 360 assets (AC, TV, Set-top box per room) with risk scores
  - 3 rooms with critical AC risk (204: 87%, 317: 73%, 412: 91%) → auto-blocked
  - 5 staff departments with current vs recommended headcount
  - 4 guest requests with pre-composed AI recommendations
- [x] `backend/resort.db` — seeded SQLite database
- [x] CORS enabled for frontend development
- [x] Static file serving for frontend pages

### Staff Dashboard — Unified SPA
- [x] `frontend/staff/index.html` — single-page app with **5 pages** and hash-based routing:
  - **Dashboard** (`#dashboard`) — stat cards (occupancy, rooms needing attention, staff status, revenue signal), recent activity feed, donut chart
  - **Room Ops** (`#roomops`) — 120-room grid organized by floor, color-coded status dots, clickable room cells → detail drawer
  - **Staff** (`#staff`) — occupancy benchmark banner, 5 department cards with progress bars, gap indicators, reassign/backup buttons
  - **Guests** (`#guests`) — AI concierge request cards, filter tabs (All/Pending/Sent), search, "Send to guest" button
  - **Revenue** (`#revenue`) — dynamic rate optimization hero card, yield pulse sidebar, room type breakdown table
- [x] Working sidebar navigation with active state highlighting
- [x] Room detail drawer with asset health telemetry (risk %, mini donut charts, explainable reasons)

### All Interactive Buttons Working
- [x] **Send to guest** — frontend-only no-op: flips card status badge to "Sent", swaps action row (no backend call)
- [x] **Apply adjustment** — animates "Broadcasting..." → "Applied to PMS" with color change
- [x] **Dismiss** — dims hero card, shows "Dismissed for 4h"
- [x] **Auto-adjust shifts** — animates "Balancing shifts..." → "Shifts Optimized"
- [x] **Export roster** — animates "Generating..." → "Downloaded"
- [x] **Mark resolved** — updates room status to Ready, removes fault flag, refreshes grid
- [x] **Assign technician** — shows toast notification
- [x] **Filter tabs** — All Requests / Pending Review / Sent (with empty state)
- [x] **Guest search** — real-time text filtering across all request cards
- [x] **Room cell click** — opens detail drawer with full asset telemetry
- [x] **Drawer close** — backdrop click or X button

### Sign-In Page
- [x] `frontend/staff/login.html` — cosmetic-only auth page
- [x] Pre-filled credentials (Alex Morgan, General Manager)
- [x] Password toggle visibility
- [x] Animated "Authenticating..." → redirects to dashboard
- [x] Workstation node & shift assignment metadata

### Guest-Facing Concierge Page
- [x] `frontend/guest/index.html` — standalone chat UI (no sidebar, guest-friendly)
- [x] Room number from URL param (`?room=203`)
- [x] Chat-style interface with typing animation (bouncing dots)
- [x] Quick-request chips (Dinner, Spa, Late checkout, Airport transfer, Pool)
- [x] Keyword-matched AI responses with operational context
- [x] Message slide-up animations

### Cross-Module Intelligence Chain
- [x] PEMS risk ≥ 70% → room auto-blocked → `has_flagged_asset = true`
- [x] Blocked rooms → excluded from allocation → `excluded_from_allocation = true`
- [x] Blocked rooms counted in Revenue → scarcity pricing (+2% per blocked room in type)
- [x] Revenue hero card shows "3 Deluxe AC rooms blocked — reduced available inventory"
- [x] Dashboard reflects blocked count in "Rooms needing attention"

### Design System
- [x] Google Stitch design tokens preserved (colors, typography, spacing, elevation)
- [x] Inter font for UI text, IBM Plex Mono for data/numbers
- [x] Tailwind CSS with full custom config
- [x] Material Symbols Outlined icons
- [x] Consistent status colors: Green (#3FAE6A), Blue (#3B7DD8), Amber (#E0A93A), Red (#DD5A5A), Orange (#E08A3A)
- [x] Toast notifications for all actions

---

## What's Remaining (Day 2)

### Must Do
- [ ] **Fix occupancy numbers** — JS mock shows ~38%, needs to match design spec (94%)
- [ ] **Wire frontend → backend API** — swap baked-in mock data with `fetch('/api/...')` calls
- [ ] **PEMS ML model integration** — existing Scikit-Learn model needs param adaptation (machine → AC/TV/set-top box), replace seeded risk scores with live predictions
- [ ] **Visual QA pass** — verify all 5 pages render correctly, responsive breakpoints

### Nice to Have
- [ ] Gemini API for live concierge responses (if API key available with zero friction)
- [ ] Guest concierge page connected to backend `POST /api/concierge`
- [ ] Demo walkthrough script / recording

---

## Project Structure

```
resortos/
├── backend/
│   ├── main.py              # FastAPI app — all endpoints + static serving
│   ├── seed.py              # Database seeding (120 rooms, 360 assets)
│   ├── requirements.txt     # fastapi, uvicorn
│   └── resort.db            # SQLite database (generated)
├── frontend/
│   ├── staff/
│   │   ├── login.html       # Sign-in page (cosmetic auth)
│   │   └── index.html       # Main staff dashboard SPA (5 pages)
│   └── guest/
│       └── index.html       # Guest-facing concierge chat
└── stitch_resort_os_operations_dashboard/
    └── (original Stitch-generated UI files — preserved as reference)
```

## Quick Start

```bash
cd backend
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Then open:
- **Staff Dashboard**: http://localhost:8000/login
- **Guest Concierge**: http://localhost:8000/guest?room=203
- **API Docs**: http://localhost:8000/docs

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python, FastAPI, SQLite |
| Frontend | HTML, Tailwind CSS, Vanilla JS |
| Design System | Google Stitch |
| Fonts | Inter, IBM Plex Mono |
| Icons | Material Symbols Outlined |
| AI (planned) | Gemini API (optional), keyword-mock fallback |
| ML (Day 2) | Scikit-Learn PEMS model (param-adapted) |

---

**Team: The 4Script** | Hackathon PS4: Smart Resort 360
