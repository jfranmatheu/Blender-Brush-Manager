import bpy
from bpy.types import Context, Texture as BlTexture
from bpy.app.timers import register as timer_register

from functools import partial
from pathlib import Path
from enum import Enum, auto
import pickle
from collections import OrderedDict

from brush_manager.pg.pg_ui import UIProps
from brush_manager.paths import Paths
from .cats import Category, BrushCat, TextureCat, BrushCat_Collection, TextureCat_Collection
from .items import BrushItem, TextureItem

from brush_manager.globals import GLOBALS, CM_UIContext
from ..utils.callback import CallbackSetCollection


callback__AddonDataInit = CallbackSetCollection.init('AddonDataByMode', 'init') # First time (not existing data was found).
callback__AddonDataLoad = CallbackSetCollection.init('AddonDataByMode', 'load') # If data exists, will load it.
callback__AddonDataSave = CallbackSetCollection.init('AddonDataByMode', 'save')


DataPath = Paths.DATA


class ContextModes(Enum):
    SCULPT = auto()
    IMAGE_PAINT = auto()
    PAINT_GPENCIL = auto()


VALID_CONTEXT_MODES = {mode.name for mode in ContextModes}


_addon_data_cache: dict[str, 'AddonDataByMode'] = {}


def init_load_defaults(addon_data: 'AddonDataByMode'):
    print(f"[brush_manager] Initializing defaults for BM_DATA.{addon_data.mode}@[{id(addon_data)}]")

    from ..api import BM_OPS
    from ..paths import Paths
    BM_OPS.import_library_default(libpath=Paths.Lib.DEFAULT_BLEND(), ui_context_mode=addon_data.mode)

    callback__AddonDataInit(addon_data)



class AddonDataByMode(object):
    # ----------------------------------------------------------------
    # Cache and database.

    @classmethod
    def get_data(cls, mode: ContextModes | str) -> 'AddonDataByMode':
        mode_name: str = mode if isinstance(mode, str) else mode.name
        if data := _addon_data_cache.get(mode_name, None):
            #### print(f"[brush_manager] Loaded BM_DATA.{data.mode}@[{id(data)}] from cache")
            return data

        # Try to load data from file.
        data_filepath: Path = DataPath / mode_name

        if not data_filepath.exists() or data_filepath.stat().st_size == 0:
            print(f"[brush_manager] BM_DATA.{mode_name} not found in path: '{str(data_filepath)}'")
            _addon_data_cache[mode_name] = data = cls(mode_name)
        else:
            with data_filepath.open('rb') as data_file:
                data: AddonDataByMode = pickle.load(data_file)
                data.ensure_owners()
                _addon_data_cache[mode_name] = data
            print(f"[brush_manager] Loaded BM_DATA.{mode_name}@[{id(data)}] from file: '{str(data_filepath)}'")
            callback__AddonDataLoad(data)
        return data


    def save(self, save_items_id_data: bool = True) -> None:
        data_filepath: Path = DataPath / self.mode

        print(f"[brush_manager] Saving BM_DATA.{self.mode}@[{id(self)}] to file: '{data_filepath}'")

        if save_items_id_data:
            for cat in self.brush_cats:
                for item in cat.items:
                    item.save()

            for cat in self.texture_cats:
                for item in cat.items:
                    item.save()

        # Avoid multiple references to objects since pickle doesn't work really well with that.
        self.clear_owners()

        with data_filepath.open('wb') as data_file:
            pickle.dump(self, data_file)

        # Restore references...
        self.ensure_owners()

        callback__AddonDataSave(self)


    def clear_owners(self) -> None:
        self.brush_cats.clear_owners()
        self.texture_cats.clear_owners()

    def ensure_owners(self) -> None:
        self.brush_cats.ensure_owners(self)
        self.texture_cats.ensure_owners(self)


    # ----------------------------------------------------------------
    # Initializing data and properties.

    mode: ContextModes

    brush_cats:     BrushCat_Collection     # OrderedDict[BrushCat]
    texture_cats:   TextureCat_Collection   # OrderedDict[TextureCat]

    ## brushes: BrushItem_Collection
    ## textures: TextureItem_Collection

    active_brush: BrushItem
    active_texture: TextureItem


    @property
    def active_brush(self) -> BrushItem | None:
        if self._active_brush is None:
            return None
        cat_id, brush_id = self._active_brush
        if cat := self.brush_cats.get(cat_id):
            return cat.items.get(brush_id)

    @property
    def active_texture(self) -> TextureItem | None:
        if self._active_texture is None:
            return None
        cat_id, texture_id = self._active_texture
        if cat := self.texture_cats.get(cat_id):
            return cat.items.get(texture_id)


    @active_brush.setter
    def active_brush(self, brush_item: BrushItem) -> None:
        self._active_brush = brush_item.uuid, brush_item.cat_id
        brush_item.set_active(bpy.context)

    @active_texture.setter
    def active_texture(self, texture_item: TextureItem) -> None:
        self._active_texture = texture_item.uuid, texture_item.cat_id
        texture_item.set_active(bpy.context)


    @property
    def active_item(self) -> BrushItem | TextureItem | None:
        return self.active_brush if GLOBALS.ui_context_item == 'BRUSH' else self.active_texture

    @active_item.setter
    def active_item(self, item: BrushItem | TextureItem) -> None:
        if isinstance(item, BrushItem):
            self.active_brush = item
        elif isinstance(item, TextureItem):
            self.active_texture = item

    @property
    def active_category(self) -> BrushCat | TextureCat | None:
        return self.brush_cats.active if GLOBALS.ui_context_item == 'BRUSH' else self.texture_cats.active

    @active_category.setter
    def active_category(self, cat: BrushCat | TextureCat) -> None:
        cat_coll = self.brush_cats if isinstance(cat, BrushCat) else self.texture_cats
        cat_coll.select(cat)


    def __init__(self, mode: str) -> None:
        print(f"[brush_manager] New BM_DATA.{mode}@[{id(self)}]")

        self.mode = mode

        self.brush_cats     = BrushCat_Collection(self)   # OrderedDict()
        self.texture_cats   = TextureCat_Collection(self) # OrderedDict()

        self._active_brush = None
        self._active_texture = None

        ## self.brushes = BrushItem_Collection(self) # OrderedDict
        ## self.textures = TextureItem_Collection(self)

        timer_register(partial(init_load_defaults, self))


    def add_bl_texture(self, context, bl_texture: BlTexture, set_active: bool = False) -> TextureItem:
        ''' Create a new texture item from a texture datablock.
            Asign it to a 'unasigned' or specified category and mark as active if wanted. '''

        cat = self.get_texture_cat('UNASIGNED')
        if cat is None:
            cat = self.new_texture_cat('Unasigned', custom_uuid='UNASIGNED')

        tex_item: TextureItem = cat.items.add_from_id_data(bl_texture)
        if set_active:
            tex_item.set_active(context)
        return tex_item


    # ----------------------------------------------------------------
    # Local Methods (per context mode).

    def get_cats(self, skip_active: bool = False) -> list[Category]:
        cat_coll = self.brush_cats if GLOBALS.ui_context_item == 'BRUSH' else self.texture_cats
        if skip_active:
            act_cat = cat_coll.active
            return [cat for cat in cat_coll if cat != act_cat]
        else:
            return cat_coll

    def _get_cat(self, cat_uuid: str) -> Category | None:
        cats = self.brush_cats if GLOBALS.ui_context_item == 'BRUSH' else self.texture_cats
        return cats.get(cat_uuid)

    def get_brush_cat(self, cat_uuid: str) -> BrushCat:
        with CM_UIContext(mode=self.mode, item_type='BRUSH'):
            return self._get_cat(cat_uuid)

    def get_texture_cat(self, cat_uuid: str) -> TextureCat:
        with CM_UIContext(mode=self.mode, item_type='TEXTURE'):
            return self._get_cat(cat_uuid)

    # ---

    def _new_cat(self, cat_name: str | None = None, custom_uuid: str | None = None) -> Category:
        cat_coll = self.brush_cats if GLOBALS.ui_context_item == 'BRUSH' else self.texture_cats
        cat_name: str = cat_name if cat_name is not None else 'New Category'
        return cat_coll.add(cat_name, custom_uuid=custom_uuid)

    def new_brush_cat(self, cat_name: str | None = None, custom_uuid: str | None = None) -> BrushCat:
        with CM_UIContext(mode=self.mode, item_type='BRUSH'):
            return self._new_cat(cat_name, custom_uuid=custom_uuid)

    def new_texture_cat(self, cat_name: str | None = None, custom_uuid: str | None = None) -> TextureCat:
        with CM_UIContext(mode=self.mode, item_type='TEXTURE'):
            return self._new_cat(cat_name, custom_uuid=custom_uuid)

    # ---



class AddonData:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = AddonData()
        return cls._instance

    @classmethod
    def clear_instances(cls):
        if cls._instance is not None:
            del cls._instance
            cls._instance = None
            for data in _addon_data_cache.values():
                del data
            _addon_data_cache.clear()


    # GOOD for development environments... LOL.
    @property
    def SCULPT(self) -> AddonDataByMode: return AddonDataByMode.get_data(mode=ContextModes.SCULPT)
    @property
    def IMAGE_PAINT(self) -> AddonDataByMode: return AddonDataByMode.get_data(mode=ContextModes.IMAGE_PAINT)
    @property
    def PAINT_GPENCIL(self) -> AddonDataByMode: return AddonDataByMode.get_data(mode=ContextModes.PAINT_GPENCIL)

    # BAD for development environments... :/
    ### SCULPT = AddonDataByMode.get_data(mode=ContextModes.SCULPT)
    ### IMAGE_PAINT = AddonDataByMode.get_data(mode=ContextModes.IMAGE_PAINT)
    ### PAINT_GPENCIL = AddonDataByMode.get_data(mode=ContextModes.PAINT_GPENCIL)

    # ----------------------------------------------------------------
    # global methods.

    @classmethod
    def get_data_by_context(cls, ctx: Context | UIProps | str | None = None) -> AddonDataByMode | None:
        if ctx is None:
            ctx = bpy.context
        if isinstance(ctx, Context):
            return cls.get_data_by_mode(ctx.mode)
        if isinstance(ctx, UIProps):
            return cls.get_data_by_mode(ctx.ui_context_mode)
        if isinstance(ctx, str):
            return cls.get_data_by_mode(ctx)
        raise TypeError(f"Invalid context type {ctx}. Expected bpy.types.Context or brush_manager's UIProps type")

    @classmethod
    def get_data_by_mode(cls, mode: str) -> AddonDataByMode | None:
        if mode not in VALID_CONTEXT_MODES:
            raise ValueError(f"Invalid mode! Expected: {VALID_CONTEXT_MODES}; But got: {mode}")
        return AddonDataByMode.get_data(mode=mode)

    @staticmethod
    def save_all(save_items_id_data: bool = True) -> None:
        for data in _addon_data_cache.values():
            data.save(save_items_id_data=save_items_id_data)


# ----------------------------------------------------------------


get_brush_names_by_ctx_mode = {
    'SCULPT': ('Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb'),
    'IMAGE_PAINT': (
        'TexDraw',

        'Soften',
        'Smear',

        'Clone',

        'Fill',

        'Mask'),
    'PAINT_GPENCIL': (
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
