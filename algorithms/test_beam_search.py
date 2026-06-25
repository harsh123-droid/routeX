from models import Location
from beam_search import optimize_route

locations = [
    Location("Museum", 8, "Historical", 4),
    Location("Fort", 10, "Historical", 5),
    Location("Waterfall", 9, "Nature", 10),
    Location("Park", 6, "Nature", 3),
]

result = optimize_route(
    locations=locations,
    distance_budget=15,
    category_threshold=2,
    beam_width=3,
)

print(result)