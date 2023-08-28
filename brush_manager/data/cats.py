from collections import OrderedDict
from typing import Iterator

from .common import IconHolder, IconPath
from .items import Item, BrushItem, TextureItem, BrushItem_Collection, TextureItem_Collection, Item_Collection
from ..utils.callback import CallbackSetCollection

# ----------------------------------------------------------------
# Category Types.


callback__CatsAdd = CallbackSetCollection.init('Category_Collection', 'cats.add')
callback__CatsRemove = CallbackSetCollection.init('Category_Collection', 'cats.remove')


class Category(IconHolder):
    # Internal props.
    owner: object # 'AddonDataByMode'
    items: Item_Collection # OrderedDict[str, Item]

    flags: set

    # User properties.
    fav: bool

    @property
    def collection(self) -> 'Cat_Collection':
        return self.owner

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.flags = set()

    def __del__(self) -> None:
        del self.items
        self.owner = None


    def set_active(self):
        self.collection.select(self)


    def save_default(self, compress: bool = True) -> None:
        for item in self.items:
            item.save_default(compress=compress)

    def reset(self) -> None:
        for item in self.items:
            item.reset()

    # ------------------------

    def clear_owners(self) -> None:
        self.owner = None
        self.items.clear_owners()

    def ensure_owners(self, cat_collection: 'Cat_Collection') -> None:
        self.owner = cat_collection
        self.items.ensure_owners(self)


class BrushCat(Category):
    icon_path: IconPath = IconPath.CAT_BRUSH
    items: BrushItem_Collection # OrderedDict[str, BrushItem]

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.items = BrushItem_Collection(self)


class TextureCat(Category):
    icon_path: IconPath = IconPath.CAT_TEXTURE
    items: TextureItem_Collection # OrderedDict[str, TextureItem]

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.items = TextureItem_Collection(self)

# ----------------------------------------------------------------
# Category Collection.


class Cat_Collection:
    active: Category
    cats: OrderedDict[str, Category]
    owner: object

    @property
    def count(self) -> int:
        return len(self.cats)

    # - Fav ___________________________
    @property
    def favs(self):
        return [cat for cat in self.cats.values() if cat.fav]

    # - Active ___________________________
    @property
    def active(self) -> Category:
        return self.get(self._active)

    @property
    def active_id(self) -> str:
        return self._active

    @active.setter
    def active(self, cat: str | Category) -> None:
        if cat is None:
            self._active = ''
            return
        if not isinstance(cat, (str, Category)):
            raise TypeError("Expected a Category instance or a string (uuid)")
        self._active = cat if isinstance(cat, str) else cat.uuid

    # - Collection class methods ___________________________
    def __init__(self, addon_data_by_mode) -> None:
        self.cats = OrderedDict()
        self._active = ''
        self._selected_items: list[str] = []
        self.owner = addon_data_by_mode

    def __iter__(self) -> Iterator[Category]:
        return iter(self.cats.values())

    def __getitem__(self, uuid_or_index: str | int) -> Category | None:
        if isinstance(uuid_or_index, str):
            return self.cats.get(uuid_or_index, None)
        elif isinstance(uuid_or_index, int):
            index: int = uuid_or_index
            if index < 0 or index >= len(self.cats):
                return None
            return list(self.cats.values())[index]
        raise TypeError("Expected int (index) or string (uuid)")

    def get(self, uuid: str) -> Category | None:
        ''' Wrapper for __getitem__ method. '''
        return self[uuid]

    def select(self, cat: str) -> None:
        if isinstance(cat, Category):
            return self.select(cat.uuid)
        if isinstance(cat, int):
            index: int = cat
            return self.select(list(self.cats.keys())[index])
        if isinstance(cat, str) and cat in self.cats:
            self._active = cat

    def add(self, name: str, _type = Category, custom_uuid: str | None = None) -> Category:
        cat = _type(name)
        if custom_uuid is not None and isinstance(custom_uuid, str) and custom_uuid != '':
            cat.uuid = custom_uuid
        self.cats[cat.uuid] = cat
        cat.owner = self
        cat.set_active()
        callback__CatsAdd(cat)
        return cat

    def remove(self, uuid_or_index: int | str | Category) -> None:
        if isinstance(uuid_or_index, str):
            if uuid_or_index in self.cats:
                callback__CatsRemove(self.cats[uuid_or_index])
                del self.cats[uuid_or_index]
            return
        if isinstance(uuid_or_index, Category):
            return self.remove(uuid_or_index.uuid)
        if isinstance(uuid_or_index, int):
            index: int = uuid_or_index
            return self.remove(list(self.cats.keys())[index])
        raise TypeError("Expected int (index) or string (uuid)")

    def clear(self) -> None:
        self.cats.clear()
        self.active = None

    def __del__(self) -> None:
        for cat in reversed(self.cats):
            del cat
        self.clear()
        self.owner = None


    # ---------------------------

    def clear_owners(self) -> None:
        self.owner = None
        for cat in self.cats.values():
            cat.clear_owners()

    def ensure_owners(self, addon_data_by_mode) -> None:
        self.owner = addon_data_by_mode
        for cat in self.cats.values():
            cat.ensure_owners(self)


class BrushCat_Collection(Cat_Collection):
    active: BrushCat
    cats: OrderedDict[str, BrushCat]

    def get(self, uuid_or_index: str | int) -> BrushCat | None: return super().get(uuid_or_index)
    def add(self, name: str, custom_uuid: str | None = None) -> BrushCat: return super().add(name, BrushCat, custom_uuid=custom_uuid)


class TextureCat_Collection(Cat_Collection):
    active: TextureCat
    cats: OrderedDict[str, TextureCat]

    def get(self, uuid_or_index: str | int) -> TextureCat | None: return super().get(uuid_or_index)
    def add(self, name: str, custom_uuid: str | None = None) -> TextureCat: return super().add(name, TextureCat, custom_uuid=custom_uuid)




def register():
    global callback__AddonDataSave
    callback__AddonDataSave = CallbackSetCollection.init('AddonDataByMode', 'save')


def unregister():
    global callback__AddonDataSave
    del callback__AddonDataSave
