from bpy.types import Panel

from bl_ui.space_userpref import USERPREF_PT_save_preferences

from ...types import UIProps
from ...ops.op_library_actions import BRUSHMANAGER_OT_add_library, BRUSHMANAGER_OT_remove_library
from ...ops.op_category_actions import BRUSHMANAGER_OT_new_category, BRUSHMANAGER_OT_remove_category, BRUSHMANAGER_OT_category_asign_icon


class USERPREF_PT_brush_manager_sidebar_actions(Panel):
    # bl_label = "Actions"
    # bl_space_type = 'PREFERENCES'
    # bl_region_type = 'EXECUTE'
    # bl_options = {'HIDE_HEADER'}
    bl_label = "Actions"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    bl_order = 2


    def draw(self, context):
        ui_props = UIProps.get_data(context)

        layout = self.layout.row(align=True)
        # layout.operator_context = 'EXEC_AREA'

        if ui_props.ui_in_libs_section:
            BRUSHMANAGER_OT_add_library.draw_in_layout(layout, icon='ADD', text='')
            BRUSHMANAGER_OT_remove_library.draw_in_layout(layout, icon='REMOVE', text='')

        elif ui_props.ui_in_cats_section:
            BRUSHMANAGER_OT_new_category.draw_in_layout(layout, icon='ADD', text='')
            BRUSHMANAGER_OT_remove_category.draw_in_layout(layout, icon='REMOVE', text='')
            layout.separator()
            BRUSHMANAGER_OT_category_asign_icon.draw_in_layout(layout, icon='IMAGE', text='')

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_save_preferences, cls)
