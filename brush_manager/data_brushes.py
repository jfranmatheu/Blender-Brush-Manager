from bpy.types import PropertyGroup
from bpy.props import PointerProperty, CollectionProperty



class PG_brush(PropertyGroup):
    pass


class PG_brush_cat(PropertyGroup):
    ''' Root PG. Via AddonPreferences. '''
    brushes : CollectionProperty(type=PG_brush)
