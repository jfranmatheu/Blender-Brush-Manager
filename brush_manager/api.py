from enum import Enum, auto
from brush_manager import data as bm_data, types as bm_types
from brush_manager.paths import Paths
import bpy
from brush_manager.globals import GLOBALS

from brush_manager.data.addon_data import callback__AddonDataSave, callback__AddonDataInit, callback__AddonDataLoad
from brush_manager.data.cats import callback__CatsAdd, callback__CatsRemove
from brush_manager.data.items import callback__ItemsAdd, callback__ItemsRemove, callback__ItemsMovePre, callback__ItemsMovePost

import brush_manager.ops as bm_ops


BM_UI = bm_types.UIProps
BM_DATA = bm_types.AddonData # Utility like the 

get_bm_data = bm_types.AddonData.get_data_by_context



class BM_SUB:
    class AddonData:
        INIT = callback__AddonDataInit
        LOAD = callback__AddonDataLoad
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
    @staticmethod
    def import_library(
                       ui_context_mode: str = '',
                       ui_context_item: str = ''):
        bm_ops.ImportLibrary.run('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def import_library_default(
                       libpath: str,
                       ui_context_mode: str = '',
                       ui_context_item: str = ''):
        bm_ops.ImportLibrary.run('EXEC_DEFAULT',
            filepath=libpath,
            use_modal=False,
            exclude_defaults=False,
            custom_uuid='DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    # ------------------------------------------------------

    @staticmethod
    def new_category(
                     cat_name: str | None = None,
                     ui_context_mode: str = '',
                     ui_context_item: str = ''):
        ''' If cat_name is not provided, it will popup an interface with a text field. '''
        bm_ops.NewCategory.run('INVOKE_DEFAULT' if cat_name is None else 'EXEC_DEFAULT',
            cat_name=cat_name if cat_name is not None else '',
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def remove_active_category(
                               ui_context_mode: str = '',
                               ui_context_item: str = ''):
        bm_ops.RemoveCategory.run(
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def select_category(
                       cat_uuid: str,
                       ui_context_mode: str = '',
                       ui_context_item: str = ''):
        bm_ops.SelectCategory.run(
            cat_uuid=cat_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def move_selected_to_category(
                               # cat_uuid: str | None = None,
                               ui_context_mode: str = '',
                               ui_context_item: str = ''):
        ''' If cat_name is not provided, it will popup an interface with a category selector. '''
        bm_ops.MoveSelectedToCategory.run('INVOKE_DEFAULT', # if cat_uuid is None else 'EXEC_DEFAULT',
            # select_category=cat_uuid if cat_uuid is not None else '',
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def asign_icon_to_active_category(ui_context_mode: str = '',
                                      ui_context_item: str = ''):
        bm_ops.AsignIconToCategory.run('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )
    
    @staticmethod
    def asign_icon_to_category(cat_uuid: str = '',
                               ui_context_mode: str = '',
                               ui_context_item: str = ''):
        bm_ops.AsignIconToCategory.run('INVOKE_DEFAULT',
            cat_uuid=cat_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def rename_cat(
                    cat_uuid: str = '',
                    ui_context_mode: str = '',
                    ui_context_item: str = ''):
        bm_ops.RenameCategory.run('INVOKE_DEFAULT',
            cat_uuid=cat_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )


    # ----------------------------------------------------------------

    @staticmethod
    def asign_icon_to_active_brush(ui_context_mode: str = ''):
        bm_ops.AsignIconToBrush.run('INVOKE_DEFAULT',
            ui_context_mode=ui_context_mode,
            ui_context_item='BRUSH',
        )

    @staticmethod
    def asign_icon_to_brush(
                            brush_uuid: str = '',
                            ui_context_mode: str = ''):
        bm_ops.AsignIconToBrush.run('INVOKE_DEFAULT',
            brush_uuid=brush_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_item='BRUSH',
        )

    @staticmethod
    def select_all(
                   ui_context_mode: str = '',
                   ui_context_item: str = ''):
        bm_ops.SelectAll.run(
            select_action='SELECT_ALL',
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def select_item(
                    item_uuid: str = '',
                    ui_context_mode: str = '',
                    ui_context_item: str = ''):
        bm_ops.SelectItem.run(
            item_uuid=item_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def deselect_all(
                   ui_context_mode: str = '',
                   ui_context_item: str = ''):
        bm_ops.SelectAll.run(
            select_action='DESELECT_ALL',
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )

    @staticmethod
    def rename_item(
                    item_uuid: str = '',
                    ui_context_mode: str = '',
                    ui_context_item: str = ''):
        bm_ops.RenameItem.run('INVOKE_DEFAULT',
            item_uuid=item_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_item=ui_context_item
        )
        
    @staticmethod
    def duplicate_brush(brush_uuid: str = '',
                        ui_context_mode: str = ''):
        bm_ops.DuplicateBrush.run(
            brush_uuid=brush_uuid,
            ui_context_mode=ui_context_mode,
            ui_context_item='BRUSH'
        )
