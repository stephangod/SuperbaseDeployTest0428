# =========================
# DB 세션 및 SQL 함수 import
# =========================
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy import func  # ⭐ 추가

# =========================
# 모델 import
# =========================
from models import User, Post, Comment

# =========================
# 비밀번호 암호화 함수
# =========================
from auth import hash_password


# =========================
# 회원가입
# =========================
def create_user(db: Session, user):

    db_user = User(
        email=user.email,
        nickname=user.nickname,
        password=hash_password(user.password),
        name=user.name,
        address=user.address,
        phone=user.phone
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# =========================
# 로그인 (이메일 조회)
# =========================
def get_user_by_email(db: Session, email: str):

    return db.query(User)\
        .filter(User.email == email)\
        .first()


# =========================
# 게시글 생성
# =========================
def create_post(db: Session, user_id: int, post):

    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=user_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# ============================================================
# 게시글 목록 조회 함수 (검색, 페이징, 댓글 수 포함)
# ============================================================
def get_posts(db: Session, keyword: str = None, skip: int = 0, limit: int = 10):
    # 1. 기본 쿼리 설계: Post 테이블을 조회하면서 각 게시글(Post)에 달린 댓글(Comment)의 개수를 셉니다.
    # func.count(Comment.id)는 댓글의 ID 개수를 세는 함수이며, 결과 컬럼명을 "comment_count"로 지정합니다.
    query = db.query(
        Post,
        func.count(Comment.id).label("comment_count")
    ).outerjoin(Comment).group_by(Post.id) 
    # .outerjoin(Comment): 댓글이 없는 게시글도 나와야 하므로 '외부 조인'을 수행합니다.
    # .group_by(Post.id): 게시글별로 댓글 개수를 묶어서 계산하기 위해 그룹화합니다.

    # 2. 검색 필터링: 사용자가 입력한 검색어(keyword)가 있을 때만 작동합니다.
    if keyword:
        # filter()와 or_()를 사용하여 제목(title) 또는 내용(content) 중 하나라도 
        # 검색어가 포함(ilike)되어 있으면 결과에 포함시킵니다.
        # f"%{keyword}%"는 앞뒤에 어떤 글자가 와도 상관없는 '포함' 검색을 의미합니다.
        query = query.filter(
            or_(
                Post.title.ilike(f"%{keyword}%"),
                Post.content.ilike(f"%{keyword}%")
            )
        )

    # 3. 데이터 카운트: 검색 조건이 모두 적용된 최종 쿼리를 바탕으로 전체 게시글 개수를 구합니다.
    # 이 값은 프론트엔드의 페이징(Pagination) 버튼 개수를 결정하는 데 사용됩니다.
    total = query.count()

    # 4. 페이징 및 정렬: 실제 화면에 보여줄 데이터 조각을 가져옵니다.
    # .order_by(Post.id.desc()): 최신글이 위로 오도록 게시글 ID 역순으로 정렬합니다.
    # .offset(skip): 앞부분의 데이터(이미 지난 페이지)를 건너뜁니다.
    # .limit(limit): 한 페이지에 보여줄 데이터 개수만큼만 가져옵니다.
    results = query.order_by(Post.id.desc())\
                   .offset(skip)\
                   .limit(limit)\
                   .all()

    # 5. 데이터 가공: DB에서 가져온 로우(Row) 데이터를 리액트가 읽기 편한 JSON(Dict) 형태로 변환합니다.
    items = []
    for p, count in results:
        items.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "user_id": p.user_id,
            # 작성자(author) 정보가 있으면 닉네임을, 없으면 "알수없음"을 표시합니다.
            "nickname": p.author.nickname if p.author else "알수없음",
            "comment_count": count # 위에서 계산한 댓글 개수를 할당합니다.
        })

    # 6. 최종 응답: 전체 개수와 가공된 게시글 리스트를 함께 반환합니다.
    return {"total": total, "items": items}

# =========================
# 게시글 수정
# =========================
def update_post(db: Session, post_id: int, user_id: int, post):

    p = db.query(Post).filter(Post.id == post_id).first()

    if not p or p.user_id != user_id:
        return None

    p.title = post.title
    p.content = post.content

    db.commit()
    db.refresh(p)

    return p


# =========================
# 게시글 삭제
# =========================
def delete_post(db: Session, post_id: int, user_id: int):

    p = db.query(Post).filter(Post.id == post_id).first()

    if not p or p.user_id != user_id:
        return False

    db.delete(p)
    db.commit()

    return True


# =========================
# 댓글 생성
# =========================
def create_comment(db: Session, user_id: int, post_id: int, comment):

    c = Comment(
        text=comment.text,
        user_id=user_id,
        post_id=post_id
    )

    db.add(c)
    db.commit()
    db.refresh(c)

    return c


# =========================
# 댓글 조회
# =========================
def get_comments(db: Session, post_id: int):

    return db.query(Comment)\
        .filter(Comment.post_id == post_id)\
        .order_by(Comment.id.desc())\
        .all()


# =========================
# 댓글 수정
# =========================
def update_comment(db: Session, comment_id: int, user_id: int, comment):

    c = db.query(Comment).filter(Comment.id == comment_id).first()

    if not c or c.user_id != user_id:
        return None

    c.text = comment.text

    db.commit()
    db.refresh(c)

    return c


# =========================
# 댓글 삭제
# =========================
def delete_comment(db: Session, comment_id: int, user_id: int):

    c = db.query(Comment).filter(Comment.id == comment_id).first()

    if not c or c.user_id != user_id:
        return False

    db.delete(c)
    db.commit()

    return True