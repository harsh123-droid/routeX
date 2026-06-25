from models import Location
from optimizer_service import optimize

locations = [
    Location("Fort", 10, "Historical", 5),
    Location("Museum", 8, "Historical", 4),
    Location("Park", 6, "Nature", 3),
]

result = optimize(
    algorithm="greedy",
    locations=locations,
    distance_budget=15,
    category_threshold=2,
)

print(result)