import bpy
from bpy.app import handlers


@handlers.persistent
def load_brushes(*args):
    from .types import AddonData
    AddonData.get_data(bpy.context).load_brushes()


def register():
    handlers.load_post.append(load_brushes)


def unregister():
    if load_brushes in handlers.load_post:
        handlers.load_post.remove(load_brushes)
