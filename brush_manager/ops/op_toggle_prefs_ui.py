import bpy
from bpy.types import Context

from brush_manager.addon_utils import Reg


enabled = False


def toggle_addon_prefs():
    from ..ui.override.sidebar_actions import USERPREF_PT_brush_manager_sidebar_actions as SidebarActions
    from ..ui.override.sidebar import USERPREF_PT_brush_manager_sidebar as Sidebar
    from ..ui.override.header import USERPREF_HT_brush_manager_header as Header
    from ..ui.override.content import USERPREF_PT_brush_manager_content as Content

    Sidebar.toggle()
    SidebarActions.toggle()
    Header.toggle()
    Content.toggle()

    global enabled
    enabled = not enabled


@Reg.Ops.setup
class ToggleBrushManagerUI(Reg.Ops.ACTION):
    label = "Toggle Brush Manager UI"

    def action(self, context: Context, _ui_props, _addon_data) -> set[str]:
        context.preferences.active_section = 'ADDONS'
        toggle_addon_prefs()

        global enabled
        show_region_header = enabled
        alignment = 'TOP' if enabled else 'BOTTOM'
        context.space_data.show_region_header = show_region_header
        for region in context.area.regions:
            if region.type == 'HEADER':
                if region.alignment != alignment:
                    with context.temp_override(window=context.window, area=context.area, region=region):
                        bpy.ops.screen.region_flip()
                break


def unregister():
    global enabled
    if enabled:
        toggle_addon_prefs()
