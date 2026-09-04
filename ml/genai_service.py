"""
Resort OS — PEMS GenAI Explanation Service
Generates human-readable maintenance explanations for room assets.
Uses Groq API if available, falls back to template-based explanations.
"""
import os
import json
import urllib.error
import urllib.request

# ── Groq Setup ───────────────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are an AI maintenance analyst for a luxury resort's room-asset management system.
Your scope is strictly limited to resort room asset maintenance — specifically AC units, TVs, and set-top boxes.

Given asset telemetry data and a risk assessment, generate a concise, actionable maintenance explanation.
Focus on:
- What the data indicates (root cause)
- Urgency level and recommended action
- Impact on guest experience if unaddressed

Keep responses to 2-3 sentences. Be specific and technical but accessible to operations staff.
Do NOT answer questions outside of resort room asset maintenance."""


def _groq_completion(prompt: str) -> str | None:
    """Call Groq's streaming API and return the combined response text."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "model": GROQ_MODEL,
        "temperature": 1,
        "max_completion_tokens": 2048,
        "top_p": 1,
        "stream": True,
        "reasoning_effort": "medium",
        "stop": None,
    }
    request = urllib.request.Request(
        GROQ_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    chunks = []
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                event = json.loads(data)
                content = event.get("choices", [{}])[0].get("delta", {}).get("content")
                if content:
                    chunks.append(content)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        print(f"[Groq] Maintenance explanation failed; using template: {exc}")
        return None
    return "".join(chunks).strip() or None


# ── Template-Based Fallback ──────────────────────────────────────────────

_AC_TEMPLATES = {
    "high": "Power draw at {power_draw:.0%} of rated capacity with {error_log_count} error events in 30 days. "
            "Compressor strain pattern detected — {op_hours}h since last service exceeds safe interval. "
            "Immediate inspection required to prevent compressor seizure and guest discomfort.",
    "medium": "Elevated power consumption ({power_draw:.0%} capacity) with {error_log_count} logged errors. "
              "Unit has been running {op_hours}h since last service — approaching maintenance threshold. "
              "Schedule preventive service within 48 hours.",
    "low": "AC unit operating within normal parameters. Power draw at {power_draw:.0%} capacity, "
           "{op_hours}h since last service. No immediate action required.",
}

_TV_TEMPLATES = {
    "high": "Display unit showing {error_log_count} error events in 30 days — potential panel or "
            "HDMI controller degradation. Runtime of {op_hours}h since service with elevated power draw "
            "({power_draw:.0%}). Replace or service before next guest check-in.",
    "medium": "TV logging intermittent errors ({error_log_count} in 30 days). "
              "Power draw slightly elevated at {power_draw:.0%}. Monitor closely and schedule "
              "diagnostic check within the week.",
    "low": "TV operating normally. {op_hours}h since last service, {error_log_count} errors logged. "
           "No action needed.",
}

_STB_TEMPLATES = {
    "high": "Set-top box reporting {error_log_count} errors in 30 days — firmware instability or "
            "hardware fault likely. Power draw at {power_draw:.0%} with {op_hours}h runtime since service. "
            "Swap unit before next guest occupancy.",
    "medium": "Set-top box showing elevated error rate ({error_log_count} events). "
              "Consider firmware update or reboot cycle. {op_hours}h since last service.",
    "low": "Set-top box functioning normally. Firmware current, {error_log_count} minor events logged. "
           "No action required.",
}

_TEMPLATES = {
    "AC": _AC_TEMPLATES,
    "TV": _TV_TEMPLATES,
    "Set-top box": _STB_TEMPLATES,
}


def _get_risk_tier(risk_probability: float) -> str:
    """Map probability to tier: High (≥0.70), Medium (0.40–0.69), Low (<0.40)."""
    if risk_probability >= 0.70:
        return "high"
    elif risk_probability >= 0.40:
        return "medium"
    return "low"


def _template_explanation(
    asset_type: str,
    risk_probability: float,
    power_draw: float,
    usage_hours: float,
    operating_hours_since_service: int,
    error_log_count: int,
) -> str:
    """Generate explanation from templates."""
    tier = _get_risk_tier(risk_probability)
    templates = _TEMPLATES.get(asset_type, _AC_TEMPLATES)
    template = templates.get(tier, templates["low"])

    return template.format(
        power_draw=power_draw,
        usage_hours=usage_hours,
        op_hours=operating_hours_since_service,
        error_log_count=error_log_count,
    )


def _compute_top_factors(
    power_draw: float,
    usage_hours: float,
    operating_hours_since_service: int,
    error_log_count: int,
) -> list[dict]:
    """Rank features by contribution to risk (simple heuristic scoring)."""
    # Normalise each feature to 0–1 range using reasonable max values
    scores = {
        "power_draw": min(power_draw / 1.0, 1.0),
        "error_log_count": min(error_log_count / 40, 1.0),
        "operating_hours_since_service": min(operating_hours_since_service / 5000, 1.0),
        "usage_hours": min(usage_hours / 24, 1.0),
    }
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{"feature": k, "score": round(v, 3)} for k, v in ranked]


async def generate_explanation(
    asset_type: str,
    risk_probability: float,
    power_draw: float,
    usage_hours: float,
    operating_hours_since_service: int,
    error_log_count: int,
) -> str:
    """Generate maintenance explanation with Groq, falling back to templates."""
    prompt = (
        f"Asset: {asset_type} in a resort room\n"
        f"Risk probability: {risk_probability:.1%}\n"
        f"Power draw: {power_draw:.0%} of rated capacity\n"
        f"Usage: {usage_hours:.1f} hours/day\n"
        f"Hours since last service: {operating_hours_since_service}\n"
        f"Error events (30 days): {error_log_count}\n\n"
        f"Generate a concise maintenance explanation for operations staff."
    )
    explanation = _groq_completion(prompt)
    if explanation:
        return explanation

    return _template_explanation(
        asset_type, risk_probability, power_draw,
        usage_hours, operating_hours_since_service, error_log_count,
    )


def get_top_factors(
    power_draw: float,
    usage_hours: float,
    operating_hours_since_service: int,
    error_log_count: int,
) -> list[dict]:
    """Public interface for top risk factors."""
    return _compute_top_factors(
        power_draw, usage_hours, operating_hours_since_service, error_log_count,
    )
