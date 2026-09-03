"""
Resort OS — main.py
FastAPI backend serving all 6 API endpoints + static frontend files.
Cross-module intelligence: PEMS risk → room blocking → allocation exclusion → revenue adjustment.
"""
import sqlite3
import os
import random
import math
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

# ── App Setup ───────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "resort.db")

app = FastAPI(title="Resort OS", version="2.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database Helper ─────────────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ── Models ──────────────────────────────────────────────────────────────
class ConciergeRequest(BaseModel):
    room_id: int
    request_text: str


# ── Concierge AI Logic ──────────────────────────────────────────────────
# Try Gemini if API key is available, fall back to keyword mock
_gemini_model = None

def _try_init_gemini():
    """Attempt to initialize Gemini client. Returns model or None."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        return _gemini_model
    except Exception:
        return None


def _keyword_mock_concierge(request_text: str, room_id: int) -> dict:
    """Keyword-matching mock for concierge recommendations."""
    text = request_text.lower()

    if any(w in text for w in ["dinner", "restaurant", "eat", "food", "dining", "italian", "seafood", "lunch"]):
        return {
            "recommendation": "We recommend Mare Nostrum Ristorante at 7:30 PM — the garden patio offers a quiet, intimate setting with dedicated sommelier service. The 7:00 PM slot has 88 dinner covers already booked, so 7:30 PM provides optimal table turnover and a more relaxed experience.",
            "reason": "Based on current kitchen load (88/120 covers at 7 PM peak), shifting to 7:30 PM avoids wait times. Mare Nostrum specializes in Italian-seafood fusion — aligns with guest preference. Garden patio has 4 available two-tops."
        }
    elif any(w in text for w in ["spa", "massage", "wellness", "treatment", "relax", "sauna", "facial"]):
        return {
            "recommendation": "We recommend the 4:30 PM couples deep tissue massage at the Lagoon Cabana Suite — our spa roster is fully staffed (8/8 therapists active) and the cabana offers complete acoustic privacy with natural lagoon views before the evening lighting transition.",
            "reason": "Spa capacity at 100% staffing. 4:30 PM slot available at premium Lagoon Cabana (Suite #3). Couples deep tissue is 90 min — finishes at 6:00 PM, ideal timing for sunset cocktails."
        }
    elif any(w in text for w in ["pool", "swim", "activity", "tennis", "golf", "yoga", "gym"]):
        return {
            "recommendation": "The infinity pool is available with reserved cabana service. We also have a guided sunset yoga session at 5:30 PM on the Ocean Terrace, and the tennis courts have a 4:00 PM slot open with our resident pro available for a private lesson.",
            "reason": "Current pool occupancy: 34%. Sunset yoga has 6/15 spots remaining. Tennis court 2 is open from 4:00-5:30 PM."
        }
    elif any(w in text for w in ["checkout", "late", "extend", "stay", "departure"]):
        return {
            "recommendation": f"We can offer a complimentary late checkout until 12:30 PM for Room {room_id}. Please note the standard checkout is 11:00 AM, and extending to 1:00 PM may conflict with incoming arrivals scheduled for 2:00 PM.",
            "reason": f"Room {room_id} has a 2:00 PM incoming arrival. 12:30 PM departure allows 90 min housekeeping turnover (avg 45 min for this room type), providing safe buffer."
        }
    elif any(w in text for w in ["transfer", "airport", "car", "taxi", "transport", "shuttle"]):
        return {
            "recommendation": f"Private luxury hybrid shuttle confirmed for departure from Room {room_id}. Pickup at lobby entrance with bellhop assistance 15 minutes before departure. Our concierge will coordinate luggage handling.",
            "reason": "Shuttle fleet: 3/5 vehicles available. Route to airport: 42 min (current traffic). Bellhop dispatch coordinated with front desk."
        }
    else:
        return {
            "recommendation": f"Thank you for your request. Our concierge team has reviewed your inquiry for Room {room_id} and will arrange the best available option. A detailed confirmation will be sent to your room shortly.",
            "reason": "Request categorized as general inquiry. Routed to duty concierge for personalized follow-up."
        }


async def generate_concierge_response(request_text: str, room_id: int) -> dict:
    """Try Gemini first, fall back to keyword mock."""
    model = _try_init_gemini()
    if model is not None:
        try:
            prompt = f"""You are an AI concierge at a luxury resort. A guest in Room {room_id} has made this request:

"{request_text}"

Respond as a helpful, warm, and knowledgeable resort concierge. Consider:
- Current resort context: 94% occupancy, dinner service has 88/120 covers booked at 7 PM peak, spa is fully staffed (8/8 therapists), pool at 34% capacity
- Be specific with times, locations, and options
- Mention operational context naturally (e.g., "the 7:30 slot offers a quieter atmosphere")

Respond with ONLY a JSON object (no markdown, no code fences) with exactly two keys:
- "recommendation": Your recommendation to the guest (2-3 sentences, warm and specific)
- "reason": Internal operational reasoning for staff (1-2 sentences, factual)"""

            response = model.generate_content(prompt)
            import json
            text = response.text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            return json.loads(text)
        except Exception:
            pass  # Fall through to keyword mock

    return _keyword_mock_concierge(request_text, room_id)


# ── API Endpoints ───────────────────────────────────────────────────────

@app.get("/api/rooms")
def list_rooms():
    """GET /rooms — array of all rooms with status and flagged-asset boolean."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT room_id, floor, wing, room_type, status, has_flagged_asset FROM rooms ORDER BY room_id"
        ).fetchall()
        return [dict(r) for r in rows]


@app.get("/api/rooms/{room_id}")
def get_room(room_id: int):
    """GET /rooms/{id} — single room with assets and exclusion flag."""
    with get_db() as conn:
        room = conn.execute(
            "SELECT room_id, floor, wing, room_type, status, has_flagged_asset FROM rooms WHERE room_id=?",
            (room_id,)
        ).fetchone()
        if not room:
            raise HTTPException(404, f"Room {room_id} not found")

        assets = conn.execute(
            "SELECT asset_type as asset, risk_percent, status, reason FROM assets WHERE room_id=? ORDER BY asset_type",
            (room_id,)
        ).fetchall()

        result = dict(room)
        result["assets"] = [dict(a) for a in assets]
        result["excluded_from_allocation"] = room["status"] == "Blocked"
        return result


@app.get("/api/staff")
def get_staff():
    """GET /staff — occupancy-driven staffing recommendations per department."""
    with get_db() as conn:
        total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        occupied = conn.execute(
            "SELECT COUNT(*) FROM rooms WHERE status='Occupied'"
        ).fetchone()[0]

        occupancy_pct = round((occupied / total_rooms) * 100, 1) if total_rooms > 0 else 0

        departments = conn.execute(
            "SELECT department as name, current_staff, recommended_staff FROM staff ORDER BY department"
        ).fetchall()

        dept_list = []
        for d in departments:
            dd = dict(d)
            dd["gap"] = dd["current_staff"] - dd["recommended_staff"]
            dept_list.append(dd)

        return {
            "date": "2025-10-24",
            "occupancy_percent": occupancy_pct,
            "departments": dept_list
        }


@app.post("/api/concierge")
async def concierge(req: ConciergeRequest):
    """POST /concierge — AI concierge recommendation."""
    result = await generate_concierge_response(req.request_text, req.room_id)

    # Save to guest_requests table
    with get_db() as conn:
        # Try to find a guest name from reservations
        guest = conn.execute(
            "SELECT guest_name FROM reservations WHERE room_id=? LIMIT 1",
            (req.room_id,)
        ).fetchone()
        guest_name = guest["guest_name"] if guest else f"Guest (Room {req.room_id})"

        conn.execute(
            "INSERT INTO guest_requests (room_id, guest_name, request_text, recommendation, status) VALUES (?,?,?,?,?)",
            (req.room_id, guest_name, req.request_text, result["recommendation"], "Pending")
        )
        conn.commit()

    return result


@app.get("/api/guest-requests")
def get_guest_requests():
    """GET /guest-requests — feed of all guest requests with recommendations."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT room_id, guest_name, request_text, recommendation, status FROM guest_requests ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


@app.get("/api/revenue")
def get_revenue():
    """GET /revenue — rule-based pricing recommendations per room type.
    Logic: occupancy % + blocked rooms → suggested % adjustment.
    """
    with get_db() as conn:
        total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        occupied = conn.execute(
            "SELECT COUNT(*) FROM rooms WHERE status='Occupied'"
        ).fetchone()[0]
        blocked = conn.execute(
            "SELECT COUNT(*) FROM rooms WHERE status='Blocked'"
        ).fetchone()[0]

        occupancy_pct = round((occupied / total_rooms) * 100, 1) if total_rooms > 0 else 0

        # Per room-type breakdown
        room_types = conn.execute("""
            SELECT
                room_type,
                COUNT(*) as total,
                SUM(CASE WHEN status='Occupied' THEN 1 ELSE 0 END) as occupied,
                SUM(CASE WHEN status='Blocked' THEN 1 ELSE 0 END) as blocked,
                SUM(CASE WHEN status='Ready' THEN 1 ELSE 0 END) as available
            FROM rooms GROUP BY room_type ORDER BY room_type
        """).fetchall()

        # Base rates per room type
        base_rates = {
            "Standard": 210,
            "Deluxe": 275,
            "Deluxe AC": 320,
            "Suite": 480,
            "Penthouse": 850,
        }

        type_breakdown = []
        for rt in room_types:
            rt = dict(rt)
            base_rate = base_rates.get(rt["room_type"], 250)
            type_occupancy = round((rt["occupied"] / rt["total"]) * 100, 1) if rt["total"] > 0 else 0

            # Rule-based adjustment:
            # Base: if occupancy > 90%, suggest +5%. If > 95%, +12%.
            # Blocked penalty: each blocked room in this type adds +2% (scarcity)
            adj = 0
            if type_occupancy >= 95:
                adj = 12
            elif type_occupancy >= 90:
                adj = 5
            elif type_occupancy >= 80:
                adj = 2

            # Scarcity boost from blocked rooms
            adj += rt["blocked"] * 2

            suggested_rate = round(base_rate * (1 + adj / 100))

            reasoning = ""
            if adj > 0 and rt["blocked"] > 0:
                reasoning = f"{type_occupancy}% occupancy with {rt['blocked']} room(s) blocked — reduced available inventory drives scarcity pricing."
            elif adj > 0:
                reasoning = f"{type_occupancy}% occupancy exceeds demand threshold — suggested rate increase to optimize yield."
            else:
                reasoning = f"{type_occupancy}% occupancy within normal range — baseline pricing maintained."

            type_breakdown.append({
                "room_type": rt["room_type"],
                "total_rooms": rt["total"],
                "occupied": rt["occupied"],
                "blocked": rt["blocked"],
                "available": rt["available"],
                "occupancy_percent": type_occupancy,
                "base_rate": base_rate,
                "suggested_rate": suggested_rate,
                "suggested_adjustment_percent": adj,
                "reasoning": reasoning
            })

        # Find the type with highest adjustment for the hero card
        hero = max(type_breakdown, key=lambda x: x["suggested_adjustment_percent"])

        return {
            "occupancy_percent": occupancy_pct,
            "blocked_rooms": blocked,
            "hero": {
                "room_type": hero["room_type"],
                "suggested_adjustment_percent": hero["suggested_adjustment_percent"],
                "base_rate": hero["base_rate"],
                "suggested_rate": hero["suggested_rate"],
                "reasoning": hero["reasoning"],
            },
            "room_types": type_breakdown
        }


@app.get("/api/dashboard")
def get_dashboard():
    """GET /dashboard — aggregated overview stats for the main dashboard."""
    with get_db() as conn:
        total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        occupied = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Occupied'").fetchone()[0]
        blocked = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Blocked'").fetchone()[0]
        dirty = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Dirty'").fetchone()[0]
        ready = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Ready'").fetchone()[0]
        arrival = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Arrival'").fetchone()[0]

        occupancy_pct = round((occupied / total_rooms) * 100, 1) if total_rooms > 0 else 0

        # Staff summary
        staff = conn.execute(
            "SELECT SUM(current_staff) as current, SUM(recommended_staff) as recommended FROM staff"
        ).fetchone()

        # Revenue signal (pick hero adjustment)
        # Quick calc — same logic as revenue endpoint but just the max
        room_types = conn.execute("""
            SELECT room_type,
                COUNT(*) as total,
                SUM(CASE WHEN status='Occupied' THEN 1 ELSE 0 END) as occ,
                SUM(CASE WHEN status='Blocked' THEN 1 ELSE 0 END) as blk
            FROM rooms GROUP BY room_type
        """).fetchall()

        max_adj = 0
        for rt in room_types:
            pct = round((rt["occ"] / rt["total"]) * 100) if rt["total"] > 0 else 0
            adj = 0
            if pct >= 95:
                adj = 12
            elif pct >= 90:
                adj = 5
            elif pct >= 80:
                adj = 2
            adj += rt["blk"] * 2
            max_adj = max(max_adj, adj)

        return {
            "total_rooms": total_rooms,
            "occupancy_percent": occupancy_pct,
            "occupied": occupied,
            "ready": ready,
            "dirty": dirty,
            "blocked": blocked,
            "arrival": arrival,
            "rooms_needing_attention": blocked + dirty,
            "staff_current": staff["current"],
            "staff_recommended": staff["recommended"],
            "revenue_signal_percent": max_adj,
        }


# ── Static File Serving ────────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

# Serve guest page
@app.get("/guest")
@app.get("/guest/")
def guest_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "guest", "index.html"))

# Serve login page
@app.get("/login")
@app.get("/login/")
def login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "staff", "login.html"))

# Root → redirect to login
@app.get("/")
def root():
    return RedirectResponse("/login")

# Serve staff dashboard
@app.get("/dashboard")
@app.get("/dashboard/")
def dashboard_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "staff", "index.html"))

# Mount static files for any other frontend assets
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
