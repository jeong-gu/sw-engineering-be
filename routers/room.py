# routers/room.py

from fastapi import APIRouter, HTTPException, Query
from datetime import time
from schemas.room import RoomResponse

router = APIRouter(
    prefix="/api/rooms",
    tags=["Rooms"]
)

# 무한상상실 회의실 (고정 자원)
ROOMS = [
    {"id": 1, "name": "무한상상실 1", "capacity": 8, "location": "7호관"},
    {"id": 2, "name": "무한상상실 2", "capacity": 8, "location": "7호관"},
    {"id": 3, "name": "무한상상실 3", "capacity": 8, "location": "7호관"},
]

# 임시 예약 데이터 (date, start_time, end_time)
RESERVATIONS = [
    {"room_id": 1, "date": "2025-12-20", "start": 10, "end": 11},
    {"room_id": 1, "date": "2025-12-20", "start": 14, "end": 15},
]


@router.get("/", response_model=list[RoomResponse])
def get_rooms():
    """
    무한상상실 회의실 목록 조회
    """
    return ROOMS


@router.get("/{room_id}/availability")
def get_room_availability(
    room_id: int,
    date: str = Query(..., description="예약 조회 날짜 (YYYY-MM-DD)")
):
    """
    특정 날짜 기준 회의실 예약 가능 시간 조회
    - 운영 시간: 09~18
    - 1시간 단위
    """
    room = next((r for r in ROOMS if r["id"] == room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail="회의실이 존재하지 않습니다")

    # 운영 시간 슬롯 생성
    all_slots = list(range(9, 18))  # 9~17 → 1시간 단위

    # 이미 예약된 시간
    reserved = [
        slot
        for r in RESERVATIONS
        if r["room_id"] == room_id and r["date"] == date
        for slot in range(r["start"], r["end"])
    ]

    available_slots = [s for s in all_slots if s not in reserved]

    return {
        "room_id": room_id,
        "date": date,
        "available_time_slots": available_slots
    }
