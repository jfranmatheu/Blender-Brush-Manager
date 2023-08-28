import bpy
from bpy.app import handlers

import atexit

first_time = True


@handlers.persistent
def initialize(*args):
    print("[brush_manager] load_post")


@handlers.persistent
def on_save_post(*args):
    print("[brush_manager] save_post")
    from .data import AddonData
    AddonData.save_all(save_items_id_data=True)


@atexit.register
def on_quit():
    global first_time
    if not first_time:
        return
    print("[brush_manager] atexit")
    first_time = False
    # from .data import AddonData
    # AddonData.save_all(save_items_id_data=False)


# ----------------------------------------------------------------


def register():
    handlers.load_post.append(initialize)
    handlers.save_post.append(on_save_post)


def unregister():
    if on_save_post in handlers.save_post:
        handlers.save_post.remove(on_save_post)
    if initialize in handlers.load_post:
        handlers.load_post.remove(initialize)
