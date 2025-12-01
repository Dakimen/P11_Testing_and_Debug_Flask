import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for

import app_logic


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def create_app(clubs_data=None, competitions_data=None):
    app = Flask(__name__)
    app.config.from_object('config')

    app.clubs = clubs_data if clubs_data else loadClubs()
    app.competitions = competitions_data if competitions_data else loadCompetitions()
    return app


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        club = [club for club in app.clubs if club['email'] == request.form['email']][0]
    except IndexError:
        flash("Sorry, that email wasn't found.")
        return render_template('index.html')
    return render_template('welcome.html', club=club, competitions=app.competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in app.clubs if c['name'] == club), None)
    foundCompetition = next((c for c in app.competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        if app_logic.is_competition_in_past(foundCompetition['date']):
            flash("Impossible to book places for a past competition!")
            return render_template('welcome.html', club=club, competitions=app.competitions)
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    elif not foundCompetition:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=app.competitions)
    else:
        return render_template('index.html')


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')
    places_str = request.form.get('places')

    club = next((c for c in app.clubs if c['name'] == club_name), None)
    allowed, template, msg = app_logic.validate_request(competition_name, club_name, places_str)
    if not allowed:
        if msg is None or club is None:
            return render_template(template)
        flash(msg)
        return render_template(template, club=club, competitions=app.competitions)

    competition = next((c for c in app.competitions if c['name'] == competition_name), None)
    if club is None:
        return render_template('index.html')
    if competition is None:
        flash("Incorrect form data, invalid competition. Booking failed!")
        return render_template('welcome.html', club=club, competitions=app.competitions)

    try:
        placesRequired = int(places_str)
    except (TypeError, ValueError):
        flash("A non-valid number of places required. Booking failed!")
        return render_template('welcome.html', club=club, competitions=app.competitions)

    validated, message = app_logic.validate_places(placesRequired,
                                                   int(club['points']),
                                                   int(competition['numberOfPlaces']))
    if not validated:
        flash(message)
    else:
        club['points'] = int(club['points']) - placesRequired
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=app.competitions)


@app.route('/points')
def pointsBoard():
    return render_template('points.html', clubs=app.clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
