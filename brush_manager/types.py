import bpy
from gpu.types import GPUTexture
from mathutils import Color


from .data import BrushCat, BrushItem, BlBrush, TextureCat, TextureItem, BlTexture, AddonData, AddonDataByMode, Category, Item


class UIProps:
    ui_context_mode: str

    ui_active_item_color: Color

    ui_context_item: str
    is_ctx_brush: bool
    is_ctx_texture: bool

    @staticmethod
    def get_data(context=None) -> 'UIProps':
        return context.window_manager.brush_manager_ui

    def switch_to_ctx_mode(self, mode: str) -> bool:
        get_ui_ctx_mode = {
            'SCULP': 'sculpt',
            'IMAGE_PAINT': 'texture_paint',
            'PAINT_GPENCIL': 'gpencil_paint',
        }
        if ui_ctx_mode := get_ui_ctx_mode.get(mode, None):
            self.ui_context_mode = ui_ctx_mode
            return True
        return False
