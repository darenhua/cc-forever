from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import threading
import signal
import sys
import time

from idea_routes import idea_router
from stats_routes import stats_router
from services.claude import start as claude_start
from services.ideas import start as ideas_start
from services.state import get_state as get_agent_state, request_stop, is_online, get_all_ideas

claude_thread: threading.Thread
ideas_thread: threading.Thread

count = 0


def test():
    global count
    while True:
        count += 1
        time.sleep(0.001)


def cleanup():
    global count
    # TODO: kill threads
    print(f"Final count: {count}")


def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)


# Register for various termination signals
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Hello from cc-forever!")

    yield

    # Shutdown
    cleanup()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(idea_router)
app.include_router(stats_router)

# Mount static files for projects
app.mount("/projects", StaticFiles(directory="projects", html=True), name="projects")


@app.get("/agent/status")
def agent_status():
    return get_agent_state()


@app.post("/agent/start")
def start_agent():
    global claude_thread
    global ideas_thread
    if is_online():
        return {"status": "already_running", "message": "Agent is already running"}

    claude_thread = threading.Thread(target=claude_start, daemon=True)
    claude_thread.start()
    ideas_thread = threading.Thread(target=ideas_start, daemon=True)
    ideas_thread.start()
    return {"status": "started", "message": "Agent started successfully"}


@app.post("/agent/stop")
def stop_agent():
    if not is_online():
        return {"status": "already_stopped", "message": "Agent is not running"}

    request_stop()
    return {"status": "stopping", "message": "Stop requested, agent will stop after current job completes"}


@app.get("/finished-projects")
def get_ideas_map():
    return get_all_ideas()


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
