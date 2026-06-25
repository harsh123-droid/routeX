from asyncio import coroutines
import math
from collections import defaultdict
from typing import TypedDict

from algorithms.models import Location


class RouteScore(TypedDict):
    total_score: float
    total_distance: float
    penalty_count: int


def effective_satisfaction(score: float, cumulative_distance: float, decay_constant: float = 0.1) -> float:
    """Score adjusted for diminishing returns as travel distance grows."""
    return score * math.exp(-decay_constant * cumulative_distance)


def score_route(
    route: list[Location],
    category_threshold: int,
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
    decay_constant: float = 0.1,
) -> RouteScore:
    """Score a route with distance decay and per-category repetition penalties."""
    total_score = 0.0
    total_distance = 0.0
    penalty_count = 0
    category_counts: dict[str, int] = defaultdict(int)

    if distance_lookup is not None:
        cumulative_distance = 0.0
        current_loc = source_id

        for location in route:
            dist = distance_lookup.get((current_loc, location.name), 0.0)

            satisfaction = effective_satisfaction(
                location.score,
                cumulative_distance,
                decay_constant,
            )

            if category_counts[location.category] >= category_threshold:
                satisfaction *= 0.9
                penalty_count += 1

            category_counts[location.category] += 1
            total_score += satisfaction
            cumulative_distance += dist

            current_loc = location.name

        final_leg = distance_lookup.get((current_loc, destination_id), 0.0)
        total_distance = cumulative_distance + final_leg

    else:
        cumulative_distance = 0.0
        for location in route:
            satisfaction = effective_satisfaction(location.score, cumulative_distance, decay_constant)

            if category_counts[location.category] >= category_threshold:
                satisfaction *= 0.9
                penalty_count += 1

            category_counts[location.category] += 1
            total_score += satisfaction
            cumulative_distance += location.detour
            total_distance += location.detour

    return {
        "total_score": total_score,
        "total_distance": total_distance,
        "penalty_count": penalty_count,
    }
