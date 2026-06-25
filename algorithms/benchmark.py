import random
import time
from collections.abc import Callable
from typing import Any, TypedDict

import beam_search
import genetic_algorithm
import greedy
from models import Location

RANDOM_SEED = 42
DATASET_SIZES = (10, 20, 50, 100)
CATEGORIES = ("Historical", "Nature", "Temple", "Museum")

DISTANCE_BUDGET = 50.0
CATEGORY_THRESHOLD = 2
BEAM_WIDTH = 10
POPULATION_SIZE = 30
GENERATIONS = 50
MUTATION_RATE = 0.1


class OptimizeResult(TypedDict):
    route: list[Location]
    total_score: float
    total_distance: float
    penalty_count: int


class BenchmarkResult(TypedDict):
    algorithm: str
    dataset_size: int
    total_score: float
    total_distance: float
    runtime_ms: float


def generate_locations(count: int, seed: int = RANDOM_SEED) -> list[Location]:
    """Generate a reproducible list of random sightseeing locations."""
    rng = random.Random(seed)
    locations: list[Location] = []

    for index in range(count):
        locations.append(
            Location(
                name=f"Location_{index + 1}",
                score=rng.uniform(1.0, 10.0),
                category=rng.choice(CATEGORIES),
                detour=rng.uniform(1.0, 15.0),
            )
        )

    return locations


def benchmark_algorithm(
    algorithm_name: str,
    optimize_fn: Callable[..., OptimizeResult],
    locations: list[Location],
    dataset_size: int,
    **optimizer_kwargs: Any,
) -> BenchmarkResult:
    """Run one optimizer and measure score, distance, and runtime in milliseconds."""
    start = time.perf_counter()
    result = optimize_fn(locations, **optimizer_kwargs)
    runtime_ms = (time.perf_counter() - start) * 1000

    return {
        "algorithm": algorithm_name,
        "dataset_size": dataset_size,
        "total_score": result["total_score"],
        "total_distance": result["total_distance"],
        "runtime_ms": runtime_ms,
    }


def _print_results_table(results: list[BenchmarkResult]) -> None:
    """Print benchmark results in a fixed-width table."""
    headers = ("Size", "Algorithm", "Total Score", "Total Distance", "Runtime (ms)")
    rows = [
        (
            str(result["dataset_size"]),
            result["algorithm"],
            f"{result['total_score']:.4f}",
            f"{result['total_distance']:.2f}",
            f"{result['runtime_ms']:.2f}",
        )
        for result in results
    ]

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]

    def format_row(cells: tuple[str, ...]) -> str:
        return " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))

    separator = "-+-".join("-" * width for width in widths)

    print("RouteX Benchmark Results")
    print("=" * len(separator))
    print(f"Distance Budget: {DISTANCE_BUDGET:.0f} | Category Threshold: {CATEGORY_THRESHOLD}")
    print(f"Random Seed: {RANDOM_SEED}")
    print()
    print(format_row(headers))
    print(separator)
    for row in rows:
        print(format_row(row))


def run_benchmarks() -> list[BenchmarkResult]:
    """Benchmark greedy, beam search, and genetic optimizers across dataset sizes."""
    results: list[BenchmarkResult] = []

    for size in DATASET_SIZES:
        locations = generate_locations(size, seed=RANDOM_SEED)

        results.append(
            benchmark_algorithm(
                algorithm_name="Greedy",
                optimize_fn=greedy.optimize_route,
                locations=locations,
                dataset_size=size,
                distance_budget=DISTANCE_BUDGET,
                category_threshold=CATEGORY_THRESHOLD,
            )
        )
        results.append(
            benchmark_algorithm(
                algorithm_name="Beam Search",
                optimize_fn=beam_search.optimize_route,
                locations=locations,
                dataset_size=size,
                distance_budget=DISTANCE_BUDGET,
                category_threshold=CATEGORY_THRESHOLD,
                beam_width=BEAM_WIDTH,
            )
        )
        results.append(
            benchmark_algorithm(
                algorithm_name="Genetic Algorithm",
                optimize_fn=genetic_algorithm.optimize_route,
                locations=locations,
                dataset_size=size,
                distance_budget=DISTANCE_BUDGET,
                category_threshold=CATEGORY_THRESHOLD,
                population_size=POPULATION_SIZE,
                generations=GENERATIONS,
                mutation_rate=MUTATION_RATE,
            )
        )

    _print_results_table(results)
    return results


if __name__ == "__main__":
    run_benchmarks()
