import bpy
from bpy.types import PropertyGroup, Context, WindowManager as WM, Brush, Texture, ToolSettings
from bpy.props import StringProperty, PointerProperty, EnumProperty, IntProperty, CollectionProperty, BoolProperty, FloatVectorProperty
from gpu.types import GPUTexture

from os.path import basename, exists, isfile
from uuid import uuid4
from collections import defaultdict

from .paths import Paths
from .icons import get_preview, get_gputex


IconPath = Paths.Icons


lib_items_cache: dict[str, set[str]] = {}


get_brush_names_by_ctx_mode = {
    'sculpt': ('Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb'),
    'texture_paint': (
        'TexDraw',

        'Soften',
        'Smear',

        'Clone',

        'Fill',

        'Mask'),
    'gpencil_paint': (
        'Airbrush',
        'Ink Pen',
        'Ink Pen Rough',
        'Marker Bold',
        'Marker Chisel',
        'Pen',
        'Pencil',
        'Pencil Soft',

        'Fill Area',

        'Eraser Hard',
        'Eraser Point',
        'Eraser Soft',
        'Eraser Stroke',

        'Tint',)
}


# ----------------------------------------------------------------


def get_ts(context: bpy.types.Context) -> 'Brush_BM':
    mode = context.mode
    if mode == 'PAINT_GPENCIL':
        mode = 'GPENCIL_PAINT'
    mode = mode.lower()

    return getattr(context.tool_settings, mode)

def get_ts_brush() -> 'Brush_BM':
    return get_ts(bpy.context).brush

def get_ts_brush_texture_slot() -> bpy.types.BrushTextureSlot:
    if bl_brush := get_ts_brush():
        return bl_brush.texture_slot
    return None

def set_ts_brush(context: bpy.types.Context, brush: 'Brush_BM') -> None:
    get_ts(context).brush = brush


# ----------------------------------------------------------------


def get_item_at_index(list, index: int):
    if index < 0 or index >= len(list):
        return None
    return list[index]

def get_item_by_uuid(list, uuid: str):
    for item in list:
        if item.uuid == uuid:
            return item
    return None

def get_item(list, item: str | int):
    if isinstance(item, int):
        return get_item_at_index(list, item)
    if isinstance(item, str):
        return get_item_by_uuid(list, item)
    return None

def get_item_index(list, uuid_or_ref: str | object) -> int | None:
    if isinstance(uuid_or_ref, str):
        for index, item in enumerate(list):
            if item.uuid == uuid_or_ref:
                return index
    else:
        for index, item in enumerate(list):
            if item == uuid_or_ref:
                return index


def remove_item(list: list, item: int | str):
    if isinstance(item, int):
        list.remove(item)
    elif isinstance(item, str):
        for idx, _item in enumerate(list):
            if _item.uuid == item:
                return remove_item(idx)


# ----------------------------------------------------------------


class IconHolder:
    @property
    def icon_path(self) -> IconPath: pass
    @property
    def icon_id(self) -> int: return get_preview(self.uuid, self.icon_path(self.uuid + '.png'))
    @property
    def icon_gputex(self) -> GPUTexture: return get_gputex(self.uuid, self.icon_path(self.uuid + '.png'))


class UUUIDHolder:
    uuid: StringProperty()

    def generate_uuid(self) -> None:
        self.uuid = uuid4().hex


class CollectionItem(UUUIDHolder, IconHolder):
    name : StringProperty()


# ----------------------------------------------------------------


class LibraryBrush_Collection(CollectionItem, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.BRUSH

class LibraryTexture_Collection(CollectionItem, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.TEXTURE


class Library_Collection(UUUIDHolder, PropertyGroup):
    def update_filepath(self, context: Context):
        self.name = basename(self.filepath)[:-6]

    filepath : StringProperty(update=update_filepath)
    name : StringProperty()
    brushes: CollectionProperty(type=LibraryBrush_Collection)
    textures: CollectionProperty(type=LibraryTexture_Collection)

    @property
    def is_valid(self) -> bool:
        return exists(self.filepath) and isfile(self.filepath)

    @property
    def brushes_ids(self) -> set[str]:
        if ids := lib_items_cache.get(self.uuid, None):
            return ids
        ids = {brush.uuid for brush in self.brushes}
        lib_items_cache[self.uuid] = ids
        return ids


# ----------------------------------------------------------------


class Item(UUUIDHolder, IconHolder):
    name: StringProperty()
    type: StringProperty()
    selected: BoolProperty(name="Select Item")


class Brush_Collection(Item, PropertyGroup):
    use_custom_icon: BoolProperty(name="Brush Use Custom Icon")
    texture_uuid: StringProperty(name="UUID of linked texture")

    @property
    def icon_path(self) -> str:
        return IconPath.BRUSH

    @property
    def bl_brush(self) -> Brush or None:
        return bpy.data.brushes.get(self.uuid, None)

    @property
    def bl_texture(self) -> Texture or None:
        return bpy.data.textures.get(self.texture_uuid, None)


class Texture_Collection(Item, PropertyGroup):
    format: StringProperty()

    @property
    def icon_path(self) -> str:
        return IconPath.TEXTURE

    @property
    def bl_texture(self) -> Texture or None:
        return bpy.data.textures.get(self.uuid, None)


# ----------------------------------------------------------------


class CategoryItem_Brush(CollectionItem, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.BRUSH

class CategoryItem_Texture(CollectionItem, PropertyGroup):
    @property
    def icon_path(self) -> str:
        return IconPath.TEXTURE


class Category(UUUIDHolder, IconHolder):
    name: StringProperty()
    load_on_boot: BoolProperty(name="Load on Boot", description="Load Category Brushes On Blender Boot", default=False)

    def add_item(self, uuid: str) -> CategoryItem_Brush | CategoryItem_Texture:
        new_item = self.items.add()
        new_item.uuid = uuid
        return new_item

    def remove_item(self, item: int | str) -> None:
        remove_item(self.items, item)

    def clear(self):
        self.items.clear()

class BrushCat_Collection(Category, PropertyGroup):
    items: CollectionProperty(type=CategoryItem_Brush)

    @property
    def icon_path(self) -> str:
        return IconPath.CAT_BRUSH

class TextureCat_Collection(Category, PropertyGroup):
    items: CollectionProperty(type=CategoryItem_Texture)

    @property
    def icon_path(self) -> str:
        return IconPath.CAT_TEXTURE


# ----------------------------------------------------------------


class UIProps(PropertyGroup):
    ui_active_item_color: FloatVectorProperty(size=4, default=(0.15, 0.6, 1.0, 1.0), subtype='COLOR')
    ui_active_section: EnumProperty(
        name="Active Section",
        items=(
            ('LIBS', 'Libraries', "", 'FILE_BLEND', 0),
            ('CATS', 'Categories', "", 'ASSET_MANAGER', 1)
        )
    )

    @property
    def ui_in_libs_section(self) -> bool: return self.ui_active_section == 'LIBS'

    @property
    def ui_in_cats_section(self) -> bool: return self.ui_active_section == 'CATS'

    # ----------------------------

    ui_context_mode: EnumProperty(
        items=(
            ('sculpt', 'Sculpt', '', 'SCULPTMODE_HLT', 0),
            ('texture_paint', 'Texture Paint', '', 'TEXTURE_DATA', 1),
            ('gpencil_paint', 'Grease Pencil', '', 'OUTLINER_DATA_GP_LAYER', 2),
        )
    )

    ui_item_type_context: EnumProperty(
        name="Item-Type Context",
        items=(
            ('BRUSH', 'Brushes', ""),
            ('TEXTURE', 'Textures', "")
        ),
        default='BRUSH'
    )

    @property
    def ui_in_brush_context(self) -> bool: return self.ui_item_type_context == 'BRUSH'

    @property
    def ui_in_texture_context(self) -> bool: return self.ui_item_type_context == 'TEXTURE'


class AddonDataByMode(PropertyGroup):
    cache_items = {}

    libraries: CollectionProperty(type=Library_Collection)
    brushes: CollectionProperty(type=Brush_Collection)
    textures: CollectionProperty(type=Texture_Collection)
    brush_cats: CollectionProperty(type=BrushCat_Collection)
    texture_cats: CollectionProperty(type=TextureCat_Collection)

    # ----------------------------

    active_library_index: IntProperty(default=-1)

    @property
    def active_library(self) -> Library_Collection:
        items = self.libraries
        index = self.active_library_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    # ----------------------------

    def get_active_category(self, type: str) -> BrushCat_Collection | TextureCat_Collection | None:
        if type == 'BRUSH':
            return self.active_brush_cat
        elif type == 'TEXTURE':
            return self.active_texture_cat
        return None

    active_brush_cat_index: IntProperty(default=-1)
    active_texture_cat_index: IntProperty(default=-1)

    @property
    def active_brush_cat(self) -> BrushCat_Collection:
        items = self.brush_cats
        index = self.active_brush_cat_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    @property
    def active_texture_cat(self) -> TextureCat_Collection:
        items = self.texture_cats
        index = self.active_texture_cat_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    # ----------------------------

    active_item_index: IntProperty(default=-1)

    def active_item(self):
        if self.ui_in_libs_section:
            active_lib = self.active_library
            if self.ui_in_brush_context:
                items = active_lib.brushes
            elif self.ui_in_texture_context:
                items = active_lib.textures
            else:
                return None
        elif self.ui_in_cats_section:
            if self.ui_in_brush_context:
                items = self.active_brush_cat.items
            elif self.ui_in_texture_context:
                items = self.active_texture_cat.items
            else:
                return None
        else:
            return None
        if items is None:
            return None
        index = self.active_item_index
        if index < 0 or index >= len(items):
            return None
        return items[index]

    # ----------------------------

    def get_library(self, index_or_uuid: int | str):
        return get_item(self.libraries, index_or_uuid)

    def remove_library(self, index: int = -1):
        if index < 0:
            index = self.active_library_index
        lib: Library_Collection = self.get_library(index)
        if lib is None:
            return

        brush_uuids = {brush.uuid for brush in lib.brushes}
        texture_uuids = {texture.uuid for texture in lib.textures}

        for idx, brush in reversed(list(enumerate(self.brushes))): # enumerate(reversed(self.brushes)):
            if brush.uuid in brush_uuids:
                self.remove_brush(idx)
            elif brush.texture_uuid in texture_uuids:
                brush.texture_uuid = ''

        for idx, texture in reversed(list(enumerate(self.textures))): # enumerate(reversed(self.textures)):
            if texture.uuid in texture_uuids:
                self.remove_texture(idx)

        for cat in self.brush_cats:
            for idx, item in reversed(list(enumerate(cat.items))): # enumerate(reversed(cat.items)):
                if item.uuid in brush_uuids:
                    cat.remove_item(idx)

        for cat in self.texture_cats:
            for idx, item in reversed(list(enumerate(cat.items))): # enumerate(reversed(cat.items)):
                if item.uuid in texture_uuids:
                    cat.remove_item(idx)

        self.libraries.remove(index)

    # ----------------------------

    def get_brush_cat(self, index_or_uuid: int | str):
        return get_item(self.brush_cats, index_or_uuid) # get_item_at_index(self.brush_cats, index)

    def get_texture_cat(self, index_or_uuid: int | str):
        return get_item(self.brush_cats, index_or_uuid) # get_item_at_index(self.texture_cats, index)

    def remove_brush_cat(self, cat: int | str):
        remove_item(self.brush_cats, cat)

    def remove_texture_cat(self, cat: int | str):
        remove_item(self.texture_cats, cat)

    def set_active_brush_category(self, index_or_uuid: int | str) -> None:
        if not isinstance(index_or_uuid, int):
            self.active_brush_cat_index = get_item_index(self.brush_cats, index_or_uuid)
        else:
            self.active_brush_cat_index = index_or_uuid

    def set_active_texture_category(self, index_or_uuid: int | str) -> None:
        if not isinstance(index_or_uuid, int):
            self.active_texture_cat_index = get_item_index(self.texture_cats, index_or_uuid)
        else:
            self.active_texture_cat_index = index_or_uuid

    # ----------------------------

    def load_select_brush(self, context: Context, brush: int | str) -> None:
        # Resolve brush UUID.
        brush_uuid = brush if isinstance(brush, str) else self.get_brush_uuid(brush)
        if not brush_uuid:
            return

        # The brush exists!
        if bl_brush := bpy.data.brushes.get(brush_uuid, None):
            return bl_brush

        # Load the brush from BM library.
        with bpy.data.libraries.load(Paths.Data.BRUSH(self.uuid + '.blend'), link=False) as (data_from, data_to):
            data_to.brushes = [self.uuid] # data_from.brushes
        bl_brush = bpy.data.brushes[self.uuid]
        bl_brush.use_fake_user = False # Make sure it does not use fake user so Blender free it on quit.

        # Check if brush has a texture that we need to import.
        texture_uuid = bl_brush['texture_uuid']
        if texture_uuid != '':
            # Load the texture from BM library.
            with bpy.data.libraries.load(Paths.Data.TEXTURE(texture_uuid + '.blend'), link=False) as (data_from, data_to):
                data_to.textures = [texture_uuid]
                data_to.images = data_from.images
            bl_texture = bpy.data.textures[texture_uuid]
            bl_texture.use_fake_user = False # Make sure it does not use fake user so Blender free it on quit.

            # Ensure texture is asigned to the brush.
            bl_brush.texture_slot.texture = bl_texture

        # Set active brush.
        set_ts_brush(context, bl_brush)


    def get_blbrush(self, uuid: str) -> Brush:
        return bpy.data.brushes.get(uuid, None)

    def get_bltexture(self, uuid: str) -> Texture:
        return bpy.data.textures.get(uuid, None)


    def get_brush_data(self, uuid: str) -> Brush_Collection:
        if not uuid:
            return None
        if brush := self.cache_items.get(uuid, None):
            return brush
        return next(brush for brush in self.brushes if brush.uuid == uuid)

    def get_texture_data(self, uuid: str) -> Texture_Collection:
        if not uuid:
            return None
        if texture := self.cache_items.get(uuid, None):
            return texture
        return next(tex for tex in self.textures if tex.uuid == uuid)


    def get_brush_uuid(self, index: int):
        return get_item_at_index(self.brushes, index).uuid

    def get_texture_uuid(self, index: int):
        return get_item_at_index(self.textures, index).uuid

    def remove_brush(self, brush: int | str):
        remove_item(self.brushes, brush)

    def remove_texture(self, texture: int | str):
        remove_item(self.textures, texture)

    @property
    def selected_brushes(self) -> list[Brush_Collection]:
        return [br for br in self.brushes if br.selected]

    @property
    def selected_textures(self) -> list[Texture_Collection]:
        return [tex for tex in self.textures if tex.selected]


    # -----------------------------------------------

    def load_brushes(self, ctx_mode: str = 'sculpt') -> None:
        if len(self.brushes) == 0 or len(self.brush_cats) == 0:
            cat: BrushCat_Collection = self.brush_cats.add()
            cat.uuid = 'DEFAULT'
            cat.name = 'Default Brushes'
            cat_items = cat.items
            data_brushes = bpy.data.brushes
            for br_name in get_brush_names_by_ctx_mode[ctx_mode]:
                if brush := data_brushes.get(br_name, None):
                    cat_item: CategoryItem_Brush = cat_items.add()
                    cat_item.uuid = brush['uuid'] = 'DEFAULT_' + br_name
                    cat_item.name = br_name

        rel_brush_id_n_name = {item.uuid: item.name for cat in self.brush_cats if not cat.load_on_boot for item in cat.items}
        brush_uuids = set(rel_brush_id_n_name.keys())
        rel_lib_n_brushes: dict[str, list[str]] = defaultdict(list)

        for lib in self.libraries:
            if not lib.is_valid:
                continue
            brushes_ids_to_load_from_lib = brush_uuids.intersection(lib.brushes_ids)
            rel_lib_n_brushes[lib.filepath] = {rel_brush_id_n_name[brush_id] for brush_id in brushes_ids_to_load_from_lib}

        for libpath, brushes in rel_lib_n_brushes.items():
            # link all objects starting with 'A'
            with bpy.data.libraries.load(libpath, link=True) as (data_from, data_to):
                data_to.brushes = [name for name in data_from.brushes if name in brushes]


    def save_brushes(self, ctx_mode: str = 'sculpt') -> None:
        for brush in self.brushes:
            brush.save()


class AddonData(PropertyGroup):
    ctx_modes = ('sculpt', 'texture_paint', 'gpencil_paint')

    sculpt: PointerProperty(type=AddonDataByMode)
    texture_paint: PointerProperty(type=AddonDataByMode)
    gpencil_paint: PointerProperty(type=AddonDataByMode)

    def load_brushes(self) -> None:
        for ctx_mode in self.ctx_modes:
            getattr(self, ctx_mode).load_brushes(ctx_mode)

    def save_brushes(self) -> None:
        for ctx_mode in self.ctx_modes:
            getattr(self, ctx_mode).save_brushes(ctx_mode)


class Brush_BM(PropertyGroup):
    uuid = property(lambda self: self.id_data['uuid']) # StringProperty(name="Brush UUID", description="Used by Brush Manager")
    icon_id = property(lambda self: get_preview(self.uuid, IconPath.BRUSH(self.uuid + '.png')))
    icon_gputex = property(lambda self: get_gputex(self.uuid, IconPath.BRUSH(self.uuid + '.png')))

    texture_uuid = property(lambda self: self.id_data['texture_uuid']) # StringProperty(name="Texture UUID", description="Used by Brush Manager")
    texture_icon_id = property(lambda self: get_preview(self.texture_uuid, IconPath.TEXTURE(self.texture_uuid + '.png')))
    texture_icon_gputex = property(lambda self: get_gputex(self.texture_uuid, IconPath.TEXTURE(self.texture_uuid + '.png')))

    def save(self) -> None:
        brush_libpath = Paths.Data.BRUSH(self.uuid + '.blend', as_path=True)
        bpy.data.libraries.write(str(brush_libpath), {self.id_data}, fake_user=True, compress=True)



class Texture_BM(PropertyGroup):
    uuid = property(lambda self: self.id_data['uuid']) # StringProperty(name="Texture UUID", description="Used by Brush Manager")
    icon_id = property(lambda self: get_preview(self.uuid, IconPath.TEXTURE(self.uuid + '.png')))
    icon_gputex = property(lambda self: get_gputex(self.uuid, IconPath.TEXTURE(self.uuid + '.png')))

    def save(self, save_default: bool = False) -> None:
        if save_default:
            filename = self.uuid + '.default.blend'
        else:
            filename = self.uuid + '.blend'
        texture_libpath = Paths.Data.BRUSH(filename, as_path=True)
        bpy.data.libraries.write(str(texture_libpath), {self.id_data}, fake_user=True, compress=True)


def register():
    WM.brush_manager_ui = PointerProperty(type=UIProps)

    # Brush.name = StringProperty(name="Brush Name", description="Override of brush name by Brush Manager")
    # Texture.name = StringProperty(name="Texture Name", description="Override of texture name by Brush Manager")

    Brush.bm = PointerProperty(type=Brush_BM)
    Texture.bm = PointerProperty(type=Texture_BM)


def unregister():
    del WM.brush_manager_ui
