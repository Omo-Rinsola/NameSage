# where the Database structure for profile table is  defines (columns like name, age, etc.)

from sqlalchemy import Column, String, Integer, Float, DateTime
from datetime import datetime, timezone
from core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True)  # UUID v7 string
    name = Column(String, unique=True, index=True)

    gender = Column(String)
    gender_probability = Column(Float)

    age = Column(Integer)
    age_group = Column(String)

    country_id = Column(String)
    country_name = Column(String)
    country_probability = Column(Float)


    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Auto-generated