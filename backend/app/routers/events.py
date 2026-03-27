import logging
from http import client

from fastapi import APIRouter

from app import client
from app.auth import AuthContext
from app.client import ExtensionClient, InstallationClient
from app.schema import Event, EventResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events")

@router.post("/cases/created")
async def process_case_created(
    event: Event,
    ctx: AuthContext,
    client: InstallationClient,
    ext_client: ExtensionClient,
) -> EventResponse:
    task_id = event.task.id if event.task else None
    case_id = event.object.id
    await ext_client.start_task(task_id) # type: ignore
    logger.info(f"===============> Support case CREATED {case_id}")
    await ext_client.complete_task(task_id) # type: ignore
    return EventResponse.ok()


@router.post("/cases/updated")
async def process_case_updated(
    event: Event,
    ctx: AuthContext,
    client: InstallationClient,
    ext_client: ExtensionClient,
) -> EventResponse:
    task_id = event.task.id if event.task else None
    case_id = event.object.id
    await ext_client.start_task(task_id) # type: ignore
    # if case has not list of parameters decorate case with the parameters
    # case.parameters.filter(p => p !== parameterList )
    logger.info(f":::::::::::::::> Support case UPDATED {case_id}")
    await ext_client.complete_task(task_id) # type: ignore
    return EventResponse.ok()

