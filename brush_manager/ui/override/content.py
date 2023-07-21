import bpy
from bpy.types import Panel, UILayout, Region
from bl_ui.space_userpref import USERPREF_PT_addons
from blf import dimensions
from mathutils import Vector

from math import floor, ceil

from ...ops import AppendSelectedToCategory, SelectAll, MoveSelectedToCategory, RemoveSelectedFromCategory, DuplicateSelected
from ...types import AddonData, UIProps, UUID, Item, Texture, Brush
from ...data import Brush_Collection
from ...icons import preview_collections, Icons
from ...images import get_default_brush_icon_by_type


class USERPREF_PT_brush_manager_content(Panel):
    bl_label = "Preferences Content"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "addons"
    bl_options = {'HIDE_HEADER'}

    def draw_icon(self, layout, icon_id: int | str):
        if isinstance(icon_id, int) and icon_id != 0:
            layout.template_icon(icon_value=icon_id, scale=1)
        else:
            _row = layout.row(align=True)
            _row.scale_x = 1.0
            _row.scale_y = 1.0
            _row.label(text="", icon_value=icon_id)

    def draw_lib_item(self, layout: UILayout, item: Brush | Texture):
        item_icon: int = item.icon_id
        if item_icon == 0:
            if isinstance(item, Brush_Collection):
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

        col2.prop(item, 'selected', text=item_name, icon='CHECKBOX_HLT' if item.selected else 'CHECKBOX_DEHLT')

    def draw_cat_item(self, layout: UILayout, item: Item):
        self.draw_lib_item(layout, item)

    def draw_items_actions(self, region: Region, layout: UILayout, ui_props: UIProps, addon_data: AddonData, items: list[tuple[Brush, Texture]]) -> None:
        h = region.height
        w = region.width
        tr = region.view2d.region_to_view(w, h)

        z = abs(tr[1]) / 29 # * self.scale)

        dummy = layout.row()
        dummy.label(text='', icon='BLANK1')
        dummy.scale_y = z

        layout = layout.column(align=True)
        layout.scale_y = 2.0

        sel_brushes = addon_data.selected_brushes

        no_selection = sel_brushes == []
        SelectAll.draw_in_layout(layout, text='', icon='CHECKBOX_DEHLT' if no_selection else 'CHECKBOX_HLT').select_action = ('SELECT_ALL' if no_selection else 'DESELECT_ALL')

        layout.separator()

        if ui_props.ui_in_libs_section:
            AppendSelectedToCategory.draw_in_layout(layout, text='', icon='APPEND_BLEND')

        elif ui_props.ui_in_cats_section:
            MoveSelectedToCategory.draw_in_layout(layout, text='', icon='VIEW_PAN')

            layout.separator()

            RemoveSelectedFromCategory.draw_in_layout(layout, text='', icon='REMOVE')

    def draw(self, context):
        layout = self.layout
        self.scale = context.preferences.system.ui_scale
        self.max_text_width = int((context.region.width / 3 * 0.75 * .75 * .92) / dimensions(0, 'a')[0])

        addon_data = AddonData.get_data_by_ui_mode(context)
        ui_props = UIProps.get_data(context)

        n_cols = max(int((context.region.width / 3) / (context.preferences.system.ui_scale * 80)), 1)

        main_row = layout.split(factor=0.9)

        grid = main_row.grid_flow(row_major=True, columns=n_cols, even_columns=True, even_rows=True, align=True)

        # def get_item_data(brush_uuid: str, use_texture: bool = True):
        #     brush_data = addon_data.get_brush(brush_uuid)
        #     return brush_data, addon_data.get_texture(brush_data.texture_uuid) if use_texture else None

        if ui_props.ui_in_libs_section:
            self.is_libs = True

            draw = self.draw_lib_item
            act_lib = addon_data.active_library
            if act_lib is None:
                return

            # # [get_item_data(uuid, use_texture=True) for uuid in active_cat.item_ids]
            if ui_props.is_ctx_brush:
                items = act_lib.get_brushes(addon_data) # [addon_data.get_brush(brush.uuid) for brush in act_lib.brushes]
            else:
                items = act_lib.get_textures(addon_data)

        elif ui_props.ui_in_cats_section:
            self.is_libs = False
            draw = self.draw_cat_item
            active_cat = addon_data.get_active_category(ui_props.ui_context_item)
            if active_cat is None:
                return

            # [get_item_data(uuid, use_texture=False) for uuid in active_cat.item_ids]
            items = active_cat.get_items(addon_data)

        else:
            return

        n_rows = ceil(len(items) / n_cols)

        region = context.region
        h = region.height
        scroll = top = abs(region.view2d.region_to_view(0, h)[1])
        bottom = abs(region.view2d.region_to_view(0, 0)[1])

        ui_scale = context.preferences.system.ui_scale

        ''' calculates the height of the item in the UI in pixels. '''
        item_height = 59.33 * ui_scale # we don't know exactly the height... just try and error lol

        above_hidden_rows = floor(top / item_height) - 1
        below_hidden_rows = ceil(bottom / item_height)
        
        # print("Scroll", scroll)
        # print("Row visible range", (below_hidden_rows, above_hidden_rows))


        for item_index, item in enumerate(items):
            row_index = max(floor(item_index / n_cols), 0)
            if row_index <= above_hidden_rows or  row_index >= below_hidden_rows:
                dummy_box = grid.box()
                #dummy_row = dummy_box.row()
                dummy_box.scale_y = 2.5
                #dummy_row.label(text='', icon='BLANK1')
                continue
            draw(grid.box(), item)

        self.draw_items_actions(context.region, main_row.column(align=True), ui_props, addon_data, items)

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_addons, cls)
