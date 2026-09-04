"""
Resort OS — PEMS Data Generator
Generates synthetic training data for room-asset predictive maintenance.
Unified feature set across AC, TV, and Set-top box assets.

Usage:  python ml/data_generator.py
Output: ml/training_data.csv
"""
import csv
import os
import random
import math

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "training_data.csv")

# ── Configuration ────────────────────────────────────────────────────────
NUM_ROOMS = 120
ASSET_TYPES = ["AC", "TV", "Set-top box"]
SAMPLES_PER_ASSET = 15  # ~5,400 total rows
RANDOM_SEED = 42

# Feature ranges per asset type (min, max, failure_threshold)
# power_draw: normalised 0–1 (relative to rated capacity)
# usage_hours: hours per day
# operating_hours_since_service: total hours since last service visit
# error_log_count: error events in last 30 days
ASSET_PROFILES = {
    "AC": {
        "power_draw":                   (0.20, 1.00, 0.80),
        "usage_hours":                  (2.0,  22.0, 16.0),
        "operating_hours_since_service": (50,  5000, 3000),
        "error_log_count":              (0,    40,   15),
        "base_failure_rate":            0.05,
    },
    "TV": {
        "power_draw":                   (0.10, 0.70, 0.55),
        "usage_hours":                  (1.0,  18.0, 14.0),
        "operating_hours_since_service": (50,  4000, 2800),
        "error_log_count":              (0,    30,   12),
        "base_failure_rate":            0.03,
    },
    "Set-top box": {
        "power_draw":                   (0.05, 0.50, 0.38),
        "usage_hours":                  (1.0,  18.0, 14.0),
        "operating_hours_since_service": (50,  3500, 2500),
        "error_log_count":              (0,    50,   18),
        "base_failure_rate":            0.02,
    },
}


def _failure_probability(profile, power_draw, usage_hours, op_hours, error_count):
    """Compute realistic failure probability from feature values."""
    _, _, pd_thresh = profile["power_draw"]
    _, _, uh_thresh = profile["usage_hours"]
    _, _, oh_thresh = profile["operating_hours_since_service"]
    _, _, ec_thresh = profile["error_log_count"]

    # Each feature contributes a 0–1 risk signal based on how far past threshold
    # High multipliers → only extreme values trigger risk
    pd_risk = max(0, (power_draw - pd_thresh * 0.75) / (pd_thresh * 0.25)) if pd_thresh else 0
    uh_risk = max(0, (usage_hours - uh_thresh * 0.75) / (uh_thresh * 0.25)) if uh_thresh else 0
    oh_risk = max(0, (op_hours - oh_thresh * 0.70) / (oh_thresh * 0.30)) if oh_thresh else 0
    ec_risk = max(0, (error_count - ec_thresh * 0.60) / (ec_thresh * 0.40)) if ec_thresh else 0

    # Weighted combination
    combined = 0.30 * pd_risk + 0.20 * uh_risk + 0.25 * oh_risk + 0.25 * ec_risk
    # Squash: base rate + scaled risk (capped at 0.85 to avoid trivial all-failure)
    prob = profile["base_failure_rate"] + (0.85 - profile["base_failure_rate"]) * min(combined ** 1.5, 1.0)
    return min(prob, 1.0)


def generate():
    random.seed(RANDOM_SEED)
    rows = []

    room_ids = [floor * 100 + num for floor in range(1, 5) for num in range(1, 31)]

    for room_id in room_ids:
        for asset_type in ASSET_TYPES:
            profile = ASSET_PROFILES[asset_type]
            pd_min, pd_max, _ = profile["power_draw"]
            uh_min, uh_max, _ = profile["usage_hours"]
            oh_min, oh_max, _ = profile["operating_hours_since_service"]
            ec_min, ec_max, _ = profile["error_log_count"]

            for _ in range(SAMPLES_PER_ASSET):
                power_draw = round(random.uniform(pd_min, pd_max), 3)
                usage_hours = round(random.uniform(uh_min, uh_max), 1)
                op_hours = random.randint(oh_min, oh_max)
                error_count = random.randint(ec_min, ec_max)

                prob = _failure_probability(profile, power_draw, usage_hours, op_hours, error_count)
                # Stochastic label with computed probability
                failure = 1 if random.random() < prob else 0

                rows.append({
                    "room_id": room_id,
                    "asset_type": asset_type,
                    "power_draw": power_draw,
                    "usage_hours": usage_hours,
                    "operating_hours_since_service": op_hours,
                    "error_log_count": error_count,
                    "failure": failure,
                })

    # Shuffle rows
    random.shuffle(rows)

    # Write CSV
    fieldnames = [
        "room_id", "asset_type", "power_draw", "usage_hours",
        "operating_hours_since_service", "error_log_count", "failure",
    ]
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Stats
    total = len(rows)
    failures = sum(r["failure"] for r in rows)
    print(f"[OK] Generated {total} samples → {OUTPUT_PATH}")
    print(f"     Failure rate: {failures}/{total} ({100*failures/total:.1f}%)")
    for at in ASSET_TYPES:
        at_rows = [r for r in rows if r["asset_type"] == at]
        at_fail = sum(r["failure"] for r in at_rows)
        print(f"     {at:15s}: {at_fail}/{len(at_rows)} ({100*at_fail/len(at_rows):.1f}%)")


if __name__ == "__main__":
    generate()
