import bpy
from bpy.types import Context
from gpu.types import GPUTexture
from mathutils import Color


from .data import (
    AddonData, AddonDataByMode,
    Category, BrushCat, TextureCat, BrushCat_Collection, TextureCat_Collection,
    Item, BrushItem, TextureItem, # BrushItem_Collection, TextureItem_Collection,
    BlBrush, BlTexture
)


class UIProps:
    ui_context_mode: str

    ui_active_item_color: Color

    ui_context_item: str
    is_ctx_brush: bool
    is_ctx_texture: bool

    @staticmethod
    def get_data(context: Context) -> 'UIProps':
        return context.window_manager.brush_manager_ui
