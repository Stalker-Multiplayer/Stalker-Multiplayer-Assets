import sys
import unreal

print "Generate mesh lods script started"

@unreal.uclass()
class MyEditorUtility(unreal.GlobalEditorUtilityBase):
	pass

editor_util = MyEditorUtility()
assets = editor_util.get_selected_assets()

for asset in assets:
    classType = asset.get_class().get_name()
    
    if classType == 'StaticMesh':
		#if 'terrain' not in asset.get_name() and 'water' not in asset.get_name():
			material = None
			options = unreal.EditorScriptingMeshReductionOptions()

			options.reduction_settings = [ unreal.EditorScriptingMeshReductionSettings(1.0, 1.0), unreal.EditorScriptingMeshReductionSettings(0.5, 0.05) ]
			#options.reduction_settings = [ unreal.EditorScriptingMeshReductionSettings(1.0, 1.0) ]
			#options.reduction_settings = [ unreal.EditorScriptingMeshReductionSettings(1.0, 1.0), unreal.EditorScriptingMeshReductionSettings(0.5, 0.9) ]
			options.auto_compute_lod_screen_size = False
			
			material = asset.get_material(1)
			unreal.EditorStaticMeshLibrary.set_lods(asset, options)
			if material is not None:
				asset.set_material(1, material)
				
			unreal.EditorAssetLibrary.save_loaded_asset(asset)
    

print "Generate mesh lods script finished"
