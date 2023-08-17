import bpy
from bpy.types import Context, Panel, UILayout, Region
from bl_ui.space_userpref import USERPREF_PT_addons
from blf import dimensions
from mathutils import Vector

from math import floor, ceil

from brush_manager.types import AddonDataByMode, UIProps

from brush_manager.api import bm_ops
from .base_ui import *
from ...ops import SelectAll, MoveSelectedToCategory, RemoveSelectedFromCategory
from ...types import AddonData, UIProps, Item, TextureItem, BrushItem, BrushCat, TextureCat, Category
from ...icons import Icons
from ...images import get_default_brush_icon_by_type



class USERPREF_PT_brush_manager_content(Panel, BaseUI):
    bl_label = "Preferences Content"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "addons"
    bl_options = {'HIDE_HEADER'}

    def draw_icon(self, layout: UILayout, icon_id: int | str):
        if isinstance(icon_id, int) and icon_id != 0:
            layout.template_icon(icon_value=icon_id, scale=1)
        else:
            _row = layout.row(align=True)
            _row.scale_x = 1.0
            _row.scale_y = 1.0
            _row.label(text="", icon_value=icon_id)

    def draw_lib_item(self, layout: UILayout, item: BrushItem | TextureItem):
        item_icon: int = item.icon_id
        if item_icon == 0:
            if isinstance(item, BrushItem):
                item_icon = get_default_brush_icon_by_type(item.type).icon_id
            else:
                item_icon = Icons.TEXTURE_PLACEHOLDER.icon_id

        col1 = layout.split(factor=0.25, align=True)
        col1.scale_y = 2.5
        self.draw_icon(col1, item_icon)
        col2 = col1.split(factor=0.99, align=True)
        col2.alignment = 'EXPAND'

        item_name = item.name
        if len(item_name) > 5:
            if item_name[1] == '|':
                item_name = item_name[2:] if item_name[2] != ' ' else item_name[3:]
            item_name = item_name.replace('_', ' ').replace('.', ' .')

        # col2.prop(item, 'select', text=item_name, icon='CHECKBOX_HLT' if item.select else 'CHECKBOX_DEHLT')
        bm_ops.SelectItem.draw_in_layout(col2,
                                         text=item_name,
                                         depress=item.select,
                                         icon='CHECKBOX_HLT' if item.select else 'CHECKBOX_DEHLT').item_uuid = item.uuid

    def draw_cat_item(self, layout: UILayout, item: Item):
        self.draw_lib_item(layout, item)

    def draw_items_actions(self, region: Region, layout: UILayout, ui_props: UIProps, active_cat: Category) -> None:
        h = region.height
        w = region.width
        tr = region.view2d.region_to_view(w, h)

        z = abs(tr[1]) / 29 # * self.scale)

        dummy = layout.row()
        dummy.label(text='', icon='BLANK1')
        dummy.scale_y = z

        layout = layout.column(align=True)
        layout.scale_y = 2.0

        sel_brushes = active_cat.items.selected

        no_selection = sel_brushes == []
        SelectAll.draw_in_layout(layout, text='', icon='CHECKBOX_DEHLT' if no_selection else 'CHECKBOX_HLT').select_action = ('SELECT_ALL' if no_selection else 'DESELECT_ALL')

        layout.separator()

        MoveSelectedToCategory.draw_in_layout(layout, text='', icon='VIEW_PAN')

        layout.separator()

        RemoveSelectedFromCategory.draw_in_layout(layout, text='', icon='REMOVE')

    def draw_ui(self, context: Context, layout: UILayout, addon_data: AddonDataByMode, ui_props: UIProps):
        self.scale = context.preferences.system.ui_scale
        self.max_text_width = int((context.region.width / 3 * 0.75 * .75 * .92) / dimensions(0, 'a')[0])

        n_cols = max(int((context.region.width / 3) / (context.preferences.system.ui_scale * 80)), 1)

        main_row = layout.split(factor=0.9)

        grid = main_row.grid_flow(row_major=True, columns=n_cols, even_columns=True, even_rows=True, align=True)

        draw = self.draw_cat_item
        active_cat = addon_data.active_category
        if active_cat is None:
            return

        items = active_cat.items

        n_rows = ceil(items.count / n_cols)
        region = context.region
        h = region.height
        scroll = top = abs(region.view2d.region_to_view(0, h)[1])
        bottom = abs(region.view2d.region_to_view(0, 0)[1])

        ui_scale = context.preferences.system.ui_scale

        ''' calculates the height of the item in the UI in pixels. '''
        item_height = 59.33 * ui_scale # we don't know exactly the height... just try and error lol

        above_hidden_rows = floor(top / item_height) - 1
        below_hidden_rows = ceil(bottom / item_height)

        for item_index, item in enumerate(items):
            row_index = max(floor(item_index / n_cols), 0)
            if row_index <= above_hidden_rows or  row_index >= below_hidden_rows:
                dummy_box = grid.box()
                dummy_box.scale_y = 2.5
                continue
            draw(grid.box(), item)

        self.draw_items_actions(context.region, main_row.column(align=True), ui_props, active_cat)

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_addons, cls)
