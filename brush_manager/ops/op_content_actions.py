import bpy
from bpy.types import Event, Context
from bpy.props import StringProperty, BoolProperty, EnumProperty

from ..types import AddonData, UIProps, AddonDataByMode
from brush_manager.addon_utils import Reg
from brush_manager.paths import Paths
from brush_manager.icons import new_preview
import brush_manager.types as bm_types


def get_cateogry_items(self, context: Context):
    addon_data = AddonData.get_data_by_ui_mode(context)
    cat_type = UIProps.get_data(context).ui_context_item
    if cat_type == 'BRUSH':
        cats = addon_data.brush_cats
    elif cat_type == 'TEXTURE':
        cats = addon_data.texture_cats
    return [
        (cat.uuid, cat.name, cat.name) for cat in cats
    ]


@Reg.Ops.setup
class SelectAll(Reg.Ops.ACTION):
    select_action: StringProperty()

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, *args) -> bm_types.Category:
        return (addon_data.selected_brushes, addon_data.brushes) \
            if ui_props.is_ctx_brush else\
               (addon_data.selected_textures, addon_data.textures)

    def action(self, selected_items: list[bm_types.Item], items: list[bm_types.Item]) -> None:
        if self.select_action == 'TOGGLE':
            for item in items:
                item.selected = not item.selected

        elif self.select_action == 'DESELECT_ALL':
            for item in selected_items:
                item.selected = False

        elif self.select_action == 'SELECT_ALL':
            for item in items:
                item.selected = True


@Reg.Ops.setup
class RemoveSelectedFromActiveCategory(Reg.Ops.ACTION):

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, uuid: str | None) -> bm_types.Category:
        if ui_props.is_ctx_brush:
            selected_items = addon_data.selected_brushes
            cat = addon_data.get_brush_cat(uuid) if uuid else addon_data.active_brush_cat
        else:
            selected_items = addon_data.selected_textures
            cat = addon_data.get_texture_cat(uuid) if uuid else addon_data.active_texture_cat

        if cat is None or len(selected_items) == 0:
            return None

        return selected_items, cat

    def action(self, selected_items: list[bm_types.Item], cat: bm_types.Category) -> None:
        cat.remove_items(selected_items)
        SelectAll.run(select_action='DESELECT_ALL')


@Reg.Ops.setup
class MoveSelectedToCategory(Reg.Ops.INVOKE_PROPS_POPUP):

    select_category : EnumProperty(
        name="Select a Category",
        items=get_cateogry_items
    )

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, uuid: str | None) -> bm_types.Category:
        if ui_props.is_ctx_brush:
            selected_items = addon_data.selected_brushes
            cat = addon_data.get_brush_cat(uuid if uuid else self.select_category)
            select_cat = addon_data.select_brush_category
        else:
            selected_items = addon_data.selected_textures
            cat = addon_data.get_texture_cat(uuid if uuid else self.select_category)
            select_cat = addon_data.select_texture_category

        if cat is None or len(selected_items) == 0:
            return None

        return selected_items, cat, select_cat

    def action(self, selected_items: list[bm_types.Item], cat: bm_types.Category, select_cat: callable) -> None:
        RemoveSelectedFromActiveCategory.run()
        cat.add_items(selected_items)
        select_cat(cat)


@Reg.Ops.setup
class AsignIconToBrush(Reg.Ops.Import.PNG):

    def get_data(self, _ui_props: UIProps, addon_data: AddonDataByMode, uuid: str | None) -> bm_types.Category:
        return addon_data.get_brush(uuid) if uuid else addon_data.active_brush

    def action(self, brush: bm_types.Brush) -> None:
        brush.asign_icon(self.filepath)
