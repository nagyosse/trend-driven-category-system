from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.schemas.analyze import AnalyzeRequest
from app.services.config_service import ConfigService


def main() -> None:
    request = AnalyzeRequest(
        project_name="Teszt kategóriaelemzés",
        ai_enabled=True,
        categories=[
            {
                "category_id": "notebooks",
                "category_name": "Notebookok",
                "keywords": ["laptop", "notebook", "ultrabook"],
            },
            {
                "category_id": "components",
                "category_name": "PC-alkatrészek",
                "keywords": ["videókártya", "processzor", "memória"],
            },
        ],
    )

    service = ConfigService(config_dir=BASE_DIR / "config")
    categories_path, keywords_path = service.save_input_config(request)

    print("Konfiguráció mentve:")
    print(categories_path)
    print(keywords_path)


if __name__ == "__main__":
    main()
