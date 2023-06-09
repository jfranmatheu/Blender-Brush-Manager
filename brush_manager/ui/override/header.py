from bpy.types import Header

from bl_ui.space_userpref import USERPREF_HT_header

from ...ops.op_toggle_prefs_ui import ToggleBrushManagerUI as OPS_TogglePrefsUI
from ...types import UIProps, AddonData



class USERPREF_HT_brush_manager_header(Header):
    bl_space_type = 'PREFERENCES'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_AREA'
        
        addon_data = AddonData.get_data(context)
        ui_props = UIProps.get_data(context)

        row = layout.row()
        # row.prop(addon_data, 'context_mode', text='')
        row.prop(ui_props, 'ui_context_mode', text='')
        row.prop(ui_props, 'ui_active_section', text='Libraries', expand=True)

        layout.separator_spacer()

        OPS_TogglePrefsUI.draw_in_layout(layout, text="Exit")

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_HT_header, cls)
