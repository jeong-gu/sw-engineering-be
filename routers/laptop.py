# routers/laptop.py

from fastapi import APIRouter, HTTPException
from schemas.laptop_reservation import (
    LaptopReservationCreate,
    LaptopReservationResponse
)
from datetime import datetime
from storage.reservation import MEETING_RESERVATIONS, LAPTOP_RESERVATIONS
from utils.time_overlap import is_time_overlap

router = APIRouter(
    prefix="/api/laptop-reservations",
    tags=["Laptop Room"]
)

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

    # 🔥 회의실 예약과 시간대 겹침 검사
    for r in MEETING_RESERVATIONS:
        if r["reserver_id"] == req.reserver_id and r["date"] == req.date:
            if is_time_overlap(
                start,
                end,
                r["start_time"],
                r["end_time"]
            ):
                raise HTTPException(
                    status_code=409,
                    detail="같은 시간에 회의실과 열람실을 동시에 예약할 수 없습니다"
                )


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

from typing import Optional

@router.get("/")
def get_laptop_reservations(
    date: Optional[str] = None,
    seat_number: Optional[int] = None,
    reserver_id: Optional[str] = None,
):
    """
    열람실 좌석 예약 조회
    """
    results = LAPTOP_RESERVATIONS

    if date:
        results = [r for r in results if r["date"] == date]

    if seat_number:
        results = [r for r in results if r["seat_number"] == seat_number]

    if reserver_id:
        results = [r for r in results if r["reserver_id"] == reserver_id]

    return results

@router.delete("/{reservation_id}")
def cancel_laptop_reservation(reservation_id: int):
    for i, r in enumerate(LAPTOP_RESERVATIONS):
        if r["id"] == reservation_id:
            LAPTOP_RESERVATIONS.pop(i)
            return {"message": "열람실 예약이 취소되었습니다"}

    raise HTTPException(status_code=404, detail="열람실 예약을 찾을 수 없습니다")