from brush_manager.addon_utils import Reg
from brush_manager.paths import Paths

from shutil import rmtree


@Reg.Ops.setup
class ClearData(Reg.Ops.ACTION):
    def action(self, *args) -> None:
        data_path = Paths.DATA
        if data_path.exists() and data_path.is_dir():
            rmtree(data_path)
        
        from brush_manager.data.addon_data import AddonData
        AddonData.clear_instances()
