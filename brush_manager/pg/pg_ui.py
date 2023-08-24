import bpy
from bpy.types import PropertyGroup, Context, WindowManager as WM, Brush as BlBrush, Texture as BlTexture, ToolSettings
from bpy.props import StringProperty, PointerProperty, EnumProperty, IntProperty, CollectionProperty, BoolProperty, FloatVectorProperty


from brush_manager.globals import GLOBALS


class UIProps(PropertyGroup):
    ui_active_item_color: FloatVectorProperty(size=4, default=(0.15, 0.6, 1.0, 1.0), subtype='COLOR')

    # ----------------------------

    ui_context_mode: EnumProperty(
        items=(
            ('SCULPT', 'Sculpt', '', 'SCULPTMODE_HLT', 0),
            ('IMAGE_PAINT', 'Texture Paint', '', 'TEXTURE_DATA', 1),
            ('PAINT_GPENCIL', 'Grease Pencil', '', 'OUTLINER_DATA_GP_LAYER', 2),
        ),
        default='SCULPT',
        update=lambda x, ctx: setattr(GLOBALS, 'ui_context_mode', x.ui_context_mode)
    )

    ui_context_item: EnumProperty(
        name="Item-Type Context",
        items=(
            ('BRUSH', 'Brushes', "", 'BRUSH_DATA', 0),
            ('TEXTURE', 'Textures', "", 'TEXTURE_DATA', 1)
        ),
        default='BRUSH',
        update=lambda x, ctx: setattr(GLOBALS, 'ui_context_item', x.ui_context_item)
    )

    @property
    def is_ctx_brush(self) -> bool: return self.ui_context_item == 'BRUSH'

    @property
    def is_ctx_texture(self) -> bool: return self.ui_context_item == 'TEXTURE'



def register():
    #### print("[brush_manager] Registering BrushManager's UIprops PropertyGroup")
    WM.brush_manager_ui = PointerProperty(type=UIProps)

def unregister():
    del WM.brush_manager_ui
