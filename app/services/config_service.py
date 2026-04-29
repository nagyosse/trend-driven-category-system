from __future__ import annotations

import json
from pathlib import Path

from app.schemas.analyze import AnalyzeRequest


class ConfigService:
    """
    Az IPO modell Input részének feldolgozása.

    Feladata:
    - AnalyzeRequest validált bemenet átalakítása
    - categories.json előállítása
    - keywords.json előállítása
    """

    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir
        self.categories_path = self.config_dir / "categories.json"
        self.keywords_path = self.config_dir / "keywords.json"

    def build_categories_config(self, request: AnalyzeRequest) -> dict[str, str]:
        return {
            category.category_id: category.category_name
            for category in request.categories
        }

    def build_keywords_config(self, request: AnalyzeRequest) -> dict[str, list[str]]:
        return {
            category.category_id: category.keywords
            for category in request.categories
        }

    def save_json(self, path: Path, data: dict) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def save_input_config(self, request: AnalyzeRequest) -> tuple[Path, Path]:
        categories_config = self.build_categories_config(request)
        keywords_config = self.build_keywords_config(request)

        self.save_json(self.categories_path, categories_config)
        self.save_json(self.keywords_path, keywords_config)

        return self.categories_path, self.keywords_path
