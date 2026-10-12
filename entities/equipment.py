import uuid
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Equipment:
    name: str
    category: str  # "LAND" or "NAVAL"
    base_production_cost: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "base_production_cost": self.base_production_cost,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Equipment":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            category=data.get("category", "LAND"),
            base_production_cost=float(data.get("base_production_cost", 0.0)),
        )