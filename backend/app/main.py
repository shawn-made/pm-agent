"""VPMA Backend — FastAPI Application Entry Point."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.services.database import init_db

# Load environment variables from project root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="VPMA API",
    description="Virtual Project Management Assistant — Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: Allow React frontend at localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
