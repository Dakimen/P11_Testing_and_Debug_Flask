import json
from flask import render_template, url_for
import pytest
from unittest.mock import mock_open
import copy

from tests.conftest import app, test_data, mock_db
import server


@pytest.mark.usefixtures("test_data", "app", "mock_db")
class TestServerIntegration:

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

    def test_showSummary_unknown_email(self, client):
        email = "fakemail@club1.co"
        response = client.post(
            "/showSummary",
            data={
                "email": email
            }
        )
        error_msg = "Sorry, that email wasn&#39;t found."
        assert error_msg in response.get_data(as_text=True)

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
        competition = server.competitions[2]

        response = client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club['name'],
                "places": "11"
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
                "places": "8"
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
        club = server.clubs[1]  # has 4 points
        competition = server.competitions[0]
        points_expected = 2
        client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club['name'],
                "places": "2"
            }
        )
        assert server.clubs[1]['points'] == points_expected

    def test_pointsBoard(self, client):
        response = client.get('/points')
        expected_html = render_template('points.html', clubs=server.clubs)
        assert response.data.decode() == expected_html
        assert "Club Test" in response.get_data(as_text=True)

    def test_purchasePlaces_more_than_12(self, client):
        competition = server.competitions[0]
        club = server.clubs[0]
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club['name'],
                "places": "13"
            }
        )
        html = response.get_data(as_text=True)
        assert "No more than 12 places allowed per club. Booking failed!" in html

    def test_purcasePlaces_no_more_than_club_points(self, client):
        competition = server.competitions[2]
        club = server.clubs[1]  # 4 points
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": competition["name"],
                "club": club["name"],
                "places": "10"  # Still within 12 points limit
            }
        )
        html = response.get_data(as_text=True)
        assert "Unable to book more places than the points available. Booking failed!" in html

    def test_booking_page_html_club_point_limit_applied(self, client):
        competition = server.competitions[2]
        club = server.clubs[1]  # has 4 points
        url = url_for('book', competition=competition['name'], club=club['name'])
        response = client.get(url)
        html_to_find = '<input type="number" name="places" id="" min="1" max="4" step="1"/>'
        assert html_to_find in response.get_data(as_text=True)

    def test_booking_page_12_point_limit_applied(self, client):
        competition = server.competitions[2]
        club = server.clubs[0]  # has 30 points, above limit
        url = url_for('book', competition=competition['name'], club=club['name'])
        response = client.get(url)
        html_to_find = '<input type="number" name="places" id="" min="1" max="12" step="1"/>'
        assert html_to_find in response.get_data(as_text=True)

    def test_logout(self, client):
        response = client.get('/logout', follow_redirects=True)
        html = render_template('index.html')
        assert html == response.data.decode()
