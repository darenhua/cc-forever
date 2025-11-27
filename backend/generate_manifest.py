import os
import json
import re
from pathlib import Path
from typing import Optional, List
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Define enums for base_game and genre
class BaseGame(str, Enum):
    SNAKE = "snake"
    MINESWEEPER = "minesweeper"
    BREAKOUT = "breakout"
    STACKER = "stacker"
    PLATFORMER = "platformer"
    ADVENTURE = "adventure"
    DUNGEON = "dungeon"

class Genre(str, Enum):
    CRAFTING = "Crafting"
    GAMBLING = "Gambling"
    SURVIVAL = "Survival"
    INVENTORY = "Inventory"
    COMBAT = "Combat"
    OPEN_WORLD = "Open World"
    ENEMIES = "Enemies"
    RACING = "Racing"
    SHOOTER = "Shooter"
    PUZZLE = "Puzzle"
    BLACK_JACK = "Black Jack"
    TOWER_DEFENSE = "Tower Defense"
    BULLET_HELL = "Bullet Hell"
    MULTIPLAYER = "Multiplayer"
    TURN_BASED = "Turn-based"
    CARD_GAME = "Card game"
    STEALTH = "Stealth"
    ROGUELIKE = "Roguelike"
    BASE_BUILDING = "Base Building"
    FISHING = "Fishing"
    RHYTHM = "Rhythm"
    SIMULATION = "Simulation"
    EXPLORATION = "Exploration"
    BOSS_RUSH = "Boss Rush"
    DECKBUILDER = "Deckbuilder"
    RPG = "RPG"
    SPORTS = "Sports"
    HORROR = "Horror"
    FIGHTING = "Fighting"
    SANDBOX = "Sandbox"
    TRIVIA = "Trivia"
    FARMING = "Farming"
    DATING_SIM = "Dating Sim"
    MATCH_3 = "Match-3"
    IDLE_CLICKER = "Idle/Clicker"

# Define the Pydantic models for structured output
class GameMetadata(BaseModel):
    name: str = Field(description="A fun, creative title for this game")
    summary: str = Field(description="A brief 3-sentence summary of how to play the game")
    base_game: BaseGame = Field(description="The base game type this is derived from")
    genre: List[Genre] = Field(description="One or two genre tags from the predefined list", min_length=1, max_length=2)
    prompt: str = Field(description="The prompt that was likely used to generate this game")

class ProjectEntry(BaseModel):
    id: str
    path_to_index_html: str
    path_to_banner_art: Optional[str] = None
    path_to_cover_art: Optional[str] = None
    metadata: GameMetadata

class TimestampGroup(BaseModel):
    index: int
    id: str
    projects: List[ProjectEntry]

def is_valid_timestamp_format(folder_name: str) -> bool:
    """Check if folder name matches timestamp format like 20251123_005659"""
    pattern = r'^\d{8}_\d{6}$'
    return bool(re.match(pattern, folder_name))

def read_html_file(file_path: str) -> str:
    """Read and return the content of an HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def find_art_files(cartridge_arts_path: str, timestamp: str, id_folder: str) -> tuple[Optional[str], Optional[str]]:
    """Find banner_art and cover_art files for a given timestamp/id combination"""
    art_folder = os.path.join(cartridge_arts_path, timestamp, id_folder)

    banner_art_path = None
    cover_art_path = None

    if os.path.exists(art_folder):
        # Check for banner_art.png_0 or banner_art.png
        if os.path.exists(os.path.join(art_folder, "banner_art.png_0")):
            banner_art_path = f"{timestamp}/{id_folder}/banner_art.png_0"
        elif os.path.exists(os.path.join(art_folder, "banner_art.png")):
            banner_art_path = f"{timestamp}/{id_folder}/banner_art.png"

        # Check for cover_art.png_0 or cover_art.png
        if os.path.exists(os.path.join(art_folder, "cover_art.png_0")):
            cover_art_path = f"{timestamp}/{id_folder}/cover_art.png_0"
        elif os.path.exists(os.path.join(art_folder, "cover_art.png")):
            cover_art_path = f"{timestamp}/{id_folder}/cover_art.png"

    return banner_art_path, cover_art_path

def analyze_game_with_openai(html_content: str, client: OpenAI) -> Optional[GameMetadata]:
    """Use OpenAI to analyze the game HTML and extract metadata"""

    system_prompt = """Analyze the following HTML game code and extract metadata about it.

Valid base_game options (choose exactly one):
- snake
- minesweeper
- breakout
- stacker
- platformer
- adventure
- dungeon

Valid genre options (choose one or two):
- Crafting, Gambling, Survival, Inventory, Combat, Open World, Enemies, Racing, Shooter, Puzzle, Black Jack, Tower Defense, Bullet Hell, Multiplayer, Turn-based, Card game, Stealth, Roguelike, Base Building, Fishing, Rhythm, Simulation, Exploration, Boss Rush, Deckbuilder, RPG, Sports, Horror, Fighting, Sandbox, Trivia, Farming, Dating Sim, Match-3, Idle/Clicker

Please provide:
1. A fun, creative name for this game
2. A 3-sentence summary of how to play
3. The base_game type (one of the options above)
4. Genre tags (1-2 from the list above)
5. A prompt that could have been used to generate this game (e.g., "make me a snake game with power-ups")"""

    user_prompt = f"HTML Code:\n{html_content[:8000]}"

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=GameMetadata,
        )

        metadata = response.choices[0].message.parsed
        return metadata
    except Exception as e:
        print(f"Error analyzing game with OpenAI: {e}")
        return None

def scan_projects_folder(projects_path: str, cartridge_arts_path: str) -> List[TimestampGroup]:
    """Scan the projects folder and build the manifest structure"""

    # Initialize OpenAI client
    client = OpenAI()

    timestamp_groups = {}

    # Walk through the projects directory
    for timestamp_folder in os.listdir(projects_path):
        timestamp_path = os.path.join(projects_path, timestamp_folder)

        # Skip if not a directory or doesn't match timestamp format
        if not os.path.isdir(timestamp_path):
            continue

        if not is_valid_timestamp_format(timestamp_folder):
            print(f"Skipping non-timestamp folder: {timestamp_folder}")
            continue

        # Initialize timestamp group if not exists
        if timestamp_folder not in timestamp_groups:
            timestamp_groups[timestamp_folder] = []

        # Look for id subfolders
        for id_folder in os.listdir(timestamp_path):
            id_path = os.path.join(timestamp_path, id_folder)

            if not os.path.isdir(id_path):
                continue

            # Check if index.html exists
            index_html_path = os.path.join(id_path, "index.html")
            if not os.path.exists(index_html_path):
                print(f"No index.html found in {id_path}")
                continue

            print(f"Processing: {timestamp_folder}/{id_folder}")

            # Read HTML content
            html_content = read_html_file(index_html_path)
            if not html_content:
                continue

            # Analyze with OpenAI
            metadata = analyze_game_with_openai(html_content, client)
            if not metadata:
                print(f"Failed to analyze {timestamp_folder}/{id_folder}")
                continue

            # Build relative path to index.html
            relative_path = f"{timestamp_folder}/{id_folder}/index.html"

            # Find art files
            banner_art_path, cover_art_path = find_art_files(cartridge_arts_path, timestamp_folder, id_folder)

            # Create project entry
            project_entry = ProjectEntry(
                id=id_folder,
                path_to_index_html=relative_path,
                path_to_banner_art=banner_art_path,
                path_to_cover_art=cover_art_path,
                metadata=metadata
            )

            timestamp_groups[timestamp_folder].append(project_entry)

    # Convert to final format with indices
    result = []
    for idx, (timestamp, projects) in enumerate(sorted(timestamp_groups.items())):
        if projects:  # Only include timestamps that have valid projects
            result.append(TimestampGroup(
                index=idx,
                id=timestamp,
                projects=projects
            ))

    return result

def main():
    # Get the projects folder path
    backend_dir = Path(__file__).parent
    projects_path = backend_dir / "projects"
    cartridge_arts_path = backend_dir / "cartridge_arts"

    if not projects_path.exists():
        print(f"Projects folder not found: {projects_path}")
        return

    if not cartridge_arts_path.exists():
        print(f"Warning: cartridge_arts folder not found: {cartridge_arts_path}")
        print("Continuing without art files...")

    print(f"Scanning projects folder: {projects_path}")

    # Scan and analyze all projects
    manifest_data = scan_projects_folder(str(projects_path), str(cartridge_arts_path))

    # Convert to dict for JSON serialization
    manifest_dict = [group.model_dump() for group in manifest_data]

    # Write manifest.json
    manifest_path = projects_path / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_dict, f, indent=2)

    print(f"\nManifest generated successfully: {manifest_path}")
    print(f"Total timestamp groups: {len(manifest_dict)}")
    total_projects = sum(len(group['projects']) for group in manifest_dict)
    print(f"Total projects analyzed: {total_projects}")

if __name__ == "__main__":
    main()
