COUNTRY_MAP = {
    "nigeria": "NG", "kenya": "KE", "ghana": "GH", "angola": "AO",
    "tanzania": "TZ", "ethiopia": "ET", "uganda": "UG", "senegal": "SN",
    "cameroon": "CM", "zambia": "ZM", "zimbabwe": "ZW", "mali": "ML",
    "niger": "NE", "chad": "TD", "egypt": "EG", "morocco": "MA",
    "algeria": "DZ", "tunisia": "TN", "sudan": "SD", "somalia": "SO",
    "benin": "BJ", "togo": "TG", "ivory coast": "CI", "rwanda": "RW",
    "mozambique": "MZ", "madagascar": "MG", "malawi": "MW",
}


def parse_nl_query(q: str) -> dict:
    q = q.lower().strip()
    tokens = q.split()
    filters = {}
    found_something: bool = False

    # Gender
    has_male = any(w in tokens for w in ["male", "males", "man", "men", "boy", "boys"])
    has_female = any(w in tokens for w in ["female", "females", "woman", "women", "girl", "girls"])

    if has_male and not has_female:
        filters["gender"] = "male"
        found_something = True
    elif has_female and not has_male:
        filters["gender"] = "female"
        found_something = True
    elif has_male and has_female:
        found_something = True  # both mentioned, no gender filter

    # Age group
    if any(w in tokens for w in ["child", "children", "kid", "kids"]):
        filters["age_group"] = "child"
        found_something = True
    elif any(w in tokens for w in ["teenager", "teenagers", "teen", "teens"]):
        filters["age_group"] = "teenager"
        found_something = True
    elif any(w in tokens for w in ["adult", "adults"]):
        filters["age_group"] = "adult"
        found_something = True
    elif any(w in tokens for w in ["senior", "seniors", "elderly"]):
        filters["age_group"] = "senior"
        found_something = True
    elif "young" in tokens:
        filters["min_age"] = 16
        filters["max_age"] = 24
        found_something = True

    # Above/below age
    for i, word in enumerate(tokens):
        if word in ["above", "over", "older"] and i + 1 < len(tokens):
            try:
                filters["min_age"] = int(tokens[i + 1])
                found_something = True
            except ValueError:
                pass
        if word in ["below", "under", "younger"] and i + 1 < len(tokens):
            try:
                filters["max_age"] = int(tokens[i + 1])
                found_something = True
            except ValueError:
                pass

    # Country
    for word in tokens:
        if word in COUNTRY_MAP:
            filters["country_id"] = COUNTRY_MAP[word]
            found_something = True

    for i in range(len(tokens) - 1):
        phrase = tokens[i] + " " + tokens[i + 1]
        if phrase in COUNTRY_MAP:
            filters["country_id"] = COUNTRY_MAP[phrase]
            found_something = True

    return filters if found_something else {}