from typing import Literal, TypedDict

from algorithms import beam_search
from algorithms import genetic_algorithm
from algorithms import greedy
from algorithms.models import Location

SupportedAlgorithm = Literal["greedy", "beam", "genetic"]
SUPPORTED_ALGORITHMS: tuple[SupportedAlgorithm, ...] = ("greedy", "beam", "genetic")


class OptimizeResult(TypedDict):
    route: list[Location]
    total_score: float
    total_distance: float
    penalty_count: int


def optimize(
    algorithm: str,
    locations: list[Location],
    distance_budget: float,
    category_threshold: int,
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
    decay_constant: float = 0.1,
) -> OptimizeResult:
    """Run the requested route optimization algorithm and return its result."""
    normalized_algorithm = algorithm.strip().lower()

    if normalized_algorithm == "greedy":
        return greedy.optimize_route(
            locations=locations,
            distance_budget=distance_budget,
            category_threshold=category_threshold,
            source_id=source_id,
            destination_id=destination_id,
            distance_lookup=distance_lookup,
            decay_constant=decay_constant,
        )

    if normalized_algorithm == "beam":
        return beam_search.optimize_route(
            locations=locations,
            distance_budget=distance_budget,
            category_threshold=category_threshold,
            source_id=source_id,
            destination_id=destination_id,
            distance_lookup=distance_lookup,
            decay_constant=decay_constant,
        )

    if normalized_algorithm == "genetic":
        return genetic_algorithm.optimize_route(
            locations=locations,
            distance_budget=distance_budget,
            category_threshold=category_threshold,
            source_id=source_id,
            destination_id=destination_id,
            distance_lookup=distance_lookup,
            decay_constant=decay_constant,
        )

    supported = ", ".join(SUPPORTED_ALGORITHMS)
    raise ValueError(
        f"Unsupported algorithm: {algorithm!r}. Supported algorithms are: {supported}."
    )
