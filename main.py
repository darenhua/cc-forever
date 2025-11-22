from flask import Flask
import threading
import atexit
import signal
import sys
import time

from idea_routes import idea_blueprint

claude_thread: threading.Thread

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


atexit.register(cleanup)

# Register for various termination signals
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

app = Flask(__name__)
app.register_blueprint(idea_blueprint)


def main():
    print("Hello from cc-forever!")

    # Start threads
    claude_thread = threading.Thread(target=test, daemon=True)
    claude_thread.start()

    app.run(debug=False)


if __name__ == "__main__":
    main()
