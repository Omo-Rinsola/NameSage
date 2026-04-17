# defines response and input structure for routers
from pydantic import BaseModel
from datetime import datetime
from typing import List


# --------- input/request--------


class ProfileCreate(BaseModel):
    name: str

#--------- output/response schema-------


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
    created_at: datetime

    class Config:
        orm_mode = True


class ProfileResponse(BaseModel):
    status: str
    data: ProfileData

# Already exist
class ProfileExistsResponse(BaseModel):
    status: str
    message: str
    data: ProfileData

# get list of the same gender, country_id, age_group
class ProfileListData(BaseModel):
    id: str
    name: str
    gender: str
    age: int
    age_group: str
    country_id: str

    class Config:
        orm_mode = True


class ProfileListResponse(BaseModel):
    status: str
    count: int
    data: List[ProfileListData]
