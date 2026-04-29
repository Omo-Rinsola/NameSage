from sqlalchemy.orm import Session
from models.user import User, RefreshToken
from utils.helpers import generate_id
from datetime import datetime, timezone


def get_user_by_github_id(db: Session, github_id: str):
    return db.query(User).filter(User.github_id == github_id).first()


def create_or_update_user(db: Session, github_data: dict) -> User:
    user = get_user_by_github_id(db, str(github_data["id"]))

    if user:
        user.username = github_data.get("login")
        user.email = github_data.get("email")
        user.avatar_url = github_data.get("avatar_url")
        user.last_login_at = datetime.now(timezone.utc)
    else:
        user = User(
            id=generate_id(),
            github_id=str(github_data["id"]),
            username=github_data.get("login"),
            email=github_data.get("email"),
            avatar_url=github_data.get("avatar_url"),
            role="analyst",  # everyone starts as analyst
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


def save_refresh_token(db: Session, user_id: str, token: str):
    db_token = RefreshToken(
        id=generate_id(),
        user_id=user_id,
        token=token,
    )
    db.add(db_token)
    db.commit()


def get_refresh_token(db: Session, token: str):
    return db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.is_revoked == False
    ).first()


def revoke_refresh_token(db: Session, token: str):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()


def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()