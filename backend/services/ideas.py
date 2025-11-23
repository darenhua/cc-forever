import random
import time

from services.blocks import snake, minesweeper, breakout
from services.state import BuildingBlock, Idea, list_all_ideas, should_stop, create_idea, get_queue_size

MAX_QUEUE_SIZE = 3


def submit_to_queue(idea: tuple[str, list[BuildingBlock]]) -> bool:
    """Submit an idea to the queue."""
    idea_id = create_idea(idea[0], idea[1])
    return idea_id is not None


def propose_idea() -> tuple[str, list[BuildingBlock]]:
    completed_ideas = [idea for idea in list_all_ideas() if idea["state"] == "Completed"]

    if len(completed_ideas) <= 3:
        ideas: list[tuple[str, list[BuildingBlock]]] = [
            ("make me a snake game using phaser.js", [snake]),
            ("make me a minesweeper game using phaser.js", [minesweeper]),
            ("make me a breakout game using phaser.js", [breakout]),
            ]

        chosen = random.choice(ideas)
        # api req to queue here
        return chosen

    block_one = random.choice(completed_ideas)
    block_two = random.choice(completed_ideas)

    prompt = f"""Combine the following two prompts below in brackets to create
    one game in phaser.js that is a blend of both:
    {{ {block_one["prompt"]} }}
    {{ {block_two["prompt"]} }}
    """

    combined_blocks = block_one["blocks"] + block_two["blocks"]

    return (prompt, combined_blocks)


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
