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

# --- Properties to receive dmx data via OSC (OLA OSC plugin)
# --- remarks:
# --- it should support multiple universes
# --- every scene has its own patch

import bpy

PatchEditMode = (('channels','Channels','List Actions'),
				('actions','Actions','List Channels')
				)

ActionContext = (('ctx_object','Object','Object'),
					('ctx_material','Material','Material'),
					('ctx_texture', 'Texture', 'Texture'),
					('ctx_operator','Operator','Operator')
				)


class OLAOSCChannel(bpy.types.PropertyGroup):
	"""
		OLAOSC - Channel: represents a DMX Channel, stores the value
		and the patched action
	"""
	action = bpy.props.StringProperty()
	value = bpy.props.IntProperty(default=0)

#
# --- OLAOSCAction: callbacks 
#
def callback_context(self, context):
	self.target = ""

def callback_target(self, context):
	self.attr = ""
	self.min = self.max = 0

def callback_attr(self, context):
	if not len(self.target) or not len(self.attr):
		return
	if self.context == 'ctx_object':
		target = context.scene.objects[self.target]
	elif self.context == 'ctx_material':
		target = bpy.data.materials[self.target]
	elif self.context == 'ctx_texture':
		target = bpy.data.textures[self.target]
	elif self.context == 'ctx_operator':
		if not len(self.attr):
			return
		op = eval("bpy.ops.%s"%self.target)
		target = op.get_rna()
	try:
		if not self.use_data:
			length = target.bl_rna.properties[self.attr].array_length
			bpy.ops.olaosc.set_attr_arrayidx(length = length)
		else:
			length = target.data.bl_rna.properties[self.attr].array_length
			bpy.ops.olaosc.set_attr_arrayidx(length = length)
	except AttributeError:
		pass

def callback_minmax(self, context):
	pass

def callback_channel(self, context):
	# --- TODO: unpatch
	pass

def callback_num_channels(self, context):
	# --- TODO: unpatch

#
# --- OLAOSC Action
#
class OLAOSCAction(bpy.types.PropertyGroup):
	"""
		OLAOSC - defines a action which is called on receiving a certain channel 
	"""
	context = bpy.props.EnumProperty(name="context",items=ActionContext,update=callback_context)
	target = bpy.props.StringProperty(update=callback_target)
	attr = bpy.props.StringProperty(update=callback_attr) 
	min = bpy.props.IntProperty(update=callback_minmax)
	max = bpy.props.IntProperty(update=callback_minmax)
	channel = bpy.props.IntProperty(default=1, min=1, max=255, update=callback_channel)
	num_channels = bpy.props.IntProperty(default=1, update=callback_num_channels)
	use_data = bpy.props.BoolProperty(default=False)
	is_patched = bpy.props.BoolProperty(default=False)

#
# --- OLAOSCUniverse: callbacks 
#
def callback_oscpath(self, context):
	pass

#
# --- OLAOSCUniverse 
#
class OLAOSCUniverse(bpy.types.PropertyGroup):
	"""
		OLAOSC - dmx universes
	"""
	oscpath = bpy.props.StringProperty(update=callback_oscpath)
	actions = bpy.props.CollectionProperty(type=OLAOSCAction)
	patch = bpy.props.CollectionProperty(type=OLAOSCChannel)
	active_action = bpy.props.IntProperty(default=0)
	active_channel = bpy.props.IntProperty(default=0)
	edit_mode = bpy.props.EnumProperty(name="edit_mode", items=PatchEditMode)

#
# --- OLAOSC
#
class OLAOSC(bpy.types.PropertyGroup):
	"""
		OLAOSC - olaosc property wrapper
	"""
	universes = bpy.props.CollectionProperty(type=OLAOSCUniverse)
	active_universe = bpy.props.IntProperty(default=0)

#
# --- OLAOSCSettings
#
class OLAOSCSettings(bpy.types.PropertyGroup):
	"""
		OLAOSC - globael settings
	"""
	ip = bpy.props.StringProperty(default="127.0.0.1")
	port = bpy.props.IntProperty(default=20001)

def register():
	bpy.utils.register_class(OLAOSCAction)
	bpy.utils.register_class(OLAOSCChannel)
	bpy.utils.register_class(OLAOSCUniverse)
	bpy.utils.register_class(OLAOSC)
	bpy.utils.register_class(OLAOSCSettings)

	bpy.types.Scene.olaosc = bpy.props.PointerProperty(type=OLAOSC)
	bpy.types.WindowManager.olaosc_settings = bpy.props.PointerProperty(type=OLAOSCSettings)

def unregister():
	bpy.utils.unregister_class(OLAOSCSettings)
	bpy.utils.unregister_class(OLAOSC)
	bpy.utils.unregister_class(OLAOSCUniverse)
	bpy.utils.unregister_class(OLAOSCChannel)
	bpy.utils.unregister_class(OLAOSCAction)

	del bpy.types.Scene.olaosc
	del bpy.types.WindowManager.olaosc_settings
