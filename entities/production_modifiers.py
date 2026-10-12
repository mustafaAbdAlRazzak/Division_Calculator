from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ProductionModifiers:
  base_military_factory_output: float = 5.0
  factory_efficiency: float = 1.0  # 1.0 = 100%
  land_production_bonus: float = 0.0  # 0.15 = +15%
  base_dockyard_output: float = 2.5
  naval_production_bonus: float = 0.0  # 0.10 = +10%

  def get_effective_military_output(self) -> float:
    return (
        self.base_military_factory_output
        * self.factory_efficiency
        * (1.0 + self.land_production_bonus)
    )

  def get_effective_dockyard_output(self) -> float:
    return self.base_dockyard_output * (1.0 + self.naval_production_bonus)

  def to_dict(self) -> Dict[str, Any]:
    return {
        "base_military_factory_output": self.base_military_factory_output,
        "factory_efficiency": self.factory_efficiency,
        "land_production_bonus": self.land_production_bonus,
        "base_dockyard_output": self.base_dockyard_output,
        "naval_production_bonus": self.naval_production_bonus,
    }

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "ProductionModifiers":
    return cls(
        base_military_factory_output=float(
            data.get("base_military_factory_output", 5.0)
        ),
        factory_efficiency=float(data.get("factory_efficiency", 1.0)),
        land_production_bonus=float(data.get("land_production_bonus", 0.0)),
        base_dockyard_output=float(data.get("base_dockyard_output", 2.5)),
        naval_production_bonus=float(data.get("naval_production_bonus", 0.0)),
    )