import bpy
from bpy.types import Event, Operator, Context
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .base_op import BaseOp
from ..types import AddonData, UIProps


def get_cateogry_items(self, context: Context):
    addon_data = AddonData.get_data_by_ui_mode(context)
    cat_type = UIProps.get_data(context).ui_item_type_context
    if cat_type == 'BRUSH':
        cats = addon_data.brush_cats
    elif cat_type == 'TEXTURE':
        cats = addon_data.texture_cats
    return [
        (cat.uuid, cat.name, cat.name) for cat in cats
    ]


class BRUSHMANAGER_OT_append_selected_from_library_to_category(BaseOp, Operator):
    bl_idname = 'brushmanager.append_selected_from_library_to_category'
    bl_label = "Append Selected from Library To Category"
    bl_options = {'REGISTER', 'UNDO'}

    select_category : EnumProperty(
        name="Select a Category",
        items=get_cateogry_items
    )

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_popup(self, event)

    def action(self, context: Context, addon_data: AddonData) -> None:
        if not self.select_category:
            return

        ui_props = UIProps.get_data(context)
        cat_type = ui_props.ui_item_type_context

        if cat_type == 'BRUSH':
            # cat = addon_data.active_brush_cat
            dst_cat = addon_data.get_brush_cat(self.select_category)
            selected_items = addon_data.selected_brushes
            addon_data.set_active_brush_category(dst_cat)
        elif cat_type == 'TEXTURE':
            # cat = addon_data.active_texture_cat
            dst_cat = addon_data.get_texture_cat(self.select_category)
            selected_items = addon_data.selected_textures
            addon_data.set_active_texture_category(dst_cat)
        else:
            return

        cat_items = dst_cat.items

        for item in selected_items:
            cat_item = cat_items.add()
            cat_item.uuid = item.uuid
            cat_item.name = item.name

        ui_props.ui_active_section = 'CATS'
        
        BRUSHMANAGER_OT_select_all.run(select_action='DESELECT_ALL')

        context.area.tag_redraw()


class BRUSHMANAGER_OT_select_all(BaseOp, Operator):
    bl_idname = 'brushmanager.select_all'
    bl_label = "Select All"

    select_action: StringProperty()

    def action(self, context: Context, addon_data: AddonData) -> None:
        ui_props = UIProps.get_data(context)
        cat_type = ui_props.ui_item_type_context

        if cat_type == 'BRUSH':
            items = addon_data.brushes
            selected_items = addon_data.selected_brushes
        elif cat_type == 'TEXTURE':
            items = addon_data.textures
            selected_items = addon_data.selected_textures
        else:
            return

        if self.select_action == 'TOGGLE':
            for item in items:
                item.selected = not item.selected

        elif self.select_action == 'DESELECT_ALL':
            for item in selected_items:
                item.selected = False

        elif self.select_action == 'SELECT_ALL':
            for item in addon_data.brushes:
                item.selected = True

        context.area.tag_redraw()


class BRUSHMANAGER_OT_remove_selected_from_category(BaseOp, Operator):
    bl_idname = 'brushmanager.remove_selected_from_category'
    bl_label = "Remove Selected from Active Category"

    def action(self, context: Context, addon_data: AddonData) -> None:
        ui_props = UIProps.get_data(context)
        cat_type = ui_props.ui_item_type_context

        if cat_type == 'BRUSH':
            act_cat_items = addon_data.active_brush_cat.items
            selected_items = addon_data.selected_brushes
        elif cat_type == 'TEXTURE':
            act_cat_items = addon_data.active_texture_cat.items
            selected_items = addon_data.selected_textures
        else:
            return

        selected_items_uuids = {sel_item.uuid for sel_item in selected_items}
        for index, cat_item in reversed(list(enumerate(act_cat_items))): # enumerate(reversed(act_cat_items)):
            if cat_item.uuid in selected_items_uuids:
                selected_items_uuids.remove(cat_item.uuid)
                act_cat_items.remove(index)
                if len(selected_items_uuids) == 0:
                    break

        BRUSHMANAGER_OT_select_all.run(select_action='DESELECT_ALL')

        context.area.tag_redraw()


class BRUSHMANAGER_OT_moved_selected_to_category(BaseOp, Operator):
    bl_idname = 'brushmanager.moved_selected_to_category'
    bl_label = "Move Selected to Category"
    bl_options = {'REGISTER', 'UNDO'}

    select_category : EnumProperty(
        name="Select a Category",
        items=get_cateogry_items
    )

    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_popup(self, event)

    def action(self, context: Context, addon_data: AddonData) -> None:
        if not self.select_category:
            return

        ui_props = UIProps.get_data(context)
        cat_type = ui_props.ui_item_type_context

        if cat_type == 'BRUSH':
            selected_items = addon_data.selected_brushes
            dst_cat_items = addon_data.get_brush_cat(self.select_category).items
        elif cat_type == 'TEXTURE':
            selected_items = addon_data.selected_textures
            dst_cat_items = addon_data.get_texture_cat(self.select_category).items
        else:
            return

        BRUSHMANAGER_OT_remove_selected_from_category.run()

        for sel_item in selected_items:
            cat_item = dst_cat_items.add()
            cat_item.uuid = sel_item.uuid
            cat_item.name = sel_item.name

        if cat_type == 'BRUSH':
            addon_data.set_active_brush_category(self.select_category)
        elif cat_type == 'TEXTURE':
            addon_data.set_active_texture_category(self.select_category)

        ui_props.ui_active_section = 'CATS'

        context.area.tag_redraw()


class BRUSHMANAGER_OT_duplicate_selected(BaseOp, Operator):
    bl_idname = 'brushmanager.duplicate_selected'
    bl_label = "Duplicate Selected"

    def action(self, context: Context, addon_data: AddonData) -> None:
        ui_props = UIProps.get_data(context)
        cat_type = ui_props.ui_item_type_context

        if cat_type == 'BRUSH':
            act_cat_items = addon_data.active_brush_cat.items
            selected_items = addon_data.selected_brushes
        elif cat_type == 'TEXTURE':
            act_cat_items = addon_data.active_texture_cat.items
            selected_items = addon_data.selected_textures
        else:
            return

        BRUSHMANAGER_OT_select_all.run(select_action='DESELECT_ALL')

        # TODO: Duplicate code ???
