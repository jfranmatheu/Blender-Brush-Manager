from bpy.types import Panel, Header, UILayout, Context

from ...types import UIProps, AddonData, AddonDataByMode



class BaseUI:
    def draw(self, context):
        layout = self.layout
        ui_props = UIProps.get_data(context)
        addon_data = AddonData.get_data_by_context(ui_props)

        self.draw_ui(context, layout, addon_data, ui_props)
        
    def draw_ui(self, context: Context, layout: UILayout, addon_data: AddonDataByMode, ui_props: UIProps):
        pass
