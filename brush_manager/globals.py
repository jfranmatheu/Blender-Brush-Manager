from bpy.types import Context

from .paths import Paths


ui_context_mode: str = 'SCULPT'
ui_context_item: str = 'BRUSH'

_is_importing_a_library: bool = False


class _GLOBALS:
    @property
    def BM_DATA(self):
        from .data.addon_data import AddonData
        return AddonData.get()

    @property
    def is_importing_a_library(self) -> bool:
        global _is_importing_a_library
        return _is_importing_a_library or Paths.Scripts.CHECK__WRITE_LIBS(as_path=True).exists()

    @is_importing_a_library.setter
    def is_importing_a_library(self, value: bool) -> None:
        global _is_importing_a_library
        _is_importing_a_library = value

    @property
    def ui_context_mode(self) -> str:
        global ui_context_mode
        return ui_context_mode

    @ui_context_mode.setter
    def ui_context_mode(self, ctx_mode: str) -> None:
        global ui_context_mode
        ui_context_mode = ctx_mode

    @property
    def ui_context_item(self) -> str:
        global ui_context_item
        return ui_context_item

    @ui_context_item.setter
    def ui_context_item(self, item_type: str) -> None:
        global ui_context_item
        ui_context_item = item_type

    @property
    def is_context_brush_item(self) -> bool:
        global ui_context_item
        return ui_context_item == 'BRUSH'

    @property
    def is_context_texture_item(self) -> bool:
        global ui_context_item
        return ui_context_item == 'TEXTURE'


GLOBALS = _GLOBALS()



class CM_UIContext:
    def __init__(self, context: Context | None = None, mode: str = 'SCULPT', item_type: str = 'BRUSH') -> None:
        if context:
            from .types import UIProps
            self.ui_props = UIProps.get_data(context)
            self.prev_mode = self.ui_props.ui_context_mode
            self.prev_item_type = self.ui_props.ui_context_item
        else:
            self.ui_props = None
            self.prev_mode = GLOBALS.ui_context_mode
            self.prev_item_type = GLOBALS.ui_context_item

        self.mode = mode
        self.item_type = item_type


    def __enter__(self):
        if self.ui_props:
            self.ui_props.ui_context_mode = self.mode
            self.ui_props.ui_context_item = self.item_type

        else:
            GLOBALS.ui_context_mode = self.mode
            GLOBALS.ui_context_item = self.item_type


    def __exit__(self, *args):
        if self.ui_props:
            self.ui_props.ui_context_mode = self.prev_mode
            self.ui_props.ui_context_item = self.prev_item_type

        else:
            GLOBALS.ui_context_mode = self.prev_mode
            GLOBALS.ui_context_item = self.prev_item_type
