# defines response and input structure for routers
from pydantic import BaseModel
from typing import List, Optional


# --------- Input / Request ---------

class ProfileCreate(BaseModel):
    name: str


# --------- Full Profile (POST response, GET by ID) ---------

class ProfileData(BaseModel):
    id: str
    name: str
    gender: str
    gender_probability: float
    sample_size: int
    age: int
    age_group: str
    country_id: str
    country_probability: float
    created_at: str  # stored and returned as ISO 8601 string

    class Config:
        from_attributes = True  # Pydantic v2 (use orm_mode = True for Pydantic v1)


class ProfileResponse(BaseModel):
    status: str
    data: ProfileData


class ProfileExistsResponse(BaseModel):
    status: str
    message: str
    data: ProfileData


# --------- List Profile (GET /profiles) ---------

class ProfileListData(BaseModel):
    id: str
    name: str
    gender: str
    age: int
    age_group: str
    country_id: str

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    status: str
    count: int
    data: List[ProfileListData]


# --------- Error ---------

class ErrorResponse(BaseModel):
    status: str
    message: str