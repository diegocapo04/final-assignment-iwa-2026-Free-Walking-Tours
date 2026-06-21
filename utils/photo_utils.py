import os
from PIL import Image

UPLOAD_FOLDER = "static/uploads/tour_photos"

def get_photo_filename(tour_id, photo_index, extension):
    return f"tour_{tour_id}_photo_{photo_index}.{extension}"

def get_db_photo_path(filename):
    return f"uploads/tour_photos/{filename}"

def save_tour_photo(photo, tour_id, photo_index, width, height):
    extension = photo.filename.rsplit(".", 1)[-1].lower()
    filename = get_photo_filename(tour_id, photo_index, extension)

    save_path = f"{UPLOAD_FOLDER}/{filename}"
    db_path = get_db_photo_path(filename)

    with Image.open(photo) as img:
        img.thumbnail((width, height))
        img.save(save_path)

    return db_path

def delete_tour_photos(photo_paths):
    for path in photo_paths:
        file_path = f"static/{path}"
        if os.path.isfile(file_path):
            os.remove(file_path)