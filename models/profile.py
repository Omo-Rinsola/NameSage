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
    sample_size = Column(Integer)

    age = Column(Integer)
    age_group = Column(String)

    country_id = Column(String)
    country_probability = Column(Float)

    created_at = Column(String)  # Store as ISO 8601 string to preserve UTC timezone