from typing import TypedDict

from models import Location


class RouteLocationResponse(TypedDict):
    name: str
    category: str
    score: float
    detour: float


class RouteSummaryResponse(TypedDict):
    total_score: float
    total_distance: float
    penalty_count: int
    runtime_ms: float


class RouteResponse(TypedDict):
    route: list[RouteLocationResponse]
    summary: RouteSummaryResponse
    explanations: list[str]


def _format_location(location: Location) -> RouteLocationResponse:
    """Convert a Location into a JSON-friendly route stop."""
    return {
        "name": location.name,
        "category": location.category,
        "score": float(location.score),
        "detour": float(location.detour),
    }


def format_route_response(
    route: list[Location],
    total_score: float,
    total_distance: float,
    penalty_count: int,
    runtime_ms: float,
    explanations: list[str],
) -> RouteResponse:
    """Format optimizer output into a JSON-friendly API response."""
    return {
        "route": [_format_location(location) for location in route],
        "summary": {
            "total_score": float(total_score),
            "total_distance": float(total_distance),
            "penalty_count": int(penalty_count),
            "runtime_ms": float(runtime_ms),
        },
        "explanations": list(explanations),
    }
