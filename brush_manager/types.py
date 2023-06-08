import bpy
from gpu.types import GPUTexture



class UUID:
    uuid: str

class UUID_Collection:
    def __getitem__(coll, index: int) -> UUID: pass
    def add(coll) -> UUID: pass
    def remove(coll, item_index: int) -> None: pass
    def clear(coll) -> None: pass


# ----------------------------------------------------------------


class Library:
    filepath : str
    name : str
    brushes: UUID_Collection
    textures: UUID_Collection

class Library_Collection:
    def __getitem__(coll, index: int) -> Library: pass
    def add(coll) -> Library: pass
    def remove(coll, item_index: int) -> None: pass
    def clear(coll) -> None: pass


# ----------------------------------------------------------------


class Item:
    uuid: str
    name: str
    type: str
    
    def icon_path(self) -> str: pass
    def icon_id(self) -> str | int: pass
    def icon_gputex(self) -> GPUTexture: pass

class Brush(Item):
    texture_uuid: str

class Texture(Item):
    format: str


class Brush_Collection:
    def __getitem__(coll, index: int) -> Brush: pass
    def add(coll) -> Brush: pass
    def remove(coll, item_index: int) -> None: pass
    def clear(coll) -> None: pass

class Texture_Collection:
    def __getitem__(coll, index: int) -> Texture: pass
    def add(coll) -> Texture: pass
    def remove(coll, item_index: int) -> None: pass
    def clear(coll) -> None: pass


# ----------------------------------------------------------------


class Category:
    uuid: str
    name: str
    items: UUID_Collection

    def icon_path(self) -> str: pass
    def icon_id(self) -> str | int: pass
    def icon_gputex(self) -> GPUTexture: pass

class BrushCategory(Category):
    pass

class TextureCategory(Category):
    pass


class BrushCat_Collection:
    def __getitem__(coll, index: int) -> BrushCategory: pass
    def add(coll) -> BrushCategory: pass
    def remove(coll, item_index: int) -> None: pass
    def clear(coll) -> None: pass

class TextureCat_Collection:
    def __getitem__(coll, index: int) -> TextureCategory: pass
    def add(coll) -> TextureCategory: pass
    def remove(coll, item_index: int) -> None: pass
    def clear(coll) -> None: pass


# ----------------------------------------------------------------


class AddonData:
    ui_active_section: str
    ui_in_libs_section: bool
    ui_in_cats_section: bool

    ui_item_type_context: str
    ui_in_brush_context: bool
    ui_in_texture_context: bool

    libraries: Library_Collection
    brushes: Brush_Collection
    textures: Texture_Collection
    brush_cats: BrushCat_Collection
    texture_cats: TextureCat_Collection

    active_library_index: int
    active_library: Library

    active_brush_cat_index: int
    active_texture_cat_index: int
    active_brush_cat: BrushCategory
    active_texture_cat: TextureCategory

    active_item_index: int
    active_item: UUID

    def get_data(self, context=None) -> 'AddonData':
        if not context:
            return bpy.context.preferences.addons[__package__].data
        return context.preferences.addons[__package__].data
