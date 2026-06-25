from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class Location(BaseModel):
    id: str = Field(..., min_length=1, examples=["A"])
    lat: float = Field(..., examples=[15.4589])
    lng: float = Field(..., examples=[75.0078])


class SightseeingLocation(Location):
    score: float = Field(..., ge=0)
    category: str = Field(..., min_length=1, examples=["historical"])
    detour_distance: float = Field(0, ge=0)


class RouteStopType(str, Enum):
    start = "start"
    pickup = "pickup"
    drop = "drop"
    waypoint = "waypoint"
    destination = "destination"


class RouteStop(BaseModel):
    location: Location
    stop_type: RouteStopType = RouteStopType.waypoint
    request_id: str | None = None
    passenger_delta: int = 0


class MatrixDistance(BaseModel):
    from_id: str
    to_id: str
    distance: float = Field(..., ge=0)


class OptimizeRouteRequest(BaseModel):
    source: Location
    destination: Location
    locations: list[SightseeingLocation] = Field(default_factory=list)
    distance_budget: float = Field(..., gt=0)
    category_threshold: int = Field(2, ge=1)
    decay_constant: float = Field(0.1, ge=0)
    distance_matrix: list[MatrixDistance] | None = None
    algorithm: str = Field(default="greedy")


class OptimizeRouteResponse(BaseModel):
    route: list[Location]
    total_distance: float
    total_effective_satisfaction: float
    selected_location_ids: list[str]
    algorithm: str
    message: str


class RideRequest(BaseModel):
    request_id: str | None = Field(default=None, examples=["req-2"])
    pickup: Location
    drop: Location
    passengers: int = Field(..., gt=0)
    base_distance: float | None = Field(default=None, ge=0)
    flexibility: float = Field(0, ge=0)

    @model_validator(mode="after")
    def validate_distinct_locations(self) -> "RideRequest":
        if self.pickup.id == self.drop.id:
            raise ValueError("pickup and drop must be different locations")
        return self


class RideRequestEnvelope(BaseModel):
    vehicle_capacity: int | None = Field(default=None, gt=0)
    current_route: list[RouteStop] | None = None
    request: RideRequest
    distance_matrix: list[MatrixDistance] | None = None


class PassengerTrace(BaseModel):
    stop_id: str
    active_passengers: int


class CurrentRouteResponse(BaseModel):
    vehicle_capacity: int
    route: list[RouteStop]
    total_distance: float
    passenger_trace: list[PassengerTrace]


class RideRequestResponse(BaseModel):
    accepted: bool
    reason: str
    route: list[RouteStop]
    total_distance: float
    added_distance: float
    passenger_trace: list[PassengerTrace]


class ResetRouteRequest(BaseModel):
    vehicle_capacity: int = Field(4, gt=0)
    start: Location = Field(default_factory=lambda: Location(id="S", lat=0, lng=0))
    destination: Location | None = None


PositiveFloatList = Annotated[list[float], Field(min_length=1)]
