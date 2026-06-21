from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import UnidentifiedImageError
from models import user_from_row
from dao import user_dao, tour_dao, tour_schedule_dao, tour_stop_dao, tour_photo_dao
from utils import auth_utils, valid_utils, photo_utils

UPLOAD_FOLDER = "static/uploads/tour_photos"
TOUR_PHOTO_WIDTH = 1200
TOUR_PHOTO_HEIGHT = 800

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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if auth_utils.redirect_if_authenticated():
        return auth_utils.redirect_if_authenticated()
    
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
    if auth_utils.redirect_if_authenticated():
        return auth_utils.redirect_if_authenticated()
    
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
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

@app.route("/participant/profile")
@login_required
def participant_profile():
    if auth_utils.require_role("participant"):
        return auth_utils.require_role("participant")
    return render_template("participant_profile.html")

@app.route("/guide/profile")
@login_required
def guide_profile():
    if auth_utils.require_role("guide"):
        return auth_utils.require_role("guide")
    tours = tour_dao.get_tours_by_guide(current_user.id)
    return render_template("guide_profile.html", tours=tours)

@app.route("/admin")
@login_required
def admin_dashboard():
    if auth_utils.require_role("admin"):
        return auth_utils.require_role("admin")
    return render_template("admin_dashboard.html")

@app.route("/tours")
def tours():
    tours = tour_dao.get_tours()
    return render_template("tours.html", tours=tours)

@app.route("/tours/<int:tour_id>")
def tour_detail(tour_id):
    tour = tour_dao.get_tour_by_id(tour_id)
    if tour is None:
        flash("Tour not found.", "warning")
        return redirect(url_for("tours"))
    
    schedules = tour_schedule_dao.get_schedules_by_tour(tour_id)
    stops = tour_stop_dao.get_stops_by_tour(tour_id)
    photos = tour_photo_dao.get_photos_by_tour(tour_id)

    return render_template("tour_detail.html", tour=tour, schedules=schedules, stops=stops, photos=photos, weekday_names=valid_utils.WEEKDAY_NAMES)

@app.route("/guide/tours/new", methods=["GET", "POST"])
@login_required
def new_tour():
    if auth_utils.require_role("guide"):
        return auth_utils.require_role("guide")
    
    guide_languages = [row["language"] for row in user_dao.get_guide_languages(current_user.id)]
    
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

        error = valid_utils.validate_tour(title, meeting_point, duration_minutes, language, max_participants, description, guide_languages)
        if error:
            flash(error, "warning")
            return render_template("new_tour.html", allowed_languages=guide_languages, weekday_names=auth_utils.WEEKDAY_NAMES, form=request.form)
        
        error = valid_utils.validate_tour_schedule(weekdays, request.form)
        if error:
            flash(error, "warning")
            return render_template("new_tour.html", allowed_languages=guide_languages, weekday_names=auth_utils.WEEKDAY_NAMES, form=request.form)

        error = valid_utils.validate_tour_stops(stop_names)
        if error:
            flash(error, "warning")
            return render_template("new_tour.html", allowed_languages=guide_languages, weekday_names=auth_utils.WEEKDAY_NAMES, form=request.form)
        
        error = valid_utils.validate_tour_photos(photos)
        if error:
            flash(error, "warning")
            return render_template("new_tour.html", allowed_languages=guide_languages, weekday_names=auth_utils.WEEKDAY_NAMES, form=request.form)

        tour_id = tour_dao.create_tour(current_user.id, title, meeting_point, int(duration_minutes), language, int(max_participants), description)
        schedules = []
        for day in weekdays:
            time = request.form.get(f"{day}_time", "").strip()
            schedules.append({"weekday": int(day), "start_time": time})
        tour_schedule_dao.add_schedules_bulk(tour_id, schedules)

        cleaned_stops = [s.strip() for s in stop_names if s.strip()]
        tour_stop_dao.add_stops_bulk(tour_id, cleaned_stops)

        saved_paths = []
        try:
            for index, photo in enumerate(photos, start=1):
                path = photo_utils.save_tour_photo(photo, tour_id, index, TOUR_PHOTO_WIDTH, TOUR_PHOTO_HEIGHT)
                saved_paths.append(path)
        except UnidentifiedImageError:
            flash("One or more files could not be read as images.", "danger")
            return render_template("new_tour.html", allowed_languages=guide_languages, weekday_names=auth_utils.WEEKDAY_NAMES, form=request.form)

        tour_photo_dao.add_photos_bulk(tour_id, saved_paths)
        flash("Tour created successfully.", "success")
        return redirect(url_for("tour_detail", tour_id=tour_id))

    return render_template("new_tour.html", allowed_languages=valid_utils.ALLOWED_LANGUAGES, weekday_names=valid_utils.WEEKDAY_NAMES, form=request.form)

@app.route("/guide/tours/<int:tour_id>/delete", methods=["POST"])
@login_required
def delete_tour(tour_id):
    if auth_utils.require_role("guide"):
        return auth_utils.require_role("guide")
    
    tour = tour_dao.get_tour_by_id(tour_id)
    if tour is None or tour["guide_id"] != current_user.id:
        flash("You are not authorized to delete this tour.", "danger")
        return redirect(url_for("tours"))
    
    photos = tour_photo_dao.get_photos_by_tour(tour_id)
    photo_paths = [photo["image_path"] for photo in photos]
    try: 
        photo_utils.delete_tour_photos(photo_paths)
    except Exception as e:
        flash(f"Error deleting tour photos: {str(e)}", "warning")
    
    tour_dao.delete_tour(tour_id)
    
    flash("Tour deleted successfully.", "success")
    return redirect(url_for("tours"))

if __name__ == "__main__":
    app.run(debug=True)