from bpy.app import handlers


@handlers.persistent
def initialize(*args):
    from brush_manager.data import AddonData
    AddonData.initialize()


def register():
    handlers.load_post.append(initialize)

def unregister():
    if initialize in handlers.load_post:
        handlers.load_post.remove(initialize)
