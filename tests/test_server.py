import json
from flask import render_template, url_for
import pytest
from unittest.mock import mock_open
import copy

from tests.conftest import app, test_data
import server


@pytest.fixture
def mock_db(mocker, test_data):
    clubs_copy = copy.deepcopy(test_data["clubs"])
    competitions_copy = copy.deepcopy(test_data["competitions"])

    mocker.patch.object(server, "clubs", clubs_copy)
    mocker.patch.object(server, "competitions", competitions_copy)

    return {"clubs": clubs_copy, "competitions": competitions_copy}


@pytest.mark.usefixtures("test_data", "app", "mock_db")
class TestServer:

    def test_loadClubs(self, test_data, mocker):
        fake_content = json.dumps({"clubs": test_data['clubs']})
        mocker.patch("builtins.open", mock_open(read_data=fake_content))
        result = server.loadClubs()

        assert result == test_data['clubs']

    def test_loadCompetitions(self, test_data, mocker):
        fake_content = json.dumps({"competitions": test_data["competitions"]})
        mocker.patch("builtins.open", mock_open(read_data=fake_content))
        result = server.loadCompetitions()

        assert result == test_data['competitions']

    def test_index_page(self, client, app):
        response = client.get("/")
        assert response.status_code == 200

        expected_html = render_template('index.html')
        assert response.data.decode() == expected_html

    def test_showSummary(self, client, test_data):
        club = test_data['clubs'][0]
        email = club['email']
        competitions = test_data['competitions']
        expected_html = render_template('welcome.html',
                                        club=club,
                                        competitions=competitions)

        response = client.post('/showSummary', data={'email': email})

        assert response.data.decode() == expected_html

    def test_book_if_found(self, client, test_data):
        club = test_data['clubs'][1]
        competition = test_data['competitions'][2]  # Competition date: 2025-12-20 14:00:00

        expected_html = render_template('booking.html', club=club, competition=competition)
        url = url_for("book", competition=competition['name'], club=club['name'])
        response = client.get(url)

        assert response.data.decode() == expected_html

    def test_book_if_not_Competition(self, client, test_data):
        inexistant_competition = {
            "name": "Inexistant Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
            }
        club = test_data['clubs'][1]
        url_not_competition = url_for('book',
                                      competition=inexistant_competition['name'],
                                      club=club['name'])
        response = client.get(url_not_competition)
        html = response.get_data(as_text=True)

        assert "Something went wrong-please try again" in html

    def test_book_if_notClub(self, client, test_data):
        inexistant_club = {
            "name": "Inexistant Club",
            "email": "inexistant@lifting.co",
            "points": "13"
            }
        expected_html_not_club = render_template('index.html')
        competition = test_data['competitions'][0]
        url_not_club = url_for('book', competition=competition['name'],
                               club=inexistant_club['name'])
        response = client.get(url_not_club)

        assert response.data.decode() == expected_html_not_club

    def test_book_past_competition(self, client):
        club = server.clubs[0]
        competition = server.competitions[0]
        url = url_for("book", competition=competition['name'], club=club['name'])
        response = client.get(url)
        html = response.get_data(as_text=True)

        assert "Impossible to book places for a past competition!" in html

    def test_purchasePlaces_too_many(self, client):
        club = server.clubs[0]
        competition = server.competitions[0]

        response = client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club['name'],
                "places": "30"
            }
        )

        html = response.get_data(as_text=True)
        assert "Not enough spots available. Booking failed!" in html

    def test_purchasePlaces(self, client):
        club = server.clubs[0]
        competition = server.competitions[0]

        response = client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club['name'],
                "places": "20"
            }
        )

        html = response.get_data(as_text=True)
        assert "Great-booking complete!" in html

    def test_purchasePlaces_invalid_competition(self, client):
        club = server.clubs[0]

        response = client.post("/purchasePlaces", data={
            "competition": "NOT_A_REAL_COMP",
            "club": club["name"],
            "places": "5",
        })
        html = response.get_data(as_text=True)
        assert "Incorrect form data, invalid competition. Booking failed!" in html

    def test_purchasePlaces_invalid_club(self, client):
        competition = server.competitions[0]

        response = client.post("/purchasePlaces", data={
            "competition": competition["name"],
            "club": "NOT_A_REAL_CLUB",
            "places": "5",
        })
        expected_html = render_template('index.html')
        assert response.data.decode() == expected_html

    def test_purchasePlaces_missing_fields(self, client):
        club = server.clubs[0]
        response = client.post("/purchasePlaces", data={
            "club": club["name"],
            "places": "5",
        })
        html = response.get_data(as_text=True)
        assert "Competition field is missing" in html

        competition = server.competitions[0]
        response = client.post("/purchasePlaces", data={
            "competition": competition["name"],
            "places": "5",
        })
        html = response.data.decode()
        expected_html = render_template('index.html')
        assert html == expected_html

        response = client.post("/purchasePlaces", data={
            "competition": competition["name"],
            "club": club["name"],
        })
        html = response.get_data(as_text=True)
        assert "Number of places field is missing" in html

    @pytest.mark.parametrize("places", ["-2", "two", "0"])
    def test_purchasePlaces_invalidNumber(self, client, places):
        competition = server.competitions[0]
        club = server.clubs[0]
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club['name'],
                "places": places
            }
        )
        html = response.get_data(as_text=True)
        assert "A non-valid number of places required." in html

    def test_purchasePlaces_pointsUpdated(self, client):
        club = server.clubs[0]  # has 13 points
        competition = server.competitions[0]
        points_expected = 5
        client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club['name'],
                "places": "8"
            }
        )
        assert server.clubs[0]['points'] == points_expected

    def test_pointsBoard(self, client):
        response = client.get('/points')
        expected_html = render_template('points.html', clubs=server.clubs)
        assert response.data.decode() == expected_html
        assert "Club Test" in response.get_data(as_text=True)
