from bpy.types import Event, Context
from bpy.props import StringProperty

from brush_manager.types import AddonDataByMode, UIProps, AddonData
from brush_manager.addon_utils import Reg
import brush_manager.types as bm_types


@Reg.Ops.setup
class NewCategory(Reg.Ops.INVOKE_PROPS_POPUP):

    cat_name : StringProperty(default="")

    def invoke(self, context: Context, event: Event):
        self.cat_name = "Untitled Category"
        return super().invoke(context, event)

    def get_data(self, ui_props: UIProps, addon_data: AddonDataByMode) -> bm_types.Category:
        return addon_data.new_brush_cat if ui_props.is_ctx_brush else addon_data.new_texture_cat

    def action(self, new_category: callable) -> None:
        new_category(self.cat_name)


@Reg.Ops.setup
class RemoveCategory(Reg.Ops.ACTION):
    ''' Removes active category. '''

    def action(self, context: Context, ui_props: UIProps, bm_data: AddonDataByMode) -> None:
        cat_collection = bm_data.brush_cats if ui_props.is_ctx_brush else bm_data.texture_cats
        cat_collection.remove(cat_collection.active_id)


@Reg.Ops.setup
class SelectCategory(Reg.Ops.ACTION):

    cat_uuid : StringProperty(default='')

    def action(self, context: Context, ui_props: UIProps, bm_data: AddonDataByMode) -> None:
        cat_collection = bm_data.brush_cats if ui_props.is_ctx_brush else bm_data.texture_cats
        cat_collection.select(self.cat_uuid)


@Reg.Ops.setup
class AsignIconToCategory(Reg.Ops.Import.PNG):
    cat_uuid : StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})

    def action(self, context: Context, ui_props: UIProps, bm_data: AddonDataByMode) -> None:
        if self.cat_uuid != '':
            cat = bm_data.brush_cats.get(self.cat_uuid) if ui_props.is_ctx_brush else bm_data.texture_cats.get(self.cat_uuid)
        else:
            cat = bm_data.brush_cats.active if ui_props.is_ctx_brush else bm_data.texture_cats.active
        if cat is not None:
            cat.asign_icon(self.filepath)


@Reg.Ops.setup
class RenameCategory(Reg.Ops.INVOKE_PROPS_POPUP):
    cat_uuid : StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})
    cat_name : StringProperty(default='Name')

    def get_cat(self, ui_props: UIProps, addon_data: AddonDataByMode) -> bm_types.Category:
        if ui_props.is_ctx_brush:
            if self.cat_uuid == '':
                cat = addon_data.brush_cats.active
            else:
                cat = addon_data.get_brush_cat(self.cat_uuid)
        else:
            if self.cat_uuid == '':
                cat = addon_data.texture_cats.active
            else:
                cat = addon_data.get_texture_cat(self.cat_uuid)

        if cat is None:
            return None

        return cat

    def invoke(self, context: Context, event: Event):
        bm_data = AddonData.get_data_by_context(context)
        ui_props = UIProps.get_data(context)
        self.cat = self.get_cat(ui_props, bm_data)
        if self.cat is None:
            return {'CANCELLED'}
        self.cat_name = self.cat.name
        return super().invoke(context, event)

    def action(self, *args) -> None:
        self.cat.name = self.cat_name
