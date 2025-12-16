# models/room.py

class Room:
    def __init__(self, id: int, name: str, capacity: int, location: str):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.location = location
