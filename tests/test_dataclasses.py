from unittest.mock import Mock, create_autospec

import pytest

from src.pyvatsim import Facility, PilotRating, Rating, Server, VatsimLiveAPI


@pytest.fixture
def mocked_vatsim_live_api() -> Mock:
    return create_autospec(VatsimLiveAPI)


class TestFacilityDataclass:
    def test_can_set_facility_class_properties_from_api(
        self, vatsim_data_facilities_blob: list[dict[str, any]]
    ):
        raw_facility = vatsim_data_facilities_blob[0]
        result = Facility.from_api_json(json_dict=raw_facility)

        assert isinstance(result.id, int)
        assert isinstance(result.long, str)
        assert isinstance(result.short, str)

        assert result.id == raw_facility["id"]
        assert result.long == raw_facility["long"]
        assert result.short == raw_facility["short"]

    def test_raises_type_error_if_data_is_missing(
        self, vatsim_data_facilities_blob: list[dict[str, any]]
    ):
        raw_facility = vatsim_data_facilities_blob[0]
        del raw_facility["id"]

        with pytest.raises(TypeError):
            Facility.from_api_json(json_dict=raw_facility)


class TestRatingDataclass:
    def test_can_set_rating_class_properties_from_api(
        self, vatsim_data_ratings_blob: list[dict[str, any]]
    ):
        raw_rating = vatsim_data_ratings_blob[0]
        result = Rating.from_api_json(json_dict=raw_rating)

        assert isinstance(result.id, int)
        assert isinstance(result.long, str)
        assert isinstance(result.short, str)

        assert result.id == raw_rating["id"]
        assert result.long == raw_rating["long"]
        assert result.short == raw_rating["short"]

    def test_raises_type_error_if_data_is_missing(
        self, vatsim_data_ratings_blob: list[dict[str, any]]
    ):
        raw_rating = vatsim_data_ratings_blob[0]
        del raw_rating["id"]

        with pytest.raises(TypeError):
            Rating.from_api_json(json_dict=raw_rating)


class TestPilotRatingDataclass:
    def test_can_set_rating_class_properties_from_api(
        self, vatsim_data_pilot_ratings_blob: list[dict[str, any]]
    ):
        raw_pilot_rating = vatsim_data_pilot_ratings_blob[0]
        result = PilotRating.from_api_json(json_dict=raw_pilot_rating)

        assert isinstance(result.id, int)
        assert isinstance(result.short_name, str)
        assert isinstance(result.long_name, str)
        assert isinstance(result.long, str)
        assert isinstance(result.short, str)

        assert result.id == raw_pilot_rating["id"]
        assert result.short == raw_pilot_rating["short_name"]
        assert result.long == raw_pilot_rating["long_name"]
        assert result.long_name == raw_pilot_rating["long_name"]
        assert result.short_name == raw_pilot_rating["short_name"]

    def test_raises_type_error_if_data_is_missing(
        self, vatsim_data_pilot_ratings_blob: list[dict[str, any]]
    ):
        raw_pilot_rating = vatsim_data_pilot_ratings_blob[0]
        del raw_pilot_rating["id"]

        with pytest.raises(TypeError):
            PilotRating.from_api_json(json_dict=raw_pilot_rating)


class TestServerDataclass:
    def test_can_set_rating_class_properties_from_api(
        self, vatsim_data_server_blob: list[dict[str, any]]
    ):
        raw_server = vatsim_data_server_blob[0]
        result = Server.from_api_json(json_dict=raw_server)

        assert isinstance(result.ident, str)
        assert isinstance(result.hostname_or_ip, str)
        assert isinstance(result.location, str)
        assert isinstance(result.name, str)
        assert isinstance(result.client_connections_allowed, bool)
        assert isinstance(result.clients_connection_allowed, bool)
        assert isinstance(result.is_sweatbox, bool)

        assert result.ident == raw_server["ident"]
        assert result.hostname_or_ip == raw_server["hostname_or_ip"]
        assert result.location == raw_server["location"]
        assert result.name == raw_server["name"]
        assert (
            result.client_connections_allowed
            == raw_server["client_connections_allowed"]
        )
        assert (
            result.clients_connection_allowed
            == raw_server["clients_connection_allowed"]
        )
        assert result.is_sweatbox == raw_server["is_sweatbox"]

    def test_raises_type_error_if_data_is_missing(
        self, vatsim_data_server_blob: list[dict[str, any]]
    ):
        raw_server = vatsim_data_server_blob[0]
        del raw_server["ident"]

        with pytest.raises(TypeError):
            Server.from_api_json(json_dict=raw_server)
