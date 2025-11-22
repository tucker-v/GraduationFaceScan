from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentIn(BaseModel):
    PID: str
    name: str
    email: EmailStr
    degree_name: Optional[str] = None
    degree_type: Optional[str] = None
    opt_in_biometric: bool = False
    photo: Optional[str] = None

class StudentOut(BaseModel):
    PID: str
    name: str
    email: EmailStr
    degree_name: Optional[str] = None
    degree_type: Optional[str] = None
    opt_in_biometric: bool

class CeremonyIn(BaseModel):
    name: str
    date_time: str
    location: str
    start_time: str
    end_time: str

class CeremonyOut(CeremonyIn):
    ceremony_id: int

class StaffIn(BaseModel):
    staff_id: str
    name: str
    email: EmailStr
    status: Optional[str] = "active"

class StaffOut(StaffIn):
    pass

class MatchIn(BaseModel):
    photo: str
