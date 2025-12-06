from pydantic import BaseModel
from typing import Optional

class GameMetadata(BaseModel):
    name: str
    summary: str
    base_game: str
    genre: list[str]
    prompt: str

class ProjectEntry(BaseModel):
    id: str
    path_to_index_html: str
    path_to_banner_art: Optional[str] = None
    path_to_cover_art: Optional[str] = None
    metadata: GameMetadata
    job_report: Optional["JobReport"] = None

class JobReport(BaseModel):
    name: str
    summary: str
    entry_point: str

# Rebuild ProjectEntry to resolve forward reference to JobReport
ProjectEntry.model_rebuild()