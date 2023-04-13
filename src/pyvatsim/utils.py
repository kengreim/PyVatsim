import requests

VATSPY_BOUNDARIES_URL = "https://raw.githubusercontent.com/vatsimnetwork/vatspy-data-project/master/Boundaries.geojson"


class VatspyBoundaries:
    def __init__(self, geojson_url: str = VATSPY_BOUNDARIES_URL):
        self._geojson_url = geojson_url
        try:
            r = requests.get(geojson_url)
            self.geojson = r.text
        except:
            raise
