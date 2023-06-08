from bpy.types import Panel

from bl_ui.space_userpref import USERPREF_PT_addons


class USERPREF_PT_brush_manager_content(Panel):
    bl_label = "Preferences Content"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "addons"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences

        layout.label(text="Hola Contenido")


    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_addons, cls)
