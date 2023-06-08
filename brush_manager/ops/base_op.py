

class BaseOp:
    @classmethod
    def draw_in_layout(cls, layout, **draw_props):
        layout.operator(cls.bl_idname, **draw_props)
