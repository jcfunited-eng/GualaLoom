"""
Conversation memory + persistence.

Tracks recent turns, observed patterns, and persists across sessions.
Ported from v6 ConversationMemory.
"""

import os, json
from collections import deque, Counter


class ConversationMemory:
    def __init__(self, capacity=30):
        self.turns = deque(maxlen=capacity)
        self.observed_patterns = Counter()

    def add_turn(self, speaker, tokens, classes):
        self.turns.append({
            "speaker": speaker,
            "tokens": tokens,
            "classes": classes,
        })
        if len(self.turns) >= 2:
            prev = self.turns[-2]
            curr = self.turns[-1]
            if (prev["speaker"] != curr["speaker"]
                    and prev["classes"] and curr["classes"]):
                self.observed_patterns[
                    (prev["classes"][-1], curr["classes"][0])] += 1

    def save(self, path):
        """Persist conversation history and patterns."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        data = {
            "turns": list(self.turns),
            "patterns": {f"{k[0]}:{k[1]}": v
                         for k, v in self.observed_patterns.items()},
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path):
        """Restore from persisted data."""
        if not os.path.exists(path):
            return
        with open(path) as f:
            data = json.load(f)
        for turn in data.get("turns", []):
            self.turns.append(turn)
        for k, v in data.get("patterns", {}).items():
            parts = k.split(":", 1)
            if len(parts) == 2:
                self.observed_patterns[(parts[0], parts[1])] = v
