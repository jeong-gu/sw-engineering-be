from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import room,reservation,laptop
from db.init_db import init_db

init_db()


app = FastAPI(
    title="Meeting Room Reservation API",
    description="회의실 예약 프로그램 백엔드 서버",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(laptop.router)
app.include_router(room.router)
app.include_router(reservation.router)

@app.get("/")
def root():
    return {"message": "Meeting Room Reservation API is running"}
