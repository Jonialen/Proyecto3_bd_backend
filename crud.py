from sqlalchemy.orm import Session
import models, schemas
from datetime import date

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id_user == user_id).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        name=user.name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        id_role=2  # client
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_courts(db: Session):
    return db.query(models.Court).all()

def create_court(db: Session, court: schemas.CourtBase):
    db_court = models.Court(name=court.name, description=court.description)
    db.add(db_court)
    db.commit()
    db.refresh(db_court)
    return db_court

def create_schedule(db: Session, id_court: int, schedule: schemas.ScheduleCreate):
    db_schedule = models.Schedule(
        id_court=id_court,
        schedule_date=schedule.schedule_date,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        price=schedule.price,
        is_available=True
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def get_available_schedules(db: Session, id_court: int, schedule_date: date):
    return db.query(models.Schedule).filter(
        models.Schedule.id_court == id_court,
        models.Schedule.schedule_date == schedule_date,
        models.Schedule.is_available == True
    ).all()

def create_booking(db: Session, user_id: int, schedule_ids: list):
    from sqlalchemy import and_
    schedules = db.query(models.Schedule).filter(
        models.Schedule.id_schedule.in_(schedule_ids),
        models.Schedule.is_available == True
    ).with_for_update().all()
    if len(schedules) != len(schedule_ids):
        raise Exception("Some schedules are not available")
    total_price = sum([float(s.price) for s in schedules])
    booking = models.Booking(
        id_user=user_id,
        booking_date=date.today(),
        status="confirmed"
    )
    db.add(booking)
    db.flush()  # get booking.id_booking
    for s in schedules:
        s.is_available = False
        db.add(models.BookingDetail(id_booking=booking.id_booking, id_schedule=s.id_schedule))
    db.commit()
    db.refresh(booking)
    return booking, schedules, total_price

def get_user_bookings(db: Session, user_id: int):
    bookings = db.query(models.Booking).filter(models.Booking.id_user == user_id).all()
    result = []
    for b in bookings:
        details = db.query(models.BookingDetail).filter(models.BookingDetail.id_booking == b.id_booking).all()
        schedules = [d.schedule for d in details]
        total_price = sum([float(s.price) for s in schedules])
        result.append({"booking": b, "schedules": schedules, "total_price": total_price})
    return result

