from bpy.types import AddonPreferences
from bpy.props import PointerProperty

from .data import AddonData
from .ops.op_toggle_prefs_ui import ToggleBrushManagerUI as OPS_TogglePrefsUI
from .ops.op_data import ClearData


class BrushManagerPreferences(AddonPreferences):
    bl_idname = __package__

    # data : PointerProperty(type=AddonData)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 5.0
        OPS_TogglePrefsUI.draw_in_layout(row, text="Manage")
        
        layout.separator(factor=2)
        
        layout.alert = True
        ClearData.draw_in_layout(row, text="Clear BrushManager Data")
        layout.alert = False
