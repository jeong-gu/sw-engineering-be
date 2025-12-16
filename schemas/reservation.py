# schemas/reservation.py

from pydantic import BaseModel, Field
from typing import List

class ReservationCreate(BaseModel):
    room_id: int
    date: str              # YYYY-MM-DD
    start_time: int        # hour (9~17)
    end_time: int          # hour (10~18)
    participants: List[str] = Field(..., min_items=3, max_items=8)


class ReservationResponse(BaseModel):
    id: int
    room_id: int
    date: str
    start_time: int
    end_time: int
    participants: List[str]
