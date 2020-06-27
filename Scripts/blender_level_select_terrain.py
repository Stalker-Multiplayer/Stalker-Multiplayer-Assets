import bpy

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
	if obj.type == 'MESH' and len(obj.data.materials) > 0 and 'terrain' in obj.data.materials[0].name:
		obj.select = True

print('Finished')