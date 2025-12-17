# 로컬로 코드 가져오기

## 1. git 설치

## 2. 로컬로 코드 가져오기
```
git clone https://github.com/jeong-gu/sw-engineering-be
cd sw-engineering-be
```

## 3. 가상 환경 세팅 (venv 설치 후 )
```
python -m venv venv
```

## 4. 의존성 패치
```
pip install -r requirements.txt
```

## 5. 서버 시작
```
uvicorn main:app --reload
```

# 커밋 이동 방법

## 1. 커밋 해시 확인
```
git log --oneline
```

## 2. 위 명령어로 해당 커밋 시점으로 코드 후 코드 테스트 진행
```
git checkout {커밋 해시}
```

## 3. 위 명령어로 main branch로 이동 (최신 버전으로 이동)
```
git checkout main
```

## 4. 1 ~ 3 반복 