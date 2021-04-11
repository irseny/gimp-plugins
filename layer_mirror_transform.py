#!/usr/bin/env python

from gimpfu import *

class mirror_axis():

	def __init__(self, x1, y1, x2, y2):
		self.dx = float(x2 - x1)
		self.dy = float(y2 - y1)
		self.ox = float(x1)
		self.oy = float(y1)

	def project_point(self, x, y):
		x1 = x - self.ox
		y1 = y - self.oy

		sqr = self.dx*self.dx + self.dy*self.dy
		longi = (self.dx*x1 + self.dy*y1)/sqr
		lateral = (-self.dy*x1 + self.dx*y1)/sqr

		return longi, lateral

	def projection_to_point(self, longi, lateral):

		x1 = self.dx*longi
		y1 = self.dy*longi

		x2 = -self.dy*lateral
		y2 = self.dx*lateral

		return x1 + x2 + self.ox, y1 + y2 + self.oy


"""
Establishes symmetry by positioning a specified layer
on the opposite of a mirror axis with regards to the selected layer

current_image: currently viewed image
selected_layer: curently active reference layer
unpinned_layer: layer to position
mirror_vector: vector to use as the mirror axis
args_ignored: superfluous arguments to ignore
return: error message
"""
def layersym(current_image, selected_layer, transform_layer, mirror_vector, *args_ignored):

	if (current_image is None):
		return "No image given"
	if (selected_layer is None):
		return "No reference layer given"
	if (transform_layer is None):
		return "Empty layer to align"
	if (mirror_vector is None):
		return "No mirror object given"

    #position = pdb.gimp_image_get_item_position(arg_image, layer)
	#pdb.gimp_message("image is " + str(current_image))
	#pdb.gimp_message("reference layer is " + str(selected_layer))
	#pdb.gimp_message("layer to align is " + str(transform_layer))
	#pdb.gimp_message("mirror vector is " + str(mirror_vector))

	#pdb.gimp_message("additional params are " + str(args_ignored))


	stroke_no, stroke_ids = pdb.gimp_vectors_get_strokes(mirror_vector)
	if stroke_no < 1:
		return "Empty mirror object"

	# read the control points of the first vector segment/line
	# this will be used as the mirror axis
	controlpoint_type, controlpoint_no, controlpoints, vector_closed = pdb.gimp_vectors_stroke_get_points(mirror_vector, stroke_ids[0])

	if controlpoint_no < 2*3*2:
		return "Not enough control points in path"

	mirror_x1 = controlpoints[0];
	mirror_y1 = controlpoints[1];
	mirror_x2 = controlpoints[2*3];
	mirror_y2 = controlpoints[2*3 + 1];
	if (mirror_x1 == mirror_x2 and mirror_y1 == mirror_y2):
		return "Control points do not form an axis"

	pdb.gimp_message("mirror axis from (" + str(int(mirror_x1)) + "|" + str(int(mirror_y1)) +
		") to (" + str(int(mirror_x2)) + "|" + str(int(mirror_y2)) + ")")

	mirror = mirror_axis(mirror_x1, mirror_y1, mirror_x2, mirror_y2)

	return establish_axis_symmetry(current_image, selected_layer, transform_layer, mirror)

"""
Moves the second layer to the other side of the mirror axis.

image: active image
pinned_layer: reference layer
unpinned layer: movable layer
mirror_axis: axis to mirror along
return: None
"""
def establish_axis_symmetry(image, pinned_layer, unpinned_layer, mirror_axis):
	# read the position of the reference layer
	off_x, off_y = pinned_layer.offsets
	origin_x = off_x + pinned_layer.width/2
	origin_y = off_y + pinned_layer.height/2

	pdb.gimp_message("mirroring (" + str(origin_x) + "|" + str(origin_y) + ")")


	# and project it onto the other side of the axis
	longi, lateral = mirror_axis.project_point(origin_x, origin_y)
	origin_x, origin_y = mirror_axis.projection_to_point(longi, -lateral)
	off_x = origin_x - unpinned_layer.width/2
	off_y = origin_y - unpinned_layer.height/2

	pdb.gimp_message("mirrored to (" + str(origin_x) + "|" + str(origin_y) + ")")

	# finally move the movable layer to the calculated coordinates
	unpinned_layer.set_offsets(int(off_x), int(off_y))

	return None

register(
	"layer-mirror-symmetry",
	"Position layers symmetrically",
	"Relocate a layer to establish symmetry with regards to an axis",
	"Irseny",
	"Irseny",
	"2021",
	"<Image>/Tools/Transform Tools/Layer mirror...",
	"*",
	[
		(PF_LAYER, "unpinned_layer", "Layer to align", None),
		(PF_VECTORS, "mirror_vector", "Mirror axis", None),
	],
	[],
	layersym)

main()
