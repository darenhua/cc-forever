import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
import signal
import sys
import time

from idea_routes import idea_router
from sandbox_routes import terminate_idle_sandboxes
from sandbox_routes import sandbox_router
from services.claude import start as claude_start
from services.ideas import start as ideas_start

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
    # Startup: Start background threads
    global claude_thread, ideas_thread

    """
    claude_thread = threading.Thread(target=claude_start, daemon=True)
    claude_thread.start()

    ideas_thread = threading.Thread(target=ideas_start, daemon=True)
    ideas_thread.start()
    """

    asyncio.create_task(terminate_idle_sandboxes())

    print("Hello from cc-forever!")

    yield

    # Shutdown
    cleanup()


app = FastAPI(lifespan=lifespan)
app.include_router(idea_router)
app.include_router(sandbox_router)


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
