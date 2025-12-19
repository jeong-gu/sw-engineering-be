# 25-2 소프트웨어공학 최종 프로젝트

## Build & Run Guide
본 프로젝트는 FastAPI 기반 백엔드 서버로,
로컬 개발 환경에서 실행 가능하도록 구성되어 있습니다.
별도의 빌드 서버 없이 가상환경으로 **requirements.txt**를 통해 의존성을 관리합니다.

FE Repository: https://github.com/jeong-gu/sw-engineering-final
### Backend Requirements
- Python: 3.10 이상
- pip

### Backend Installation
```bash
git clone https://github.com/jeong-gu/sw-engineering-be
cd sw-engineering-be

python -m venv venv         #가상환경 설정
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### Run Backend Server
```bash
uvicorn main:app --reload
```

### Notes
- 서버 실행 시 SQLite 데이터베이스가 자동으로 생성됩니다.
- 기본 서버 주소: http://127.0.0.1:8000
- API 문서(Swagger UI): http://127.0.0.1:8000/docs