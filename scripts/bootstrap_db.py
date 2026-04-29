from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.db.base import Base
from app.db.session import engine

# Fontos: modellek importálása, hogy a Base ismerje őket
import app.db.models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Adatbázis táblák létrehozva.")


if __name__ == "__main__":
    main()
