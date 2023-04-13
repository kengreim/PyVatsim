import pprint

import vatsim as vatsim

# if __name__ == '__main__':

api = vatsim.VatsimLiveAPI()
# m = api.metars()
# n = api.metars()
# k = api.metars()
# n = api.metar('KSFO')
# print(k)
# api._fetch_conn_data()
# print(api.facility(5))
# print(api.facility(21))
# print(api.server('USA-WEST'))
# print(api.atis('EDDS_ATIS'))
# x = api.atises(callsigns=['KMCO', 'KIAD'])
# print(x)
pp = pprint.PrettyPrinter(indent=1)
# pp.pprint(api.pilots(callsigns='WAT'))
# pp.pprint(api.pilot(callsign='WAT2992'))
# pp.pprint(api.controller(callsign='IND_CTR'))

# print(api._parse_pilot(x))

# r = requests.get('https://data.vatsim.net/v3/vatsim-data.json')
# x = r.json()['pilots'][0]['flight_plan']
# print(x)
# y = Flightplan(**x)
# print(y)
# print(y.remarks)


p = api.pilots()
for cid, pilot in p.items():
    if pilot.flight_plan is not None:
        print(
            "%s departed from %s and is going to %s at current altitude %i connected to server %s"
            % (
                pilot.callsign,
                pilot.flight_plan.departure,
                pilot.flight_plan.arrival,
                pilot.altitude,
                pilot.server.ident,
            )
        )
    else:
        print(
            "%s is at current altitude %i with no flight plan"
            % (pilot.callsign, pilot.altitude)
        )
