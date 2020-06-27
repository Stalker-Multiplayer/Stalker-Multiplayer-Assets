import sys
import unreal
import os
import inspect


class TextureData(object):
	texture = ''
	bumpMode = ''
	normalTexture = ''
	bumpTexture = ''
	useDetails = ''
	detailsTexture = ''
	detailsTextureNormal = ''
	detailsTextureBump = ''
	detailsTextureScale = 1.0
	
	
def parseAndSetLine(textureData, line):
	if '=' in line:
		field = line[:line.find('=')]
		value = line[line.find('=') + 1:]
		
		if field == 'texture':
			textureData.texture = value.strip()
		elif field == 'bumpMode':
			textureData.bumpMode = value.strip()
		elif field == 'normalTexture':
			textureData.normalTexture = value.strip()
		elif field == 'bumpTexture':
			textureData.bumpTexture = value.strip()
		elif field == 'useDetails':
			textureData.useDetails = value.strip()
		elif field == 'detailsTexture':
			textureData.detailsTexture = value.strip()
		elif field == 'detailsTextureNormal':
			textureData.detailsTextureNormal = value.strip()
		elif field == 'detailsTextureBump':
			textureData.detailsTextureBump = value.strip()
		elif field == 'detailsTextureScale':
			textureData.detailsTextureScale = float(value.strip())
	
	
def parseTextureCfg(dir):
	file = open(dir, 'r')
	try:
		textureData = TextureData()
		line = file.readline()
		while line:
			parseAndSetLine(textureData, line)
			line = file.readline()
		return textureData
	finally:
		file.close()

	return None
	
	
def textureCfgToBaseMaterial(textureCfg):
	if textureCfg.bumpMode == 'withbump':
		useNormal = 'yes'
		useParallax = 'no'
	elif textureCfg.bumpMode == 'bumpwithparallax':
		useNormal = 'yes'
		useParallax = 'yes'
	else:
		useNormal = 'no'
		useParallax = 'no'
	
	if textureCfg.useDetails == 'true':
		useDetails = 'yes'
	else:
		useDetails = 'no'
		
	return 'Generic_' + useNormal + '_' + useParallax + '_' + useDetails

	
if len(sys.argv) < 4:
    print 'Please provide path to Stalker \'textures\' folder, to output textures folder and to output materials folder'
    sys.exit()

print "Import textures and materials script started"

sourceTexturesFolder = sys.argv[1]
outputTexturesFolder = "/Game/" + sys.argv[2]
outputMaterialsFolder = "/Game/" + sys.argv[3]

textureConfigs = []
for (dirpath, dirnames, filenames) in os.walk(sourceTexturesFolder):
	for filename in filenames:
		if '.cfg' in filename:
			textureCfg = parseTextureCfg(dirpath + '\\' + filename)
			textureConfigs.append(textureCfg)
			
			
for textureCfg in textureConfigs:
	print sourceTexturesFolder + '\\' + textureCfg.texture + '.png'
	
	task = unreal.AssetImportTask()
	task.filename = sourceTexturesFolder + '\\' + textureCfg.texture + '.png'
	task.destination_path = outputTexturesFolder + '/' + textureCfg.texture[:textureCfg.texture.rfind('\\')].replace('\\', '/')
	task.automated = True
	task.save = True
	task.replace_existing = False
	
	tasks = [task]
	
	if textureCfg.bumpMode != 'nobump':
		task = unreal.AssetImportTask()
		task.filename = sourceTexturesFolder + '\\' + textureCfg.normalTexture + '.png'
		task.destination_path = outputTexturesFolder + '/' + textureCfg.normalTexture[:textureCfg.normalTexture.rfind('\\')].replace('\\', '/')
		task.automated = True
		task.save = False
		task.replace_existing = False
		
		tasks.append(task)
		
		
		task = unreal.AssetImportTask()
		task.filename = sourceTexturesFolder + '\\' + textureCfg.bumpTexture + '.png'
		task.destination_path = outputTexturesFolder + '/' + textureCfg.bumpTexture[:textureCfg.bumpTexture.rfind('\\')].replace('\\', '/')
		task.automated = True
		task.save = False
		task.replace_existing = False
		
		tasks.append(task)
	
	unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)


for textureCfg in textureConfigs:
	unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=textureCfg.texture[textureCfg.texture.rfind('\\') + 1:] + '_Mat', package_path=outputMaterialsFolder + '/' + textureCfg.texture[:textureCfg.texture.rfind('\\')].replace('\\', '/'), asset_class=unreal.MaterialInstanceConstant, factory=unreal.MaterialInstanceConstantFactoryNew())
	
	# set parent
	baseMaterialName = textureCfgToBaseMaterial(textureCfg)
	parent = unreal.EditorAssetLibrary.load_asset('/Game/Base/Instances/' + baseMaterialName + '.' + baseMaterialName)
	asset = unreal.EditorAssetLibrary.load_asset(outputMaterialsFolder + '/' + textureCfg.texture + '_Mat' + '.' + textureCfg.texture[textureCfg.texture.rfind('\\') + 1:] + '_Mat')
	unreal.MaterialEditingLibrary.set_material_instance_parent(asset, parent)
	
	# set parameters
	texture = unreal.EditorAssetLibrary.load_asset(outputTexturesFolder + '/' + textureCfg.texture + '.' + textureCfg.texture[textureCfg.texture.rfind('\\') + 1:])
	unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(asset, 'BaseTexture', texture)
	
	if textureCfg.bumpMode == 'withbump' or textureCfg.bumpMode == 'bumpwithparallax':
		texture = unreal.EditorAssetLibrary.load_asset(outputTexturesFolder + '/' + textureCfg.normalTexture + '.' + textureCfg.normalTexture[textureCfg.normalTexture.rfind('\\') + 1:])
		unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(asset, 'NormalMap', texture)
		
		texture = unreal.EditorAssetLibrary.load_asset(outputTexturesFolder + '/' + textureCfg.bumpTexture + '.' + textureCfg.bumpTexture[textureCfg.bumpTexture.rfind('\\') + 1:])
		unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(asset, 'Bump', texture)
		
	if textureCfg.useDetails == 'true':
		texture = unreal.EditorAssetLibrary.load_asset(outputTexturesFolder + '/' + textureCfg.detailsTexture + '.' + textureCfg.detailsTexture[textureCfg.detailsTexture.rfind('\\') + 1:])
		unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(asset, 'DetailedTexture', texture)
		
		texture = unreal.EditorAssetLibrary.load_asset(outputTexturesFolder + '/' + textureCfg.detailsTextureNormal + '.' + textureCfg.detailsTextureNormal[textureCfg.detailsTextureNormal.rfind('\\') + 1:])
		unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(asset, 'DetailedNormal', texture)
		
		texture = unreal.EditorAssetLibrary.load_asset(outputTexturesFolder + '/' + textureCfg.detailsTextureBump + '.' + textureCfg.detailsTextureBump[textureCfg.detailsTextureBump.rfind('\\') + 1:])
		unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(asset, 'DetailedBump', texture)
		
		unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(asset, 'DetailScale', textureCfg.detailsTextureScale)
		

print "Import textures and materials finished"
