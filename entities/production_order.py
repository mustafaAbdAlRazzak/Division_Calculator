from dataclasses import dataclass
from typing import Any, Dict
from .design_template import DesignTemplate
from .production_rate import ProductionRate


@dataclass
class ProductionOrder:
  id: str
  template: DesignTemplate
  rate: ProductionRate
  is_active: bool = True

  def to_dict(self) -> Dict[str, Any]:
    return {
        "id": self.id,
        "template": self.template.to_dict(),
        "rate": self.rate.to_dict(),
        "is_active": self.is_active,
    }

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "ProductionOrder":
    return cls(
        id=data["id"],
        template=DesignTemplate.from_dict(data["template"]),
        rate=ProductionRate.from_dict(data["rate"]),
        is_active=data.get("is_active", True),
    )