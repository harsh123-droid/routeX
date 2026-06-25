import time
from pprint import pprint

from explainer import generate_route_explanation
from models import Location
from optimizer_service import optimize
from response_formatter import format_route_response

locations = [
    Location(name="Fort", score=10, category="Historical", detour=5),
    Location(name="Museum", score=8, category="Historical", detour=4),
    Location(name="Park", score=6, category="Nature", detour=3),
    Location(name="Waterfall", score=9, category="Nature", detour=10),
]

distance_budget = 20
category_threshold = 2

start = time.perf_counter()
result = optimize(
    algorithm="greedy",
    locations=locations,
    distance_budget=distance_budget,
    category_threshold=category_threshold,
)
runtime_ms = (time.perf_counter() - start) * 1000

explanation = generate_route_explanation(
    route=result["route"],
    total_score=result["total_score"],
    total_distance=result["total_distance"],
    penalty_count=result["penalty_count"],
)

response = format_route_response(
    route=result["route"],
    total_score=result["total_score"],
    total_distance=result["total_distance"],
    penalty_count=result["penalty_count"],
    runtime_ms=runtime_ms,
    explanations=explanation["explanations"],
)

pprint(response)
