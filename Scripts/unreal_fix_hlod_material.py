import sys
import unreal

print "Fix hlod materials script started"

@unreal.uclass()
class MyEditorUtility(unreal.GlobalEditorUtilityBase):
	pass

editor_util = MyEditorUtility()
assets = editor_util.get_selected_assets()

for material in assets:
	classType = material.get_class().get_name()
	
	if classType == 'MaterialInstanceConstant':
		print material.get_name()
		
		properties = material.get_editor_property("base_property_overrides")
		properties.set_editor_property("override_shading_model", True)
		properties.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_SUBSURFACE)
		material.set_editor_property("base_property_overrides", properties)
		
		unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "SpecularConst", 0.05)
		unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material, "OpacityConst", 0.025)
		
		textures = material.get_editor_property("texture_parameter_values")
		for texture in textures:
			if texture.get_editor_property("parameter_info").get_editor_property("name") == "OpacityMaskTexture" or texture.get_editor_property("parameter_info").get_editor_property("name") == "DiffuseTexture":
				texture.get_editor_property("parameter_value").set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)

unreal.EditorAssetLibrary.save_loaded_asset(material, False)

print "Fix hlod materials script finished"
