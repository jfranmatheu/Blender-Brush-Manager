import bpy
from bpy.types import UILayout, Context, WindowManager as WM
from gpu.types import GPUTexture
from bpy.props import StringProperty

from enum import Enum, auto
from uuid import uuid4

from brush_manager.paths import Paths
from brush_manager.icons import get_preview, get_gputex, create_preview_from_filepath, clear_icon



IconPath = Paths.Icons


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


temp_properties: list[str] = []


def ensure_temp_property(context: Context, item: 'IconHolder', attr: str):
    wm = context.window_manager
    prop_name = item.uuid + attr
    prop_value = getattr(item, attr)
    if not hasattr(wm, prop_name):
        setattr(WM, prop_name, StringProperty(
            name=prop_name.title(),
            default=prop_value,
            update=lambda self, _ctx: setattr(item, attr, getattr(self, prop_name))
        ))
        temp_properties.append(prop_name)
    return prop_name


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class IdHolder:
    # Internal props.
    uuid: str

    # Mutable by user.
    name: str

    def __init__(self, name: str) -> None:
        self.uuid = uuid4().hex
        self.name = name

    def draw_item_in_layout(self, context: Context, layout: UILayout) -> UILayout:
        wm = context.window_manager
        prop_name = ensure_temp_property(context, self.uuid, 'name')
        row = layout.row(align=True)
        row.prop(wm, prop_name, text='Name')
        return row


class IconHolder(IdHolder):
    icon_path: IconPath = None

    @property
    def icon_filepath(self) -> str: return self.icon_path(self.uuid + '.png')
    @property
    def icon_id(self) -> int: return get_preview(self.uuid, self.icon_filepath)
    @property
    def icon_gputex(self) -> GPUTexture: return get_gputex(self.uuid, self.icon_filepath)

    def asign_icon(self, filepath: str) -> None:
        create_preview_from_filepath(self.uuid, filepath, self.icon_filepath)

    def clear_icon(self) -> None:
        clear_icon(self.uuid, self.icon_filepath)

    def draw_item_in_layout(self, context: Context, layout: UILayout, icon_scale: float = 1.0) -> UILayout:
        row = super().draw_item_in_layout(context, layout)
        row.template_icon(self.icon_id, scale=icon_scale)
        return row


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Collection:
    pass


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def unregister():
    for prop_name in temp_properties:
        delattr(WM, prop_name)
