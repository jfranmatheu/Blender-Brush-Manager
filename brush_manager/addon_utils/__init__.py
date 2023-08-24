import re
from typing import Union

from bpy.types import Operator

from .operator import OpsAction, OpsInvokePropsPopup, OpsImportBlend, OpsImportPNG


class Reg:
    class Ops:
        ACTION = OpsAction
        INVOKE_PROPS_POPUP = OpsInvokePropsPopup

        class Import:
            BLEND = OpsImportBlend
            PNG = OpsImportPNG


        @staticmethod
        def setup(deco_cls) -> Union[OpsAction, Operator]:
            #### print("[brush_manager] Setup operator:", deco_cls.__name__)
            keywords = re.findall('[A-Z][^A-Z]*', deco_cls.__name__)
            idname: str = '_'.join([word.lower() for word in keywords])

            return type(
                'BRUSHMANAGER_OT_' + idname,
                (deco_cls, Operator),
                {
                    'bl_idname': 'brush_manager.' + idname,
                    'bl_label': deco_cls.label if hasattr(deco_cls, 'label') else ' '.join(keywords),
                }
            )
