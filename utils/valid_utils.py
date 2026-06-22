ALLOWED_LANGUAGES = ["Italian", "English", "Spanish", "Portuguese", "German"]
ALLOWED_ROLES = ["participant", "guide"]
ALLOWED_PHOTO_EXTENSIONS = ["png", "jpg", "jpeg"]
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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

def validate_tour_text(title, description):
    """Validation for the fields that stay editable even after the tour is locked."""
    if not title or not description:
        return "Title and description are required."

    if len(title) < 5 or len(title) > 100:
        return "Title must contain between 5 and 100 characters."

    if len(description) < 10 or len(description) > 1000:
        return "Description must contain between 10 and 1000 characters."

    return None

def validate_tour(title, meeting_point, duration_minutes, language, max_participants, description, guide_languages):
    if not title or not description or not meeting_point or not duration_minutes or not language or not max_participants:
        return "All fields are required."

    text_error = validate_tour_text(title, description)
    if text_error:
        return text_error

    if language not in guide_languages:
        return "Selected language is not among the guide's languages."

    try:
        duration_minutes = int(duration_minutes)
        if duration_minutes <= 0:
            return "Duration must be a positive integer."
    except ValueError:
        return "Duration must be a valid integer."

    try:
        max_participants = int(max_participants)
        if max_participants <= 0:
            return "Maximum participants must be a positive integer."
    except ValueError:
        return "Maximum participants must be a valid integer."

    if language not in ALLOWED_LANGUAGES:
        return "Invalid language selected."

def validate_tour_schedule(weekdays, start_times):
    if not weekdays:
        return "Please select at least one day of the week."
    
    for day in weekdays:
        try:
            day_int = int(day)
            if day_int < 0 or day_int > 6:
                return "Invalid weekday selected."
        except (ValueError, TypeError):
            return "Invalid weekday selected."
        
        time = start_times.get(f"start_time_{day}", "").strip()
        if not time:
            return f"Please enter a start time for {WEEKDAY_NAMES[int(day)]}."
        
    return None

def validate_tour_stops(stop_names):
    cleaned = [s.strip() for s in stop_names if s.strip()]
    if len(cleaned) < 4:
        return "Please enter at least 4 stops."
    
    for name in cleaned:
        if len(name) > 100:
            return "Each stop name must be at most 100 characters."
        
    return None

def has_allowed_extension(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_PHOTO_EXTENSIONS

def validate_tour_photos(photos):
    valid_photos = [p for p in photos if p.filename != ""]
    if len(valid_photos) != 5:
        return "Please upload exactly 5 promotional photos."
    for photo in valid_photos:
        if not has_allowed_extension(photo.filename):
            return "Photos must be PNG, JPG or JPEG files."
    return None

def validate_report_photo(photo):
    if photo is None or photo.filename == "":
        return "Please upload one photo as evidence of the tour."
    if not has_allowed_extension(photo.filename):
        return "The evidence photo must be a PNG, JPG or JPEG file."
    return None

def validate_actual_attendees(actual_attendees, reserved_total):
    """The declared number of attendees must be a non-negative integer
    not greater than the people who had reserved for that date."""
    try:
        value = int(actual_attendees)
    except (ValueError, TypeError):
        return "The number of attendees must be a valid integer."

    if value < 0:
        return "The number of attendees cannot be negative."

    if value > reserved_total:
        return f"The number of attendees cannot exceed the {reserved_total} reserved people."

    return None