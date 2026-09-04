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
            power_draw       REAL NOT NULL DEFAULT 0.0,
            usage_hours      REAL NOT NULL DEFAULT 0.0,
            operating_hours_since_service INTEGER NOT NULL DEFAULT 0,
            error_log_count  INTEGER NOT NULL DEFAULT 0,
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
        204: {"AC": (87, "Critical", "Power spike detected + service overdue by 40 days. Compressor vibrational frequency anomaly at 10:42 AM — overheating imminent.",
                     0.92, 18.5, 4200, 28),
              "TV": (42, "Warning", "HDMI handshake intermittent failures logged 6 times in 48h. Firmware update pending.",
                     0.38, 12.0, 2100, 14),
              "Set-top box": (8, "Operational", "All telemetry nominal. Last firmware sync 3 days ago.",
                              0.12, 8.0, 800, 2)},
        317: {"AC": (73, "Critical", "Refrigerant pressure drop detected — 18% below safe threshold. Condenser coil efficiency degraded, likely blockage.",
                     0.85, 16.0, 3800, 22),
              "TV": (15, "Operational", "Display panel within spec. Backlight hours: 4,200 / 60,000.",
                     0.25, 10.0, 1500, 4),
              "Set-top box": (22, "Operational", "Minor network latency spikes during peak hours. Non-critical.",
                              0.18, 9.0, 1200, 6)},
        412: {"AC": (91, "Critical", "Compressor motor current draw 34% above rated capacity. Bearing wear pattern consistent with imminent seizure. Emergency service required.",
                     0.96, 20.0, 4800, 35),
              "TV": (5, "Operational", "All systems nominal.",
                     0.15, 6.0, 1000, 1),
              "Set-top box": (12, "Operational", "Firmware v3.2.1 current. No issues detected.",
                              0.10, 5.0, 600, 1)},
    }

    assets_data = []
    for room_id, floor, wing, room_type, status, flagged in rooms_data:
        if room_id in flagged_rooms:
            for asset_type, (risk, ast_status, reason, pd, uh, oh, ec) in flagged_rooms[room_id].items():
                assets_data.append((room_id, asset_type, risk, ast_status, reason, pd, uh, oh, ec))
        else:
            # Normal assets with low risk and nominal sensor values
            ac_risk = random.randint(2, 25)
            tv_risk = random.randint(1, 18)
            stb_risk = random.randint(1, 12)
            ac_pd = round(random.uniform(0.20, 0.55), 3)
            tv_pd = round(random.uniform(0.10, 0.35), 3)
            stb_pd = round(random.uniform(0.05, 0.20), 3)
            ac_oh = random.randint(100, 2000)
            tv_oh = random.randint(100, 1800)
            stb_oh = random.randint(50, 1500)
            assets_data.append((room_id, "AC", ac_risk, "Operational",
                              f"Routine operation. Last serviced {random.randint(5,90)} days ago.",
                              ac_pd, round(random.uniform(4.0, 14.0), 1), ac_oh, random.randint(0, 6)))
            assets_data.append((room_id, "TV", tv_risk, "Operational",
                              f"Display panel within spec. Backlight hours: {random.randint(1000,8000):,} / 60,000.",
                              tv_pd, round(random.uniform(2.0, 12.0), 1), tv_oh, random.randint(0, 4)))
            assets_data.append((room_id, "Set-top box", stb_risk, "Operational",
                              f"Firmware current. Uptime: {random.randint(10,180)} days.",
                              stb_pd, round(random.uniform(2.0, 10.0), 1), stb_oh, random.randint(0, 3)))

    c.executemany(
        "INSERT INTO assets (room_id, asset_type, risk_percent, status, reason, power_draw, usage_hours, operating_hours_since_service, error_log_count) VALUES (?,?,?,?,?,?,?,?,?)",
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
