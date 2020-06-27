import bpy

print('---------------------------------------------------')
print('Replace asset name started')

text_to_replace = "sector_-2_0"
text_to_put = "sector_-2_0_U"

if bpy.context.selected_objects != []:
	objectss = bpy.context.selected_objects.copy()
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objectss:
		obj.name = obj.name.replace(text_to_replace, text_to_put)
		if obj.type == 'MESH':
			obj.data.name = obj.data.name.replace(text_to_replace, text_to_put)

print('Replace asset name finished')
print('---------------------------------------------------')