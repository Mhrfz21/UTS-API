from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app import models  # Import models so SQLAlchemy registers all tables.
from app.routers import facilities, reports
from app.services.facility_service import NotFoundError, ConflictError

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="LabCare API",
    description="REST API untuk pelaporan dan penanganan kerusakan fasilitas laboratorium.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(facilities.router)
app.include_router(reports.router)

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.get("/", tags=["Health"])
def root():
    return {"message": "LabCare API aktif", "docs": "/docs"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
