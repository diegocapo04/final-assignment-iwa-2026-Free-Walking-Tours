from flask import flash, redirect, url_for
from flask_login import current_user

def redirect_if_authenticated():
    if current_user.is_authenticated:
        return redirect_by_role()
    return None

def redirect_by_role():
    if current_user.role == "participant":
        return redirect(url_for("participant_profile"))
    if current_user.role == "guide":
        return redirect(url_for("guide_profile"))
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("index"))

def require_role(role):
    if not current_user.is_authenticated:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("login"))

    if current_user.role != role:
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for("index"))

    return None