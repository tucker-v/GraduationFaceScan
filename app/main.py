from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import students as students_routes
from app.routes import ceremonies as ceremonies_routes
from app.routes import degrees as degree_routes
from app.routes import queue as queue_routes
from app.routes import staff as staff_routes
from app.routes import auth as auth_routes   # NEW
from app.routes import reports as reports_routes

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Commencement DB Admin")

frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students_routes.router)
app.include_router(ceremonies_routes.router)
app.include_router(staff_routes.router)
app.include_router(auth_routes.router)   # NEW
app.include_router(degree_routes.router)
app.include_router(queue_routes.router)
app.include_router(reports_routes.router)

@app.get("/health")
def root():
    return {"message": "FastAPI backend is running"}

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
