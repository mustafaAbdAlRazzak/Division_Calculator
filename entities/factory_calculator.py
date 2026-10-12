from dataclasses import dataclass
from typing import Any, Dict, List
from .production_modifiers import ProductionModifiers
from .production_order import ProductionOrder


@dataclass
class FactoryCalculator:

  @staticmethod
  def calculate_required_facilities(
      orders: List[ProductionOrder], modifiers: ProductionModifiers
  ) -> Dict[str, Any]:
    mil_output = modifiers.get_effective_military_output()
    dock_output = modifiers.get_effective_dockyard_output()

    total_military_factories = 0.0
    total_dockyards = 0.0
    order_results = []
    equipment_totals = {}

    for order in orders:
      if not order.is_active:
        continue

      daily_rate = order.rate.get_daily_rate()
      order_mil_facs = 0.0
      order_docks = 0.0

      for item in order.template.items:
        eq = item.equipment
        daily_cost = (
            item.count_per_unit * eq.base_production_cost * daily_rate
        )

        if eq.category.upper() == "NAVAL":
          facs = daily_cost / dock_output if dock_output > 0 else 0.0
          order_docks += facs
        else:
          facs = daily_cost / mil_output if mil_output > 0 else 0.0
          order_mil_facs += facs

        if eq.id not in equipment_totals:
          equipment_totals[eq.id] = {
              "name": eq.name,
              "category": eq.category,
              "total_facilities": 0.0,
          }
        equipment_totals[eq.id]["total_facilities"] += facs

      total_military_factories += order_mil_facs
      total_dockyards += order_docks

      order_results.append({
          "order_id": order.id,
          "template_name": order.template.name,
          "template_type": order.template.type,
          "military_factories": order_mil_facs,
          "dockyards": order_docks,
      })

    return {
        "order_results": order_results,
        "equipment_breakdown": equipment_totals,
        "total_military_factories": total_military_factories,
        "total_dockyards": total_dockyards,
    }
    