from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

import pytest
from fastapi.testclient import TestClient
from main import app
from db.session import SessionLocal
from models.laptop_reservation import LaptopReservation

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_laptop_reservations():
    """
    각 테스트 실행 전에 열람실 예약 테이블 초기화
    """
    db = SessionLocal()
    db.query(LaptopReservation).delete()
    db.commit()
    db.close()

#정상 예약
def test_laptop_reservation_success():
    response = client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 1,
            "date": "2025-01-10",
            "start_time": 9,
            "reserver_id": "202017832"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["seat_number"] == 1
    assert data["start_time"] == 9
    assert data["end_time"] == 11

#운영 시간 위반
def test_laptop_reservation_fail_invalid_time():
    response = client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 2,
            "date": "2025-01-10",
            "start_time": 8,  # ❌ 운영 시간 아님
            "reserver_id": "202017832"
        }
    )

    assert response.status_code == 400
    assert "09~16시" in response.json()["detail"]

#좌석 중복 예약
def test_laptop_reservation_fail_conflict_seat():
    payload = {
        "seat_number": 3,
        "date": "2025-01-11",
        "start_time": 10,
        "reserver_id": "202017832"
    }

    # 첫 예약
    client.post("/api/laptop-reservations/", json=payload)

    # 같은 좌석, 같은 시간 예약 시도
    response = client.post("/api/laptop-reservations/", json=payload)

    assert response.status_code == 409
    assert "이미 예약된 좌석" in response.json()["detail"]

#하루 최대 4시간 초과
def test_laptop_reservation_fail_daily_limit():
    # 첫 예약 (2시간)
    client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 4,
            "date": "2025-01-12",
            "start_time": 9,
            "reserver_id": "202017832"
        }
    )

    # 두 번째 예약 (2시간)
    client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 5,
            "date": "2025-01-12",
            "start_time": 11,
            "reserver_id": "202017832"
        }
    )

    # 세 번째 예약 → 6시간 ❌
    response = client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 6,
            "date": "2025-01-12",
            "start_time": 13,
            "reserver_id": "202017832"
        }
    )

    assert response.status_code == 400
    assert "하루 최대 4시간" in response.json()["detail"]

#같은 시간에 두 자리 예약
def test_laptop_same_user_same_time_two_seats_allowed():
    # 첫 번째 좌석 예약
    res1 = client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 20,
            "date": "2025-04-01",
            "start_time": 9,
            "reserver_id": "202017832"
        }
    )

    # 두 번째 좌석 예약 (같은 사람, 같은 시간, 다른 좌석)
    res2 = client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 21,
            "date": "2025-04-01",
            "start_time": 9,
            "reserver_id": "202017832"
        }
    )

    assert res1.status_code == 200
    assert res2.status_code == 200

#메모리 저장 성공
def test_laptop_reservation_stored_in_memory():
    response = client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 1,
            "date": "2025-01-01",
            "start_time": 9,
            "reserver_id": "202017832"
        }
    )

    assert response.status_code == 200

    # 조회 API로 확인 (메모리)
    res = client.get("/api/laptop-reservations/")
    data = res.json()

    assert len(data) == 1
    assert data[0]["seat_number"] == 1

from db.session import SessionLocal
from models.laptop_reservation import LaptopReservation

#DB 저장 성공
def test_laptop_reservation_persisted_in_database():
    # 예약 생성
    response = client.post(
        "/api/laptop-reservations/",
        json={
            "seat_number": 30,
            "date": "2025-05-01",
            "start_time": 9,
            "reserver_id": "202017832"
        }
    )

    assert response.status_code == 200

    # DB 직접 조회
    db = SessionLocal()
    reservation = db.query(LaptopReservation).filter(
        LaptopReservation.seat_number == 30,
        LaptopReservation.date == "2025-05-01"
    ).first()
    db.close()

    assert reservation is not None
    assert reservation.start_time == 9
    assert reservation.end_time == 11