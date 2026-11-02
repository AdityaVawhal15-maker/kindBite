"""
KindBite — Route planning service
Uses Google OR-Tools when available (requires installation).
Falls back to simulated estimates when Maps credentials not configured.
IMPORTANT: Simulated times are NOT real road travel times.
"""
from __future__ import annotations
import math
import os
from typing import Any, Dict

from app.models import Donation, Volunteer


async def compute_route(donation: Donation, volunteer: Volunteer) -> Dict[str, Any]:
    """
    Compute pickup route for a volunteer.
    Returns distance_km, duration_minutes, and notes.
    Falls back to simulation if Maps not configured.
    """
    maps_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if maps_key:
        return await _compute_real_route(donation, volunteer, maps_key)
    return _simulate_route(donation, volunteer)


async def _compute_real_route(donation: Donation, volunteer: Volunteer, api_key: str) -> Dict[str, Any]:
    """Real route computation using Google Maps Distance Matrix API."""
    try:
        import httpx
        origin = f"{volunteer.latitude},{volunteer.longitude}" if volunteer.latitude else volunteer.city or "Mumbai"
        destination = (
            f"{donation.pickup_latitude},{donation.pickup_longitude}"
            if donation.pickup_latitude else donation.pickup_address
        )
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "key": api_key,
            "mode": "driving",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                return {
                    "distance_km": element["distance"]["value"] / 1000,
                    "duration_minutes": element["duration"]["value"] // 60,
                    "notes": f"Route computed via Google Maps ({element['distance']['text']}, {element['duration']['text']})",
                }
    except Exception:
        pass
    return _simulate_route(donation, volunteer)


def _simulate_route(donation: Donation, volunteer: Volunteer) -> Dict[str, Any]:
    """
    Simulate route when Maps not configured.
    NOT real road distances — for development only.
    """
    # Simple haversine estimate
    lat1 = volunteer.latitude or 19.076  # Default Mumbai
    lon1 = volunteer.longitude or 72.877
    lat2 = donation.pickup_latitude or 19.080
    lon2 = donation.pickup_longitude or 72.880

    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    dist_km = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Very rough estimate: 20 km/h average Mumbai traffic + 10 min overhead
    duration_min = int(dist_km / 20 * 60) + 10

    return {
        "distance_km": round(dist_km, 2),
        "duration_minutes": duration_min,
        "notes": (
            "[SIMULATED] Distance and duration are estimates only. "
            "Real routing requires GOOGLE_MAPS_API_KEY configuration. "
            f"Estimated straight-line distance: {dist_km:.1f} km."
        ),
    }
