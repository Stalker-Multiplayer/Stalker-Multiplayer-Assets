import bpy


def selectAllObjectsInObjectRecursively(rootObject):
	selectedAmount = 1

	for child in rootObject.children:
		selectedAmount = selectedAmount + selectAllObjectsInObjectRecursively(child)
		
	rootObject.select = True
	
	return selectedAmount


if bpy.context.selected_objects != []:
	objectss = bpy.context.selected_objects.copy()
	for obj in objectss:
		selectAllObjectsInObjectRecursively(obj)
	

print('Finished')