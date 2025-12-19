from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from schemas.laptop_reservation import (
    LaptopReservationCreate,
    LaptopReservationResponse,
)
from models.laptop_reservation import LaptopReservation
from models.meeting_reservation import MeetingReservation
from db.session import get_db

router = APIRouter(
    prefix="/api/laptop-reservations",
    tags=["Laptop Room"]
)

@router.post("/", response_model=LaptopReservationResponse)
def create_laptop_reservation(
    req: LaptopReservationCreate,
    db: Session = Depends(get_db),
):
    # 1️⃣ 운영 시간 (2시간 단위 → 09~16 시작)
    if req.start_time < 9 or req.start_time > 16:
        raise HTTPException(
            status_code=400,
            detail="열람실은 09~16시 시작만 가능합니다"
        )

    start = req.start_time
    end = start + 2

    conflict = db.query(LaptopReservation).filter(
        LaptopReservation.seat_number == req.seat_number,
        LaptopReservation.date == req.date,
        LaptopReservation.start_time < end,
        LaptopReservation.end_time > start,
    ).first()

    if conflict:
        raise HTTPException(
            status_code=409,
            detail="이미 예약된 좌석입니다"
        )

    daily_reservations = db.query(LaptopReservation).filter(
        LaptopReservation.reserver_id == req.reserver_id,
        LaptopReservation.date == req.date,
    ).all()

    used_hours = sum(
        r.end_time - r.start_time for r in daily_reservations
    )

    if used_hours + 2 > 4:
        raise HTTPException(
            status_code=400,
            detail="열람실은 하루 최대 4시간 이용 가능합니다"
        )

    meeting_conflict = db.query(MeetingReservation).filter(
        MeetingReservation.reserver_id == req.reserver_id,
        MeetingReservation.date == req.date,
        MeetingReservation.start_time < end,
        MeetingReservation.end_time > start,
    ).first()

    if meeting_conflict:
        raise HTTPException(
            status_code=409,
            detail="같은 시간에 회의실과 열람실을 동시에 예약할 수 없습니다"
        )

    reservation = LaptopReservation(
        seat_number=req.seat_number,
        date=req.date,
        start_time=start,
        end_time=end,
        reserver_id=req.reserver_id,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation

@router.get("/availability")
def get_laptop_reservations_availability(
    date: Optional[str] = None,
    seat_number: Optional[int] = None,
    reserver_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(LaptopReservation)

    if date:
        query = query.filter(LaptopReservation.date == date)

    if seat_number:
        query = query.filter(LaptopReservation.seat_number == seat_number)

    return query.all()

@router.get("/")
def get_laptop_reservations(
    date: Optional[str] = None,
    seat_number: Optional[int] = None,
    reserver_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(LaptopReservation)

    if date:
        query = query.filter(LaptopReservation.date == date)

    if seat_number:
        query = query.filter(LaptopReservation.seat_number == seat_number)

    if reserver_id:
        query = query.filter(LaptopReservation.reserver_id == reserver_id)

    return query.all()

@router.delete("/{reservation_id}")
def cancel_laptop_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.query(LaptopReservation).filter(
        LaptopReservation.id == reservation_id
    ).first()

    if not reservation:
        raise HTTPException(
            status_code=404,
            detail="열람실 예약을 찾을 수 없습니다"
        )

    db.delete(reservation)
    db.commit()

    return {"message": "열람실 예약이 취소되었습니다"}

import random
from schemas.laptop_reservation import LaptopReservationRandomCreate

@router.post("/random", response_model=LaptopReservationResponse)
def create_random_laptop_reservation(
    req: LaptopReservationRandomCreate,
    db: Session = Depends(get_db),
):
    # 1️⃣ 운영 시간
    if req.start_time < 9 or req.start_time > 16:
        raise HTTPException(
            status_code=400,
            detail="열람실은 09~16시 시작만 가능합니다"
        )

    start = req.start_time
    end = start + 2

    # 2️⃣ 하루 사용량 제한 (4시간)
    daily_reservations = db.query(LaptopReservation).filter(
        LaptopReservation.reserver_id == req.reserver_id,
        LaptopReservation.date == req.date,
    ).all()

    used_hours = sum(r.end_time - r.start_time for r in daily_reservations)

    if used_hours + 2 > 4:
        raise HTTPException(
            status_code=400,
            detail="열람실은 하루 최대 4시간 이용 가능합니다"
        )

    # 3️⃣ 회의실과 시간 겹침 검사
    meeting_conflict = db.query(MeetingReservation).filter(
        MeetingReservation.reserver_id == req.reserver_id,
        MeetingReservation.date == req.date,
        MeetingReservation.start_time < end,
        MeetingReservation.end_time > start,
    ).first()

    if meeting_conflict:
        raise HTTPException(
            status_code=409,
            detail="같은 시간에 회의실과 열람실을 동시에 예약할 수 없습니다"
        )

    # 4️⃣ 이미 예약된 좌석 조회
    occupied_seats = db.query(LaptopReservation.seat_number).filter(
        LaptopReservation.date == req.date,
        LaptopReservation.start_time < end,
        LaptopReservation.end_time > start,
    ).all()

    occupied_seats = {s[0] for s in occupied_seats}

    # 5️⃣ 빈 좌석 계산 (1 ~ 70)
    available_seats = [
        seat for seat in range(1, 71)
        if seat not in occupied_seats
    ]

    if not available_seats:
        raise HTTPException(
            status_code=409,
            detail="예약 가능한 좌석이 없습니다"
        )

    # 6️⃣ 랜덤 선택
    seat = random.choice(available_seats)

    reservation = LaptopReservation(
        seat_number=seat,
        date=req.date,
        start_time=start,
        end_time=end,
        reserver_id=req.reserver_id,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation
