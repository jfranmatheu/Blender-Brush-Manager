import bpy
from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty

from ..paths import Paths
from ..types import AddonData, UIProps
from ..icons import new_preview
from brush_manager.addon_utils import Reg


@Reg.Ops.setup
class NewCategory(Reg.Ops.ACTION):

    def action(self, context: Context, addon_data: AddonData) -> None:
        cat_type = UIProps.get_data(context).ui_item_type_context

        if cat_type == 'BRUSH':
            cat_collection = addon_data.brush_cats
        elif cat_type == 'TEXTURE':
            cat_collection = addon_data.texture_cats
        else:
            return
        
        index = len(cat_collection)
        new_cat = cat_collection.add()
        new_cat.generate_uuid()
        new_cat.name = 'New Category %i' % (index + 1)

        if cat_type == 'BRUSH':
            addon_data.active_brush_cat_index = index
        elif cat_type == 'TEXTURE':
            addon_data.active_texture_cat_index = index
        
        context.area.tag_redraw()


@Reg.Ops.setup
class RemoveCategory(Reg.Ops.ACTION):

    def action(self, context: Context, addon_data: AddonData) -> None:
        cat_type = UIProps.get_data(context).ui_item_type_context

        if cat_type == 'BRUSH':
            active_cat = addon_data.active_brush_cat
            cat_collection = addon_data.brush_cats
            cat_index = addon_data.active_brush_cat_index
            cat_icon_path = Paths.Icons.CAT_BRUSH
        elif cat_type == 'TEXTURE':
            active_cat = addon_data.active_texture_cat
            cat_collection = addon_data.texture_cats
            cat_index = addon_data.active_texture_cat_index
            cat_icon_path = Paths.Icons.CAT_TEXTURE
        else:
            return

        if active_cat is None:
            return

        # Remove icon if it exists.
        icon_path = cat_icon_path(active_cat.uuid + '.png', as_path=True)
        if icon_path.exists():
            icon_path.unlink()

        cat_collection.remove(cat_index)

        context.area.tag_redraw()


@Reg.Ops.setup
class AsignIconToCategory(Reg.Ops.ACTION, ImportHelper):
    filename_ext = '.png'

    filter_glob: StringProperty(
        default='*.png',
        options={'HIDDEN'}
    )

    def action(self, context: Context, addon_data: AddonData) -> None:
        cat_type = UIProps.get_data(context).ui_item_type_context

        if cat_type == 'BRUSH':
            active_cat = addon_data.active_brush_cat
            cat_icon_path = Paths.Icons.CAT_BRUSH
        elif cat_type == 'TEXTURE':
            active_cat = addon_data.active_texture_cat
            cat_icon_path = Paths.Icons.CAT_TEXTURE
        else:
            return

        if active_cat is None:
            return

        icon_path = cat_icon_path(active_cat.uuid + '.png', as_path=True)
        if icon_path.exists():
            icon_path.unlink()
        
        image = bpy.data.images.load(self.filepath)
        image.scale(92, 92)
        image.filepath_raw = str(icon_path)
        image.save()
        bpy.data.images.remove(image)
        del image

        new_preview(active_cat.uuid, str(icon_path), collection='runtime', force_reload=True)

        context.area.tag_redraw()
