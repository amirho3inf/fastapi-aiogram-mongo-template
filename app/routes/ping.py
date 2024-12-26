from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Ping"])


@router.get("/ping")
async def ping() -> dict:
    return {"pong": True}
