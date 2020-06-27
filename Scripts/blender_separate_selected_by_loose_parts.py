import bpy

i = 0

if bpy.context.selected_objects != []:
    objectss = bpy.context.selected_objects.copy()
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objectss:
        if obj.type == 'MESH':
            i += 1
            print('Processing object       :  ' + str(i) + ' of ' + str(len(objectss)))
            obj.select = True
            bpy.ops.mesh.separate(type='LOOSE')
            print('Separate result amount  :  ' + str(len(bpy.context.selected_objects)))
            print('Total objects in scene  :  ' + str(len(bpy.context.scene.objects)))
            bpy.ops.object.select_all(action='DESELECT')

print('Finished')