from bpy.types import Panel, UILayout

from bl_ui.space_userpref import USERPREF_PT_addons

from ..types import AddonData, UIProps, UUID, Item, Texture, Brush
from ..icons import preview_collections, Icons


class USERPREF_PT_brush_manager_content(Panel):
    bl_label = "Preferences Content"
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "addons"
    bl_options = {'HIDE_HEADER'}

    def draw_icon(self, layout, icon_id: int | str):
        if isinstance(icon_id, int) and icon_id != 0:
            layout.template_icon(icon_value=icon_id, scale=2.5)
        else:
            _row = layout.row(align=True)
            _row.scale_x = 2.0
            _row.scale_y = 2.0
            _row.label(text="", icon=icon_id)

    def draw_lib_item(self, layout: UILayout, item: tuple[Brush, Texture]):
        brush, texture = item

        brush_icon = brush.icon_id
        if brush_icon == 0:
            brush_icon = Icons.BRUSH_PLACEHOLDER.icon_id # 'BRUSH_DATA'
        tex_icon = texture.icon_id if texture is not None else 0
        if tex_icon == 0:
            tex_icon = Icons.TEXTURE_PLACEHOLDER.icon_id # 'TEXTURE_DATA'

        row = layout.row(align=False)
        col1 = row.column().row(align=True)
        col1.alignment = 'LEFT'
        self.draw_icon(col1, brush_icon)
        col1.label(text=brush.name)
        col2 = row.column().row(align=True)
        col2.alignment = 'RIGHT'
        self.draw_icon(col2, tex_icon)


    def draw_cat_item(self, layout: UILayout, item: Item):
        if icon_id := item.icon_id:
            layout.template_icon(icon_value=icon_id, scale=2.0)
        layout.label(text=item.name)

    def draw(self, context):
        addon_data = AddonData.get_data(context)
        ui_props = UIProps.get_data(context)

        layout = self.layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=False)

        if ui_props.ui_in_libs_section:
            draw = self.draw_lib_item
            act_lib = addon_data.active_library
            if act_lib is None:
                return

            def get_data(brush_uuid: str):
                brush_data = addon_data.get_brush_data(brush_uuid)
                return brush_data, addon_data.get_texture_data(brush_data.texture_uuid)
            items = [get_data(brush.uuid) for brush in act_lib.brushes]
            # uid_name = {brush.uuid: brush.name for brush in act_lib.brushes}

            # if ui_props.ui_in_brush_context:
            #     items = act_lib.brushes
            # else:
            #     items = act_lib.textures
        elif ui_props.ui_in_cats_section:
            draw = self.draw_cat_item
            active_cat = addon_data.get_active_category(ui_props.ui_item_type_context)
            if active_cat is None:
                return
            items = active_cat.items
            # uid_name = {item.uuid: item.name for item in active_cat.items}

        # print(items)
        # icon_previews = preview_collections['runtime']

        for item in items:
            draw(layout.box(), item)

        # print(uid_name.keys())
        # print(icon_previews.keys())
        # print(set(uid_name.keys()).intersection(set(icon_previews.keys())))
        # for key, preview in icon_previews.items():
        #     if key not in uid_name:
        #         continue
        #     # print(key, preview.icon_id)
        #     row = layout.row(align=True)
        #     row.template_icon(icon_value=preview.icon_id, scale=0.1)
        #     row.label(text=uid_name[key])

    @classmethod
    def toggle(cls):
        from .override_ui import toggle_ui
        toggle_ui(USERPREF_PT_addons, cls)
