import bpy

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
	if obj.type == 'EMPTY' and 'multiusage' in obj.name:
		obj.select = True
		
		for child in obj.children:
			child.select = True

print('Finished')