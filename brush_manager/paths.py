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


class _Path_Enum(Enum):
    def __call__(self, *paths, as_path: bool = False) -> str | Path:
        if not paths:
            return self.value if as_path else str(self.value)
        return self.value.joinpath(*paths) if as_path else str(self.value.joinpath(*paths))


src_path = Path(__file__).parent
user_data = Path(b3d_appdata_path) / "addon_data" / __package__



class Paths: # (_Path, Enum)
    ROOT = src_path
    DATA = user_data

    class Lib(_Path_Enum):
        _LIB = src_path / 'lib'
        ICONS = _LIB / 'icons'

    class Scripts(_Path_Enum):
        _SCRIPTS = src_path / 'scripts'
        EXPORT = _SCRIPTS / 'export_brushes.py'
        EXPORT_JSON = _SCRIPTS / 'export.json'

    class Data: # (_Path, Enum)

        class Icons(_Path_Enum):
            _ICONS = user_data / "icons"

            BRUSH = _ICONS / "brushes"
            TEXTURE = _ICONS / "textures"
            CAT_BRUSH = _ICONS / "cat_brushes"
            CAT_TEXTURE = _ICONS / "cat_textures"


Paths.DATA.mkdir(parents=True, exist_ok=True)
Paths.Data.Icons._ICONS.value.mkdir(exist_ok=True)
Paths.Data.Icons.BRUSH.value.mkdir(exist_ok=True)
Paths.Data.Icons.TEXTURE.value.mkdir(exist_ok=True)
Paths.Data.Icons.CAT_BRUSH.value.mkdir(exist_ok=True)
Paths.Data.Icons.CAT_TEXTURE.value.mkdir(exist_ok=True)

'''
for path_cls in _Path_Enum.__subclasses__():
    for path_item in path_cls:
        print(path_cls, path_item)
        if hasattr(path_item, 'value'):
            print("\t>>> " + str(path_item.value))
            dirpath: Path = path_item.value
            if not dirpath.exists() and dirpath.is_dir():
                dirpath.mkdir(parents=True)
'''