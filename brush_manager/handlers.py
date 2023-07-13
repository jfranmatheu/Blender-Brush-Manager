import bpy
from bpy.app import handlers

import atexit


first_time = True


@handlers.persistent
def load_brushes(*args):
    print("on_load_post::load_brushes()")
    from .types import AddonData
    addon_data = AddonData.get_data(bpy.context)
    addon_data.load_brushes()

@handlers.persistent
def save_brushes(*args):
    print("on_save_post::save_brushes()")
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


@atexit.register
def on_quit():
    global first_time
    if not first_time:
        return
    print("atexit::on_quit()")
    first_time = False


def register():
    global first_time
    first_time = True

    handlers.save_post.append(save_brushes)
    handlers.load_post.append(load_brushes)


def unregister():
    if load_brushes in handlers.load_post:
        handlers.load_post.remove(load_brushes)
    if save_brushes in handlers.save_post:
        handlers.save_post.remove(save_brushes)
