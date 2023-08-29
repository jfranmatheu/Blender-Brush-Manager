import bpy
from bpy.types import ImageTexture
from brush_manager.paths import Paths

from os.path import exists


bpy.ops.file.make_paths_absolute()
bpy.ops.file.pack_all()


write_lib = bpy.data.libraries.write


checkfile = Paths.Scripts.CHECK__WRITE_LIBS(as_path=True)

checkfile.touch(exist_ok=True)



for brush in bpy.data.brushes:
    # Write brush to its own lib file.
    # NOTE: that we exclude the image texture from the lib file to reduce space usage.
    # As well as match the brush name with its UUID.
    if 'brush_manager' not in brush:
        continue

    uuid = brush['uuid']
    brush.name = uuid
    brush.texture = None
    write_lib(Paths.Data.BRUSH(uuid + '.blend'), {brush}, fake_user=True, compress=True)
    write_lib(Paths.Data.BRUSH(uuid + '.default.blend'), {brush}, fake_user=True, compress=True)


for texture in bpy.data.textures:
    # Write texture to its own lib file.
    # NOTE: that we match the texture name with its UUID.
    if 'brush_manager' not in texture:
        continue
    if texture.type != 'IMAGE':
        continue
    if not isinstance(texture, ImageTexture):
        continue
    if not texture.image:
        continue
    # if not exists(texture.image.filepath_raw):
    #     continue

    image = texture.image
    # image.pack()

    uuid = texture['uuid']
    texture_libpath = Paths.Data.TEXTURE(uuid + '.blend')
    texture.name = uuid
    write_lib(texture_libpath, {texture, image}, fake_user=True, compress=True)

    # image.unpack()


checkfile.unlink()
