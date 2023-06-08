from bpy.types import PropertyGroup
from bpy.props import PointerProperty, CollectionProperty



class PG_texture(PropertyGroup):
    pass


class PG_texture_cat(PropertyGroup):
    ''' Root PG. Via AddonPreferences. '''
    textures : CollectionProperty(type=PG_texture)
