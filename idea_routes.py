from flask import Response, abort, jsonify, request
from dataclasses import dataclass, asdict

from flask.blueprints import Blueprint


# Blueprints
idea_blueprint = Blueprint('/ideas', __name__, url_prefix='/ideas')


@dataclass
class Idea:
    id: int
    prompt: str
    repos: list[str]
    state: str

    def __init__(self, id: int, prompt: str, repos: list[str], state: str):
        self.id = id
        self.prompt = prompt
        self.repos = repos
        self.state = state


@dataclass
class QueueStatusResponse:
    is_full: bool
    size: int
    max_size: int


work_queue = []
ideas = {}
idea_count = 0
max_queue_size = 50


@idea_blueprint.get('/pop')
def popIdea():
    if len(ideas) == 0:
        r = Response('No ideas in queue', status=404)
        abort(r)

    return jsonify(asdict(work_queue.pop(0)))


@idea_blueprint.get('/')
def listIdeas():
    return jsonify([asdict(idea) for idea in ideas.values()])


@idea_blueprint.patch('/')
def patchIdea():
    data = request.get_json()

    if 'id' not in data:
        return Response('id not in body', status=400)

    idea_id = data['id']

    if not isinstance(idea_id, int):
        return Response('id not int', status=400)

    if 'prompt' in data:
        prompt = data.get('prompt')
        if isinstance(prompt, str):
            ideas[idea_id].prompt = prompt

    if 'repos' in data:
        repos = data.get('repos')
        if isinstance(repos, list):
            ideas[idea_id].repos = repos

    if 'state' in data:
        state = data.get('state')
        if isinstance(state, str):
            ideas[idea_id].state = state

    return jsonify(asdict(ideas[idea_id]))


@idea_blueprint.get('/<id>')
def getIdea(id: int):
    try:
        return jsonify(asdict(ideas[int(id)]))
    except (KeyError, ValueError):
        abort(Response("Idea not found", status=404))


@idea_blueprint.post('/')
def createIdea():
    global idea_count

    if len(work_queue) >= max_queue_size:
        return Response('Idea queue is full', status=400)

    data = request.get_json()

    if 'prompt' not in data:
        return Response('prompt not in body', status=400)

    if 'repos' not in data:
        return Response('repos not in body', status=400)

    prompt = data.get('prompt')
    repos = data.get('repos')

    if not isinstance(prompt, str):
        return Response('prompt in incorrect format', status=400)

    if not isinstance(repos, list):
        return Response('repos in incorrect format', status=400)

    i = Idea(
            id=idea_count + 1,
            prompt=prompt,
            repos=repos,
            state='NotStarted'
            )

    ideas[idea_count + 1] = i
    work_queue.append(i)

    idea_count = idea_count + 1

    return jsonify(asdict(i))


@idea_blueprint.get("/status")
def getQueueStatus():
    q = QueueStatusResponse(
            size=len(work_queue),
            max_size=max_queue_size,
            is_full=len(work_queue) >= max_queue_size
            )
    return jsonify(asdict(q))
