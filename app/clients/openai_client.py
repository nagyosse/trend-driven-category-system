from __future__ import annotations

from openai import OpenAI
from openai import OpenAIError

from app.core.settings import settings


class OpenAIClient:
    """
    Valódi OpenAI kliens a kategória-rangsor értelmezéséhez.

    - Responses API használata
    - rövid, üzleti fókuszú szöveg generálása
    """

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("Hiányzik az OPENAI_API_KEY környezeti változó.")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def explain_ranking(self, prompt: str) -> str:
        """
        AI válasz generálása a rangsor alapján.
        """

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=(
                    "Te egy senior e-kereskedelmi adat elemző vagy. "
                    "A válasz legyen rövid, tárgyilagos és üzleti szemléletű. "
                    "Kerüld a felesleges általánosságokat. "
                    "A cél: gyors döntéstámogatás."
                ),
                input=prompt,
            )

            return response.output_text.strip()

        except OpenAIError as e:
            return (
                "Hiba történt az AI szolgáltatás hívása során. "
                f"Részletek: {str(e)}"
            )

        except Exception as e:
            return (
                "Ismeretlen hiba történt az AI feldolgozás során. "
                f"Részletek: {str(e)}"
            )
