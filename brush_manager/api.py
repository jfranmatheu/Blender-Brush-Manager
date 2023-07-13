from enum import Enum, auto
from brush_manager import types as bm_types
from brush_manager.paths import Paths
import bpy



class BM(Enum):
    SCULPT = auto()
    TEXTURE_PAINT = auto()
    GPENCIL_PAINT = auto()

    def __call__(self) -> bm_types.AddonDataByMode:
        return bm_types.AddonData.get_data_by_ui_mode(self.name.lower())

    # ----------------------------------------------------------------
    # Category Management Methods.

    brush_cats: bm_types.BrushCat_Collection = property(lambda self: self().brush_cats)
    texture_cats: bm_types.TextureCat_Collection = property(lambda self: self().texture_cats)

    active_brush_cat: bm_types.BrushCategory = property(lambda self: self().active_brush_cat)
    active_texture_cat: bm_types.TextureCategory = property(lambda self: self().active_texture_cat)

    def set_active_brush_cat(self, category: str or int) -> None: self().set_active_brush_category(category)
    def set_active_texture_cat(self, category: str or int) -> None: self().set_active_texture_category(category)
    def remove_brush_cat(self, category: str or int) -> None: self().remove_brush_cat(category)
    def remove_texture_cat(self, category: str or int) -> None: self().remove_texture_cat(category)
    def remove_active_brush_cat(self) -> None: self.remove_brush_cat(self.active_brush_cat.uuid)
    def remove_active_texture_cat(self) -> None: self.remove_texture_cat(self.active_texture_cat.uuid)

    # ----------------------------------------------------------------
    # Category Items Management Methods.

    brushes: bm_types.Brush_Collection = property(lambda self: self().brushes)
    textures: bm_types.Texture_Collection = property(lambda self: self().textures)

    def load_select_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        self().load_select_brush(context, brush)

    def rest_brush_to_default(self, context: bpy.types.Context, brush: int or str) -> None:
        uuid = self().get_brush_uuid(brush) if isinstance(brush, int) else brush
        bl_brush = self().get_blbrush(uuid)
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
        self().load_select_brush(context, uuid)

    def save_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        uuid = self().get_brush_uuid(brush) if isinstance(brush, int) else brush
        bl_brush = self().get_blbrush(uuid)
        if bl_brush is None:
            return
        bl_brush.bm.save()

    def save_default_brush(self, context: bpy.types.Context, brush: int or str) -> None:
        uuid = self().get_brush_uuid(brush) if isinstance(brush, int) else brush
        bl_brush = self().get_blbrush(uuid)
        if bl_brush is None:
            return
        bl_brush.bm.save(save_default=True)
