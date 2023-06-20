import bpy
from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.app import timers

from functools import partial
from os.path import basename
from pathlib import Path
from time import time, sleep
import json
import subprocess

from ..paths import Paths
from .base_op import BaseOp
from ..types import AddonData
from ..icons import register_icons


def refresh_icons(process):
    while process.poll() is None:
        return 0.1
    register_icons()


class BRUSHMANAGER_OT_add_library(Operator, ImportHelper, BaseOp):
    bl_idname = 'brushmanager.add_library'
    bl_label = "Import a .blend Library"

    filename_ext = '.blend'

    filter_glob: StringProperty(
        default='*.blend',
        options={'HIDDEN'}
    )

    create_category: BoolProperty()

    def action(self, context: Context, addon_data: AddonData) -> None:
        export_json: Path = Paths.Scripts.EXPORT_JSON.value
        if export_json.exists():
            export_json.unlink(missing_ok=True)

        print("Start Subprocess")

        process = subprocess.Popen(
            [
                bpy.app.binary_path,
                self.filepath,
                '--background',
                '--python',
                Paths.Scripts.EXPORT(),
            ],
            stdin=None, # subprocess.PIPE,
            stdout=None, # subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False
        )

        timeout = time() + 60 # 1 minute timeout
        print("Wait until timeout or export json completion")
        while 1:
            if export_json.exists():
                print("WE CAN NOW IMPORT JSON DATA")
                break
            if time() > timeout:
                raise TimeoutError("BRUSHMANAGER_OT_add_library: Timeout expired")

        # timers.register(partial(refresh_icons, process), first_interval=1.0)

        libdata = None
        with export_json.open('r') as f:
            raw_data = f.read()
            if not raw_data:
                print("No raw data in export.json")
                return
            libdata: dict[str, dict] = json.loads(raw_data)

        if libdata is None:
            print("Invalid data in export.json")
            return

        export_json.unlink()

        sleep(1.0)

        brushes_data: dict[str, dict] = libdata['brushes']
        textures_data: dict[str, dict] = libdata['textures']

        print(f"export.json: brushes_count {len(brushes_data)} - textures_count {len(textures_data)}")

        lib_index = len(addon_data.libraries)
        lib = addon_data.libraries.add()
        lib.filepath = self.filepath
        addon_data.active_library_index = lib_index

        for br_uuid, br_data in brushes_data.items():
            item_uuid = lib.brushes.add()
            item_uuid.uuid = br_uuid
            item_uuid.name = br_data['name']

            brush_item = addon_data.brushes.add()
            brush_item.uuid = br_uuid
            brush_item.name = br_data['name']
            brush_item.type = br_data['type']
            brush_item.use_custom_icon = br_data['use_custom_icon']
            brush_item.texture_uuid = br_data['texture_uuid']

        for tex_uuid, tex_data in textures_data.items():
            item_uuid = lib.textures.add()
            item_uuid.uuid = tex_uuid
            item_uuid.name = tex_data['name']

            tex_item = addon_data.textures.add()
            tex_item.uuid = tex_uuid
            tex_item.name = tex_data['name']
            tex_item.type = tex_data['type']

        context.area.tag_redraw()



class BRUSHMANAGER_OT_remove_library(BaseOp, Operator):
    bl_idname = 'brushmanager.remove_library'
    bl_label = "Remove Library"

    def action(self, context: Context, addon_data: AddonData) -> None:
        active_lib = addon_data.active_library
        if not active_lib:
            return

        # Remove library brush data from brushes collection.
        brush_uuids = {brush.uuid for brush in active_lib.brushes}
        for idx, brush in enumerate(reversed(addon_data.brushes)):
            if brush.uuid in brush_uuids:
                addon_data.brushes.remove(idx)

        # Remove library brush references from brush categories collection.
        for brush_cat in addon_data.brush_cats:
            for idx, brush in enumerate(reversed(brush_cat.items)):
                if brush.uuid in brush_uuids:
                    brush_cat.items.remove(idx)

        # Remove library from library collection.
        addon_data.libraries.remove(addon_data.active_library_index)

        context.area.tag_redraw()


class BRUSHMANAGER_OT_select_library(BaseOp, Operator):
    bl_idname = 'brushmanager.select_library'
    bl_label = "Select Active Library"

    index: IntProperty()

    def action(self, context: Context, addon_data: AddonData) -> None:
        addon_data.active_library_index = self.index
        context.area.tag_redraw()
