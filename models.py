from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, first_name, last_name, email, password_hash, role):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.role = role