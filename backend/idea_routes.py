from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel


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


work_queue: list[Idea] = []
ideas: dict[int, Idea] = {}
idea_count = 0
max_queue_size = 50


@idea_router.get("/pop")
def pop_idea():
    if len(ideas) == 0:
        raise HTTPException(status_code=404, detail="No ideas in queue")

    return work_queue.pop(0).model_dump()


@idea_router.get("/")
def list_ideas():
    return [idea.model_dump() for idea in ideas.values()]


@idea_router.patch("/")
def patch_idea(data: PatchIdeaRequest):
    idea_id = data.id

    if idea_id not in ideas:
        raise HTTPException(status_code=404, detail="Idea not found")

    if data.prompt is not None:
        ideas[idea_id].prompt = data.prompt

    if data.repos is not None:
        ideas[idea_id].repos = data.repos

    if data.state is not None:
        ideas[idea_id].state = data.state

    return ideas[idea_id].model_dump()


@idea_router.get("/status")
def get_queue_status():
    return QueueStatusResponse(
        size=len(work_queue),
        max_size=max_queue_size,
        is_full=len(work_queue) >= max_queue_size
    )


@idea_router.get("/{id}")
def get_idea(id: int):
    if id not in ideas:
        raise HTTPException(status_code=404, detail="Idea not found")
    return ideas[id].model_dump()


@idea_router.post("/", status_code=204)
def create_idea(data: CreateIdeaRequest):
    global idea_count

    i = Idea(
        id=idea_count + 1,
        prompt=data.prompt,
        repos=data.repos,
        state="NotStarted"
    )

    ideas[idea_count + 1] = i
    work_queue.append(i)

    idea_count = idea_count + 1

    return Response(status_code=204)
