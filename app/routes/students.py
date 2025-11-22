from fastapi import APIRouter, HTTPException
from app.db import get_db_connection
from app.schemas import StudentIn, StudentOut, MatchIn
from psycopg2.errors import UniqueViolation
from app.face.scan import store_face, get_embedding, base64_to_cv2
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
        if student.opt_in_biometric:
            storage_uri = store_face(student)
            embedding = get_embedding(storage_uri)
            cur.execute(
                """
                INSERT INTO FACE_IMAGE (SPID, storage_uri, embedding)
                VALUES (%s, %s, %s)
                """,
                (student.PID, storage_uri, embedding)
            )
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
        print("ERROR: " + str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except AssertionError:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error with face analysis")
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
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

@router.post("/match", response_model=StudentOut)
def get_match(b: MatchIn):
    
    conn = get_db_connection()
    try:
        im = base64_to_cv2(b.photo)
        embedding = get_embedding(im)
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                face_id,
                SPID,
                storage_uri,
                embedding <=> %s::vector AS distance
            FROM FACE_IMAGE
            ORDER BY embedding <=> %s::vector
            LIMIT 1;
            """, (embedding_str, embedding_str))
        student_pid = cur.fetchone()[1]
        cur.execute(
            """
            SELECT PID, name, email, degree_name, degree_type, opt_in_biometric
            FROM STUDENT
            WHERE PID = %s
            """,
            (student_pid,)
        )
        r = cur.fetchone()
        conn.commit()
        return {
            "PID": r[0],
            "name": r[1],
            "email": r[2],
            "degree_name": r[3],
            "degree_type": r[4],
            "opt_in_biometric": r[5],
        }
        
    except psycopg2.Error as e:
        conn.rollback()
        print("ERROR: " + str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        conn.rollback
        print("ERROR: " + str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close(); conn.close()
