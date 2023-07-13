from enum import Enum

from brush_manager.paths import Paths
from brush_manager.icons import get_preview, get_gputex, GPUTexture


class DefaultBrushIcon(Enum):
    # SCULPT MDOE
    DEFAULT = ".Default_icon"
    DRAW = '.Draw_icon'
    DRAW_SHARP = '.Draw_Sharp_icon'
    CLAY = '.Clay_icon'
    CLAY_STRIPS = '.Clay_Strips_icon'
    CLAY_THUMB = '.Clay_Thumb_icon'
    LAYER = '.Layer_icon'
    INFLATE = '.Inflate_icon'
    BLOB = '.Blob_icon'
    CREASE = '.Crease_icon'
    SMOOTH = '.Smooth_icon'
    FLATTEN = '.Flatten_icon'
    FILL = '.Fill_icon'
    SCRAPE = '.Scrape_icon'
    MULTIPLANE_SCRAPE = '.Scrape_MultiPlane_icon'
    PINCH = '.Pinch_icon'
    GRAB = '.Grab_icon'
    ELASTIC_DEFORM = '.ElasticDeform_icon'
    SNAKE_HOOK = '.SnakeHook_icon'
    THUMB = '.Thumb_icon'
    POSE = '.Pose_icon'
    NUDGE = '.Nudge_icon'
    ROTATE = '.Rotate_icon'
    #TOPOLOGY = '.Topology_icon'
    #BOUNDARY = '.Boundary_icon'
    CLOTH = '.Cloth_icon'
    SIMPLIFY = '.Simplify_icon'
    MASK = '.Mask_icon'
    PAINT = '.Paint_icon'
    SMEAR = '.Paint_Smear_icon'
    DRAW_FACE_SETS = '.Draw_FaceSets_icon'

    # 2.91
    BOUNDARY = '.Boundary_icon'
    DISPLACEMENT_ERASER = '.Displacement_Eraser_icon'

    # def __call__(self):
    #     return load_image(self.value, '.png', 'brushes')

    @property
    def icon_path(self) -> str:
        return Paths.Images.BRUSHES(self.value + '.png')

    @property
    def icon_id(self) -> int:
        return get_preview(self.name, self.icon_path, collection='builtin')

    @property
    def gputex(self) -> GPUTexture:
        return get_gputex(self.name, self.icon_path)

    # def __call__(self) -> int:
    #     return self.icon_id

    def draw(self, layout, text: str = ''):
        layout.label(text=text, icon_value=self.icon_id)


def get_default_brush_icon_by_type(brush_tool_type: str) -> DefaultBrushIcon:
    return getattr(DefaultBrushIcon, brush_tool_type, DefaultBrushIcon.DEFAULT)
