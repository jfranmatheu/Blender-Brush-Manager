from typing import Set
from collections import defaultdict


class CallbackSet:
    def __init__(self):
        self.callback_func: Set[callable] = set()

    def __iadd__(self, function: callable) -> None:
        self.add(function)

    def __isub__(self, function: callable) -> bool:
        return self.remove(function)

    def add(self, function: callable) -> None:
        self.callback_func.add(function)

    def remove(self, function: callable) -> bool:
        if function in self.callback_func:
            self.callback_func.remove(function)
            return True
        return False

    def __call__(self, *args, **kwargs) -> None:
        for call in self.callback_func:
            call(*args, **kwargs)


class _CallbackSetCollection:
    def __init__(self) -> None:
        self.callbacks: dict[str, dict[str, CallbackSet]] = defaultdict(dict)

    def get(self, owner_id: str, callback_idname: str) -> CallbackSet | None:
        if owner_callbacks := self.callbacks.get(owner_id, None):
            return owner_callbacks.get(callback_idname, None)

    def init(self, owner_id: str, callback_idname: str) -> CallbackSet:
        self.callbacks[owner_id][callback_idname] = new_callback_set = CallbackSet()
        return new_callback_set

CallbackSetCollection = _CallbackSetCollection()
