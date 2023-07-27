import bpy
from bpy.types import PropertyGroup, UILayout, ID, Context, WindowManager as WM, Brush as BlBrush, Texture as BlTexture, ToolSettings
from gpu.types import GPUTexture
from bpy.props import StringProperty

from enum import Enum, auto
import os
from os.path import basename, exists, isfile
from uuid import uuid4
from pathlib import Path
from collections import defaultdict, OrderedDict
from shutil import copyfile
import shelve
import pickle

from .paths import Paths
from .icons import get_preview, get_gputex, create_preview_from_filepath, clear_icon



load_lib = None
write_lib = None

IconPath = Paths.Icons
DataPath = Paths.DATA


class ContextModes(Enum):
    SCULPT = auto()
    TEXTURE_PAINT = auto()
    GPENCIL_PAINT = auto()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


temp_properties: list[str] = []


def ensure_temp_property(context: Context, item: 'IconHolder', attr: str):
    wm = context.window_manager
    prop_name = item.uuid + attr
    prop_value = getattr(item, attr)
    if not hasattr(wm, prop_name):
        setattr(WM, prop_name, StringProperty(
            name=prop_name.title(),
            default=prop_value,
            update=lambda self, _ctx: setattr(item, attr, getattr(self, prop_name))
        ))
        temp_properties.append(prop_name)
    return prop_name


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class IdHolder:
    # Internal props.
    uuid: str

    # Mutable by user.
    name: str

    def __init__(self, name: str) -> None:
        self.uuid = uuid4().hex
        self.name = name

    def draw_item_in_layout(self, context: Context, layout: UILayout) -> UILayout:
        wm = context.window_manager
        prop_name = ensure_temp_property(context, self.uuid, 'name')
        row = layout.row(align=True)
        row.prop(wm, prop_name, text='Name')
        return row


class IconHolder(IdHolder):
    icon_path: IconPath = None

    @property
    def icon_filepath(self) -> str: return self.icon_path(self.uuid + '.png')
    @property
    def icon_id(self) -> int: return get_preview(self.uuid, self.icon_filepath)
    @property
    def icon_gputex(self) -> GPUTexture: return get_gputex(self.uuid, self.icon_filepath)

    def asign_icon(self, filepath: str) -> None:
        create_preview_from_filepath(self.uuid, filepath, self.icon_filepath)

    def clear_icon(self) -> None:
        clear_icon(self.uuid, self.icon_filepath)

    def draw_item_in_layout(self, context: Context, layout: UILayout, icon_scale: float = 1.0) -> UILayout:
        row = super().draw_item_in_layout(context, layout)
        row.template_icon(self.icon_id, scale=icon_scale)
        return row


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Item(IconHolder):
    # Internal props.
    owner: 'Category'
    type: str

    @property
    def id_data(self) -> ID:
        return

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name)

        # Custom Data.
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def remove(self) -> None:
        self.owner.remove_item(self)
    
    def __del__(self) -> None:
        self.clear_icon()


class BrushItem(Item):
    # Internal props.
    icon_path = IconPath.BRUSH

    @property
    def id_data(self) -> BlBrush:
        return bpy.data.brushes.get(self.uuid, None)


class TextureItem(Item):
    # Internal props.
    icon_path = IconPath.TEXTURE
    format: str

    @property
    def id_data(self) -> BlBrush:
        return bpy.data.textures.get(self.uuid, None)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Category(IconHolder):
    # Internal props.
    owner: 'AddonDataByMode'
    items: dict[str, Item]

    # Mutable by user.
    fav: bool

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def items_ids(self) -> tuple[str]:
        return self.items.keys()


    def add_item(self, item: Item) -> None:
        self.items[item.uuid] = item
    
    def remove_item(self, item: Item | str) -> None:
        uuid: str = item if isinstance(item, str) else item.uuid
        del self.items[uuid] # triggers item.__del__()


class BrushCat(Category):
    items: list[BrushItem]


class TextureCat(Category):
    items: list[TextureItem]



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class AddonDataByMode:
    # ----------------------------------------------------------------
    # Cache and database.

    _cache = {}

    @classmethod
    def get_data(cls, mode: ContextModes) -> 'AddonDataByMode':
        if data := cls._cache.get(mode):
            return data

        # Try to load data from file.
        data_filepath: Path = DataPath / mode.name

        if not data_filepath.exists():
            cls._cache[mode] = data = cls(mode)
        else:
            with data_filepath.open('rb') as data_file:
                data: AddonDataByMode = pickle.load(data_file)

        cls._cache[mode] = data
        return data


    def save(self) -> None:
        data_filepath: Path = DataPath / self.mode.name

        with data_filepath.open('wb') as data_file:
            pickle.dump(self, data_file)


    # ----------------------------------------------------------------
    # Initializing data and properties.

    mode: ContextModes

    brush_cats: OrderedDict[BrushCat]
    texture_cats: OrderedDict[TextureCat]


    def __init__(self, mode: ContextModes) -> None:
        self.mode = mode

        self.brush_cats = OrderedDict()
        self.texture_cats = OrderedDict()
    
    
    def import_lib() -> None:


    # ----------------------------------------------------------------
    # Local Methods (per context mode).

    def _new_cat(self, cat_type: str, cat_name: str | None = None) -> Category:
        cat_name: str = cat_name if cat_name is None else 'New Category'
        if cat_type == 'BRUSH':
            cat = BrushCat(cat_name)
            cat_dict = self.brush_cats
        else:
            cat = TextureCat(cat_name)
            cat_dict = self.texture_cats
        cat.owner = self
        cat_dict[cat.uuid] = cat
        return cat

    def new_brush_cat(self, cat_name: str | None = None) -> BrushCat:
        return self._new_cat('BRUSH', cat_name)
    
    def new_texture_cat(self, cat_name: str | None = None) -> TextureCat:
        return self._new_cat('TEXTURE', cat_name)




class AddonData:
    SCULPT = AddonDataByMode.get_data(mode=ContextModes.SCULPT)
    TEXTURE_PAINT = AddonDataByMode.get_data(mode=ContextModes.TEXTURE_PAINT)
    GPENCIL_PAINT = AddonDataByMode.get_data(mode=ContextModes.GPENCIL_PAINT)

    # ----------------------------------------------------------------
    # global methods.

    @staticmethod
    def save_all() -> None:
        for ctx_mode in ContextModes:
            AddonDataByMode.get_data(mode=ctx_mode).save()



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def unregister():
    for prop_name in temp_properties:
        delattr(WM, prop_name)
