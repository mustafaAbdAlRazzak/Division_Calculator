from dataclasses import dataclass
from typing import Any, Dict
from .equipment import Equipment


@dataclass
class TemplateItem:
  equipment: Equipment
  count_per_unit: float

  def to_dict(self) -> Dict[str, Any]:
    return {
        "equipment": self.equipment.to_dict(),
        "count_per_unit": self.count_per_unit,
    }

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "TemplateItem":
    return cls(
        equipment=Equipment.from_dict(data["equipment"]),
        count_per_unit=float(data["count_per_unit"]),
    )