from bpy.types import Context

from pathlib import Path
from enum import Enum, auto
import pickle
from collections import OrderedDict

from brush_manager.pg.pg_ui import UIProps
from brush_manager.paths import Paths
from .cats import Category, BrushCat, TextureCat, BrushCat_Collection, TextureCat_Collection


DataPath = Paths.DATA


class ContextModes(Enum):
    SCULPT = auto()
    IMAGE_PAINT = auto()
    PAINT_GPENCIL = auto()


VALID_CONTEXT_MODES = {mode.name for mode in ContextModes}



class AddonDataByMode(object):
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

    brush_cats:     BrushCat_Collection     # OrderedDict[BrushCat]
    texture_cats:   TextureCat_Collection   # OrderedDict[TextureCat]


    def __init__(self, mode: ContextModes) -> None:
        self.mode = mode

        self.brush_cats     = BrushCat_Collection()   # OrderedDict()
        self.texture_cats   = TextureCat_Collection() # OrderedDict()


    # ----------------------------------------------------------------
    # Local Methods (per context mode).

    def _get_cat(self, cat_type: str, cat_uuid: str) -> Category | None:
        cats = self.brush_cats if cat_type == 'BRUSH' else self.texture_cats
        return cats.get(cat_uuid, None)

    def get_brush_cat(self, cat_uuid: str) -> BrushCat: return self._get_cat('BRUSH', cat_uuid)
    def get_texture_cat(self, cat_uuid: str) -> TextureCat: return self._get_cat('TEXTURE', cat_uuid)

    # ---

    def _new_cat(self, cat_type: str, cat_name: str | None = None) -> Category:
        cats = self.brush_cats if cat_type == 'BRUSH' else self.texture_cats
        cat_name: str = cat_name if cat_name is None else 'New Category'
        cat = cats.add(cat_name)
        cat.owner = self
        return cat

    def new_brush_cat(self, cat_name: str | None = None) -> BrushCat: return self._new_cat('BRUSH', cat_name)
    def new_texture_cat(self, cat_name: str | None = None) -> TextureCat: return self._new_cat('TEXTURE', cat_name)

    # ---



class AddonData:
    SCULPT = AddonDataByMode.get_data(mode=ContextModes.SCULPT)
    IMAGE_PAINT = AddonDataByMode.get_data(mode=ContextModes.IMAGE_PAINT)
    PAINT_GPENCIL = AddonDataByMode.get_data(mode=ContextModes.PAINT_GPENCIL)

    # ----------------------------------------------------------------
    # global methods.

    @classmethod
    def get_data_by_context(cls, ctx: Context | UIProps) -> AddonDataByMode | None:
        if isinstance(ctx, Context):
            return cls.get_data_by_mode(ctx.mode)
        if isinstance(ctx, UIProps):
            return cls.get_data_by_mode(ctx.ui_context_mode)
        raise TypeError(f"Invalid context type {ctx}. Expected bpy.types.Context or brush_manager's UIProps type")

    @classmethod
    def get_data_by_mode(cls, mode: str) -> AddonDataByMode | None:
        if mode not in VALID_CONTEXT_MODES:
            raise ValueError(f"Invalid mode! Expected: {VALID_CONTEXT_MODES}; But got: {mode}")
        return AddonDataByMode.get_data(mode=mode)

    @staticmethod
    def save_all() -> None:
        for ctx_mode in ContextModes:
            AddonDataByMode.get_data(mode=ctx_mode).save()
