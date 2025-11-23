# Claude Service
# This is an infinitely running process which pulls from api to get ideas, and does them in a secure place that can be revisited and verified.

from typing import Dict
import anyio
import errno
import os
import shutil
import time
from PIL import Image
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, create_sdk_mcp_server, tool, Message

from pydantic import BaseModel, Field, ValidationError
from datetime import datetime

from services.state import Idea, start_job, add_message, finish_job, set_online, should_stop, pop_idea, update_idea, get_session_timestamp


class JobReport(BaseModel):
    summary: str = Field(description="description of what you made and how you did it")
    entry_point: str = Field(default=f"./projects/<uuid>/index.html", description="the entry point of the project")


def fetch_from_queue():
    """Fetch next job from queue. Returns (prompt, job_id) or None if empty."""
    job_data = pop_idea()
    if job_data is None:
        return None
    return job_data


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

import base64
import mimetypes
import os
import io
from google import genai
from google.genai import types

# Global to track current project path for image generation
_current_project_path = None


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to: {file_name}")


def generate(file_name: str, prompt: str, background_color: str):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-3-pro-image-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"When generating images, the background color MUST be {background_color}. {prompt}"),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
        image_config=types.ImageConfig(
            image_size="1K",
        ),
        tools=tools,
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print("TESTT", chunk)
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:

            # Use global project path for saving images
            base_path = _current_project_path if _current_project_path else "."
            output_file = f"{base_path}/assets/{file_name}_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = make_white_transparent(png_data=inline_data.data)
            file_extension = ".png"
            save_binary_file(f"{output_file}{file_extension}", data_buffer)
            # Return relative path for use in the project
            return f"./assets/{file_name}_{file_index - 1}{file_extension}"
        else:
            print(chunk.text)


@tool("use_image_generation_tool", "Use the image generation tool to generate an image, with the background color in hex value", {"file_name": str, "prompt": str, "background_color": str})
async def use_image_generation_tool(args) -> str:
    return generate(args["file_name"], args["prompt"], "#ffffff")


def make_white_transparent(png_data: bytes) -> bytes:
    """
    Takes PNG data as bytes and makes all white pixels (255,255,255) transparent.

    Args:
        png_data: PNG image data as bytes

    Returns:
        Modified PNG data as bytes with white pixels made transparent
    """
    # Open image from bytes
    image = Image.open(io.BytesIO(png_data))

    # Convert to RGBA if not already (adds alpha channel)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Get image data
    data = image.getdata()

    # Create new data where white pixels become transparent
    new_data = []
    for item in data:
        # Check if pixel is white (255,255,255)
        if item[0] >= 240 and item[1] >= 240 and item[2] >= 240:
            # Make transparent (keep RGB values but set alpha to 0)
            new_data.append((255, 255, 255, 0))
        else:
            # Keep original pixel
            new_data.append(item)

    # Update image data
    image.putdata(new_data)

    # Convert back to bytes
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')

    return output_buffer.getvalue()


async def run_once(idea: Dict):
    prompt = idea["prompt"]
    job_id = idea["id"]
    session_timestamp = get_session_timestamp()

    # Create timestamped project path: projects/<timestamp>/<id>
    project_path = f"./projects/{session_timestamp}/{job_id}"
    project_resources_path = project_path + "/resources"

    # Store the project path in the idea for frontend access
    # Path is relative to the static mount point (without ./)
    relative_project_path = f"{session_timestamp}/{job_id}"
    update_idea(job_id, project_path=relative_project_path)

    start_job(job_id, prompt)

    # Set global project path for image generation tool
    global _current_project_path
    _current_project_path = project_path

    try:
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(project_resources_path, exist_ok=True)
        os.makedirs(project_path + "/assets", exist_ok=True)

        # Create building block folders and files
        for block in idea["blocks"]:
            folder_name = block["folder_path"].split("/")[-1]
            dest = project_resources_path + f"/{folder_name}"

            try:
                shutil.copytree(block["folder_path"], dest)
            except OSError as err:
                # error caused if the source was not a directory
                if err.errno == errno.ENOTDIR:
                    shutil.copy2(block["folder_path"], dest)
                else:
                    print("Error: % s" % err)

        server = create_sdk_mcp_server(
            name="gemini",
            version="1.0.0",
            tools=[use_image_generation_tool]
        )

        image_gen_instructions = f"""
Here is common code that you may encounter for loading images in Phaser 3:
```javascript
this.load.setBaseURL('https://cdn.phaserfiles.com/v385');
this.load.image('food', 'assets/games/snake/food.png');
this.load.image('body', 'assets/games/snake/body.png');
```
You must NEVER use cdn link for images. You ALWAYS use the local image files found in the assets folder. Initially, there will be no images in the assets folder. You must generate them using the use_image_generation_tool, and upon getting the image url from this tool, you must update the phaser code to use the new images. Think about different assets that you need to generate for the game and prompt the use_image_generation_tool wisely to generate the best images for the game. You may be asked to generate images in a certain STYLE, and in this case you should update the image generation instructions to generate images in that style. Please think carefully about the sizing of the assets when controlling them using setDisplaySize() especially given that the image assets have quite high resolution (1024 x 1024 pixels for each image). 
        """

        options = ClaudeAgentOptions(
            mcp_servers={"gemini": server},
            allowed_tools=["Read", "Write", "Bash", "mcp__gemini__use_image_generation_tool"],
            permission_mode='acceptEdits',
            cwd=project_path,
            output_format={
                "type": "json_schema",
                "schema": JobReport.model_json_schema()
            }
        )

        instructions = f"We are using Phaser 3 to make web games. First read all the files in the resources folder. When you are done, please summarize what you made and how you did it. For certain games, you may need to generate images. Use the following instructions to generate images: {image_gen_instructions}"

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
        # Clean up empty directories in projects folder (including nested timestamp dirs)
        from pathlib import Path
        projects_dir = Path("./projects")
        if projects_dir.exists():
            # Clean up empty project directories within timestamp folders
            for timestamp_dir in projects_dir.iterdir():
                if timestamp_dir.is_dir():
                    for project_dir in timestamp_dir.iterdir():
                        if project_dir.is_dir() and not any(project_dir.iterdir()):
                            project_dir.rmdir()
                    # Also clean up empty timestamp directories
                    if not any(timestamp_dir.iterdir()):
                        timestamp_dir.rmdir()


def start():
    set_online(True)
    try:
        while not should_stop():
            result = fetch_from_queue()
            if result:
                job_id = result["id"]
                summary = anyio.run(lambda: run_once(result))
                # report back to the coordinator that the task is complete
                complete_job(job_id, summary)
            else:
                # No job available, wait before polling again
                time.sleep(5)
    finally:
        set_online(False)


if __name__ == "__main__":
    start()
