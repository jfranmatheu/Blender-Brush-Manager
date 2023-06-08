from bpy.types import Panel

from bl_ui.space_userpref import USERPREF_PT_navigation_bar


class USERPREF_PT_brush_manager_sidebar(Panel):
    bl_label = "Preferences Navigation"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    # bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        prefs = context.preferences

        col = layout.column()

        col.scale_x = 1.3
        col.scale_y = 1.3
        col.label(text="Hello Sidebar")

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_navigation_bar, cls)
