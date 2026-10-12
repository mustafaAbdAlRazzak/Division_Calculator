from typing import Callable, List, Optional
import flet as ft

from entities.design_template import DesignTemplate
from entities.production_order import ProductionOrder
from entities.production_rate import ProductionRate


class ProductionOrderView(ft.UserControl):
    """لوحة أوامر الإنتاج مهيأة لشاشات الهواتف الذكية (وضع طولي) باستخدام مكتبة Flet[cite: 4]."""

    def __init__(
        self,
        orders_list: List[ProductionOrder],
        templates_list: List[DesignTemplate],
        on_changed_callback: Optional[Callable[[], None]] = None,
        is_order_used_callback: Optional[Callable[[str], bool]] = None,
    ):
        super().__init__()
        self.orders_list = orders_list
        self.templates_list = templates_list
        self.on_changed_callback = on_changed_callback
        self.is_order_used_callback = is_order_used_callback

        self.editing_order_id: Optional[str] = None

        # عناصر حقول الإدخال مهيأة للمس وسياق الهواتف
        self.entry_order_id = ft.TextField(
            label="Order ID",
            hint_text="e.g. order_inf_1",
            border_radius=8
        )
        
        self.menu_template = ft.Dropdown(
            label="Select Template",
            options=[ft.dropdown.Option("No Templates Available")],
            value="No Templates Available",
            border_radius=8
        )
        
        self.entry_rate_value = ft.TextField(
            label="Rate Value",
            hint_text="e.g. 1.0",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8
        )
        
        self.menu_unit = ft.Dropdown(
            label="Time Horizon",
            options=[
                ft.dropdown.Option("DAILY"),
                ft.dropdown.Option("WEEKLY"),
                ft.dropdown.Option("MONTHLY"),
                ft.dropdown.Option("YEARLY"),
            ],
            value="WEEKLY",
            border_radius=8
        )

        # أزرار الإجراءات بحجم مناسب لشاشات اللمس
        self.btn_add_order = ft.ElevatedButton(
            text="Create Order",
            icon=ft.icons.ADD,
            on_click=self._add_or_save_order,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        
        self.btn_cancel_edit = ft.OutlinedButton(
            text="Cancel",
            on_click=lambda e: self._cancel_editing(),
            visible=False,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )

        # قائمة عرض الأوامر بشكل بطاقات عمودية (Cards)
        self.orders_list_view = ft.ListView(expand=1, spacing=10, padding=10)

    def build(self):
        """إنشاء الهيكل الطولي للوحة الأوامر بنظام البطاقات[cite: 4]."""
        form_container = ft.Container(
            content=ft.Column([
                ft.Text("Production Orders Management", size=18, weight=ft.FontWeight.BOLD),
                self.entry_order_id,
                self.menu_template,
                self.entry_rate_value,
                self.menu_unit,
                ft.Row([self.btn_add_order, self.btn_cancel_edit], spacing=10)
            ], spacing=12),
            padding=15,
            border_radius=12,
            margin=ft.margin.all(10)
        )

        return ft.Column([
            form_container,
            ft.Divider(height=1),
            ft.Container(
                content=self.orders_list_view,
                expand=True,
                padding=5
            )
        ], expand=True)

    def did_mount(self):
        """تحميل القوائم والبيانات عند ظهور المكون على الشاشة[cite: 4]."""
        self._refresh_template_dropdown()
        self._refresh_table()

    def _refresh_template_dropdown(self):
        """تحديث قائمة النماذج المتاحة[cite: 4]."""
        if not self.templates_list:
            self.menu_template.options = [ft.dropdown.Option("No Templates Available")]
            self.menu_template.value = "No Templates Available"
        else:
            names = [t.name for t in self.templates_list]
            self.menu_template.options = [ft.dropdown.Option(name) for name in names]
            if not self.editing_order_id:
                self.menu_template.value = names[0]
        if self.page:
            self.update()

    def _refresh_table(self):
        """إعادة بناء البطاقات العمودية لأوامر الإنتاج[cite: 4]."""
        self.orders_list_view.controls.clear()

        if not self.orders_list:
            self.orders_list_view.controls.append(
                ft.Container(
                    content=ft.Text("No production orders added.", italic=True, color=ft.colors.GREY),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for order in self.orders_list:
                rate_str = f"{order.rate.value:.2f} / {order.rate.unit}"
                daily_str = f"{order.rate.get_daily_rate():.4f} / day"

                switch_active = ft.Switch(
                    value=order.is_active,
                    on_change=lambda e, o=order: self._toggle_order_active(o, e.control.value)
                )

                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(order.id, weight=ft.FontWeight.BOLD, size=16),
                                ft.Row([
                                    ft.Text("Active:", size=12, color=ft.colors.GREY_700),
                                    switch_active
                                ], spacing=5)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                            ft.Text(f"Template: {order.template.name}", size=13, weight=ft.FontWeight.W_500),
                            ft.Text(f"Target Rate: {rate_str}", color=ft.colors.GREY_700, size=12),
                            ft.Text(f"Normalized Daily: {daily_str}", color=ft.colors.GREY_700, size=12),

                            ft.Row([
                                ft.TextButton("Edit", icon=ft.icons.EDIT, on_click=lambda e, o=order: self._edit_order(o)),
                                ft.TextButton("Delete", icon=ft.icons.DELETE, icon_color=ft.colors.RED, text_color=ft.colors.RED, on_click=lambda e, o_id=order.id: self._delete_order(o_id))
                            ], alignment=ft.MainAxisAlignment.END, spacing=0)
                        ], spacing=6),
                        padding=12
                    ),
                    elevation=2
                )
                self.orders_list_view.controls.append(card)

        if self.page:
            self.update()

    def _add_or_save_order(self, e):
        """التحقق من البيانات وإضافة أمر جديد أو تحديث القائم[cite: 4]."""
        order_id = (self.entry_order_id.value or "").strip()
        selected_tmpl_name = self.menu_template.value
        rate_val_raw = (self.entry_rate_value.value or "").strip()
        unit = self.menu_unit.value

        if not order_id:
            self._show_dialog("Validation Error", "Please enter an 'Order ID'.")
            return

        if not self.templates_list or selected_tmpl_name == "No Templates Available":
            self._show_dialog("Validation Error", "No design template selected. Please create a template first.")
            return

        if not rate_val_raw:
            self._show_dialog("Validation Error", "Please enter a 'Rate Value'.")
            return

        try:
            rate_val = float(rate_val_raw)
            if rate_val <= 0:
                self._show_dialog("Value Error", "Rate Value must be a positive number.")
                return
        except ValueError:
            self._show_dialog("Invalid Input", "Rate Value must be a valid number (e.g. 1.5).")
            return

        template = next((t for t in self.templates_list if t.name == selected_tmpl_name), None)
        if not template:
            self._show_dialog("Error", "Selected template was not found.")
            return

        if self.editing_order_id:
            order = next((o for o in self.orders_list if o.id == self.editing_order_id), None)
            if order:
                order.template = template
                order.rate = ProductionRate(value=rate_val, unit=unit)
            self._cancel_editing()
        else:
            if any(o.id == order_id for o in self.orders_list):
                self._show_dialog("Duplicate ID", f"An order with ID '{order_id}' already exists.")
                return

            rate = ProductionRate(value=rate_val, unit=unit)
            new_order = ProductionOrder(
                id=order_id, template=template, rate=rate, is_active=True
            )
            self.orders_list.append(new_order)
            self._clear_entries()

        self._refresh_table()
        if self.on_changed_callback:
            self.on_changed_callback()

    def _edit_order(self, order: ProductionOrder):
        """تعبئة الحقول ببيانات الأمر المحدد لتعديله[cite: 4]."""
        self.editing_order_id = order.id
        self.entry_order_id.value = order.id
        self.entry_order_id.disabled = True
        self.menu_template.value = order.template.name
        self.entry_rate_value.value = str(order.rate.value)
        self.menu_unit.value = order.rate.unit

        self.btn_add_order.text = "Save Changes"
        self.btn_add_order.icon = ft.icons.SAVE
        self.btn_add_order.bgcolor = ft.colors.GREEN_700
        self.btn_cancel_edit.visible = True
        if self.page:
            self.update()

    def _cancel_editing(self):
        """إلغاء وضع التعديل وإعادة الحقول لوضع الإنشاء العادي[cite: 4]."""
        self.editing_order_id = None
        self.entry_order_id.disabled = False
        self._clear_entries()
        
        self.btn_add_order.text = "Create Order"
        self.btn_add_order.icon = ft.icons.ADD
        self.btn_add_order.bgcolor = None
        self.btn_cancel_edit.visible = False
        if self.page:
            self.update()

    def _clear_entries(self):
        """مسح نصوص الحقول[cite: 4]."""
        self.entry_order_id.value = ""
        self.entry_rate_value.value = ""
        if self.page:
            self.update()

    def _toggle_order_active(self, order: ProductionOrder, is_active: bool):
        """تبديل حالة التفعيل (is_active) للأمر المستهدف[cite: 4]."""
        order.is_active = is_active
        if self.on_changed_callback:
            self.on_changed_callback()

    def _delete_order(self, order_id: str):
        """حذف الأمر مع التحقق من عدم استخدامه وعرض نافذة تأكيد[cite: 4]."""
        if self.is_order_used_callback and self.is_order_used_callback(order_id):
            self._show_dialog(
                "Action Blocked",
                f"Cannot delete order '{order_id}' because it is currently linked or in use in another section."
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
            self.orders_list[:] = [o for o in self.orders_list if o.id != order_id]
            self._refresh_table()
            if self.on_changed_callback:
                self.on_changed_callback()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete order '{order_id}'?"),
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
        """عرض مربعات الحوار والرسائل المنبثقة[cite: 4]."""
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
        """دالة عامة لتحديث القوائم والجدول من الخارج[cite: 4]."""
        self._refresh_template_dropdown()
        self._refresh_table()