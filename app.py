from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import user_from_row
from dao.user_dao import (
    get_user_by_id,
    get_user_by_email,
    email_exists,
    create_participant,
    create_guide,
    add_guide_languages
)
from utils.auth_utils import redirect_if_authenticated, redirect_by_role, require_role
from utils.valid_utils import (
    ALLOWED_LANGUAGES,
    validate_basic_registration,
    validate_role,
    validate_guide_languages
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret key for the final project"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."

@login_manager.user_loader
def load_user(user_id):
    row = get_user_by_id(user_id)
    return user_from_row(row)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if redirect_if_authenticated():
        return redirect_if_authenticated()
    
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password")
        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("login.html")
        
        user_row = get_user_by_email(email)
        if user_row is None or not check_password_hash(user_row["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        
        user = user_from_row(user_row)
        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect_by_role()
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if redirect_if_authenticated():
        return redirect_if_authenticated()
    
    if request.method == "POST":
        role = request.form.get("role", "participant").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        languages = request.form.getlist("languages")

        role_error = validate_role(role)
        if role_error:
            flash(role_error, "warning")
            return render_template("register.html", allowed_languages=ALLOWED_LANGUAGES, selected_role=role)
        
        error = validate_basic_registration(first_name, last_name, email, password, confirm_password)
        if error:
            flash(error, "warning")
            return render_template("register.html", allowed_languages=ALLOWED_LANGUAGES, selected_role=role)
        
        if email_exists(email):
            flash("Email is already registered.", "danger")
            return render_template("register.html", allowed_languages=ALLOWED_LANGUAGES, selected_role=role)
        
        if role == "guide":
            language_error = validate_guide_languages(languages)
            if language_error:
                flash(language_error, "warning")
                return render_template("register.html", allowed_languages=ALLOWED_LANGUAGES, selected_role=role)
            
            password_hash = generate_password_hash(password)
            user_id = create_guide(first_name, last_name, email, password_hash)
            user_row = get_user_by_id(user_id)
            user = user_from_row(user_row)
            
            login_user(user)
            flash("Guide registration completed successfully.", "success")
            return redirect(url_for("guide_profile"))
        
        password_hash = generate_password_hash(password)
        user_id = create_participant(first_name, last_name, email, password_hash)

        user_row = get_user_by_id(user_id)
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
    if require_role("participant"):
        return require_role("participant")
    return render_template("participant_profile.html")

@app.route("/guide/profile")
@login_required
def guide_profile():
    if require_role("guide"):
        return require_role("guide")
    return render_template("guide_profile.html")

@app.route("/admin")
@login_required
def admin_dashboard():
    if require_role("admin"):
        return require_role("admin")
    return render_template("admin_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)