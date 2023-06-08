from bpy.types import Context, Operator

from .base_op import BaseOp


def toggle_addon_prefs():
    from ..ui.sidebar_actions import USERPREF_PT_brush_manager_sidebar_actions as SidebarActions
    from ..ui.sidebar import USERPREF_PT_brush_manager_sidebar as Sidebar
    from ..ui.header import USERPREF_HT_brush_manager_header as Header
    from ..ui.content import USERPREF_PT_brush_manager_content as Content

    Sidebar.toggle()
    SidebarActions.toggle()
    Header.toggle()
    Content.toggle()


class BRUSHMANAGER_OT_toggle_prefs_ui(BaseOp, Operator):
    bl_idname = 'brushmanager.toggle_prefs_ui'
    bl_label = "Toggle Brush Manager UI"

    def execute(self, context: Context) -> set[str]:
        context.preferences.active_section = 'ADDONS'
        toggle_addon_prefs()
        return {'FINISHED'}
