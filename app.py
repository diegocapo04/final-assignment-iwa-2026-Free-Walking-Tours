from flask import Flask, render_template
from flask_login import LoginManager
from models import User
from db.database import init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret key for the final project"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."

@login_manager.user_loader
def load_user(user_id):
    return None

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)