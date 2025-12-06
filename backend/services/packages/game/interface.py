import json
from .types import ProjectEntry

class GameInterface:
    def __init__(self):
        self.manifest_path = "backend/projects/manifest.json"

    def add_project(self, project: ProjectEntry):
        manifest = self._load_manifest()
        manifest.append(project)
        self._save_manifest(manifest)

    def _load_manifest(self) -> list[ProjectEntry]:
        with open(self.manifest_path, "r") as f:
            manifest = json.load(f)
        return [ProjectEntry(**entry) for entry in manifest]

    def _save_manifest(self, manifest: list[ProjectEntry]):
        manifest_dict = [entry.model_dump() for entry in manifest]
        with open(self.manifest_path, "w") as f:
            json.dump(manifest_dict, f, indent=2)