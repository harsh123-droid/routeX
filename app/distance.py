from math import sqrt

from app.models import Location, MatrixDistance


DistanceLookup = dict[tuple[str, str], float]


def build_distance_lookup(matrix: list[MatrixDistance] | None) -> DistanceLookup:
    lookup: DistanceLookup = {}
    if not matrix:
        return lookup

    for item in matrix:
        lookup[(item.from_id, item.to_id)] = item.distance
        lookup[(item.to_id, item.from_id)] = item.distance
    return lookup


def distance_between(a: Location, b: Location, lookup: DistanceLookup | None = None) -> float:
    if a.id == b.id:
        return 0.0

    if lookup:
        matrix_distance = lookup.get((a.id, b.id))
        if matrix_distance is not None:
            return matrix_distance

    return sqrt((a.lat - b.lat) ** 2 + (a.lng - b.lng) ** 2)


def route_distance(locations: list[Location], lookup: DistanceLookup | None = None) -> float:
    if len(locations) < 2:
        return 0.0

    return sum(distance_between(a, b, lookup) for a, b in zip(locations, locations[1:]))
