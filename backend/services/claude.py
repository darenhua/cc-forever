# Claude Service
# This is an infinitely running process which pulls from api to get ideas, and does them in a secure place that can be revisited and verified.

from typing import Dict
import anyio
import errno
import os
import shutil
import time
import json
import subprocess
import tempfile
from PIL import Image
from bs4 import BeautifulSoup
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


def generate_cover_art_image(file_name: str, prompt: str, background_color: str):
    """Generate cover art for games - PS2 style box art."""
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-image"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Please make cover art inspired by PS2 style box cover art for the following game:{prompt}. DO NOT INCLUDE any actual PS2 logo or playstation imagery, only include the art for the game."),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
        ],
        image_config=types.ImageConfig(
            aspect_ratio="1:1",
        ),
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"{file_name}_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(file_name, data_buffer)
            return file_name

        else:
            print(chunk.text)

def generate_banner_art_image(file_name: str, prompt: str):
    """Generate cover art for games - PS2 style box art."""
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-image"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Please make vertical banner art for the following game:{prompt}. This will be displayed on the sides of the gameboy screen. It should be roughly 800px tall and 200px wide."),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
        ],
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
            file_name = f"{file_name}_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(file_name, data_buffer)
            return file_name

        else:
            print(chunk.text)


def generate(file_name: str, prompt: str, background_color: str):
    """Generate images for tool use - with transparent white background."""
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-image"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"When generating images, the background color MUST be {background_color}. {prompt}"),
            ],
        ),
    ]
    tools = [
        # types.Tool(googleSearch=types.GoogleSearch(
        # )),
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

async def generate_banner_art(session_timestamp: str, job_id: int, prompt: str):
    # Create the folder if it doesn't exist
    folder_path = f"./cartridge_arts/{session_timestamp}/{job_id}"
    os.makedirs(folder_path, exist_ok=True)
    return generate_banner_art_image(f"{folder_path}/banner_art.png", prompt)

async def generate_cover_art(session_timestamp: str, job_id: int, prompt: str):
    # Create the folder if it doesn't exist
    folder_path = f"./cartridge_arts/{session_timestamp}/{job_id}"
    os.makedirs(folder_path, exist_ok=True)
    return generate_cover_art_image(f"{folder_path}/cover_art.png", prompt, "#ffffff")

@tool("use_image_generation_tool", "Use the image generation tool to generate an image, with the background color in hex value", {"file_name": str, "prompt": str, "background_color": str})
async def use_image_generation_tool(args) -> str:
    return generate(args["file_name"], args["prompt"], "#ffffff")


@tool("validate_javascript_tool", "Use the validate javascript tool to validate your index.html file at the end to see if there are any bugs left to fix", {"path_to_file": str})
async def validate_javascript_tool(args) -> list[str]:
    return validate_javascript(args["path_to_file"])


def validate_javascript(path_to_file: str) -> list[str]:
    """
    Extract JavaScript from HTML and detect undefined function calls
    """
    issues = []

    with open(path_to_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script')

    for i, script in enumerate(script_tags):
        if script.string and script.string.strip():
            js_code = script.string

            # Create temporary JS file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_js:
                temp_js.write(js_code)
                temp_js_path = temp_js.name

            try:
                # Run ESLint with no-undef rule
                result = subprocess.run([
                    'npx', 'eslint',
                    '--no-config-lookup',  # Ignore local config
                    '--no-ignore',
                    '--quiet',
                    '--format', 'json',
                    temp_js_path
                ], capture_output=True, text=True)
                print(result)

                if result.returncode != 0 and result.stdout.strip():
                    errors = json.loads(result.stdout)
                    for error in errors[0]['messages']:
                        if error['ruleId'] == 'no-undef':
                            issues.append(f"Script #{i+1}: {error['message']} (line {error['line']})")
            except Exception as e:
                issues.append(f"Analysis error in script #{i+1}: {str(e)}")
            finally:
                os.unlink(temp_js_path)

    return issues


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

    # Generate cover art and banner art in parallel
    async with anyio.create_task_group() as tg:
        tg.start_soon(generate_cover_art, session_timestamp, job_id, prompt)
        tg.start_soon(generate_banner_art, session_timestamp, job_id, prompt)

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

        instructions = f"We are using Phaser 3 to make web games. First read all the files in the resources folder. When you are done, please summarize what you made and how you did it. For certain games, you may need to generate images. Use the following instructions to generate images: {image_gen_instructions}. Make sure only one index.html file is present in the root of this project."

        async with ClaudeSDKClient(options=options) as client:
            await client.query(f"{prompt} using phaser.js. \n\n{instructions}")
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
                res = complete_job(job_id, summary)


            else:
                # No job available, wait before polling again
                time.sleep(5)
    finally:
        set_online(False)


if __name__ == "__main__":
    start()
