"""VPMA API Routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Backend health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
