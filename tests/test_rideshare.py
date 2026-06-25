import unittest

from app.models import Location, MatrixDistance, RideRequest, RouteStop, RouteStopType
from app.rideshare import insert_request


def loc(location_id: str) -> Location:
    coordinates = {
        "S": (0, 0),
        "A": (0, 4),
        "B": (0, 8),
        "C": (0, 6),
        "D": (0, 10),
    }
    lat, lng = coordinates[location_id]
    return Location(id=location_id, lat=lat, lng=lng)


def matrix() -> list[MatrixDistance]:
    values = {
        ("S", "A"): 4,
        ("S", "B"): 8,
        ("S", "C"): 6,
        ("S", "D"): 10,
        ("A", "B"): 5,
        ("A", "C"): 3,
        ("A", "D"): 7,
        ("B", "C"): 4,
        ("B", "D"): 2,
        ("C", "D"): 6,
    }
    return [MatrixDistance(from_id=a, to_id=b, distance=d) for (a, b), d in values.items()]


class RideShareInsertionTests(unittest.TestCase):
    def test_insert_request_chooses_least_cost_feasible_route(self):
        route = [
            RouteStop(location=loc("S"), stop_type=RouteStopType.start),
            RouteStop(location=loc("A"), stop_type=RouteStopType.pickup, request_id="req-1", passenger_delta=1),
            RouteStop(location=loc("B"), stop_type=RouteStopType.drop, request_id="req-1", passenger_delta=-1),
        ]
        request = RideRequest(
            request_id="req-2",
            pickup=loc("C"),
            drop=loc("D"),
            passengers=1,
            base_distance=6,
            flexibility=2,
        )

        result = insert_request(route, request, capacity=2, distance_matrix=matrix())

        self.assertTrue(result.accepted)
        self.assertEqual([stop.location.id for stop in result.route], ["S", "A", "C", "B", "D"])
        self.assertEqual(result.total_distance, 13)
        self.assertEqual([item.active_passengers for item in result.passenger_trace], [0, 1, 2, 1, 0])

    def test_insert_request_rejects_when_capacity_would_be_exceeded(self):
        route = [
            RouteStop(location=loc("S"), stop_type=RouteStopType.start, request_id="req-1", passenger_delta=2),
            RouteStop(location=loc("B"), stop_type=RouteStopType.destination, request_id="req-1", passenger_delta=-2),
        ]
        request = RideRequest(
            request_id="req-2",
            pickup=loc("C"),
            drop=loc("D"),
            passengers=1,
            base_distance=6,
            flexibility=10,
        )

        result = insert_request(route, request, capacity=2, distance_matrix=matrix())

        self.assertFalse(result.accepted)


if __name__ == "__main__":
    unittest.main()
