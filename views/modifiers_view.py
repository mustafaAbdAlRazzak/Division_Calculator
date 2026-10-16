from typing import Callable, Optional
import flet as ft
from entities.production_modifiers import ProductionModifiers


class ModifiersView(ft.Control):
    """لوحة معاملات الإنتاج مهيأة لشاشات الهواتف الذكية (وضع طولي) باستخدام مكتبة Flet."""

    def __init__(
        self,
        modifiers: ProductionModifiers,
        on_calculate_callback: Optional[Callable[[], None]] = None,
    ):
        super().__init__()
        self.modifiers = modifiers
        self.on_calculate_callback = on_calculate_callback

        # ----------------- Land / Military Panel Fields -----------------
        self.entry_base_military = ft.TextField(
            label="Base Factory Output",
            hint_text="e.g. 4.5",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_input_changed,
            border_radius=8
        )
        self.entry_efficiency = ft.TextField(
            label="Factory Efficiency (e.g. 1.0 for 100%)",
            hint_text="e.g. 1.0 or 1.5",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_input_changed,
            border_radius=8
        )
        self.entry_land_bonus = ft.TextField(
            label="Land Bonus (e.g. 0.15 for 15%)",
            hint_text="e.g. 0.15",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_input_changed,
            border_radius=8
        )
        self.lbl_effective_land = ft.Text(
            "0.00 cost / day",
            weight=ft.FontWeight.BOLD,
            size=14,
            color=ft.colors.GREEN_ACCENT
        )

        # ----------------- Naval / Dockyard Panel Fields -----------------
        self.entry_base_dockyard = ft.TextField(
            label="Base Dockyard Output",
            hint_text="e.g. 2.5",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_input_changed,
            border_radius=8
        )
        self.entry_naval_bonus = ft.TextField(
            label="Naval Bonus (e.g. 0.10 for 10%)",
            hint_text="e.g. 0.10",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_input_changed,
            border_radius=8
        )
        self.lbl_effective_naval = ft.Text(
            "0.00 cost / day",
            weight=ft.FontWeight.BOLD,
            size=14,
            color=ft.colors.BLUE_ACCENT
        )

    def build(self):
        """إنشاء الهيكل الطولي للوحة المعاملات بنظام البطاقات (Cards) المتسلسلة."""
        
        # لوحة المصانع الحربية (Land Modifiers Panel)
        land_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "🏭 Land / Military Factory Modifiers", 
                        size=16, 
                        weight=ft.FontWeight.BOLD
                    ),
                    self.entry_base_military,
                    self.entry_efficiency,
                    self.entry_land_bonus,
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Text("Effective Land Output / Factory:", weight=ft.FontWeight.BOLD, size=13),
                        self.lbl_effective_land
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=12),
                padding=15
            ),
            elevation=2
        )

        # لوحة أحواض بناء السفن (Naval Modifiers Panel)
        naval_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "⚓ Naval / Dockyard Modifiers", 
                        size=16, 
                        weight=ft.FontWeight.BOLD
                    ),
                    self.entry_base_dockyard,
                    self.entry_naval_bonus,
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Text("Effective Naval Output / Dockyard:", weight=ft.FontWeight.BOLD, size=13),
                        self.lbl_effective_naval
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=12),
                padding=15
            ),
            elevation=2
        )

        # حاوية قابلة للتمرير رأسياً لتناسب الهواتف الطولية
        return ft.ListView([
            land_card,
            naval_card
        ], expand=True, spacing=10, padding=10)

    def did_mount(self):
        """تحميل القيم عند ظهور المكون على الشاشة"""
        self._load_modifiers_values()

    def _on_input_changed(self, e=None):
        """يتم تفعيلها فورياً عند إدخال أو تغيير أي قيمة لضمان التحديث اللحظي[cite: 3]."""
        if self.sync_modifiers_from_ui():
            if self.on_calculate_callback:
                self.on_calculate_callback()

    def _load_modifiers_values(self):
        """تعبئة حقول الواجهة بالقيم القادمة من كائن ProductionModifiers[cite: 3]."""
        self.entry_base_military.value = str(self.modifiers.base_military_factory_output)
        self.entry_efficiency.value = str(self.modifiers.factory_efficiency)
        self.entry_land_bonus.value = str(self.modifiers.land_production_bonus)
        
        self.entry_base_dockyard.value = str(self.modifiers.base_dockyard_output)
        self.entry_naval_bonus.value = str(self.modifiers.naval_production_bonus)

        self._update_effective_labels()

    def sync_modifiers_from_ui(self) -> bool:
        """قراءة الحقول من واجهة الهاتف وتحديث كائن البيانات (Dataclass)[cite: 3]."""
        try:
            self.modifiers.base_military_factory_output = float(
                (self.entry_base_military.value or "").strip() or 0.0
            )
            self.modifiers.factory_efficiency = float(
                (self.entry_efficiency.value or "").strip() or 0.0
            )
            self.modifiers.land_production_bonus = float(
                (self.entry_land_bonus.value or "").strip() or 0.0
            )
            self.modifiers.base_dockyard_output = float(
                (self.entry_base_dockyard.value or "").strip() or 0.0
            )
            self.modifiers.naval_production_bonus = float(
                (self.entry_naval_bonus.value or "").strip() or 0.0
            )

            self._update_effective_labels()
            return True
        except ValueError:
            return False

    def _update_effective_labels(self):
        """تحديث النصوص الخاصة بالنواتج الفعالة المحسوبة[cite: 3]."""
        eff_land = self.modifiers.get_effective_military_output()
        eff_naval = self.modifiers.get_effective_dockyard_output()

        self.lbl_effective_land.value = f"{eff_land:.4f} cost / day"
        self.lbl_effective_naval.value = f"{eff_naval:.4f} cost / day"
        
        if self.page:
            self.update()

    def refresh_view(self):
        """دالة عامة لإعادة تحميل القيم إذا تم تحديث كائن المعاملات من مصدر خارجي[cite: 3]."""
        self._load_modifiers_values()