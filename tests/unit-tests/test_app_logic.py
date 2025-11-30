import pytest
from freezegun import freeze_time
import app_logic


@pytest.mark.parametrize("places", [-1, 0])
def test_validate_places_less_than_one(places):
    result, message = app_logic.validate_places(places, 12, 12)
    assert result is False
    assert message == "A non-valid number of places required. Booking failed!"


@pytest.mark.parametrize("places", [13, 20, 50])
def test_validate_places_more_than_12(places):
    result, message = app_logic.validate_places(places, 50, 50)
    assert result is False
    assert message == "No more than 12 places allowed per club. Booking failed!"


@pytest.mark.parametrize("places, club_points", [(5, 4), (7, 1), (11, 10)])
def test_validate_places_more_than_points(places, club_points):
    result, message = app_logic.validate_places(places, club_points, 12)
    assert result is False
    assert message == "Unable to book more places than the points available. Booking failed!"


@pytest.mark.parametrize("places, available", [(1, 0), (11, 10), (12, 5)])
def test_validate_places_more_than_spots_available(places, available):
    result, message = app_logic.validate_places(places, 12, available)
    assert result is False
    assert message == "Not enough spots available. Booking failed!"


def test_validate_places_correct():
    result, message = app_logic.validate_places(5, 10, 12)
    assert result is True
    assert message is None


@freeze_time("2025-11-30 12:00:00")
def test_is_competition_in_past_no(mocker):
    result = app_logic.is_competition_in_past("2025-12-20 14:00:00")
    assert result is False


@freeze_time("2025-11-30 12:00:00")
def test_is_competition_in_past_yes(mocker):
    result = app_logic.is_competition_in_past("2025-11-20 14:00:00")
    assert result is True
