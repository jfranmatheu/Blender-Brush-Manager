from enum import Enum

from pathlib import Path
from enum import Enum
from os.path import join, dirname, exists, isdir
from os import mkdir
import sys

import bpy

b3d_user_path = bpy.utils.resource_path('USER')
b3d_config_path = join(b3d_user_path, "config")

b3d_appdata_path = dirname(bpy.utils.resource_path('USER'))

"""
* Linux *
LOCAL: ./3.1/
USER: $HOME/.config/blender/3.1/
SYSTEM: /usr/share/blender/3.1/
-----
* Mac OS *
LOCAL: ./3.1/
USER: /Users/$USER/Library/Application Support/Blender/3.1/
SYSTEM: /Library/Application Support/Blender/3.1/
-----
* Windows *
LOCAL: .\3.1\
USER: %USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\3.1\
SYSTEM: %USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\3.1\
"""


def get_addondatadir() -> Path:

    '''
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    '''

    home = Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/Blender Foundation/Blender/addon_data"
    elif sys.platform == "linux":
        return home / ".local/share/blender/addon_data"
    elif sys.platform == "darwin":
        return home / "Library/Application Support/Blender/addon_data"

    '''
    import os

    configpath = os.path.join(
        os.environ.get('APPDATA') or
        os.environ.get('XDG_CONFIG_HOME') or
        os.path.join(os.environ['HOME'], '.config'),
        "Blender Foundation"
    )
    print(configpath)
    '''


class _Path:
    def __call__(self, *paths) -> str | Path:
        if not paths:
            return self.value
        return str(self.value.joinpath(*paths))


user_data = Path(b3d_appdata_path) / "addon_data" / __package__


class Paths(_Path, Enum):
    ROOT = Path(__file__).parent
    DATA = user_data

    class Data(_Path, Enum):

        class Icons(_Path, Enum):
            _ICONS = user_data / "icons"

            BRUSH = _ICONS / "brushes"
            TEXTURE = _ICONS / "textures"
            CAT_BRUSH = _ICONS / "cat_brushes"
            CAT_TEXTURE = _ICONS / "cat_textures"


for path in Paths:
    dirpath: Path = path.value
    if not dirpath.exists() and dirpath.is_dir():
        dirpath.mkdir(parents=True)
