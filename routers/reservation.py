# routers/reservation.py

from fastapi import APIRouter, HTTPException
from schemas.reservation import ReservationCreate, ReservationResponse
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/api/reservations",
    tags=["Reservations"]
)

RESERVATIONS = []
RESERVATION_SEQ = 1


def is_time_overlap(room_id, date, start, end):
    for r in RESERVATIONS:
        if r["room_id"] == room_id and r["date"] == date:
            if start < r["end_time"] and end > r["start_time"]:
                return True
    return False


def get_week_range(date_str: str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start.date(), end.date()


def calculate_user_usage(reserver_id: str, date_str: str):
    """일일 / 주간 누적 사용 시간 계산"""
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    week_start, week_end = get_week_range(date_str)

    daily = 0
    weekly = 0

    for r in RESERVATIONS:
        if r["reserver_id"] != reserver_id:
            continue

        hours = r["end_time"] - r["start_time"]
        r_date = datetime.strptime(r["date"], "%Y-%m-%d").date()

        if r_date == target_date:
            daily += hours

        if week_start <= r_date <= week_end:
            weekly += hours

    return daily, weekly


@router.post("/", response_model=ReservationResponse)
def create_reservation(req: ReservationCreate):
    global RESERVATION_SEQ

    reserver_id = req.participants[0]  # 예약자 = 첫 번째 참석자
    duration = req.end_time - req.start_time

    # 운영 시간 검증
    if req.start_time < 9 or req.end_time > 18:
        raise HTTPException(status_code=400, detail="운영 시간은 09~18시입니다")

    # 1시간 단위
    if duration != 1:
        raise HTTPException(status_code=400, detail="회의실은 1시간 단위로 예약 가능합니다")

    # 시간 중복
    if is_time_overlap(req.room_id, req.date, req.start_time, req.end_time):
        raise HTTPException(status_code=409, detail="이미 예약된 시간대입니다")

    # 🔥 일일 / 주간 이용 제한
    daily, weekly = calculate_user_usage(reserver_id, req.date)

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

    reservation = {
        "id": RESERVATION_SEQ,
        "room_id": req.room_id,
        "date": req.date,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "participants": req.participants,
        "reserver_id": reserver_id,
    }

    RESERVATIONS.append(reservation)
    RESERVATION_SEQ += 1

    return reservation
