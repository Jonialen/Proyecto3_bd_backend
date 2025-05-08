from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, crud, auth, database
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth & Users ---

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(user.password)
    db_user = crud.create_user(db, user, hashed)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = auth.create_access_token({"sub": user.id_user})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# --- Courts ---

@app.get("/courts", response_model=list[schemas.CourtOut])
def list_courts(db: Session = Depends(get_db)):
    return crud.get_courts(db)

@app.post("/courts", response_model=schemas.CourtOut)
def create_court(
    court: schemas.CourtBase,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    return crud.create_court(db, court)

# --- Schedules ---

@app.post("/courts/{id_court}/schedules", response_model=schemas.ScheduleOut)
def create_schedule(
    id_court: int,
    schedule: schemas.ScheduleCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    return crud.create_schedule(db, id_court, schedule)

@app.get("/courts/{id_court}/schedules", response_model=list[schemas.ScheduleOut])
def list_schedules(
    id_court: int,
    schedule_date: str,
    db: Session = Depends(get_db)
):
    from datetime import datetime
    date_obj = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    return crud.get_available_schedules(db, id_court, date_obj)

# --- Bookings ---

@app.post("/bookings", response_model=schemas.BookingOut)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    try:
        booking_obj, schedules, total_price = crud.create_booking(db, user.id_user, booking.schedule_ids)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "id_booking": booking_obj.id_booking,
        "booking_date": booking_obj.booking_date,
        "status": booking_obj.status,
        "schedules": schedules,
        "total_price": total_price
    }

@app.get("/my-bookings", response_model=list[schemas.BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    bookings = crud.get_user_bookings(db, user.id_user)
    return [
        {
            "id_booking": b["booking"].id_booking,
            "booking_date": b["booking"].booking_date,
            "status": b["booking"].status,
            "schedules": b["schedules"],
            "total_price": b["total_price"]
        }
        for b in bookings
    ]

