import bpy
from bpy.types import Context

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


callback__AddonDataSave = CallbackSetCollection.init('AddonDataByMode', 'save')


DataPath = Paths.DATA


class ContextModes(Enum):
    SCULPT = auto()
    IMAGE_PAINT = auto()
    PAINT_GPENCIL = auto()


VALID_CONTEXT_MODES = {mode.name for mode in ContextModes}


_addon_data_cache: dict[str, 'AddonDataByMode'] = {}


class AddonDataByMode(object):
    # ----------------------------------------------------------------
    # Cache and database.

    @classmethod
    def get_data(cls, mode: ContextModes | str) -> 'AddonDataByMode':
        mode_name: str = mode if isinstance(mode, str) else mode.name
        if data := _addon_data_cache.get(mode_name, None):
            return data

        # Try to load data from file.
        data_filepath: Path = DataPath / mode_name

        if not data_filepath.exists():
            _addon_data_cache[mode_name] = data = cls(mode_name)
        else:
            with data_filepath.open('rb') as data_file:
                data: AddonDataByMode = pickle.load(data_file)
                _addon_data_cache[mode_name] = data
        return data


    def save(self) -> None:
        data_filepath: Path = DataPath / self.mode.name

        # Avoid multiple references to objects since pickle doesn't work really well with that.
        self.brush_cats.clear_owners()
        self.texture_cats.clear_owners()

        with data_filepath.open('wb') as data_file:
            pickle.dump(self, data_file)

        # Restore references...
        self.brush_cats.ensure_owners(self)
        self.texture_cats.ensure_owners(self)

        callback__AddonDataSave(self)


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


    @property
    def active_category(self) -> BrushCat | TextureCat | None:
        return self.brush_cats.active if GLOBALS.ui_context_item == 'BRUSH' else self.texture_cats.active

    @active_category.setter
    def active_category(self, cat: BrushCat | TextureCat) -> None:
        cat_coll = self.brush_cats if isinstance(cat, BrushCat) else self.texture_cats
        cat_coll.select(cat)


    def __init__(self, mode: str) -> None:
        self.mode = mode

        self.brush_cats     = BrushCat_Collection(self)   # OrderedDict()
        self.texture_cats   = TextureCat_Collection(self) # OrderedDict()

        self._active_brush = None
        self._active_texture = None

        ## self.brushes = BrushItem_Collection(self) # OrderedDict
        ## self.textures = TextureItem_Collection(self)


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

    def _new_cat(self, cat_name: str | None = None) -> Category:
        cat_coll = self.brush_cats if GLOBALS.ui_context_item == 'BRUSH' else self.texture_cats
        cat_name: str = cat_name if cat_name is not None else 'New Category'
        return cat_coll.add(cat_name)

    def new_brush_cat(self, cat_name: str | None = None) -> BrushCat:
        with CM_UIContext(mode=self.mode, item_type='BRUSH'):
            return self._new_cat(cat_name)

    def new_texture_cat(self, cat_name: str | None = None) -> TextureCat:
        with CM_UIContext(mode=self.mode, item_type='TEXTURE'):
            return self._new_cat(cat_name)

    # ---



class AddonData:
    SCULPT = AddonDataByMode.get_data(mode=ContextModes.SCULPT)
    IMAGE_PAINT = AddonDataByMode.get_data(mode=ContextModes.IMAGE_PAINT)
    PAINT_GPENCIL = AddonDataByMode.get_data(mode=ContextModes.PAINT_GPENCIL)

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
    def save_all() -> None:
        for data in _addon_data_cache.values():
            data.save()
            
    @staticmethod
    def initialize() -> None:
        from ..api import BM_OPS
        for data in _addon_data_cache.values():
            BM_OPS.import_library_default(libpath=, ui_context_mode=data.mode)



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
