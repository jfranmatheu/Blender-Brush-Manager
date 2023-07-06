from bpy.types import Panel, UILayout

from bl_ui.space_userpref import USERPREF_PT_navigation_bar

from ...types import UIProps, AddonData, Library, Category
from ...ops.op_library_actions import BRUSHMANAGER_OT_select_library



class USERPREF_PT_brush_manager_sidebar(Panel):
    bl_label = "Brush Manager Sidebar"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    bl_order = 1

    def draw_lib_item(self, layout: UILayout, item: Library, index: int):
        BRUSHMANAGER_OT_select_library.draw_in_layout(layout, text=item.name, icon='FILE_BLEND').index = index

    def draw_cat_item(self, layout: UILayout, item: Category):
        if icon_id := item.icon_id:
            layout.template_icon(icon_value=icon_id, scale=2.0)
        layout.label(text=item.name)


    def draw(self, context):
        layout = self.layout
        addon_data = AddonData.get_data_by_ui_mode(context)
        ui_props = UIProps.get_data(context)

        col = layout.column(align=True)

        col.scale_x = 1.5
        col.scale_y = 1.5

        if ui_props.ui_in_libs_section:
            draw = self.draw_lib_item
            items = addon_data.libraries
            coll_propname = 'libraries'
            coll_act_item_propname = 'active_library_index'
            active_index = addon_data.active_library_index
        elif ui_props.ui_in_cats_section:
            # active_cat = addon_data.get_active_category(ui_props.ui_item_type_context)
            draw = self.draw_cat_item
            if ui_props.ui_in_brush_context:
                items = addon_data.brush_cats
                coll_propname = 'brush_cats'
                coll_act_item_propname = 'active_brush_cat_index'
                active_index = addon_data.active_brush_cat_index
            elif ui_props.ui_in_texture_context:
                items = addon_data.texture_cats
                coll_propname = 'texture_cats'
                coll_act_item_propname = 'active_texture_cat_index'
                active_index = addon_data.active_texture_cat_index

        n_rows = int(context.region.height / (32 * context.preferences.system.ui_scale)) - 1
        col.template_list(
            'BRUSHMANAGER_UL_sidebar_list', '',
            addon_data, coll_propname,
            addon_data, coll_act_item_propname,
            maxrows=n_rows,
            rows=n_rows,
            # type='GRID'
        )

        # for index, item in enumerate(items):
        #     row = col.row(align=True)
        #     if index == active_index:
        #         _row = row.split(align=True, factor=0.05)
        #         _row.prop(ui_props, 'ui_active_item_color', text='')
        #         draw(row, item, index)
        #     else:
        #         draw(row, item, index)


    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_navigation_bar, cls)
