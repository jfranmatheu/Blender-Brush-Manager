from bpy.types import Panel

from bl_ui.space_userpref import USERPREF_PT_save_preferences


class USERPREF_PT_brush_manager_sidebar_actions(Panel):
    bl_label = "Actions"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'EXECUTE'
    # bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_AREA'

        layout.menu("USERPREF_MT_save_load", text="", icon='COLLAPSEMENU')
        layout.operator('render.render')
        layout.label(text="Hola Mundo", icon='MONKEY')
    
    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_save_preferences, cls)
