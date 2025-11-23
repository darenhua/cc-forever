import random
import time

from services.blocks import snake, minesweeper, breakout, stacker, platformer
from services.resources.modifiers import modifiers
from services.state import BuildingBlock, list_all_ideas, should_stop, create_idea, get_queue_size

MAX_QUEUE_SIZE = 3

depth = 0


def submit_to_queue(idea: tuple[str, list[BuildingBlock]]) -> bool:
    """Submit an idea to the queue."""
    idea_id = create_idea(idea[0], idea[1])
    return idea_id is not None


def propose_idea() -> tuple[str, list[BuildingBlock]]:
    ideas: list[tuple[str, list[BuildingBlock]]] = [
        ("make me a snake game", [snake]),
        ("make me a minesweeper game", [minesweeper]),
        ("make me a breakout game", [breakout]),
        ("make me a block stacking game", [stacker]),
        ("make me a platformer game", [platformer]),
        ]

    chosen = random.choice(ideas)
    modifier = random.choice(modifiers)
    newPrompt = chosen[0] + " that also has " + modifier + " aspects using phaser.js"

    return (newPrompt, chosen[1])


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
