# routers/reservation.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from schemas.reservation import ReservationCreate, ReservationResponse
from models.meeting_reservation import MeetingReservation
from models.laptop_reservation import LaptopReservation
from db.session import get_db

router = APIRouter(
    prefix="/api/reservations",
    tags=["Reservations"]
)

def get_week_range(date_str: str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start.date(), end.date()

@router.post("/", response_model=ReservationResponse)
def create_reservation(
    req: ReservationCreate,
    db: Session = Depends(get_db),
):
    reserver_id = req.participants[0]
    duration = req.end_time - req.start_time

    # 운영 시간
    if req.start_time < 9 or req.end_time > 18:
        raise HTTPException(status_code=400, detail="운영 시간은 09~18시입니다")

    if duration != 1:
        raise HTTPException(status_code=400, detail="회의실은 1시간 단위로 예약 가능합니다")

    # ⛔ 시간 중복 검사 (회의실)
    conflict = db.query(MeetingReservation).filter(
        MeetingReservation.room_id == req.room_id,
        MeetingReservation.date == req.date,
        MeetingReservation.start_time < req.end_time,
        MeetingReservation.end_time > req.start_time,
    ).first()

    if conflict:
        raise HTTPException(status_code=409, detail="이미 예약된 시간대입니다")

    reservations = db.query(MeetingReservation).filter(
        MeetingReservation.date >= get_week_range(req.date)[0].isoformat(),
        MeetingReservation.date <= get_week_range(req.date)[1].isoformat(),
    ).all()

    daily = 0
    weekly = 0
    target_date = req.date

    for r in reservations:
        if r.date == target_date:
            daily += r.end_time - r.start_time
        weekly += r.end_time - r.start_time

    if daily + duration > 2:
        raise HTTPException(
            status_code=400,
            detail="회의실은 하루 최대 2시간까지 이용 가능합니다"
        )

    if weekly + duration > 5:
        raise HTTPException(
            status_code=400,
            detail="회의실은 주간 최대 5시간까지 이용 가능합니다"
        )

    laptop_conflict = db.query(LaptopReservation).filter(
        LaptopReservation.reserver_id == reserver_id,
        LaptopReservation.date == req.date,
        LaptopReservation.start_time < req.end_time,
        LaptopReservation.end_time > req.start_time,
    ).first()

    if laptop_conflict:
        raise HTTPException(
            status_code=409,
            detail="같은 시간에 열람실과 회의실을 동시에 예약할 수 없습니다"
        )

    reservation = MeetingReservation(
        room_id=req.room_id,
        date=req.date,
        start_time=req.start_time,
        end_time=req.end_time,
        reserver_id=reserver_id,
        participants=req.participants,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation

@router.get("/")
def get_reservations(
    date: Optional[str] = None,
    room_id: Optional[int] = None,
    reserver_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(MeetingReservation)

    if date:
        query = query.filter(MeetingReservation.date == date)

    if room_id:
        query = query.filter(MeetingReservation.room_id == room_id)

    return query.all()

@router.delete("/{reservation_id}")
def cancel_meeting_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.query(MeetingReservation).filter(
        MeetingReservation.id == reservation_id
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="회의실 예약을 찾을 수 없습니다")

    db.delete(reservation)
    db.commit()

    return {"message": "회의실 예약이 취소되었습니다"}
