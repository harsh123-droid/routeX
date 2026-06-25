import random
from typing import TypedDict

from algorithms.models import Location
from algorithms.scoring import score_route


class OptimizeResult(TypedDict):
    route: list[Location]
    total_score: float
    total_distance: float
    penalty_count: int


def _get_route_distance(
    route: list[Location],
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
) -> float:
    if distance_lookup is not None:
        dist = 0.0
        current_loc = source_id
        for loc in route:
            dist += distance_lookup.get((current_loc, loc.name), 0.0)
            current_loc = loc.name
        dist += distance_lookup.get((current_loc, destination_id), 0.0)
        return dist
    else:
        return sum(loc.detour for loc in route)


def _generate_random_route(
    locations: list[Location],
    distance_budget: float,
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
) -> list[Location]:
    """Generate a single valid random route that respects the distance budget.

    No duplicate locations are allowed in the route.
    """
    shuffled = list(locations)
    random.shuffle(shuffled)
    route: list[Location] = []
    for loc in shuffled:
        candidate_route = route + [loc]
        if _get_route_distance(candidate_route, source_id, destination_id, distance_lookup) <= distance_budget:
            route.append(loc)
    return route


def _tournament_select(
    population: list[list[Location]],
    fitnesses: list[float],
    tournament_size: int = 3,
) -> list[Location]:
    """Select a route from the population using tournament selection."""
    k = min(tournament_size, len(population))
    candidates = random.choices(range(len(population)), k=k)
    best_idx = max(candidates, key=lambda idx: fitnesses[idx])
    return list(population[best_idx])


def _crossover(
    parent1: list[Location],
    parent2: list[Location],
    distance_budget: float,
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
) -> list[Location]:
    """Combine two parent routes to produce a valid child route.

    Copies a random prefix of parent1 and fills the remaining budget with unique
    locations from parent2.
    """
    if not parent1 and not parent2:
        return []
    if not parent1:
        return list(parent2)
    if not parent2:
        return list(parent1)

    split_idx = random.randint(0, len(parent1))
    child: list[Location] = []
    seen: set[str] = set()

    # Step 1: Copy a prefix from parent1
    for loc in parent1[:split_idx]:
        candidate_route = child + [loc]
        if _get_route_distance(candidate_route, source_id, destination_id, distance_lookup) <= distance_budget:
            child.append(loc)
            seen.add(loc.name)
        else:
            break

    # Step 2: Fill remaining budget with unique locations from parent2
    for loc in parent2:
        if loc.name not in seen:
            candidate_route = child + [loc]
            if _get_route_distance(candidate_route, source_id, destination_id, distance_lookup) <= distance_budget:
                child.append(loc)
                seen.add(loc.name)

    return child


def _mutate(route: list[Location], mutation_rate: float) -> list[Location]:
    """Mutate a route by randomly swapping two locations if the rate check passes.

    Swapping locations preserves the total detour distance, ensuring route validity.
    """
    if random.random() > mutation_rate:
        return list(route)
    if len(route) < 2:
        return list(route)

    mutated = list(route)
    idx1, idx2 = random.sample(range(len(mutated)), 2)
    mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
    return mutated


def optimize_route(
    locations: list[Location],
    distance_budget: float,
    category_threshold: int,
    population_size: int = 30,
    generations: int = 50,
    mutation_rate: float = 0.1,
    source_id: str = "S",
    destination_id: str = "D",
    distance_lookup: dict[tuple[str, str], float] | None = None,
    decay_constant: float = 0.1,
) -> OptimizeResult:
    """Optimize a sightseeing route using a genetic algorithm.

    Args:
        locations: A list of candidate locations to visit.
        distance_budget: The maximum allowed cumulative detour distance.
        category_threshold: The threshold for repeating categories before penalties apply.
        population_size: The number of individuals in the genetic algorithm population.
        generations: The number of evolution iterations to run.
        mutation_rate: The probability of mutating an individual route.
        source_id: The identifier for the start node.
        destination_id: The identifier for the end node.
        distance_lookup: Pre-calculated lookup of node-to-node distances.
        decay_constant: Decaying factor for diminishing satisfaction.

    Returns:
        A dictionary containing the optimized route, total score, total distance,
        and category penalty count.

    Raises:
        ValueError: If population_size is less than 2, generations is negative,
                    or mutation_rate is not in the range [0.0, 1.0].
    """
    # Validation checks
    if population_size < 2:
        raise ValueError("population_size must be at least 2 to run genetic optimization.")
    if generations < 0:
        raise ValueError("generations must be non-negative.")
    if not (0.0 <= mutation_rate <= 1.0):
        raise ValueError("mutation_rate must be between 0.0 and 1.0.")

    # Edge cases
    if not locations or distance_budget <= 0:
        scored = score_route(
            route=[],
            category_threshold=category_threshold,
            source_id=source_id,
            destination_id=destination_id,
            distance_lookup=distance_lookup,
            decay_constant=decay_constant,
        )
        return {
            "route": [],
            "total_score": float(scored["total_score"]),
            "total_distance": float(scored["total_distance"]),
            "penalty_count": int(scored["penalty_count"]),
        }

    # Initialize population
    population = [
        _generate_random_route(locations, distance_budget, source_id, destination_id, distance_lookup)
        for _ in range(population_size)
    ]

    # Keep track of the global best route found
    best_route: list[Location] = []
    best_score = float("-inf")

    # Evaluate initial population
    fitnesses = [
        score_route(
            route=route,
            category_threshold=category_threshold,
            source_id=source_id,
            destination_id=destination_id,
            distance_lookup=distance_lookup,
            decay_constant=decay_constant,
        )["total_score"]
        for route in population
    ]
    for route, score in zip(population, fitnesses):
        if score > best_score:
            best_score = score
            best_route = list(route)

    # Evolution loop
    for _ in range(generations):
        next_population: list[list[Location]] = []

        # Elitism: carry over the best route from the current generation
        elite_idx = max(range(population_size), key=lambda idx: fitnesses[idx])
        next_population.append(list(population[elite_idx]))

        # Generate the rest of the next population
        while len(next_population) < population_size:
            parent1 = _tournament_select(population, fitnesses)
            parent2 = _tournament_select(population, fitnesses)

            child = _crossover(
                parent1=parent1,
                parent2=parent2,
                distance_budget=distance_budget,
                source_id=source_id,
                destination_id=destination_id,
                distance_lookup=distance_lookup,
            )
            child = _mutate(child, mutation_rate)

            next_population.append(child)

        population = next_population
        fitnesses = [
            score_route(
                route=route,
                category_threshold=category_threshold,
                source_id=source_id,
                destination_id=destination_id,
                distance_lookup=distance_lookup,
                decay_constant=decay_constant,
            )["total_score"]
            for route in population
        ]

        # Update global best route
        for route, score in zip(population, fitnesses):
            if score > best_score:
                best_score = score
                best_route = list(route)

    # Return final results for the best route found
    scored = score_route(
        route=best_route,
        category_threshold=category_threshold,
        source_id=source_id,
        destination_id=destination_id,
        distance_lookup=distance_lookup,
        decay_constant=decay_constant,
    )
    return {
        "route": best_route,
        "total_score": float(scored["total_score"]),
        "total_distance": float(scored["total_distance"]),
        "penalty_count": int(scored["penalty_count"]),
    }
