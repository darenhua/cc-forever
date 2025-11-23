# Refactor Idea Queue from API to Shared State

## Overview

Consolidate the dual state management system by moving the ideas queue from API-based management (via `idea_routes.py`) to thread-safe shared memory management in `services/state.py`. This eliminates HTTP overhead for inter-thread communication and creates a single source of truth for all application state.

## Current State Analysis

The application currently has two parallel state management approaches:
1. **Thread-safe shared state** (`services/state.py`): Properly uses locks for agent execution state
2. **API-based queue** (`idea_routes.py`): Manages ideas queue through HTTP endpoints, causing inefficiency

### Key Discoveries:
- The claude service thread polls `/ideas/pop` endpoint every 5 seconds when idle ([backend/services/claude.py:114-122](backend/services/claude.py#L114-L122))
- The ideas service thread polls `/ideas/status` for queue size ([backend/services/ideas.py:14](backend/services/ideas.py#L14))
- Both threads run in the same process but communicate via localhost HTTP ([backend/main.py:82-85](backend/main.py#L82-L85))
- Frontend client uses the same API endpoints ([client/apps/web/src/lib/api.ts:101-115](client/apps/web/src/lib/api.ts#L101-L115))

## Desired End State

A single, thread-safe state management system where:
- All queue operations happen directly in memory with proper locking
- Inter-thread communication uses shared memory instead of HTTP
- API endpoints become thin wrappers around state functions
- Frontend continues to work seamlessly through existing API contract

### Success Verification:
- No HTTP calls between backend threads
- Queue operations are faster and more reliable
- Frontend functionality remains unchanged
- All tests pass

## What We're NOT Doing

- Not changing the frontend API contract (endpoints remain the same)
- Not modifying the threading architecture
- Not changing the Claude agent execution logic
- Not refactoring stats_routes.py or other unrelated code

## Implementation Approach

Migrate the queue data structures and logic to `services/state.py` while maintaining the API interface for the frontend. Replace HTTP calls in service threads with direct function calls to the shared state module.

## Phase 1: Extend Shared State Module

### Overview
Add queue management functionality to the existing thread-safe state module.

### Changes Required:

#### 1. Extend services/state.py
**File**: `backend/services/state.py`
**Changes**: Add queue data structures and management functions

```python
# Add imports at the top
from typing import Optional, List, Dict
from datetime import datetime

# After existing _state definition (around line 17), add:

# Queue-related data structures
class Idea:
    def __init__(self, id: int, prompt: str, repos: List[str], state: str = "NotStarted"):
        self.id = id
        self.prompt = prompt
        self.repos = repos
        self.state = state
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "repos": self.repos,
            "state": self.state,
            "created_at": self.created_at
        }

_queue_state = {
    "work_queue": [],  # List[Idea]
    "ideas": {},  # Dict[int, Idea]
    "idea_count": 0,
    "max_queue_size": 3
}

# Add queue management functions (after line 81):

def create_idea(prompt: str, repos: List[str]) -> Optional[int]:
    """Create a new idea and add to queue. Returns idea ID or None if queue is full."""
    with _lock:
        if len(_queue_state["work_queue"]) >= _queue_state["max_queue_size"]:
            return None

        _queue_state["idea_count"] += 1
        idea_id = _queue_state["idea_count"]

        idea = Idea(id=idea_id, prompt=prompt, repos=repos)
        _queue_state["ideas"][idea_id] = idea
        _queue_state["work_queue"].append(idea)

        return idea_id

def pop_idea() -> Optional[Dict]:
    """Remove and return the next idea from queue, or None if empty."""
    with _lock:
        if not _queue_state["work_queue"]:
            return None

        idea = _queue_state["work_queue"].pop(0)
        return idea.to_dict()

def get_idea(idea_id: int) -> Optional[Dict]:
    """Get a specific idea by ID."""
    with _lock:
        idea = _queue_state["ideas"].get(idea_id)
        return idea.to_dict() if idea else None

def list_ideas() -> List[Dict]:
    """List all ideas."""
    with _lock:
        return [idea.to_dict() for idea in _queue_state["ideas"].values()]

def update_idea(idea_id: int, prompt: Optional[str] = None,
                repos: Optional[List[str]] = None, state: Optional[str] = None) -> Optional[Dict]:
    """Update an existing idea."""
    with _lock:
        if idea_id not in _queue_state["ideas"]:
            return None

        idea = _queue_state["ideas"][idea_id]
        if prompt is not None:
            idea.prompt = prompt
        if repos is not None:
            idea.repos = repos
        if state is not None:
            idea.state = state

        return idea.to_dict()

def get_queue_status() -> Dict:
    """Get current queue status."""
    with _lock:
        size = len(_queue_state["work_queue"])
        return {
            "size": size,
            "max_size": _queue_state["max_queue_size"],
            "is_full": size >= _queue_state["max_queue_size"]
        }

def get_queue_size() -> int:
    """Get current queue size."""
    with _lock:
        return len(_queue_state["work_queue"])
```

### Success Criteria:

#### Automated Verification:
- [ ] Python syntax check passes: `python -m py_compile backend/services/state.py`
- [ ] Module imports successfully: `python -c "from backend.services.state import create_idea, pop_idea"`

#### Manual Verification:
- [ ] Review that all queue operations are properly locked
- [ ] Verify data structures match original implementation

---

## Phase 2: Update Service Threads

### Overview
Replace HTTP calls in service threads with direct state function calls.

### Changes Required:

#### 1. Update services/claude.py
**File**: `backend/services/claude.py`
**Changes**: Replace HTTP calls with direct state calls

```python
# Update imports (line 7, replace requests import):
# Remove: import requests
# Add:
from services.state import pop_idea, update_idea

# Replace fetch_from_queue function (lines 22-33):
def fetch_from_queue():
    """Fetch next job from queue. Returns (prompt, job_id) or None if empty."""
    job_data = pop_idea()
    if job_data is None:
        return None
    return job_data['prompt'], job_data['id']

# Replace mark_complete function (lines 35-46):
def mark_complete(job_id: int, summary: str):
    """Mark a job as completed."""
    result = update_idea(job_id, state="Completed")
    if result:
        print(f"Job {job_id} marked as completed")
    else:
        print(f"Error marking job {job_id} complete: ID not found")
```

#### 2. Update services/ideas.py
**File**: `backend/services/ideas.py`
**Changes**: Replace HTTP calls with direct state calls

```python
# Update imports (lines 1-5):
import random
import time
# Remove: import requests

from services.state import should_stop, create_idea, get_queue_size

# Remove BASE_URL (line 7)
# Keep MAX_QUEUE_SIZE (line 8)

# Replace get_queue_size function (lines 11-19):
# This function is no longer needed since we import it directly
# Delete these lines

# Replace submit_to_queue function (lines 22-33):
def submit_to_queue(prompt: str) -> bool:
    """Submit an idea to the queue."""
    idea_id = create_idea(prompt=prompt, repos=[])
    return idea_id is not None

# Update start function to use imported get_queue_size (line 64):
# The function call remains the same since we imported get_queue_size
```

### Success Criteria:

#### Automated Verification:
- [ ] Python syntax check passes: `python -m py_compile backend/services/claude.py backend/services/ideas.py`
- [ ] Import verification: `python -c "from backend.services import claude, ideas"`

#### Manual Verification:
- [ ] No more requests library usage in service threads
- [ ] All queue operations go through state module

---

## Phase 3: Update API Routes

### Overview
Convert API endpoints to use the new shared state functions instead of maintaining local state.

### Changes Required:

#### 1. Update idea_routes.py
**File**: `backend/idea_routes.py`
**Changes**: Replace local state with calls to shared state module

```python
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

# Keep the Pydantic models (lines 10-32)
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

# Remove global state variables (lines 35-38)
# Delete: work_queue, ideas, idea_count, max_queue_size

# Update all route handlers to use state functions:

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

@idea_router.post("/", status_code=204)
def create_idea(data: CreateIdeaRequest):
    idea_id = state_create_idea(
        prompt=data.prompt,
        repos=data.repos
    )
    if idea_id is None:
        raise HTTPException(status_code=429, detail="Queue is full")
    return Response(status_code=204)
```

### Success Criteria:

#### Automated Verification:
- [ ] Python syntax check passes: `python -m py_compile backend/idea_routes.py`
- [ ] FastAPI route registration works: `python -c "from backend.idea_routes import idea_router"`

#### Manual Verification:
- [ ] API endpoints maintain the same interface
- [ ] No local state variables in idea_routes.py

---

## Phase 4: Integration Testing

### Overview
Test the complete system to ensure all components work together correctly.

### Testing Steps:

#### 1. Start the Backend Server
```bash
cd backend
python main.py
```

#### 2. Test API Endpoints
```bash
# Create an idea
curl -X POST http://localhost:8000/ideas/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test idea", "repos": []}'

# Check queue status
curl http://localhost:8000/ideas/status

# List ideas
curl http://localhost:8000/ideas/

# Pop an idea
curl http://localhost:8000/ideas/pop

# Start agent threads
curl -X POST http://localhost:8000/agent/start
```

#### 3. Verify Thread Communication
Monitor logs to confirm:
- No HTTP requests between threads
- Ideas flow from creation to processing
- State updates occur correctly

### Success Criteria:

#### Automated Verification:
- [ ] Server starts without errors: `python backend/main.py`
- [ ] All API endpoints respond correctly (test with curl commands above)

#### Manual Verification:
- [ ] Frontend application continues to work unchanged
- [ ] Agent threads process ideas without HTTP calls between them
- [ ] Queue management behaves identically to original implementation
- [ ] No race conditions or deadlocks observed

---

## Testing Strategy

### Unit Tests:
- Test all new state functions with concurrent access
- Verify locking prevents race conditions
- Test queue size limits and edge cases

### Integration Tests:
- Verify API endpoints return expected responses
- Test thread communication through shared state
- Ensure frontend compatibility

### Manual Testing Steps:
1. Start the backend server
2. Use the frontend to create multiple ideas
3. Start agent processing
4. Monitor logs for proper execution
5. Verify ideas transition through states correctly
6. Test queue full scenario (max 3 items)

## Performance Considerations

- **Improved Performance**: Eliminating HTTP calls between threads reduces latency and CPU usage
- **Lock Contention**: All queue operations now require the same lock, but operations are fast enough this shouldn't be an issue
- **Memory Usage**: Slightly reduced by eliminating HTTP request/response overhead

## Migration Notes

- No data migration needed as queue is ephemeral
- Deployment can be done with zero downtime
- If rollback is needed, simply deploy previous version

## References

- Original idea routes: [backend/idea_routes.py](backend/idea_routes.py)
- Thread-safe state module: [backend/services/state.py](backend/services/state.py)
- Claude service: [backend/services/claude.py](backend/services/claude.py)
- Ideas service: [backend/services/ideas.py](backend/services/ideas.py)
- Frontend API client: [client/apps/web/src/lib/api.ts](client/apps/web/src/lib/api.ts)