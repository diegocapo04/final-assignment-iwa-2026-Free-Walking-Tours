from datetime import datetime, date, timedelta

def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()

def parse_time(time_string):
    return datetime.strptime(time_string, "%H:%M").time()

def combine_date_and_time(date_string, time_string):
    reservation_date = parse_date(date_string)
    reservation_time = parse_time(time_string)
    return datetime.combine(reservation_date, reservation_time)

def get_tour_end_datetime(tour_date, start_time, duration_minutes):
    start_datetime = combine_date_and_time(tour_date, start_time)
    end_datetime = start_datetime + timedelta(minutes=float(duration_minutes))
    return end_datetime

def intervals_overlap(start_a, end_a, start_b, end_b):
    return start_a < end_b and end_a > start_b

def is_valid_date_for_schedule(tour_date, schedules):
    """
    schedules: list of rows with:
    - weekday (0=Monday, ..., 6=Sunday)
    - start_time
    """
    selected_date = parse_date(tour_date)
    selected_weekday = selected_date.weekday()

    for schedule in schedules:
        if schedule["weekday"] == selected_weekday:
            return True

    return False

def get_start_time_for_date(tour_date, schedules):
    """
    Returns the start_time associated with the weekday of the selected date.
    Assumption: for each weekday, there is at most one schedule for the tour.
    """
    selected_date = parse_date(tour_date)
    selected_weekday = selected_date.weekday()

    for schedule in schedules:
        if schedule["weekday"] == selected_weekday:
            return schedule["start_time"]

    return None

def get_available_dates_for_tour(schedules, days_ahead=30):
    """
    Generates the next bookable dates for a tour in the next N days.
    Returns a list of dictionaries:
    {
        "date": "YYYY-MM-DD",
        "weekday": "Monday",
        "start_time": "10:00"
    }
    """
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    available_dates = []

    today = date.today()
    for offset in range(days_ahead + 1):
        current_date = today + timedelta(days=offset)
        current_weekday = current_date.weekday()

        for schedule in schedules:
            if schedule["weekday"] == current_weekday:
                available_dates.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "weekday": weekday_names[current_weekday],
                    "start_time": schedule["start_time"]
                })

    return available_dates

def can_reserve_tour_date(tour, tour_date, schedules):
    """
    Verify that the selected tour_date:
    - is valid for the tour's schedule;
    - is in the future (after the current date and time).;
    """
    if not is_valid_date_for_schedule(tour_date, schedules):
        return False, "The selected date is not available for this tour."

    start_time = get_start_time_for_date(tour_date, schedules)
    if start_time is None:
        return False, "Invalid tour date."

    start_datetime = combine_date_and_time(tour_date, start_time)

    if start_datetime <= datetime.now():
        return False, "The selected tour date must be in the future."

    return True, None

def has_overlapping_reservation(existing_reservations, new_tour_date, new_start_time, new_duration_minutes):
    """
    existing_reservations: list of active reservations for the participant with:
    - tour_date
    - start_time
    - duration_minutes
    """
    new_start = combine_date_and_time(new_tour_date, new_start_time)
    new_end = new_start + timedelta(minutes=float(new_duration_minutes))

    for reservation in existing_reservations:
        existing_start = combine_date_and_time(reservation["tour_date"], reservation["start_time"])
        existing_end = existing_start + timedelta(minutes=float(reservation["duration_minutes"]))

        if intervals_overlap(new_start, new_end, existing_start, existing_end):
            return True

    return False

def is_tour_date_past(tour_date, start_time):
    """A tour occurrence is 'past' once its start datetime is before now."""
    start_datetime = combine_date_and_time(tour_date, start_time)
    return start_datetime < datetime.now()


def group_guide_reservations_by_date(reservation_rows):
    """
    Aggregates a flat list of active reservations (with participant names) into
    one entry per scheduled date, used in the guide profile.
    Each entry: date, start_time, total_people, reservations (list of names).
    """
    grouped = {}

    for row in reservation_rows:
        key = (row["tour_date"], row["start_time"])
        if key not in grouped:
            grouped[key] = {
                "tour_date": row["tour_date"],
                "start_time": row["start_time"],
                "total_people": 0,
                "reservations": []
            }
        grouped[key]["total_people"] += row["total_people"]
        grouped[key]["reservations"].append({
            "participant_name": f"{row['first_name']} {row['last_name']}",
            "people": row["total_people"]
        })

    return [grouped[key] for key in sorted(grouped.keys())]


def can_cancel_reservation(tour_date, start_time):
    """
    A reservation can be cancelled only if at least 24 hours remain before the tour starts.
    """
    start_datetime = combine_date_and_time(tour_date, start_time)
    deadline = start_datetime - timedelta(hours=24)

    return datetime.now() <= deadline


def get_total_people_from_guest_lists(extra_first_names, extra_last_names):
    """
    The reservation always includes the logged-in participant (1 person).
    Valid additional participants are those where both first name and last name are provided.
    """
    valid_guests = []
    total_rows = min(len(extra_first_names), len(extra_last_names))

    for i in range(total_rows):
        first_name = extra_first_names[i].strip()
        last_name = extra_last_names[i].strip()

        if first_name and last_name:
            valid_guests.append({
                "first_name": first_name,
                "last_name": last_name
            })
        elif first_name or last_name:
            return None, None, "Each additional participant must include both first name and last name."

    total_people = 1 + len(valid_guests)

    if total_people < 1 or total_people > 4:
        return None, None, "A reservation can include from 1 to 4 people."

    return total_people, valid_guests, None