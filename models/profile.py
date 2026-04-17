# where the Database structure for profile table is  defines (columns like name, age, etc.)

from sqlalchemy import Column, String, Integer, Float, DateTime
from datetime import datetime
from core.database import Base


class Profile(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    gender = Column(String)
    gender_probability = Column(Float)

    sample_size = Column(Integer)

    age = Column(Integer)
    age_group = Column(String)

    country_id = Column(String)
    country_probability = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)


