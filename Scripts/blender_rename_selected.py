import bpy

textToReplace = 'sector_-2_-2'
textToPut = 'sector_-2_-2_U'

if bpy.context.selected_objects != []:
	objectss = bpy.context.selected_objects.copy()
	for obj in objectss:
		if (textToReplace in obj.name):
			obj.name = obj.name.replace(textToReplace, textToPut)

print('Finished')