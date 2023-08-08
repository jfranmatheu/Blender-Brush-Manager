from collections import OrderedDict

from .common import IconHolder
from .items import Item, BrushItem, TextureItem

# from .addon_data import AddonDataByMode


# ----------------------------------------------------------------
# Category Types.


class Category(IconHolder):
    # Internal props.
    owner: object # 'AddonDataByMode'
    items: dict[str, Item]

    # User properties.
    fav: bool

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def item_ids(self) -> tuple[str]:
        return self.items.keys()

    def get_item(self, item_uuid: str) -> Item | None:
        return self.items.get(item_uuid, None)

    def add_item(self, item: Item) -> None:
        item.owner = self
        self.items[item.uuid] = item

    def remove_item(self, item: Item | str) -> None:
        uuid: str = item if isinstance(item, str) else item.uuid
        del self.items[uuid] # triggers item.__del__()
        # item = self.items.pop(uuid)
        # del item
    
    def __del__(self) -> None:
        for item in reversed(self.items):
            del item
        self.items.clear()
        self.owner = None


class BrushCat(Category):
    items: list[BrushItem]


class TextureCat(Category):
    items: list[TextureItem]


# ----------------------------------------------------------------
# Category Collection.


class Cat_Collection:
    active: Category
    cats: OrderedDict[str, Category]

    @property
    def active(self) -> Category:
        return self.get(self._active)

    @active.setter
    def active(self, cat: str | Category) -> None:
        if not isinstance(cat, (str, Category)):
            raise TypeError("Expected a Category instance or a string (uuid)")
        self._active = cat if isinstance(cat, str) else cat.uuid

    def __init__(self) -> None:
        self.cats = OrderedDict()
        self._active = ''

    def __iter__(self):
        return self.cats.values()

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

    def add(self, name: str, _type = Category) -> Category:
        cat = _type(name)
        self.cats[cat.uuid] = cat
        return cat

    def remove(self, uuid_or_index: int) -> None:
        if isinstance(uuid_or_index, str):
            if uuid_or_index in self.cats:
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


class BrushCat_Collection(Cat_Collection):
    active: BrushCat
    cats: OrderedDict[str, BrushCat]

    def get(self, uuid_or_index: str | int) -> BrushCat | None: return super().get(uuid_or_index)
    def add(self, name: str) -> BrushCat: return super().add(name, BrushCat)


class TextureCat_Collection(Cat_Collection):
    active: TextureCat
    cats: OrderedDict[str, TextureCat]

    def get(self, uuid_or_index: str | int) -> TextureCat | None: return super().get(uuid_or_index)
    def add(self, name: str) -> TextureCat: return super().add(name, TextureCat)
