from app.models import OptimizeRouteRequest
from pydantic import Field, BaseModel

# Let's try changing model_config extra to "allow"
# In Pydantic v2, we might need to rebuild the model using model_rebuild()
OptimizeRouteRequest.model_config["extra"] = "allow"
OptimizeRouteRequest.model_rebuild(force=True)

payload_data = {
    "source": {"id": "S", "lat": 0.0, "lng": 0.0},
    "destination": {"id": "D", "lat": 1.0, "lng": 1.0},
    "distance_budget": 10.0,
    "algorithm": "beam"
}

req = OptimizeRouteRequest(**payload_data)
print("model_extra:", req.model_extra)
print("hasattr:", hasattr(req, "algorithm"))
print("model_dump:", req.model_dump())
