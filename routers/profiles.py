from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from services.profile_service import build_profile
from models.profile import Profile
from crud import profiles as crud

from utils.helpers import generate_id

router = APIRouter(prefix="/api", tags=["Profiles"])


# ---------------- POST ----------------
@router.post("/profiles")
async def create_profile(name: str, db: Session = Depends(get_db)):

    # idempotency
    existing = crud.get_by_name(db, name)

    if existing:
        return {
            "status": "success",
            "message": "Profile already exists",
            "data": existing
        }

    # service call
    profile_data = await build_profile(name)

    # error handling (REQUIRED FORMAT)
    if "error" in profile_data:
        raise HTTPException(
            status_code=502,
            detail={
                "status": "error",
                "message": profile_data["error"]
            }
        )

    # create DB object
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
        created_at=profile_data["created_at"]
    )

    crud.create(db, new_profile)

    return {
        "status": "success",
        "data": new_profile
    }


# ---------------- GET BY ID ----------------
@router.get("/profiles/{id}")
def get_profile(id: str, db: Session = Depends(get_db)):

    profile = crud.get_by_id(db, id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Profile not found"
            }
        )

    return {
        "status": "success",
        "data": profile
    }


# ---------------- GET ALL ----------------
@router.get("/profiles")
def get_profiles(db: Session = Depends(get_db)):

    profiles = db.query(Profile).all()

    return {
        "status": "success",
        "count": len(profiles),
        "data": profiles
    }


# ---------------- DELETE ----------------
@router.delete("/profiles/{id}", status_code=204)
def delete_profile(id: str, db: Session = Depends(get_db)):

    profile = crud.get_by_id(db, id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "Profile not found"
            }
        )

    crud.delete(db, profile)
    return