from __future__ import annotations

from pathlib import Path
import pandas as pd

from app.clients.openai_client import OpenAIClient
from app.core.settings import settings


class AIExplanationService:
    """
    AI alapú rangsor-értelmező szolgáltatás.

    Feladata:
    - a kész kategória-rangsor betöltése
    - prompt előállítása
    - opcionálisan AI segítségével üzleti értelmezés készítése
    """

    def __init__(self, ranking_csv: Path) -> None:
        self.ranking_csv = ranking_csv

    def load_ranking(self) -> pd.DataFrame:
        if not self.ranking_csv.exists():
            raise FileNotFoundError(f"Hiányzik a rangsor fájl: {self.ranking_csv}")

        return pd.read_csv(self.ranking_csv)

    def build_prompt(self, df: pd.DataFrame, top_n: int = 3) -> str:
        """
        Üzleti fókuszú prompt generálása.

        Cél:
        - ne csak leírás legyen
        - hanem döntéstámogató összefoglaló
        """
        top_df = df.sort_values("final_rank").head(top_n)

        lines = [
            "Feladat:",
            "Egy e-kereskedelmi rendszer kategória-rangsorának rövid üzleti értelmezése.",
            "",
            "Szabályok:",
            "- Ne írd felül a rangsort.",
            "- Ne találj ki új adatokat.",
            "- Maximum 5 mondat.",
            "- Magyar nyelven válaszolj.",
            "",
            "Fókusz:",
            "- Mely kategóriák a legerősebbek és miért?",
            "- Van-e rövid távú növekedés?",
            "- Mely kategóriák gyengülnek?",
            "- Milyen üzleti döntést indokol (pl. készlet, marketing)?",
            "",
            "Adatok:",
            "Top kategóriák:",
        ]

        for _, row in top_df.iterrows():
            lines.append(
                f"- helyezés: {int(row['final_rank'])}, "
                f"kategória: {row.get('category_name', row['category_id'])}, "
                f"avg_53w: {row['avg_53w']}, "
                f"avg_last_8w: {row['avg_last_8w']}, "
                f"active_weeks: {row['active_weeks']}, "
                f"peak_value: {row['peak_value']}"
            )

        return "\n".join(lines)

    def explain(self, top_n: int = 3) -> str:
        """
        AI magyarázat generálása.

        Ha AI ki van kapcsolva:
            → fallback szöveg

        Ha be van kapcsolva:
            → OpenAI API hívás
        """
        df = self.load_ranking()
        prompt = self.build_prompt(df, top_n=top_n)

        if not settings.ai_enabled:
            return (
                "Az AI modul jelenleg ki van kapcsolva. "
                "A rangsor ettől függetlenül teljes értékűen rendelkezésre áll."
            )

        client = OpenAIClient()
        return client.explain_ranking(prompt)
