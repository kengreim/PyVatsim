import pytest

"""
TODO: Fix the structure as this shouldnt really be needed to allow for tests to run.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def vatsim_data_general_blob() -> dict[str, any]:
    return {
        "version": 3,
        "reload": 1,
        "update": "20230411161343",
        "update_timestamp": "2023-04-11T16:13:43.9537663Z",
        "connected_clients": 1350,
        "unique_users": 1268
    }


@pytest.fixture
def vatsim_data_pilots_blob() -> list[dict[str, any]]:
    return [
        {
            "cid": 5555555,
            "name": "Alex Doe EGKK",
            "callsign": "BAW32",
            "server": "UK",
            "pilot_rating": 0,
            "latitude": 24.02507,
            "longitude": 82.52637,
            "altitude": 29977,
            "groundspeed": 476,
            "transponder": "5741",
            "heading": 286,
            "qnh_i_hg": 29.9,
            "qnh_mb": 1013,
            "flight_plan": {
                "flight_rules": "I",
                "aircraft": "B77W/H-VGDW/C",
                "aircraft_faa": "H/B77W/L",
                "aircraft_short": "B77W",
                "departure": "VHHH",
                "arrival": "EGLL",
                "alternate": "EGSS",
                "cruise_tas": "509",
                "altitude": "34100",
                "deptime": "1214",
                "enroute_time": "1415",
                "fuel_time": "1622",
                "remarks": "Pilot Remarks",
                "route": "BEKOL3A/07R BEKOL A461 IDUMA W22 TEPID W90 POU A599 LXI W148 XSJ W146 GULOT A599 LINSO/N0500F340 A599 CTG B465 CEA G450 JJS B209 KKJ L333 MERUN L750 RANAH B449 DUKAN L850 ADEKI N644 ROLIN UN644 GAKSU DCT ODERO DCT DEGET DCT OGVUN DCT MOVOS DCT RENKA DCT BATTY L608 LOGAN",
                "revision_id": 6,
                "assigned_transponder": "5741"
            },
            "logon_time": "2023-04-11T11:45:21.4513207Z",
            "last_updated": "2023-04-11T16:13:42.5134797Z"
        },
        {
            "cid": 4556677,
            "name": "Patrick Doe CYYZ",
            "callsign": "KLM64B",
            "server": "CANADA",
            "pilot_rating": 0,
            "latitude": 17.92323,
            "longitude": 92.49153,
            "altitude": 34933,
            "groundspeed": 480,
            "transponder": "3621",
            "heading": 94,
            "qnh_i_hg": 29.84,
            "qnh_mb": 1011,
            "flight_plan": {
                "flight_rules": "I",
                "aircraft": "A320/M-SDE3FGHIRWY/LB1",
                "aircraft_faa": "A320/L",
                "aircraft_short": "A320",
                "departure": "OPKC",
                "arrival": "VYYY",
                "alternate": "VYNT",
                "cruise_tas": "453",
                "altitude": "35000",
                "deptime": "1300",
                "enroute_time": "0351",
                "fuel_time": "0527",
                "remarks": "Pilot Remarks",
                "route": "DANGI1C DANGI DCT TELEM DCT AAE N895 IKOSI/N0453F370 N895 SAGOD DCT OKIKO OKIKO1A",
                "revision_id": 3,
                "assigned_transponder": "0000"
            },
            "logon_time": "2023-04-11T11:46:01.5562155Z",
            "last_updated": "2023-04-11T16:13:42.5799969Z"
        }
    ]


@pytest.fixture
def vatsim_data_atis_blob() -> list[dict[str, any]]:
    return [
        {
            "cid": 1122334,
            "name": "Steve Doe",
            "callsign": "EDDK_ATIS",
            "frequency": "132.125",
            "facility": 4,
            "rating": 2,
            "server": "GERMANY",
            "visual_range": 0,
            "atis_code": "T",
            "text_atis": [
                "COLOGNE BONN INFORMATION T MET REPORT TIME 1550 .. AUTOMATED",
                "WEATHER MESSAGE .. EXPECT ILS APPROACH .. RUNWAYS IN USE 24 ..",
                "RUNWAY 14L/32R CLSD DUE TO WORK IN PROGRESS ..TRL 60 .. WIND 280",
                "DEGREES 14 KNOTS VARIABLE BETWEEN 250 AND 330 DEGREES ..",
                "VISIBILITY 10 KILOMETERS OR MORE .. LIGHT SHOWERS OF RAIN",
                "NO CLOUD BASE AVAILABLE TEMPERATURE 14 DEW POINT 2 .. QNH 1014",
                ".. TREND BECOMING WIND 210 DEGREES 5 KNOTS .. COLOGNE BONN",
                "INFORMATION T OUT ATTENTION!",
                "DEPARTURE FREQUENCY FOR ALL DEPARTING AIRCRAFT IS UNICOM",
                "ON FREQUENCY 122.800"
            ],
            "last_updated": "2023-04-11T16:13:21.8150075Z",
            "logon_time": "2023-04-11T11:01:56.0983382Z"
        },
        {
            "cid": 4433221,
            "name": "Joe Doe",
            "callsign": "LGAV_ATIS",
            "frequency": "136.125",
            "facility": 4,
            "rating": 3,
            "server": "GERMANY2",
            "visual_range": 50,
            "atis_code": "H",
            "text_atis": [
                "HERE IS ATHINA VENIZELOS ATIS INFORMATION H. RECORDED AT 1550Z.",
                "APP TYPE ILS Z. LDG RWY 03R. TAKE OFF RWY 03L. . TRANSITION",
                "LEVEL FL 105. 35006KT 330V050. 9999. . . FEW030. 16. 02. Q1009.",
                ". CONCENTRATION OF BIRDS IN THE AIRPORT VICINITY. ADVISE ON",
                "INITIAL CONTACT YOU HAVE LISTENED TO INFORMATION H."
            ],
            "last_updated": "2023-04-11T16:13:27.9893166Z",
            "logon_time": "2023-04-11T13:00:27.9962805Z"
        },
    ]


@pytest.fixture
def vatsim_data_controller_blob() -> list[dict[str, any]]:
    return [
        {
            "cid": 1122334,
            "name": "Steve Doe",
            "callsign": "EDDK_TWR",
            "frequency": "124.975",
            "facility": 4,
            "rating": 2,
            "server": "GERMANY2",
            "visual_range": 50,
            "text_atis": [
                "Koeln/Bonn Tower",
                "ATIS Info"
            ],
            "last_updated": "2023-04-11T16:13:21.8151445Z",
            "logon_time": "2023-04-11T10:58:47.4890896Z"
        },
        {
            "cid": 4433221,
            "name": "Joe Doe",
            "callsign": "LGAV_TWR",
            "frequency": "118.625",
            "facility": 4,
            "rating": 3,
            "server": "GERMANY2",
            "visual_range": 25,
            "text_atis": [
                "Venizelos Tower - PDC Datalink available at [LGAV]",
                "ATIS on 136.125",
            ],
            "last_updated": "2023-04-11T16:13:34.4763517Z",
            "logon_time": "2023-04-11T12:59:10.7839569Z"
        },
    ]


@pytest.fixture
def vatsim_data_server_blob() -> list[dict[str, any]]:
    return [
        {
            "ident": "USA-EAST",
            "hostname_or_ip": "159.65.171.192",
            "location": "New York, USA",
            "name": "USA-EAST",
            "clients_connection_allowed": 1,
            "client_connections_allowed": True,
            "is_sweatbox": False
        },
        {
            "ident": "CANADA",
            "hostname_or_ip": "159.203.44.51",
            "location": "Toronto, Canada",
            "name": "CANADA",
            "clients_connection_allowed": 1,
            "client_connections_allowed": True,
            "is_sweatbox": False
        },
    ]


@pytest.fixture
def vatsim_data_prefile_blob() -> list[dict[str, any]]:
    return [
        {
            "cid": 1111111,
            "name": "Prefile User One",
            "callsign": "CNS949",
            "flight_plan": {
                "flight_rules": "I",
                "aircraft": "PC12/L-SDFGRWY/S",
                "aircraft_faa": "PC12/L",
                "aircraft_short": "PC12",
                "departure": "KACK",
                "arrival": "KHPN",
                "alternate": "KPHL",
                "cruise_tas": "266",
                "altitude": "12000",
                "deptime": "1345",
                "enroute_time": "0049",
                "fuel_time": "0238",
                "remarks": "PBN/D2 DOF/230411 REG/N949AF OPR/CNS PER/B RMK/TCAS SIMBRIEF /V/",
                "route": "MVY SEY V34 CREAM BDR BDR288 RYMES",
                "revision_id": 1,
                "assigned_transponder": "7002"
            },
            "last_updated": "2023-04-11T13:16:47.6318459Z"
        },
        {
            "cid": 2222222,
            "name": "Prefile User Two",
            "callsign": "N8184Q",
            "flight_plan": {
                "flight_rules": "I",
                "aircraft": "B350/L-SBGRW/S",
                "aircraft_faa": "B350/L",
                "aircraft_short": "B350",
                "departure": "KMBS",
                "arrival": "KHRX",
                "alternate": "KLBB",
                "cruise_tas": "306",
                "altitude": "26000",
                "deptime": "1410",
                "enroute_time": "0311",
                "fuel_time": "0405",
                "remarks": "PBN/B2C2D2O2S1S2 DOF/230411 REG/N8184Q EET/KZAU0014 KZKC0115 KZAB0245 PER/B RMK/TCAS SIMBRIEF /V/",
                "route": "SLLAP OBK IRK J26 ICT PNH",
                "revision_id": 1,
                "assigned_transponder": "0562"
            },
            "last_updated": "2023-04-11T13:43:17.2226956Z"
        }
    ]


@pytest.fixture
def vatsim_data_facilities_blob() -> list[dict[str, any]]:
    return [
        {
            "id": 0,
            "short": "OBS",
            "long": "Observer"
        },
        {
            "id": 1,
            "short": "FSS",
            "long": "Flight Service Station"
        },
        {
            "id": 2,
            "short": "DEL",
            "long": "Clearance Delivery"
        },
        {
            "id": 3,
            "short": "GND",
            "long": "Ground"
        },
        {
            "id": 4,
            "short": "TWR",
            "long": "Tower"
        },
        {
            "id": 5,
            "short": "APP",
            "long": "Approach/Departure"
        },
        {
            "id": 6,
            "short": "CTR",
            "long": "Enroute"
        }
    ]


@pytest.fixture
def vatsim_data_ratings_blob() -> list[dict[str, any]]:
    return [
        {
            "id": -1,
            "short": "INAC",
            "long": "Inactive"
        },
        {
            "id": 0,
            "short": "SUS",
            "long": "Suspended"
        },
        {
            "id": 1,
            "short": "OBS",
            "long": "Observer"
        },
        {
            "id": 2,
            "short": "S1",
            "long": "Tower Trainee"
        },
        {
            "id": 3,
            "short": "S2",
            "long": "Tower Controller"
        },
        {
            "id": 4,
            "short": "S3",
            "long": "Senior Student"
        },
        {
            "id": 5,
            "short": "C1",
            "long": "Enroute Controller"
        },
        {
            "id": 6,
            "short": "C2",
            "long": "Controller 2 (not in use)"
        },
        {
            "id": 7,
            "short": "C3",
            "long": "Senior Controller"
        },
        {
            "id": 8,
            "short": "I1",
            "long": "Instructor"
        },
        {
            "id": 9,
            "short": "I2",
            "long": "Instructor 2 (not in use)"
        },
        {
            "id": 10,
            "short": "I3",
            "long": "Senior Instructor"
        },
        {
            "id": 11,
            "short": "SUP",
            "long": "Supervisor"
        },
        {
            "id": 12,
            "short": "ADM",
            "long": "Administrator"
        }
    ]


@pytest.fixture
def vatsim_data_pilot_ratings_blob() -> list[dict[str, any]]:
    return [
        {
            "id": 0,
            "short_name": "NEW",
            "long_name": "Basic Member"
        },
        {
            "id": 1,
            "short_name": "PPL",
            "long_name": "Private Pilot License"
        },
        {
            "id": 3,
            "short_name": "IR",
            "long_name": "Instrument Rating"
        },
        {
            "id": 7,
            "short_name": "CMEL",
            "long_name": "Commercial Multi-Engine License"
        },
        {
            "id": 15,
            "short_name": "ATPL",
            "long_name": "Airline Transport Pilot License"
        }
    ]


@pytest.fixture
def vatsim_data_response(
        vatsim_data_general_blob: dict[str, any],
        vatsim_data_pilots_blob: list[dict[str, any]],
        vatsim_data_controller_blob: list[dict[str, any]],
        vatsim_data_atis_blob: list[dict[str, any]],
        vatsim_data_server_blob: list[dict[str, any]],
        vatsim_data_prefile_blob: list[dict[str, any]],
        vatsim_data_facilities_blob: list[dict[str, any]],
        vatsim_data_ratings_blob: list[dict[str, any]],
        vatsim_data_pilot_ratings_blob: list[dict[str, any]],
) -> dict[str, any]:
    """
    This is a stripped down example of the response from
    the vatsim-data.json response URL to be used for writing tests.
    """
    return {
        "general": vatsim_data_general_blob,
        "pilots": vatsim_data_pilots_blob,
        "controllers": vatsim_data_controller_blob,
        "atis": vatsim_data_atis_blob,
        "servers": vatsim_data_server_blob,
        "prefiles": vatsim_data_prefile_blob,
        "facilities": vatsim_data_facilities_blob,
        "ratings": vatsim_data_ratings_blob,
        "pilot_ratings": vatsim_data_pilot_ratings_blob,
    }
