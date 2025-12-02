from fastapi import APIRouter, HTTPException
import psycopg2
from app.db import get_db_connection


router = APIRouter(prefix="/api/degrees", tags=["degrees"])

@router.get("/", response_model=list[str])
def get_all_degrees():
    """
    Returns a list of all degree names
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT degree_name FROM DEGREE ORDER BY degree_name;")
        rows = cur.fetchall()  # returns list of tuples
        degree_names = [row[0] for row in rows]
        return degree_names
    except Exception as e:
        print(f"ERROR fetching degrees: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch degrees")
    finally:
        conn.close()