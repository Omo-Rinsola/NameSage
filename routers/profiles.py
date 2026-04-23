from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from dependencies import get_db
from services.profile_service import build_profile
from models.profile import Profile
from crud import profiles as crud
from schemas.profiles import ProfileCreate
from utils.helpers import generate_id
from services.nl_parser import parse_nl_query

router = APIRouter(prefix="/api", tags=["Profiles"])


def profile_to_dict(profile: Profile) -> dict:
    """Serialize a Profile ORM object to a full dict."""
    return {
        "id": profile.id,
        "name": profile.name,
        "gender": profile.gender,
        "gender_probability": profile.gender_probability,
        "sample_size": profile.sample_size,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id,
        "country_probability": profile.country_probability,
        "created_at": profile.created_at,
    }


def profile_to_list_dict(profile: Profile) -> dict:
    """Serialize a Profile ORM object to the list (filtered) format."""
    return {
        "id": profile.id,
        "name": profile.name,
        "gender": profile.gender,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id,
    }


# ---------------- POST /api/profiles ----------------

@router.post("/profiles", status_code=201)
async def create_profile(body: ProfileCreate, db: Session = Depends(get_db)):
    # 400 — missing or empty name
    if not body.name or not body.name.strip():
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Name is required"}
        )

    name = body.name.strip().lower()  # normalize for idempotency

    # Idempotency — return existing profile if name already stored
    existing = crud.get_by_name(db, name)
    if existing:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Profile already exists",
                "data": profile_to_dict(existing),
            }
        )

    # Call external APIs and build profile data
    profile_data = await build_profile(name)

    # 502 — upstream API returned invalid data
    if "error" in profile_data:
        raise HTTPException(
            status_code=502,
            detail={"status": "502", "message": profile_data["error"]}
        )

    # Persist to database
    new_profile = Profile(
        id=generate_id(),
        name=name,
        gender=profile_data["gender"],
        gender_probability=profile_data["gender_probability"],
        sample_size=profile_data["sample_size"],
        age=profile_data["age"],
        age_group=profile_data["age_group"],
        country_id=profile_data["country_id"],
        country_probability=profile_data["country_probability"],
        created_at=profile_data["created_at"],
    )

    crud.create(db, new_profile)

    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "data": profile_to_dict(new_profile),
        }
    )

# -------------------- profile search with natural language-------
@router.get("/profiles/search")
def search_profiles(
        q: str = Query(...),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db),
):
    if not q or not q.strip():
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Invalid query parameters"}
        )

    filters = parse_nl_query(q)

    if not filters:
        raise HTTPException(
            status_code=400,
            detail={"status": "error", "message": "Unable to interpret query"}
        )

    query = db.query(Profile)

    if "gender" in filters:
        query = query.filter(Profile.gender == filters["gender"])
    if "age_group" in filters:
        query = query.filter(Profile.age_group == filters["age_group"])
    if "country_id" in filters:
        query = query.filter(Profile.country_id == filters["country_id"])
    if "min_age" in filters:
        query = query.filter(Profile.age >= filters["min_age"])
    if "max_age" in filters:
        query = query.filter(Profile.age <= filters["max_age"])

    total = query.count()
    skip = (page - 1) * limit
    profiles = query.offset(skip).limit(limit).all()

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [profile_to_list_dict(p) for p in profiles],
    }

# ---------------- GET /api/profiles/{id} ----------------

@router.get("/profiles/{id}")
def get_profile(id: str, db: Session = Depends(get_db)):
    profile = crud.get_by_id(db, id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )

    return {
        "status": "success",
        "data": profile_to_dict(profile),
    }


# ---------------- GET /api/profiles ----------------

@router.get("/profiles")
def get_profiles(
        gender: str = Query(None),
        country_id: str = Query(None),
        age_group: str = Query(None),
        min_age: int = Query(None),
        max_age: int = Query(None),
        min_gender_probability: float = Query(None),
        min_country_probability: float = Query(None),
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=50),
        sort_by: str = Query(None),
        order: str = Query("asc"),
        db: Session = Depends(get_db),
):
    query = db.query(Profile)

    # Case-insensitive filtering
    if gender:
        query = query.filter(func.lower(Profile.gender) == gender.lower())
    if country_id:
        query = query.filter(func.lower(Profile.country_id) == country_id.lower())
    if age_group:
        query = query.filter(func.lower(Profile.age_group) == age_group.lower())
    if min_age:
        query = query.filter(Profile.age >= min_age)

    if max_age:
        query = query.filter(Profile.age <= max_age)
    if min_gender_probability:
        query = query.filter(Profile.gender_probability >= min_gender_probability)
    if min_country_probability:
        query = query.filter(Profile.country_probability >= min_country_probability)

    total = query.count()

    if sort_by:
        column = getattr(Profile, sort_by, None)
        if column is not None:
            if order =="desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

    skip = (page - 1) * limit
    profiles = query.offset(skip).limit(limit).all()

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [profile_to_list_dict(p) for p in profiles],
    }


# ---------------- DELETE /api/profiles/{id} ----------------

@router.delete("/profiles/{id}", status_code=204)
def delete_profile(id: str, db: Session = Depends(get_db)):
    profile = crud.get_by_id(db, id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Profile not found"}
        )

    crud.delete(db, profile)
    return "204 No Content"
