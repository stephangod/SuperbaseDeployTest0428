from datetime import datetime, timedelta  # datetime → 현재 시간 생성, timedelta → 시간 계산 (토큰 만료 시간 설정)

from jose import jwt, JWTError  # jwt → JWT 토큰 생성/디코드 JWTError → 토큰 오류 발생 시 예외 처리

from fastapi import HTTPException  # API에서 에러 발생 시 클라이언트에 응답하기 위한 예외 클래스

import os  # 환경변수 사용 (보안상 중요한 값 관리)

from passlib.context import CryptContext  # 비밀번호 암호화/검증을 위한 라이브러리


# =========================
# 비밀번호 암호화 설정
# =========================
pwd_context = CryptContext(
    schemes=["bcrypt"],     # bcrypt 알고리즘 사용 (가장 안전한 해시 방식 중 하나)
    deprecated="auto"       # 오래된 방식은 자동으로 제외
)
# pwd_context → 비밀번호 해싱 및 검증을 담당하는 객체


# =========================
# JWT 설정
# =========================
SECRET_KEY = os.getenv("SECRET_KEY")  # JWT 서명에 사용할 비밀 키
# 운영에서는 반드시 환경변수로 설정해야 함 (코드에 하드코딩 금지)

ALGORITHM = "HS256"  # JWT 서명 알고리즘 (대칭키 방식)


# =========================
# 비밀번호 해시 (회원가입 시 사용)
# =========================
def hash_password(password: str):
    return pwd_context.hash(password)  # 입력된 평문 비밀번호를 암호화하여 반환, DB에는 이 값만 저장됨 (보안 핵심)


# =========================
# 비밀번호 검증 (로그인 시 사용)
# =========================
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)  # 사용자가 입력한 평문 비밀번호(plain)와 DB에 저장된 해시 비밀번호(hashed)를 비교
                                              # 일치하면 True 반환


# =========================
# Access Token 생성
# =========================
def create_access_token(user_id: int):

    payload = {
        "sub": str(user_id),  
        # subject (표준 필드) → 사용자 식별자 (user_id)

        "type": "access",  
        # 토큰 타입 (access / refresh 구분용)

        "exp": datetime.utcnow() + timedelta(minutes=30)  
        # 토큰 만료 시간 (현재 시간 + 30분)
        # 시간이 지나면 자동으로 사용 불가
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  
    # payload를 SECRET_KEY로 암호화하여 JWT 토큰 생성


# =========================
# 토큰 디코드 (검증)
# =========================
def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        # 토큰을 복호화하면서 유효성 검사 수행
        # (서명, 만료시간 등 자동 검증)

    except JWTError:
        # 토큰이 변조되었거나 만료된 경우
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")  
        # 클라이언트에 401 Unauthorized 응답 반환


# =========================
# 사용자 ID 추출
# =========================
def get_user_id_from_token(token: str):

    payload = decode_token(token)  
    # 먼저 토큰을 디코드해서 payload 가져오기

    if payload.get("type") != "access":  
        # access 토큰이 아닌 경우 (예: refresh 토큰 사용 시)
        raise HTTPException(status_code=401, detail="잘못된 토큰 타입")

    return int(payload.get("sub"))  
    # payload에서 사용자 ID 추출 후 int로 변환하여 반환