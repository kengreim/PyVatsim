from __future__ import annotations # Required for type annotations to use forward reference
import requests
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CacheOlderThanTTL(Exception):
    pass


# Constants
STATUS_JSON_URL = 'https://status.vatsim.net/status.json'

class UpdateMode(Enum):
    NOUPDATE = 0
    NORMAL = 1
    FORCE = 2


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
    def from_api_json(cls, json_dict: dict, api: Optional[VatsimLiveAPI] = None) -> PilotRating:
        json_dict['short'] = json_dict['short_name']
        json_dict['long'] = json_dict['long_name']
        return cls(**json_dict)

@dataclass
class MilitaryRating(PilotRating):
    pass


@dataclass
class Server:
    """
    Dataclass for VATSIM FSD Server details
    """
    ident: str
    hostname_or_ip: str
    location: str
    name: str
    clients_connection_allowed: bool
    client_connections_allowed: bool
    is_sweatbox: bool

    @classmethod
    def from_api_json(cls, json_dict: dict, api: Optional[VatsimLiveAPI] = None) -> Server:
        args = json_dict
        args['clients_connection_allowed'] = bool(args['clients_connection_allowed'])
        return cls(**args)


@dataclass
class Flightplan:
    """
    Dataclass for flight plans filed on the VATSIM network
    """
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
    def from_api_json(cls, json_dict: dict, api: Optional[VatsimLiveAPI] = None) -> Flightplan:

        if json_dict is None:
            return None

        args = json_dict

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

        # Create datetime for filed departure time
        now = datetime.now(timezone.utc)
        try:
            # TODO -- still need to clean up the departure time logic
            # Start with naive interpretation that the hours and minutes belong to today
            args['deptime'] = datetime(now.year, now.month, now.day, int(args['deptime'][:2]), int(args['deptime'][2:]), tzinfo=timezone.utc)

            # If we find a DOF field in the remarks, that gives us the exact year, time and day. Although this might not always be right...
            # r = re.search(r'DOF/([0-9]{6})', args['remarks'])
            # if r is not None:
            #     print(r.group())
            #     d = datetime.strptime(r.group(), '%y%m%d')
            #     print(d)
            #     args['deptime']= args['deptime'].replace(year=d.year, month=d.month, day=d.day)

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
class PrefiledPilot:
    """
    Dataclass for describing a pilot with a filed flight plan
    """
    cid: int
    name: str
    callsign: str
    flight_plan: Flightplan
    last_updated: datetime

    @classmethod
    def from_api_json(cls, json_dict: dict, api: VatsimLiveAPI) -> PrefiledPilot:
        args = json_dict
        args['flight_plan'] = Flightplan.from_api_json(args['flight_plan'], api)
        args['last_updated'] = VatsimLiveAPI.parse_timestampstr(args['last_updated'])
        return cls(**args)


@dataclass
class ActivePilot:
    """
    Dataclass for a pilot who is actively on the network
    """
    cid: int
    name: str
    callsign: str
    server: Server
    pilot_rating: PilotRating
    military_rating: MilitaryRating
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
    def from_api_json(cls, json_dict: dict, api: VatsimLiveAPI) -> ActivePilot:
        args = json_dict
        args['pilot_rating'] = api.pilot_rating(args['pilot_rating'])
        args['server'] = api.server(args['server'])
        args['flight_plan'] = Flightplan.from_api_json(args['flight_plan'], api)
        args['logon_time'] = VatsimLiveAPI.parse_timestampstr(args['logon_time'])
        args['last_updated'] = VatsimLiveAPI.parse_timestampstr(args['last_updated'])

        # add a field for time online? Maybe as post_init on class itself

        return cls(**args)


@dataclass
class Metar:
    """
    Dataclass for storing METARs
    """
    field: str
    time: datetime
    condition: str
    raw_text: str

    @classmethod
    def from_raw_text(cls, raw_text: str, api: Optional[VatsimLiveAPI] = None) -> Metar:
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
    """
    Dataclass for defining an active Air Traffic Controller
    """
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
    def from_api_json(cls, json_dict: dict, api: VatsimLiveAPI) -> Controller:
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
    """
    Dataclass for defining a controller's ATIS connection
    """
    atis_code: str

    @classmethod
    def from_api_json(cls, json_dict: dict, api: VatsimLiveAPI) -> ATIS:
        args = json_dict
        if args['text_atis'] is not None:
            args['text_atis'] = ' '.join(args['text_atis'])
        args['logon_time'] = VatsimLiveAPI.parse_timestampstr(args['logon_time'])
        args['last_updated'] = VatsimLiveAPI.parse_timestampstr(args['last_updated'])
        args['facility'] = api.facility(args['facility'])
        args['rating'] = api.controller_rating(args['rating'])
        args['server'] = api.server(args['server'])
        return cls(**args)


class TTLCache:
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
        # TODO - should probably add logic checks for stale data here, maybe throw error if attempting to get cached data older than TTL
        now = datetime.now(timezone.utc)
        diff = (now - self._last_update_time[key]).total_seconds()
        if diff > ttl:
            raise CacheOlderThanTTL("Cached data has expired")
        return self._cache[key] if key in self._cache else None

    def cache(self, val, key='_ALL'):
        self._cache[key] = val
        self._last_update_time[key] = datetime.now(timezone.utc)


class VatsimEndpoints:

    def __init__(self, status_url: str = STATUS_JSON_URL) -> None:

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


class VatsimLiveAPI:

    def __init__(self, vatsim_endpoints: VatsimEndpoints = None, DATA_TTL: int = 15, METAR_TTL: int = 60) -> None:
        if vatsim_endpoints is None:
            self.vatsim_endpoints = VatsimEndpoints()
        else:
            assert isinstance(vatsim_endpoints, VatsimEndpoints)
            self.vatsim_endpoints = vatsim_endpoints

        self._metar_cache = TTLCache(METAR_TTL)
        self._conndata_cache  = TTLCache(DATA_TTL)
        self._server_last_updated = None

    def _fetch_metars(self, fields):
        if isinstance(fields, str):
            field_str = fields
        else:
            field_str = ','.join(fields)
        url = self.vatsim_endpoints.metar_php_url + '?' + urlencode({'id': field_str})
        try:
            r = requests.get(url)
        except Exception as e:
            raise
        metars = {}
        for row in r.text.splitlines():
            metar = Metar.from_raw_text(row)
            metars[metar.field] = metar

        return metars

    def _fetch_and_cache_conn_data(self):
        try:
            r = requests.get(self.vatsim_endpoints.data_json_url)
        except Exception as e:
            raise

        json = r.json()

        # Before we do anything, check the timestamp for the last server-side update. If the server-side data hasn't updated, 
        # we don't need to parse everything (even though the data might be "stale" according to our TTL)
        server_update_dt = self.parse_timestampstr(json['general']['update_timestamp'])
        if self._server_last_updated == server_update_dt:
            return # Don't cache anything here as we don't want to reset our internal TTL

        # If we have new server-side data, update timestamp and cache raw result with '_ALL' special key
        self._server_last_updated = server_update_dt
        self._conndata_cache.cache(json)

        # Fetch configs map the json dict to
        #   1. class method that takes the json dict and returns an instance of the class
        #   2. instance variable that will be used as the unique key in the resulting stored dict
        # 
        # Ex. for each i in json['facilities'], store f = Facility.from_api_json(i) in new dict with f.id as the key
        # Order matters here. Have to fetch the lookup tables first so that we can join objects properly
        fetch_configs = {
            'facilities'       : (Facility.from_api_json,         'id'),
            'ratings'          : (Rating.from_api_json,           'id'),
            'pilot_ratings'    : (PilotRating.from_api_json,      'id'),
            'military_ratings' : (MilitaryRating.from_api_json,   'id'),
            'servers'          : (Server.from_api_json,           'ident'),
            'pilots'           : (ActivePilot.from_api_json,      'cid'),
            'prefiles'         : (PrefiledPilot.from_api_json,    'cid'),
            'controllers'      : (Controller.from_api_json,       'cid'),
            'atis'             : (ATIS.from_api_json,             'callsign')
        }

        # Iterate over fetch configs to parse json into objects and cache
        for name, (constructor, key) in fetch_configs.items():
            result = {}
            for i in json[name]:
                j = constructor(i, self)
                result[getattr(j, key)] = j
            self._conndata_cache.cache(result, name)

    @staticmethod
    def parse_timestampstr(timestr: str) -> datetime:
        try:
            d = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ')
            return d.replace(tzinfo=timezone.utc)
        except ValueError as e:
            pass

        try:
            d = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S.%fZ')
            return d.replace(tzinfo=timezone.utc)
        except ValueError as e:
            pass

        try:
            d = datetime.strptime(timestr[:26], '%Y-%m-%dT%H:%M:%S.%f')
            return d.replace(tzinfo=timezone.utc)
        except ValueError as e:
            raise

    @staticmethod
    def wrap_if_single(input):
        return [input] if isinstance(input, (str, int)) else input

    def _update_metars_if_needed(self, key='_ALL', update_mode=UpdateMode.NORMAL):
        match update_mode:
            case UpdateMode.NOUPDATE:
                return
            case UpdateMode.NORMAL:
                if self._metar_cache.is_stale(key):
                    new_metars = self._fetch_metars('all')
                    self._metar_cache.cache(new_metars)
            case UpdateMode.FORCE:
                new_metars = self._fetch_metars('all')
                self._metar_cache.cache(new_metars)

    def metars(self, fields: Optional[str | list[str]] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[str, Metar]:
        self._update_metars_if_needed(update_mode=update_mode)
        if fields is None:
            return self._metar_cache.get_cached()
        else:
            # TODO -- can probably be smarter about not requesting all metars from API, but for now this works
            r = {k: v for k, v in self._metar_cache.get_cached().items() if k in VatsimLiveAPI.wrap_if_single(fields)}
            return r if len(r.keys()) > 0 else None

    def metar(self, field: str, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | Metar:
        self._update_metars_if_needed(update_mode=update_mode) # could only request 1 filed instead of all
        cached = self._metar_cache.get_cached()
        return cached[field] if field in cached else None

    def _update_conndata_if_needed(self, key='_ALL', update_mode=UpdateMode.NORMAL):
        match update_mode:
            case UpdateMode.NOUPDATE:
                return
            case UpdateMode.NORMAL:
                if self._conndata_cache.is_stale(key):
                    self._fetch_and_cache_conn_data()
            case UpdateMode.FORCE:
                self._fetch_and_cache_conn_data()

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

    def _return_list_filtered_cid_or_callsign(self, cache_key, cids=None, callsigns=None, update_mode=UpdateMode.NORMAL):
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

    def _return_single_filtered_cid_or_callsign(self, cache_key, cid=None, callsign=None, update_mode=UpdateMode.NORMAL):
        if cid is not None:
            return self._return_single_exact_match(cache_key, cid, update_mode)
        elif callsign is not None:
            def filter(v):
                return getattr(v, 'callsign') == callsign
            f = self._return_filtered(cache_key, filter, update_mode)
            return f[list(f.keys())[0]] if f is not None else None
        else:
            return None

    def _return_single_exact_match(self, cache_key, val_key, update_mode):
        self._update_conndata_if_needed(update_mode=update_mode)
        r = self._conndata_cache.get_cached(cache_key)
        return r[val_key] if val_key in r else None

    def pilot(self, cid: Optional[int] = None, callsign: Optional[str] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | ActivePilot:
        return self._return_single_filtered_cid_or_callsign('pilots', cid, callsign, update_mode)

    def pilots(self, cids: Optional[int | list[int]] = None, callsigns: Optional[str | list[str]] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[int, ActivePilot]:
        return self._return_list_filtered_cid_or_callsign('pilots', cids, callsigns, update_mode)

    def prefiled_pilot(self, cid: Optional[int] = None, callsign: Optional[str] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | PrefiledPilot:
        return self._return_single_filtered_cid_or_callsign('prefiles', cid, callsign, update_mode)

    def prefiled_pilots(self, cids: Optional[int | list[int]] = None, callsigns: Optional[str | list[str]] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[int, PrefiledPilot]:
        return self._return_list_filtered_cid_or_callsign('prefiles', cids, callsigns, update_mode)

    def controller(self, cid: Optional[int] = None, callsign: Optional[str] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | Controller:
        return self._return_single_filtered_cid_or_callsign('controllers', cid, callsign, update_mode)

    def controllers(self, cids: Optional[int | list[int]] = None, callsigns: Optional[str | list[str]] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[int, Controller]:
        return self._return_list_filtered_cid_or_callsign('controllers', cids, callsigns, update_mode)

    def atis(self, callsign: Optional[str] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | ATIS:
        return self._return_single_exact_match('atis', callsign, update_mode)

    def atises(self, cids: Optional[int | list[int]] = None, callsigns: Optional[str | list[str]] = None, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[str, ATIS]:
        return self._return_list_filtered_cid_or_callsign('atis', cids, callsigns, update_mode)

    def pilot_ratings(self, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[int, PilotRating]:
        return self._return_whole('pilot_ratings', update_mode)

    def pilot_rating(self, id: int, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | PilotRating:
        return self._return_single_exact_match('pilot_ratings', id, update_mode)

    def facilities(self, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[int, Facility]:
        return self._return_whole('facilities', update_mode)

    def facility(self, id: int, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | Facility:
        return self._return_single_exact_match('facilities', id, update_mode)

    def controller_ratings(self, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[int, Rating]:
        return self._return_whole('ratings', update_mode)

    def controller_rating(self, id: int, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | Rating:
        return self._return_single_exact_match('ratings', id, update_mode)

    def servers(self, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | dict[str, Server]:
        return self._return_whole('servers', update_mode)

    def server(self, ident_str: str, update_mode: UpdateMode = UpdateMode.NORMAL) -> None | Server:
        return self._return_single_exact_match('servers', ident_str, update_mode)

    # TODO: function that can return all, only active or only prefiled flightplans
    # def flight_plans(self):
    #     pass
