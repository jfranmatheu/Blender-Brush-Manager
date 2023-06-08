# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Brush Manager",
    "author" : "J. Fran Matheu (@jfranmatheu)",
    "description" : "",
    "blender" : (3, 5, 1),
    "version" : (0, 1, 0),
    "location" : "Addon Preferences",
    "category" : "General"
}

if __package__ != 'brush_manager':
    import sys
    print("[BrushManager] Please, rename the addon folder as 'brush_manager'")
    sys.exit(0)

from . import auto_load

auto_load.init()

def register():
    auto_load.register()

def unregister():
    auto_load.unregister()
