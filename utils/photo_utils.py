import os
from PIL import Image

UPLOAD_FOLDER = "static/uploads/tour_photos"
REPORT_UPLOAD_FOLDER = "static/uploads/report_photos"

def get_photo_filename(tour_id, photo_index, extension):
    return f"tour_{tour_id}_photo_{photo_index}.{extension}"

def get_db_photo_path(filename):
    return f"uploads/tour_photos/{filename}"

def _save_resized(photo, save_path, width, height):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with Image.open(photo) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((width, height))
        img.save(save_path)

def save_tour_photo(photo, tour_id, photo_index, width, height):
    extension = photo.filename.rsplit(".", 1)[-1].lower()
    filename = get_photo_filename(tour_id, photo_index, extension)

    save_path = f"{UPLOAD_FOLDER}/{filename}"
    db_path = get_db_photo_path(filename)

    _save_resized(photo, save_path, width, height)
    return db_path

def save_report_photo(photo, tour_id, tour_date, width, height):
    """One evidence photo per (tour, date). Date is part of the file name so
    different occurrences of the same tour do not overwrite each other."""
    extension = photo.filename.rsplit(".", 1)[-1].lower()
    safe_date = tour_date.replace("-", "")
    filename = f"report_{tour_id}_{safe_date}.{extension}"

    save_path = f"{REPORT_UPLOAD_FOLDER}/{filename}"
    db_path = f"uploads/report_photos/{filename}"

    _save_resized(photo, save_path, width, height)
    return db_path

def delete_tour_photos(photo_paths):
    for path in photo_paths:
        file_path = f"static/{path}"
        if os.path.isfile(file_path):
            os.remove(file_path)