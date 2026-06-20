ALLOWED_LANGUAGES = ["Italian", "English", "Spanish", "Portuguese", "German"]
ALLOWED_ROLES = ["participant", "guide"]


def validate_basic_registration(first_name, last_name, email, password, confirm_password):
    if not first_name or not last_name or not email or not password or not confirm_password:
        return "All fields are required."

    if len(first_name) < 2 or len(first_name) > 50:
        return "First name must contain between 2 and 50 characters."

    if len(last_name) < 2 or len(last_name) > 50:
        return "Last name must contain between 2 and 50 characters."

    if len(email) > 255:
        return "Email is too long."

    if len(password) < 8 or len(password) > 128:
        return "Password must contain between 8 and 128 characters."

    if password != confirm_password:
        return "Password and confirmation do not match."

    return None

def validate_role(role):
    if role not in ALLOWED_ROLES:
        return "Invalid role selected."

    return None


def validate_guide_languages(languages):
    if not languages:
        return "Please select at least one language."

    for language in languages:
        if language not in ALLOWED_LANGUAGES:
            return "One or more selected languages are invalid."

    return None