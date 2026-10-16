from typing import Callable, List, Optional
import flet as ft
from entities.equipment import Equipment


class EquipmentView(ft.Control):
    """مكون إدارة المعدات مصمم خصيصاً لشاشات الهواتف الذكية (وضع طولي) باستخدام مكتبة Flet."""

    def __init__(
        self,
        equipment_list: List[Equipment],
        on_changed_callback: Optional[Callable[[], None]] = None,
        is_equipment_used_callback: Optional[Callable[[str], bool]] = None,
    ):
        super().__init__()
        self.equipment_list = equipment_list
        self.on_changed_callback = on_changed_callback
        self.is_equipment_used_callback = is_equipment_used_callback

        self.editing_equipment_id: Optional[str] = None

        # عناصر حقول الإدخال مهيأة للمس وسياق الهواتف
        self.name_field = ft.TextField(
            label="Name", 
            hint_text="e.g. Infantry Rifle", 
            border_radius=8
        )
        
        self.category_dropdown = ft.Dropdown(
            label="Category",
            value="LAND",
            options=[
                ft.dropdown.Option("LAND"),
                ft.dropdown.Option("NAVAL"),
            ],
            border_radius=8
        )
        
        self.cost_field = ft.TextField(
            label="Base Cost", 
            hint_text="e.g. 0.5", 
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8
        )

        # أزرار الإجراءات بحجم مناسب لشاشات اللمس
        self.btn_add = ft.ElevatedButton(
            text="Add Equipment",
            icon=ft.icons.ADD,
            on_click=self._add_or_save_equipment,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        
        self.btn_cancel = ft.OutlinedButton(
            text="Cancel",
            on_click=lambda e: self._cancel_editing(),
            visible=False,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )

        # قائمة عرض العناصر بشكل بطاقات عمودية (Cards)
        self.equipment_list_view = ft.ListView(expand=1, spacing=10, padding=10)

    def build(self):
        # لوحة الإدخال العلوية (تم ترتيبها رأسياً لتلائم الهواتف الطولية)
        form_container = ft.Container(
            content=ft.Column([
                ft.Text("Equipment Management", size=18, weight=ft.FontWeight.BOLD),
                self.name_field,
                self.category_dropdown,
                self.cost_field,
                ft.Row([self.btn_add, self.btn_cancel], spacing=10)
            ], spacing=12),
            padding=15,
            border_radius=12,
            margin=ft.margin.all(10)
        )

        # الهيكل الرئيسي للتطبيق (Layout)
        return ft.Column([
            form_container,
            ft.Divider(height=1),
            ft.Container(
                content=self.equipment_list_view,
                expand=True,
                padding=5
            )
        ], expand=True)

    def did_mount(self):
        """يتم استدعاؤها عند تحميل المكون لعرض القائمة"""
        self._refresh_table()

    def _refresh_table(self):
        """إعادة بناء البطاقات العمودية بناءً على قائمة المعدات"""
        self.equipment_list_view.controls.clear()

        if not self.equipment_list:
            self.equipment_list_view.controls.append(
                ft.Container(
                    content=ft.Text("No equipment items added.", italic=True, color=ft.colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for item in self.equipment_list:
                # تصميم بطاقة مستقلة لكل عنصر (تجنب جداول سطح المكتب الواسعة)
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(item.name, weight=ft.FontWeight.BOLD, size=16),
                                ft.Container(
                                    content=ft.Text(item.category, size=11, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                                    bgcolor=ft.colors.BLUE_GREY_700,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    border_radius=4
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            
                            ft.Text(f"Base Cost: {item.base_production_cost:.2f}", color=ft.colors.GREY_700, size=13),
                            
                            ft.Row([
                                ft.TextButton("Edit", icon=ft.icons.EDIT, on_click=lambda e, eq=item: self._edit_equipment(eq)),
                                ft.TextButton("Delete", icon=ft.icons.DELETE, icon_color=ft.colors.RED, text_color=ft.colors.RED, on_click=lambda e, eq_id=item.id: self._delete_equipment(eq_id))
                            ], alignment=ft.MainAxisAlignment.END, spacing=0)
                        ], spacing=6),
                        padding=12
                    ),
                    elevation=2
                )
                self.equipment_list_view.controls.append(card)

        if self.page:
            self.update()

    def _add_or_save_equipment(self, e):
        """التحقق من البيانات وإضافة أو حفظ التعديل"""
        name = self.name_field.value.strip() if self.name_field.value else ""
        category = self.category_dropdown.value
        cost_raw = self.cost_field.value.strip() if self.cost_field.value else ""

        if not name or not cost_raw:
            self._show_dialog("Input Error", "Both Name and Base Cost are required.")
            return

        try:
            cost = float(cost_raw)
            if cost <= 0:
                self._show_dialog("Value Error", "Base Production Cost must be greater than zero.")
                return
        except ValueError:
            self._show_dialog("Invalid Input", "Base Production Cost must be a valid number.")
            return

        if self.editing_equipment_id:
            eq = next((item for item in self.equipment_list if item.id == self.editing_equipment_id), None)
            if eq:
                eq.name = name
                eq.category = category
                eq.base_production_cost = cost
            self._cancel_editing()
        else:
            new_eq = Equipment(name=name, category=category, base_production_cost=cost)
            self.equipment_list.append(new_eq)
            self._clear_entries()

        self._refresh_table()
        if self.on_changed_callback:
            self.on_changed_callback()

    def _edit_equipment(self, eq: Equipment):
        """تعبئة الحقول ببيانات العنصر المحدد للتعديل"""
        self.editing_equipment_id = eq.id
        self.name_field.value = eq.name
        self.category_dropdown.value = eq.category
        self.cost_field.value = str(eq.base_production_cost)
        
        self.btn_add.text = "Save Changes"
        self.btn_add.icon = ft.icons.SAVE
        self.btn_add.bgcolor = ft.colors.GREEN_700
        self.btn_cancel.visible = True
        self.update()

    def _cancel_editing(self):
        """إلغاء وضع التعديل وإعادة الحقول لوضع الإضافة"""
        self.editing_equipment_id = None
        self._clear_entries()
        
        self.btn_add.text = "Add Equipment"
        self.btn_add.icon = ft.icons.ADD
        self.btn_add.bgcolor = None
        self.btn_cancel.visible = False
        self.update()

    def _clear_entries(self):
        """تفريغ مربعات النص"""
        self.name_field.value = ""
        self.cost_field.value = ""
        self.category_dropdown.value = "LAND"
        self.update()

    def _delete_equipment(self, eq_id: str):
        """حذف العنصر مع التحقق من عدم استخدامه وعرض نافذة تأكيد"""
        if self.is_equipment_used_callback and self.is_equipment_used_callback(eq_id):
            self._show_dialog(
                "Action Blocked",
                "Cannot delete equipment because it is actively used in Design Templates or Production Orders."
            )
            return

        def close_dialog(e):
            dlg.open = False
            self.page.update()

        def confirm_delete(e):
            dlg.open = False
            self.page.update()
            self.equipment_list[:] = [item for item in self.equipment_list if item.id != eq_id]
            self._refresh_table()
            if self.on_changed_callback:
                self.on_changed_callback()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this equipment item?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Delete", text_color=ft.colors.RED, on_click=confirm_delete),
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _show_dialog(self, title: str, message: str):
        """عرض رسائل التنبيه والخطأ"""
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
        self.page.update()