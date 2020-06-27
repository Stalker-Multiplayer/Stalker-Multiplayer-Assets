import bpy

def fixMeshesScale():
	print('Fixing meshes scale...')

	bpy.ops.object.select_all(action='DESELECT')

	singleDataObjects = []

	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			singleDataObjects.append(obj)

	processedObjectsCount = 0
	totalObjectsToProcess = len(singleDataObjects)

	for obj in singleDataObjects:
		processedObjectsCount = processedObjectsCount + 1
		print(str(processedObjectsCount) + '/' + str(totalObjectsToProcess) + '	| Scaling ' + obj.name)
		
		obj.location = [0, 0, 0]
		obj.scale = [100, 100, 100]
		obj.select = True
		bpy.context.scene.objects.active = obj
		bpy.ops.object.transform_apply(location = True, scale = True, rotation = False)
		obj.select = False

print('---------------------------------------------------')
print('Scale meshes started')

fixMeshesScale()

bpy.context.scene.objects.active = None
bpy.ops.object.select_all(action='DESELECT')

print('Scale meshes finished')
print('---------------------------------------------------')