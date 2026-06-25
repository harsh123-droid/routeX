from models import Location
from explainer import generate_route_explanation
from pprint import pprint

route = [
    Location("Fort", 10, "Historical", 5),
    Location("Museum", 8, "Historical", 4),
    Location("Park", 6, "Nature", 3),
]

result = generate_route_explanation(
    route=route,
    total_score=17.29166323614466,
    total_distance=12.0,
    penalty_count=0,
)

pprint(result)