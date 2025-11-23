# Agent State Management (functional style)
# Thread-safe shared state for tracking Claude agent execution

from threading import Lock
from datetime import datetime
from typing import Optional

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
            "conversation_log": list(_state["conversation_log"])
        }
