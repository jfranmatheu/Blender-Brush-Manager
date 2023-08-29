import bpy
import sys
import json
from uuid import uuid4
## from time import time
from os.path import isfile, exists, splitext
# import socket
import subprocess

from bpy.path import abspath as bpy_abspath
from bpy.types import Image, ImageTexture, Context, SpaceImageEditor, Brush, Texture

from brush_manager.paths import Paths

import bpy.utils.previews
from bpy.utils import previews


CONTEXT_MODE = sys.argv[-2].lower()
EXCLUDE_DEFAULTS = bool(int(sys.argv[-1]))

# print(sys.argv, EXCLUDE_DEFAULTS, len(bpy.data.brushes))

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
elif CONTEXT_MODE == 'gpencil_paint':
    builtin_brush_names = ()

if EXCLUDE_DEFAULTS:
    builtin_brushes = {data_brushes.get(brush_name, None) for brush_name in builtin_brush_names}
else:
    builtin_brushes = set()


get_use_paint_attr = {
    'sculpt': 'use_paint_sculpt',
    'image_paint': 'use_paint_image',
    'paint_gpencil': 'use_paint_grease_pencil',
}
get_tool_attr = {
    'sculpt': 'sculpt_tool',
    'image_paint': 'image_tool',
    'paint_gpencil': 'gpencil_tool',
}


use_paint_attr = get_use_paint_attr[CONTEXT_MODE]
tool_attr = get_tool_attr[CONTEXT_MODE]

## start_time = time()

## _start_time = time()
if EXCLUDE_DEFAULTS:
    brushes: list[Brush] = [brush for brush in data_brushes if getattr(brush, use_paint_attr) and brush not in builtin_brushes]
else:
    brushes: list[Brush] = [brush for brush in data_brushes if getattr(brush, use_paint_attr) and brush]
textures: list[Texture] = [brush.texture for brush in brushes if brush.texture is not None]
## print("\t> Filter brushes and textures: %.2fs" % (time() - _start_time))


## _start_time = time()
textures_data = []
for texture in textures:
    if texture.type != 'IMAGE':
        continue
    if not isinstance(texture, ImageTexture):
        continue
    if not texture.image:
        continue
    # if not exists(bpy_abspath(texture.image.filepath_raw)):
    #     continue

    # Generate a UUID for the texture.
    uuid = uuid4().hex

    # Copy name and UUID to BM data.
    texture['name'] = texture.name
    texture['uuid'] = uuid
    texture['brush_manager'] = 1

    # Pack texture.
    textures_data.append(
        {
            'uuid': uuid,
            'name': texture.name,
            'type': texture.type
        }
    )
## print("\t> Pack textures data: %.2fs" % (time() - _start_time))


## _start_time = time()
brushes_data = []
for brush in brushes:
    # Generate a UUID for the brush.
    uuid = uuid4().hex

    # Copy name and UUID to BM data.
    brush['name'] = brush.name
    brush['uuid'] = uuid
    brush['brush_manager'] = 1
    brush['texture_uuid'] = brush.texture['uuid'] if brush.texture is not None else ''

    # Pack brush.
    brushes_data.append(
        {
            'uuid': uuid,
            'name': brush.name,
            'type': getattr(brush, tool_attr),
            'use_custom_icon': brush.use_custom_icon,
            'texture_uuid': brush['texture_uuid']
        }
    )
## print("\t> Pack brush data: %.2fs" % (time() - _start_time))

## print("[DEBUG::TIME] Prepare data to export: %.2fs" % (time() - start_time))


## start_time = time()
with open(Paths.Scripts.EXPORT_JSON(), 'w') as file:
    file.write(json.dumps(
        {
            'brushes': brushes_data,
            'textures': textures_data
        }
    ))
## print("[DEBUG::TIME] Write export.json: %.2fs" % (time() - start_time))


## start_time = time()
bpy.ops.wm.save_mainfile()
## print("[DEBUG::TIME] Save .blend: %.2fs" % (time() - start_time))


## start_time = time()
'''for texture in textures:
    # Write texture to its own lib file.
    # NOTE: that we match the texture name with its UUID.
    uuid = texture['uuid']
    texture_libpath = Paths.Data.TEXTURE(uuid + '.blend')
    texture.name = uuid
    bpy.data.libraries.write(texture_libpath, {texture}, fake_user=True, compress=True)
    # texture.name = texture['name']
print("[DEBUG::TIME] Save texture lib .blend: %.2fs" % (time() - start_time))

start_time = time()
for brush in brushes:
    # Write brush to its own lib file.
    # NOTE: that we exclude the image texture from the lib file to reduce space usage.
    # As well as match the brush name with its UUID.
    uuid = brush['uuid']
    brush.name = uuid
    brush.texture = None
    bpy.data.libraries.write(Paths.Data.BRUSH(uuid + '.blend'), {brush}, fake_user=True, compress=True)
    bpy.data.libraries.write(Paths.Data.BRUSH(uuid + '.default.blend'), {brush}, fake_user=True, compress=True)
    # brush.name = brush['name']
    # brush.texture = brush_texture'''

# print(sys.argv)
process = subprocess.Popen(
    [
        bpy.app.binary_path,
        sys.argv[1],
        '--background',
        '--python',
        Paths.Scripts.WRITE_LIBS(),
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT,
    shell=False
)

## print("[DEBUG::TIME] Save brush lib .blend: %.2fs" % (time() - start_time))


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

BrushIcon = Paths.Icons.BRUSH
TextureIcon = Paths.Icons.TEXTURE

data_images = bpy.data.images

tagged_images_to_generate_with_pil = []
tagged_images_to_generate_with_bpy = []


def generate_thumbnail__pil(in_image_path: str, out_image_path: str) -> str:
    # filename = ''.join(c for c in filename if c in valid_filename_chars)
    ## print("PIL ->", in_image_path, out_image_path)
    with PILImage.open(in_image_path) as image:
        image.thumbnail(ICON_SIZE, PIL_RESAMPLING_NEAREST) # PIL_RESAMPLING_NEAREST # image.resize(ICON_SIZE, PIL_RESAMPLING_NEAREST)
        image.save(out_image_path, 'PNG')
    return out_image_path


def generate_thumbnail__bpy(in_image_path: str | ImageTexture, out_image_path: str):
    ## print("BPY ->", in_image_path, out_image_path)
    if isinstance(in_image_path, ImageTexture):
        texture: ImageTexture = in_image_path
        image: Image = texture.image
        image_user = texture.image_user

        # print("\t>>> ImageTexture", image.file_format)

        # WORKS FAST BUT NOT WITH LAYERS (FUCK PSD ADOBE)
        if image.source == 'FILE':
            # print("\t>>> FILE")
            temp_name = uuid4().hex
            preview = image_previews.load(temp_name, image.filepath_from_user(image_user=image_user), 'IMAGE')
            icon_image = bpy.data.images.new(texture['uuid'], *preview.image_size, alpha=True)
            icon_image.pixels.foreach_get(preview.image_pixels_float)
            # icon_image.filepath_raw = out_image_path
            # icon_image.save()
            icon_image.save_render(out_image_path, scene=scene)
            bpy.data.images.remove(icon_image)
            del icon_image
            del image_previews[temp_name]

        elif image.source == 'SEQUENCE':
            # image.scale(*ICON_SIZE)
            # print("\t>>> SEQUENCE")
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
        # print("\t>>> str | Path")
        if not exists(in_image_path) or not isfile(in_image_path):
            print("\t>>> ERROR! IMAGE NOT FOUND IN PATH!", in_image_path)
            return
        icon_image = bpy.data.images.load(in_image_path, check_existing=False)
        if icon_image is None:
            print("\t>>> ERROR! IMAGE INVALIDATED!", in_image_path)
            return
        icon_image.scale(*ICON_SIZE)
        # icon_image.filepath_raw = out_image_path # BrushIcon(brush['uuid'] + '.png')
        # icon_image.file_format = 'PNG'
        # icon_image.save()
        icon_image.save_render(out_image_path, scene=scene)
        bpy.data.images.remove(icon_image)
        del icon_image


def tag_generate_thumbnail(in_image_path: str | ImageTexture, out_image_path: str):
    if isinstance(in_image_path, ImageTexture):
        texture: ImageTexture = in_image_path
        image: Image = texture.image
        if image is None:
            return
        image_user = texture.image_user
        if HAS_PIL and image.file_format in {'PNG', 'JPEG'}:
            tagged_images_to_generate_with_pil.append((image.filepath_from_user(image_user=image_user), out_image_path))
        else:
            # if image.file_format not in {'PNG', 'JPEG'}:
            #     image.file_format = 'PNG'
            tagged_images_to_generate_with_bpy.append((texture, out_image_path))
    elif isinstance(in_image_path, str):
        root, ext = splitext(in_image_path)
        if HAS_PIL and ext in {'.png', '.jpg', 'jpeg'}:
            tagged_images_to_generate_with_pil.append((in_image_path, out_image_path))
        else:
            tagged_images_to_generate_with_bpy.append((in_image_path, out_image_path))


## start_time = time()
for _brush in brushes:
    if not _brush.use_custom_icon:
        continue
    icon_path = bpy_abspath(_brush.icon_filepath)
    if not exists(icon_path) or not isfile(icon_path):
        continue

    # print("Brush Icon:", _brush.name, icon_path)
    tag_generate_thumbnail(icon_path, BrushIcon(_brush['uuid'] + '.png'))
## print("[DEBUG::TIME] Tag brush icons: %.2fs" % (time() - start_time))

# ----------------------------------------------------------------
## start_time = time()

# temporal. first brush thumnails, then WILL TRY textures...
if HAS_PIL and len(tagged_images_to_generate_with_pil) != 0:
    import threading
    from multiprocessing import cpu_count
    from math import floor

    n_threads = int((cpu_count() / 5) * 3)
    n_images = len(tagged_images_to_generate_with_pil)
    n_images_per_thread_float = n_images / n_threads
    n_images_per_thread = floor(n_images_per_thread_float)

    def multi_generate_thumbnail__pil(images):
        for image in images:
            generate_thumbnail__pil(*image)
        return None

    threads: list[threading.Thread] = []

    def add_thread(images):
        thread = threading.Thread(target=multi_generate_thumbnail__pil, args=(images,))
        thread.start()
        # thread.daemon = True
        threads.append(thread)

    start_index = 0
    for cpu_index in range(n_threads-1):
        add_thread(
            tagged_images_to_generate_with_pil[start_index:start_index+n_images_per_thread]
        )
        start_index += n_images_per_thread

    add_thread(tagged_images_to_generate_with_pil[start_index:])

    # for (in_image_path, out_image_path) in tagged_images_to_generate_with_pil:

    for thread in threads:
        thread.join()

    # while 1:
    #     for thread in threads:
    #         if thread.is_alive:
    #             sleep(.1)
    #             continue
    #     break

if len(tagged_images_to_generate_with_bpy) != 0:
    for (in_image, out_image) in tagged_images_to_generate_with_bpy:
        generate_thumbnail__bpy(in_image, out_image)

## print("[DEBUG::TIME] Generate brush icons: %.2fs" % (time() - start_time))

# ----------------------------------------------------------------

sys.exit(0)

tagged_images_to_generate_with_bpy.clear()

for _texture in textures:
    if _texture.type != 'IMAGE':
        continue
    if not isinstance(_texture, ImageTexture):
        continue
    if _texture.image is None:
        continue
    tag_generate_thumbnail(_texture, TextureIcon(_texture['uuid'] + '.png'))


# GENERATE IMAGE THUMBNAILS WITH PIL.
if HAS_PIL and len(tagged_images_to_generate_with_pil) != 0:
    print("Generating with PIL...")
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
