from dataclasses import dataclass, field
from typing import Any, Dict, List
from .template_item import TemplateItem


@dataclass
class DesignTemplate:
  name: str
  type: str  # "LAND_DIVISION", "NAVAL_SHIP", "AIRCRAFT"
  items: List[TemplateItem] = field(default_factory=list)

  def to_dict(self) -> Dict[str, Any]:
    return {
        "name": self.name,
        "type": self.type,
        "items": [item.to_dict() for item in self.items],
    }

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "DesignTemplate":
    items = [TemplateItem.from_dict(item) for item in data.get("items", [])]
    return cls(name=data["name"], type=data["type"], items=items)