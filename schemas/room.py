# schemas/room.py

from pydantic import BaseModel

class RoomBase(BaseModel):
    name: str
    capacity: int
    location: str


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True
