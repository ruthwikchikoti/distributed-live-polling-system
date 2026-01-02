from fastapi import APIRouter, HTTPException

from app.schemas.poll import PollResults, VoteRequest
from app.services.polling_service import PollingService

router = APIRouter()

service = PollingService()


@router.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(service.flush_batch())


@router.post("/vote/{poll_id}")
async def vote(poll_id: str, vote_req: VoteRequest):
    try:
        await service.vote(poll_id, vote_req.option_id)
        return {"status": "success", "message": "Vote accepted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{poll_id}", response_model=PollResults)
async def get_results(poll_id: str):
    results = await service.get_results(poll_id)
    served_via = "redis"  
    return PollResults(
        poll_id=poll_id,
        results=results,
        served_via=served_via
    )
