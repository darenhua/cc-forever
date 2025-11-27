from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
# import threading
# import signal
# import sys
# import time
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

# from idea_routes import idea_router
# from stats_routes import stats_router
# from services.claude import start as claude_start
# from services.ideas import start as ideas_start
# from services.state import get_state as get_agent_state, request_stop, is_online, get_all_ideas

# claude_thread: threading.Thread
# ideas_thread: threading.Thread

# count = 0


# def test():
#     global count
#     while True:
#         count += 1
#         time.sleep(0.001)


# def cleanup():
#     global count
#     # TODO: kill threads
#     print(f"Final count: {count}")


# def signal_handler(signum, frame):
#     cleanup()
#     sys.exit(0)


# # Register for various termination signals
# signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
# signal.signal(signal.SIGTERM, signal_handler)  # Termination signal


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     print("Hello from cc-forever!")

#     yield

#     # Shutdown
#     cleanup()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(idea_router)
# app.include_router(stats_router)

# Mount static files for projects
app.mount("/projects", StaticFiles(directory="projects", html=True), name="projects")

# Mount static files for cartridge arts
app.mount("/cartridge_arts", StaticFiles(directory="cartridge_arts"), name="cartridge_arts")

app.mount("/assets", StaticFiles(directory="assets"), name="assets")


# @app.get("/agent/status")
# def agent_status():
#     return get_agent_state()


# @app.post("/agent/start")
# def start_agent():
#     global claude_thread
#     global ideas_thread
#     if is_online():
#         return {"status": "already_running", "message": "Agent is already running"}

#     claude_thread = threading.Thread(target=claude_start, daemon=True)
#     claude_thread.start()
#     ideas_thread = threading.Thread(target=ideas_start, daemon=True)
#     ideas_thread.start()
#     return {"status": "started", "message": "Agent started successfully"}


# @app.post("/agent/stop")
# def stop_agent():
#     if not is_online():
#         return {"status": "already_stopped", "message": "Agent is not running"}

#     request_stop()
#     return {"status": "stopping", "message": "Stop requested, agent will stop after current job completes"}


# @app.get("/finished-projects")
# def get_ideas_map():
#     return get_all_ideas()


# @app.get("/projects-list")
# def list_projects():
#     """List all timestamp directories and their numbered subdirectories under projects/"""
#     projects_dir = Path("projects")
#     result = []

#     if not projects_dir.exists():
#         return result

#     sorted_dirs = sorted(projects_dir.iterdir(), reverse=True)

#     for i, timestamp_dir in enumerate(sorted_dirs):
#         if timestamp_dir.is_dir():
#             subdirs = []
#             for subdir in sorted(timestamp_dir.iterdir()):
#                 if subdir.is_dir():
#                     subdirs.append(subdir.name)

#             num_games = len(subdirs)
#             result.append({
#                 "name": f"Game Pack #{len(sorted_dirs) - i} ({num_games} games)",
#                 "timestamp": timestamp_dir.name,
#                 "games": subdirs
#             })

#     return result


@app.get("/get-entry-point/{timestamp}/{job_id}")
def get_entry_point(timestamp: str, job_id: int):
    """Find the index.html entry point for a project, searching recursively if needed"""
    project_dir = Path("projects") / timestamp / str(job_id)

    if not project_dir.exists():
        return {"error": "Project not found", "path": None}

    # First check the root directory
    root_index = project_dir / "index.html"
    if root_index.exists():
        return {"path": f"/projects/{timestamp}/{job_id}/index.html"}

    # Search recursively for index.html
    index_files = list(project_dir.rglob("index.html"))

    if index_files:
        # Return the first one found (could be improved to prioritize certain paths)
        relative_path = index_files[0].relative_to(Path("projects"))
        return {"path": f"/projects/{relative_path}"}

    return {"error": "No index.html found", "path": None}


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    main()
