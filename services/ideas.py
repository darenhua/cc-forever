import random
import time

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
    while True:
        # possibly some backpressure based off queue size here
        # status = get_queue_status()
        
        status = {
            'is_full': False,
            'size': 10,
            'max_size': 100,
        }
        if status['is_full']:
            time.sleep(30)
            continue
        elif status['size'] / status['max_size'] >= 0.8:
            time.sleep(10)
        elif status['size'] / status['max_size'] >= 0.5:
            time.sleep(2)

        idea = propose_idea()
        print(idea)


if __name__ == "__main__":
    start()
