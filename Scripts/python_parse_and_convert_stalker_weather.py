import sys


class TimeData(object):
	hours = 0
	minutes = 0
	seconds = 0
	
	def __str__(self):
		 return "(Hours={0},Minutes={1},Seconds={2},Frames=0)".format(self.hours, self.minutes, self.seconds)

class ColorData(object):
	r = 0
	g = 0
	b = 0
	a = 0

	def __str__(self):
		 return "(R={0},G={1},B={2},A=1.0)".format(self.r, self.g, self.b)

class WeatherData(object):
	startTime = TimeData()
	skyCubemap = ''
	skyColor = ColorData()
	sunLongitude = 90
	sunAltitude = 0
	sunLightIntensity = 2.0
	sunLightColor = ColorData()
	skyLightColor = ColorData()
	fogColor = ColorData()
	rainColor = ColorData()
	rainIntensity = 0

	def __str__(self):
		 return "(StartTime={0},SkyCubemap={1},SkyColor={2},SunLongitude={3},SunAltitude={4},SunLightIntensity={5},SunLightColor={6},SkyLightColor={7},FogColor={8},RainColor={9},RainIntensity={10})".format(self.startTime, self.skyCubemap, self.skyColor, self.sunLongitude, self.sunAltitude, self.sunLightIntensity, self.sunLightColor, self.skyLightColor, self.fogColor, self.rainColor, self.rainIntensity)


def parseColorData(rawText):
	colorData = ColorData()
	colorData.r = float(rawText[0:8])
	colorData.g = float(rawText[10:18])
	colorData.b = float(rawText[20:28])
	average = (colorData.r + colorData.g + colorData.b) / 3
	
	return colorData, average


if len(sys.argv) < 3:
	print("Please provide path to source weather file and weather name")
	sys.exit()

print("Parse stalker weather script started")

sourceFile = sys.argv[1]
prefix = sys.argv[2]

sourceFile = open(sourceFile, 'r') 
lines = sourceFile.readlines() 

weatherDatas = []
for line in lines: 
	line = line.strip()
	if len(line) > 0:
		if line[0] == '[':
			weatherData = WeatherData()
			weatherData.startTime = TimeData()
			weatherData.startTime.hours = int(line[1:3])
			weatherData.startTime.minutes = int(line[4:6])
			weatherData.startTime.seconds = int(line[7:9])
			
			weatherDatas.append(weatherData)
		else:
			propertyName = line[0:33].strip()
			propertyValue = line[34:].strip()
			
			if propertyName == 'sky_texture':
				propertyValue = propertyValue[propertyValue.rfind("\\") + 1:]
				weatherData.skyCubemap = "TextureCube'\"/Game/Levels/Weather/SkyTextures/{0}/{0}_{1}.{0}_{1}\"'".format(prefix, propertyValue)
			
			elif propertyName == 'sky_color':
				weatherData.skyColor, _ = parseColorData(propertyValue)
				
			elif propertyName == 'sun' and (propertyValue == "none" or propertyValue == "gradient" or propertyValue == "gradient1" or propertyValue == "sun_rise_cloudy" or propertyValue == "default"):
				weatherData.sunLightIntensity = 0.0
				weatherData.sunLightColor = ColorData()
				weatherData.sunLightColor.r = 0.0
				weatherData.sunLightColor.g = 0.0
				weatherData.sunLightColor.b = 0.0
				
			elif propertyName == 'sun_longitude':
				weatherData.sunLongitude = float(propertyValue[0:8])
				
			elif propertyName == 'sun_altitude':
				weatherData.sunAltitude = -float(propertyValue[0:8]) - 90
				
			elif propertyName == 'sun_color':
				if weatherData.sunLightIntensity > 0:
					weatherData.sunLightColor, _ = parseColorData(propertyValue)
				else:
					weatherData.sunLightColor = ColorData()
					weatherData.sunLightColor.r = 0.0
					weatherData.sunLightColor.g = 0.0
					weatherData.sunLightColor.b = 0.0
				#weatherData.sunLightColor, weatherData.sunLightIntensity = parseColorData(propertyValue)
				#weatherData.sunLightIntensity *= 2
				
			elif propertyName == 'ambient_color':
				weatherData.skyLightColor, _ = parseColorData(propertyValue)
				
			elif propertyName == 'fog_color':
				weatherData.fogColor, _ = parseColorData(propertyValue)
			
			elif propertyName == 'rain_color':
				weatherData.rainColor, _ = parseColorData(propertyValue)
			
			elif propertyName == 'rain_density':
				weatherData.rainIntensity = int(float(propertyValue[0:8]) * 2000)
			
			#print(weatherData)

print("(" + ''.join([str(weatherData) + "," for weatherData in weatherDatas])[:-1] + ")")

print("Parse stalker weather script finished")
