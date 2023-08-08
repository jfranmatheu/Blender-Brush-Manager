import bpy
from bpy.app import handlers


@handlers.persistent
def save_brushes(*args):
    print("[brush_manager] on_save_post::save_brushes()")
    # from .types import AddonData
    # addon_data = AddonData.get_data(bpy.context)
    # addon_data.save_brushes()
    for brush in bpy.data.brushes:
        if 'dirty' in brush:
            del brush['dirty']
            brush.bm.save()

    for texture in bpy.data.texture:
        if 'dirty' in texture:
            del texture['dirty']
            texture.bm.save()


def register():
    handlers.save_post.append(save_brushes)

def unregister():
    if save_brushes in handlers.save_post:
        handlers.save_post.remove(save_brushes)
