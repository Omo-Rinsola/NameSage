from services.external_apis import (
    get_gender_data,
    get_age_data,
    get_country_data
)
from datetime import datetime, timezone


# AGE GROUP LOGIC

def get_age_group(age: int) -> str:
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

    # Call all three external APIs
    gender_data = await get_gender_data(name)
    age_data = await get_age_data(name)
    country_data = await get_country_data(name)

    # --- Genderize validation ---
    # Fail if gender is null OR count is 0
    if not gender_data.get("gender") or gender_data.get("count", 0) == 0:
        return {"error": "Genderize returned an invalid response"}

    # --- Agify validation ---
    if age_data.get("age") is None:
        return {"error": "Agify returned an invalid response"}

    # --- Nationalize validation ---
    if not country_data.get("country") or len(country_data["country"]) == 0:
        return {"error": "Nationalize returned an invalid response"}

    # --- Process data ---

    gender = gender_data["gender"]
    gender_probability = gender_data["probability"]
    sample_size = gender_data["count"]

    age = age_data["age"]

    # Pick country with highest probability
    country = max(
        country_data["country"],
        key=lambda x: x["probability"]
    )

    # Build and return profile dict
    return {
        "name": name,
        "gender": gender,
        "gender_probability": gender_probability,
        "sample_size": sample_size,
        "age": age,
        "age_group": get_age_group(age),
        "country_id": country["country_id"],
        "country_probability": country["probability"],
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

