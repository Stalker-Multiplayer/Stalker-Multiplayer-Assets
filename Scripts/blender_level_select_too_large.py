import bpy

bpy.ops.object.select_all(action='DESELECT')

SECTOR_SIZE = 200

for obj in bpy.data.objects:
	if obj.type == 'MESH':
		boundingBoxSize = [abs(obj.bound_box[0][0] - obj.bound_box[6][0]), abs(obj.bound_box[0][1] - obj.bound_box[6][1]), abs(obj.bound_box[0][2] - obj.bound_box[6][2])]

		if boundingBoxSize[0] > SECTOR_SIZE or boundingBoxSize[1] > SECTOR_SIZE:
			obj.select = True


print('Finished')