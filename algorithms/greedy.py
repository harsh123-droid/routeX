from typing import TypedDict

from algorithms.models import Location
from algorithms.scoring import effective_satisfaction, score_route


class OptimizeResult(TypedDict):
    route: list[Location]
    total_score: float
    total_distance: float
    penalty_count: int


def optimize_route(
    locations: list[Location],
    distance_budget: float,
    category_threshold: int,
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
    decay_constant: float = 0.1,
) -> OptimizeResult:
    """Select stops greedily by satisfaction per unit detour, then score the route."""
    route: list[Location] = []
    unvisited = list(locations)

    if distance_lookup is not None:
        current_loc = source_id
        cumulative_distance = 0.0

        while unvisited:
            best_location: Location | None = None
            best_value = float("-inf")

            for location in unvisited:
                d_next = distance_lookup.get((current_loc, location.name), 0.0)
                d_dest = distance_lookup.get((location.name, destination_id), 0.0)
                
                # Check if adding this location is within the distance budget
                new_cumulative = cumulative_distance + d_next
                total_dist = new_cumulative + d_dest
                if total_dist > distance_budget:
                    continue

                # detour distance is the cost of visiting this node
                satisfaction = effective_satisfaction(
                                        location.score,
                                        cumulative_distance,
                                        decay_constant,
                )

                # Check category penalty
                category_counts = [r.category for r in route]
                if category_counts.count(location.category) >= category_threshold:
                    satisfaction *= 0.9

                travel_cost = max(d_next, 1.0)

                value = satisfaction / travel_cost
                if value > best_value:
                    best_value = value
                    best_location = location

            if best_location is None:
                break

            route.append(best_location)
            cumulative_distance += distance_lookup.get((current_loc, best_location.name), 0.0)
            current_loc = best_location.name
            unvisited.remove(best_location)
    else:
        current_distance = 0.0
        while unvisited:
            best_location: Location | None = None
            best_value = float("-inf")

            for location in unvisited:
                if location.detour <= 0:
                    continue
                if current_distance + location.detour > distance_budget:
                    continue

                satisfaction = effective_satisfaction(location.score, current_distance, decay_constant)
                # Check category penalty
                category_counts = [r.category for r in route]
                if category_counts.count(location.category) >= category_threshold:
                    satisfaction *= 0.9

                value = satisfaction / location.detour
                if value > best_value:
                    best_value = value
                    best_location = location

            if best_location is None:
                break

            route.append(best_location)
            current_distance += best_location.detour
            unvisited.remove(best_location)
    scored = score_route(
        route=route,
        category_threshold=category_threshold,
        source_id=source_id,
        destination_id=destination_id,
        distance_lookup=distance_lookup,
        decay_constant=decay_constant,
    )

    return {
        "route": route,
        "total_score": scored["total_score"],
        "total_distance": scored["total_distance"],
        "penalty_count": scored["penalty_count"],
    }
