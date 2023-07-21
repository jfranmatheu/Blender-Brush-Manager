import bpy
from bpy.types import Context, Event, OperatorProperties
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from ..types import AddonData, AddonDataByMode, UIProps


class OpsAction:
    uuid: StringProperty(default='')

    ui_context_mode : StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})
    ui_context_item : StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})

    def _get_data(self, ui_props: UIProps, addon_data: AddonDataByMode, uuid: str | None) -> object:
        pass

    def action(self, context: Context, addon_data: AddonDataByMode):
        pass

    def invoke(self, context: Context, event: Event) -> set[str]:
        return self.execute(context)

    def execute(self, context: Context) -> set[str]:
        ui_props = UIProps.get_data(context)

        if context.area is not None:
            self.tag_redraw = context.area.tag_redraw
        else:
            self.tag_redraw = lambda: None

        # Custom context?
        if self.ui_context_mode != '':
            ui_props.ui_context_mode = self.ui_context_mode
        if self.ui_context_item != '':
            ui_props.ui_context_item = self.ui_context_item

        # Context-sesitive data source.
        addon_data = AddonData.get_data_by_ui_mode(context)

        # Call our operator action.
        if hasattr(self, 'get_data'):
            element_data = self.get_data(ui_props, addon_data, self.uuid if self.uuid != '' else None)
            if element_data is None:
                return {'CANCELLED'}
            if not isinstance(element_data, tuple):
                self.action(element_data)
            else:
                self.action(*element_data)
        else:
            self.action(addon_data)
        self.tag_redraw()
        return {'FINISHED'}

    @classmethod
    def draw_in_layout(cls, layout, **draw_props) -> OperatorProperties:
        return layout.operator(cls.bl_idname, **draw_props)

    @classmethod
    def run(cls, *args, **kwargs) -> None:
        module, name = cls.bl_idname.split('.')
        getattr(getattr(bpy.ops, module), name)(*args, **kwargs)


class OpsInvokePropsPopup(OpsAction):
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_popup(self, event)


class OpsImport(OpsAction, ImportHelper):
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



# def register_classes_factory():
#     return [op.create_b3d_class() for op in OpsAction.__subclasses__() + OpsInvokePropsPopup.__subclasses__()]
