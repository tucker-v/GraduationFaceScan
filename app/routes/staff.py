from fastapi import APIRouter, HTTPException
from app.db import get_db_connection
from app.schemas import StaffIn, StaffOut
from psycopg2.errors import UniqueViolation
import psycopg2

router = APIRouter(prefix="/api/staff", tags=["staff"])

@router.get("/", response_model=list[StaffOut])
def list_staff():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT staff_id, name, email, status FROM STAFF ORDER BY staff_id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [{"staff_id": r[0], "name": r[1], "email": r[2], "status": r[3]} for r in rows]

@router.post("/", response_model=StaffOut)
def insert_staff(s: StaffIn):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO STAFF (staff_id, name, email, status)
            VALUES (%s, %s, %s, %s)
            RETURNING staff_id, name, email, status
            """,
            (s.staff_id, s.name, s.email, s.status),
        )
        row = cur.fetchone()
        conn.commit()
        return {"staff_id": row[0], "name": row[1], "email": row[2], "status": row[3]}
    except UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="staff_id or email already exists")
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close(); conn.close()

@router.put("/{staff_id}", response_model=StaffOut)
def update_staff(staff_id: str, s: StaffIn):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE STAFF 
            SET name = %s, email = %s, status = %s
            WHERE staff_id = %s
            RETURNING staff_id, name, email, status
            """,
            (s.name, s.email, s.status, staff_id),
        )
        row = cur.fetchone()
        conn.commit()
        if not row:
            raise HTTPException(status_code=404, detail="Staff not found")
        return {"staff_id": row[0], "name": row[1], "email": row[2], "status": row[3]}
    except UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close(); conn.close()

@router.delete("/{staff_id}")
def delete_staff(staff_id: str):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM STAFF WHERE staff_id = %s RETURNING staff_id", (staff_id,))
    row = cur.fetchone()
    conn.commit()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"status": "deleted", "staff_id": staff_id}
