from .base_ui import *

from bl_ui.space_userpref import USERPREF_PT_save_preferences

from ...ops.op_library_actions import ImportLibrary #, RemoveActiveLibrary
from ...ops.op_category_actions import NewCategory, RemoveCategory, AsignIconToCategory


class USERPREF_PT_brush_manager_sidebar_actions(Panel, BaseUI):
    bl_label = "Actions"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    bl_order = 2


    def draw_ui(self, context: Context, layout: UILayout, addon_data: AddonDataByMode, ui_props: UIProps):
        row = layout.row(align=True)

        ImportLibrary.draw_in_layout(row, icon='IMPORT', text='')
        row.separator()

        NewCategory.draw_in_layout(row, icon='COLLECTION_NEW', text='')
        RemoveCategory.draw_in_layout(row, icon='REMOVE', text='')
        row.separator()
        AsignIconToCategory.draw_in_layout(row, icon='IMAGE_DATA', text='')


    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_save_preferences, cls)
