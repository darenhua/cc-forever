from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

# Import state functions
from services.state import (
    create_idea as state_create_idea,
    pop_idea as state_pop_idea,
    get_idea as state_get_idea,
    list_ideas as state_list_ideas,
    update_idea as state_update_idea,
    get_queue_status as state_get_queue_status
)

# Router
idea_router = APIRouter(prefix="/ideas", tags=["ideas"])


class Idea(BaseModel):
    id: int
    prompt: str
    repos: list[str]
    state: str


class CreateIdeaRequest(BaseModel):
    prompt: str
    repos: list[str]


class PatchIdeaRequest(BaseModel):
    id: int
    prompt: str | None = None
    repos: list[str] | None = None
    state: str | None = None


class QueueStatusResponse(BaseModel):
    is_full: bool
    size: int
    max_size: int


@idea_router.get("/pop")
def pop_idea():
    result = state_pop_idea()
    if result is None:
        raise HTTPException(status_code=404, detail="No ideas in queue")
    return result


@idea_router.get("/")
def list_ideas():
    return state_list_ideas()


@idea_router.patch("/")
def patch_idea(data: PatchIdeaRequest):
    result = state_update_idea(
        idea_id=data.id,
        prompt=data.prompt,
        repos=data.repos,
        state=data.state
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return result


@idea_router.get("/status")
def get_queue_status():
    status = state_get_queue_status()
    return QueueStatusResponse(
        size=status["size"],
        max_size=status["max_size"],
        is_full=status["is_full"]
    )


@idea_router.get("/{id}")
def get_idea(id: int):
    result = state_get_idea(id)
    if result is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return result


# @idea_router.post("/", status_code=204)
# def create_idea(data: CreateIdeaRequest):
#     idea_id = state_create_idea(
#         prompt=data.prompt,
#         repos=data.repos
#     )
#     if idea_id is None:
#         raise HTTPException(status_code=429, detail="Queue is full")
#     return Response(status_code=204)
