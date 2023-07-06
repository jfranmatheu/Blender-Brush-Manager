from bpy.types import Panel, UILayout, Region
from bl_ui.space_userpref import USERPREF_PT_addons
from blf import dimensions
from mathutils import Vector

from ...ops import AppendSelectedToCategory, SelectAll, MoveSelectedToCategory, RemoveSelectedFromCategory, DuplicateSelected
from ...types import AddonData, UIProps, UUID, Item, Texture, Brush
from ...icons import preview_collections, Icons


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

    def draw_lib_item(self, layout: UILayout, item: tuple[Brush, Texture], use_secondary: bool = False):
        brush, texture = item

        brush_icon = brush.icon_id
        if brush_icon == 0:
            brush_icon = Icons.BRUSH_PLACEHOLDER.icon_id # 'BRUSH_DATA'
        tex_icon = texture.icon_id if texture is not None else 0
        if tex_icon == 0:
            tex_icon = Icons.TEXTURE_PLACEHOLDER.icon_id # 'TEXTURE_DATA'

        #row = layout.row(align=False)
        #col1 = row.column().row(align=True)
        #col1.alignment = 'LEFT'
        col1 = layout.split(factor=0.25, align=True)
        col1.scale_y = 2.5
        self.draw_icon(col1, brush_icon)
        col2 = col1.split(factor=0.75, align=True) if use_secondary else col1.split(factor=0.99, align=True) # col1.row(align=True)
        col2.alignment = 'LEFT' if use_secondary else 'EXPAND'
        brush_name = brush.name
        if brush_name[1] == '|':
            brush.name = brush_name[2:] if brush_name[2] != ' ' else brush.name[3:]
        brush_name = brush_name.replace('_', ' ').replace('.', ' .')
        # brush_name = brush_name[:max(self.max_text_width-3, 1)] + '...' if len(brush_name) > self.max_text_width else brush_name
        # textwrap.shorten(brush_name.replace('_', ' ').replace('.', ' .'), width=self.max_text_width, placeholder="...")
        # col2.label(text=brush_name)
        col2.prop(brush, 'selected', text=brush_name, icon='CHECKBOX_HLT' if brush.selected else 'CHECKBOX_DEHLT')
        #col2 = row.column().row(align=True)
        #col2.alignment = 'RIGHT'
        if use_secondary:
            col3 = col2.row(align=True)
            self.draw_icon(col3, tex_icon)

    def draw_cat_item(self, layout: UILayout, item: Item):
        self.draw_lib_item(layout, item, use_secondary=False)

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

        grid = main_row.grid_flow(row_major=True, columns=n_cols, even_columns=True, even_rows=True, align=False)

        def get_item_data(brush_uuid: str, use_texture: bool = True):
            brush_data = addon_data.get_brush_data(brush_uuid)
            return brush_data, addon_data.get_texture_data(brush_data.texture_uuid) if use_texture else None

        if ui_props.ui_in_libs_section:
            self.is_libs = True

            draw = self.draw_lib_item
            act_lib = addon_data.active_library
            if act_lib is None:
                return

            items = [get_item_data(brush.uuid) for brush in act_lib.brushes]

        elif ui_props.ui_in_cats_section:
            self.is_libs = False
            draw = self.draw_cat_item
            active_cat = addon_data.get_active_category(ui_props.ui_item_type_context)
            if active_cat is None:
                return

            items = [get_item_data(item.uuid, use_texture=False) for item in active_cat.items]

        else:
            return

        for item in items:
            draw(grid.box(), item)

        self.draw_items_actions(context.region, main_row.column(align=True), ui_props, addon_data, items)

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_addons, cls)
