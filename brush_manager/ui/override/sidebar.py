from bpy.types import Panel, UILayout

from bl_ui.space_userpref import USERPREF_PT_navigation_bar

from ...types import UIProps, AddonData, Category
from ...ops.op_library_actions import SelectLibraryAtIndex



class USERPREF_PT_brush_manager_sidebar(Panel):
    bl_label = "Brush Manager Sidebar"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    bl_order = 1

    def draw_cat_item(self, layout: UILayout, item: Category):
        if icon_id := item.icon_id:
            layout.template_icon(icon_value=icon_id, scale=2.0)
        layout.label(text=item.name)

    def draw(self, context):
        layout = self.layout
        ui_props = UIProps.get_data(context)
        addon_data = AddonData.get_data_by_context(ui_props)

        col = layout.column(align=True)

        col.scale_x = 1.5
        col.scale_y = 1.5

        draw = self.draw_cat_item
        if ui_props.is_ctx_brush:
            items = addon_data.brush_cats
            # coll_propname = 'brush_cats'
            # coll_act_item_propname = 'active_brush_cat_index'
            active = addon_data.brush_cats.active
        elif ui_props.is_ctx_texture:
            items = addon_data.texture_cats
            # coll_propname = 'texture_cats'
            # coll_act_item_propname = 'active_texture_cat_index'
            active = addon_data.texture_cats.active

        # n_rows = int(context.region.height / (32 * context.preferences.system.ui_scale)) - 1
        # col.template_list(
        #     'BRUSHMANAGER_UL_sidebar_list', '',
        #     addon_data, coll_propname,
        #     addon_data, coll_act_item_propname,
        #     maxrows=n_rows,
        #     rows=n_rows,
        #     # type='GRID'
        # )

        for item in items:
            row = col.row(align=True)
            if item == active:
                _row = row.split(align=True, factor=0.05)
                _row.prop(ui_props, 'ui_active_item_color', text='')
                _row = row.split(align=True, factor=0.95)
                _row.box()
                draw(row, item)
            else:
                draw(row, item)


    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_navigation_bar, cls)
