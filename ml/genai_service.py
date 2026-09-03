"""
Resort OS — PEMS GenAI Explanation Service
Generates human-readable maintenance explanations for room assets.
Uses Gemini API if available, falls back to template-based explanations.
"""
import os

# ── Gemini Setup ─────────────────────────────────────────────────────────
_genai_model = None

SYSTEM_PROMPT = """You are an AI maintenance analyst for a luxury resort's room-asset management system.
Your scope is strictly limited to resort room asset maintenance — specifically AC units, TVs, and set-top boxes.

Given asset telemetry data and a risk assessment, generate a concise, actionable maintenance explanation.
Focus on:
- What the data indicates (root cause)
- Urgency level and recommended action
- Impact on guest experience if unaddressed

Keep responses to 2-3 sentences. Be specific and technical but accessible to operations staff.
Do NOT answer questions outside of resort room asset maintenance."""


def _try_init_genai():
    """Attempt to initialise Gemini client. Returns model or None."""
    global _genai_model
    if _genai_model is not None:
        return _genai_model

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _genai_model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        return _genai_model
    except Exception:
        return None


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
    """Generate maintenance explanation. Tries Gemini, falls back to templates."""
    model = _try_init_genai()

    if model is not None:
        try:
            prompt = (
                f"Asset: {asset_type} in a resort room\n"
                f"Risk probability: {risk_probability:.1%}\n"
                f"Power draw: {power_draw:.0%} of rated capacity\n"
                f"Usage: {usage_hours:.1f} hours/day\n"
                f"Hours since last service: {operating_hours_since_service}\n"
                f"Error events (30 days): {error_log_count}\n\n"
                f"Generate a concise maintenance explanation for operations staff."
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            pass  # Fall through to template

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
