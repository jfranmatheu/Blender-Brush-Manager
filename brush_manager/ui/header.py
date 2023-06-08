from bpy.types import Header

from bl_ui.space_userpref import USERPREF_HT_header

from ..ops.op_toggle_prefs_ui import BRUSHMANAGER_OT_toggle_prefs_ui as OPS_TogglePrefsUI



class USERPREF_HT_brush_manager_header(Header):
    bl_space_type = 'PREFERENCES'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_AREA'

        layout.template_header()

        layout.label(text="Tengo Caca!")

        layout.separator_spacer()

        OPS_TogglePrefsUI.draw_in_layout(layout, text="Exit")

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_HT_header, cls)
