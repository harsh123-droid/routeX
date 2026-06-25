from benchmark import generate_locations
from beam_search import optimize_route

locations = generate_locations(50)

for width in [3, 10, 20]:
    result = optimize_route(
        locations=locations,
        distance_budget=50,
        category_threshold=2,
        beam_width=width,
    )

    print(f"\nBeam Width = {width}")
    print(f"Score = {result['total_score']}")
    print(f"Distance = {result['total_distance']}")