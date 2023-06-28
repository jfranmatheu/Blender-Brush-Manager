import bpy.utils.previews
from gpu.types import GPUTexture
from bpy.types import Image, ImagePreview
from bpy.utils import previews
from gpu import texture

from enum import Enum, auto
import numpy as np
from os.path import splitext, exists, isfile
import glob
from os.path import basename

from .paths import Paths

preview_collections: dict[str, previews.ImagePreviewCollection] = {}

# icon_previews: previews.ImagePreviewCollection = None
icon_gputex: dict[str, GPUTexture] = {}

GPUTEX_ICON_SIZE = 128, 128


class Icons(Enum):
    BRUSH_PLACEHOLDER = auto()
    TEXTURE_PLACEHOLDER = auto()

    @property
    def icon_path(self) -> str:
        return Paths.Lib.ICONS(self.name.lower() + '.png')

    @property
    def icon_id(self) -> int:
        return get_preview(self.name, self.icon_path, collection='builtin')

    def __call__(self) -> int:
        return self.icon_id

    def draw(self, layout, text: str = ''):
        layout.label(text=text, icon_value=self.icon_id)


def new_preview(uuid: str, filepath: str, collection: str = 'runtime', force_reload: bool = True) -> None:
    print("New preview ->", uuid, filepath)
    if preview := preview_collections[collection].get(uuid, None):
        del preview
        del preview_collections[collection][uuid]
    return preview_collections[collection].load(
        uuid, # basename(filepath)[:-4],
        filepath,
        'IMAGE',
        force_reload=force_reload
    )

def get_preview(uuid: str, filepath: str, collection: str = 'runtime') -> int:
    if not uuid or not exists(filepath) or not isfile(filepath):
        print("\t>", uuid, " DOES NOT EXIST > ", filepath)
        return 0
    # bpy.utils.user_resource('SCRIPTS', path='Brush Manager\icons', create=False)
    pcoll = preview_collections[collection]
    if uuid not in pcoll:
        # if filepath in pcoll:
        #     return pcoll[filepath].icon_id
        new_preview(uuid, filepath, collection)
    p: ImagePreview = pcoll[uuid]
    return p.icon_id


    # print("> get_preview", uuid, filepath)
    if preview := preview_collections['runtime'].get(uuid, None):
        preview: ImagePreview
        if preview.icon_size[0] == 0 or preview.icon_size[1] == 0:
            # print("\t> something went wrong!")
            # print("\t\t>", preview.icon_id, list(preview.icon_size), preview.is_icon_custom, list(preview.image_size), preview.is_image_custom)
            # preview.reload()
            # if preview.image_size[0] == 0 or preview.image_size[1] == 0:
            return 0
            # preview.is_icon_custom = True
            # preview.icon_size = 128, 128
            # preview.icon_pixels_float = preview.image_pixels_float
        # print("\t> exists!", preview.icon_id, list(preview.icon_size))
        return preview.icon_id
    if filepath is not None:
        # print("\t> needs to create it!")
        return new_preview(uuid, filepath).icon_id
    # print("\t> something went wrong!")
    return 0


def new_gputex(uuid: str, filepath: str) -> GPUTexture:
    image: Image = bpy.data.images.load(filepath)
    gputex = texture.from_image(image)
    bpy.data.images.remove(image)
    del image
    icon_gputex[uuid] = gputex
    return gputex


def get_gputex(uuid: str, filepath: str) -> GPUTexture:
    if gputex := icon_gputex.get(uuid, None):
        return gputex
    if filepath is not None:
        return new_gputex(uuid, filepath)
    return None


def register_icons():
    if preview_collections:
        bpy.utils.previews.remove(preview_collections['builtin'])
        bpy.utils.previews.remove(preview_collections['runtime'])
        preview_collections.clear()
    preview_collections['builtin'] = previews.new()
    preview_collections['runtime'] = previews.new()
    from .paths import Paths

    for filepath in glob.glob(Paths.Data.Icons._ICONS('**', '*.png')):
        uuid, ext = splitext(basename(filepath))
        new_preview(uuid, filepath, collection='runtime')
        # new_gputex(uuid, filepath)

    for filepath in glob.glob(Paths.Lib.ICONS('**', '*.png')):
        uuid, ext = splitext(basename(filepath))
        new_preview(uuid.upper(), filepath, collection='builtin')


def register():
    register_icons()


def unregister():
    # icon_previews.close()
    bpy.utils.previews.remove(preview_collections['builtin'])
    bpy.utils.previews.remove(preview_collections['runtime'])
    preview_collections.clear()
