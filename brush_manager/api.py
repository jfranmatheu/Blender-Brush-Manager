from enum import Enum, auto
from brush_manager import data as bm_data, types as bm_types
from brush_manager.paths import Paths
import bpy

import brush_manager.ops as bm_ops


class BM_UI: # -> bm_types.UIProps:

    @classmethod
    def get_data(context: bpy.types.Context | None = None) -> bm_types.UIProps:
        return bm_types.UIProps.get_data(context)

    @classmethod
    def get_ctx_mode(cls, context: bpy.types.Context) -> str:
        cls.get_data(context).ui_context_mode

    @classmethod
    def get_ctx_item(cls, context: bpy.types.Context) -> str:
        cls.get_data(context).ui_context_item

    @classmethod
    def _set_ctx_mode(cls, context: bpy.types.Context, mode: str) -> None:
        ui: bm_types.UIProps = cls.get_data(context)
        ui.ui_context_mode = mode

    @classmethod
    def _set_ctx_item(cls, context: bpy.types.Context, item_type: str) -> None:
        ui: bm_types.UIProps = cls.get_data(context)
        ui.ui_context_item = item_type

    @classmethod
    def toggle_ctx_item(cls, context: bpy.types.Context | None = None) -> str:
        item_type: str = cls.get_ctx_item(context)
        item_type = 'BRUSH' if item_type == 'TEXTURE' else 'TEXTURE'
        cls._set_ctx_item(context, item_type)
        return item_type

    @classmethod
    def set_ctx_item__brush(cls, context: bpy.types.Context | None = None) -> None:
        cls._set_ctx_item(context, 'BRUSH')

    @classmethod
    def set_ctx_item__brush(cls, context: bpy.types.Context | None = None) -> None:
        cls._set_ctx_item(context, 'TEXTURE')

    @classmethod
    def set_ctx_mode__sculpt(cls, context: bpy.types.Context | None = None) -> None:
        cls._set_ctx_mode(context, 'SCULPT')


class BM(Enum):
    SCULPT = auto()
    TEXTURE_PAINT = auto()
    GPENCIL_PAINT = auto()

    def __call__(self, context: bpy.types.Context | None = None) -> bm_types.AddonDataByMode:
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

    selected_brushes: bm_types.Brush_Collection = property(lambda self: self().selected_brushes)
    selected_textures: bm_types.Brush_Collection = property(lambda self: self().selected_textures)

    def load_select_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        self(context).select_brush(context, brush)

    def reset_brush_to_default(self, context: bpy.types.Context, uuid_or_index: int or str) -> None:
        data = self(context)
        uuid = data.get_brush_uuid(uuid_or_index) if isinstance(uuid_or_index, int) else uuid_or_index
        brush = data.get_brush(uuid)
        brush.reset()
        brush.select(context)

        # Load brush again from lib (will load default since we replaced it).
        data.select_brush(context, uuid)

    def save_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        if isinstance(brush, bm_data.Brush_Collection):
            pass
        else:
            data = self(context)
            uuid = data.get_brush_uuid(brush) if isinstance(brush, int) else brush
            brush = data.get_brush(uuid)
        brush.save()

    def save_default_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        if isinstance(brush, bm_data.Brush_Collection):
            pass
        else:
            data = self(context)
            uuid = data.get_brush_uuid(brush) if isinstance(brush, int) else brush
            brush = data.get_brush(uuid)
        brush.save(save_default=True)


    # ----------------------------------------------------------------

    def load_default_brush_cat(self, context: bpy.types.Context, cat: int or str) -> None:
        data = self(context)
        cat: bm_types.BrushCategory = data.get_brush_cat(cat)
        if cat is None:
            return
        for brush in cat.get_items(data):
            brush.load()

    def save_default_brush_cat(self, context: bpy.types.Context, cat: int or str) -> None:
        data = self(context)
        cat: bm_types.BrushCategory = data.get_brush_cat(cat)
        if cat is None:
            return
        for brush in cat.get_items(data):
            brush.save(save_default=True)



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
