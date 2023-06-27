import bpy
from bpy.types import UILayout, Context


class BRUSHMANAGER_UL_sidebar_list(bpy.types.UIList):
    use_order_name: bpy.props.BoolProperty(
        name="Name", default=False, options=set(),
        description="Sort groups by their name (case-insensitive)",
    )

    use_filter_name_reverse: bpy.props.BoolProperty(
        name="Reverse Name",
        default=False,
        options=set(),
        description="Reverse name filtering",
    )

    # Usual draw item function.
    def draw_item(self, context: Context, layout: UILayout, data, item, icon, active_data, active_propname, index, flt_flag):
        active_index = getattr(active_data, active_propname)

        row = layout.row(align=True)

        left = row.row(align=True)
        left.alignment = 'LEFT'
        left.label(text="", icon='KEYTYPE_KEYFRAME_VEC' if index == active_index else 'BLANK1')
        left.prop(item, "name", text="", emboss=False, icon_value=item.icon_id if hasattr(item, "icon_id") else 0)

        right = row.row(align=True)
        right.alignment = 'RIGHT'

        if hasattr(item, 'load_on_boot'):
            right.prop(item, 'load_on_boot', icon='QUIT', emboss=item.load_on_boot, text='')


    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        icon = 'ZOOM_OUT' if self.use_filter_name_reverse else 'ZOOM_IN'
        subrow.prop(self, "use_filter_name_reverse", text="", icon=icon)

        row = layout.row(align=True)
        row.label(text="Order by:")
        row.prop(self, "use_order_name", toggle=True)


    def filter_items(self, context, data, propname):
        # This function gets the collection property (as the usual tuple (data, propname)), and must return two lists:
        # * The first one is for filtering, it must contain 32bit integers were self.bitflag_filter_item marks the
        #   matching item as filtered (i.e. to be shown), and 31 other bits are free for custom needs. Here we use the
        #   first one to mark VGROUP_EMPTY.
        # * The second one is for reordering, it must return a list containing the new indices of the items (which
        #   gives us a mapping org_idx -> new_idx).
        # Please note that the default UI_UL_list defines helper functions for common tasks (see its doc for more info).
        # If you do not make filtering and/or ordering, return empty list(s) (this will be more efficient than
        # returning full lists doing nothing!).
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Filtering by name
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "name",
                                                          reverse=self.use_filter_name_reverse)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(items)

        # Reorder by name or average weight.
        if self.use_order_name:
            flt_neworder = helper_funcs.sort_items_by_name(items, "name")

        return flt_flags, flt_neworder
