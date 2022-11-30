import pyvatsim
from shapely import geometry
import requests
import geopandas as gpd

# GeoJSON file from the VatSpy Data Project on Github
boundaries = requests.get('https://raw.githubusercontent.com/vatsimnetwork/vatspy-data-project/master/Boundaries.geojson').text
gdf = gpd.read_file(boundaries, driver='GeoJSON').set_index('id')
zoa_poly = gdf.loc['KZOA']['geometry']

api = pyvatsim.VatsimLiveAPI()
for cid, p in api.pilots().items():
    if zoa_poly.contains(geometry.Point(p.longitude, p.latitude)):
        print('%s is within ZOA' % (p.callsign))