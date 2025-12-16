from fastapi import FastAPI
from routers import room

app = FastAPI(
    title="Meeting Room Reservation API",
    description="회의실 예약 프로그램 백엔드 서버",
    version="0.1.0"
)

app.include_router(room.router)

@app.get("/")
def root():
    return {"message": "Meeting Room Reservation API is running"}
