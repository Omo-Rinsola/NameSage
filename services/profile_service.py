from services.external_apis import (
    get_gender_data,
    get_age_data,
    get_country_data
)
from datetime import datetime, timezone


# AGE GROUP LOGIC


def get_age_group(age: int):
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    else:
        return "senior"


# MAIN SERVICE FUNCTION


async def build_profile(name: str):

    # Call external APIs
    gender_data = await get_gender_data(name)
    age_data = await get_age_data(name)
    country_data = await get_country_data(name)

    # VALIDATION (IMPORTANT FOR TASK)

    # Genderize validation
    if not gender_data.get("gender") or gender_data.get("count", 0) == 0:
        return {
            "error": "Genderize returned invalid response"
        }

    # Agify validation
    if not age_data.get("age"):
        return {
            "error": "Agify returned invalid response"
        }

    # Nationalize validation
    if not country_data.get("country") or len(country_data["country"]) == 0:
        return {
            "error": "Nationalize returned invalid response"
        }

    # PROCESS DATA

    gender = gender_data["gender"]
    gender_probability = gender_data["probability"]
    sample_size = gender_data["count"]

    age = age_data["age"]

    # pick country with highest probability
    country = max(
        country_data["country"],
        key=lambda x: x["probability"]
    )

    # FINAL PROFILE STRUCTURE

    profile = {
        "name": name,
        "gender": gender,
        "gender_probability": gender_probability,
        "sample_size": sample_size,
        "age": age,
        "age_group": get_age_group(age),
        "country_id": country["country_id"],
        "country_probability": country["probability"],
        "created_at": datetime.now(timezone.utc)
    }

    return profile
