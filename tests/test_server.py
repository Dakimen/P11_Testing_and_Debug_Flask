import json
from flask import render_template, url_for
import pytest

from tests.conftest import app
import server


@pytest.fixture(scope="class")
def test_data(request):
    with open('clubs.json') as file:
        clubs = json.load(file)['clubs']

    with open('competitions.json') as file:
        competitions = json.load(file)["competitions"]

    return {'clubs': clubs, 'competitions': competitions}


@pytest.mark.usefixtures("test_data", "app")
class TestServer:

    def test_loadClubs(self, test_data):
        result = server.loadClubs()

        assert result == test_data['clubs']

    def test_loadCompetitions(self, test_data):
        result = server.loadCompetitions()

        assert result == test_data['competitions']

    def test_index_page(self, client, app):
        response = client.get("/")
        assert response.status_code == 200

        with open(f"{app.template_folder}/index.html", encoding="utf-8") as f:
            expected_html = f.read()
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
        competition = test_data['competitions'][0]

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
        competitions = test_data['competitions']
        expected_html_not_competition = render_template('welcome.html',
                                                        club=club,
                                                        competitions=competitions)
        url_not_competition = url_for('book',
                                      competition=inexistant_competition['name'],
                                      club=club['name'])
        response = client.get(url_not_competition)

        assert response.data.decode() == expected_html_not_competition

    def test_book_if_notClub(self, client, test_data):
        inexistant_club = {
            "name": "Inexistant Club",
            "email": "inexistant@lifting.co",
            "points": "13"
            }
        competitions = test_data['competitions']
        expected_html_not_club = render_template('welcome.html',
                                                 club=inexistant_club,
                                                 competitions=competitions)
        competition = test_data['competitions'][0]
        url_not_club = url_for('book', competition=competition['name'],
                               club=inexistant_club['name'])
        response = client.get(url_not_club)

        assert response.data.decode() == expected_html_not_club

    def test_purchasePlaces_too_many(self, client):
        server.competitions[:] = [{
            "name": "TestComp",
            "date": "2025-12-20 12:00:00",
            "numberOfPlaces": "5"
        }]

        server.clubs[:] = [{
            "name": "TestClub",
            "email": "test@example.com",
            "points": "10"
        }]
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": "TestComp",
                "club": "TestClub",
                "places": "10"
            }
        )
        updated = server.competitions[0]
        assert int(updated["numberOfPlaces"]) >= 0
