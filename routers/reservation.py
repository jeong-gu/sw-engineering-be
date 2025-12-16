# routers/reservation.py

from fastapi import APIRouter, HTTPException
from schemas.reservation import ReservationCreate, ReservationResponse

router = APIRouter(
    prefix="/api/reservations",
    tags=["Reservations"]
)

# 임시 저장소
RESERVATIONS = []
RESERVATION_SEQ = 1


def is_time_overlap(room_id, date, start, end):
    for r in RESERVATIONS:
        if r["room_id"] == room_id and r["date"] == date:
            if start < r["end_time"] and end > r["start_time"]:
                return True
    return False


@router.post("/", response_model=ReservationResponse)
def create_reservation(req: ReservationCreate):
    global RESERVATION_SEQ

    # 운영 시간 검증 (09~18)
    if req.start_time < 9 or req.end_time > 18:
        raise HTTPException(status_code=400, detail="운영 시간은 09~18시입니다")

    # 1시간 단위 검증
    if req.end_time - req.start_time != 1:
        raise HTTPException(status_code=400, detail="회의실은 1시간 단위로 예약 가능합니다")

    # 시간 중복 검증
    if is_time_overlap(req.room_id, req.date, req.start_time, req.end_time):
        raise HTTPException(status_code=409, detail="이미 예약된 시간대입니다")

    reservation = {
        "id": RESERVATION_SEQ,
        "room_id": req.room_id,
        "date": req.date,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "participants": req.participants,
    }

    RESERVATIONS.append(reservation)
    RESERVATION_SEQ += 1

    return reservation
