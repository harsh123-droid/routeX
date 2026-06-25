from app.models import Location, RouteStop, RouteStopType, RideRequest


class RouteState:
    def __init__(self) -> None:
        self.vehicle_capacity = 4
        self.active_requests: dict[str, RideRequest] = {}

        self.route: list[RouteStop] = [
            RouteStop(
                location=Location(id="S", lat=0, lng=0),
                stop_type=RouteStopType.start,
            )
        ]

    def reset(self, vehicle_capacity: int, start: Location, destination: Location | None = None) -> None:
        self.vehicle_capacity = vehicle_capacity
        self.active_requests = {}
        self.route = [RouteStop(location=start, stop_type=RouteStopType.start)]
        if destination is not None:
            self.route.append(RouteStop(location=destination, stop_type=RouteStopType.destination))


route_state = RouteState()
