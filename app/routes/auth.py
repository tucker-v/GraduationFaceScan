from fastapi import APIRouter, HTTPException, Depends

from app.db import get_db_connection
from app.schemas import (
    UserSignupIn,
    UserLoginIn,
    UserOut,
    ChangePasswordIn,
    CreateAdminIn,
)
from app.auth import (
    create_token,
    verify_password,
    hash_password,
    get_current_user,
    get_current_admin,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(payload: UserLoginIn):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT user_id, username, password_hash, is_admin
            FROM USER_ACCOUNT
            WHERE username = %s
            """,
            (payload.username,),
        )
        row = cur.fetchone()
        if not row or not verify_password(payload.password, row[2]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token(row[0], row[1], row[3])
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "user_id": row[0],
                "username": row[1],
                "is_admin": row[3],
            },
        }
    finally:
        cur.close()
        conn.close()


@router.post("/signup", response_model=UserOut)
def signup(payload: UserSignupIn):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT 1 FROM USER_ACCOUNT WHERE username = %s",
            (payload.username,),
        )
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Username already exists")

        pwd_hash = hash_password(payload.password)
        cur.execute(
            """
            INSERT INTO USER_ACCOUNT (username, password_hash, is_admin)
            VALUES (%s, %s, FALSE)
            RETURNING user_id, username, is_admin
            """,
            (payload.username, pwd_hash),
        )
        row = cur.fetchone()
        conn.commit()
        return UserOut(user_id=row[0], username=row[1], is_admin=row[2])
    finally:
        cur.close()
        conn.close()


@router.post("/change-password")
def change_password(
    payload: ChangePasswordIn,
    current = Depends(get_current_user),
):
    user_id = int(current["sub"])
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT password_hash FROM USER_ACCOUNT WHERE user_id = %s",
            (user_id,),
        )
        row = cur.fetchone()
        if not row or not verify_password(payload.old_password, row[0]):
            raise HTTPException(status_code=401, detail="Old password incorrect")

        new_hash = hash_password(payload.new_password)
        cur.execute(
            """
            UPDATE USER_ACCOUNT
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            """,
            (new_hash, user_id),
        )
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()
        conn.close()


@router.post("/admin/create", response_model=UserOut)
def create_admin(
    payload: CreateAdminIn,
    admin = Depends(get_current_admin),
):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT 1 FROM USER_ACCOUNT WHERE username = %s",
            (payload.username,),
        )
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Username already exists")

        pwd_hash = hash_password(payload.password)
        cur.execute(
            """
            INSERT INTO USER_ACCOUNT (username, password_hash, is_admin)
            VALUES (%s, %s, TRUE)
            RETURNING user_id, username, is_admin
            """,
            (payload.username, pwd_hash),
        )
        row = cur.fetchone()
        conn.commit()
        return UserOut(user_id=row[0], username=row[1], is_admin=row[2])
    finally:
        cur.close()
        conn.close()


@router.post("/logout")
def logout(current = Depends(get_current_user)):
    # Stateless JWT logout: client discards token
    return {"status": "logged_out"}
