import json
import re
from pathlib import Path
from .types import ProjectEntry

class GameInterface:
    def __init__(self):
        # Get the path relative to the backend directory
        backend_dir = Path(__file__).parent.parent.parent.parent
        self.manifest_path = backend_dir / "projects" / "manifest.json"

    def add_project(self, project: ProjectEntry):
        # Extract timestamp from path if not already set
        if not project.timestamp:
            project.timestamp = self._extract_timestamp(project.path_to_index_html)
        manifest = self._load_manifest()
        manifest.append(project)
        self._save_manifest(manifest)

    def _extract_timestamp(self, path: str) -> str:
        """Extract timestamp from path like './projects/20251205_202015/1/index.html'"""
        match = re.search(r'projects/(\d{8}_\d{6})/', path)
        return match.group(1) if match else ''

    def _load_manifest(self) -> list[ProjectEntry]:
        with open(self.manifest_path, "r") as f:
            manifest = json.load(f)

        entries = []
        for entry in manifest:
            # Backfill timestamp for existing entries that don't have it
            if 'timestamp' not in entry or not entry['timestamp']:
                entry['timestamp'] = self._extract_timestamp(entry.get('path_to_index_html', ''))
            entries.append(ProjectEntry(**entry))
        return entries

    def _save_manifest(self, manifest: list[ProjectEntry]):
        manifest_dict = [entry.model_dump() for entry in manifest]
        with open(self.manifest_path, "w") as f:
            json.dump(manifest_dict, f, indent=2)