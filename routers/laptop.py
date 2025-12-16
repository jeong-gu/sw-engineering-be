# routers/laptop.py

from fastapi import APIRouter, HTTPException
from schemas.laptop_reservation import (
    LaptopReservationCreate,
    LaptopReservationResponse
)
from datetime import datetime

router = APIRouter(
    prefix="/api/laptop-reservations",
    tags=["Laptop Room"]
)

LAPTOP_RESERVATIONS = []
LAPTOP_SEQ = 1


def is_overlap(seat, date, start, end):
    for r in LAPTOP_RESERVATIONS:
        if r["seat_number"] == seat and r["date"] == date:
            if start < r["end_time"] and end > r["start_time"]:
                return True
    return False


def get_daily_usage(reserver_id, date):
    total = 0
    for r in LAPTOP_RESERVATIONS:
        if r["reserver_id"] == reserver_id and r["date"] == date:
            total += (r["end_time"] - r["start_time"])
    return total


@router.post("/", response_model=LaptopReservationResponse)
def create_laptop_reservation(req: LaptopReservationCreate):
    global LAPTOP_SEQ

    # 1️⃣ 운영 시간 + 2시간 단위
    if req.start_time < 9 or req.start_time > 16:
        raise HTTPException(status_code=400, detail="열람실은 09~16시 시작만 가능합니다")

    start = req.start_time
    end = start + 2

    # 2️⃣ 시간 중복
    if is_overlap(req.seat_number, req.date, start, end):
        raise HTTPException(status_code=409, detail="이미 예약된 좌석입니다")

    # 3️⃣ 일일 4시간 제한
    used = get_daily_usage(req.reserver_id, req.date)
    if used + 2 > 4:
        raise HTTPException(status_code=400, detail="열람실은 하루 최대 4시간 이용 가능합니다")

    reservation = {
        "id": LAPTOP_SEQ,
        "seat_number": req.seat_number,
        "date": req.date,
        "start_time": start,
        "end_time": end,
        "reserver_id": req.reserver_id
    }

    LAPTOP_RESERVATIONS.append(reservation)
    LAPTOP_SEQ += 1

    return reservation
