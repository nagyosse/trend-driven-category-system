# scripts/trends_fetcher_long.py
# 12 hónap, HU – long/tidy formátum
from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd
from pytrends.request import TrendReq


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "config"
RAW_DIR = BASE_DIR / "data" / "raw"

GEO = "HU"
TIMEFRAME = "today 12-m"  # 12 hónap
HL = "hu-HU"
TZ = 60  # Europe/Budapest (perc)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_keyword_timeseries(pytrends: TrendReq, keyword: str) -> pd.DataFrame:
    pytrends.build_payload([keyword], geo=GEO, timeframe=TIMEFRAME)
    df = pytrends.interest_over_time()
    if df.empty:
        return df
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])
    return df


def to_long(df: pd.DataFrame, keyword: str, category_id: str) -> pd.DataFrame:
    # df index: date, column: keyword
    out = df.copy()
    out = out.rename(columns={keyword: "value"})
    out = out.reset_index().rename(columns={"date": "date"})
    out["keyword"] = keyword
    out["category_id"] = category_id
    out["geo"] = GEO
    out["timeframe"] = TIMEFRAME
    out["fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # oszlopsorrend
    out = out[["date", "keyword", "category_id", "value", "geo", "timeframe", "fetched_at"]]
    return out


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    categories = load_json(CONFIG_DIR / "categories.json")  # csak metadata
    keywords_cfg: Dict[str, List[str]] = load_json(CONFIG_DIR / "keywords.json")

    pytrends = TrendReq(hl=HL, tz=TZ, retries=3, backoff_factor=0.2)

    all_rows: List[pd.DataFrame] = []

    for category_id, keywords in keywords_cfg.items():
        category_name = categories.get(category_id, category_id)
        print(f"\n== Kategória: {category_id} ({category_name}) ==")

        for kw in keywords:
            print(f"  - Lekérés: {kw}")
            try:
                df = fetch_keyword_timeseries(pytrends, kw)
            except Exception as e:
                print(f"    ! Hiba ({kw}): {e}")
                continue

            if df.empty:
                print(f"    ! Nincs adat: {kw} (üres idősor)")
            else:
                # df oszlopneve pontosan a keyword
                # néha a pytrends oszlopneve kicsit módosulhat, ezért biztosítjuk:
                col = df.columns[0]
                df = df.rename(columns={col: kw})

                long_df = to_long(df, kw, category_id)
                all_rows.append(long_df)
                print(f"    ✓ Sorok: {len(long_df)}")

            # 429 ellen véletlen várakozás
            time.sleep(random.uniform(6, 10))

    if not all_rows:
        print("\nNem keletkezett egyetlen adatsor sem (minden lekérés üres/hibás volt).")
        return

    result = pd.concat(all_rows, ignore_index=True)

    out_path = RAW_DIR / "trends_long.csv"
    result.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"\nKész. Mentve: {out_path.relative_to(BASE_DIR)}")
    print(f"Összes sor: {len(result)}")


if __name__ == "__main__":
    main()

