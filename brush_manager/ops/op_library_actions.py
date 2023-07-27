import bpy
from bpy.types import Event, Operator, Context

from bpy.props import StringProperty, BoolProperty, IntProperty

from os.path import basename
from pathlib import Path
from time import time, sleep
import json
import subprocess
from collections import deque

from ..paths import Paths
from .base_op import BaseOp
from ..types import UIProps, AddonDataByMode
from ..icons import register_icons
from brush_manager.addon_utils import Reg
from .op_category_actions import NewCategory



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

    def action(self, context: Context, addon_data: AddonDataByMode) -> None:
        print("Import Library data from:", self.filepath)

        if self.filepath == '':
            raise ValueError("filepath must not be empty")
            return {'CANCELLED'}

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
                UIProps.get_data(context).ui_context_mode,
                str(int(self.exclude_defaults))
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
                raise TimeoutError("ImportLibrary: Timeout expired for checking json existence")

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
                raise TimeoutError("ImportLibrary: Timeout expired for reading json")

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

        # Create library.
        print("Create library")
        lib_index = len(addon_data.libraries)
        lib = addon_data.libraries.add()
        lib.filepath = self.filepath
        addon_data.active_library_index = lib_index
        self.update_cache = addon_data._update_indices

        # Create category.
        brush_cat = None
        texture_cat = None

        if self.create_category:
            ui_props = UIProps.get_data(context)
            ui_props.ui_active_section = 'CATS'

            if textures_count != 0:
                print("Create Texture Category")
                ui_props.ui_context_item = 'TEXTURE'
                texture_cat = addon_data.new_texture_cat(lib.name)
                if self.custom_uuid:
                    texture_cat.uuid = self.custom_uuid

            if brushes_count != 0:
                print("Create Brush Category")
                ui_props.ui_context_item = 'BRUSH'
                brush_cat = addon_data.new_brush_cat(lib.name)
                if self.custom_uuid:
                    brush_cat.uuid = self.custom_uuid

        # Util functions to add data items.
        addon_data_brushes_add = addon_data.brushes.add
        addon_data_textures_add = addon_data.textures.add

        lib_brushes_add = lib.add_brush
        lib_textures_add = lib.add_texture

        brush_cat_items_add = brush_cat.add_item if brushes_count != 0 else None
        texture_cat_items_add = texture_cat.add_item if textures_count != 0 else None

        def _add_item_to_data(item_data: dict, add_data_func: callable, add_to_lib_func: callable, add_to_cat_func: callable):
            data_item = add_data_func()
            for key, value in item_data.items():
                setattr(data_item, key, value)

            add_to_lib_func(data_item)

            if self.create_category:
                add_to_cat_func(data_item) # item_data['uuid']

        self.add_brush_to_data = lambda brush_data: _add_item_to_data(brush_data, addon_data_brushes_add, lib_brushes_add, brush_cat_items_add)
        self.add_texture_to_data = lambda texture_data: _add_item_to_data(texture_data, addon_data_textures_add, lib_textures_add, texture_cat_items_add)

        self.refresh_timer = time() + .2

        if self.use_modal:
            # print("Create Modal Handler and Timer!")
            if not context.window_manager.modal_handler_add(self):
                print("ERROR: Window Manager was unable to add a modal handler")
                return {'CANCELLED'}
            self._timer = context.window_manager.event_timer_add(0.000001, window=context.window)
            self.tag_redraw()
            return {'RUNNING_MODAL'}

        while 1:
            if 'FINISHED' in self.modal(None, None):
                break
        return {'FINISHED'}


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

        if self.brushes_count != 0:
            self.brushes_count -= 1
            self.add_brush_to_data(self.brushes.popleft())

        if self.textures_count != 0:
            self.textures_count -= 1
            self.add_texture_to_data(self.textures.popleft())

        if self.brushes_count == 0 and self.textures_count == 0:
            print("FINISHED!")
            self.update_cache()
            if context is not None:
                context.window_manager.event_timer_remove(self._timer)
                del self._timer
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


@Reg.Ops.setup
class RemoveActiveLibrary(Reg.Ops.ACTION):

    def action(self, context: Context, addon_data: AddonDataByMode) -> None:
        target_lib = addon_data.active_library
        index = addon_data.active_library_index

        # Remove library brush data from brushes collection.
        brush_uuids = {brush.uuid for brush in target_lib.brushes}
        remove_brush = addon_data.brushes.remove
        for idx, brush in reversed(list(enumerate(addon_data.brushes))):
            if brush.uuid in brush_uuids:
                remove_brush(idx)

        # Remove library brush data from textures collection.
        texture_uuids = {texture.uuid for texture in target_lib.textures}
        remove_texture = addon_data.textures.remove
        for idx, texture in reversed(list(enumerate(addon_data.textures))):
            if texture.uuid in texture_uuids:
                remove_texture(idx)

        # Remove library brush references from brush categories collection.
        for brush_cat in addon_data.brush_cats:
            remove_brush = brush_cat.x_items.remove
            for idx, brush in reversed(list(enumerate(brush_cat.x_items))):
                if brush.uuid in brush_uuids:
                    remove_brush(idx)

        # Remove library texture references from texture categories collection.
        for tex_cat in addon_data.texture_cats:
            remove_texture = tex_cat.x_items.remove
            for idx, texture in reversed(list(enumerate(tex_cat.x_items))):
                if texture.uuid in texture_uuids:
                    remove_texture(idx)

        # Remove library from library collection.
        addon_data.libraries.remove(index)

        # Update cache.
        addon_data._update_indices()

        self.tag_redraw()


@Reg.Ops.setup
class SelectLibraryAtIndex(Reg.Ops.ACTION):

    index: IntProperty()

    def action(self, context: Context, addon_data: AddonDataByMode) -> None:
        addon_data.active_library_index = self.index
        self.tag_redraw()


@Reg.Ops.setup
class ImportBuiltinLibraries(Reg.Ops.ACTION):

    # use_modal: BoolProperty(default=True)

    def action(self, context: Context, addon_data: AddonDataByMode) -> None:
        from dataclasses import dataclass

        @dataclass
        class FakeAddLibraryOp:
            filepath: str
            create_category: bool
            custom_uuid: str
            exclude_defaults: bool
            use_modal: bool

            def modal(self, context=None, event=None):
                return ImportLibrary.modal(self, context, event)

        import glob
        from os.path import splitext
        for filepath in glob.glob(str(Paths.LIB / '*.blend')):
            uuid, ext = splitext(basename(filepath))

            cat = addon_data.get_brush_cat(uuid) or addon_data.get_texture_cat(uuid)
            if cat is None:
                ImportLibrary.action(
                    FakeAddLibraryOp(filepath, True, uuid, uuid!='default', False),
                    context,
                    addon_data
                )

        self.tag_redraw()
