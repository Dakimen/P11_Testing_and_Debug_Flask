import pytest
import copy

import server
from server import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})
    print("SECRET_KEY:", flask_app.config["SECRET_KEY"])
    yield flask_app


@pytest.fixture(scope="class")
def test_data(request):
    clubs = [
        {
            "name": "Club 1",
            "email": "john@club1.co",
            "points": "30"
        },
        {
            "name": "Club Test",
            "email": "admin@clubtests.com",
            "points": "4"
        },
        {
            "name": "She Clubs",
            "email": "kate@sheclubs.co.uk",
            "points": "12"
        }]
    competitions = [
        {
            "name": "New Festival",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Le Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        },
        {
            "name": "December Lifts",
            "date": "2025-12-20 14:00:00",
            "numberOfPlaces": "10"
        },
        ]

    return {'clubs': clubs, 'competitions': competitions}


@pytest.fixture
def mock_db(mocker, test_data):
    clubs_copy = copy.deepcopy(test_data["clubs"])
    competitions_copy = copy.deepcopy(test_data["competitions"])

    mocker.patch.object(server, "clubs", clubs_copy)
    mocker.patch.object(server, "competitions", competitions_copy)

    return {"clubs": clubs_copy, "competitions": competitions_copy}
