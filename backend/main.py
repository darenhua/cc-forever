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
    # Hard-coded 20 random projects for testing
    return [
        {"id": 1, "prompt": "Build a CLI tool for managing Docker containers", "repos": ["docker-cli"], "state": "Completed", "created_at": "2024-01-15T10:30:00"},
        {"id": 2, "prompt": "Create a REST API for a blog platform", "repos": ["blog-api"], "state": "Completed", "created_at": "2024-01-16T14:20:00"},
        {"id": 3, "prompt": "Implement user authentication with OAuth2", "repos": ["auth-service"], "state": "Completed", "created_at": "2024-01-17T09:45:00"},
        {"id": 4, "prompt": "Build a real-time chat application", "repos": ["chat-app"], "state": "Completed", "created_at": "2024-01-18T16:00:00"},
        {"id": 5, "prompt": "Create a task scheduler with cron support", "repos": ["task-scheduler"], "state": "Completed", "created_at": "2024-01-19T11:15:00"},
        {"id": 6, "prompt": "Implement a file upload service with S3", "repos": ["file-upload"], "state": "Completed", "created_at": "2024-01-20T08:30:00"},
        {"id": 7, "prompt": "Build a GraphQL API for e-commerce", "repos": ["ecommerce-gql"], "state": "Completed", "created_at": "2024-01-21T13:45:00"},
        {"id": 8, "prompt": "Create a monitoring dashboard with metrics", "repos": ["metrics-dash"], "state": "Completed", "created_at": "2024-01-22T15:00:00"},
        {"id": 9, "prompt": "Implement a rate limiter middleware", "repos": ["rate-limiter"], "state": "Completed", "created_at": "2024-01-23T10:20:00"},
        {"id": 10, "prompt": "Build a notification service with webhooks", "repos": ["notif-service"], "state": "Completed", "created_at": "2024-01-24T12:30:00"},
        {"id": 11, "prompt": "Create a PDF generator from HTML templates", "repos": ["pdf-gen"], "state": "Completed", "created_at": "2024-01-25T09:00:00"},
        {"id": 12, "prompt": "Implement a search engine with Elasticsearch", "repos": ["search-engine"], "state": "Completed", "created_at": "2024-01-26T14:45:00"},
        {"id": 13, "prompt": "Build a CI/CD pipeline configuration tool", "repos": ["cicd-tool"], "state": "Completed", "created_at": "2024-01-27T11:30:00"},
        {"id": 14, "prompt": "Create a database migration utility", "repos": ["db-migrate"], "state": "Completed", "created_at": "2024-01-28T16:15:00"},
        {"id": 15, "prompt": "Implement a caching layer with Redis", "repos": ["cache-layer"], "state": "Completed", "created_at": "2024-01-29T08:45:00"},
        {"id": 16, "prompt": "Build a log aggregation service", "repos": ["log-aggregator"], "state": "Completed", "created_at": "2024-01-30T13:00:00"},
        {"id": 17, "prompt": "Create an API gateway with routing", "repos": ["api-gateway"], "state": "Completed", "created_at": "2024-01-31T10:30:00"},
        {"id": 18, "prompt": "Implement a feature flag management system", "repos": ["feature-flags"], "state": "Completed", "created_at": "2024-02-01T15:20:00"},
        {"id": 19, "prompt": "Build a backup automation tool", "repos": ["backup-tool"], "state": "Completed", "created_at": "2024-02-02T09:15:00"},
        {"id": 20, "prompt": "Create a secrets management service", "repos": ["secrets-mgmt"], "state": "Completed", "created_at": "2024-02-03T12:00:00"},
    ]


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
