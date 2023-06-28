from bpy.utils import register_class, unregister_class


states: dict[type, bool] = {}


def toggle_ui(cls_to_replace, my_cls):
    if my_cls not in states:
        states[my_cls] = False
    
    try:
        if states[my_cls]:
            unregister_class(my_cls)
            register_class(cls_to_replace)

        else:
            unregister_class(cls_to_replace)
            register_class(my_cls)
    except (RuntimeError, ValueError) as e:
        pass

    states[my_cls] = not states[my_cls]


def clear_states():
    states.clear()
