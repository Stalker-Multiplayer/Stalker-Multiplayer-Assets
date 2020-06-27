import sys
import unreal

print "Change impostor material shading model script started"

@unreal.uclass()
class MyEditorUtility(unreal.GlobalEditorUtilityBase):
	pass

editor_util = MyEditorUtility()
assets = editor_util.get_selected_assets()

for material in assets:
	classType = material.get_class().get_name()
	
	if classType == 'MaterialInstanceConstant':
		print material.get_name()
		
		unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "Roughness", 1.0)
		unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "Speculat", 0.05)
		
		unreal.EditorAssetLibrary.save_loaded_asset(material, False)

print "Change impostor material shading model script finished"
