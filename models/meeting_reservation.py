from sqlalchemy import Column, Integer, String,JSON
from db.base import Base

class MeetingReservation(Base):
    __tablename__ = "meeting_reservations"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, index=True)
    date = Column(String, index=True)
    start_time = Column(Integer)
    end_time = Column(Integer)
    reserver_id=Column(String)
    participants = Column(JSON) 
