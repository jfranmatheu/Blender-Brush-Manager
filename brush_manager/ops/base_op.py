from ..types import AddonData, AddonDataByMode

import bpy
from bpy.types import Context, OperatorProperties


class BaseOp:
    def action(self, context: Context, addon_data_ctx: AddonDataByMode):
        pass

    def execute(self, context) -> set[str]:
        data = AddonData.get_data_by_ui_mode(context)
        res = self.action(context, data)
        if isinstance(res, set):
            return res
        return {'FINISHED'}

    @classmethod
    def draw_in_layout(cls, layout, **draw_props) -> OperatorProperties:
        return layout.operator(cls.bl_idname, **draw_props)
    
    @classmethod
    def run(cls, *args, **kwargs) -> None:
        module, name = cls.bl_idname.split('.')
        getattr(getattr(bpy.ops, module), name)(*args, **kwargs)
