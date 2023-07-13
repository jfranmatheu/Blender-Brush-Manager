import bpy
from brush_manager.paths import Paths


write_lib = bpy.data.libraries.write


for texture in bpy.data.textures:
    # Write texture to its own lib file.
    # NOTE: that we match the texture name with its UUID.
    if 'brush_manager' not in texture:
        continue

    uuid = texture['uuid']
    texture_libpath = Paths.Data.TEXTURE(uuid + '.blend')
    texture.name = uuid
    write_lib(texture_libpath, {texture}, fake_user=True, compress=True)


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
