from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime, timezone
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True)
    username = Column(String)
    email = Column(String)
    avatar_url = Column(String)
    role = Column(String, default="analyst")
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))