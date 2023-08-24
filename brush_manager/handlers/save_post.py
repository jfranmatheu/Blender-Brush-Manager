import bpy
from bpy.app import handlers


@handlers.persistent
def save_brushes(*args):
    print("[brush_manager] on_save_post::save_brushes()")
    from ..data import AddonData
    AddonData.save_all()


def register():
    handlers.save_post.append(save_brushes)

def unregister():
    if save_brushes in handlers.save_post:
        handlers.save_post.remove(save_brushes)
