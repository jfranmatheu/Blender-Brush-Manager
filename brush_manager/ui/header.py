from bpy.types import Header

from bl_ui.space_userpref import USERPREF_HT_header

from ..ops.op_toggle_prefs_ui import BRUSHMANAGER_OT_toggle_prefs_ui as OPS_TogglePrefsUI
from ..types import UIProps



class USERPREF_HT_brush_manager_header(Header):
    bl_space_type = 'PREFERENCES'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_AREA'
        ui_props = UIProps.get_data(context)

        layout.row(align=False).prop(ui_props, 'ui_active_section', text='Libraries', expand=True)

        layout.separator_spacer()

        OPS_TogglePrefsUI.draw_in_layout(layout, text="Exit")

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_HT_header, cls)
