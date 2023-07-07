import bpy
from bpy.types import Context
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
    selected: bool


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
    ui_context_mode: str

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

    def switch_to_ctx_mode(self, mode: str) -> bool:
        get_ui_ctx_mode = {
            'SCULP': 'sculpt',
            'IMAGE_PAINT': 'texture_paint',
            'PAINT_GPENCIL': 'gpencil',
        }
        if ui_ctx_mode := get_ui_ctx_mode.get(mode, None):
            self.ui_context_mode = ui_ctx_mode
            return True
        return False


class AddonDataByMode:
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

    # ----------------------------

    def get_library(self, index_or_uuid: int | str) -> Library: pass
    def remove_library(self, index: int = -1) -> None: pass

    # ----------------------------

    def get_active_category(self, type: str) -> BrushCategory | TextureCategory: pass
    def get_brush_cat(self, index_or_uuid: int | str) -> BrushCategory: pass
    def get_texture_cat(self, index_or_uuid: int | str) -> TextureCategory: pass
    def remove_brush_cat(self, cat: int | str) -> None: pass
    def remove_texture_cat(self, cat: int | str) -> None: pass

    def set_active_brush_category(self, index_or_uuid: int | str) -> None: pass
    def set_active_texture_category(self, index_or_uuid: int | str) -> None: pass

    # ----------------------------

    def get_brush_data(self, uuid: str) -> Brush: pass
    def get_texture_data(self, uuid: str) -> Texture: pass

    def get_brush_uuid(self, index: int) -> str: pass
    def get_texture_uuid(self, index: int) -> str: pass
    def remove_brush(self, brush: int | str) -> None: pass
    def remove_texture(self, texture: int | str) -> None: pass

    @property
    def selected_brushes(self) -> list[Brush_Collection]: pass

    @property
    def selected_textures(self) -> list[Texture_Collection]: pass

    # ------------------------------

    def load_brushes(self) -> None: pass



class AddonData:
    sculpt: AddonDataByMode
    texture_paint: AddonDataByMode
    gpencil: AddonDataByMode

    @staticmethod
    def get_data(context=None) -> 'AddonData':
        if not context:
            return bpy.context.preferences.addons[__package__].preferences.data
        return context.preferences.addons[__package__].preferences.data

    @classmethod
    def get_data_by_ui_mode(cls, context: Context | str = None) -> 'AddonDataByMode':
        addon_data = cls.get_data(context)
        if isinstance(context, str):
            return getattr(addon_data, context)
        return  getattr(addon_data, UIProps.get_data(context).ui_context_mode)

    @classmethod
    def get_data_by_ctx_mode(cls, context=None) -> 'AddonDataByMode' or None:
        if not context:
            context = bpy.context
        if not UIProps.get_data(context).switch_to_ctx_mode(context.mode):
            return None
        return cls.get_data_by_ui_mode(context)


    # ------------------------------------------------------------------------------

    def load_brushes(self) -> None: pass
