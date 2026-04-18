from sqlalchemy.orm import Session
from models.profile import Profile


def get_by_name(db: Session, name: str):
    return db.query(Profile).filter(Profile.name == name).first()


def get_by_id(db: Session, id: str):
    return db.query(Profile).filter(Profile.id == id).first()


def create(db: Session, profile: Profile):
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def delete(db: Session, profile: Profile):
    db.delete(profile)
    db.commit()
