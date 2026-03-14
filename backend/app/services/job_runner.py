"""VPMA Job Runner — Background execution of long-running tasks (Task 57).

Wraps existing service functions so they can run as fire-and-forget background jobs.
Jobs are tracked in the `jobs` DB table and polled via GET /api/jobs/{job_id}.
"""

import asyncio
import json
import logging

from app.models.schemas import ArtifactSyncRequest, DeepStrategyRequest
from app.services.crud import get_job, update_job_status

logger = logging.getLogger(__name__)

# Keep references to running tasks so they aren't garbage-collected
_active_tasks: set[asyncio.Task] = set()

# Maximum concurrent active jobs per project
MAX_CONCURRENT_PER_PROJECT = 2

# Valid job types
VALID_JOB_TYPES = {"artifact_sync", "deep_strategy", "risk_prediction"}


async def _run_artifact_sync(payload: dict) -> str:
    """Parse payload and call run_artifact_sync, return JSON result."""
    from app.services.artifact_sync import run_artifact_sync

    req = ArtifactSyncRequest(**payload)
    result = await run_artifact_sync(text=req.text, project_id=req.project_id, mode=req.mode)
    return result.model_dump_json()


async def _run_deep_strategy(payload: dict) -> str:
    """Parse payload and call run_deep_strategy, return JSON result."""
    from app.services.deep_strategy import run_deep_strategy

    req = DeepStrategyRequest(**payload)
    result = await run_deep_strategy(artifacts=req.artifacts, project_id=req.project_id)
    return result.model_dump_json()


async def _run_risk_prediction(payload: dict) -> str:
    """Parse payload and call predict_risks, return JSON result."""
    from app.services.risk_prediction import predict_risks

    project_id = payload.get("project_id", "default")
    result = await predict_risks(project_id=project_id)
    return result.model_dump_json()


# Map job_type → handler function
_JOB_HANDLERS = {
    "artifact_sync": _run_artifact_sync,
    "deep_strategy": _run_deep_strategy,
    "risk_prediction": _run_risk_prediction,
}


async def execute_job(job_id: str) -> None:
    """Execute a job in the background. Called via launch_job()."""
    try:
        job = await get_job(job_id)
        if not job:
            logger.error("Job %s not found", job_id)
            return

        job_type = job["job_type"]
        handler = _JOB_HANDLERS.get(job_type)
        if not handler:
            await update_job_status(job_id, "failed", error_message=f"Unknown job type: {job_type}")
            return

        # Mark as running
        await update_job_status(job_id, "running")

        # Parse and execute
        payload = json.loads(job["request_json"])
        result_json = await handler(payload)

        await update_job_status(job_id, "completed", result_json=result_json)
        logger.info("Job %s completed successfully", job_id)

    except Exception as e:
        logger.exception("Job %s failed: %s", job_id, e)
        await update_job_status(job_id, "failed", error_message=str(e))


def launch_job(job_id: str) -> asyncio.Task:
    """Create an asyncio task for the job and track it to prevent GC."""
    task = asyncio.create_task(execute_job(job_id))
    _active_tasks.add(task)
    task.add_done_callback(_active_tasks.discard)
    return task
