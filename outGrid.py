from supermercado import burntiles
from glob import glob
from socket import timeout
import json, mercantile, urllib, time, os, sys, random
from osgeo import ogr, osr

start = time.time()

zoomList = [156412, 78206, 39103, 19551, 9776, 4888, 2444, 1222, 610.984, 305.492, 152.746, 76.373, 38.187, 19.093, 9.547, 4.773, 2.387, 1.193, 0.596, 0.298]
def getTiles(geojsonFile, zoom, folder):
	with open(geojsonFile) as ofile:
		geojson = json.loads(ofile.read())

	# extrem = burntiles.find_extrema(geojson["features"])
	# mercantile.tiles(extrem[0], extrem[1], extrem[2], extrem[3], [zoom], truncate=False)

	data = burntiles.burn(geojson["features"], zoom)
	millis = int(round(time.time() * 1000))
	for r in data:
		# time.sleep(0.3)
		l = r.tolist()
		bound = mercantile.xy_bounds(l[0], l[1], l[2])
		fileName = str(l[0]) + "_" + str(l[1])
		# OSM url
		url = "http://c.tile.openstreetmap.org/{2}/{0}/{1}.png".format(str(l[0]), str(l[1]), str(l[2]), millis)

		# case use timeout for url
		# tile = urllib.urlopen(url, timeout=10)
		tile = urllib.urlopen(url)
		code = tile.getcode()
		if code != 204:
			image = open(folder + '/' + fileName + '.png', "wb")
			image.write(tile.read())
			image.close()

			f = open(folder + '/' + fileName + '.wld', 'w')
			f.write(str(zoomList[zoom]) + '\n0.0\n0.0\n' + str(zoomList[zoom]*(-1)) + '\n')
			point = mercantile.ul(l[0], l[1], l[2])
		
			x1 = bound.left
			y1 = bound.top

			f.write(str(x1) + '\n')
			f.write(str(y1) + '\n')
			f.close()

			gdalwarp = os.system('gdalwarp -s_srs EPSG:3857 -t_srs EPSG:3857 ' + folder + '/' + fileName + '.png ' + folder + '/' + fileName + '.tif')

			os.remove(folder + '/' + fileName + '.png')

	gdalbuildvrt = os.system('gdalbuildvrt -srcnodata "0 0 0" -vrtnodata "0 0 0" ' + folder + '/out.vrt ' + folder + '/*.tif')
	for tif in glob(folder + '/*.tif'):
		os.remove(tif)
	gdalwarp = os.system('gdalwarp -s_srs EPSG:3857 -t_srs EPSG:3857 ' + folder + '/out.vrt ' + folder + '/out.tiff')
	os.remove(folder + '/out.vrt')
	for wld in glob(folder + '/*.wld'):
		os.remove(wld)

if __name__ == '__main__':
	args = sys.argv[1:]
	start = time.time()
	getTiles(args[0], int(args[1]), args[2])
	end = time.time()
	print end - start
