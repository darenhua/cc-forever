# Agent State Management (functional style)
# Thread-safe shared state for tracking Claude agent execution

from threading import Lock
from datetime import datetime
from typing import Optional, List, Dict

_lock = Lock()

_state = {
    "is_online": False,
    "is_running": False,
    "current_job_id": None,
    "current_prompt": None,
    "started_at": None,
    "conversation_log": []
}

# Stop flag for graceful shutdown
_stop_requested = False


def set_online(online: bool):
    global _stop_requested
    with _lock:
        _state["is_online"] = online
        if online:
            _stop_requested = False


def request_stop():
    global _stop_requested
    with _lock:
        _stop_requested = True


def should_stop() -> bool:
    with _lock:
        return _stop_requested


def is_online() -> bool:
    with _lock:
        return _state["is_online"]


def start_job(job_id: str, prompt: str):
    with _lock:
        _state["is_running"] = True
        _state["current_job_id"] = job_id
        _state["current_prompt"] = prompt
        _state["started_at"] = datetime.now().isoformat()
        _state["conversation_log"] = []


def add_message(msg):
    with _lock:
        _state["conversation_log"].append({
            "timestamp": datetime.now().isoformat(),
            "type": type(msg).__name__,
            "content": str(msg)
        })


def finish_job():
    with _lock:
        _state["is_running"] = False


def get_state():
    with _lock:
        return {
            "is_online": _state["is_online"],
            "is_running": _state["is_running"],
            "current_job_id": _state["current_job_id"],
            "current_prompt": _state["current_prompt"],
            "started_at": _state["started_at"],
            "message_count": len(_state["conversation_log"]),
            "conversation_log": list(_state["conversation_log"]),
            "ideas_queue": [_idea.to_dict() for _idea in _queue_state["work_queue"]],
            "num_completed_ideas": len([idea for idea in _queue_state["ideas"].values() if idea.state == "Completed"]),
        }


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
    """List all ideas currently in the queue."""
    with _lock:
        return [idea.to_dict() for idea in _queue_state["work_queue"]]


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
