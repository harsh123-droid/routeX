from dataclasses import dataclass


@dataclass
class Location:
    name: str
    score: float
    category: str
    detour: float

    def __repr__(self) -> str:
        return (
            f"Location(name={self.name!r}, score={self.score}, "
            f"category={self.category!r}, detour={self.detour})"
        )
