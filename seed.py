from db.database import init_db

def seed_database():
    init_db()
    print("Database initialized. Seed data will be added in the next milestone.")

if __name__ == "__main__":
    seed_database()