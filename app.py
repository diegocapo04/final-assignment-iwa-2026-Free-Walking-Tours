from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import UnidentifiedImageError
from models import user_from_row
from dao import user_dao, tour_dao, tour_schedule_dao, tour_stop_dao, tour_photo_dao, reservation_dao, reservation_guest_dao, tour_report_dao
from utils import auth_utils, valid_utils, photo_utils, reservation_utils

UPLOAD_FOLDER = "static/uploads/tour_photos"
TOUR_PHOTO_WIDTH = 1200
TOUR_PHOTO_HEIGHT = 800
REPORT_PHOTO_WIDTH = 1200
REPORT_PHOTO_HEIGHT = 800

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret key for the final project"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."

@login_manager.user_loader
def load_user(user_id):
    row = user_dao.get_user_by_id(user_id)
    return user_from_row(row)

def _parse_schedules(weekdays, form):
    """Builds the list of {weekday, start_time} from the submitted form.
    Each selected weekday has its start time in the field 'start_time_<weekday>'."""
    schedules = []
    for day in weekdays:
        start_time = form.get(f"start_time_{day}", "").strip()
        schedules.append({"weekday": int(day), "start_time": start_time})
    return schedules

@app.route("/")
def index():
    # Public, filterable list of tours (homepage). Filters come from the query string.
    language = request.args.get("language", "").strip()
    duration_min_raw = request.args.get("duration_min", "").strip()
    duration_max_raw = request.args.get("duration_max", "").strip()
    date_raw = request.args.get("date", "").strip()

    language = language if language in valid_utils.ALLOWED_LANGUAGES else None
    duration_min = int(duration_min_raw) if duration_min_raw.isdigit() else None
    duration_max = int(duration_max_raw) if duration_max_raw.isdigit() else None

    weekday = None
    if date_raw:
        try:
            weekday = reservation_utils.parse_date(date_raw).weekday()
        except ValueError:
            weekday = None

    tours = tour_dao.get_tours(language=language, duration_min=duration_min, duration_max=duration_max, weekday=weekday)

    return render_template(
        "index.html",
        tours=tours,
        allowed_languages=valid_utils.ALLOWED_LANGUAGES,
        filters={
            "language": language or "",
            "duration_min": duration_min_raw,
            "duration_max": duration_max_raw,
            "date": date_raw,
        },
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    redirect_response = auth_utils.redirect_if_authenticated()
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password")
        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("login.html")
        
        user_row = user_dao.get_user_by_email(email)
        if user_row is None or not check_password_hash(user_row["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        
        user = user_from_row(user_row)
        login_user(user)
        flash("Logged in successfully.", "success")
        return auth_utils.redirect_by_role()
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    redirect_response = auth_utils.redirect_if_authenticated()
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        role = request.form.get("role", "participant").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        languages = request.form.getlist("languages")

        role_error = valid_utils.validate_role(role)
        if role_error:
            flash(role_error, "warning")
            return render_template("register.html", allowed_languages=valid_utils.ALLOWED_LANGUAGES, selected_role=role)
        
        error = valid_utils.validate_basic_registration(first_name, last_name, email, password, confirm_password)
        if error:
            flash(error, "warning")
            return render_template("register.html", allowed_languages=valid_utils.ALLOWED_LANGUAGES, selected_role=role)
        
        if user_dao.email_exists(email):
            flash("Email is already registered.", "danger")
            return render_template("register.html", allowed_languages=valid_utils.ALLOWED_LANGUAGES, selected_role=role)
        
        if role == "guide":
            language_error = valid_utils.validate_guide_languages(languages)
            if language_error:
                flash(language_error, "warning")
                return render_template("register.html", allowed_languages=valid_utils.ALLOWED_LANGUAGES, selected_role=role)
            
            password_hash = generate_password_hash(password)
            user_id = user_dao.create_guide(first_name, last_name, email, password_hash)
            user_dao.add_guide_languages(user_id, languages)
            user_row = user_dao.get_user_by_id(user_id)
            user = user_from_row(user_row)

            login_user(user)
            flash("Guide registration completed successfully.", "success")
            return redirect(url_for("guide_profile"))
        
        password_hash = generate_password_hash(password)
        user_id = user_dao.create_participant(first_name, last_name, email, password_hash)

        user_row = user_dao.get_user_by_id(user_id)
        user = user_from_row(user_row)

        login_user(user)
        flash("Participant registration completed successfully.", "success")
        return redirect(url_for("participant_profile"))

    return render_template("register.html", allowed_languages=valid_utils.ALLOWED_LANGUAGES, selected_role="participant")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/participant/profile")
@login_required
def participant_profile():
    redirect_response = auth_utils.require_role("participant")
    if redirect_response:
        return redirect_response

    reservations = reservation_dao.get_active_reservations_by_participant(current_user.id)
    reservation_with_guests = []
    for reservation in reservations:
        guests = reservation_guest_dao.get_guests_by_reservation(reservation["id"])
        cancelable = False
        if reservation["status"] == "active":
            cancelable = reservation_utils.can_cancel_reservation(reservation["tour_date"], reservation["start_time"])
        
        reservation_with_guests.append({
            "reservation": reservation,
            "guests": guests,
            "cancelable": cancelable
        })

    return render_template("participant_profile.html", reservation_with_guests=reservation_with_guests)

@app.route("/guide/profile")
@login_required
def guide_profile():
    redirect_response = auth_utils.require_role("guide")
    if redirect_response:
        return redirect_response

    tours = tour_dao.get_tours_by_guide(current_user.id)

    tours_overview = []
    for tour in tours:
        reservation_rows = reservation_dao.get_active_reservations_with_participant(tour["id"])
        dates = reservation_utils.group_guide_reservations_by_date(reservation_rows)
        tours_overview.append({
            "tour": tour,
            "dates": dates,
            "locked": reservation_dao.tour_has_active_reservations(tour["id"]),
        })

    return render_template("guide_profile.html", tours_overview=tours_overview)

@app.route("/admin")
@login_required
def admin_dashboard():
    redirect_response = auth_utils.require_role("admin")
    if redirect_response:
        return redirect_response
    return render_template("admin_dashboard.html")

@app.route("/tours/<int:tour_id>")
def tour_detail(tour_id):
    tour = tour_dao.get_tour_by_id(tour_id)
    if tour is None:
        flash("Tour not found.", "warning")
        return redirect(url_for("index"))
    
    schedules = tour_schedule_dao.get_schedules_by_tour(tour_id)
    stops = tour_stop_dao.get_stops_by_tour(tour_id)
    photos = tour_photo_dao.get_photos_by_tour(tour_id)

    available_dates = []
    
    if current_user.is_authenticated:
        available_dates = reservation_utils.get_available_dates_for_tour(schedules)

    return render_template("tour_detail.html", tour=tour, schedules=schedules, stops=stops, photos=photos, available_dates=available_dates)

@app.route("/tours/<int:tour_id>/reserve", methods=["POST"])
@login_required
def reserve_tour(tour_id):
    if current_user.role != "participant":
        flash("Only participants can make reservations.", "danger")
        return redirect(url_for("tour_detail", tour_id=tour_id))
    
    tour = tour_dao.get_tour_by_id(tour_id)
    if tour is None:
        flash("Tour not found.", "danger")
        return redirect(url_for("index"))
    
    tour_date = request.form.get("tour_date","").strip()
    if not tour_date:
        flash("Please select a tour date.", "warning")
        return redirect(url_for("tour_detail", tour_id=tour_id))
    
    schedules = tour_schedule_dao.get_schedules_by_tour(tour_id)
    valid, error = reservation_utils.can_reserve_tour_date(tour, tour_date, schedules)
    if not valid:
        flash(error, "warning")
        return redirect(url_for("tour_detail", tour_id=tour_id))
    
    start_time = reservation_utils.get_start_time_for_date(tour_date, schedules)
    extra_first_names = request.form.getlist("guest_first_name")
    extra_last_names = request.form.getlist("guest_last_name")

    total_people, valid_guest, error = reservation_utils.get_total_people_from_guest_lists(extra_first_names, extra_last_names)
    if error:
        flash(error, "warning")
        return redirect(url_for("tour_detail", tour_id=tour_id))
    
    reserved_places = reservation_dao.get_reserved_places_for_tour_date(tour_id, tour_date)
    available_places = tour["max_participants"] - reserved_places

    if total_people > available_places:
        flash(f"Only {available_places} places are available for the selected date.", "warning")
        return redirect(url_for("tour_detail", tour_id=tour_id))
    
    existing_reservations = reservation_dao.get_active_reservations_by_participant(current_user.id)
    if reservation_utils.has_overlapping_reservation(existing_reservations, tour_date, start_time, tour["duration_minutes"]):
        flash("You have an overlapping reservation for another tour at the same time.", "warning")
        return redirect(url_for("tour_detail", tour_id=tour_id))
    
    reservation_id = reservation_dao.create_reservation(current_user.id, tour_id, tour_date, total_people)
    if valid_guest:
        reservation_guest_dao.add_guests_bulk(reservation_id, valid_guest)

    flash("Tour reserved successfully.", "success")
    return redirect(url_for("participant_profile"))

@app.route("/guide/tours/new", methods=["GET", "POST"])
@login_required
def new_tour():
    redirect_response = auth_utils.require_role("guide")
    if redirect_response:
        return redirect_response

    guide_languages = [row["language"] for row in user_dao.get_guide_languages(current_user.id)]

    def render_form():
        return render_template("new_tour.html", allowed_languages=guide_languages, weekday_names=valid_utils.WEEKDAY_NAMES, form=request.form)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        meeting_point = request.form.get("meeting_point", "").strip()
        duration_minutes = request.form.get("duration_minutes", "")
        language = request.form.get("language", "")
        max_participants = request.form.get("max_participants", "")
        description = request.form.get("description", "").strip()
        weekdays = request.form.getlist("weekday")
        stop_names = request.form.getlist("stop_name")
        photos = request.files.getlist("photos")

        error = (
            valid_utils.validate_tour(title, meeting_point, duration_minutes, language, max_participants, description, guide_languages)
            or valid_utils.validate_tour_schedule(weekdays, request.form)
            or valid_utils.validate_tour_stops(stop_names)
            or valid_utils.validate_tour_photos(photos)
        )
        if error:
            flash(error, "warning")
            return render_form()

        tour_id = tour_dao.create_tour(current_user.id, title, meeting_point, int(duration_minutes), language, int(max_participants), description)
        tour_schedule_dao.add_schedules_bulk(tour_id, _parse_schedules(weekdays, request.form))
        tour_stop_dao.add_stops_bulk(tour_id, [s.strip() for s in stop_names if s.strip()])

        saved_paths = []
        try:
            for index, photo in enumerate(photos, start=1):
                path = photo_utils.save_tour_photo(photo, tour_id, index, TOUR_PHOTO_WIDTH, TOUR_PHOTO_HEIGHT)
                saved_paths.append(path)
        except UnidentifiedImageError:
            flash("One or more files could not be read as images.", "danger")
            return render_form()

        tour_photo_dao.add_photos_bulk(tour_id, saved_paths)
        flash("Tour created successfully.", "success")
        return redirect(url_for("tour_detail", tour_id=tour_id))

    return render_form()

@app.route("/guide/tours/<int:tour_id>/edit", methods=["GET", "POST"])
@login_required
def edit_tour(tour_id):
    redirect_response = auth_utils.require_role("guide")
    if redirect_response:
        return redirect_response

    tour = tour_dao.get_tour_by_id(tour_id)
    if tour is None or tour["guide_id"] != current_user.id:
        flash("You are not authorized to edit this tour.", "danger")
        return redirect(url_for("guide_profile"))

    locked = reservation_dao.tour_has_active_reservations(tour_id)
    guide_languages = [row["language"] for row in user_dao.get_guide_languages(current_user.id)]
    schedules = tour_schedule_dao.get_schedules_by_tour(tour_id)
    stops = tour_stop_dao.get_stops_by_tour(tour_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        stop_names = request.form.getlist("stop_name")

        def render_form():
            return render_template(
                "edit_tour.html",
                tour=tour,
                schedules=schedules,
                stops=stops,
                locked=locked,
                allowed_languages=guide_languages,
                weekday_names=valid_utils.WEEKDAY_NAMES,
                form=request.form,
            )

        error = valid_utils.validate_tour_text(title, description) or valid_utils.validate_tour_stops(stop_names)
        if error:
            flash(error, "warning")
            return render_form()

        if locked:
            tour_dao.update_tour_text(tour_id, title, description)
        else:
            meeting_point = request.form.get("meeting_point", "").strip()
            duration_minutes = request.form.get("duration_minutes", "")
            language = request.form.get("language", "")
            max_participants = request.form.get("max_participants", "")
            weekdays = request.form.getlist("weekday")

            error = (
                valid_utils.validate_tour(title, meeting_point, duration_minutes, language, max_participants, description, guide_languages)
                or valid_utils.validate_tour_schedule(weekdays, request.form)
            )
            if error:
                flash(error, "warning")
                return render_form()

            tour_dao.update_tour_full(tour_id, title, meeting_point, duration_minutes, language, max_participants, description)
            tour_schedule_dao.replace_schedules(tour_id, _parse_schedules(weekdays, request.form))

        tour_stop_dao.replace_stops(tour_id, [s.strip() for s in stop_names if s.strip()])
        flash("Tour updated successfully.", "success")
        return redirect(url_for("tour_detail", tour_id=tour_id))

    return render_template(
        "edit_tour.html",
        tour=tour,
        schedules=schedules,
        stops=stops,
        locked=locked,
        allowed_languages=guide_languages,
        weekday_names=valid_utils.WEEKDAY_NAMES,
        form=None,
    )

@app.route("/guide/tours/<int:tour_id>/delete", methods=["POST"])
@login_required
def delete_tour(tour_id):
    redirect_response = auth_utils.require_role("guide")
    if redirect_response:
        return redirect_response

    tour = tour_dao.get_tour_by_id(tour_id)
    if tour is None or tour["guide_id"] != current_user.id:
        flash("You are not authorized to delete this tour.", "danger")
        return redirect(url_for("index"))

    if reservation_dao.tour_has_active_reservations(tour_id):
        flash("This tour cannot be deleted because it has active reservations.", "warning")
        return redirect(url_for("guide_profile"))

    photos = tour_photo_dao.get_photos_by_tour(tour_id)
    photo_paths = [photo["image_path"] for photo in photos]
    try: 
        photo_utils.delete_tour_photos(photo_paths)
    except Exception as e:
        flash(f"Error deleting tour photos: {str(e)}", "warning")
    
    tour_dao.delete_tour(tour_id)
    
    flash("Tour deleted successfully.", "success")
    return redirect(url_for("index"))

@app.route("/reservations/<int:reservation_id>/cancel", methods=["POST"])
@login_required
def cancel_reservation(reservation_id):
    if current_user.role != "participant":
        flash("Only participants can cancel reservations.", "danger")
        return redirect(url_for("participant_profile"))

    reservation = reservation_dao.get_reservation_detail_for_participant(reservation_id, current_user.id)
    if reservation is None:
        flash("Reservation not found.", "danger")
        return redirect(url_for("participant_profile"))

    if reservation["status"] != "active":
        flash("This reservation cannot be canceled.", "danger")
        return redirect(url_for("participant_profile"))

    if not reservation_utils.can_cancel_reservation(reservation["tour_date"], reservation["start_time"]):
        flash("This reservation cannot be canceled.", "danger")
        return redirect(url_for("participant_profile"))

    reservation_dao.cancel_reservation(reservation_id)
    flash("Reservation canceled successfully.", "success")
    return redirect(url_for("participant_profile"))

def _build_report_overview(tour_id):
    """Splits the tour's reserved dates into: dates that already took place and
    still need a report, dates already reported, and upcoming dates."""
    reservation_rows = reservation_dao.get_active_reservations_with_participant(tour_id)
    grouped = reservation_utils.group_guide_reservations_by_date(reservation_rows)
    reports_by_date = {r["tour_date"]: r for r in tour_report_dao.get_reports_by_tour(tour_id)}

    pending, reported, upcoming = [], [], []
    for entry in grouped:
        is_past = reservation_utils.is_tour_date_past(entry["tour_date"], entry["start_time"])
        if not is_past:
            upcoming.append(entry)
        elif entry["tour_date"] in reports_by_date:
            entry = dict(entry)
            entry["report"] = reports_by_date[entry["tour_date"]]
            reported.append(entry)
        else:
            pending.append(entry)

    return pending, reported, upcoming

@app.route("/guide/tours/<int:tour_id>/report", methods=["GET", "POST"])
@login_required
def tour_report(tour_id):
    redirect_response = auth_utils.require_role("guide")
    if redirect_response:
        return redirect_response

    tour = tour_dao.get_tour_by_id(tour_id)
    if tour is None or tour["guide_id"] != current_user.id:
        flash("You are not authorized to manage reports for this tour.", "danger")
        return redirect(url_for("guide_profile"))

    if request.method == "POST":
        tour_date = request.form.get("tour_date", "").strip()
        actual_attendees = request.form.get("actual_attendees", "")
        photo = request.files.get("evidence_photo")

        pending, _, _ = _build_report_overview(tour_id)
        target = next((e for e in pending if e["tour_date"] == tour_date), None)
        if target is None:
            flash("You can only report a past tour date that has reservations and no report yet.", "warning")
            return redirect(url_for("tour_report", tour_id=tour_id))

        error = (
            valid_utils.validate_actual_attendees(actual_attendees, target["total_people"])
            or valid_utils.validate_report_photo(photo)
        )
        if error:
            flash(error, "warning")
            return redirect(url_for("tour_report", tour_id=tour_id))

        try:
            photo_path = photo_utils.save_report_photo(photo, tour_id, tour_date, REPORT_PHOTO_WIDTH, REPORT_PHOTO_HEIGHT)
        except UnidentifiedImageError:
            flash("The uploaded file could not be read as an image.", "danger")
            return redirect(url_for("tour_report", tour_id=tour_id))

        tour_report_dao.create_report(tour_id, tour_date, actual_attendees, photo_path)
        flash("Report submitted successfully.", "success")
        return redirect(url_for("tour_report", tour_id=tour_id))

    pending, reported, upcoming = _build_report_overview(tour_id)
    return render_template(
        "tour_report.html",
        tour=tour,
        pending=pending,
        reported=reported,
        upcoming=upcoming,
    )

if __name__ == "__main__":
    app.run(debug=True)