from typing import Any, Dict
import flet as ft


class ResultsView(ft.Control):
    """لوحة عرض النتائج والإحصائيات مهيأة لشاشات الهواتف الذكية (وضع طولي) باستخدام مكتبة Flet[cite: 5]."""

    def __init__(self):
        super().__init__()

        # بطاقة إجمالي المصانع العسكرية (Land / Military Factories Card)
        self.lbl_total_military = ft.Text(
            "0.00",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.GREEN_ACCENT
        )
        
        # بطاقة إجمالي أحواض بناء السفن (Naval Dockyards Card)
        self.lbl_total_dockyards = ft.Text(
            "0.00",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_ACCENT
        )

        # حاويات عرض بيانات الجداول (Order Breakdown & Equipment Requirements)
        self.order_rows_column = ft.Column(spacing=8)
        self.equip_rows_column = ft.Column(spacing=8)

    def build(self):
        """بناء الهيكل الطولي المتجاوب لعرض الملخص والجداول[cite: 5]."""

        # 1. قسم بطاقات الملخص العلوية (Summary Cards)
        summary_cards = ft.Row([
            ft.Container(
                expand=True,
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("🏭 Military Factories", size=11, weight=ft.FontWeight.BOLD),
                            self.lbl_total_military
                        ], spacing=4),
                        padding=12
                    ),
                    elevation=2
                )
            ),
            ft.Container(
                expand=True,
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("⚓ Naval Dockyards", size=11, weight=ft.FontWeight.BOLD),
                            self.lbl_total_dockyards
                        ], spacing=4),
                        padding=12
                    ),
                    elevation=2
                )
            )
        ], spacing=10)

        # 2. قسم تفصيل الأوامر (Order Breakdown Section)
        order_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 Order Breakdown", size=15, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    self.order_rows_column
                ], spacing=10),
                padding=12
            ),
            elevation=2
        )

        # 3. قسم متطلبات المعدات (Equipment Requirements Section)
        equip_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📦 Equipment Requirements", size=15, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1),
                    self.equip_rows_column
                ], spacing=10),
                padding=12
            ),
            elevation=2
        )

        # حاوية رئيسية قابلة للتمرير رأسياً لتناسب الهواتف الطولية
        return ft.ListView([
            summary_cards,
            order_section,
            equip_section
        ], expand=True, spacing=12, padding=10)

    def display_results(self, calculation_data: Dict[str, Any]):
        """تحديث بطاقات الملخص والجداول بالبيانات المحسوبة من نظام الحسابات[cite: 5]."""
        
        # استخراج وتحديث إجماليات المصانع والأحواض[cite: 5]
        total_military = calculation_data.get("total_military_factories", 0.0)
        total_dockyards = calculation_data.get("total_dockyards", 0.0)

        self.lbl_total_military.value = f"{total_military:.2f}"
        self.lbl_total_dockyards.value = f"{total_dockyards:.2f}"

        # تفريغ الصفوف السابقة[cite: 5]
        self.order_rows_column.controls.clear()
        self.equip_rows_column.controls.clear()

        # --- تعبئة جدول تفصيل الأوامر (Order Breakdown) ---
        order_results = calculation_data.get("order_results", [])
        if not order_results:
            self.order_rows_column.controls.append(
                ft.Text("No order results available.", italic=True, color=ft.colors.GREY, size=12)
            )
        else:
            for order in order_results:
                row_container = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"ID: {order.get('order_id', '')}", weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(order.get('template_name', ''), size=12, color=ft.colors.GREY_700)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text(f"Land: {order.get('military_factories', 0.0):.2f}", size=12),
                            ft.Text(f"Naval: {order.get('dockyards', 0.0):.2f}", size=12)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=4),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                    padding=8,
                    border_radius=6
                )
                self.order_rows_column.controls.append(row_container)

        # --- تعبئة جدول متطلبات المعدات (Equipment Requirements) ---
        equip_breakdown = calculation_data.get("equipment_breakdown", {})
        if not equip_breakdown:
            self.equip_rows_column.controls.append(
                ft.Text("No equipment requirements available.", italic=True, color=ft.colors.GREY, size=12)
            )
        else:
            for eq_id, eq_info in equip_breakdown.items():
                row_container = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(eq_info.get("name", eq_id), weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(f"Category: {eq_info.get('category', '')}", size=11, color=ft.colors.GREY_700)
                        ], spacing=2, expand=True),
                        ft.Text(f"Total: {eq_info.get('total_facilities', 0.0):.2f}", weight=ft.FontWeight.BOLD, size=13, color=ft.colors.BLUE_GREY)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                    padding=8,
                    border_radius=6
                )
                self.equip_rows_column.controls.append(row_container)

        # تحديث واجهة التطبيق إذا تم ربطها بصفحة حية[cite: 5]
        if self.page:
            self.update()