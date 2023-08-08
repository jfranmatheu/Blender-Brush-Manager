import bpy
from bpy.types import ID, Brush as BlBrush, Texture as BlTexture, ImageTexture as BlImageTexture

from shutil import copyfile

from brush_manager.paths import Paths
from .common import IconHolder



class Item(IconHolder):
    # Internal props.
    lib_path: Paths.Data
    owner: object # 'Category'
    type: str

    @property
    def id_data(self) -> ID:
        return

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(name)

        # Custom Data.
        for key, value in kwargs.items():
            setattr(self, key, value)

    def load(self, link: bool = False) -> None:
        raise NotImplementedError

    def save(self, compress: bool = True) -> None:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    def remove(self) -> None:
        ''' You can remove directly from the item,
            this will call the remove method from the parent. '''
        if self.owner is not None:
            self.owner.remove_item(self) # Category.remove_item()

    def __del__(self) -> None:
        self.owner = None
        
        # Removes the icon from memory (preview and cached GPUTexture).
        self.clear_icon()

        # Removes the library .blend file.
        data_path = self.lib_path(self.uuid + '.blend', as_path=True)
        if data_path.exists() and data_path.is_file():
            data_path.unlink()


class BrushItem(Item):
    # Internal props.
    lib_path = Paths.Data.BRUSH
    icon_path = Paths.Icons.BRUSH

    @property
    def id_data(self) -> BlBrush:
        return bpy.data.brushes.get(self.uuid, None)

    def load(self, link: bool = False, from_default: bool = False) -> None:
        # Remove datablock if it exists.
        bl_brush = self.id_data
        if bl_brush is not None:
            bpy.data.brushes.remove(bl_brush)
            del bl_brush

        # Load datablock from library.
        filename = self.uuid + '.default.blend' if from_default else self.uuid + '.blend'
        filepath = self.lib_path(filename, as_path=False)
        with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
            data_to.brushes = data_from.brushes

    def save(self, compress: bool = True, save_default: bool = False) -> None:
        # Get datablock from blend data.
        bl_brush = self.id_data
        if bl_brush is None:
            raise RuntimeError(f"Can't save! No BlBrush was found with the uuid '{self.uuid}', in the blend data")

        # Write Library with the datablock.
        filename = self.uuid + '.default.blend' if save_default else self.uuid + '.blend'
        filepath = self.lib_path(filename, as_path=False)
        bpy.data.libraries.write(
            filepath,
            {bl_brush},
            fake_user=False,
            compress=compress
        )

    def reset(self) -> None:
        # This will remove current datablock and load the default from library.
        self.load(from_default=True)

        # Still we need to replace the active library .blend file with the default.
        copyfile(
            filepath = self.lib_path(self.uuid + '.default.blend', as_path=False),
            filepath = self.lib_path(self.uuid + '.blend', as_path=False)
        )

    def __del__(self) -> None:
        super(Item, self).__del__()

        # Removes the - default - library .blend file (only for brushes).
        data_path = self.lib_path(self.uuid + '.default.blend', as_path=True)
        if data_path.exists() and data_path.is_file():
            data_path.unlink()


class TextureItem(Item):
    # Internal props.
    lib_path = Paths.Data.TEXTURE
    icon_path = Paths.Icons.TEXTURE
    format: str

    @property
    def id_data(self) -> BlTexture:
        return bpy.data.textures.get(self.uuid, None)

    def load(self, link: bool = False) -> None:
        # Remove datablock if it exists.
        bl_texture = self.id_data
        if bl_texture is not None:
            if isinstance(bl_texture, BlImageTexture) and bl_texture.image is not None:
                bpy.data.images.remove(bl_texture.image)
            bpy.data.textures.remove(bl_texture)
            del bl_texture

        # Load datablock from library.
        filename = self.uuid + '.blend'
        filepath = self.lib_path(filename, as_path=False)
        with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
            data_to.textures = data_from.textures
            data_to.images = data_from.images

    def save(self, compress: bool = True) -> None:
        # Get datablock from blend data.
        bl_texture = self.id_data
        if bl_texture is None:
            raise RuntimeError(f"Can't save! No BlTexture was found with the uuid '{self.uuid}', in the blend data")

        # Write Library with the datablock.
        filename = self.uuid + '.blend'
        filepath = self.lib_path(filename, as_path=False)
        bpy.data.libraries.write(
            filepath,
            {bl_texture},
            fake_user=False,
            compress=compress
        )
