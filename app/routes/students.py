from fastapi import APIRouter, HTTPException
from app.db import get_db_connection
from app.schemas import StudentIn, StudentOut
from psycopg2.errors import UniqueViolation
import psycopg2

router = APIRouter(prefix="/api/students", tags=["students"])

@router.get("/", response_model=list[StudentOut])
def list_students():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT PID, name, email, degree_name, degree_type, opt_in_biometric FROM STUDENT ORDER BY PID")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [
        {
            "PID": r[0],
            "name": r[1],
            "email": r[2],
            "degree_name": r[3],
            "degree_type": r[4],
            "opt_in_biometric": r[5],
        }
        for r in rows
    ]

@router.post("/", response_model=StudentOut)
def insert_student(student: StudentIn):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO STUDENT (PID, name, email, degree_name, degree_type, opt_in_biometric)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING PID, name, email, degree_name, degree_type, opt_in_biometric
            """,
            (student.PID, student.name, student.email, student.degree_name, student.degree_type, student.opt_in_biometric),
        )
        row = cur.fetchone()
        conn.commit()
        return {
            "PID": row[0], "name": row[1], "email": row[2],
            "degree_name": row[3], "degree_type": row[4],
            "opt_in_biometric": row[5]
        }
    except UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="PID or email already exists")
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close(); conn.close()

@router.delete("/{pid}")
def delete_student(pid: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM STUDENT WHERE PID = %s RETURNING PID", (pid,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close(); conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"status": "deleted", "PID": pid}
