from .base_ui import *

from bl_ui.space_userpref import USERPREF_HT_header

from ...ops.op_toggle_prefs_ui import ToggleBrushManagerUI as OPS_TogglePrefsUI



class USERPREF_HT_brush_manager_header(Header, BaseUI):
    bl_space_type = 'PREFERENCES'

    def draw_ui(self, context: Context, layout: UILayout, addon_data: AddonDataByMode, ui_props: UIProps):
        layout.operator_context = 'EXEC_AREA'

        row = layout.row()
        row.prop(ui_props, 'ui_context_mode', text='')
        row.prop(ui_props, 'ui_context_item', text='', expand=True)

        layout.separator_spacer()

        OPS_TogglePrefsUI.draw_in_layout(layout, text="Exit")

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_HT_header, cls)
