import bpy.utils.previews
from gpu.types import GPUTexture
from bpy.utils import previews

import glob
from os.path import basename


runtime_previews = previews.new()
gputex_cache = {}


def new_preview(filepath: str) -> None:
    return runtime_previews.load(
        basename(filepath)[:-4],
        filepath,
        'IMAGE'
    )

def get_preview(uuid: str, filepath: str = None) -> int | None:
    if preview := runtime_previews.get(uuid, None):
        return preview
    if filepath is not None:
        return new_preview(filepath)
    return None


def new_gputex(filepath: str) -> GPUTexture:
    # TODO. copy from other project.
    pass

def get_gputex(uuid: str, filepath: str) -> GPUTexture:
    if gputex := gputex_cache.get(uuid, None):
        return gputex
    if filepath is not None:
        return new_gputex(filepath)
    return None


def register():
    from .paths import Paths

    for filepath in glob.glob(Paths.Data.Icons._ICONS('**', '*.png')):
        new_preview(filepath)
        new_gputex(filepath)


def unregister():
    runtime_previews.close()
