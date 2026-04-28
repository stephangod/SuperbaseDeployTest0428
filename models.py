from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # ⭐ 변경된 부분: String 길이 제한 해제 및 PostgreSQL 최적화
    email = Column(String, unique=True, index=True, nullable=False) # 한글 주석: PostgreSQL은 String 길이를 지정하지 않아도 성능 차이가 거의 없습니다.
    nickname = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String) # 한글 주석: String(100)에서 유연한 String으로 변경되었습니다.
    address = Column(String)
    phone = Column(String)
    # ⭐ 변경된 부분: PostgreSQL의 timestamptz 대응
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 한글 주석: 타임존을 포함하여 전 세계 배포 시 시간 혼선을 방지합니다.

    posts = relationship("Post", back_populates="author", cascade="all, delete")
    comments = relationship("Comment", back_populates="author", cascade="all, delete")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 한글 주석: 게시글 생성 시간에도 타임존 설정을 적용했습니다.

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 한글 주석: 댓글 역시 동일한 시간 형식을 유지합니다.

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")