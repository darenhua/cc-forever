from pydantic import BaseModel, Field
from typing import Optional

class GameMetadata(BaseModel):
    name: str
    summary: str
    base_game: str
    genre: list[str]
    prompt: str

class ProjectEntry(BaseModel):
    id: str
    timestamp: Optional[str] = None  # e.g., "20251205_202015"
    path_to_index_html: str
    path_to_banner_art: Optional[str] = None
    path_to_cover_art: Optional[str] = None
    metadata: GameMetadata
    job_report: Optional["JobReport"] = None

class JobReport(BaseModel):
    name: str = Field(description="a creative, catchy name for the game you made")
    summary: str = Field(description="description of what you made and how you did it")
    entry_point: str = Field(default="./projects/<uuid>/index.html", description="the entry point of the project")

# Rebuild ProjectEntry to resolve forward reference to JobReport
ProjectEntry.model_rebuild()