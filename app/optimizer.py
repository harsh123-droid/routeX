from collections import defaultdict
from math import exp

from app.distance import build_distance_lookup, route_distance, distance_between
from app.models import Location, OptimizeRouteRequest, OptimizeRouteResponse, SightseeingLocation
from algorithms.optimizer_service import optimize
from algorithms.models import Location as AlgoLocation


def effective_satisfaction(
    location: SightseeingLocation,
    cumulative_distance: float,
    category_count: int,
    category_threshold: int,
    decay_constant: float,
) -> float:
    score = location.score * exp(-decay_constant * cumulative_distance)
    if category_count >= category_threshold:
        score *= 0.9
    return score


def placeholder_optimize_route(payload: OptimizeRouteRequest) -> OptimizeRouteResponse:
    """Simple deterministic placeholder until Member 1 plugs in a real optimizer."""
    algorithm = getattr(payload, "algorithm", None)
    if not algorithm and hasattr(payload, "model_extra") and payload.model_extra:
        algorithm = payload.model_extra.get("algorithm")
    if not algorithm:
        algorithm = "greedy"

    algo_locations = [
        AlgoLocation(
            name=loc.id,
            score=loc.score,
            category=loc.category,
            detour=loc.detour_distance,
        )
        for loc in payload.locations
    ]

    matrix_lookup = build_distance_lookup(payload.distance_matrix)
    distance_lookup = {}
    all_locs = [payload.source] + list(payload.locations) + [payload.destination]
    for loc1 in all_locs:
        for loc2 in all_locs:
            distance_lookup[(loc1.id, loc2.id)] = distance_between(loc1, loc2, matrix_lookup)

    result = optimize(
        algorithm=algorithm,
        locations=algo_locations,
        distance_budget=payload.distance_budget,
        category_threshold=payload.category_threshold,
        source_id=payload.source.id,
        destination_id=payload.destination.id,
        distance_lookup=distance_lookup,
        decay_constant=payload.decay_constant,
    )

    location_by_id = {loc.id: loc for loc in payload.locations}
    selected_locations = []
    for item in result["route"]:
        original_loc = location_by_id.get(item.name)
        if original_loc is not None:
            selected_locations.append(original_loc)

    route = [payload.source] + selected_locations + [payload.destination]

    return OptimizeRouteResponse(
        route=route,
        total_distance=round(result["total_distance"], 3),
        total_effective_satisfaction=round(result["total_score"], 3),
        selected_location_ids=[item.name for item in result["route"]],
        algorithm=algorithm,
        message=f"Route optimized successfully using the {algorithm} algorithm.",
    )
