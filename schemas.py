from pydantic import BaseModel, EmailStr  
# BaseModel → 요청(Request)과 응답(Response) 데이터 구조 정의용 클래스
# EmailStr → 이메일 형식 자동 검증 (잘못된 이메일이면 에러 발생)

from typing import Optional  
# Optional → 값이 있을 수도 있고 없을 수도 있는 필드 정의

from datetime import datetime  
# 날짜/시간 타입 (created_at 등에 사용)


# =========================
# 회원가입 요청 모델
# =========================
class UserCreate(BaseModel):  # 클라이언트 → 서버로 전달되는 데이터 구조

    email: EmailStr  # 이메일 (형식 자동 검증)
    password: str  # 비밀번호 (평문으로 들어오지만 서버에서 암호화됨)
    nickname: str  # 사용자 닉네임
    name: str  # 사용자 이름
    address: str  # 주소
    phone: str  # 전화번호


# =========================
# 로그인 요청 모델
# =========================
class UserLogin(BaseModel):  

    email: EmailStr  # 로그인 ID (이메일)
    password: str  # 비밀번호


# =========================
# 토큰 응답 모델
# =========================
class Token(BaseModel):  

    access_token: str  # JWT 토큰 문자열
    token_type: str  # 보통 "bearer" 사용 (Authorization 헤더에 사용)

# =========================
# 사용자 응답 모델
# =========================
class UserResponse(BaseModel):  

    id: int  # 사용자 고유 ID
    email: EmailStr  # 이메일
    nickname: str  # 닉네임
    name: str  # 이름
    address: str  # 주소
    phone: str  # 전화번호
    created_at: datetime  # 가입 시간

    class Config:  
        orm_mode = True  
        # SQLAlchemy ORM 객체 → 자동으로 JSON 변환 가능하게 설정
        # 예: User 객체 그대로 return 가능


# =========================
# 게시글 생성 요청 모델
# =========================
class PostCreate(BaseModel):  
    title: str  # 게시글 제목
    content: str  # 게시글 내용


# =========================
# 게시글 응답 모델
# =========================
class PostResponse(BaseModel):  

    id: int  # 게시글 ID
    title: str  # 제목
    content: str  # 내용
    user_id: int  # 작성자 ID
    created_at: datetime  # 생성 시간

    class Config:  
        orm_mode = True  
        # ORM 객체를 그대로 반환 가능

# =========================
# 댓글 생성 요청 모델
# =========================
class CommentCreate(BaseModel):  
    text: str  # 댓글 내용


# =========================
# 댓글 응답 모델
# =========================
class CommentResponse(BaseModel):  

    id: int  # 댓글 ID
    text: str  # 댓글 내용
    user_id: int  # 작성자 ID
    post_id: int  # 게시글 ID
    created_at: datetime  # 생성 시간

    class Config:  
        orm_mode = True  
        # ORM → JSON 자동 변환