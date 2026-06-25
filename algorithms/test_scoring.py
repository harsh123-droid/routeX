from models import Location
from scoring import score_route

museum = Location(name="Museum", score=8, category="Historical", detour=4)
fort = Location(name="Fort", score=10, category="Historical", detour=5)
temple = Location(name="Temple", score=9, category="Historical", detour=6)

route = [museum, fort, temple]

result = score_route(route, category_threshold=2)
print(result)
