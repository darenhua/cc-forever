# CC-Forever

An AI-powered game generation platform that uses Claude and Gemini to create Phaser.js web games.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Bun](https://bun.sh/) 1.3.1+
- API keys for:
  - Anthropic (Claude)
  - Google (Gemini)

## Project Structure

```
.
├── backend/          # FastAPI backend with Claude agent
│   ├── main.py       # FastAPI app entry point
│   ├── services/     # Claude agent and state management
│   └── projects/     # Generated game projects
├── client/           # React frontend (Turborepo monorepo)
│   └── apps/web/     # Vite + React web application
└── README.md
```

## Setup

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv sync
   ```

3. Create a `.env` file with your API keys:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_key
   GEMINI_API_KEY=your_gemini_key
   ```

4. Start the backend server:
   ```bash
   uv run python main.py
   ```

   The API will be available at `http://localhost:8000`

### Frontend

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   bun install
   ```

3. Start the development server:
   ```bash
   bun run dev:web
   ```

   The frontend will be available at `http://localhost:3001`

## Running Both Services

For development, run in separate terminals:

**Terminal 1 (Backend):**
```bash
cd backend
uv run python main.py
```

**Terminal 2 (Frontend):**
```bash
cd client
bun run dev:web
```

## API Endpoints

- `GET /agent/status` - Check agent status
- `POST /agent/start` - Start the game generation agent
- `POST /agent/stop` - Stop the agent
- `GET /finished-projects` - List completed game projects
- `GET /projects-list` - List all project directories
- `GET /get-entry-point/{timestamp}/{job_id}` - Get game entry point URL

## How It Works

1. Submit game ideas through the frontend
2. The Claude agent picks up ideas from the queue
3. Claude generates Phaser.js games with assets created by Gemini
4. Completed games are served as static files and playable in-browser
