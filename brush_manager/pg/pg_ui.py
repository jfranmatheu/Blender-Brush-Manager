import bpy
from bpy.types import PropertyGroup, Context, WindowManager as WM, Brush as BlBrush, Texture as BlTexture, ToolSettings
from bpy.props import StringProperty, PointerProperty, EnumProperty, IntProperty, CollectionProperty, BoolProperty, FloatVectorProperty



class UIProps(PropertyGroup):
    ui_active_item_color: FloatVectorProperty(size=4, default=(0.15, 0.6, 1.0, 1.0), subtype='COLOR')
    ui_active_section: EnumProperty(
        name="Active Section",
        items=(
            ('LIBS', 'Libraries', "", 'FILE_BLEND', 0),
            ('CATS', 'Categories', "", 'ASSET_MANAGER', 1)
        )
    )

    @property
    def ui_in_libs_section(self) -> bool: return self.ui_active_section == 'LIBS'

    @property
    def ui_in_cats_section(self) -> bool: return self.ui_active_section == 'CATS'

    # ----------------------------

    ui_context_mode: EnumProperty(
        items=(
            ('sculpt', 'Sculpt', '', 'SCULPTMODE_HLT', 0),
            ('texture_paint', 'Texture Paint', '', 'TEXTURE_DATA', 1),
            ('gpencil_paint', 'Grease Pencil', '', 'OUTLINER_DATA_GP_LAYER', 2),
        )
    )

    ui_context_item: EnumProperty(
        name="Item-Type Context",
        items=(
            ('BRUSH', 'Brushes', ""),
            ('TEXTURE', 'Textures', "")
        ),
        default='BRUSH'
    )

    @property
    def is_ctx_brush(self) -> bool: return self.ui_context_item == 'BRUSH'

    @property
    def is_ctx_texture(self) -> bool: return self.ui_context_item == 'TEXTURE'



def register():
    WM.brush_manager_ui = PointerProperty(type=UIProps)

def unregister():
    del WM.brush_manager_ui
