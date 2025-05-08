from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, time

class UserCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id_user: int
    name: str
    last_name: str
    email: EmailStr
    id_role: int
    class Config:
        orm_mode = True

class CourtBase(BaseModel):
    name: str
    description: str

class CourtOut(CourtBase):
    id_court: int
    class Config:
        orm_mode = True

class ScheduleCreate(BaseModel):
    schedule_date: date
    start_time: time
    end_time: time
    price: float

class ScheduleOut(BaseModel):
    id_schedule: int
    schedule_date: date
    start_time: time
    end_time: time
    price: float
    is_available: bool
    class Config:
        orm_mode = True

class BookingCreate(BaseModel):
    schedule_ids: List[int]

class BookingOut(BaseModel):
    id_booking: int
    booking_date: date
    status: str
    schedules: List[ScheduleOut]
    total_price: float
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

