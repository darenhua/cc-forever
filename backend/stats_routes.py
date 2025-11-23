from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import json
import httpx
from datetime import datetime
from typing import Optional

# Router
stats_router = APIRouter(prefix="/stats", tags=["stats"])


class UsageStats(BaseModel):
    session: int  # 0-100
    weekly: int  # 0-100


class WorkSession(BaseModel):
    start_time: Optional[str]
    end_time: Optional[str]
    idea_id: Optional[int]
    duration_seconds: int


class StatsResponse(BaseModel):
    usage_stats: UsageStats
    work_session: WorkSession


# Track current work session
current_session: dict = {
    "start_time": None,
    "end_time": None,
    "idea_id": None,
}


def get_claude_token() -> str:
    """Retrieves Claude Code OAuth token from macOS Keychain"""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
            capture_output=True,
            text=True,
            check=True
        )
        credentials_json = result.stdout.strip()
        credentials = json.loads(credentials_json)
        return credentials["claudeAiOauth"]["accessToken"]
    except subprocess.CalledProcessError as e:
        if "could not be found" in str(e.stderr):
            raise HTTPException(
                status_code=500,
                detail="Claude Code credentials not found in Keychain. Please run `claude` and complete the login flow first."
            )
        raise HTTPException(status_code=500, detail=f"Failed to retrieve token: {e.stderr}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse credentials: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Invalid credentials format: missing {str(e)}")


async def fetch_usage_limits(token: str) -> dict:
    """Fetches usage limits from Claude API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.anthropic.com/api/oauth/usage",
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                    "User-Agent": "claude-code/2.0.31",
                    "Authorization": f"Bearer {token}",
                    "anthropic-beta": "oauth-2025-04-20",
                    "Accept-Encoding": "gzip, compress, deflate, br",
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"API request failed: {response.text}"
                )

            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch usage data: {str(e)}")



@stats_router.get("/", response_model=StatsResponse)
async def get_stats():
    """Get usage statistics and current work session info"""
    # Get Claude token from Keychain
    token = get_claude_token()

    # Fetch usage data from API
    usage_data = await fetch_usage_limits(token)

    # Extract usage percentages
    session_usage = 0
    weekly_usage = 0

    if usage_data.get("five_hour"):
        session_usage = int(usage_data["five_hour"].get("utilization", 0))

    if usage_data.get("seven_day"):
        weekly_usage = int(usage_data["seven_day"].get("utilization", 0))

    # Calculate session duration
    duration_seconds = 0
    if current_session["start_time"]:
        start = datetime.fromisoformat(current_session["start_time"])
        end = datetime.fromisoformat(current_session["end_time"]) if current_session["end_time"] else datetime.now()
        duration_seconds = int((end - start).total_seconds())

    return StatsResponse(
        usage_stats=UsageStats(
            session=session_usage,
            weekly=weekly_usage,
        ),
        work_session=WorkSession(
            start_time=current_session["start_time"],
            end_time=current_session["end_time"],
            idea_id=current_session["idea_id"],
            duration_seconds=duration_seconds
        )
    )
