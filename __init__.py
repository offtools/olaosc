# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


# Script copyright (C) 2012 Thomas Achtner (offtools)

bl_info = {
	"name": "olaosc",
	"author": "offtools",
	"version": (0, 0, 1),
	"blender": (2, 6, 4),
	"location": "Render Panel",
	"description": "Receive dmx data as Osc Message blob from OLA",
	"warning": "Linux only",
	"wiki_url": "",
	"tracker_url": "",
	"category": "misc"}
	
# import modules
if "bpy" in locals():
	import imp
	imp.reload(network)
	imp.reload(props)
	imp.reload(ops)
	imp.reload(handler)
	imp.reload(ui)
else:
	from . import network
	from . import props
	from . import ops
	from . import handler
	from . import ui

import bpy

def register():
	props.register()
	ops.register()
	handler.register()
	ui.register()

def unregister():
	ui.unregister()
	handler.unregister()
	ops.unregister()
	props.unregister()

if __name__ == "__main__":
	pass
