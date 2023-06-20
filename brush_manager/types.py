import bpy
from gpu.types import GPUTexture
from mathutils import Color


class IconHolder:
    @property
    def icon_path(self) -> str: pass
    @property
    def icon_id(self) -> int: pass
    @property
    def icon_gputex(self) -> GPUTexture: pass


class UUID(IconHolder):
    name: str # added for lib items
    uuid: str

    def generate_uuid(self) -> None: pass


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

    @property
    def is_valid(self) -> bool: pass

    @property
    def brushes_ids(self) -> set[str]: pass


class Library_Collection:
    def __getitem__(coll, index: int) -> Library: pass
    def add(coll) -> Library: pass
    def remove(coll, item_index: int) -> None: pass
    def clear(coll) -> None: pass


# ----------------------------------------------------------------


class Item(UUID, IconHolder):
    name: str
    type: str


class Brush(Item):
    use_custom_icon: bool
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


class Category(UUID, IconHolder):
    name: str
    items: UUID_Collection
    load_on_boot: bool

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


class UIProps:
    ui_active_item_color: Color

    ui_active_section: str
    ui_in_libs_section: bool
    ui_in_cats_section: bool

    ui_item_type_context: str
    ui_in_brush_context: bool
    ui_in_texture_context: bool

    @staticmethod
    def get_data(context=None) -> 'UIProps':
        return context.window_manager.brush_manager_ui


class AddonData:
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

    @staticmethod
    def get_data(context=None) -> 'AddonData':
        if not context:
            return bpy.context.preferences.addons[__package__].preferences.data
        return context.preferences.addons[__package__].preferences.data

    # ----------------------------

    def get_library(self, index: int) -> Library: pass
    def remove_library(self, index: int = -1) -> None: pass

    # ----------------------------

    def get_active_category(self, type: str) -> BrushCategory | TextureCategory: pass
    def get_brush_cat(self, index: int) -> BrushCategory: pass
    def get_texture_cat(self, index: int) -> TextureCategory: pass
    def remove_brush_cat(self, cat: int | str) -> None: pass
    def remove_texture_cat(self, cat: int | str) -> None: pass

    # ----------------------------

    def get_brush_data(self, uuid: str) -> Brush: pass
    def get_texture_data(self, uuid: str) -> Texture: pass

    def get_brush_uuid(self, index: int) -> str: pass
    def get_texture_uuid(self, index: int) -> str: pass
    def remove_brush(self, brush: int | str) -> None: pass
    def remove_texture(self, texture: int | str) -> None: pass

    # ------------------------------

    def load_brushes(self) -> None: pass