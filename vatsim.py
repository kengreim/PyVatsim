import requests
import constants
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import re
from dataclasses import dataclass
import pprint

@dataclass
class Flightplan:
    flight_rules: str
    aircraft: str
    aircraft_faa: str
    aircraft_short: str
    departure: str
    arrival: str
    alternate: str
    cruise_tas: int
    altitude: int
    deptime: datetime
    enroute_time: timedelta
    fuel_time: timedelta
    remarks: str
    route: str
    revision_id: int
    assigned_transponder: str

    @classmethod
    def from_api_json(cls, json_dict, api):

        if json_dict is None:
            return None
        
        args = json_dict
        # print(fp_json)
        # Vatsim API returns strings for some numeric values, so cast them
        args['cruise_tas'] = int(args['cruise_tas'])

        # Some altitudes are filed as feet, others are filed as FL. Convert all to feet
        try:
            args['altitude'] = int(args['altitude'])
        except ValueError as e:
            m = re.match(r'FL([0-9]*)', args['altitude'])
            if m is not None:
                args['altitude'] = int(m.group(1)) * 100
            # else: the altitude is malformed, leave as the string that API returned

        # Create datetime for filed departure time, and ensure that departure time is in the future
        now = datetime.now(timezone.utc)
        try: 
            args['deptime'] = datetime(now.year, now.month, now.day, int(args['deptime'][:2]), int(args['deptime'][2:]), tzinfo=timezone.utc)
            
            # if prefile:
            #     # TODO -- need to fix this logic, prefiles could have departure times in the past that shouldn't be updated, need some kind of rollover logic. Maybe check 2 hours from now
            #     if args['deptime'] < now:
            #         args['deptime'] += timedelta(days=1)
            #         print(args['deptime']) # TODO -- we can delete

        except ValueError as e:
            pass # if the deptime is malformed and we can't create a datetime, leave as the string that API returned

        # Create timedeltas to represent filed enroute_time and fuel time
        args['enroute_time'] = timedelta(hours=int(args['enroute_time'][:2]), minutes=int(args['enroute_time'][2:]))
        args['fuel_time'] = timedelta(hours=int(args['fuel_time'][:2]), minutes=int(args['fuel_time'][2:]))
        
        return cls(**args)


@dataclass
class Server:
    ident: str
    hostname_or_ip: str
    location: str
    name: str
    clients_connection_allowed: bool
    client_connections_allowed: bool
    is_sweatbox: bool


@dataclass
class Pilot:
    cid: int
    name: str
    callsign: str
    server: Server
    pilot_rating: int # todo -- update
    latitude: float
    longitude: float
    altitude: int
    groundspeed: int
    transponder: str
    heading: int
    qnh_i_hg: float
    qnh_mb: int
    flight_plan: Flightplan
    logon_time: datetime
    last_updated: datetime

    @classmethod
    def from_api_json(cls, json_dict, api):
        args = json_dict
        # TODO: Pilot Rating lookup
        args['flight_plan'] = Flightplan.from_api_json(args['flight_plan'], api)
        args['logon_time'] = VatsimLiveAPI.parse_timestampstr(args['logon_time'])
        args['last_updated'] = VatsimLiveAPI.parse_timestampstr(args['last_updated'])

        # add a field for time online? Maybe as post_init on class itself

        return cls(**args)


@dataclass
class NameTable:
    id: int
    short: str
    long: str

    @classmethod
    def from_api_json(cls, json_dict, api=None):
        return cls(**json_dict)


@dataclass
class Rating(NameTable):
    pass

@dataclass
class Facility(NameTable):
    pass

@dataclass
class PilotRating(NameTable):
    short_name: str
    long_name: str
    
    @classmethod
    def from_api_json(cls, json_dict, api=None):
        json_dict['short'] = json_dict['short_name']
        json_dict['long'] = json_dict['long_name']
        return cls(**json_dict)


@dataclass
class Metar:
    field: str
    time: datetime
    condition: str
    raw_text: str

    @classmethod
    def from_raw_text(cls, raw_text, api=None):
        r = re.compile(r'(?P<field>[\S]+?) (?P<time>[0-9]{6}Z?) (?P<condition>.*)')
        try:
            m = r.match(raw_text)
            today = datetime.now(timezone.utc).today()
            args = {
                'field'     : m.group('field'),
                'condition' : m.group('condition'),
                'raw_text'  : raw_text,
                'time'      : datetime(today.year, today.month, int(m.group('time')[:2]), int(m.group('time')[2:4]), int(m.group('time')[4:6]))
            }
        except:
            args = {
                'field'     : raw_text[:4],
                'condition' : None,
                'raw_text'  : raw_text,
                'time'      : None
            }
        return cls(**args)


@dataclass
class Controller:
    cid: int
    name: str
    callsign: str
    frequency: str
    facility: Facility
    rating: Rating
    server: Server
    visual_range: int
    text_atis: str
    last_updated: datetime
    logon_time: datetime

    @classmethod
    def from_api_json(cls, json_dict, api):
        args = json_dict
        if args['text_atis'] is not None:
            args['text_atis'] = '\n'.join(args['text_atis'])
        args['logon_time'] = VatsimLiveAPI.parse_timestampstr(args['logon_time'])
        args['last_updated'] = VatsimLiveAPI.parse_timestampstr(args['last_updated'])
        # TODO -- facility and rating and server join
        return cls(**args)


@dataclass
class ATIS(Controller):
    atis_code: str

    @classmethod
    def from_api_json(cls, json_dict, api):
        args = json_dict
        if args['text_atis'] is not None:
            args['text_atis'] = ' '.join(args['text_atis'])
        args['logon_time'] = VatsimLiveAPI.parse_timestampstr(args['logon_time'])
        args['last_updated'] = VatsimLiveAPI.parse_timestampstr(args['last_updated'])
        # TODO -- facility and rating and server join
        return cls(**args)


class TTLCache():
    def __init__(self, ttl):
        self.ttl = ttl
        self._cache = {}
        self._last_update_time = {}

    def is_stale(self, key='_ALL'):
        now = datetime.now(timezone.utc)
        if key not in self._cache:
            return True
        else:
            return self._cache[key] == None or (now - self._last_update_time[key]).total_seconds() > self.ttl
    
    def get_cached(self, key='_ALL'):
        return self._cache[key] # should probably add logic checks for stale data here, maybe throw error if attempting to get cached data older than TTL
    
    def cache(self, val, key='_ALL'):
        self._cache[key] = val
        self._last_update_time[key] = datetime.now(timezone.utc)


class VatsimEndpoints():

    def __init__(self, status_url=constants.STATUS_JSON_URL):

        try:
            r = requests.get(status_url)
        except Exception as e:
            raise
        
        j = r.json()
        self.status_json_url = status_url
        self.data_json_url = j['data']['v3'][0]
        self.transceivers_json_url = j['data']['transceivers'][0]
        self.servers_json_url = j['data']['servers'][0]
        self.servers_sweatbox_json_url = j['data']['servers_sweatbox'][0]
        self.user_php_url = j['user'][0]
        self.metar_php_url = j['metar'][0]


class VatsimLiveAPI():

    def __init__(self, vatsim_endpoints=None, DATA_TTL=15, METAR_TTL=60):  # change timeouts to be configurable here
        if vatsim_endpoints is None:
            self.vatsim_endpoints = VatsimEndpoints()
        else:
            assert isinstance(vatsim_endpoints, VatsimEndpoints)
            self.vatsim_endpoints = vatsim_endpoints

        self._metar_cache = TTLCache(METAR_TTL)
        self._data_cache  = TTLCache(DATA_TTL)

    def _fetch_metars(self, fields):
        if isinstance(fields, str):
            field_str = fields
        else:
            field_str = ','.join(fields)
        url = self.vatsim_endpoints.metar_php_url + '?' + urlencode({'id': field_str})
        # print(url)
        try:
            r = requests.get(url)
        except Exception as e:
            raise
        metars = {}
        for row in r.text.splitlines():
            metar = Metar.from_raw_text(row)
            metars[metar.field] = metar

        return metars
    
    def _fetch_conn_data(self):
        try:
            r = requests.get(self.vatsim_endpoints.data_json_url)
        except Exception as e:
            raise
            
        json = r.json()

        fetch_configs = {
            'facilities'    : (Facility, 'from_api_json', 'id'),
            'ratings'       : (Rating, 'from_api_json', 'id'),
            'pilot_ratings' : (PilotRating, 'from_api_json', 'id'),
            'pilots'        : (Pilot, 'from_api_json', 'cid'),
            'controllers'   : (Controller, 'from_api_json', 'cid'),
            'atis'          : (ATIS, 'from_api_json', 'callsign')  
        }

        result = {}
        for name, (obj, constructor, key) in fetch_configs.items():
            result[name] = {}
            for i in json[name]:
                j = getattr(obj, constructor)(i, self)
                result[name][getattr(j, key)] = j

        pp = pprint.PrettyPrinter()
        #pp.pprint(result)
        
        # # TODO -- fetch and handle prefiles, facility levels, controller ratings, pilot ratings

        # print(len(pilots.keys()))
        # print(len(json['atis']))
        # print(len(atises.keys()))
        # return pilots
    
    @staticmethod
    def parse_timestampstr(timestr):
        try:
            d = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ')
            d = d.replace(tzinfo=timezone.utc)
            return d
        except ValueError as e:
            pass
        
        try:
            d = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S.%fZ')
            d = d.replace(tzinfo=timezone.utc)
            return d
        except ValueError as e:
            pass
        
        try:
            d = datetime.strptime(timestr[:26], '%Y-%m-%dT%H:%M:%S.%f')
            d = d.replace(tzinfo=timezone.utc)
            return d
        except ValueError as e:
            raise
 
    def metars(self, fields=None, force_update=False):
        if fields is None:
            if force_update or self._metar_cache.is_stale():
                new_metars = self._fetch_metars('all')
                self._metar_cache.cache(new_metars)
                return new_metars
            else:
                # print('cache alive')
                return self._metar_cache.get_cached()
        else:
            pass # TODO: handle list of fields. Need to construc the fresh list and the stale list separately then fetch as needed

    def metar(self, field, force_update=False):
        if force_update or self._metar_cache.is_stale(field):
            metar = self._fetch_metars(field)
            self._metar_cache.cache(metar, field)
            return metar
        else:
            #print('cache alive')
            # print(self._metar_cache._last_update_time)
            return self._metar_cache.get_cached(field)

    def pilot(self, cid=None, callsign=None):
        # maybe change the arguments to some kind of dictionary, or have callsign be a regex
        if cid is None and callsign is None:
            return None
        elif cid is not None:
            pass
        else:
            # If we are here we know that callsign is not None
            pass

    def pilots(self, cids=None, callsigns=None): #callsign should be regex? and what would CID do here, just allow return a single result as list?
        pass

    def controller(self, cid=None, callsign=None):
        if cid is None and callsign is None:
            return None
        elif cid is not None:
            pass
        else:
            # If we are here we know that callsign is not None
            pass

    def controllers(self): #cid or callsign? same as pilots above
        pass

    def atises(self): #cid or callsigns
        pass

    def atis(self): # cid will not be unique here, but callsign will
        pass

    # all, active only, or prefile only
    def flight_plans(self):
        pass


# if __name__ == '__main__':

api = VatsimLiveAPI()
# m = api.metars()
# n = api.metars()
#k = api.metars()
#n = api.metar('KSFO')
#print(k)
api._fetch_conn_data()
#print(api._parse_pilot(x))

# r = requests.get('https://data.vatsim.net/v3/vatsim-data.json')
# x = r.json()['pilots'][0]['flight_plan']
# print(x)
# y = Flightplan(**x)
# print(y)
# print(y.remarks)