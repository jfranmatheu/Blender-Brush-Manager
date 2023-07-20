import bpy
from bpy.types import Context, Brush as BlBrush, Texture as BlTexture, ImageTexture as BlImageTexture
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
    brushes: UUID
    textures: UUID

    @property
    def is_valid(self) -> bool: pass

    @property
    def brushes_ids(self) -> set[str]: pass

    def add_brush(self, brush_data: 'Brush') -> UUID: pass
    def add_texture(self, texture_data: 'Texture') -> UUID: pass
    
    def get_brushes(self, addon_data: 'AddonDataByMode') -> list['Brush']: pass
    def get_textures(self, addon_data: 'AddonDataByMode') -> list['Texture']: pass


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


class Texture(Item):
    format: str

    bl_texture: BlTexture | None

    def load(self, link: bool = False) -> None: pass
    def save(self) -> None: pass


class Brush(Item):
    texture: Texture

    use_custom_icon: bool
    texture_uuid: str

    bl_brush: BlBrush | None
    bl_texture: BlTexture | None

    def load(self, link: bool = False) -> None: pass
    def save(self, save_default: bool = False) -> None: pass


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


class BrushPointer:
    data: Brush_Collection

class TexturePointer:
    data: Texture_Collection


# ----------------------------------------------------------------


class Category(UUID, IconHolder):
    name: str
    load_on_boot: bool

    @property
    def item_ids(self) -> tuple[str]: pass

    def add_item(self, item_data: Brush | Texture) -> UUID: pass # BrushPointer | TexturePointer: pass
    def remove_item(self, index_or_uuid: int | str) -> None: pass
    def clear(self) -> None: pass


class BrushCategory(Category):
    x_items: list[UUID] # BrushPointer

    # @property
    # def items(self) -> list[Brush]: pass
    def get_items(self, addon_data: 'AddonDataByMode') -> list[Brush]: pass

    def load_default(self) -> None: pass
    def save_default(self) -> None: pass

class TextureCategory(Category):
    x_items: list[UUID] # TexturePointer

    # @property
    # def items(self) -> list[Texture]: pass
    def get_items(self, addon_data: 'AddonDataByMode') -> list[Texture]: pass


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
            'PAINT_GPENCIL': 'gpencil_paint',
        }
        if ui_ctx_mode := get_ui_ctx_mode.get(mode, None):
            self.ui_context_mode = ui_ctx_mode
            return True
        return False


class AddonDataByMode:
    cached_indices: dict[str, int]
    def _get_item_index(self, uuid: str) -> int: pass
    def _update_indices(self) -> None: pass

    # ------------------------------

    libraries: Library_Collection
    brushes: Brush_Collection
    textures: Texture_Collection
    brush_cats: BrushCat_Collection
    texture_cats: TextureCat_Collection


    # ----------------------------
    # --- UI management ---
    @property
    def selected_brushes(self) -> list[Brush_Collection]: pass

    @property
    def selected_textures(self) -> list[Texture_Collection]: pass


    # ----------------------------
    # Libraries.

    active_library_index: int
    active_library: Library

    def get_library(self, index_or_uuid: int | str) -> Library: pass
    def remove_library(self, index_or_uuid: int | str = -1) -> None: pass


    # ----------------------------
    # Categories.

    active_brush_cat_index: int
    active_texture_cat_index: int
    active_brush_cat: BrushCategory
    active_texture_cat: TextureCategory

    def get_active_category(self, type: str) -> BrushCategory | TextureCategory: pass

    def get_brush_cat(self, index_or_uuid: int | str) -> BrushCategory: pass
    def get_texture_cat(self, index_or_uuid: int | str) -> TextureCategory: pass

    def remove_brush_cat(self, cat: int | str) -> None: pass
    def remove_texture_cat(self, cat: int | str) -> None: pass

    def select_brush_category(self, index_or_uuid: int | str) -> None: pass
    def select_texture_category(self, index_or_uuid: int | str) -> None: pass


    # ----------------------------
    # Brush/Texture Utilities.

    def get_brush_index(self, uuid: str) -> int: pass
    def get_texture_index(self, uuid: str) -> int: pass
    def get_brush_uuid(self, index: int) -> str: pass
    def get_texture_uuid(self, index: int) -> str: pass

    def get_brush(self, uuid: str) -> Brush: pass
    def get_texture(self, uuid: str) -> Texture: pass

    def get_blbrush(self, uuid: str) -> BlBrush: pass
    def get_bltexture(self, uuid: str) -> BlTexture: pass


    # ----------------------------
    # Brush/Texture Management.

    active_brush_index: int
    active_brush: Brush

    active_texture_index: int
    active_texture: Texture

    def select_brush(self, index_or_uuid: int | str) -> None: pass
    def select_texture(self, index_or_uuid: int | str) -> None: pass

    def remove_brush(self, brush: int | str) -> None: pass
    def remove_texture(self, texture: int | str) -> None: pass


    # ------------------------------
    # Utility methods.

    def initialize(self) -> None: pass
    def load_brushes(self) -> None: pass
    def save_brushes(self) -> None: pass



class AddonData:
    sculpt: AddonDataByMode
    texture_paint: AddonDataByMode
    gpencil_paint: AddonDataByMode

    @staticmethod
    def get_data(context=None) -> 'AddonData':
        if not context:
            return bpy.context.preferences.addons[__package__].preferences.data
        return context.preferences.addons[__package__].preferences.data

    @classmethod
    def get_data_by_ui_mode(cls, context: Context = None, ui_context_mode: str | None = None) -> 'AddonDataByMode':
        addon_data = cls.get_data(context)
        if ui_context_mode is not None:
            return getattr(addon_data, context)
        return  getattr(addon_data, UIProps.get_data(context).ui_context_mode)

    @classmethod
    def get_data_by_ctx_mode(cls, context: Context = None) -> AddonDataByMode | None:
        if not context:
            context = bpy.context
        if not UIProps.get_data(context).switch_to_ctx_mode(context.mode):
            return None
        return cls.get_data_by_ui_mode(context)


    # ------------------------------------------------------------------------------

    def initialize(self) -> None: pass
    def load_brushes(self) -> None: pass
    def save_brushes(self) -> None: pass
