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

from . import OSC
from .OSC import OSCClient, OSCMessage, OSCServer

class OLAOSCServer(OSCServer):
	def __init__(self, ip="127.0.0.1", port=20001):
		super().__init__((ip,port))
		self.timeout = 0

	def handle_timeout(self):
		self.timed_out = True

	def update(self):
		self.timed_out = False
		while not self.timed_out:
			self.handle_request()

# --- global server instead of Singleton
server = None

def ServerInstance():
	global server
	return server

def InitServer(ip, port):
	global server
	server = OLAOSCServer(ip, port)
	return server
