import os
from typing import List
import flet as ft

from entities.design_template import DesignTemplate
from entities.equipment import Equipment
from entities.factory_calculator import FactoryCalculator
from entities.production_modifiers import ProductionModifiers
from entities.production_order import ProductionOrder
from storage.json_storage import JSONStorage

# استدعاء الواجهات الفرعية المحولة مسبقاً لمكتبة Flet
from views.equipment_view import EquipmentView
from views.template_view import TemplateView
from views.production_order_view import ProductionOrderView
from views.modifiers_view import ModifiersView
from views.results_view import ResultsView


def main(page: ft.Page):
    page.title = "Military Division & Production Factory Calculator"
    page.theme_mode = ft.ThemeMode.DARK
    
    # محاكاة أبعاد شاشة الهاتف المحمول (وضع طولي عمودي) مع إمكانية التمدد
    page.window_width = 400
    page.window_height = 800
    page.window_resizable = True
    page.padding = 0

    # الحالة البرمجية في الذاكرة (State Data In-Memory)[cite: 8]
    equipment_list: List[Equipment] = []
    templates_list: List[DesignTemplate] = []
    orders_list: List[ProductionOrder] = []
    modifiers = ProductionModifiers()

    # شريط الحالة السفلي (Status Bar)[cite: 8]
    lbl_status = ft.Text(
        "Auto-Save Enabled",
        italic=True,
        size=12,
        color=ft.colors.GREY_700
    )

    def set_status(message: str, is_error: bool = False):
        """تحديث نص وحالة شريط الإشعارات السفلي[cite: 8]."""
        lbl_status.value = message
        lbl_status.color = ft.colors.RED_ACCENT if is_error else ft.colors.GREY_700
        if page:
            page.update()

    def _is_equipment_used(eq_id: str) -> bool:
        """التحقق مما إذا كانت المعدات مستخدمة في أي نموذج تصميم أو أمر إنتاج[cite: 8]."""
        for tmpl in templates_list:
            for item in tmpl.items:
                if item.equipment and item.equipment.id == eq_id:
                    return True

        for order in orders_list:
            if hasattr(order, "template") and order.template:
                for item in order.template.items:
                    if item.equipment and item.equipment.id == eq_id:
                        return True
        return False

    def _is_template_used(tmpl_name: str) -> bool:
        """التحقق مما إذا كان نموذج التصميم مستخدماً في أي أمر إنتاج[cite: 8]."""
        for order in orders_list:
            if order.template and order.template.name == tmpl_name:
                return True
        return False

    # دوال الحسابات والحفظ التلقائي[cite: 8]
    def calculate_all():
        """تشغيل محرك الحسابات FactoryCalculator وتحديث واجهة النتائج[cite: 8]."""
        view_modifiers.sync_modifiers_from_ui()
        calc_data = FactoryCalculator.calculate_required_facilities(
            orders=orders_list, modifiers=modifiers
        )
        view_results.display_results(calc_data)

    def auto_save_data():
        """حفظ التغييرات تلقائياً في ملف JSON[cite: 8]."""
        view_modifiers.sync_modifiers_from_ui()
        success, msg = JSONStorage.save_to_file(
            filepath="app_state.json",
            equipment_list=equipment_list,
            templates_list=templates_list,
            orders_list=orders_list,
            modifiers=modifiers,
        )
        if success:
            set_status("Auto-saved successfully.", is_error=False)
        else:
            set_status(f"Auto-save error: {msg}", is_error=True)

    def _on_equipment_changed():
        """يتم تفعيلها عند أي تغيير في كتالوج المعدات[cite: 8]."""
        view_template.refresh_view()
        calculate_all()
        auto_save_data()

    def _on_templates_changed():
        """يتم تفعيلها عند أي تغيير في نماذج التصميم[cite: 8]."""
        view_orders.refresh_view()
        calculate_all()
        auto_save_data()

    def _on_orders_changed():
        """يتم تفعيلها عند أي تغيير في أوامر الإنتاج[cite: 8]."""
        calculate_all()
        auto_save_data()

    def _on_trigger_calculation():
        """يتم تفعيلها عند النقر على زر الحساب في لوحة المعاملات[cite: 8]."""
        calculate_all()
        auto_save_data()

    # تهيئة واجهات العرض الفرعية[cite: 8]
    view_equipment = EquipmentView(
        equipment_list=equipment_list,
        on_changed_callback=_on_equipment_changed,
        is_equipment_used_callback=_is_equipment_used,
    )

    view_template = TemplateView(
        templates_list=templates_list,
        equipment_list=equipment_list,
        on_changed_callback=_on_templates_changed,
        is_template_used_callback=_is_template_used,
    )

    view_orders = ProductionOrderView(
        orders_list=orders_list,
        templates_list=templates_list,
        on_changed_callback=_on_orders_changed,
    )

    view_modifiers = ModifiersView(
        modifiers=modifiers,
        on_calculate_callback=_on_trigger_calculation,
    )

    view_results = ResultsView()

    # نظام التبويبات الرئيسي (Tabs) الملائم للشاشات العمودية في الهواتف[cite: 8]
    tabs_view = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        expand=True,
        tabs=[
            ft.Tab(text="Equipment", content=view_equipment),
            ft.Tab(text="Templates", content=view_template),
            ft.Tab(text="Orders", content=view_orders),
            ft.Tab(text="Modifiers", content=view_modifiers),
            ft.Tab(text="Results", content=view_results),
        ],
    )

    # الشريط السفلي لعرض الحالة[cite: 8]
    bottom_bar = ft.Container(
        content=lbl_status,
        padding=ft.padding.symmetric(horizontal=15, vertical=8),
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    # تجميع العناصر في الصفحة الرئيسية
    page.add(
        ft.Column([
            ft.Container(content=tabs_view, expand=True),
            bottom_bar
        ], expand=True, spacing=0)
    )

    def auto_load_data():
        """تحميل الحالة السابقة تلقائياً عند بدء تشغيل التطبيق[cite: 8]."""
        if not os.path.exists("app_state.json"):
            calculate_all()
            set_status("Ready (New State)", is_error=False)
            return

        eq_list, tmpl_list, ord_list, mods, msg = JSONStorage.load_from_file("app_state.json")
        if eq_list is not None:
            equipment_list.clear()
            equipment_list.extend(eq_list)

            templates_list.clear()
            templates_list.extend(tmpl_list)

            orders_list.clear()
            orders_list.extend(ord_list)

            modifiers.base_military_factory_output = mods.base_military_factory_output
            modifiers.factory_efficiency = mods.factory_efficiency
            modifiers.land_production_bonus = mods.land_production_bonus
            modifiers.base_dockyard_output = mods.base_dockyard_output
            modifiers.naval_production_bonus = mods.naval_production_bonus

            # تحديث الواجهات الفرعية[cite: 8]
            if hasattr(view_equipment, "refresh_view"):
                view_equipment.refresh_view()
            elif hasattr(view_equipment, "_refresh_table"):
                view_equipment._refresh_table()

            view_template.refresh_view()
            view_orders.refresh_view()
            view_modifiers.refresh_view()

            calculate_all()
            set_status("Auto-loaded previous session data.", is_error=False)
        else:
            calculate_all()
            set_status(msg, is_error=True)

    # تنفيذ التحميل التلقائي عند بدء التشغيل[cite: 8]
    auto_load_data()


if __name__ == "__main__":
    ft.app(target=main)