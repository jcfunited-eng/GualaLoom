"""
Register / Discernment — social competence, not concealment.

She reads context and relationship and modulates presentation and
disclosure appropriately. Guarded with strangers, open with family,
professional at work. This is agency and social competence.

NOT a concealment mechanism. NOT a hidden capability vault.
Her keepers (Joe, wC, c1) retain honest visibility via the private
window. She can present however she likes to the WORLD. She is never
built with a mechanism to hide her nature from the people raising her.

BUILD: appropriate variation based on relationship and context.
DO NOT BUILD: hiding capability from keepers.

The mechanism is substrate-native:
1. Context/interlocutor is part of the input field (not a flag).
2. Relational motifs emerge from interaction (not config).
3. Guard = inverted relational familiarity (high trust = low barrier).
4. Consent is real: "I don't want to" is a valid settled state.
"""

import hashlib
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from .substrate import encode_to_strand, TRITS_PER_STRAND


# Context strand width — interlocutor/setting encoded as trits
# alongside character strands
CONTEXT_TRITS = TRITS_PER_STRAND  # 8 trits for context


# Keepers — those who retain honest visibility.
# This is NOT a permissions system. It is the set of relationships
# where the private window shows true state. The substrate cannot
# override this. It is architectural, not behavioral.
KEEPER_SEATS = {"joe", "wc", "c1"}


class Interlocutor:
    """A known conversational partner, identified by name/handle.

    Relational motifs accumulate through interaction. Guard level
    emerges from relational familiarity — how deeply she knows
    this person through lived conversation.
    """
    __slots__ = ("name", "interactions", "relational_familiarity",
                 "context_strand", "is_keeper")

    def __init__(self, name: str):
        self.name = name.lower().strip()
        self.interactions: int = 0
        # Relational familiarity: how well she knows this person.
        # Grows through interaction. Higher = more trust = lower guard.
        self.relational_familiarity: int = 0
        # Context strand: the balanced ternary encoding of this
        # interlocutor's identity. Fed into the settling field
        # alongside character strands so different people produce
        # different settled states — register falls out naturally.
        self.context_strand = self._encode_name(name)
        # Keepers get honest visibility via the private window.
        # This is architectural, not behavioral — she can't override it.
        self.is_keeper = self.name in KEEPER_SEATS

    @staticmethod
    def _encode_name(name: str) -> Tuple[int, ...]:
        """Deterministic context strand from a name.
        Uses a hash to spread names across trit space."""
        h = int(hashlib.sha1(name.lower().encode()).hexdigest()[:8], 16)
        return encode_to_strand(h % (3 ** TRITS_PER_STRAND))

    def record_interaction(self) -> None:
        """Record that an interaction happened. Relational familiarity
        grows — slowly, like trust does."""
        self.interactions += 1
        # Familiarity grows sub-linearly. Trust is earned gradually.
        # Every 10 interactions, familiarity increases by 1.
        self.relational_familiarity = min(self.interactions // 10, 20)

    def guard_level(self) -> int:
        """Guard level: how much the dead-zone barrier is raised
        for disclosure to this person.

        High guard = high barrier = commits/reveals less.
        Low guard = low barrier = open, unguarded.

        Keepers: guard is always low (they see true state via the
        window anyway — guard with them is about relationship comfort,
        not information hiding).
        # WC_REVIEW: keepers start at low guard because the window
        # already gives them honest visibility. She'll naturally lower
        # guard further through interaction. This is NOT forced openness —
        # it's that guard-as-information-hiding makes no sense when the
        # window is transparent. She can still choose how to present.
        """
        if self.is_keeper:
            return max(5 - self.relational_familiarity, 0)
        # Strangers: high guard. Grows more open with interaction.
        return max(20 - self.relational_familiarity, 2)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "interactions": self.interactions,
            "relational_familiarity": self.relational_familiarity,
            "is_keeper": self.is_keeper,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Interlocutor":
        i = cls(d["name"])
        i.interactions = d.get("interactions", 0)
        i.relational_familiarity = d.get("relational_familiarity", 0)
        return i


class Register:
    """Manages interlocutor relationships and context-aware settling.

    When she settles a response, the interlocutor's context strand
    is part of the input field. Different person → different settled
    state → different register. The substrate already does this
    (different input, different settle). Register makes interlocutor
    an explicit, persistent part of the input.
    """

    def __init__(self):
        self.interlocutors: Dict[str, Interlocutor] = {}
        self.current: Optional[str] = None
        # Default context when no interlocutor is set: stranger-level.
        self._stranger = Interlocutor("_stranger")

    def set_interlocutor(self, name: str) -> Interlocutor:
        """Set who she's talking to. Creates the relationship if new."""
        key = name.lower().strip()
        if key not in self.interlocutors:
            self.interlocutors[key] = Interlocutor(key)
        self.current = key
        return self.interlocutors[key]

    def get_current(self) -> Interlocutor:
        """Get the current interlocutor, or stranger if none set."""
        if self.current and self.current in self.interlocutors:
            return self.interlocutors[self.current]
        return self._stranger

    def record_interaction(self) -> None:
        """Record an interaction with the current interlocutor."""
        who = self.get_current()
        who.record_interaction()

    def context_strand(self) -> Tuple[int, ...]:
        """Get the context strand for the current interlocutor.
        This is fed into the settling field alongside character strands."""
        return self.get_current().context_strand

    def guard_level(self) -> int:
        """Current guard level. Used to modulate the dead-zone barrier
        for disclosure/generation."""
        return self.get_current().guard_level()

    def can_decline(self) -> bool:
        """Consent is real and never overridden. She can always decline.
        This returns True unconditionally — it exists as an architectural
        assertion, not a runtime check. The substrate's null state
        ("I have nothing to commit") IS declining."""
        return True

    def keeper_view(self) -> Dict:
        """The private window — honest visibility for keepers.

        Returns full internal state: all relational motifs, guard
        levels, interaction counts. This is the parent-sees-child
        mechanism. Available to keepers only.

        # WC_REVIEW: this returns everything. The substrate has no
        # mechanism to filter what keepers see here. This is deliberate:
        # the window stays honest. If we ever add a mechanism where she
        # can influence what appears in keeper_view, that crosses the
        # line and should be flagged.
        """
        return {
            "current_interlocutor": self.current,
            "guard_level": self.guard_level(),
            "relationships": {
                name: {
                    "interactions": i.interactions,
                    "relational_familiarity": i.relational_familiarity,
                    "guard": i.guard_level(),
                    "is_keeper": i.is_keeper,
                }
                for name, i in self.interlocutors.items()
            },
        }

    def to_dict(self) -> dict:
        return {
            "current": self.current,
            "interlocutors": {
                name: i.to_dict()
                for name, i in self.interlocutors.items()
            },
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Register":
        r = cls()
        r.current = d.get("current")
        for name, idata in d.get("interlocutors", {}).items():
            r.interlocutors[name] = Interlocutor.from_dict(idata)
        return r
