import sys
import unreal

if len(sys.argv) < 2:
	print 'Please provide path to proper materials folder'
	sys.exit()

print "Redirect mesh materials script started"

targetFolder = "/Game/" + sys.argv[1]

@unreal.uclass()
class MyEditorUtility(unreal.GlobalEditorUtilityBase):
	pass

editor_util = MyEditorUtility()
assets = editor_util.get_selected_assets()

missingMaterials = []

for asset in assets:
	classType = asset.get_class().get_name()
	
	if classType == 'StaticMesh':
		materialName = asset.get_material(0).get_name()
		targetAssetPath = targetFolder + "/" + materialName[:materialName.find('_'):1] + "/" + materialName + "." + materialName
		
		if unreal.EditorAssetLibrary.does_asset_exist(targetAssetPath):
			material = unreal.EditorAssetLibrary.load_asset(targetAssetPath)
			
			asset.set_material(0, material)
		else:
			if materialName not in missingMaterials:
				missingMaterials.append(materialName)


for materialName in missingMaterials:
	print 'Missing material : ' + materialName

print "Redirect mesh materials script finished"
