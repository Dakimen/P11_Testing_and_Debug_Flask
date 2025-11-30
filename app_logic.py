from datetime import datetime


def validate_places(places, club_points, comp_places):
    if places <= 0:
        return False, "A non-valid number of places required. Booking failed!"
    if places > 12:
        return False, "No more than 12 places allowed per club. Booking failed!"
    if places > club_points:
        return False, "Unable to book more places than the points available. Booking failed!"
    if places > comp_places:
        return False, "Not enough spots available. Booking failed!"
    return True, None


def is_competition_in_past(date_str):
    comp_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return datetime.now().replace(microsecond=0) > comp_date
