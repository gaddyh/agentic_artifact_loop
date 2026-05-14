from pathlib import Path
import json
from datetime import datetime


class ArtifactStore:
    def __init__(self, base_dir: str = "results/runs"):
        self.base_dir = Path(base_dir)

    def create_run_dir(self, stage_name: str) -> Path:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        run_dir = self.base_dir / stage_name / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def save_json(self, path: Path, obj) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else obj
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def save_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
