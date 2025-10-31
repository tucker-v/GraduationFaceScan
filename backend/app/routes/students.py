from fastapi import APIRouter, HTTPException
from ..db import get_db_connection

router = APIRouter(prefix="/students", tags=["items"])

@router.get("/")
def get_students():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT PID, name FROM STUDENT")
    items = cur.fetchall()
    cur.close()
    conn.close()
    return [{"PID": i[0], "name": i[1]} for i in items]
