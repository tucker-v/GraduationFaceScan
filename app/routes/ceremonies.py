from fastapi import APIRouter, HTTPException
from app.db import get_db_connection
from app.schemas import CeremonyIn, CeremonyOut

router = APIRouter(prefix="/api/ceremonies", tags=["ceremonies"])

@router.get("/", response_model=list[CeremonyOut])
def list_ceremonies():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT ceremony_id, name, date_time, location, start_time, end_time FROM CEREMONY ORDER BY ceremony_id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [
        {
            "ceremony_id": r[0],
            "name": r[1],
            "date_time": r[2].isoformat(),
            "location": r[3],
            "start_time": str(r[4]),
            "end_time": str(r[5]),
        }
        for r in rows
    ]

@router.post("/", response_model=CeremonyOut)
def insert_ceremony(c: CeremonyIn):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO CEREMONY (name, date_time, location, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING ceremony_id, name, date_time, location, start_time, end_time
        """,
        (c.name, c.date_time, c.location, c.start_time, c.end_time),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close(); conn.close()
    return {
        "ceremony_id": row[0],
        "name": row[1],
        "date_time": row[2].isoformat(),
        "location": row[3],
        "start_time": str(row[4]),
        "end_time": str(row[5]),
    }

@router.put("/{ceremony_id}", response_model=CeremonyOut)
def update_ceremony(ceremony_id: int, c: CeremonyIn):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE CEREMONY 
            SET name = %s, date_time = %s, location = %s, start_time = %s, end_time = %s
            WHERE ceremony_id = %s
            RETURNING ceremony_id, name, date_time, location, start_time, end_time
            """,
            (c.name, c.date_time, c.location, c.start_time, c.end_time, ceremony_id),
        )
        row = cur.fetchone()
        conn.commit()
        if not row:
            raise HTTPException(status_code=404, detail="Ceremony not found")
        return {
            "ceremony_id": row[0],
            "name": row[1],
            "date_time": row[2].isoformat(),
            "location": row[3],
            "start_time": str(row[4]),
            "end_time": str(row[5]),
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close(); conn.close()

@router.delete("/{ceremony_id}")
def delete_ceremony(ceremony_id: int):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM CEREMONY WHERE ceremony_id = %s RETURNING ceremony_id", (ceremony_id,))
    row = cur.fetchone()
    conn.commit()
    cur.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Ceremony not found")
    return {"status": "deleted", "ceremony_id": ceremony_id}
