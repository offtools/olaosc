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

import bpy
from .network import ServerInstance
from .utils.utils import unique_name

# --- dmx to blender value conversion
def to_bool(value):
	if isinstance(value, bool):
		return bool(value >> 7)
	else:
		raise TypeError

def to_float(value):
	if isinstance(value, float):
		return float(value/255)
	else:
		raise TypeError

def to_int(value):
	if isinstance(value, int):
		if value >> 8:
			return value
		else:
			if value < 0:
				return 0
			elif value > 255:
				return 255
	else:
		raise TypeError

def convert(attr, value):
	if isinstance(attr, bpy.types.FloatProperty):
		return to_float(value)
	elif isinstance(attr, bpy.types.IntProperty):
		return to_int(value)
	elif isinstance(attr, bpy.types.BoolProperty):
		return to_bool(value)
	else:
		raise TypeError("convert: unsupported type works only with float, int, bool")

def write_dmx(target, action, value):
	if action.use_data:
		target = target.data
	if hasattr(action, "attr_idx"):
		prop = getattr(target, action.attr)
		prop[int(action.attr_idx)] = convert(prop[int(action.attr_idx)], value)
	else:
		value = convert(getattr(target, action.attr))
		setattr(target, action.attr, value)

def callback_rcv_dmx(path, tags, args, source):
	data = args[0]
	olaosc = bpy.context.scene.olaosc
	universe = olaosc.universes[olaosc.active_universe]
	patch = universe.patch

	for key in patch.keys():
		value = data[int(key)-1]

		if patch[key].value != value:
			id_action = patch[key].action
			action = universe.actions[id_action]
			# --- Objects
			if action.context == "ctx_object":
				write_dmx(bpy.context.scene.objects[action.target], action, value)
			if action.context == "ctx_material":
				write_dmx(bpy.data.materials[action.target], action, value)
			if action.context == "ctx_texture":
				bpy.data.textures[action.target]
				write_dmx(bpy.data.textures[action.target], action, value)
			# --- Operator
			if action.context == "ctx_operator":
				op = eval("bpy.ops.%s"%action.target)
				if not hasattr(action, "attr_idx"):
					op()
				else:
					rna = op.get_rna()
					if action.attr in rna.properties.keys():
						#~ print("bpy.ops.%s(%s=%s)"%(action.target,action.attr,value))
						eval("bpy.ops.%s(%s=%s)"%(action.target,action.attr,value))

			# --- write dmx value to patch
			patch[key].value = value

class OLAOSC_OT_olaosc_connect(bpy.types.Operator):
	"""
		OLAOSC Operator - connect
	"""
	bl_idname = "blive.olaosc_connect"
	bl_label = "OLAOSC - connect olaosc"

	def execute(self, context):
		port = context.window_manager.olaosc_settings.port
		ip = context.window_manager.olaosc_settings.ip
		try:
			server = ServerInstance()(ip, port)
			print(server)
		except OSError as err:
			print("OLA OSC: ", err)
		return{'FINISHED'}

class OLAOSC_OT_olaosc_disconnect(bpy.types.Operator):
	"""
		OLAOSC Operator - disconnect
	"""
	bl_idname = "blive.olaosc_disconnect"
	bl_label = "OLAOSC - disconnect olaosc "

	def execute(self, context):
		if ServerInstance().running:
			ServerInstance().close()
		return{'FINISHED'}

class OLAOSC_OT_olaosc_set_attr_arrayidx(bpy.types.Operator):
	"""
		Operator - set array idx enum
	"""
	bl_idname = "blive.olaosc_set_attr_arrayidx"
	bl_label = "OLAOSC - set attr arrayidx"
	length = bpy.props.IntProperty()

	def execute(self, context):
		if self.length:
			gen = [ (str(i),str(i),'') for i in range(self.length) ]
			bpy.types.OLAOSCAction.attr_idx = bpy.props.EnumProperty(name="attr_idx", items=gen)
		return{'FINISHED'}

class OLAOSC_OT_olaosc_add_universe(bpy.types.Operator):
	"""
		Operator - add dmx universe
	"""
	bl_idname = "blive.olaosc_add_universe"
	bl_label = "OLAOSC - add dmx universe "

	def execute(self, context):
		global server
		olaosc = context.scene.olaosc
		u = olaosc.universes.add()
		u.name = unique_name(olaosc.universes, "Universe")
		u.oscpath = "/dmx/universe/%d"%len(olaosc.universes)
		olaosc.active_by_name = u.name

		return{'FINISHED'}

class OLAOSC_OT_olaosc_del_universe(bpy.types.Operator):
	"""
		Operator - delete dmx universe  
	"""
	bl_idname = "blive.olaosc_del_universe"
	bl_label = "OLAOSC - remove dmx universe "

# TODO: del msghandler
	def execute(self, context):
		olaosc = context.scene.olaosc
		active = olaosc.active_universe
		olaosc.universes.remove(active)
		return{'FINISHED'}

class OLAOSC_OT_olaosc_add_msghandler(bpy.types.Operator):
	"""
		Operator - add osc message handler
	"""
	bl_idname = "blive.olaosc_add_msghandler"
	bl_label = "OLAOSC - add osc message handler"
	oscpath = bpy.props.StringProperty()

	def execute(self, context):
		if ServerInstance() and not self.oscpath in ServerInstance().callbacks:
			ServerInstance().addMsgHandler(self.oscpath, callback_rcv_dmx)
			return{'FINISHED'}
		else:
			return{'CANCELLED'}

class OLAOSC_OT_olaosc_del_msghandler(bpy.types.Operator):
	"""
		Operator - del osc message handler
	"""
	bl_idname = "blive.olaosc_del_msghandler"
	bl_label = "OLAOSC - del osc message handler"
	oscpath = bpy.props.StringProperty()

	def execute(self, context):
		if ServerInstance() and self.oscpath in ServerInstance().callbacks:
			ServerInstance().delMsgHandler(self.oscpath)
			return{'FINISHED'}
		else:
			return{'CANCELLED'}

class OLAOSC_OT_olaosc_add_action(bpy.types.Operator):
	"""
		Operator - olaosc create new action
	"""
	bl_idname = "blive.olaosc_add_action"
	bl_label = "OLAOSC - olaosc add action"

# TODO: add msghandler
	def execute(self, context):
		olaosc = context.scene.olaosc
		universe = olaosc.universes[olaosc.active_universe]
		actions = universe.actions

		action = actions.add()
		action.name = unique_name(actions, "Action")
		return{'FINISHED'}

class OLAOSC_OT_olaosc_del_action(bpy.types.Operator):
	"""
		Operator - olaosc delete action
	"""
	bl_idname = "blive.olaosc_del_action"
	bl_label = "OLAOSC - olaosc delete action"

	def execute(self, context):
		olaosc = context.scene.olaosc
		universe = olaosc.universes[olaosc.active_universe]
		actions = universe.actions

		if len(actions):
			actions.remove(universe.active_action)
			return{'FINISHED'}
		else:
			return{'CANCELLED'}

class OLAOSC_OT_olaosc_patch(bpy.types.Operator):
	"""
		Operator - olaosc patch channel
	"""
	bl_idname = "blive.olaosc_patch"
	bl_label = "OLAOSC - olaosc patch channel"

	def execute(self, context):
		olaosc = context.scene.olaosc
		universe = olaosc.universes[olaosc.active_universe]
		action = universe.actions[universe.active_action]
		req_chan = action.channel
		num_chan = action.num_channels

		# --- check if channels already set
		for i in range(num_chan):
			chan = req_chan + i
			if "%s"%chan in universe.patch:
				action.is_patched = False
				return{'CANCELLED'}

		for i in range(num_chan):
			chan = universe.patch.add()
			chan.name = "%s"%(req_chan + i)
			chan.action = action.name
			action.is_patched = True
		return{'FINISHED'}

class OLAOSC_OT_olaosc_unpatch(bpy.types.Operator):
	"""
		Operator - olaosc unpatch channel
	"""
	bl_idname = "blive.olaosc_unpatch"
	bl_label = "OLAOSC - olaosc unpatch channel"

	def execute(self, context):
		olaosc = context.scene.olaosc
		universe = olaosc.universes[olaosc.active_universe]
		action = universe.actions[universe.active_action]
		req_chan = action.channel
		num_chan = action.num_channels

		for i in range(num_chan):
			chan = req_chan + 1
			if "%s"%chan in universe.patch:
				universe.patch.remove(universe.patch.keys().index("%s"%chan))
				action.is_patched = False
				return{'CANCELLED'}

def register():
	print("olaosc.ops.register")
	bpy.utils.register_class(OLAOSC_OT_olaosc_enable)
	bpy.utils.register_class(OLAOSC_OT_olaosc_disable)
	bpy.utils.register_class(OLAOSC_OT_olaosc_set_attr_arrayidx)
	bpy.utils.register_class(OLAOSC_OT_olaosc_add_msghandler)
	bpy.utils.register_class(OLAOSC_OT_olaosc_del_msghandler)
	bpy.utils.register_class(OLAOSC_OT_olaosc_add_universe)
	bpy.utils.register_class(OLAOSC_OT_olaosc_del_universe)
	bpy.utils.register_class(OLAOSC_OT_olaosc_add_action)
	bpy.utils.register_class(OLAOSC_OT_olaosc_del_action)
	bpy.utils.register_class(OLAOSC_OT_olaosc_patch)
	bpy.utils.register_class(OLAOSC_OT_olaosc_unpatch)

def unregister():
	print("olaosc.ops.unregister")
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_connect)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_disconnect)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_set_attr_arrayidx)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_add_universe)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_del_universe)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_add_msghandler)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_del_msghandler)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_add_action)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_del_action)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_patch)
	bpy.utils.unregister_class(OLAOSC_OT_olaosc_unpatch)

