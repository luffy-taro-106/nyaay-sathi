import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SEED_FILE = BASE_DIR / "data" / "employment" / "acts_and_cases.seed.json"
OUTPUT_FILE = BASE_DIR / "data" / "employment" / "acts_and_cases.json"


def main() -> None:
    seed_rows = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    OUTPUT_FILE.write_text(json.dumps(seed_rows, indent=2), encoding="utf-8")
    print(f"Ingest complete: wrote {len(seed_rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
