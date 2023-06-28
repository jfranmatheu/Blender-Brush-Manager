import bpy
import sys
import json
from uuid import uuid4
from pathlib import Path
import numpy as np
from os.path import isfile, exists, splitext
# import socket

from bpy.path import abspath as bpy_abspath
from bpy.types import Image, Brush, Texture, ImageTexture, ImageSequence, Context, SpaceImageEditor

from brush_manager.paths import Paths

import bpy.utils.previews
from bpy.utils import previews


CONTEXT_MODE = sys.argv[-1]

image_previews = previews.new()

try:
    import PIL
    from PIL import Image as PILImage

    from PIL import __version__
    PIL_VERSION = float(''.join(__version__.split('.')[:-1]))
    if PIL_VERSION >= 9.0 and hasattr(PILImage, 'Resampling'):
        PIL_RESAMPLING_NEAREST = PILImage.Resampling.NEAREST
    else:
        PIL_RESAMPLING_NEAREST = PILImage.NEAREST

    if hasattr(PILImage, 'Transpose'):
        PIL_FLIP_TOP_BOTTOM = PILImage.Transpose.FLIP_TOP_BOTTOM
    else:
        PIL_FLIP_TOP_BOTTOM = PILImage.FLIP_TOP_BOTTOM
    
    HAS_PIL = True

except ImportError as e:
    PILImage = None
    PIL_RESAMPLING_NEAREST = None
    PIL_FLIP_TOP_BOTTOM = None

    HAS_PIL = False

HAS_PIL = False

ICON_SIZE = 92, 92

import string
valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)


data_brushes: list[Brush] = bpy.data.brushes

if CONTEXT_MODE == 'sculpt':
    builtin_brush_names = ('Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb')
elif CONTEXT_MODE == 'texture_paint':
    builtin_brush_names = ()
elif CONTEXT_MODE == 'gp_draw':
    builtin_brush_names = ()

builtin_brushes = {data_brushes.get(brush_name, None) for brush_name in builtin_brush_names}


get_use_paint_attr = {
    'sculpt': 'use_paint_sculpt',
    'texture_paint': 'use_paint_image',
    'gp_draw': 'use_paint_grease_pencil',
}
get_tool_attr = {
    'sculpt': 'sculpt_tool',
    'texture_paint': 'image_tool',
    'gp_draw': 'gpencil_tool',
}


use_paint_attr = get_use_paint_attr[CONTEXT_MODE]
tool_attr = get_tool_attr[CONTEXT_MODE]

brushes: list[Brush] = [brush for brush in data_brushes if getattr(brush, use_paint_attr) and brush not in builtin_brushes]
textures: list[Texture] = [brush.texture for brush in brushes if brush.texture is not None]


textures_data = {}
for texture in textures:
    if texture.type != 'IMAGE':
        continue
    if not isinstance(texture, ImageTexture):
        continue
    if not texture.image:
        continue

    uuid = uuid4().hex
    texture['uuid'] = uuid
    texture.image['uuid'] = uuid
    textures_data[uuid] = {
        'name': texture.name,
        'type': texture.type
    }


brushes_data = {}
for brush in brushes:
    uuid = uuid4().hex
    brush['uuid'] = uuid
    brushes_data[uuid] = {
        'name': brush.name,
        'type': getattr(brush, tool_attr),
        'use_custom_icon': brush.use_custom_icon and exists(brush.icon_filepath) and isfile(brush.icon_filepath),
        'texture_uuid': brush.texture['uuid'] if brush.texture is not None else ''
    }


output_data = {
    'brushes': brushes_data,
    'textures': textures_data
}


with open(Paths.Scripts.EXPORT_JSON(), 'w') as file:
    file.write(json.dumps(output_data))


bpy.ops.wm.save_mainfile()


# -----------------------------------------------------------------------------------

bpy.ops.scene.new()
scene = bpy.data.scenes[-1]
scene.name = 'TEMP'
# use docs.blender.org/api/current/bpy.types.ImageFormatSettings.html for more properties
settings = scene.render.image_settings
settings.file_format = 'PNG'  # Options: 'BMP', 'IRIS', 'PNG', 'JPEG', 'JPEG2000', 'TARGA', 'TARGA_RAW', 'CINEON', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EXR', 'HDR', 'TIFF', 'WEBP'
settings.color_mode = 'RGBA'  # Options: 'BW', 'RGB', 'RGBA' (depends on file_format)
settings.color_depth = '8'  # Options: '8', '10', '12', '16', '32' (depends on file_format)
settings.compression = 75  # Range: 0 - 100

# SETUP IMAGE EDITOR.
context: Context = bpy.context
area = context.screen.areas[0]
area.type = 'IMAGE_EDITOR'
space: SpaceImageEditor = area.spaces[0]
space.ui_mode = 'VIEW'
space.image_user.use_auto_refresh = True
context_override = {
    'window': bpy.context.window,
    'area': area,
    'space_data': space,
    # 'scene': scene,
    # 'image_settings': settings
}


# -----------------------------------------------------------------------------------

BrushIcon = Paths.Data.Icons.BRUSH
TextureIcon = Paths.Data.Icons.TEXTURE

data_images = bpy.data.images

tagged_images_to_generate_with_pil = []
tagged_images_to_generate_with_bpy = []


def generate_thumbnail__pil(in_image_path: str, out_image_path: str) -> str:
    # filename = ''.join(c for c in filename if c in valid_filename_chars)
    with PILImage.open(in_image_path) as image:
        image.thumbnail(ICON_SIZE, PIL_RESAMPLING_NEAREST) # image.resize(ICON_SIZE, PIL_RESAMPLING_NEAREST)
        image.save(out_image_path, 'PNG')
    return out_image_path


def generate_thumbnail__bpy(in_image_path: str | ImageTexture, out_image_path: str):
    print(in_image_path, out_image_path)
    if isinstance(in_image_path, ImageTexture):
        image: Image = in_image_path.image
        image_user = in_image_path.image_user

        # print("\t>>> ImageTexture", image.file_format)

        # WORKS FAST BUT NOT WITH LAYERS (FUCK PSD ADOBE)
        if image.source == 'FILE':
            print("\t>>> FILE")
            temp_name = uuid4().hex
            preview = image_previews.load(temp_name, image.filepath_from_user(image_user=image_user), 'IMAGE')
            icon_image = data_images.new(image['uuid'], *preview.image_size, alpha=True)
            icon_image.pixels.foreach_get(preview.image_pixels_float)
            # icon_image.filepath_raw = out_image_path
            # icon_image.save()
            icon_image.save_render(out_image_path, scene=scene)
            data_images.remove(icon_image)
            del icon_image
            del image_previews[temp_name]

        elif image.source == 'SEQUENCE':
            # image.scale(*ICON_SIZE)
            print("\t>>> SEQUENCE")
            with context.temp_override(**context_override):
                # print("\t>>> temp_override")
                space.image = image
                # print("\t>>> space.image = image")
                space.image_user.frame_duration = image_user.frame_duration
                space.image_user.frame_start = image_user.frame_start
                space.image_user.frame_offset = image_user.frame_offset
                space.image_user.frame_current = image_user.frame_current
                # print("\t>>> setup frame attr: space.image_user")
                # bpy.ops.image.resize(size=ICON_SIZE)
                # print("\t>>> bpy.ops.image.resize")
                bpy.ops.image.save_as(filepath=out_image_path, save_as_render=True)
                # print("\t>>> bpy.ops.image.save_as")
                # data_images.remove(image)
                del image

                generate_thumbnail__bpy(out_image_path, out_image_path)

    elif isinstance(in_image_path, str):
        print("\t>>> str | Path")
        icon_image = data_images.load(in_image_path, check_existing=False)
        icon_image.scale(*ICON_SIZE)
        # icon_image.filepath_raw = out_image_path # BrushIcon(brush['uuid'] + '.png')
        # icon_image.file_format = 'PNG'
        # icon_image.save()
        icon_image.save_render(out_image_path, scene=scene)
        data_images.remove(icon_image)
        del icon_image


def tag_generate_thumbnail(in_image_path: str | ImageTexture, out_image_path: str):
    if isinstance(in_image_path, ImageTexture):
        image: Image = in_image_path.image
        image_user = in_image_path.image_user
        if HAS_PIL and image.file_format in {'PNG', 'JPEG'}:
            tagged_images_to_generate_with_pil.append((image.filepath_from_user(image_user=image_user), out_image_path))
        else:
            if image.file_format not in {'PNG', 'JPEG'}:
                image.file_format = 'PNG'
            tagged_images_to_generate_with_bpy.append((in_image_path, out_image_path))
    elif isinstance(in_image_path, str):
        root, ext = splitext(in_image_path)
        if HAS_PIL and ext in {'.png', '.jpg', 'jpeg'}:
            tagged_images_to_generate_with_pil.append((in_image_path, out_image_path))
        else:
            tagged_images_to_generate_with_bpy.append((in_image_path, out_image_path))


for _brush in brushes:
    if not _brush.use_custom_icon:
        continue
    icon_path = bpy_abspath(_brush.icon_filepath)
    if not exists(icon_path) or not isfile(icon_path):
        continue

    print(_brush.name, icon_path)
    tag_generate_thumbnail(icon_path, BrushIcon(_brush['uuid'] + '.png'))


for texture in textures:
    if texture.type != 'IMAGE':
        continue
    if not isinstance(texture, ImageTexture):
        continue
    if texture.image is None:
        continue
    tag_generate_thumbnail(texture, TextureIcon(texture['uuid'] + '.png'))


# GENERATE IMAGE THUMBNAILS WITH PIL.
if HAS_PIL:
    from concurrent.futures import ProcessPoolExecutor
    from concurrent.futures import as_completed, wait

    # create the process pool.
    with ProcessPoolExecutor() as exe:
        # submit tasks.
        futures = [exe.submit(generate_thumbnail__pil, in_image_path, out_image_path)
                   for (in_image_path, out_image_path) in tagged_images_to_generate_with_pil]

        # report progress.
        for future in as_completed(futures):
            # get the output path that was saved.
            outpath = future.result()
            # report progress.
            print(f'.saved {outpath}')

        # wait(futures)


# FINALLY, GENERATE IMAGE THUMBNAILS WITH BPY.
for (in_image, out_image) in tagged_images_to_generate_with_bpy:
    generate_thumbnail__bpy(in_image, out_image)
