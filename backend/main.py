from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from database import init_db
from routers import auth, symptom, medicine, health, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="HealthBridge AI API",
    description="Intelligent Healthcare Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/auth",     tags=["Authentication"])
app.include_router(symptom.router,  prefix="/symptom",  tags=["Symptom Analysis"])
app.include_router(medicine.router, prefix="/medicine",  tags=["Medicine Info"])
app.include_router(health.router,   prefix="/health",    tags=["Health Records"])
app.include_router(admin.router,    prefix="/admin",     tags=["Admin"])

@app.get("/")
def root():
    return {"message": "HealthBridge AI API", "status": "running", "version": "1.0.0"}

@app.get("/health-check")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
