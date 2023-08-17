import bpy
from bpy.types import Brush as BlBrush, Texture as BlTexture, ToolSettings



def get_ts(context: bpy.types.Context) -> ToolSettings:
    mode = context.mode
    if mode == 'PAINT_GPENCIL':
        mode = 'GPENCIL_PAINT'
    mode = mode.lower()

    return getattr(context.tool_settings, mode)

def get_ts_brush() -> BlBrush:
    return get_ts(bpy.context).brush

def get_ts_brush_texture_slot() -> bpy.types.BrushTextureSlot:
    if bl_brush := get_ts_brush():
        return bl_brush.texture_slot
    return None

def set_ts_brush(context: bpy.types.Context, brush: BlBrush) -> None:
    get_ts(context).brush = brush

def set_ts_texture(context: bpy.types.Context, texture: BlTexture) -> None:
    get_ts(context).brush.texture_slot.texture = texture
