from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ProductionRate:
  value: float
  unit: str  # "DAILY", "WEEKLY", "MONTHLY", "YEARLY"

  def get_daily_rate(self) -> float:
    unit_upper = self.unit.upper()
    if unit_upper == "DAILY":
      return self.value
    elif unit_upper == "WEEKLY":
      return self.value / 7.0
    elif unit_upper == "MONTHLY":
      return self.value / 30.0
    elif unit_upper == "YEARLY":
      return self.value / 365.0
    return self.value

  def to_dict(self) -> Dict[str, Any]:
    return {
        "value": self.value,
        "unit": self.unit,
    }

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "ProductionRate":
    return cls(value=float(data["value"]), unit=data["unit"])