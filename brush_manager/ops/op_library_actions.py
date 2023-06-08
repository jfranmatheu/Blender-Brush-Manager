from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

from os.path import basename

from .base_op import BaseOp
from ..types import AddonData


class BRUSHMANAGER_OT_add_library(BaseOp, Operator, ImportHelper):
    bl_idname = 'brushmanager.add_library'
    bl_label = "Import a .blend Library"

    filename_ext = '.blend'

    filter_glob: StringProperty(
        default='*.blend',
        options={'HIDDEN'}
    )

    def execute(self, context: Context) -> set[str]:
        data = AddonData.get_data(context)

        lib = data.libraries.add()
        lib.filepath = self.filepath
        lib.name = basename(self.filepath)[:-6]
        

        return {'FINISHED'}


class BRUSHMANAGER_OT_remove_library(BaseOp, Operator):
    bl_idname = 'brushmanager.remove_library'
    bl_label = "Remove Library"

    def execute(self, context: Context) -> set[str]:
        data = AddonData.get_data(context)

        data.libraries.remove
        return {'FINISHED'}

