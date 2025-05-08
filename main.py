from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from userCrud import UserCrud
from auth import Auth
from crud import CourtCrud

API_PREFIX = "/api"

app = FastAPI()
router = APIRouter()

# CORS (opcional, para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_crud = UserCrud()
auth = Auth()
court_crud = CourtCrud()

# --------- MODELOS ---------
class UserRegister(BaseModel):
    name: str
    last_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UpdateUser(BaseModel):
    name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    password: Optional[str]
    id_role: Optional[int]

class AddPhone(BaseModel):
    phone_number: str

class BookingRequest(BaseModel):
    id_user: int
    id_court: int
    schedule_date: str
    start_time: str
    end_time: str

class UpdateBookingStatus(BaseModel):
    new_status: str

# --------- ENDPOINTS ---------
@router.get("/")
def hola():
    return "<h1>API!!</h1>"

@router.post("/register")
def register(user: UserRegister):
    result = auth.register(user.name, user.last_name, user.email, user.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/login")
def login(user: UserLogin):
    result = auth.login(user.email, user.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@router.get("/users")
def get_all_users():
    return user_crud.get_all_users()

@router.get("/users/{id_user}")
def get_user(id_user: int):
    result = user_crud.get_user_by_id(id_user)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.put("/users/{id_user}")
def update_user(id_user: int, user: UpdateUser):
    result = user_crud.update_user(
        id_user,
        name=user.name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
        id_role=user.id_role
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.delete("/users/{id_user}")
def delete_user(id_user: int):
    result = user_crud.delete_user(id_user)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/users/{id_user}/phones")
def add_phone(id_user: int, phone: AddPhone):
    result = user_crud.add_phone(id_user, phone.phone_number)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/users/{id_user}/phones")
def get_phones(id_user: int):
    return user_crud.get_phones(id_user)

@router.get("/courts")
def get_all_courts():
    return court_crud.get_all_courts()

@router.get("/courts/type/{id_type}")
def get_courts_by_type(id_type: int):
    return court_crud.get_courts_by_type(id_type)

@router.get("/courts/{id_court}")
def get_court_details(id_court: int):
    return court_crud.get_court_details(id_court)

@router.get("/courts/{id_court}/unavailable")
def get_unavailable_schedules(id_court: int):
    return court_crud.get_unavailable_schedules(id_court)

@router.get("/courts/{id_court}/available")
def get_available_schedules(id_court: int):
    return court_crud.get_available_schedules(id_court)

@router.post("/bookings")
def make_booking(req: BookingRequest):
    result = court_crud.make_booking_with_schedule(
        req.id_user, req.id_court, req.schedule_date, req.start_time, req.end_time
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.put("/bookings/{id_booking}/status")
def update_booking_status(id_booking: int, req: UpdateBookingStatus):
    result = court_crud.update_booking_status(id_booking, req.new_status)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/users/{id_user}/bookings/pending")
def get_user_pending_bookings(id_user: int):
    return court_crud.get_user_pending_bookings(id_user)

@router.get("/users/{id_user}/bookings/confirmed")
def get_user_confirmed_bookings(id_user: int):
    return court_crud.get_user_confirmed_bookings(id_user)

@router.get("/court-types")
def get_all_court_types():
    result = court_crud.get_all_court_types()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# Monta el router con el prefijo
app.include_router(router, prefix=API_PREFIX)
