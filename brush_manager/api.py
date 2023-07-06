from enum import Enum, auto
from brush_manager import types as bm_types
import bpy


class _RuntimeUIPropsType:
    pass

class _RuntimeUIPropsForExternalAddons(bpy.types.PropertyGroup):
    pass

class _RuntimeUIPropsWrapper:
    _cache = {}

    @classmethod
    def get(cls, addon_idname: str) ->  '_RuntimeUIPropsForExternalAddons':
        ''' addon_idname: the module name of the addon. '''
        if addon_idname not in cls._cache:
            setattr(bpy.types.Scene, 'brush_manager_' + addon_idname)
            cls._cache[addon_idname] = 'scene.brush_manager_' + addon_idname
        return cls._cache[addon_idname]


class BMData(Enum):
    SCULPT = auto()
    TEXTURE_PAINT = auto()
    GP_DRAW = auto()

    def __call__(self) -> bm_types.AddonDataByMode:
        return bm_types.AddonData.get_data_by_ui_mode(self.name.lower())

    brushes: bm_types.Brush_Collection = property(lambda self: self().brushes)
    textures: bm_types.Texture_Collection = property(lambda self: self().textures)
    brush_cats: bm_types.BrushCat_Collection = property(lambda self: self().brush_cats)
    texture_cats: bm_types.TextureCat_Collection = property(lambda self: self().texture_cats)

    active_brush_cat: bm_types.BrushCategory = property(lambda self: self().active_brush_cat)
    active_texture_cat: bm_types.TextureCategory = property(lambda self: self().active_texture_cat)
