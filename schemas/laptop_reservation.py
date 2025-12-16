# schemas/laptop_reservation.py

from pydantic import BaseModel, Field

class LaptopReservationCreate(BaseModel):
    seat_number: int = Field(..., ge=1, le=70)
    date: str                 # YYYY-MM-DD
    start_time: int           # hour (9~16)
    reserver_id: str          # 학번


class LaptopReservationResponse(BaseModel):
    id: int
    seat_number: int
    date: str
    start_time: int
    end_time: int
    reserver_id: str
