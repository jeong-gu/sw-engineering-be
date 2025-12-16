from sqlalchemy import Column, Integer, String
from db.base import Base

class LaptopReservation(Base):
    __tablename__ = "laptop_reservations"

    id = Column(Integer, primary_key=True, index=True)
    seat_number = Column(Integer, index=True)
    date = Column(String, index=True)
    start_time = Column(Integer)
    end_time = Column(Integer)
    reserver_id = Column(String)
