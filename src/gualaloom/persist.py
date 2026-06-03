"""
Serialize/deserialize krimelack and loom state to the state/ directory.
JSON, human-readable, hand-editable.
"""

import json
from pathlib import Path
from typing import Optional

from .krimelack import Krimelack, Motif


STATE_DIR = Path("state")
KRIMELACK_PATH = STATE_DIR / "krimelack.json"
LOOM_STATE_PATH = STATE_DIR / "loom_state.json"
DREAMS_DIR = STATE_DIR / "dreams"


def ensure_dirs() -> None:
    STATE_DIR.mkdir(exist_ok=True)
    DREAMS_DIR.mkdir(exist_ok=True)


def save_krimelack(k: Krimelack) -> None:
    ensure_dirs()
    data = {
        "version": 1,
        "motifs": [m.to_dict() for m in k.motifs.values()],
    }
    KRIMELACK_PATH.write_text(json.dumps(data, indent=2))


def load_krimelack() -> Krimelack:
    k = Krimelack()
    if not KRIMELACK_PATH.exists():
        return k
    data = json.loads(KRIMELACK_PATH.read_text())
    for md in data.get("motifs", []):
        m = Motif.from_dict(md)
        k.motifs[m.fingerprint] = m
    return k


def save_loom_state(context_chars: int, recent: list,
                    familiarity: int,
                    last_settled: Optional[tuple]) -> None:
    ensure_dirs()
    data = {
        "context_chars": context_chars,
        "recent_chars": recent,
        "familiarity": familiarity,
        "last_settled": list(last_settled) if last_settled else [],
    }
    LOOM_STATE_PATH.write_text(json.dumps(data, indent=2))


def load_loom_state() -> Optional[dict]:
    if not LOOM_STATE_PATH.exists():
        return None
    return json.loads(LOOM_STATE_PATH.read_text())


def save_dream(dream_data: dict) -> None:
    ensure_dirs()
    ts = dream_data.get("started", "unknown").replace(":", "-")
    path = DREAMS_DIR / f"{ts}.json"
    path.write_text(json.dumps(dream_data, indent=2))
