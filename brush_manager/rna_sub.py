import bpy
from bpy.types import Brush as BlBrush, Texture as BlTexture

from uuid import uuid4

from brush_manager.utils.tool_settings import get_ts, get_ts_brush, get_ts_brush_texture_slot


sub_owners = {}


def on_brush_update(brush: BlBrush, key: str):
    if brush is None:
        return
    print("Brush '%s' Datablock -> '%s' value was changed!" % (brush.name, key))

    brush['dirty'] = True


def on_brush_texture_slot_update(brush: BlBrush, key: str):
    if brush is None:
        return
    texture_slot = brush.texture_slot
    if texture_slot is None:
        return
    print("BrushTextureSlot '%s' Datablock -> '%s' value was changed!" % (texture_slot.name, key))

    brush['dirty'] = True

    texture = texture_slot.texture
    if texture and 'uuid' not in texture:
        texture['uuid'] = uuid4().hex
        texture['dirty'] = True


def on_brush_texture_update(brush: BlBrush, _key: str):
    if brush is None:
        return
    print("Brush '%s' Datablock -> texture value was changed!" % brush.name)
    texture = brush.texture
    if texture is None:
        brush['texture_uuid'] = ''

        brush['dirty'] = True
    else:
        if 'uuid' not in texture:
            texture['uuid'] = uuid4().hex
            texture['dirty'] = True

        brush['texture_uuid'] = texture['uuid']

        brush['dirty'] = True


def register_prop(type, attr, notify: callable, get_data: callable):
    owner = object()
    sub_owners[owner] = attr

    bpy.msgbus.subscribe_rna(
        key=(type, attr),
        owner=owner,
        args=(),
        notify=lambda *args: notify(get_data(), sub_owners[owner]),
        options={'PERSISTENT'}
    )


def register():
    if sub_owners:
        print("[brush_manager] WARN! There are owners already registered for RNA subscription!")
        sub_owners.clear()

    def _register_after_load():
        brush = bpy.data.brushes[0]
        for key, prop in brush.rna_type.properties.items():
            if prop.type in {'POINTER', 'COLLECTION'}:
                continue
            #### print("[brush_manager] Info! RNA Subscription to bpy.types.Brush." + key)
            register_prop(bpy.types.Brush, key, on_brush_update, get_ts_brush)

        for key, prop in brush.texture_slot.rna_type.properties.items():
            if prop.type in {'POINTER', 'COLLECTION'}:
                continue
            #### print("[brush_manager] Info! RNA Subscription to bpy.types.BrushTextureSlot." + key)
            register_prop(bpy.types.BrushTextureSlot, key, on_brush_texture_slot_update, get_ts_brush)

        #### print("[brush_manager] Info! RNA Subscription to bpy.types.Brush.texture")
        register_prop(bpy.types.BrushTextureSlot, 'texture', on_brush_texture_update, get_ts_brush)

    bpy.app.timers.register(_register_after_load, first_interval=1)


def unregister():
    for owner in sub_owners.keys():
        bpy.msgbus.clear_by_owner(owner)
