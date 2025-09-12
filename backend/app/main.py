from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection
from app.routers  import contracts
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Contract Intelligence Parser API...")
    await connect_to_mongo()
    yield
    # Shutdown
    logger.info("Shutting down Contract Intelligence Parser API...")
    await close_mongo_connection()

app = FastAPI(
    title="Contract Intelligence Parser API",
    description="API for parsing and analyzing contracts with AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contracts.router, prefix="/api/contracts", tags=["contracts"])

@app.get("/")
async def root():
    return {"message": "Contract Intelligence Parser API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}