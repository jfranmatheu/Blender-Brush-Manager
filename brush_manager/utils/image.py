from os.path import realpath, relpath, abspath, join, basename, dirname, exists, isfile
import bpy

from brush_manager.paths import Paths

images_folder = str(Paths.IMAGES)


def clear_image(image):
    if not image:
        return
    image.gl_free()  # free opengl image memory # Probably will be deprecated.
    image.buffers_free()
    image.user_clear()

def remove_image(image):
    if not image:
        return
    # delete image
    # print(image)
    bpy.data.images.remove(image, do_unlink=True, do_id_user=True, do_ui_user=True)

def load_image(image_name, ext='.png', from_path="brushes"):
    path = join(images_folder, from_path, image_name+ext)
    if not isfile(path):
        print("ERROR image [%s] not found in path [%s]" % (image_name, path))
        return None
    return bpy.data.images.load(path, check_existing=True)
    #img.name = '.'+img.name
    #return img

def load_image_from_file_dir(file, image_name, ext='.png', from_path="brushes"):
    path = join(images_folder, from_path, image_name+ext)
    if not isfile(path):
        return None
    return bpy.data.images.load(path, check_existing=True)

def load_image_from_filepath(filepath):
    if not isfile(filepath):
        return None
    return bpy.data.images.load(filepath, check_existing=True)
