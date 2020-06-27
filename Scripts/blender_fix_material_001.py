import bpy

print('---------------------------------------------------')
print('Fix material 001 started')

dict_materials = dict()

for obj in bpy.data.objects:
	if obj.type == 'MESH':
		materialName = obj.data.materials[0].name
		
		if '.' not in materialName and materialName not in dict_materials:
			dict_materials[materialName] = obj.data.materials[0]

for obj in bpy.data.objects:
	if obj.type == 'MESH':
		materialName = obj.data.materials[0].name
		
		if '.' in materialName:
			materialName = materialName[:materialName.rfind('.'):1]
			obj.data.materials[0] = dict_materials[materialName]
	
print('Fix material 001 finished')
print('---------------------------------------------------')