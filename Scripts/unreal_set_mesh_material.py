import sys
import unreal

MATERIAL_SLOT_INDEX = 1

print "Set mesh material script started"

if len(sys.argv) < 2:
	print("Please provide material path")
	sys.exit()

materialPath = "/Game/" + sys.argv[1]
if not unreal.EditorAssetLibrary.does_asset_exist(materialPath):
	print("Specified material doesn't exist")
	exit

@unreal.uclass()
class MyEditorUtility(unreal.GlobalEditorUtilityBase):
	pass

editor_util = MyEditorUtility()
assets = editor_util.get_selected_assets()

material = unreal.EditorAssetLibrary.load_asset(materialPath)

for asset in assets:
    classType = asset.get_class().get_name()
    
    if classType == 'StaticMesh':
		if asset.get_material(MATERIAL_SLOT_INDEX) is None:
			asset.add_material(material)
		else:
			asset.set_material(MATERIAL_SLOT_INDEX, material)
		
		unreal.EditorAssetLibrary.save_loaded_asset(asset)
    

print "Set mesh material script finished"
