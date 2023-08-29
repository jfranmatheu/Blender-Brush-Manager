import bpy
from bpy.types import Event, Context

from bpy.props import StringProperty, BoolProperty

from os.path import basename
from pathlib import Path
from time import time, sleep
import json
import subprocess
from collections import deque
from typing import Type

from ..paths import Paths
from ..types import UIProps, AddonDataByMode, BrushItem, TextureItem, Item
from brush_manager.addon_utils import Reg
from brush_manager.globals import GLOBALS



@Reg.Ops.setup
class ImportLibrary(Reg.Ops.Import.BLEND):
    bl_idname = 'brushmanager.import_library'
    bl_label = "Import a .blend Library"

    # INTERNAL PROPERTY... MUST HAVE ENABLED.
    create_category: BoolProperty(
        default=True,
        name="Setup Category",
        description="Create a category from",
        options={'HIDDEN'}
    )

    custom_uuid: StringProperty(default='')

    exclude_defaults: BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})

    use_modal: BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})

    def action(self, context: Context, ui_props: UIProps, addon_data: AddonDataByMode) -> None:
        print("[brush_manager] ImportLibrary:", self.filepath)

        if self.filepath == '':
            raise ValueError("filepath must not be empty")
            return {'CANCELLED'}

        GLOBALS.is_importing_a_library = True

        export_json: Path = Paths.Scripts.EXPORT_JSON.value
        if export_json.exists():
            export_json.unlink(missing_ok=True)

        print("Start Subprocess")

        self.process = subprocess.Popen(
            [
                bpy.app.binary_path,
                self.filepath,
                '--background',
                '--python',
                Paths.Scripts.EXPORT(),
                '-',
                ui_props.ui_context_mode,
                str(int(self.exclude_defaults))
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=False
        )

        timeout = time() + 60 # 1 minute timeout
        ## print("Wait until timeout or export json completion")
        while 1:
            if export_json.exists():
                ## print("WE CAN NOW IMPORT JSON DATA")
                break
            if time() > timeout:
                raise TimeoutError("ImportLibrary: Timeout expired for checking json existence")

        sleep(0.1)

        timeout = time() + 60 # 1 minute timeout
        libdata = None
        while libdata is None:
            with export_json.open('r') as f:
                raw_data = f.read()
                if not raw_data:
                    print("\t> No raw data in export.json")
                    sleep(0.1)
                    return
                libdata: dict[str, dict] = json.loads(raw_data)

            if time() > timeout:
                raise TimeoutError("ImportLibrary: Timeout expired for reading json")

        if libdata is None:
            print("\t> Invalid data in export.json")
            self.end()
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
            self.end()
            return {'CANCELLED'}

        # Create category.
        brush_cat = None
        texture_cat = None

        ui_props = UIProps.get_data(context)

        lib_name = Path(self.filepath).stem.title()

        if textures_count != 0:
            print("Create Texture Category")
            ui_props.ui_context_item = 'TEXTURE'
            texture_cat = addon_data.new_texture_cat(lib_name, self.custom_uuid)

        if brushes_count != 0:
            print("Create Brush Category")
            ui_props.ui_context_item = 'BRUSH'
            brush_cat = addon_data.new_brush_cat(lib_name, self.custom_uuid)

        # Util functions to add data items.
        brush_cat_items_add = brush_cat.items.add if brushes_count != 0 else None
        texture_cat_items_add = texture_cat.items.add if textures_count != 0 else None

        texture_items: dict[str, object] = {}

        def _add_brush_to_data(item_data: dict):
            tex_item = texture_items.get(item_data.pop('texture_uuid', ''), None)
            brush_cat_items_add(texture=tex_item, **item_data) # item_data['uuid']

        def _add_tex_to_data(item_data: dict):
            texture_items[item_data['uuid']] = texture_cat_items_add(**item_data)

        self.add_brush_to_data = _add_brush_to_data
        self.add_texture_to_data = _add_tex_to_data

        self.refresh_timer = time() + .2
        self.addon_data = addon_data

        if self.use_modal:
            # print("Create Modal Handler and Timer!")
            if not context.window_manager.modal_handler_add(self):
                print("ERROR: Window Manager was unable to add a modal handler")
                self.end()
                return {'CANCELLED'}
            self._timer = context.window_manager.event_timer_add(0.000001, window=context.window)
            self.tag_redraw()
            return {'RUNNING_MODAL'}

        while 1:
            if 'FINISHED' in self.modal(None, None):
                break
        self.end()
        return {'FINISHED'}


    def end(self):
        ## self.process.wait()
        GLOBALS.is_importing_a_library = False

    def modal(self, context: Context, event: Event):
        # print(event.type, event.value)

        if event is not None and event.type != 'TIMER':
            return {'PASS_THROUGH'}

        # print("Modal Timer Event...", self.brushes_count, self.textures_count)
        if context is not None:
            if time() > self.refresh_timer:
                # Don't over-refresh!
                self.refresh_timer = time() + .2
                self.tag_redraw()

        if self.textures_count != 0:
            self.textures_count -= 1
            self.add_texture_to_data(self.textures.popleft())

            return {'RUNNING_MODAL'}

        if self.brushes_count != 0:
            self.brushes_count -= 1
            self.add_brush_to_data(self.brushes.popleft())

            return {'RUNNING_MODAL'}

        if self.brushes_count == 0 and self.textures_count == 0:
            ## print("FINISHED!")
            if context is not None:
                context.window_manager.event_timer_remove(self._timer)
                del self._timer
            self.end()
            self.addon_data.save()
            return {'FINISHED'}

        return {'RUNNING_MODAL'}
