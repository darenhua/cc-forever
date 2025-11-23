import random
import time
import requests

from services.state import should_stop

BASE_URL = "http://localhost:8000"
MAX_QUEUE_SIZE = 3


def get_queue_size() -> int:
    """Get current queue size from status endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/ideas/status/")
        response.raise_for_status()
        return response.json()["size"]
    except requests.RequestException as e:
        print(f"Error getting queue size: {e}")
        return 0


def submit_to_queue(prompt: str) -> bool:
    """Submit an idea to the queue."""
    try:
        response = requests.post(
            f"{BASE_URL}/ideas/",
            json={"prompt": prompt, "repos": []}
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error submitting to queue: {e}")
        return False


def propose_idea() -> str:
    ideas =  [
        "make me a todo list website using html, css, js",
        "make me a calculator website using html, css, js",
        "make me a weather website using html, css, js",
        "make me a portfolio website using html, css, js",
        "make me a blog website using html, css, js",
        "make me a contact form website using html, css, js",
        "make me a login page website using html, css, js",
        "make me a registration page website using html, css, js",
        "make me a password reset page website using html, css, js",
        "make me a dashboard website using html, css, js",
        "make me a admin dashboard website using html, css, js",
        "make me a admin login page website using html, css, js",
        "make me a admin registration page website using html, css, js",
        "make me a admin password reset page website using html, css, js",
        "make me a admin dashboard website using html, css, js",
        "make me a admin login page website using html, css, js",
        "make me a admin registration page website using html, css, js",
        "make me a admin password reset page website using html, css, js",
    ]

    chosen = random.choice(ideas)
    # api req to queue here
    return chosen

def start():
    while not should_stop():
        queue_size = get_queue_size()

        # Backpressure based on queue fullness
        if queue_size >= MAX_QUEUE_SIZE:
            time.sleep(30)
            continue
        elif queue_size / MAX_QUEUE_SIZE >= 0.8:
            time.sleep(10)
        elif queue_size / MAX_QUEUE_SIZE >= 0.5:
            time.sleep(2)

        idea = propose_idea()
        if submit_to_queue(idea):
            print(f"Submitted: {idea}")


if __name__ == "__main__":
    start()
