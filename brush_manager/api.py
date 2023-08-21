from enum import Enum, auto
from brush_manager import data as bm_data, types as bm_types
from brush_manager.paths import Paths
import bpy

from brush_manager.data.addon_data import callback__AddonDataSave
from brush_manager.data.cats import callback__CatsAdd, callback__CatsRemove
from brush_manager.data.items import callback__ItemsAdd, callback__ItemsRemove, callback__ItemsMovePre, callback__ItemsMovePost

import brush_manager.ops as bm_ops


BM_UI = bm_types.UIProps
BM_DATA = bm_types.AddonData

get_bm_data = BM_DATA.get_data_by_context



class BM_SUB:
    class AddonData:
        SAVE = callback__AddonDataSave

    class Cats:
        ADD = callback__CatsAdd
        REMOVE = callback__CatsRemove

    class Items:
        ADD = callback__ItemsAdd
        REMOVE = callback__ItemsRemove
        MOVE_PRE = callback__ItemsMovePre
        MOVE_POST = callback__ItemsMovePost


class BM_OPS:
    def import_library(self,
                       ui_context_mode: str = '',
                       ui_context_type: str = ''):
        bm_ops.ImportLibrary('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def import_library_default(self,
                       libpath: str,
                       ui_context_mode: str = '',
                       ui_context_type: str = ''):
        bm_ops.ImportLibrary('EXEC_DEFAULT',
            filepath=libpath,
            use_modal=False,
            exclude_defaults=False,
            custom_uuid='DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    # ------------------------------------------------------


    def new_category(self,
                     cat_name: str | None = None,
                     ui_context_mode: str = '',
                     ui_context_type: str = ''):
        ''' If cat_name is not provided, it will popup an interface with a text field. '''
        bm_ops.NewCategory('INVOKE_DEFAULT' if cat_name is None else 'EXEC_DEFAULT',
            cat_name=cat_name,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def remove_active_category(self,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        bm_ops.RemoveCategory(
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def select_category(self,
                       cat_uuid: str,
                       ui_context_mode: str = '',
                       ui_context_type: str = ''):
        bm_ops.SelectCategory(
            cat_uuid=cat_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def move_selected_to_category(self,
                               cat_uuid: str | None = None,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        ''' If cat_name is not provided, it will popup an interface with a category selector. '''
        bm_ops.MoveSelectedToCategory('INVOKE_DEFAULT' if cat_uuid is None else 'EXEC_DEFAULT',
            select_category=cat_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def asign_icon_to_active_category(self,
                               ui_context_mode: str = '',
                               ui_context_type: str = ''):
        bm_ops.AsignIconToCategory('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )


    # ----------------------------------------------------------------


    def asign_icon_to_active_brush(self,
                                   ui_context_mode: str = ''):
        bm_ops.AsignIconToBrush('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_type='BRUSH',
        )

    def asign_icon_to_brush(self,
                            brush_uuid: str = '',
                            ui_context_mode: str = ''):
        bm_ops.AsignIconToBrush('INVOKE_DEFAULT',
            brush_uuid=brush_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_type='BRUSH',
        )

    def select_all(self,
                   ui_context_mode: str = '',
                   ui_context_type: str = ''):
        bm_ops.SelectAll(
            select_action='SELECT_ALL',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def select_item(self,
                    item_uuid: str = '',
                    ui_context_mode: str = '',
                    ui_context_type: str = ''):
        bm_ops.SelectItem(
            item_uuid=item_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )

    def deselect_all(self,
                   ui_context_mode: str = '',
                   ui_context_type: str = ''):
        bm_ops.SelectAll(
            select_action='DESELECT_ALL',
            ui_context_mode=ui_context_mode,
            ui_context_type=ui_context_type
        )
