# What is PyVatsim?
PyVatsim is a Python library to interact with data from Vatsim's live datafeed, currently located at: http://data.vatsim.net/. It implements Python objects to access the underlying Vatsim data in a Pythonic way, and also parses certain data into developer friendly formats (e.g., timestamp strings into Python datetime objects). 

Because Vatsim's datafeed is updated every ~15 seconds, Py-API supports configurable caching of data from the datafeed so that each access method does not fetch the datafeed (although a "force update" override exists if needed).

# Status
This project is in alpha state. It currently offers full functionality to access the Vatsim live data (with time-based caching support), but
further work is needed in the areas of: documentation, error handling, caching, configurability, testing.

# Installation

The easiest way to install is via pip.
```
pip install pyvatsim
```

Alternatively, you can use the `pyvatsim` folder or `liveapi.py` as a package or single-file module, respectively. Make sure you have the necessary 3rd-party libraries installed with `pip` (at the moment, only `requests` is required).

# How to Develop
Clone the repo and create a new Python virtual environment using `requirements.txt`, which should look something like:
```
git clone https://github.com/kengreim/PyVatsim.git
cd pyvatsim
python3 -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

# Full Documentation
TBD

# Known Issues and Noteworthy Considerations
* Vatsim only supplies departure time (in flightplans) in HHMM format. This could be in the past or future and could be yesterday, today or tomorrow.
    * **Currently**, we assume that all departure times belong to the current day for the purposes of converting the `deptime` string to a Python `datetime` object.
    * **In the future**, we can look for a "DOF" string in the remarks to get the right date. However, in looking at the data, this is not always realsitic (e.g., you will find flightplans with DOF remarks for a date that was months ago)
    * In general, it is best to not rely on the departure time, as they are generally not used on the network

# Possible Todos
* Add support for Vatsim's rest API, which is separate from the live data
* Potentially create utils functions in a separate namespace from the API functions. For example:
    * Pilot's distance from filed departure airport and arrival airport
    * List of all pilots within a GeoJSON-defined boundary
    * List of all pilots within a given distance to a given point

# Examples

## Create API object
Use default caching periods (60 seconds for METARs and 15 seconds for network data)
```python
import pyvatsim
api = pyvatsim.VatsimLiveAPI()
```

## Create API object with different cache TTLs
Configurable with the `DATA_TTL` and `METAR_TTL` arguments, which speciy how long network data and METAR data should be cached (in seconds), respectively
```python
import pyvatsim
# 1 min network data cache and 5 min METAR cache
api = pyvatsim.VatsimLiveAPI(DATA_TTL=60, METAR_TTL=300)
```

## Retrieve all pilots, controllers or ATISes and iterate through them
`pilots()` returns a dictionary of `Pilot` instances with each `Pilot.cid` as the dictionary key

`controllers()` returns a dictionary of `Controller` instances with each `Controller.cid` as the dictionary key

`atises()` returns a dictionary of `ATIS` instances with each `ATIS.callsign` as the dictionary key (`cid` is not unique as one user can host multiple ATISes)
```python
p = api.pilots()
for cid, pilot in p.items():
    print('%s at altitude %d' % (pilot.callsign, pilot.altitude))

c = api.controllers()
for cid, controller in c.items():
    print('%s online at %s with controller information: %s' % (controller.callsign, controller.frequency, controller.text_atis))

a = api.atises()
for callsign, atis in a.items():
    print('Information %s at %s is %s' % (atis.atis_code, callsign[:4], atis.text_atis))
```

## Retrieve a list of pilots, controllers or ATISes based on multiple CIDs
`cids` argument expects either a single integer or a list of integers.

`pilots(cid)` returns a dictionary of `Pilot` instances based on exact CID matches, or `None` if no matches are found

`controllers(cid)` returns a dictionary of `Controller` instances based on exact CID matches, or `None` if no matches are found

`atises(cid)` returns a dictionary of `ATIS` instances based on exact CID matches, or `None` if no matches are found
```python
p = api.pilots(cids=[123456, 234567, 345678])
for cid, pilot in p.items():
    # Do something here

c = api.controllers(cids=[123456, 234567, 345678])
for cid, controller in c.items():
    # Do something here

a = api.atises(cids=[123456, 234567, 345678])
for callsign, atis in a.items():
    # Do something here
```

## Retrieve a list of pilots, controllers or ATISes based on one or more string regular expressions
`callsigns` argument expects either a single string or a list of strings. `callsigns` argument will be ignored if `cids` argument is provided, as in the example above.

`pilots(callsigns)` will evaluate each string as a Python regular expression and return a dictionary of `Pilot` instances where the Pilot's callsign matches one of the given callsign regular expressions (using `re.search`), or `None` if no matches are found

`controllers(callsigns)` will evaluate each string as a Python regular expression and return a dictionary of `Controller` instances where the Controller's callsign matches one of the given callsign regular expressions (using `re.search`), or `None` if no matches are found

`atises(callsigns)` will evaluate each string as a Python regular expression and return a dictionary of `ATIS` instances where the ATIS's callsign matches one of the given callsign regular expressions (using `re.search`), or `None` if no matches are found
```python
p = api.pilots(callsigns=['UAL123', 'UAL', 'SWA'])
for cid, pilot in p.items():
    # Do something here

# Note that last item uses regex to match OAK_CTR, OAK_41_CTR, OAK_44_CTR, etc. but not OAK_GND
c = api.controllers(callsigns=['SFO', 'SJC', 'OAK.*_CTR'])
for cid, controller in c.items():
    # Do something here

# Note that the last item would match KMCO_ATIS, KMCO_D_ATIS and KMCO_A_ATIS if any or all were online
a = api.atises(callsigns=['KSFO', 'KLAX', r'KMCO\S*ATIS'])
for callsign, atis in a.items():
    # Do something here
```

## Retrieve a single pilot, controller or ATIS by Vatsim CID or callsign
`cid` argument expects an integer. `callsign` argument expects a string. . If both `cid` and `callsign` arguments are provided, only `cid` will be used.

`pilot()` returns a single `Pilot` instance based on exact CID or callsign string match (both are unique on the Vatsim network for Pilots) or `None`

`controller()` returns a single `Controller` instance based on exact CID or callsign string match (both are unique on the Vatsim network for Controllers) or `None`

`atis()` returns a single `ATIS` instance based on exact callsign string match or `None`. Note that CID is not used for a single ATIS as a single CID can host multiple ATISes
```python
p1 = api.pilot(cid=123456)
p2 = api.pilot(callsign='UAL123')

c1 = api.controller(cid=123456)
c2 = api.controller(callsign='SFO_TWR')

a1 = api.atis('KSFO_ATIS')
```

## Retrieve all METARs
```python
m = api.metars()
for field, metar in m.items():
    # Do something
```

## Retrieve a subset of METARs
```python
m = api.metars(['KSFO', 'KLAX', 'KSJC'])
for field, metar in m.items():
    # Do something
```

## Retrieve a single METAR
```python
m = api.metar('KSFO')
```

## Access information about a pilot and their flightplan
```python
p = api.pilots()
for cid, pilot in p.items():
    if pilot.flight_plan is not None:
        print('%s departed from %s and is going to %s at current altitude %i' % (pilot.callsign, pilot.flight_plan.departure, pilot.flight_plan.arrival, pilot.altitude))
    else:
        print('%s is at current altitude %i with no flight plan' % (pilot.callsign, pilot.altitude))
```

## Get information about a controller
```python
c = api.controllers()
for cid, controller in c.items():
    print('%s controlling position %s on %s' % (controller.name, controller.callsign, controller.frequency))
```

## Force a request to fetch fresh data, or force a request to use cached data
```python
c = api.controllers(update_mode=pyvatsim.UpdateMode.FORCE)
c = api.controllers(update_mode=pyvatsim.UpdateMode.NOUPDATE)
```

# License
PyVatsim is licensed under the MIT License.
