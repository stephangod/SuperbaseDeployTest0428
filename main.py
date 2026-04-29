# =========================
# FastAPI 및 필수 모듈 import
# =========================
from fastapi import FastAPI, Depends, HTTPException, Query, Header, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware



from sqlalchemy.orm import Session

from database import SessionLocal, engine
import models, schemas, crud

from auth import (
    create_access_token,
    verify_password,
    get_user_id_from_token,
    decode_token
)

from models import User

# =========================
# DB 생성
# =========================
models.Base.metadata.create_all(bind=engine)

# =========================
# FastAPI 앱 생성
# =========================
app = FastAPI()

# =========================
# CORS 설정
# =========================
# ⭐ 변경된 부분: 배포 환경에 맞는 CORS 설정
# 배포 후 Vercel 주소가 확정되면 여기에 추가해야 합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "react-deployment-test-0429.vercel.app" # 한글 주석: 프론트엔드 배포 주소를 추가하여 CORS 차단을 방지합니다.
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# =========================
# DB 연결
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# 현재 사용자
# =========================
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401)

    token = authorization.replace("Bearer ", "")
    return get_user_id_from_token(token)

# =========================
# JWT 설정
# =========================
from datetime import datetime, timedelta
from jose import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# =========================
# refresh token 생성
# =========================
def create_refresh_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# refresh 검증
# =========================
def verify_refresh_token(token: str):
    if not token:
        raise HTTPException(status_code=401)

    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401)

    return int(payload.get("sub"))

# =========================
# REGISTER
# =========================
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

# =========================
# LOGIN
# =========================
@app.post("/login")
def login(user: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401)

    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 7
    )

    return {
        "access_token": access_token,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "nickname": db_user.nickname
        }
    }

# =========================
# REFRESH
# =========================
@app.post("/refresh")
def refresh(refresh_token: str = Cookie(None), db: Session = Depends(get_db)):

    if not refresh_token:
        raise HTTPException(status_code=401)

    user_id = verify_refresh_token(refresh_token)

    user = db.query(User).filter(User.id == user_id).first()

    return {
        "access_token": create_access_token(user_id),
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname
        }
    }

# =========================
# LOGOUT
# =========================
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "로그아웃 완료"}

# =========================
# POSTS 목록
# =========================
# @app.get("/posts")
# def get_posts(keyword: str = Query(None), db: Session = Depends(get_db)):
#     return crud.get_posts(db, keyword)

# =========================
# POSTS 목록 (페이징 + 검색)
# =========================
@app.get("/posts")
def get_posts(
    keyword: str = Query("", description="검색어"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size

    return crud.get_posts(
        db,
        keyword=keyword,
        skip=skip,
        limit=size
    )

# =========================
# 🔥 게시글 상세조회 추가 (핵심)
# =========================
@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="게시글 없음")

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id,
        "nickname": post.author.nickname if post.author else None
    }

# =========================
# POST CREATE
# =========================
@app.post("/posts")
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    return crud.create_post(db, user_id, post)

#추가
# =========================
# 🔥 POST UPDATE 추가 (핵심)
# =========================
@app.put("/posts/{post_id}")
def update_post(
    post_id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    result = crud.update_post(db, post_id, user_id, post)

    if not result:
        raise HTTPException(status_code=403, detail="수정 권한 없음")

    return {
        "id": result.id,
        "title": result.title,
        "content": result.content,
        "user_id": result.user_id
    }

# =========================
# POST DELETE
# =========================
@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    if not crud.delete_post(db, post_id, user_id):
        raise HTTPException(status_code=403)

    return {"message": "삭제 완료"}

# =========================
# 🔥 댓글 조회 추가 (핵심)
# =========================
@app.get("/posts/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):

    comments = crud.get_comments(db, post_id)

    return [
        {
            "id": c.id,
            "text": c.text,
            "user_id": c.user_id,
            "nickname": c.author.nickname if c.author else None
        }
        for c in comments
    ]

# =========================
# COMMENT CREATE
# =========================
@app.post("/posts/{post_id}/comments")
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    return crud.create_comment(db, user_id, post_id, comment)

# =========================
# COMMENT UPDATE
# =========================
@app.put("/comments/{comment_id}")
def update_comment(
    comment_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    result = crud.update_comment(db, comment_id, user_id, comment)

    if not result:
        raise HTTPException(status_code=403)

    return result

# =========================
# COMMENT DELETE
# =========================
@app.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    if not crud.delete_comment(db, comment_id, user_id):
        raise HTTPException(status_code=403)

    return {"message": "댓글 삭제 완료"}