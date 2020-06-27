import sys
import struct
import os


class TextureData(object):
	texture = ''
	bumpMode = ''
	normalTexture = ''
	bumpTexture = ''
	useDetails = ''
	useDetailsBump = ''
	detailsTexture = None
	detailsTextureScale = 1.0


def use_details_switch(i):
	switcher={
		0:'false',
		128:'true'
	}
	return switcher.get(i, str(i))

	
def use_details_bump_switch(i):
	switcher={
		0:'false',
		1:'false',
		2:'false',
		3:'false',
		4:'true',
		6:'true'
	}
	return switcher.get(i, str(i))


def texture_type_switch(i):
	switcher={
		0:'texture',
		1:'cubemap',
		2:'bumpmap',
		3:'normalmap',
		4:'terrain'
	}
	return switcher.get(i, str(i))


def bump_mode_switch(i):
	switcher={
		1:'nobump',
		2:'withbump',
		3:'bumpwithparallax'
	}
	return switcher.get(i, str(i))
	
	
def parseThm(sourceFolder, filename):
	file = open(sourceFolder + "\\" + filename + '.thm', 'rb')
	try:
		textureData = TextureData()

		file.read(36)

		textureData.texture = filename
		textureData.useDetails = use_details_switch(ord(file.read(1)))
		if textureData.useDetails != 'false' and textureData.useDetails != 'true':
			print(dirpath + '\\' + filename)
			print('unknown useDetails : ' + useDetails)
			return None

		textureData.useDetailsBump = use_details_bump_switch(ord(file.read(1)))
		if textureData.useDetailsBump != 'false' and textureData.useDetailsBump != 'true':
			print(dirpath + '\\' + filename)
			print('unknown useDetailsBump : ' + textureData.useDetailsBump)
			return None

		file.read(32)

		if '_det.thm' in filename + '.thm':
			textureData.textureType = 'terraindetail'
		else:
			textureData.textureType = texture_type_switch(ord(file.read(1)))
		if textureData.textureType != 'texture' and textureData.textureType != 'cubemap' and textureData.textureType != 'bumpmap' and textureData.textureType != 'normalmap' and textureData.textureType != 'terrain' and textureData.textureType != 'terraindetail':
			print(dirpath + '\\' + filename)
			print('unknown textureType : ' + textureData.textureType)
			return None

		if textureData.textureType != 'texture':
			#print(dirpath + '\\' + filename)
			#print('textureType is not supported : ' + textureData.textureType)
			return None

		file.read(7)

		detailsTextureNameLength = ord(file.read(1)) - 5

		file.read(3)

		if detailsTextureNameLength > 0:
			detailsTextureName = file.read(detailsTextureNameLength).decode('utf-8')
			
			if textureData.useDetails == 'true':
				textureData.detailsTexture = parseThm(sourceFolder, detailsTextureName)

		file.read(1)

		textureData.detailsTextureScale = struct.unpack('f', file.read(4))[0]

		file.read(20)
					
		bumpTextureNameLength = ord(file.read(1)) - 9
					
		file.read(7)
					
		textureData.bumpMode = bump_mode_switch(ord(file.read(1)))
		if textureData.bumpMode != 'nobump' and textureData.bumpMode != 'withbump' and textureData.bumpMode != 'bumpwithparallax':
			print(dirpath + '\\' + filename)
			print('unknown bumpMode : ' + textureData.bumpMode)
			return None
					
		file.read(3)
					
		if bumpTextureNameLength > 0:
			textureData.normalTexture = file.read(bumpTextureNameLength).decode('utf-8')
			textureData.bumpTexture = textureData.normalTexture + '#'
			
		return textureData
	finally:
		file.close()


if len(sys.argv) < 3:
	print("Please provide path to source textures folder and to output folder")
	sys.exit()

print("Parse stalker textures script started")

sourceFolder = sys.argv[1]
outputFolder = sys.argv[2]

for (dirpath, dirnames, filenames) in os.walk(sourceFolder):
	for filename in filenames:
		if '.thm' in filename and not '#.thm' in filename and not '$' in filename:
			filename = dirpath[len(sourceFolder) + 1:] + '\\' + filename[0:-4]
			
			textureData = parseThm(sourceFolder, filename)
			if textureData == None:
				continue

			print('Converting ' + filename)

			# write cfg data
			os.makedirs(os.path.dirname(outputFolder + "\\" + filename), exist_ok=True)
			file = open(outputFolder + "\\" + filename + '.cfg', 'w')
			try:
				if textureData.textureType == 'texture':
					file.write('texture=' + textureData.texture.replace(' ', '') + '\r\n')
					file.write('bumpMode=' + textureData.bumpMode + '\r\n')
					if textureData.bumpMode != 'nobump':
						file.write('normalTexture=' + textureData.normalTexture.replace(' ', '') + '\r\n')
						file.write('bumpTexture=' + textureData.bumpTexture.replace('#', '_').replace(' ', '') + '\r\n')
					
					file.write('useDetails=' + textureData.useDetails + '\r\n')
					if textureData.useDetails == 'true' and textureData.detailsTexture != None:
						file.write('detailsTexture=' + textureData.detailsTexture.texture.replace(' ', '') + '\r\n')
						file.write('useDetailsBump=' + textureData.useDetailsBump + '\r\n')
						if textureData.useDetailsBump == 'true':
							file.write('detailsTextureNormal=' + textureData.detailsTexture.normalTexture.replace(' ', '') + '\r\n')
							file.write('detailsTextureBump=' + textureData.detailsTexture.bumpTexture.replace('#', '_').replace(' ', '') + '\r\n')
							file.write('detailsTextureScale=' + str(textureData.detailsTextureScale) + '\r\n')
			finally:
				file.close()
				
			# convert images
			newTextureName = textureData.texture.replace(' ', '')
            # convert base image
			os.system('magick convert \"' + sourceFolder + "\\" + textureData.texture + '.dds\" -set colorspace RGBA \"' + outputFolder + "\\" + newTextureName + '.png\"')
			if textureData.bumpMode != 'nobump':
				newNormalName = textureData.normalTexture.replace(' ', '')
				newBumpName = textureData.bumpTexture.replace('#', '_').replace(' ', '')
			
				os.makedirs(os.path.dirname(outputFolder + "\\" + textureData.bumpTexture), exist_ok=True)
                # convert normal texture
				os.system('magick convert \"' + sourceFolder + "\\" + textureData.normalTexture + '.dds\" -set colorspace RGBA -separate -swap 0,3 -swap 1,2 -combine \"' + outputFolder + "\\" + newNormalName + '.png\"')
                # convert bump texture and move alpha to red
				os.system('magick convert \"' + sourceFolder + "\\" + textureData.bumpTexture + '.dds\" -set colorspace RGBA -separate -swap 0,3 -combine \"' + outputFolder + "\\" + newBumpName + '.png\"')
                # copy normal texture alpha to bump texture
				os.system('magick convert \"' + outputFolder + "\\" + newBumpName + '.png\" \"' + outputFolder + "\\" + newNormalName + '.png\" -compose CopyOpacity -composite \"' + outputFolder + "\\" + newBumpName + '.png\"')
                # move bump texture alpha to blue and remove alpha channel
				os.system('magick convert \"' + outputFolder + "\\" + newBumpName + '.png\" -set colorspace RGBA -separate -swap 1,3 -combine -alpha off \"' + outputFolder + "\\" + newBumpName + '.png\"')
                # remove alpha channel from normal texture
				os.system('magick convert \"' + outputFolder + "\\" + newNormalName + '.png\" -alpha off \"' + outputFolder + "\\" + newNormalName + '.png\"')



print("Parse stalker textures script finished")
