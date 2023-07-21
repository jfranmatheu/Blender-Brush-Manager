from enum import Enum, auto
from brush_manager import types as bm_types
from brush_manager.paths import Paths
import bpy

import brush_manager.ops as bm_ops



class BM(Enum):
    UI = auto()

    SCULPT = auto()
    TEXTURE_PAINT = auto()
    GPENCIL_PAINT = auto()

    def __call__(self, context: bpy.types.Context | None = None) -> bm_types.AddonDataByMode | bm_types.UIProps:
        if self == BM.UI:
            return bm_types.UIProps.get_data(context)
        ui_context_mode: str = self.name.lower()
        bm_types.UIProps.get_data(context).ui_context_mode = ui_context_mode
        return bm_types.AddonData.get_data_by_ui_mode(context, ui_context_mode)

    # ----------------------------------------------------------------
    # Category Management Methods.

    brush_cats: bm_types.BrushCat_Collection = property(lambda self: self().brush_cats)
    texture_cats: bm_types.TextureCat_Collection = property(lambda self: self().texture_cats)

    active_brush_cat: bm_types.BrushCategory = property(lambda self: self().active_brush_cat)
    active_texture_cat: bm_types.TextureCategory = property(lambda self: self().active_texture_cat)

    def set_active_brush_cat(self, context: bpy.types.Context, category: str or int) -> None: self(context).select_brush_category(category)
    def set_active_texture_cat(self, context: bpy.types.Context, category: str or int) -> None: self(context).select_texture_category(category)
    def remove_brush_cat(self, context: bpy.types.Context, category: str or int) -> None: self(context).remove_brush_cat(category)
    def remove_texture_cat(self, context: bpy.types.Context, category: str or int) -> None: self(context).remove_texture_cat(category)
    def remove_active_brush_cat(self, context: bpy.types.Context) -> None: self.remove_brush_cat(context, self(context).active_brush_cat_index)
    def remove_active_texture_cat(self, context: bpy.types.Context) -> None: self.remove_texture_cat(context, self(context).active_texture_cat_index)

    # ----------------------------------------------------------------
    # Category Items Management Methods.

    brushes: bm_types.Brush_Collection = property(lambda self: self().brushes)
    textures: bm_types.Texture_Collection = property(lambda self: self().textures)

    def load_select_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        self(context).select_brush(context, brush)

    def reset_brush_to_default(self, context: bpy.types.Context, brush: int or str) -> None:
        uuid = self(context).get_brush_uuid(brush) if isinstance(brush, int) else brush
        bl_brush = self(context).get_blbrush(uuid)
        if bl_brush is None:
            return

        # Remove brush.
        uuid = bl_brush.uuid
        bpy.data.brushes.remove(bl_brush)
        del bl_brush

        # Replace current brush state with default state.
        from shutil import copyfile
        copyfile(Paths.Data.BRUSH(uuid + '.default.blend'), Paths.Data.BRUSH(uuid + '.blend'))

        # Load brush again from lib (will load default since we replaced it).
        self(context).select_brush(context, uuid)

    def save_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        data = self(context)
        uuid = data.get_brush_uuid(brush) if isinstance(brush, int) else brush
        data.get_brush(uuid).save()

    def save_default_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        data = self(context)
        uuid = data.get_brush_uuid(brush) if isinstance(brush, int) else brush
        data.get_brush(uuid).save(save_default=True)



class BM_OPS:
    def import_library(self,
                       ui_context_mode: str = '',
                       ui_context_type: str = ''):
        bm_ops.ImportLibrary('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def select_library(self,
                       index: int,
                       ui_context_mode: str = '',
                       ui_context_type: str = ''):
        bm_ops.SelectLibraryAtIndex(
            index=index,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def remove_active_library(self, ui_context_mode: str = ''):
        bm_ops.RemoveActiveLibrary(ui_context_mode=ui_context_mode)


    def append_selected_to_category(self,
                               cat_uuid: str | None = None,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        ''' If cat_uuid is not provided, it will popup an interface with a category selector. '''
        bm_ops.AppendSelectedToCategory('INVOKE_DEFAULT' if cat_uuid is None else 'EXEC_DEFAULT',
            select_category=cat_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type,
        )


    # ------------------------------------------------------


    def new_category(self,
                     cat_name: str | None = None,
                     ui_context_mode: str = '',
                     ui_context_type: str = ''):
        ''' If cat_name is not provided, it will popup an interface with a text field. '''
        bm_ops.NewCategory('INVOKE_DEFAULT' if cat_name is None else 'EXEC_DEFAULT',
            cat_name=cat_name,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def remove_active_category(self,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        bm_ops.RemoveCategory(
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def select_category(self,
                       index: int,
                       ui_context_mode: str = '',
                       ui_context_type: str = ''):
        bm_ops.SelectCategoryAtIndex(
            index=index,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def move_selected_to_category(self,
                               cat_uuid: str | None = None,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        ''' If cat_name is not provided, it will popup an interface with a category selector. '''
        bm_ops.MoveSelectedToCategory('INVOKE_DEFAULT' if cat_uuid is None else 'EXEC_DEFAULT',
            select_category=cat_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def asign_icon_to_active_category(self,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        bm_ops.AsignIconToCategory('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )


    # ----------------------------------------------------------------


    def asign_icon_to_active_brush(self,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        bm_ops.AsignIconToBrush('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def select_all(self,
                   ui_context_mode: str = '',
                   ui_context_type: str = ''):
        bm_ops.SelectAll(
            select_action='SELECT_ALL',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def deselect_all(self,
                   ui_context_mode: str = '',
                   ui_context_type: str = ''):
        bm_ops.SelectAll(
            select_action='DESELECT_ALL',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )
