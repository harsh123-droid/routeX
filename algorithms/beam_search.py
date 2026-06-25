from typing import TypedDict

from algorithms.models import Location
from algorithms.scoring import score_route


class OptimizeResult(TypedDict):
    route: list[Location]
    total_score: float
    total_distance: float
    penalty_count: int


def _to_result(route: list[Location], scored: dict[str, float | int]) -> OptimizeResult:
    return {
        "route": list(route),
        "total_score": float(scored["total_score"]),
        "total_distance": float(scored["total_distance"]),
        "penalty_count": int(scored["penalty_count"]),
    }


def optimize_route(
    locations: list[Location],
    distance_budget: float,
    category_threshold: int,
    beam_width: int = 10,
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
    decay_constant: float = 0.1,
) -> OptimizeResult:
    """Find a high-scoring route by expanding and pruning partial routes with beam search."""
    width = max(beam_width, 1)
    best = _to_result(
        [],
        score_route(
            route=[],
            category_threshold=category_threshold,
            source_id=source_id,
            destination_id=destination_id,
            distance_lookup=distance_lookup,
            decay_constant=decay_constant,
        )
    )
    best_score = best["total_score"]

    beam: list[list[Location]] = [[]]

    while beam:
        candidates: list[tuple[float, list[Location]]] = []

        for route in beam:
            scored = score_route(
                route=route,
                category_threshold=category_threshold,
                source_id=source_id,
                destination_id=destination_id,
                distance_lookup=distance_lookup,
                decay_constant=decay_constant,
            )
            if scored["total_score"] > best_score:
                best_score = scored["total_score"]
                best = _to_result(route, scored)

            for location in locations:
                if any(location.name == stop.name for stop in route):
                    continue

                candidate_route = route + [location]
                candidate_scored = score_route(
                    route=candidate_route,
                    category_threshold=category_threshold,
                    source_id=source_id,
                    destination_id=destination_id,
                    distance_lookup=distance_lookup,
                    decay_constant=decay_constant,
                )
                if candidate_scored["total_distance"] > distance_budget:
                    continue

                candidates.append((candidate_scored["total_score"], candidate_route))

        if not candidates:
            break

        candidates.sort(key=lambda item: item[0], reverse=True)
        
        seen_routes = set()
        next_beam = []
        for _, route in candidates:
            route_key = tuple(loc.name for loc in route)
            if route_key not in seen_routes:
                seen_routes.add(route_key)
                next_beam.append(route)
                if len(next_beam) == width:
                    break
        beam = next_beam

    return best
