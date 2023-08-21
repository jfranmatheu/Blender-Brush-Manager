from .base_ui import *
from ...types import Category
from brush_manager.api import bm_ops

from bl_ui.space_userpref import USERPREF_PT_navigation_bar





class USERPREF_PT_brush_manager_sidebar(Panel, BaseUI):
    bl_label = "Brush Manager Sidebar"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'NAVIGATION_BAR'
    bl_options = {'HIDE_HEADER'}
    bl_order = 1

    def draw_cat_item(self, layout: UILayout, item: Category, active: bool):
        icon_id = item.icon_id
        # layout.template_icon(icon_value=icon_id, scale=2.0)
        # BM_OPS.select_category(cat_uuid=item.uuid)
        if active:
            layout.label(text=item.name, icon_value=icon_id)
        else:
            bm_ops.SelectCategory.draw_in_layout(layout, text=item.name, icon_value=icon_id).cat_uuid = item.uuid

    def draw_ui(self, context: Context, layout: UILayout, addon_data: AddonDataByMode, ui_props: UIProps):
        col = layout.column(align=True)

        col.scale_x = 2
        col.scale_y = 2

        draw = self.draw_cat_item
        if ui_props.is_ctx_brush:
            cat_coll = addon_data.brush_cats
            active_cat = addon_data.brush_cats.active
        elif ui_props.is_ctx_texture:
            cat_coll = addon_data.texture_cats
            active_cat = addon_data.texture_cats.active
        else:
            return

        cat_count: int = cat_coll.count

        for cat_idx, cat in enumerate(cat_coll):
            row = col.row(align=True)
            if cat == active_cat:
                _row = row.split(align=True, factor=0.03)
                _row.prop(ui_props, 'ui_active_item_color', text='')
                # _row = row.split(align=True, factor=0.95)
                box = _row.box()
                #if cat_idx != (cat_count-1):
                #    box.scale_y = 0.5
                #else:
                box.scale_y = 0.75
                draw(box.row(align=True), cat, True)
            else:
                draw(row, cat, False)


    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_navigation_bar, cls)
