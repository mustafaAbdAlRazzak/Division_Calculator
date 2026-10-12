import json
import os
from typing import List, Tuple

from entities.equipment import Equipment
from entities.design_template import DesignTemplate
from entities.production_order import ProductionOrder
from entities.production_modifiers import ProductionModifiers


class JSONStorage:

  @staticmethod
  def save_to_file(
      filepath: str,
      equipment_list: List[Equipment],
      templates_list: List[DesignTemplate],
      orders_list: List[ProductionOrder],
      modifiers: ProductionModifiers,
  ) -> Tuple[bool, str]:
    """حفظ كافة بيانات النظام في ملف JSON باستدعاء to_dict لكل كائن."""
    try:
      full_payload = {
          "equipment": [e.to_dict() for e in equipment_list],
          "templates": [t.to_dict() for t in templates_list],
          "orders": [o.to_dict() for o in orders_list],
          "modifiers": (
              modifiers.to_dict()
              if hasattr(modifiers, "to_dict")
              else {
                  "base_military_factory_output": getattr(
                      modifiers, "base_military_factory_output", 4.5
                  ),
                  "factory_efficiency": getattr(
                      modifiers, "factory_efficiency", 1.0
                  ),
                  "land_production_bonus": getattr(
                      modifiers, "land_production_bonus", 0.0
                  ),
                  "base_dockyard_output": getattr(
                      modifiers, "base_dockyard_output", 2.5
                  ),
                  "naval_production_bonus": getattr(
                      modifiers, "naval_production_bonus", 0.0
                  ),
              }
          ),
      }

      dir_name = os.path.dirname(filepath)
      if dir_name:
        os.makedirs(dir_name, exist_ok=True)

      with open(filepath, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, indent=2, ensure_ascii=False)

      return True, f"Saved successfully to {filepath}"

    except Exception as e:
      return False, f"Failed to save data: {str(e)}"

  @staticmethod
  def load_from_file(
      filepath: str,
  ) -> Tuple[
      List[Equipment],
      List[DesignTemplate],
      List[ProductionOrder],
      ProductionModifiers,
      str,
  ]:
    """تحميل كافة البيانات من ملف JSON باستدعاء from_dict لكل كائن."""
    if not os.path.exists(filepath):
      return [], [], [], ProductionModifiers(), f"File not found: {filepath}"

    try:
      with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

      # 1. Equipment
      equipment_list = [
          Equipment.from_dict(item) for item in data.get("equipment", [])
      ]

      # 2. Templates
      templates_list = [
          DesignTemplate.from_dict(item) for item in data.get("templates", [])
      ]

      # 3. Orders
      orders_list = [
          ProductionOrder.from_dict(item) for item in data.get("orders", [])
      ]

      # 4. Modifiers
      mods_data = data.get("modifiers", {})
      if hasattr(ProductionModifiers, "from_dict"):
        modifiers = ProductionModifiers.from_dict(mods_data)
      else:
        modifiers = ProductionModifiers()
        modifiers.base_military_factory_output = float(
            mods_data.get("base_military_factory_output", 4.5)
        )
        modifiers.factory_efficiency = float(
            mods_data.get("factory_efficiency", 1.0)
        )
        modifiers.land_production_bonus = float(
            mods_data.get("land_production_bonus", 0.0)
        )
        modifiers.base_dockyard_output = float(
            mods_data.get("base_dockyard_output", 2.5)
        )
        modifiers.naval_production_bonus = float(
            mods_data.get("naval_production_bonus", 0.0)
        )

      return (
          equipment_list,
          templates_list,
          orders_list,
          modifiers,
          "Data loaded successfully.",
      )

    except Exception as e:
      return [], [], [], ProductionModifiers(), f"Failed to load data: {str(e)}"