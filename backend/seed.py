"""
Resort OS — seed.py
Seeds the SQLite database with 120 rooms, assets, staff, and guest requests.
Run once: python seed.py
"""
import sqlite3, os, random

DB_PATH = os.path.join(os.path.dirname(__file__), "resort.db")

def seed():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ── Tables ──────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE rooms (
            room_id   INTEGER PRIMARY KEY,
            floor     INTEGER NOT NULL,
            wing      TEXT NOT NULL,
            room_type TEXT NOT NULL,
            status    TEXT NOT NULL DEFAULT 'Ready',
            has_flagged_asset INTEGER NOT NULL DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE assets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id     INTEGER NOT NULL,
            asset_type  TEXT NOT NULL,
            risk_percent INTEGER NOT NULL DEFAULT 0,
            status      TEXT NOT NULL DEFAULT 'Operational',
            reason      TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    """)

    c.execute("""
        CREATE TABLE staff (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            department       TEXT NOT NULL,
            current_staff    INTEGER NOT NULL,
            recommended_staff INTEGER NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE guest_requests (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id        INTEGER NOT NULL,
            guest_name     TEXT NOT NULL,
            request_text   TEXT NOT NULL,
            recommendation TEXT NOT NULL DEFAULT '',
            status         TEXT NOT NULL DEFAULT 'Pending',
            created_at     TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE reservations (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id   INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            check_in  TEXT NOT NULL,
            check_out TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    """)

    # ── Seed rooms (120 total across 4 floors) ──────────────────────────
    # Floor layout: 30 rooms per floor
    # Room types distributed: Std(40), Deluxe(35), Deluxe AC(25), Suite(15), Penthouse(5)
    floor_wings = {
        1: "Lobby Wing",
        2: "Garden Wing",
        3: "Ocean Wing",
        4: "Penthouse Wing"
    }

    room_type_pool = (
        ["Standard"] * 40 +
        ["Deluxe"] * 35 +
        ["Deluxe AC"] * 25 +
        ["Suite"] * 15 +
        ["Penthouse"] * 5
    )
    random.seed(42)  # Deterministic
    random.shuffle(room_type_pool)

    # Status distribution: ~48 Occupied, ~65 Ready, ~4 Dirty, ~3 Blocked (by PEMS)
    status_pool = (
        ["Occupied"] * 48 +
        ["Ready"] * 61 +
        ["Dirty"] * 4 +
        ["Arrival"] * 4 +
        ["Blocked"] * 3
    )
    random.shuffle(status_pool)

    rooms_data = []
    idx = 0
    for floor in range(1, 5):
        for room_num in range(1, 31):
            room_id = floor * 100 + room_num
            room_type = room_type_pool[idx]
            status = status_pool[idx]
            rooms_data.append((room_id, floor, floor_wings[floor], room_type, status, 0))
            idx += 1

    c.executemany("INSERT INTO rooms VALUES (?,?,?,?,?,?)", rooms_data)

    # ── Seed assets (3 per room: AC, TV, Set-top box) ───────────────────
    # Most assets are low risk. Specific rooms get high risk for demo.
    flagged_rooms = {
        204: {"AC": (87, "Critical", "Power spike detected + service overdue by 40 days. Compressor vibrational frequency anomaly at 10:42 AM — overheating imminent."),
              "TV": (42, "Warning", "HDMI handshake intermittent failures logged 6 times in 48h. Firmware update pending."),
              "Set-top box": (8, "Operational", "All telemetry nominal. Last firmware sync 3 days ago.")},
        317: {"AC": (73, "Critical", "Refrigerant pressure drop detected — 18% below safe threshold. Condenser coil efficiency degraded, likely blockage."),
              "TV": (15, "Operational", "Display panel within spec. Backlight hours: 4,200 / 60,000."),
              "Set-top box": (22, "Operational", "Minor network latency spikes during peak hours. Non-critical.")},
        412: {"AC": (91, "Critical", "Compressor motor current draw 34% above rated capacity. Bearing wear pattern consistent with imminent seizure. Emergency service required."),
              "TV": (5, "Operational", "All systems nominal."),
              "Set-top box": (12, "Operational", "Firmware v3.2.1 current. No issues detected.")},
    }

    assets_data = []
    for room_id, floor, wing, room_type, status, flagged in rooms_data:
        if room_id in flagged_rooms:
            for asset_type, (risk, ast_status, reason) in flagged_rooms[room_id].items():
                assets_data.append((room_id, asset_type, risk, ast_status, reason))
        else:
            # Normal assets with low risk
            ac_risk = random.randint(2, 25)
            tv_risk = random.randint(1, 18)
            stb_risk = random.randint(1, 12)
            assets_data.append((room_id, "AC", ac_risk, "Operational",
                              f"Routine operation. Last serviced {random.randint(5,90)} days ago."))
            assets_data.append((room_id, "TV", tv_risk, "Operational",
                              f"Display panel within spec. Backlight hours: {random.randint(1000,8000):,} / 60,000."))
            assets_data.append((room_id, "Set-top box", stb_risk, "Operational",
                              f"Firmware current. Uptime: {random.randint(10,180)} days."))

    c.executemany("INSERT INTO assets (room_id, asset_type, risk_percent, status, reason) VALUES (?,?,?,?,?)",
                  assets_data)

    # Mark flagged rooms as Blocked + has_flagged_asset
    for room_id in flagged_rooms:
        c.execute("UPDATE rooms SET status='Blocked', has_flagged_asset=1 WHERE room_id=?", (room_id,))

    # ── Seed staff departments ──────────────────────────────────────────
    staff_data = [
        ("Housekeeping", 8, 11),
        ("Front Desk & Concierge", 6, 6),
        ("Kitchen & Culinary", 12, 15),
        ("Facilities & Engineering", 4, 6),
        ("Spa & Wellness", 8, 8),
    ]
    c.executemany("INSERT INTO staff (department, current_staff, recommended_staff) VALUES (?,?,?)",
                  staff_data)

    # ── Seed guest requests ─────────────────────────────────────────────
    guest_requests_data = [
        (203, "Sophia Jenkins",
         "Could we get a recommendation for a quiet dinner for two tonight? Preferably Italian or seafood, around 7:00 PM.",
         "Suggest Mare Nostrum Ristorante at 7:30 PM — main dining kitchen is currently at peak load at 7:00 PM (88 dinner covers booked), whereas the 7:30 PM window offers optimal table turnover in the scenic garden patio with dedicated sommelier service.",
         "Pending"),
        (301, "David & Clara Vance",
         "Requesting extra towels and late checkout tomorrow around 1:00 PM if possible.",
         "Counter-offer 12:30 PM complimentary late checkout — Room 301 has an incoming Diamond Tier VIP arrival scheduled at 14:00 PM; a 1:00 PM departure leaves only 60 minutes and risks a ~45m housekeeping turn bottleneck. Fresh plush towel set dispatched via Cart #2.",
         "Pending"),
        (104, "Elena Rostova",
         "Spa booking for couples deep tissue massage this afternoon. Looking for something tranquil around 4 or 5 PM.",
         "Recommend 16:30 slot at Lagoon Cabana Suite — Spa treatment roster is fully staffed (8/8 therapists active), and the cabana offers complete acoustic privacy before evening lagoon lighting transitions.",
         "Pending"),
        (402, "Marcus Brody",
         "Airport transfer arrangements for 06:30 AM flight tomorrow. Two carry-ons and one oversized surf bag.",
         "Booked private luxury hybrid shuttle dispatch at 04:45 AM with bellhop escort for surf gear scheduled at 04:30 AM. Chauffeur assigned.",
         "Sent"),
    ]
    c.executemany(
        "INSERT INTO guest_requests (room_id, guest_name, request_text, recommendation, status) VALUES (?,?,?,?,?)",
        guest_requests_data)

    # ── Seed reservations (for occupied rooms) ──────────────────────────
    occupied_rooms = [r for r in rooms_data if r[4] == "Occupied"]
    guest_names = ["James Miller", "Sarah Chen", "Robert Kim", "Emily Davis",
                   "Michael Brown", "Lisa Wang", "David Johnson", "Anna Schmidt",
                   "Thomas Lee", "Maria Garcia", "William Park", "Jennifer Liu"]
    for i, (room_id, *_) in enumerate(occupied_rooms):
        name = guest_names[i % len(guest_names)]
        c.execute("INSERT INTO reservations (room_id, guest_name, check_in, check_out) VALUES (?,?,?,?)",
                  (room_id, name, "2025-10-23", "2025-10-26"))

    conn.commit()
    conn.close()
    print(f"[OK] Database seeded at {DB_PATH}")
    print(f"  - 120 rooms, {len(assets_data)} assets, {len(staff_data)} departments, {len(guest_requests_data)} guest requests")

if __name__ == "__main__":
    seed()
