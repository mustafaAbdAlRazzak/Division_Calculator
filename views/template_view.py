from typing import Callable, List, Optional
import flet as ft

from entities.design_template import DesignTemplate
from entities.equipment import Equipment
from entities.template_item import TemplateItem


class TemplateView(ft.UserControl):
    """لوحة بناء وإدارة نماذج التصميم مهيأة لشاشات الهواتف الذكية (وضع طولي) باستخدام مكتبة Flet[cite: 7]."""

    def __init__(
        self,
        templates_list: List[DesignTemplate],
        equipment_list: List[Equipment],
        on_changed_callback: Optional[Callable[[], None]] = None,
        is_template_used_callback: Optional[Callable[[str], bool]] = None,
    ):
        super().__init__()
        self.templates_list = templates_list
        self.equipment_list = equipment_list
        self.on_changed_callback = on_changed_callback
        self.is_template_used_callback = is_template_used_callback

        self.editing_template_original_name: Optional[str] = None
        self.current_builder_items: List[TemplateItem] = []

        # حقول الإدخال والتحكم الخاصة بالبناء[cite: 7]
        self.entry_template_name = ft.TextField(
            label="Template Name",
            hint_text="e.g. Armored Division 40cw",
            border_radius=8
        )
        self.menu_type = ft.Dropdown(
            label="Type",
            options=[
                ft.dropdown.Option("LAND_DIVISION"),
                ft.dropdown.Option("NAVAL_SHIP"),
                ft.dropdown.Option("AIRCRAFT"),
            ],
            value="LAND_DIVISION",
            border_radius=8
        )

        self.menu_equipment = ft.Dropdown(
            label="Select Equipment",
            options=[ft.dropdown.Option("No Equipment Available")],
            value="No Equipment Available",
            border_radius=8
        )
        self.entry_count = ft.TextField(
            label="Count per Unit",
            hint_text="e.g. 50",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8
        )

        # حاويات عرض العناصر والأسطر المتسلسلة[cite: 7]
        self.builder_items_column = ft.Column(spacing=8)
        self.templates_rows_column = ft.Column(spacing=8)

        self.btn_save_template = ft.ElevatedButton(
            text="Save Template",
            icon=ft.icons.SAVE,
            bgcolor=ft.colors.GREEN_700,
            color=ft.colors.WHITE,
            on_click=lambda e: self._save_template(),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )

    def build(self):
        """إنشاء الهيكل الطولي المتجاوب للوحة بناء وإدارة النماذج[cite: 7]."""
        
        # 1. لوحة بناء النموذج (Builder Panel)
        builder_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🏗️ Template Builder", size=16, weight=ft.FontWeight.BOLD),
                    self.entry_template_name,
                    self.menu_type,
                    ft.Divider(height=1),
                    ft.Text("Add Equipment to Template", size=13, weight=ft.FontWeight.BOLD),
                    self.menu_equipment,
                    self.entry_count,
                    ft.ElevatedButton(
                        text="Add Item",
                        icon=ft.icons.ADD,
                        on_click=lambda e: self._add_item_to_builder(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                    ft.Divider(height=1),
                    ft.Text("Current Items", size=13, weight=ft.FontWeight.BOLD),
                    self.builder_items_column,
                    self.btn_save_template
                ], spacing=10),
                padding=15
            ),
            elevation=2
        )

        # 2. لوحة النماذج المحفوظة (Saved Templates List Panel)
        list_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📋 Saved Design Templates", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    self.templates_rows_column
                ], spacing=10),
                padding=15
            ),
            elevation=2
        )

        # حاوية رئيسية قابلة للتمرير رأسياً لتناسب شاشات الهواتف الطولية[cite: 7]
        return ft.ListView([
            builder_card,
            list_card
        ], expand=True, spacing=12, padding=10)

    def did_mount(self):
        """تحميل البيانات الأولية عند ظهور المكون على الشاشة[cite: 7]."""
        self._refresh_equipment_dropdown()
        self._refresh_templates_table()

    def _refresh_equipment_dropdown(self):
        """تحديث خيارات المعدات من القائمة العامة للنظام[cite: 7]."""
        if not self.equipment_list:
            self.menu_equipment.options = [ft.dropdown.Option("No Equipment Available")]
            self.menu_equipment.value = "No Equipment Available"
        else:
            eq_options = [f"{e.name} ({e.id})" for e in self.equipment_list]
            self.menu_equipment.options = [ft.dropdown.Option(opt) for opt in eq_options]
            self.menu_equipment.value = eq_options[0]
        if self.page:
            self.update()

    def _refresh_builder_items_table(self):
        """إعادة بناء قائمة عناصر النموذج قيد الإنشاء[cite: 7]."""
        self.builder_items_column.controls.clear()
        if not self.current_builder_items:
            self.builder_items_column.controls.append(
                ft.Text("No items added yet.", italic=True, color=ft.colors.GREY, size=12)
            )
        else:
            for idx, item in enumerate(self.current_builder_items):
                row = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(item.equipment.name, weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(f"Count: {item.count_per_unit:.1f}", size=12, color=ft.colors.GREY_700)
                        ], spacing=2, expand=True),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            icon_color=ft.colors.RED,
                            icon_size=20,
                            on_click=lambda e, i=idx: self._remove_builder_item(i)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                    padding=8,
                    border_radius=6
                )
                self.builder_items_column.controls.append(row)
        if self.page:
            self.update()

    def _refresh_templates_table(self):
        """إعادة بناء بطاقات النماذج المحفوظة[cite: 7]."""
        self.templates_rows_column.controls.clear()
        if not self.templates_list:
            self.templates_rows_column.controls.append(
                ft.Text("No templates saved yet.", italic=True, color=ft.colors.GREY, size=12)
            )
        else:
            for tmpl in self.templates_list:
                card_row = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(tmpl.name, weight=ft.FontWeight.BOLD, size=14),
                            ft.Container(
                                content=ft.Text(tmpl.type, size=10, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.colors.BLUE_GREY_700,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                border_radius=4
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"Items Count: {len(tmpl.items)}", size=12, color=ft.colors.GREY_700),
                        ft.Row([
                            ft.TextButton("Edit", icon=ft.icons.EDIT, on_click=lambda e, t=tmpl: self._edit_template(t)),
                            ft.TextButton("Delete", icon=ft.icons.DELETE, icon_color=ft.colors.RED, text_color=ft.colors.RED, on_click=lambda e, t_name=tmpl.name: self._delete_template(t_name))
                        ], alignment=ft.MainAxisAlignment.END, spacing=0)
                    ], spacing=6),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                    padding=10,
                    border_radius=6
                )
                self.templates_rows_column.controls.append(card_row)
        if self.page:
            self.update()

    def _add_item_to_builder(self):
        """إضافة المعدات المحددة والكمية إلى منشئ النماذج مع التحقق[cite: 7]."""
        selected_option = self.menu_equipment.value
        count_raw = (self.entry_count.value or "").strip()

        if not self.equipment_list or selected_option == "No Equipment Available":
            self._show_dialog("Warning", "No equipment available to add.")
            return

        if not count_raw:
            self._show_dialog("Input Error", "Please enter 'Count per Unit'.")
            return

        try:
            count = float(count_raw)
            if count <= 0:
                self._show_dialog("Value Error", "Count per Unit must be a positive number.")
                return
        except ValueError:
            self._show_dialog("Invalid Input", "Count per Unit must be a valid number.")
            return

        eq_id = selected_option.split("(")[-1].rstrip(")")
        equipment = next((e for e in self.equipment_list if e.id == eq_id), None)

        if not equipment:
            self._show_dialog("Error", "Selected equipment was not found.")
            return

        existing = next((i for i in self.current_builder_items if i.equipment.id == eq_id), None)
        if existing:
            existing.count_per_unit = count
        else:
            self.current_builder_items.append(TemplateItem(equipment=equipment, count_per_unit=count))

        self.entry_count.value = ""
        self._refresh_builder_items_table()

    def _remove_builder_item(self, idx: int):
        """إزالة عنصر من قائمة البناء الحالية[cite: 7]."""
        if 0 <= idx < len(self.current_builder_items):
            self.current_builder_items.pop(idx)
            self._refresh_builder_items_table()

    def _edit_template(self, tmpl: DesignTemplate):
        """تحميل نموذج موجود إلى المنشئ لتعديله[cite: 7]."""
        self.editing_template_original_name = tmpl.name
        self.entry_template_name.value = tmpl.name
        self.menu_type.value = tmpl.type

        self.current_builder_items = [
            TemplateItem(equipment=item.equipment, count_per_unit=item.count_per_unit)
            for item in tmpl.items
        ]
        self._refresh_builder_items_table()

    def _save_template(self):
        """حفظ النموذج المُنشأ في قائمة النماذج مع التحقق الكامل[cite: 7]."""
        name = (self.entry_template_name.value or "").strip()
        tmpl_type = self.menu_type.value

        if not name:
            self._show_dialog("Validation Error", "Please enter a 'Template Name'.")
            return

        if not self.current_builder_items:
            self._show_dialog("Validation Error", "Template must contain at least one equipment item.")
            return

        existing = next(
            (t for t in self.templates_list if t.name == name and t.name != self.editing_template_original_name),
            None,
        )
        if existing:
            self._show_dialog("Duplicate Name", f"A template named '{name}' already exists.")
            return

        if self.editing_template_original_name:
            target_tmpl = next(
                (t for t in self.templates_list if t.name == self.editing_template_original_name), None
            )
            if target_tmpl:
                target_tmpl.name = name
                target_tmpl.type = tmpl_type
                target_tmpl.items = list(self.current_builder_items)
        else:
            new_tmpl = DesignTemplate(
                name=name, type=tmpl_type, items=list(self.current_builder_items)
            )
            self.templates_list.append(new_tmpl)

        self.entry_template_name.value = ""
        self.editing_template_original_name = None
        self.current_builder_items.clear()
        self._refresh_builder_items_table()
        self._refresh_templates_table()

        if self.on_changed_callback:
            self.on_changed_callback()

    def _delete_template(self, tmpl_name: str):
        """حذف نموذج التصميم بالاسم مع التحقق من الأمان وعرض نافذة تأكيد[cite: 7]."""
        if self.is_template_used_callback and self.is_template_used_callback(tmpl_name):
            self._show_dialog(
                "Action Blocked",
                f"Cannot delete template '{tmpl_name}' because it is currently used in one or more Production Orders."
            )
            return

        def close_dialog(e):
            dlg.open = False
            if self.page:
                self.page.update()

        def confirm_delete(e):
            dlg.open = False
            if self.page:
                self.page.update()
            self.templates_list[:] = [t for t in self.templates_list if t.name != tmpl_name]
            self._refresh_templates_table()
            if self.on_changed_callback:
                self.on_changed_callback()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete template '{tmpl_name}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Delete", text_color=ft.colors.RED, on_click=confirm_delete),
            ],
        )
        if self.page:
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

    def _show_dialog(self, title: str, message: str):
        """عرض رسائل التنبيه والخطأ المنبثقة[cite: 7]."""
        if not self.page:
            return
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self._close_dialog(dlg))]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _close_dialog(self, dlg):
        dlg.open = False
        if self.page:
            self.page.update()

    def refresh_view(self):
        """تحديث خيارات المعدات وجدول النماذج من الخارج[cite: 7]."""
        self._refresh_equipment_dropdown()
        self._refresh_templates_table()