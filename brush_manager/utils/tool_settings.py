import bpy
from bpy.types import Brush as BlBrush, Texture as BlTexture, ToolSettings



def get_ts(context: bpy.types.Context) -> ToolSettings | None:
    mode = context.mode
    if mode == 'PAINT_GPENCIL':
        mode = 'GPENCIL_PAINT'
    mode = mode.lower()

    return getattr(context.tool_settings, mode, None)

def get_ts_brush() -> BlBrush | None:
    if ts := get_ts(bpy.context):
        return ts.brush

def get_ts_brush_texture_slot() -> bpy.types.BrushTextureSlot | None:
    if bl_brush := get_ts_brush():
        return bl_brush.texture_slot
    return None

def set_ts_brush(context: bpy.types.Context, brush: BlBrush) -> None:
    if ts := get_ts(context):
        ts.brush = brush

def set_ts_texture(context: bpy.types.Context, texture: BlTexture) -> None:
    if ts := get_ts(context):
        ts.brush.texture_slot.texture = texture
