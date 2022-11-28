import requests
import constants
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import re
from dataclasses import dataclass
import pprint
from enum import Enum

class UpdateMode(Enum):
    NOUPDATE = 0
    NORMAL = 1
    FORCE = 2

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

    @classmethod
    def from_api_json(cls, json_dict, api):
        args = json_dict
        args['clients_connection_allowed'] = bool(args['clients_connection_allowed'])
        return cls(**args)

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
        args['pilot_rating'] = api.pilot_rating(args['pilot_rating'])
        args['server'] = api.server(args['server'])
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
        args['facility'] = api.facility(args['facility'])
        args['rating'] = api.controller_rating(args['rating'])
        args['server'] = api.server(args['server'])
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
        args['facility'] = api.facility(args['facility'])
        args['rating'] = api.controller_rating(args['rating'])
        args['server'] = api.server(args['server'])
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
        if key in self._cache:
            return self._cache[key] # should probably add logic checks for stale data here, maybe throw error if attempting to get cached data older than TTL
        else:
            return None

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
        self._conndata_cache  = TTLCache(DATA_TTL)

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

        # Have to fetch the lookup tables first so that we can join objects properly
        fetch_configs = {
            'facilities'    : (Facility, 'from_api_json', 'id'),
            'ratings'       : (Rating, 'from_api_json', 'id'),
            'pilot_ratings' : (PilotRating, 'from_api_json', 'id'),
            'servers'       : (Server, 'from_api_json', 'ident'),
            'pilots'        : (Pilot, 'from_api_json', 'cid'),
            'controllers'   : (Controller, 'from_api_json', 'cid'),
            'atis'          : (ATIS, 'from_api_json', 'callsign') 
            # TODO -- fetch prefiles
        }

        self._conndata_cache.cache(json) # Cache raw result with '_ALL' special key

        for name, (obj, constructor, key) in fetch_configs.items():
            result = {}
            for i in json[name]:
                j = getattr(obj, constructor)(i, self)
                result[getattr(j, key)] = j
            self._conndata_cache.cache(result, name)
    
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
            
    @staticmethod
    def wrap_if_single(input):
        return [input] if isinstance(input, (str, int)) else input
    
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

    def _update_conndata_if_needed(self, key='_ALL', update_mode=UpdateMode.NORMAL):
        match update_mode:
            case UpdateMode.NOUPDATE:
                return
            case UpdateMode.NORMAL:
                if self._conndata_cache.is_stale(key):
                    print('updating here')
                    self._fetch_conn_data()
                    print('done updating')
            case UpdateMode.FORCE:
                self._fetch_conn_data()

    def pilot(self, cid=None, callsign=None, update_mode=UpdateMode.NORMAL):
        if cid is not None:
            return self._return_single_exact_match('pilots', cid, update_mode)
        elif callsign is not None:
            def filter(v):
                return getattr(v, 'callsign') == callsign
            f = self._return_filtered('pilots', filter, update_mode)
            return f[list(f.keys())[0]]
        else:
            return None

    def pilots(self, cids=None, callsigns=None, update_mode=UpdateMode.NORMAL): #callsign should be regex? and what would CID do here, just allow return a single result as list?
        return self._return_filtered_cid_or_callsign('pilots', cids, callsigns, update_mode)

    def controller(self, cid=None, callsign=None, update_mode=UpdateMode.NORMAL):
        if cid is not None:
            return self._return_single_exact_match('controllers', cid, update_mode)
        elif callsign is not None:
            def filter(v):
                return getattr(v, 'callsign') == callsign
            f = self._return_filtered('controllers', filter, update_mode)
            return f[list(f.keys())[0]]
        else:
            return None

    def controllers(self, cids=None, callsigns=None, update_mode=UpdateMode.NORMAL): #cid or callsign? same as pilots above
        return self._return_filtered_cid_or_callsign('controllers', cids, callsigns, update_mode)

    def atis(self, callsign, update_mode=UpdateMode.NORMAL): # cid will not be unique here, but callsign will
        return self._return_single_exact_match('atis', callsign, update_mode)

    def atises(self, cids=None, callsigns=None, update_mode=UpdateMode.NORMAL): #cid or callsigns
        return self._return_filtered_cid_or_callsign('atis', cids, callsigns, update_mode)

    # all, active only, or prefile only
    def flight_plans(self):
        # TODO -- update
        pass
        
    def _return_whole(self, cache_key, update_mode):
        self._update_conndata_if_needed(update_mode=update_mode)
        return self._conndata_cache.get_cached(cache_key)
    
    def _return_filtered(self, cache_key, filter_func, update_mode):
        self._update_conndata_if_needed(update_mode=update_mode)
        r = {}
        for k, v in self._conndata_cache.get_cached(cache_key).items():
            if filter_func(v):
                r[k] = v
        return r if len(r.keys()) > 0 else None
    
    def _return_filtered_cid_or_callsign(self, cache_key, cids=None, callsigns=None, update_mode=UpdateMode.NORMAL):
        if cids is not None:
            def filter(v):
                return getattr(v, 'cid') in VatsimLiveAPI.wrap_if_single(cids)
            return self._return_filtered(cache_key, filter, update_mode)
        elif callsigns is not None:
            def filter(v):
                return any([re.search(i, getattr(v, 'callsign')) for i in VatsimLiveAPI.wrap_if_single(callsigns)])
            return self._return_filtered(cache_key, filter, update_mode)
        else:
            return self._return_whole(cache_key, update_mode)
    
    def _return_single_exact_match(self, cache_key, val_key, update_mode):
        self._update_conndata_if_needed(update_mode=update_mode)
        r = self._conndata_cache.get_cached(cache_key)
        if val_key in r:
            return r[val_key]
        else:
            return None
    
    def pilot_ratings(self, update_mode=UpdateMode.NORMAL):
        return self._return_whole('pilot_ratings', update_mode)

    def pilot_rating(self, id, update_mode=UpdateMode.NORMAL):
        return self._return_single_exact_match('pilot_ratings', id, update_mode)

    def facilities(self, update_mode=UpdateMode.NORMAL):
        return self._return_whole('facilities', update_mode)

    def facility(self, id, update_mode=UpdateMode.NORMAL):
        return self._return_single_exact_match('facilities', id, update_mode)

    def controller_ratings(self, update_mode=UpdateMode.NORMAL):
        return self._return_whole('ratings', update_mode)

    def controller_rating(self, id, update_mode=UpdateMode.NORMAL):
        return self._return_single_exact_match('ratings', id, update_mode)

    def servers(self, update_mode=UpdateMode.NORMAL):
        return self._return_whole('servers', update_mode)
    
    def server(self, ident_str, update_mode=UpdateMode.NORMAL):
        return self._return_single_exact_match('servers', ident_str, update_mode)




# if __name__ == '__main__':

api = VatsimLiveAPI()
# m = api.metars()
# n = api.metars()
#k = api.metars()
#n = api.metar('KSFO')
#print(k)
#api._fetch_conn_data()
#print(api.facility(5))
#print(api.facility(21))
#print(api.server('USA-WEST'))
#print(api.atis('EDDS_ATIS'))
#x = api.atises(callsigns=['KMCO', 'KIAD'])
#print(x)
pp = pprint.PrettyPrinter(indent = 1)
#pp.pprint(api.pilots(callsigns='WAT'))
#pp.pprint(api.pilot(callsign='WAT2992'))
#pp.pprint(api.controller(callsign='IND_CTR'))

#print(api._parse_pilot(x))

# r = requests.get('https://data.vatsim.net/v3/vatsim-data.json')
# x = r.json()['pilots'][0]['flight_plan']
# print(x)
# y = Flightplan(**x)
# print(y)
# print(y.remarks)


p = api.pilots()
for cid, pilot in p.items():
    if pilot.flight_plan is not None:
        print('%s departed from %s and is going to %s at current altitude %i' % (pilot.callsign, pilot.flight_plan.departure, pilot.flight_plan.arrival, pilot.altitude))
    else:
        print('%s is at current altitude %i with no flight plan' % (pilot.callsign, pilot.altitude))