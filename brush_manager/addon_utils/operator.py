from typing import Any
import bpy
from bpy.types import Context, Event, OperatorProperties
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from ..types import AddonData, AddonDataByMode, UIProps


class OpsAction:
    ui_context_mode : StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})
    ui_context_item : StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})

    def _get_data(self, ui_props: UIProps, bm_data: AddonDataByMode, uuid: str | None) -> object:
        pass

    def action(self, context: Context, ui_props: UIProps, bm_data: AddonDataByMode):
        pass

    def execute(self, context: Context) -> set[str]:
        ui_props = UIProps.get_data(context)

        if context.area is not None:
            self.tag_redraw = context.area.tag_redraw
        else:
            self.tag_redraw = lambda: None

        # Custom context?
        if self.ui_context_mode != '':
            ui_props.ui_context_mode = self.ui_context_mode.upper()
        if self.ui_context_item != '':
            ui_props.ui_context_item = self.ui_context_item.upper()

        # Context-sesitive data source.
        addon_data = AddonData.get_data_by_context(ui_props)

        # Call our operator action.
        res = None
        if hasattr(self, 'get_data'):
            element_data = self.get_data(ui_props, addon_data)
            if element_data is None:
                return {'CANCELLED'}
            if not isinstance(element_data, tuple):
                res = self.action(element_data)
            else:
                res = self.action(*element_data)
        else:
            res = self.action(context, ui_props, addon_data)

        self.tag_redraw()

        if res is not None:
            if isinstance(res, set):
                return res
            if isinstance(res, str):
                return {res}
        return {'FINISHED'}

    @classmethod
    def draw_in_layout(cls, layout, **draw_props) -> OperatorProperties:
        return layout.operator(cls.bl_idname, **draw_props)

    @classmethod
    def run(cls, *args, **kwargs) -> None:
        module, name = cls.bl_idname.split('.')
        getattr(getattr(bpy.ops, module), name)(*args, **kwargs)
    
    @classmethod
    def __call__(cls, *args, **kwds):
        cls.run(args, **kwds)


class OpsInvokePropsPopup(OpsAction):
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self, width=360)


class OpsImport(ImportHelper, OpsAction):
    pass

class OpsImportBlend(OpsImport):
    filename_ext = '.blend'

    filter_glob: StringProperty(
        default='*.blend',
        options={'HIDDEN'}
    )

class OpsImportPNG(OpsImport):
    filename_ext = '.png'

    filter_glob: StringProperty(
        default='*.png',
        options={'HIDDEN'}
    )
