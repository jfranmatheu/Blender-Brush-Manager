import bpy
from bpy.types import ID, Brush as BlBrush, Texture as BlTexture, ImageTexture as BlImageTexture, Context

from collections import OrderedDict
from shutil import copyfile
from typing import Iterator

from brush_manager.paths import Paths
from .common import IconHolder, IconPath
from brush_manager.utils.tool_settings import get_ts, get_ts_brush, get_ts_brush_texture_slot, set_ts_brush
from ..utils.callback import CallbackSetCollection


callback__ItemsAdd = CallbackSetCollection.init('Item_Collection', 'items.add')
callback__ItemsRemove = CallbackSetCollection.init('Item_Collection', 'items.remove')
callback__ItemsMovePre = CallbackSetCollection.init('Item_Collection', 'items.move(pre)')
callback__ItemsMovePost = CallbackSetCollection.init('Item_Collection', 'items.move(post)')


class Item(IconHolder):
    # Internal props.
    lib_path: Paths.Data
    owner: object # 'Category'

    # Toggles.
    fav: bool
    select: bool
    flags: set
    
    # Item data.
    type: str


    @property
    def id_data(self) -> ID:
        return None

    @property
    def collection(self) -> 'BrushItem_Collection':
        return self.owner

    @property
    def cat(self):
        ''' Wrapper prop for Item.owner (Category). '''
        from .cats import Category
        cat : Category = self.collection.owner
        return cat

    @property
    def cat_id(self) -> str:
        return self.cat.uuid

    def __init__(self, collection: 'Item_Collection', name: str, **kwargs) -> None:
        super().__init__(name)
        self.owner = collection

        self.fav = False
        self.select = False
        self.flags = set()

        # Custom Data.
        for key, value in kwargs.items():
            setattr(self, key, value)

    def set_active(self, context: Context) -> None:
        pass

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
            self.collection.remove(self) # Category.remove_item()

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
    icon_path = IconPath.BRUSH

    @property
    def id_data(self) -> BlBrush:
        return bpy.data.brushes.get(self.uuid, None)

    def set_active(self, context: Context) -> None:
        bl_brush = self.id_data
        if bl_brush is None:
            bl_brush = self.load(link=False, from_default=False)

        set_ts_brush(context, bl_brush)


    def load(self, link: bool = False, from_default: bool = False) -> BlBrush:
        # Remove datablock if it exists.
        bl_brush = self.id_data
        if bl_brush is not None:
            bpy.data.brushes.remove(bl_brush)
            del bl_brush

        # Load datablock from library.
        filename = self.uuid + '.default.blend' if from_default else self.uuid + '.blend'
        filepath = self.lib_path(filename, as_path=True)
        if not filepath.exists():
            print("WARN! Could not find Brush .blend lib-file at", str(filepath))
            return None

        with bpy.data.libraries.load(str(filepath), link=link) as (data_from, data_to):
            data_to.brushes = data_from.brushes

        bl_brush = self.id_data
        if bl_brush is not None:
            bl_brush['name'] = self.name
        return bl_brush

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
            path_remap=False,
            fake_user=False,
            compress=compress
        )

    def save_default(self) -> None:
        self.save(compress=True, save_default=True)

    def reset(self) -> None:
        # This will remove current datablock and load the default from library.
        self.load(from_default=True)

        # Still we need to replace the active library .blend file with the default.
        copyfile(
            self.lib_path(self.uuid + '.default.blend', as_path=False),
            self.lib_path(self.uuid + '.blend', as_path=False)
        )

    def __del__(self) -> None:
        super().__del__()

        # Removes the - default - library .blend file (only for brushes).
        data_path = self.lib_path(self.uuid + '.default.blend', as_path=True)
        if data_path.exists() and data_path.is_file():
            data_path.unlink()


class TextureItem(Item):
    # Internal props.
    lib_path = Paths.Data.TEXTURE
    icon_path = IconPath.TEXTURE
    format: str

    @property
    def id_data(self) -> BlTexture:
        return bpy.data.textures.get(self.uuid, None)

    def set_active(self, context: Context) -> None:
        bl_texture = self.id_data
        if bl_texture is None:
            bl_texture = self.load(link=True)

        get_ts_brush(context).texture_slot.texture = bl_texture

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

        bl_texture = self.id_data
        if bl_texture is not None:
            bl_texture['name'] = self.name
        return bl_texture

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





# ----------------------------------------------------------------
# Category Collection.


class Item_Collection:
    active: Item
    items: OrderedDict[str, Item]
    owner: object # AddonDataByMode

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def favs(self) -> list[Item]:
        return [item for item in self if item.fav]

    @property
    def selected(self) -> list[Item]:
        return [item for item in self if item.select]

    @property
    def active(self) -> Item:
        return self.get(self._active)

    @property
    def active_id(self) -> str:
        return self._active

    @active.setter
    def active(self, item: str | Item) -> None:
        if item is None:
            self._active = ''
            return
        if not isinstance(item, (str, Item)):
            raise TypeError("Expected an Item instance or a string (uuid) but got:", type(item))
        self._active = item if isinstance(item, str) else item.uuid

    def __init__(self, cat: object) -> None:
        self.items = OrderedDict()
        self._active = ''
        self.owner = cat

    def __iter__(self) -> Iterator[Item]:
        return iter(self.items.values())

    def __getitem__(self, uuid_or_index: str | int) -> Item | None:
        if isinstance(uuid_or_index, str):
            return self.items.get(uuid_or_index, None)
        elif isinstance(uuid_or_index, int):
            index: int = uuid_or_index
            if index < 0 or index >= len(self.items):
                return None
            return list(self.items.values())[index]
        raise TypeError("Expected int (index) or string (uuid)")

    def get(self, uuid: str) -> Item | None:
        # Wrapper for __getitem__ method.
        return self[uuid]

    def select(self, item: str) -> None:
        if isinstance(item, Item):
            return self.select(item.uuid)
        if isinstance(item, int):
            index: int = item
            return self.select(list(self.items.keys())[index])
        if isinstance(item, str) and item in self.items:
            self._active = item

    def add(self, name: str, _type = Item, **kwargs) -> Item:
        # Construct a new Item.
        item = _type(self, name)
        for key, value in kwargs.items():
            setattr(item, key, value)
        # Link the item to this category.
        self.items[item.uuid] = item
        callback__ItemsAdd(item)
        return item

    def move(self, item_uuid: str, other_coll: 'Item_Collection') -> None:
        if not isinstance(other_coll, Item_Collection):
            raise TypeError("Trying to move an item to another collection but the given type is not Item_Collection! but", type(other_coll))
        callback__ItemsMovePre(self.items.get(item_uuid))
        item = self.remove(item_uuid, perma_remove=False)
        other_coll.items[item.uuid] = item
        item.owner = other_coll
        callback__ItemsMovePost(item)

    def remove(self, uuid_or_index: int, perma_remove: bool = True) -> None | Item:
        if isinstance(uuid_or_index, str):
            if uuid_or_index in self.items:
                callback__ItemsRemove(self.items[uuid_or_index])
                if perma_remove:
                    del self.items[uuid_or_index]
                else:
                    return self.items.pop(uuid_or_index)
            return
        if isinstance(uuid_or_index, Item):
            return self.remove(uuid_or_index.uuid)
        if isinstance(uuid_or_index, int):
            index: int = uuid_or_index
            return self.remove(list(self.items.keys())[index])
        raise TypeError("Expected int (index) or string (uuid)")

    def clear(self) -> None:
        self.items.clear()
        self.active = None

    def __del__(self) -> None:
        for item in reversed(self.items):
            del item
        self.owner = None
        self.clear()

    # ---------------------------

    def clear_owners(self) -> None:
        self.owner = None
        for item in self:
            item.owner = None

    def ensure_owners(self, cat: object) -> None:
        self.owner = cat
        for item in self:
            item.owner = self


class BrushItem_Collection(Item_Collection):
    active: BrushItem
    items: OrderedDict[str, BrushItem]

    def get(self, uuid: str) -> BrushItem | None: return super().get(uuid)
    def add(self, name: str = 'New Brush', **data) -> BrushItem: return super().add(name, BrushItem, **data)


class TextureItem_Collection(Item_Collection):
    active: TextureItem
    items: OrderedDict[str, TextureItem]

    def get(self, uuid: str) -> TextureItem | None: return super().get(uuid)
    def add(self, name: str = 'New Texture', **data) -> TextureItem: return super().add(name, TextureItem, **data)
