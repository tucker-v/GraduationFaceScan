from fastapi import APIRouter, HTTPException
from app.schemas import QueueIn, DequeueIn, ViewQueueIn
from app.db import get_db_connection
import psycopg2



router = APIRouter(prefix="/api/queue", tags=["queue"])


@router.post("/push")
def add_to_queue(q: QueueIn):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        #get student
        cur.execute(
            "SELECT degree_name FROM STUDENT WHERE PID = %s;",
            (q.SPID,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        degree_name = row[0]
        #get ceremony id
        cur.execute(
            "SELECT ceremony_id FROM DEGREE WHERE degree_name = %s;",
            (degree_name,)
        )
        row = cur.fetchone()
        if not row or row[0] is None:
            raise HTTPException(status_code=400, detail="No ceremony assigned for this degree")
        ceremony_id = row[0]
        cur.execute(
            """
            INSERT INTO QUEUED (SPID, ceremony_id)
            VALUES (%s, %s)
            """,
            (q.SPID, ceremony_id)
        )
        conn.commit()
        return {"message": f"Student {q.SPID} queued for ceremony {ceremony_id}"}
    
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Student is already queued for this ceremony"
        )
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.post("/pop")
def dequeue_next_student(d: DequeueIn):
    conn = get_db_connection()

    try:
        cur = conn.cursor()

        # Get the next pending student in line (and lock row)
        cur.execute(
            """
            SELECT SPID
            FROM QUEUED
            WHERE ceremony_id = %s AND status = 'pending'
            ORDER BY time_queued
            FOR UPDATE SKIP LOCKED
            LIMIT 1;
            """,
            (d.ceremony_id,)
        )

        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="No pending students in queue")

        pid = row[0]

        # Update their status to 'called'
        cur.execute(
            """
            UPDATE QUEUED
            SET status = 'called'
            WHERE SPID = %s AND ceremony_id = %s;
            """,
            (pid, d.ceremony_id)
        )

        # Get student info
        cur.execute(
            """
            SELECT PID, name, email, degree_name, degree_type, opt_in_biometric
            FROM STUDENT
            WHERE PID = %s;
            """,
            (pid,)
        )

        student = cur.fetchone()

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        conn.commit()

        return {
            "PID": student[0],
            "name": student[1],
            "email": student[2],
            "degree_name": student[3],
            "degree_type": student[4],
            "opt_in_biometric": student[5],
            "ceremony_id": d.ceremony_id,
            "status": "called"
        }

    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cur.close()
        conn.close()

@router.post("/view")
def view_queue(v: ViewQueueIn):
    conn = get_db_connection()

    try:
        cur = conn.cursor()

        #get students with status pending
        cur.execute(
            """
            SELECT q.status, s.PID, s.name, s.degree_name, s.degree_type, q.time_queued
            FROM QUEUED q INNER JOIN STUDENT s
            ON q.SPID = s.PID
            WHERE q.ceremony_id = %s AND q.status = 'pending'
            ORDER BY q.time_queued
            """,
            (v.ceremony_id,)
        )
        pending = cur.fetchall()
        cur.execute(
            """
            SELECT q.status, s.PID, s.name, s.degree_name, s.degree_type, q.time_queued
            FROM QUEUED q INNER JOIN STUDENT s
            ON q.SPID = s.PID
            WHERE q.ceremony_id = %s AND q.status = 'called'
            ORDER BY q.time_queued
            """,
            (v.ceremony_id,)
        )
        called = cur.fetchall()

        return {
            'pending': [
                {
                    'PID': p[1],
                    'name': p[2],
                    'degree_name': p[3],
                    'degree_type': p[4],
                    'time_queued': p[5],
                }
                for p in pending
            ],
            'called': [
                {
                    'PID': c[1],
                    'name': c[2],
                    'degree_name': c[3],
                    'degree_type': c[4],
                    'time_queued': c[5],
                }
                for c in called
            ]
        }

    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cur.close()
        conn.close()
