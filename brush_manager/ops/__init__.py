from .op_library_actions import (
    ImportLibrary,
    ImportBuiltinLibraries,
    SelectLibraryAtIndex,
    RemoveActiveLibrary,
)

from .op_category_actions import (
    AsignIconToCategory,
    NewCategory,
    RemoveCategory,
    SelectCategoryAtIndex,
)

from .op_content_actions import (
    AppendSelectedFromLibraryToCategory,
    SelectAll,
    MoveSelectedToCategory,
    RemoveSelectedFromActiveCategory,
    DuplicateSelected,
    AsignIconToBrush,
)



AppendSelectedToCategory = AppendSelectedFromLibraryToCategory
RemoveSelectedFromCategory = RemoveSelectedFromActiveCategory
