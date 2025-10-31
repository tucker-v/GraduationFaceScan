from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import students

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)

@app.get("/")
def root():
    return {"message": "FastAPI + psycopg2 backend is running"}
