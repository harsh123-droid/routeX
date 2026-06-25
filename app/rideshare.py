from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4

from app.distance import DistanceLookup, build_distance_lookup, distance_between, route_distance
from app.models import PassengerTrace, RideRequest, RouteStop, RouteStopType


@dataclass(frozen=True)
class InsertionResult:
    accepted: bool
    reason: str
    route: list[RouteStop]
    total_distance: float
    added_distance: float
    passenger_trace: list[PassengerTrace]
    runtime_ms: float


def ensure_request_id(request: RideRequest) -> RideRequest:
    if request.request_id:
        return request
    return request.model_copy(update={"request_id": f"req-{uuid4().hex[:8]}"})


def stop_locations(route: list[RouteStop]):
    return [stop.location for stop in route]


def calculate_passenger_trace(route: list[RouteStop]) -> list[PassengerTrace]:
    active = 0
    trace: list[PassengerTrace] = []
    for stop in route:
        active += stop.passenger_delta
        trace.append(PassengerTrace(stop_id=stop.location.id, active_passengers=active))
    return trace


def route_capacity_is_valid(route: list[RouteStop], capacity: int) -> bool:
    return all(0 <= item.active_passengers <= capacity for item in calculate_passenger_trace(route))


def request_ride_distance(route: list[RouteStop], request_id: str, lookup: DistanceLookup) -> float | None:
    pickup_index = None
    drop_index = None
    for index, stop in enumerate(route):
        if stop.request_id == request_id and stop.stop_type == RouteStopType.pickup:
            pickup_index = index
        if stop.request_id == request_id and stop.stop_type == RouteStopType.drop:
            drop_index = index

    if pickup_index is None or drop_index is None or pickup_index >= drop_index:
        return None

    locations = [stop.location for stop in route[pickup_index : drop_index + 1]]
    return route_distance(locations, lookup)


def request_flexibility_is_valid(route: list[RouteStop], request: RideRequest, lookup: DistanceLookup) -> bool:
    if not request.request_id:
        return False

    base_distance = request.base_distance
    if base_distance is None:
        base_distance = distance_between(request.pickup, request.drop, lookup)

    actual_distance = request_ride_distance(route, request.request_id, lookup)
    if actual_distance is None:
        return False

    return actual_distance <= base_distance + request.flexibility

def all_flexibility_constraints_valid(
    route: list[RouteStop],
    requests: dict[str, RideRequest],
    lookup: DistanceLookup,
) -> bool:

    for request in requests.values():
        if not request_flexibility_is_valid(route, request, lookup):
            return False

    return True

def insert_request(
    route: list[RouteStop],
    new_request: RideRequest,
    capacity: int,
    active_requests=None,
    distance_matrix=None,
) -> InsertionResult:
    started_at = perf_counter()
    lookup = build_distance_lookup(distance_matrix)
    request = ensure_request_id(new_request)
    original_distance = route_distance(stop_locations(route), lookup)

    pickup_stop = RouteStop(
        location=request.pickup,
        stop_type=RouteStopType.pickup,
        request_id=request.request_id,
        passenger_delta=request.passengers,
    )
    drop_stop = RouteStop(
        location=request.drop,
        stop_type=RouteStopType.drop,
        request_id=request.request_id,
        passenger_delta=-request.passengers,
    )

    best_route: list[RouteStop] | None = None
    best_distance: float | None = None
    last_stop_is_destination = bool(route and route[-1].stop_type == RouteStopType.destination)
    max_pickup_index = len(route) - 1 if last_stop_is_destination else len(route)

    for pickup_index in range(1, max_pickup_index + 1):
        route_with_pickup = [*route[:pickup_index], pickup_stop, *route[pickup_index:]]
        max_drop_index = len(route_with_pickup) - 1 if last_stop_is_destination else len(route_with_pickup)
        for drop_index in range(pickup_index + 1, max_drop_index + 1):
            candidate = [*route_with_pickup[:drop_index], drop_stop, *route_with_pickup[drop_index:]]
            if not route_capacity_is_valid(candidate, capacity):
                continue
            requests_to_check = dict(active_requests or {})

            requests_to_check[request.request_id] = request

            if not all_flexibility_constraints_valid(
                candidate,
                requests_to_check,
                lookup,
            ):
                continue

            candidate_distance = route_distance(stop_locations(candidate), lookup)
            if best_distance is None or candidate_distance < best_distance:
                best_distance = candidate_distance
                best_route = candidate

    runtime_ms = (perf_counter() - started_at) * 1000
    if best_route is None or best_distance is None:
        return InsertionResult(
            accepted=False,
            reason="No feasible insertion satisfies pickup/drop order, capacity, and flexibility constraints.",
            route=route,
            total_distance=round(original_distance, 3),
            added_distance=0,
            passenger_trace=calculate_passenger_trace(route),
            runtime_ms=round(runtime_ms, 3),
        )

    return InsertionResult(
        accepted=True,
        reason="Request inserted using least-cost feasible insertion.",
        route=best_route,
        total_distance=round(best_distance, 3),
        added_distance=round(best_distance - original_distance, 3),
        passenger_trace=calculate_passenger_trace(best_route),
        runtime_ms=round(runtime_ms, 3),
    )
