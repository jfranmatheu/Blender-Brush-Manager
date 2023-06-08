from bpy.types import AddonPreferences
from bpy.props import PointerProperty

from .data import AddonData
from .ops.op_toggle_prefs_ui import BRUSHMANAGER_OT_toggle_prefs_ui as OPS_TogglePrefsUI


class BrushManagerPreferences(AddonPreferences):
    bl_idname = __package__

    data : PointerProperty(type=AddonData)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 5.0
        OPS_TogglePrefsUI.draw_in_layout(row, text="Manage")

