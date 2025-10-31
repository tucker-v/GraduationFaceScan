from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import students as students_routes
from app.routes import ceremonies as ceremonies_routes
from app.routes import staff as staff_routes

app = FastAPI(title="Commencement DB Admin")

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

@app.get("/")
def root():
    return {"message": "FastAPI backend is running"}
