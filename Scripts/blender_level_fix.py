import bpy

def selectAllObjectsInObjectRecursively(rootObject):
	selectedAmount = 1

	for child in rootObject.children:
		selectedAmount = selectedAmount + selectAllObjectsInObjectRecursively(child)
		
	rootObject.select = True
	
	return selectedAmount

def getObjectLocationFull(obj):
	objLocation = [obj.location[0], obj.location[1], obj.location[2]]
	objParent = obj.parent
	while objParent != None:
		objLocation = [objParent.location[0] + objLocation[0], objParent.location[1] + objLocation[1], objParent.location[2] + objLocation[2]]
		objParent = objParent.parent
		
	return objLocation

def getObjectRotationFull(obj):
	objRotation = [obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]]
	objParent = obj.parent
	while objParent != None:
		objRotation = [objParent.rotation_euler[0] + objRotation[0], objParent.rotation_euler[1] + objRotation[1], objParent.rotation_euler[2] + objRotation[2]]
		objParent = objParent.parent
		
	return objRotation

def getObjectScaleFull(obj):
	objScale = [obj.scale[0], obj.scale[1], obj.scale[2]]
	objParent = obj.parent
	while objParent != None:
		objScale = [objParent.scale[0] * objScale[0], objParent.scale[1] * objScale[1], objParent.scale[2] * objScale[2]]
		objParent = objParent.parent
		
	return objScale

def mergeListMeshes(listToMerge):
	bpy.ops.object.select_all(action='DESELECT')

	materialName = listToMerge[0].data.materials[0].name
	if '_Mat' in materialName:
		materialName = materialName[:materialName.find('_Mat'):1]

	mesh = bpy.data.meshes.new(materialName)
	mesh = bpy.data.objects.new(materialName, mesh)
	bpy.context.scene.objects.link(mesh)
	mesh.data = listToMerge[0].data
	mesh.data.name = mesh.name
	bpy.context.scene.objects.active = mesh
	mesh.select = True

	for obj in listToMerge:
		obj.select = True
	
	bpy.ops.object.join()
	mesh.data.name = mesh.name


def removeUnusedObjects():
	bpy.ops.object.select_all(action='DESELECT')

	for obj in bpy.data.objects:
		if obj.type == 'MESH' and 'FASTPATH' not in obj.name:
			objLocation = getObjectLocationFull(obj)
			objRotation = getObjectRotationFull(obj)
			objScale = getObjectScaleFull(obj)
			obj.location = objLocation
			obj.rotation_euler = objRotation
			obj.scale = objScale
		
	objectsToDeleteCount = 0
	
	for obj in bpy.data.objects:
		if obj.type == 'EMPTY':
			objectsToDeleteCount = objectsToDeleteCount + 1
			obj.select = True
		if obj.type == 'MESH' and 'FASTPATH' in obj.name:
			objectsToDeleteCount = objectsToDeleteCount + 1
			obj.select = True

	print('Deleting ' + str(objectsToDeleteCount) + ' unused objects. This might take a while...')
	bpy.ops.object.delete()


def fixMaterialNames():
	print('Fixing material names...')
	
	dict_materials = dict()

	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			materialName = obj.data.materials[0].name
			if '\\' in materialName:
				materialName = materialName[materialName.rfind('\\') + 1::1]
			if '.' in materialName:
				materialName = materialName[:materialName.find('.'):1]
				
			if not materialName.endswith('_Mat'):
				materialName = materialName + '_Mat'

			if materialName in dict_materials:
				obj.data.materials[0] = dict_materials[materialName]
			else:
				obj.data.materials[0].name = materialName
				obj.data.materials[0].texture_slots[0].texture.name = materialName
				obj.data.materials[0].texture_slots[0].texture.image.name = materialName
				dict_materials[materialName] = obj.data.materials[0]


def mergeMeshesBySectors():
	print('Merging meshes by sectors...')

	SECTOR_SIZE = 200
	
	dict_staticSectors = dict()
	dict_multiusageSectors = dict()
	dict_decalSectors = dict()
	list_terrainMeshes = []
	list_waterMeshes = []
	list_nosunMeshes = []

	arr_objectsToSplit = []
	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			boundingBoxSize = [abs(obj.bound_box[0][0] - obj.bound_box[6][0]), abs(obj.bound_box[0][1] - obj.bound_box[6][1]), abs(obj.bound_box[0][2] - obj.bound_box[6][2])]

			if boundingBoxSize[0] > SECTOR_SIZE or boundingBoxSize[1] > SECTOR_SIZE:
				arr_objectsToSplit.append(obj)

	processedObjectsCount = 0
	totalObjectsToProcess = len(arr_objectsToSplit)
	for objToSplit in arr_objectsToSplit:
		processedObjectsCount = processedObjectsCount + 1
		print(str(processedObjectsCount) + '/' + str(totalObjectsToProcess) + '	| Splitting ' + objToSplit.name)
		objToSplit.select = True
		bpy.ops.mesh.separate(type='LOOSE')
		bpy.ops.object.select_all(action='DESELECT')

	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			type = 'NORMAL'
			if 'TREE_' in obj.name:
				type = 'MULTIUSAGE'
			else:
				if 'water_water' in obj.data.materials[0].name:
					type = 'WATER'
				elif ('decal' in obj.data.materials[0].name or 'wm_' in obj.data.materials[0].name):
					type = 'DECAL'

			if type == 'WATER':
				list_waterMeshes.append(obj)
			else:
				objLocation = getObjectLocationFull(obj)
				objRotation = getObjectRotationFull(obj)
				objScale = getObjectScaleFull(obj)

				boundingBoxCenter = [(obj.bound_box[0][0] + obj.bound_box[6][0]) / 2, (obj.bound_box[0][1] + obj.bound_box[6][1]) / 2, (obj.bound_box[0][2] + obj.bound_box[6][2]) / 2]
				boundingBoxCenter[0] = boundingBoxCenter[0] + objLocation[0]
				boundingBoxCenter[1] = boundingBoxCenter[1] + objLocation[1]
				boundingBoxCenter[2] = boundingBoxCenter[2] + objLocation[2]

				sectorName = 'sector_' + str(round(boundingBoxCenter[0] / SECTOR_SIZE)) + '_' + str(round(boundingBoxCenter[1] / SECTOR_SIZE))
				
				if type == 'MULTIUSAGE':
					if sectorName not in dict_multiusageSectors:
						sector = bpy.data.objects.new(sectorName + '_multiusage', None)
						bpy.context.scene.objects.link(sector)
						dict_multiusageSectors[sectorName] = sector
						
						print('Creating multiusage ' + sectorName)
					obj.parent = dict_multiusageSectors[sectorName]
				elif type == 'DECAL':
					if sectorName not in dict_decalSectors:
						sector = bpy.data.objects.new(sectorName + '_decals', None)
						bpy.context.scene.objects.link(sector)
						dict_decalSectors[sectorName] = sector
						
						print('Creating decal ' + sectorName)
					obj.parent = dict_decalSectors[sectorName]
				else:
					if sectorName not in dict_staticSectors:
						sector = bpy.data.objects.new(sectorName, None)
						bpy.context.scene.objects.link(sector)
						dict_staticSectors[sectorName] = sector
						
						print('Creating ' + sectorName)
					obj.parent = dict_staticSectors[sectorName]
					
				obj.location = objLocation
				obj.rotation_euler = objRotation
				obj.scale = objScale

	bpy.context.scene.objects.active = None
	bpy.ops.object.select_all(action='DESELECT')

	if len(list_waterMeshes) > 0:
		print('Merging water...')
		mergeListMeshes(list_waterMeshes)
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.remove_doubles(threshold=0.0002, use_unselected=True)
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')
	
	print('Merging static meshes by material and grouping multiusage...')

	for sectorName, sector in dict_staticSectors.items():
		print('Merging ' + sectorName + '...')

		dict_toMerge = dict()

		for obj in sector.children:
			if obj.type == 'MESH':
				materialName = obj.data.materials[0].name
				if '_Mat' in materialName:
					materialName = materialName[:materialName.find('_Mat'):1]

				if materialName not in dict_toMerge:
					mesh = bpy.data.meshes.new(sectorName + '_' + materialName)
					baseObj = bpy.data.objects.new(sectorName + '_' + materialName, mesh)
					bpy.context.scene.objects.link(baseObj)
					baseObj.data = obj.data
					baseObj.data.name = baseObj.name
					baseObj.parent = sector
					dict_toMerge[materialName] = [ baseObj ]

				dict_toMerge[materialName].append(obj)

		processedObjectsCount = 0
		totalObjectsToProcess = len(dict_toMerge)

		for key, meshesArray in dict_toMerge.items():
			processedObjectsCount = processedObjectsCount + 1
			print(str(processedObjectsCount) + '/' + str(totalObjectsToProcess) + '	| Merging ' + meshesArray[0].name)
			bpy.ops.object.select_all(action='DESELECT')
			bpy.context.scene.objects.active = meshesArray[0]
			for meshObject in meshesArray:
				meshObject.select = True
			bpy.ops.object.join()
			meshesArray[0].data.name = meshesArray[0].name
			
	dict_multiusageMeshNumbers = dict()

	for sectorName, sector in dict_multiusageSectors.items():
		dict_multiusage = dict()
		
		for obj in sector.children:
			if obj.type == 'MESH':
				materialName = obj.data.materials[0].name
				if materialName not in dict_multiusage:
					dict_multiusage[materialName] = []

				dict_multiusage[materialName].append(obj)
				
		totalObjectsToProcess = 0
		for key, multiusageArray in dict_multiusage.items():
			totalObjectsToProcess = totalObjectsToProcess + len(multiusageArray)
			
		print('Processing ' + str(totalObjectsToProcess) + ' multiusage...')
		
		if len(dict_multiusage.items()) > 0:
			for materialName, multiusageArray in dict_multiusage.items():
				if '_Mat' in materialName:
					materialName = materialName[:materialName.find('_Mat'):1]
	
				multiusageNumber = 0
				
				for multiusageObject in multiusageArray:
					childLocation = getObjectLocationFull(multiusageObject)
					childRotation = getObjectRotationFull(multiusageObject)
					childScale = getObjectScaleFull(multiusageObject)

					multiusageNumber = multiusageNumber + 1
					if materialName in dict_multiusageMeshNumbers:
						if multiusageObject.data not in dict_multiusageMeshNumbers[materialName]:
							dict_multiusageMeshNumbers[materialName].append(multiusageObject.data)
					else:
						dict_multiusageMeshNumbers[materialName] = [ multiusageObject.data ]

					multiusageObject.name = sectorName + '_' + materialName + '_' + str(multiusageNumber)
					multiusageObject.data.name = materialName + '_' + str(dict_multiusageMeshNumbers[materialName].index(multiusageObject.data))
					multiusageObject.parent = sector

					multiusageObject.location = childLocation
					multiusageObject.rotation_euler = childRotation
					multiusageObject.scale = childScale

	for sectorName, sector in dict_decalSectors.items():
		dict_decals = dict()

		for obj in sector.children:
			if obj.type == 'MESH':
				materialName = obj.data.materials[0].name
				if materialName not in dict_decals:
					dict_decals[materialName] = []

				dict_decals[materialName].append(obj)

		totalObjectsToProcess = 0
		for key, decalArray in dict_decals.items():
			totalObjectsToProcess = totalObjectsToProcess + len(decalArray)
			
		print('Processing ' + str(totalObjectsToProcess) + ' decals...')
		
		if len(dict_decals.items()) > 0:
			for materialName, decalArray in dict_decals.items():
				if '_Mat' in materialName:
					materialName = materialName[:materialName.find('_Mat'):1]
	
				decalNumber = 0
				
				for decalObject in decalArray:
					childLocation = getObjectLocationFull(decalObject)
					childRotation = getObjectRotationFull(decalObject)
					childScale = getObjectScaleFull(decalObject)

					decalNumber = decalNumber + 1

					decalObject.name = sectorName + '_' + materialName + '_' + str(decalNumber)
					decalObject.data.name = decalObject.name
					decalObject.parent = sector

					decalObject.location = childLocation
					decalObject.rotation_euler = childRotation
					decalObject.scale = childScale


def fixMeshesScale():
	print('Fixing meshes scale...')

	bpy.ops.object.select_all(action='DESELECT')

	singleDataObjects = []
	multiDataObjects = dict()

	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			if obj.data.users == 1:
				singleDataObjects.append(obj)
			else:
				if obj.data.name not in multiDataObjects:
					multiDataObjects[obj.data.name] = []

				multiDataObjects[obj.data.name].append(obj)

	processedObjectsCount = 0
	totalObjectsToProcess = len(singleDataObjects) + len(multiDataObjects)

	for obj in singleDataObjects:
		processedObjectsCount = processedObjectsCount + 1
		print(str(processedObjectsCount) + '/' + str(totalObjectsToProcess) + '	| Scaling ' + obj.name)
		
		obj.location = [obj.location[0] * 100, obj.location[1] * 100, obj.location[2] * 100]
		obj.scale = [100, 100, 100]
		obj.select = True
		bpy.context.scene.objects.active = obj
		bpy.ops.object.transform_apply(location = True, scale = True, rotation = False)
		obj.select = False

	for key, arr in multiDataObjects.items():
		processedObjectsCount = processedObjectsCount + 1
		print(str(processedObjectsCount) + '/' + str(totalObjectsToProcess) + '	| Scaling ' + obj.name)
		
		obj = arr[0]

		newData = obj.data.copy()
		obj.data = newData
		obj.scale = [100, 100, 100]
		obj.select = True
		bpy.context.scene.objects.active = obj
		bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
		obj.select = False

		for subObj in arr:
			subObj.location = [subObj.location[0] * 100, subObj.location[1] * 100, subObj.location[2] * 100]
			if subObj != obj:
				subObj.data = newData

		newData.name = newData.name[:-4]


def removeMeshDoubles():
	print('Removing meshes doubles...')

	dict_datas = dict()

	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			if obj.data not in dict_datas:
				dict_datas[obj.data] = obj

	processedObjectsCount = 0
	totalObjectsToProcess = len(dict_datas)

	for data, mesh in dict_datas.items():
		processedObjectsCount = processedObjectsCount + 1
		print(str(processedObjectsCount) + '/' + str(totalObjectsToProcess) + '	| Removing doubles ' + mesh.name)

		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.scene.objects.active = mesh
		mesh.select = True

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=True)
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')

	bpy.context.scene.objects.active = None
	bpy.ops.object.select_all(action='DESELECT')


def fixMeshLightmaps():
	print('Fixing mesh lightmaps...')

	bpy.context.scene.objects.active = None
	bpy.ops.object.select_all(action='DESELECT')

	lightmappedMeshes = []

	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			if obj.data not in lightmappedMeshes:
				lightmappedMeshes.append(obj.data)
				
	totalObjectsToProcess = len(lightmappedMeshes)
	processedObjectsCount = 0
	lightmappedMeshes = []

	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			if obj.data not in lightmappedMeshes:
				processedObjectsCount = processedObjectsCount + 1

				print(str(processedObjectsCount) + '/' + str(totalObjectsToProcess) + '	| Making lightmap for ' + obj.name)

				bpy.context.scene.objects.active = obj
				obj.select = True

				if len(obj.data.uv_layers) < 2:
					bpy.ops.mesh.uv_texture_add()

				obj.data.uv_layers[0].name = 'MainTexture'
				obj.data.uv_layers[1].name = 'LightMapUV'
				obj.data.uv_textures['LightMapUV'].active = True

				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.uv.unwrap()
				bpy.ops.object.mode_set(mode='OBJECT')

				obj.select = False

				lightmappedMeshes.append(obj.data)

	bpy.context.scene.objects.active = None


print('---------------------------------------------------')
print('Level fix started')

removeUnusedObjects()
fixMaterialNames()
mergeMeshesBySectors()
fixMeshesScale()
#removeMeshDoubles()
fixMeshLightmaps()

bpy.context.scene.objects.active = None
bpy.ops.object.select_all(action='DESELECT')

print('Level fix finished')
print('---------------------------------------------------')