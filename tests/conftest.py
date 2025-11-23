import pytest

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
            "points": "13"
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
