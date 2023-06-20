from ..types import AddonData

from bpy.types import Context, OperatorProperties


class BaseOp:
    def action(self, context: Context, data: AddonData):
        pass

    def execute(self, context) -> set[str]:
        data = AddonData.get_data(context)
        self.action(context, data)
        return {'FINISHED'}

    @classmethod
    def draw_in_layout(cls, layout, **draw_props) -> OperatorProperties:
        return layout.operator(cls.bl_idname, **draw_props)
