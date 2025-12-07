from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import threading
import signal
import sys
import time
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

from services.s3interface import get_storage, S3Storage

from idea_routes import idea_router
from stats_routes import stats_router
from s3_routes import s3_router
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


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(idea_router)
app.include_router(stats_router)
app.include_router(s3_router)

# Mount static files for projects
app.mount("/projects", StaticFiles(directory="projects", html=True), name="projects")

# Mount static files for cartridge arts
app.mount("/cartridge_arts", StaticFiles(directory="cartridge_arts"), name="cartridge_arts")

app.mount("/assets", StaticFiles(directory="assets"), name="assets")


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


@app.get("/projects-list")
def list_projects():
    """List all timestamp directories and their numbered subdirectories under projects/"""
    projects_dir = Path("projects")
    result = []

    if not projects_dir.exists():
        return result

    sorted_dirs = sorted(projects_dir.iterdir(), reverse=True)

    for i, timestamp_dir in enumerate(sorted_dirs):
        if timestamp_dir.is_dir():
            subdirs = []
            for subdir in sorted(timestamp_dir.iterdir()):
                if subdir.is_dir():
                    subdirs.append(subdir.name)

            num_games = len(subdirs)
            result.append({
                "name": f"Game Pack #{len(sorted_dirs) - i} ({num_games} games)",
                "timestamp": timestamp_dir.name,
                "games": subdirs
            })

    return result


@app.get("/get-entry-point/{timestamp}/{job_id}")
def get_entry_point(timestamp: str, job_id: int):
    """Find the index.html entry point for a project, searching recursively if needed"""
    storage = get_storage()

    # Check if using S3 storage
    if isinstance(storage, S3Storage):
        # For S3, return the S3 URL directly
        s3_path = f"projects/{timestamp}/{job_id}/index.html"
        if storage.exists(s3_path):
            return {"path": storage.get_url(s3_path), "storage": "s3"}

        # Search for index.html in S3 bucket under the project prefix
        files = storage.list_files(f"projects/{timestamp}/{job_id}/")
        index_files = [f for f in files if f.endswith("index.html")]

        if index_files:
            return {"path": storage.get_url(index_files[0]), "storage": "s3"}

        return {"error": "No index.html found in S3", "path": None}

    # Local storage fallback
    project_dir = Path("projects") / timestamp / str(job_id)

    if not project_dir.exists():
        return {"error": "Project not found", "path": None}

    # First check the root directory
    root_index = project_dir / "index.html"
    if root_index.exists():
        return {"path": f"/projects/{timestamp}/{job_id}/index.html", "storage": "local"}

    # Search recursively for index.html
    index_files = list(project_dir.rglob("index.html"))

    if index_files:
        # Return the first one found (could be improved to prioritize certain paths)
        relative_path = index_files[0].relative_to(Path("projects"))
        return {"path": f"/projects/{relative_path}", "storage": "local"}

    return {"error": "No index.html found", "path": None}


@app.get("/get-asset-url/{asset_type}/{timestamp}/{job_id}/{filename}")
def get_asset_url(asset_type: str, timestamp: str, job_id: int, filename: str):
    """
    Get the URL for an asset (cover art, banner art, or project asset).

    asset_type: "cartridge_arts" or "projects"
    """
    storage = get_storage()

    if asset_type == "cartridge_arts":
        path = f"cartridge_arts/{timestamp}/{job_id}/{filename}"
    else:
        path = f"projects/{timestamp}/{job_id}/assets/{filename}"

    if isinstance(storage, S3Storage):
        if storage.exists(path):
            return {"url": storage.get_url(path), "storage": "s3"}
        return {"error": "Asset not found in S3", "url": None}

    # Local storage
    if Path(path).exists():
        return {"url": f"/{path}", "storage": "local"}

    return {"error": "Asset not found", "url": None}


@app.get("/storage-config")
def get_storage_config():
    """Return the current storage configuration for frontend to use."""
    storage = get_storage()

    if isinstance(storage, S3Storage):
        return {
            "type": "s3",
            "base_url": storage.get_url(""),
            "bucket": storage.bucket_name,
        }

    return {
        "type": "local",
        "base_url": "",
    }


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    main()
