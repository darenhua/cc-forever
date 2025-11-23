# Claude Service
# This is an infinitely running process which pulls from api to get ideas, and does them in a secure place that can be revisited and verified.

import anyio
import os
import time
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, create_sdk_mcp_server, Message

from pydantic import BaseModel, Field, ValidationError
from datetime import datetime

from services.state import start_job, add_message, finish_job, set_online, should_stop, pop_idea, update_idea

class JobReport(BaseModel):
    summary: str = Field(description="description of what you made and how you did it")
    entry_point: str = Field(default=f"./projects/<uuid>/index.html", description="the entry point of the project")


def fetch_from_queue():
    """Fetch next job from queue. Returns (prompt, job_id) or None if empty."""
    job_data = pop_idea()
    if job_data is None:
        return None
    return job_data['prompt'], job_data['id']

def mark_complete(job_id: int, summary: str):
    """Mark a job as completed."""
    result = update_idea(job_id, state="Completed")
    if result:
        print(f"Job {job_id} marked as completed")
    else:
        print(f"Error marking job {job_id} complete: ID not found")


def complete_job(job_id: int, summary: str):
    mark_complete(job_id, summary)
    return {
        "id": job_id,
        "summary": summary,
        "created_at": datetime.now().isoformat()
    }

async def run_once(prompt: str, job_id: str):
    project_path = f"./projects/{job_id}"
    start_job(job_id, prompt)

    try:
        os.makedirs(project_path, exist_ok=True)
        
        server = create_sdk_mcp_server(
            name="my-tools",
            version="1.0.0",
            tools=[]
        )

        options = ClaudeAgentOptions(
            mcp_servers={"tools": server},
            allowed_tools=["Read", "Write", "Bash"],
            permission_mode='acceptEdits',
            cwd=project_path,
            output_format={
                "type": "json_schema",
                "schema": JobReport.model_json_schema()
            }
        )

        instructions = "When you are done, please summarize what you made and how you did it."

        async with ClaudeSDKClient(options=options) as client:
            await client.query(f"{prompt}\n\n{instructions}")
            async for msg in client.receive_response():
                print(msg)
                add_message(msg)

                if hasattr(msg, 'structured_output'):
                    # Validate and get fully typed result
                    result = JobReport.model_validate(msg.structured_output)
                    return result

    except ValidationError as e:
        print(f"Validation error: {e}")
        return "no summary available"
    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        finish_job()
        # Clean up empty directories in projects folder
        from pathlib import Path
        projects_dir = Path("./projects")
        if projects_dir.exists():
            for dir_path in projects_dir.iterdir():
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
    

def start():
    set_online(True)
    try:
        while not should_stop():
            result = fetch_from_queue()
            if result:
                prompt, job_id = result
                summary = anyio.run(lambda: run_once(prompt, job_id))
                # report back to the coordinator that the task is complete
                complete_job(job_id, summary)
            else:
                # No job available, wait before polling again
                time.sleep(5)
    finally:
        set_online(False)


if __name__ == "__main__":
    start()
