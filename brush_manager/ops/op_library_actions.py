import bpy
from bpy.types import Event, Operator, Context
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, IntProperty

from os.path import basename
from pathlib import Path
from time import time, sleep
import json
import subprocess
from collections import deque

from ..paths import Paths
from .base_op import BaseOp
from ..types import AddonData, UIProps, AddonDataByMode
from ..icons import register_icons
from brush_manager.addon_utils import Reg
from .op_category_actions import NewCategory


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

    # INTERNAL PROPERTY... MUST HAVE ENABLED.
    create_category: BoolProperty(
        default=True,
        name="Setup Category",
        description="Create a category from",
        options={'HIDDEN'}
    )

    def action(self, context: Context, addon_data: AddonDataByMode) -> None:
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
                '-',
                # AddonData.get_data(context).context_mode
                UIProps.get_data(context).ui_context_mode
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
                raise TimeoutError("BRUSHMANAGER_OT_add_library: Timeout expired for checking json existence")

        # timers.register(partial(refresh_icons, process), first_interval=1.0)
        sleep(0.1)

        timeout = time() + 60 # 1 minute timeout
        libdata = None
        while libdata is None:
            with export_json.open('r') as f:
                raw_data = f.read()
                if not raw_data:
                    print("No raw data in export.json")
                    sleep(0.1)
                    return
                libdata: dict[str, dict] = json.loads(raw_data)

            if time() > timeout:
                raise TimeoutError("BRUSHMANAGER_OT_add_library: Timeout expired for reading json")

        if libdata is None:
            print("Invalid data in export.json")
            return {'CANCELLED'}

        export_json.unlink()

        # PREPARE queue FOR MODAL ITERATION.
        self.brushes = deque(libdata['brushes'])
        self.textures = deque(libdata['textures'])

        self.brushes_count = brushes_count = len(self.brushes)
        self.textures_count = textures_count = len(self.textures)

        print(f"export.json: brushes_count {brushes_count} - textures_count {textures_count}")

        if brushes_count == 0 and textures_count == 0:
            print("WARN: No data in export.json")
            return {'CANCELLED'}

        # PREPARE MODAL.
        if not context.window_manager.modal_handler_add(self):
            print("ERROR: Window Manager was unable to add a modal handler")
            return {'CANCELLED'}
        self._timer = context.window_manager.event_timer_add(0.000001, window=context.window)

        # Create library.
        print("Create library")
        lib_index = len(addon_data.libraries)
        lib = addon_data.libraries.add()
        lib.filepath = self.filepath
        addon_data.active_library_index = lib_index

        # Create category.
        brush_cat = None
        texture_cat = None

        if self.create_category:
            ui_props = UIProps.get_data(context)
            ui_props.ui_active_section = 'CATS'

            if textures_count != 0:
                print("Create Texture Category")
                ui_props.ui_item_type_context = 'TEXTURE'
                NewCategory.action(self, context, addon_data)
                texture_cat = addon_data.active_texture_cat
                texture_cat.name = lib.name

            if brushes_count != 0:
                print("Create Brush Category")
                ui_props.ui_item_type_context = 'BRUSH'
                NewCategory.action(self, context, addon_data)
                brush_cat = addon_data.active_brush_cat
                brush_cat.name = lib.name

        # Util functions to add data items.
        addon_data_brushes_add = addon_data.brushes.add
        addon_data_textures_add = addon_data.textures.add

        lib_brushes_add = lib.brushes.add
        lib_textures_add = lib.textures.add

        brush_cat_items_add = brush_cat.items.add if brushes_count != 0 else None
        texture_cat_items_add = texture_cat.items.add if textures_count != 0 else None

        def _add_item_to_data(item_data: dict, add_data_func: callable, add_to_lib_func: callable, add_to_cat_func: callable):
            lib_item = add_to_lib_func()
            lib_item.uuid = item_data['uuid']

            if self.create_category:
                cat_item = add_to_cat_func()
                cat_item.uuid = item_data['uuid']

            data_item = add_data_func()
            for key, value in item_data.items():
                setattr(data_item, key, value)

        self.add_brush_to_data = lambda brush_data: _add_item_to_data(brush_data, addon_data_brushes_add, lib_brushes_add, brush_cat_items_add)
        self.add_texture_to_data = lambda texture_data: _add_item_to_data(texture_data, addon_data_textures_add, lib_textures_add, texture_cat_items_add)

        self.refresh_timer = time() + .2

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def modal(self, context: Context, event: Event):
        # print(event.type, event.value)

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        # print("Modal Timer Event...", self.brushes_count, self.textures_count)
        if time() > self.refresh_timer:
            # Don't over-refresh!
            self.refresh_timer = time() + .2
            context.region.tag_redraw()

        if self.brushes_count != 0:
            self.brushes_count -= 1
            self.add_brush_to_data(self.brushes.popleft())

        if self.textures_count != 0:
            self.textures_count -= 1
            self.add_texture_to_data(self.textures.popleft())

        if self.brushes_count == 0 and self.textures_count == 0:
            context.window_manager.event_timer_remove(self._timer)
            del self._timer
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


@Reg.Ops.setup
class RemoveLibrary(Reg.Ops.ACTION):

    def action(self, context: Context, addon_data: AddonData) -> None:
        active_lib = addon_data.active_library
        if not active_lib:
            return

        # Remove library brush data from brushes collection.
        brush_uuids = {brush.uuid for brush in active_lib.brushes}
        for idx, brush in reversed(list(enumerate(addon_data.brushes))): # enumerate(reversed(addon_data.brushes)):
            if brush.uuid in brush_uuids:
                addon_data.brushes.remove(idx)

        # Remove library brush references from brush categories collection.
        for brush_cat in addon_data.brush_cats:
            for idx, brush in reversed(list(enumerate(brush_cat.items))): # enumerate(reversed(brush_cat.items)):
                if brush.uuid in brush_uuids:
                    brush_cat.items.remove(idx)

        # Remove library from library collection.
        addon_data.libraries.remove(addon_data.active_library_index)

        context.area.tag_redraw()


@Reg.Ops.setup
class SelectActiveLibrary(Reg.Ops.ACTION):

    index: IntProperty()

    def action(self, context: Context, addon_data: AddonData) -> None:
        addon_data.active_library_index = self.index
        context.area.tag_redraw()
