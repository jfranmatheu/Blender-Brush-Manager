from bpy.types import Event, Context
from bpy.props import StringProperty, IntProperty

from ..types import AddonDataByMode, UIProps
from brush_manager.addon_utils import Reg
import brush_manager.types as bm_types


@Reg.Ops.setup
class NewCategory(Reg.Ops.INVOKE_PROPS_POPUP):

    cat_name : StringProperty(default="")

    def invoke(self, context: Context, event: Event):
        self.cat_name = "Untitled Category"
        return super().invoke(context, event)

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, *args) -> bm_types.Category:
        return addon_data.new_brush_cat if ui_props.is_ctx_brush else addon_data.new_texture_cat

    def action(self, new_category: callable) -> None:
        new_category(self.cat_name)


@Reg.Ops.setup
class RemoveCategory(Reg.Ops.ACTION):

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, uuid: str | None) -> bm_types.Category:
        remove_func = addon_data.remove_brush_cat if ui_props.is_ctx_brush else addon_data.remove_texture_cat
        if uuid is not None:
            return remove_func, uuid
        active_cat_index = addon_data.active_brush_cat_index if ui_props.is_ctx_brush else addon_data.active_texture_cat_index
        return remove_func, active_cat_index

    def action(self, remove_cat: callable, cat: int | str) -> None:
        remove_cat(cat)


@Reg.Ops.setup
class SelectCategoryAtIndex(Reg.Ops.ACTION):

    index : IntProperty(default=-1)

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, *args) -> callable:
        return addon_data.select_brush_category if ui_props.is_ctx_brush else addon_data.select_texture_category

    def action(self, select_cat_at_index: callable) -> None:
        select_cat_at_index(self.index)


@Reg.Ops.setup
class AsignIconToCategory(Reg.Ops.Import.PNG):

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, uuid: str | None) -> bm_types.Category:
        if uuid is None:
            return addon_data.active_brush_cat if ui_props.is_ctx_brush else addon_data.active_texture_cat
        return addon_data.get_brush_cat(uuid) if ui_props.is_ctx_brush else addon_data.get_texture_cat(uuid)

    def action(self, cat: bm_types.Category) -> None:
        cat.asign_icon(self.filepath)
