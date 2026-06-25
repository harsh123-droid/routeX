import unittest
from app.models import Location, SightseeingLocation, MatrixDistance, OptimizeRouteRequest
from app.optimizer import placeholder_optimize_route


class SightseeingOptimizationTests(unittest.TestCase):
    def setUp(self):
        self.source = Location(id="S", lat=0.0, lng=0.0)
        self.destination = Location(id="D", lat=0.0, lng=10.0)

        # Three locations along the way
        self.locations = [
            SightseeingLocation(id="A", lat=0.0, lng=2.0, score=10.0, category="Historical"),
            SightseeingLocation(id="B", lat=0.0, lng=5.0, score=8.0, category="Historical"),
            SightseeingLocation(id="C", lat=0.0, lng=8.0, score=6.0, category="Nature"),
        ]

        # Explicit distance matrix: S->A->B->C->D is a straight line
        # Total straight line distance is 10.0
        # If we visit all: S(0) -> A(2) -> B(5) -> C(8) -> D(10) -> distance = 2+3+3+2 = 10.0
        self.distance_matrix = [
            MatrixDistance(from_id="S", to_id="A", distance=2.0),
            MatrixDistance(from_id="S", to_id="B", distance=5.0),
            MatrixDistance(from_id="S", to_id="C", distance=8.0),
            MatrixDistance(from_id="S", to_id="D", distance=10.0),
            MatrixDistance(from_id="A", to_id="B", distance=3.0),
            MatrixDistance(from_id="A", to_id="C", distance=6.0),
            MatrixDistance(from_id="A", to_id="D", distance=8.0),
            MatrixDistance(from_id="B", to_id="C", distance=3.0),
            MatrixDistance(from_id="B", to_id="D", distance=5.0),
            MatrixDistance(from_id="C", to_id="D", distance=2.0),
        ]

    def test_greedy_optimization_within_budget(self):
        # Budget of 12.0 allows all locations to be visited (total route distance is 10.0)
        request = OptimizeRouteRequest(
            source=self.source,
            destination=self.destination,
            locations=self.locations,
            distance_budget=12.0,
            category_threshold=2,
            decay_constant=0.05,
            distance_matrix=self.distance_matrix,
            algorithm="greedy",
        )
        response = placeholder_optimize_route(request)
        self.assertTrue(len(response.route) > 2)
        self.assertLessEqual(response.total_distance, 12.0)
        self.assertEqual(response.selected_location_ids, ["A", "B", "C"])

    def test_greedy_optimization_exceeding_budget_skipped(self):
        # Budget of 6.0 allows visiting A, but not B or C.
        # Route S->A->D has distance 2.0 + 8.0 = 10.0 (exceeds budget 6.0)
        # Route S->D has distance 10.0 (exceeds budget 6.0)
        # So greedy should return empty route (S -> D)
        request = OptimizeRouteRequest(
            source=self.source,
            destination=self.destination,
            locations=self.locations,
            distance_budget=6.0,
            category_threshold=2,
            decay_constant=0.05,
            distance_matrix=self.distance_matrix,
            algorithm="greedy",
        )
        response = placeholder_optimize_route(request)
        self.assertEqual(response.selected_location_ids, [])
        self.assertEqual(response.total_distance, 10.0)

    def test_beam_search_respects_budget(self):
        # Budget of 10.5 allows visiting all locations (total distance 10.0)
        request = OptimizeRouteRequest(
            source=self.source,
            destination=self.destination,
            locations=self.locations,
            distance_budget=10.5,
            category_threshold=2,
            decay_constant=0.1,
            distance_matrix=self.distance_matrix,
            algorithm="beam",
        )
        response = placeholder_optimize_route(request)
        self.assertEqual(response.selected_location_ids, ["A", "B", "C"])
        self.assertEqual(response.total_distance, 10.0)

    def test_decay_constant_and_category_penalty(self):
        # Category threshold of 1 means visiting both A and B (Historical)
        # will trigger a 10% penalty on the second stop (B).
        request = OptimizeRouteRequest(
            source=self.source,
            destination=self.destination,
            locations=self.locations,
            distance_budget=15.0,
            category_threshold=1,
            decay_constant=0.1,
            distance_matrix=self.distance_matrix,
            algorithm="greedy",
        )
        response = placeholder_optimize_route(request)

        # Expected score (correct pre-arrival cumulative distance convention):
        # A: cumulative_before=0.0, satisfaction = 10 * exp(-0.1*0) = 10.000
        # B: cumulative_before=2.0, satisfaction = 8 * exp(-0.1*2) * 0.9 (2nd Historical, penalty)
        #                          = 8 * 0.8187 * 0.9 = 5.895
        # C: cumulative_before=5.0, satisfaction = 6 * exp(-0.1*5) = 6 * 0.6065 = 3.639
        # Total = 10.000 + 5.895 + 3.639 = 19.534
        self.assertAlmostEqual(response.total_effective_satisfaction, 19.534, places=2)


if __name__ == "__main__":
    unittest.main()
