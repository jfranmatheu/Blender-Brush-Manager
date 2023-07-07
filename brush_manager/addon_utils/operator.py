import bpy
from bpy.types import Context, Event, OperatorProperties

from ..types import AddonData, AddonDataByMode


class OpsAction:
    def action(self, context: Context, addon_data: AddonDataByMode):
        pass

    def execute(self, context) -> set[str]:
        data = AddonData.get_data_by_ui_mode(context)
        self.action(context, data)
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


# def register_classes_factory():
#     return [op.create_b3d_class() for op in OpsAction.__subclasses__() + OpsInvokePropsPopup.__subclasses__()]
