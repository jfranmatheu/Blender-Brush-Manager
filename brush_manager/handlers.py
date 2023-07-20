import bpy
from bpy.app import handlers, timers

import atexit


first_time = True


@handlers.persistent
def initialize(*args):
    print("[brush_manager] on_load_post::initialize()")
    from .types import AddonData
    addon_data = AddonData.get_data(bpy.context)
    addon_data.initialize()

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


@atexit.register
def on_quit():
    global first_time
    if not first_time:
        return
    print("[brush_manager] atexit::on_quit()")
    first_time = False


def __dev__load_post_timer():
    print("[brush_manager] timers::__dev__load_post_timer()")
    # IN CASE OF DEVELOPMENT ENV, The handlers are broken because of who knows.
    initialize()
    return None


def register():
    global first_time
    first_time = True

    handlers.save_post.append(save_brushes)
    handlers.load_post.append(initialize)

    timers.register(__dev__load_post_timer, first_interval=1, persistent=True)


def unregister():
    if initialize in handlers.load_post:
        handlers.load_post.remove(initialize)
    if save_brushes in handlers.save_post:
        handlers.save_post.remove(save_brushes)

    if timers.is_registered(__dev__load_post_timer):
        timers.unregister(__dev__load_post_timer)
