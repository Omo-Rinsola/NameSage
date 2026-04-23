import json
from crud import profiles as crud
from core.database import SessionLocal
from models.profile import Profile
from utils.helpers import generate_id
from core.database import Base, engine
Base.metadata.create_all(bind=engine)

db = SessionLocal()
with open("seed_profiles.json", "r") as file:
    data = json.load(file)
    profiles = data["profiles"]
    for profile_data in profiles:
        if crud.get_by_name(db, profile_data["name"]):
            continue

        new_profile = Profile(
            id=generate_id(),
            name=profile_data["name"],
            gender=profile_data["gender"],
            gender_probability=profile_data["gender_probability"],
            age=profile_data["age"],
            age_group=profile_data["age_group"],
            country_id=profile_data["country_id"],
            country_name=profile_data["country_name"],
            country_probability=profile_data["country_probability"],
        )

        crud.create(db, new_profile)
    db.close()
