import bpy
import sys
import io

bpy.ops.object.select_all(action='DESELECT')

objectss = []

for obj in bpy.data.objects:
	if obj.type == 'MESH':
		objectss.append(obj)

while len(objectss) > 0:
	print('Removing duplicates vertices for ' + str(len(objectss)) + ' meshes')
	for obj in objectss:
		bpy.context.scene.objects.active = obj
		obj.select = True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		
		stdout_ = sys.stdout #Keep track of the previous value.
		stream = io.StringIO()
		sys.stdout = stream
		bpy.ops.mesh.remove_doubles(threshold=0.00001, use_unselected=True)
		removedVerticesCount = stream.getvalue()
		
		bpy.ops.object.mode_set(mode='OBJECT')
		sys.stdout = stdout_ # restore the previous stdout.
		
		obj.select = False
		
		removedVerticesCount = int(removedVerticesCount.split()[2])
		if removedVerticesCount <= 0:
			objectss.remove(obj)
		
bpy.context.scene.objects.active = None

print('Script finished')