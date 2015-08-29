bl_info = {
	"name": "Gutters",
	"description": " Add gutters to edge corners",
	"author": "Juha W",
	"version": (1, 0),
	"blender": (2, 75, 0),
	"location": "Tools",
	"warning": "",
	"wiki_url": "https://github.com/gregzaal/Matalogue",
	"tracker_url": "https://github.com/gregzaal/Matalogue/issues",
	"category": "Object"}

import bpy
import bmesh
from math import degrees, pi, sin, cos, atan2
from mathutils import Vector
from bpy.props import FloatProperty, BoolProperty

bpy.types.Scene.offset = FloatProperty(default = 0.0)
bpy.types.Scene.angle = BoolProperty(default = False)

# ------------------------------------------------
def rename(name, angle):

	print ("rename angle:",degrees(angle.angle))
	#print ("rename angle:",angle.angle)
	#degrees(angle.angle))
	name += "|" + chr(248) + str(round(degrees(angle.angle),2))
	return name

def get_angle(v1, v2, v3):
	# v1 = middle vertex coordinates of 3 corner vertices
	# v2 and v3 are outer vertices coordinates
	# return direction vector

	vec1 = (v2 - v1).normalized()
	vec2 = (v3 - v1).normalized()

	vec_result = vec1+vec2

	return  vec_result


# ------------------------------------------------


def corner_vertices(bm):
	# returns verts indices, 1 shared vertex and 2 other

	selected_verts = [v for v in bm.verts if v.select]

	cornerverts = []
	sharp = []

	for v in selected_verts:
		cnt = 0
		edgesharp = 0
		for e in v.link_edges:
			if e.other_vert(v).select and e.select:
				cnt += 1
				if not e.smooth:
					edgesharp += 1
				if cnt == 1:
					v1 = e.other_vert(v)

				else:
					cornerverts.append(v.index)
					cornerverts.append(v1.index)
					cornerverts.append(e.other_vert(v).index)
					if edgesharp == 2:
						sharp.append(True)
					else:
						sharp.append(False)
					break
	return cornerverts, sharp


# ------------------------------------------------


def move_local(o):
	# move object local axis
	# parameters: o, object

	o = bpy.context.object
	# one blender unit in x-direction
	vec = Vector((0.0, -1.0, 0.0))
	inv = o.matrix_world.copy()
	inv.invert()
	# vec aligned to local axis
	vec_rot = vec * inv
	o.location += vec_rot
# ------------------------------------------------


def create_object(o, v1):

	# o = object to duplicate
	# v1 = vertex coordinates to locate new object

	# Create new object associated with the mesh
	me = o.data
	#o1 = me.copy()
	# Copy data block from the old object into the new object
	ob = bpy.data.objects.new(o.name, o.data)
	ob.data = o.data
	ob.location = v1
	ob.scale = o.scale
	# Link new object to the given scene and select it
	bpy.context.scene.objects.link(ob)
	ob.select = True

	return ob
# ------------------------------------------------

class Gutters(bpy.types.Operator):

	bl_idname = 'gutters.doit'
	bl_label = 'Add gutters'

	def execute(self, context):

		bpy.ops.object.mode_set(mode='EDIT')
		obj = bpy.context.edit_object
		me = obj.data
		bm = bmesh.from_edit_mesh(me)

		cornerverts, sharp = corner_vertices(bm)
		#print("corner verts:", cornerverts)
		#print ("corner sharp:",sharp)
		# ------------------------------------------------
		# Get angle of edge corners
		bpy.ops.object.mode_set(mode='OBJECT')
		o = bpy.context.object
		mat = o.matrix_world
		sel = bpy.context.selected_objects
		#bpy.context.Scene.offset = .1

		if len(sel) == 2:

			sharpcnt = 0
			for v in range(0, len(cornerverts), 3):

				v1 = mat * o.data.vertices[cornerverts[v]].co
				v2 = mat * o.data.vertices[cornerverts[v + 1]].co
				v3 = mat * o.data.vertices[cornerverts[v + 2]].co

				vec_result = get_angle (v1,v2,v3)

				ob = create_object(sel[0], v1)

				ob.rotation_mode = 'QUATERNION'

				if sharp[sharpcnt] == True:
					vec_result = - vec_result
				sharpcnt += 1

				ob.rotation_quaternion = Vector.to_track_quat(-vec_result, '-Y', 'Z')
				bpy.context.scene.update()

				# offset
				vec = Vector((0, -bpy.context.scene.offset, 0))
				inv = ob.matrix_world.copy()
				inv.invert()
				# vec aligned to local axis
				vec_rot = vec * inv
				ob.location += vec_rot

				# rename
				if bpy.context.scene.angle:
					ob.name = rename(ob.name,Vector.to_track_quat(-vec_result, '-Y', 'Z'))

		return {'FINISHED'}


class Gutterpanel(bpy.types.Panel):

	bl_label = "Add Gutters"
	bl_idname = "OBJECT_PT_gutter"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	#bl_context = "scene"

	def draw(self, context):

		layout = self.layout
		scene = context.scene

		col = layout.column()
		col.operator("gutters.doit", "Gutters")
		col.prop(scene,"offset","offset")
		col.prop(scene,"angle","Angle to name")

def register():
	bpy.utils.register_module(__name__)


def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
