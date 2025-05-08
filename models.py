from sqlalchemy import (
    Column, Integer, String, ForeignKey, Date, Time, Boolean, Numeric, Text
)
from sqlalchemy.orm import relationship
from database import Base

class Role(Base):
    __tablename__ = "roles"
    id_role = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    id_user = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)
    id_role = Column(Integer, ForeignKey("roles.id_role"), default=2)
    role = relationship("Role")

class Court(Base):
    __tablename__ = "courts"
    id_court = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)

class Schedule(Base):
    __tablename__ = "schedules"
    id_schedule = Column(Integer, primary_key=True, index=True)
    id_court = Column(Integer, ForeignKey("courts.id_court"), nullable=False)
    schedule_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    price = Column(Numeric(8, 2), nullable=False)
    is_available = Column(Boolean, default=True)
    court = relationship("Court")

class Booking(Base):
    __tablename__ = "bookings"
    id_booking = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=False)
    booking_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    user = relationship("User")

class BookingDetail(Base):
    __tablename__ = "booking_details"
    id_booking = Column(Integer, ForeignKey("bookings.id_booking"), primary_key=True)
    id_schedule = Column(Integer, ForeignKey("schedules.id_schedule"), primary_key=True)
    schedule = relationship("Schedule")

