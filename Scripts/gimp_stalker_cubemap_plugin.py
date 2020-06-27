#!/usr/bin/python
 
from gimpfu import *
 
def convert_plugin(timg, tdrawable):
  images = gimp.image_list()
  for image in images:
	layer = pdb.gimp_image_get_layer_by_name(image, 'main surface (positive x)')
	pdb.gimp_item_transform_rotate_simple(layer, 2, True, 256, 256)
	pdb.gimp_layer_set_name(layer, "+x")
	
	layer = pdb.gimp_image_get_layer_by_name(image, 'main surface (negative x)')
	item = pdb.gimp_item_transform_rotate_simple(layer, 0, True, 256, 256)
	pdb.gimp_layer_set_name(layer, "-x")
	
	layer = pdb.gimp_image_get_layer_by_name(image, 'main surface (positive y)')
	pdb.gimp_layer_set_name(layer, "+z")
	
	layer = pdb.gimp_image_get_layer_by_name(image, 'main surface (negative y)')
	pdb.gimp_layer_set_name(layer, "-z")
	
	layer = pdb.gimp_image_get_layer_by_name(image, 'main surface (positive z)')
	pdb.gimp_layer_set_name(layer, "-y")
	
	layer = pdb.gimp_image_get_layer_by_name(image, 'main surface (negative z)')
	item = pdb.gimp_item_transform_rotate_simple(layer, 1, True, 256, 256)
	pdb.gimp_layer_set_name(layer, "+y")

register(
  "convert_plugin",
  "Converts all opened cubemap images to be suitable for SMP cubemap",
  "Converts all opened cubemap images to be suitable for SMP cubemap",
  "Evghenii Olenciuc",
  "Evghenii Olenciuc",
  "2020",
  "<Image>/Image/Convert all cubemaps for SMP",
  "RGB*, GRAY*",
  [],
  [],
  convert_plugin)

main()