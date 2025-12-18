import pytest
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from db.session import get_db
from db.base import Base

from models.laptop_reservation import LaptopReservation


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def today_str() -> str:
    return date.today().isoformat()


def participants_ok(prefix: str = "202500"):
    return [f"{prefix}01", f"{prefix}02", f"{prefix}03"]


def payload(room_id=1, date_s=None, start=9, end=10, participants=None):
    if date_s is None:
        date_s = today_str()
    if participants is None:
        participants = participants_ok("202500")
    return {
        "room_id": room_id,
        "date": date_s,
        "start_time": start,
        "end_time": end,
        "participants": participants,
    }


# 1. 정상 예약 생성 성공
def test_create_reservation_success_200(client):
    r = client.post("/api/reservations/", json=payload())
    assert r.status_code == 200


# 2. 참여자 학번 중복이면 400
def test_create_reservation_duplicate_participants_400(client):
    dup = payload(participants=["20250001", "20250001", "20250003"])
    r = client.post("/api/reservations/", json=dup)
    assert r.status_code == 400
    assert "중복" in r.json()["detail"]


# 3. 같은 슬롯 중복 예약이면 409
def test_create_reservation_same_slot_conflict_409(client):
    assert client.post("/api/reservations/", json=payload()).status_code == 200
    r2 = client.post("/api/reservations/", json=payload())
    assert r2.status_code == 409


# 4. 인접 슬롯은 허용(09~10 후 10~11 성공)
def test_create_reservation_adjacent_slot_allowed_200(client):
    assert client.post(
        "/api/reservations/",
        json=payload(start=9, end=10, participants=participants_ok("301000")),
    ).status_code == 200

    assert client.post(
        "/api/reservations/",
        json=payload(start=10, end=11, participants=participants_ok("301001")),
    ).status_code == 200


# 5. 노트북 예약과 동시간 충돌이면 409
def test_create_reservation_laptop_conflict_409(client, db_session):
    reserver = participants_ok("202500")[0]

    db_session.add(
        LaptopReservation(
            seat_number=1,
            date=today_str(),
            start_time=9,
            end_time=10,
            reserver_id=reserver,
        )
    )
    db_session.commit()

    r = client.post("/api/reservations/", json=payload(start=9, end=10))
    assert r.status_code == 409


# 6. 하루 최대 2시간 제한 초과면 400
def test_create_reservation_daily_limit_400(client):
    d = today_str()

    assert client.post(
        "/api/reservations/",
        json=payload(date_s=d, start=9, end=10, participants=participants_ok("401000")),
    ).status_code == 200

    assert client.post(
        "/api/reservations/",
        json=payload(date_s=d, start=10, end=11, participants=participants_ok("401001")),
    ).status_code == 200

    r = client.post(
        "/api/reservations/",
        json=payload(date_s=d, start=11, end=12, participants=participants_ok("401002")),
    )
    assert r.status_code == 400
    assert "하루 최대 2시간" in r.json()["detail"]


# 7. 주간 최대 5시간 제한 초과면 400 (조건 충족 불가 시 skip)
def test_create_reservation_weekly_limit_400(client):
    today = date.today()
    remaining_in_week = 7 - today.weekday()  # 월0~일6

    if remaining_in_week < 4:
        pytest.skip("7일 예약 제한 + 주 경계 때문에 주간 제한(6시간) 케이스 구성 불가")

    d0 = today.isoformat()
    d1 = (today + timedelta(days=1)).isoformat()
    d2 = (today + timedelta(days=2)).isoformat()
    d3 = (today + timedelta(days=3)).isoformat()

    assert client.post(
        "/api/reservations/",
        json=payload(date_s=d0, start=9, end=10, participants=participants_ok("501000")),
    ).status_code == 200
    assert client.post(
        "/api/reservations/",
        json=payload(date_s=d0, start=10, end=11, participants=participants_ok("501001")),
    ).status_code == 200

    assert client.post(
        "/api/reservations/",
        json=payload(date_s=d1, start=9, end=10, participants=participants_ok("501002")),
    ).status_code == 200
    assert client.post(
        "/api/reservations/",
        json=payload(date_s=d1, start=10, end=11, participants=participants_ok("501003")),
    ).status_code == 200

    assert client.post(
        "/api/reservations/",
        json=payload(date_s=d2, start=9, end=10, participants=participants_ok("501004")),
    ).status_code == 200

    r = client.post(
        "/api/reservations/",
        json=payload(date_s=d3, start=9, end=10, participants=participants_ok("501005")),
    )
    assert r.status_code == 400
    assert "주간 최대 5시간" in r.json()["detail"]


# 8. 예약 취소 성공
def test_delete_reservation_success_200(client):
    d = today_str()
    ps = ["90900001", "90900002", "90900003"]

    created = client.post(
        "/api/reservations/",
        json=payload(date_s=d, start=9, end=10, participants=ps),
    )
    assert created.status_code == 200
    rid = created.json()["id"]

    deleted = client.delete(f"/api/reservations/{rid}")
    assert deleted.status_code == 200
