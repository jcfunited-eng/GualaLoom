"""
Logic Encoding — premise→conclusion as settling; L6 validates.

STATUS: DORMANT. Built and tested in isolation. Not wired to the
living substrate until school activates.

Logic IS the substrate settling under constraints. Premises constrain
the field; the valid conclusion is the state with the only remaining
freedom after constraints apply; L6 fires when the conclusion is
forced (n_eff < n/e). Invalid arguments don't settle — the field
holds null. "This does not follow" is a first-class result.

No emotion. No reward. Valid = L6 fires. Invalid = L6 does not fire.
"""

from typing import List, Optional, Tuple

from ..substrate import (
    encode_to_strand, settle_field, l6_freedom,
    TRITS_PER_STRAND, DEAD_ZONE_BASE,
)


# ── Proposition encoding ─────────────────────────────────────

def encode_proposition(label: str) -> Tuple[int, ...]:
    """Encode a proposition label as a trit strand.
    Deterministic: same label → same strand."""
    # Use character sum mod 3^8 for deterministic encoding
    val = sum(ord(c) * (i + 1) for i, c in enumerate(label)) % (3 ** TRITS_PER_STRAND)
    return encode_to_strand(val)


# ── Logical forms ────────────────────────────────────────────

class Argument:
    """A logical argument: premises + conclusion.

    The substrate evaluates this by settling the premises as
    constraints and checking whether the conclusion is forced.
    """
    __slots__ = ("premises", "conclusion", "label", "expected_valid")

    def __init__(self, premises: List[str], conclusion: str,
                 label: str = "", expected_valid: bool = True):
        self.premises = premises
        self.conclusion = conclusion
        self.label = label
        self.expected_valid = expected_valid


class LogicEngine:
    """Evaluates arguments by settling premise-strands and checking L6.

    DORMANT. Call evaluate() to test in isolation.

    The mechanism:
    1. Encode each premise as a trit strand.
    2. Encode the conclusion as a trit strand.
    3. Settle the premises together (they constrain the field).
    4. Check: does the settled premise-field, when the conclusion
       strand is added, produce L6 structural lock?
       - Yes → the conclusion is forced by the premises (VALID).
       - No → the conclusion is not forced (INVALID or UNDETERMINED).

    This is not a truth-table evaluator. It's the substrate doing
    what it always does — settling under constraint until freedom
    collapses. Logic is what that looks like when the input is
    structured argument.
    """

    def evaluate(self, arg: Argument) -> Tuple[bool, dict]:
        """Evaluate an argument. Returns (fires_valid, details).

        fires_valid: True if L6 fires with the conclusion added
        (the argument is structurally valid — premises force conclusion).
        """
        # Encode premises as strands
        premise_strands = [encode_proposition(p) for p in arg.premises]

        # Settle premises alone
        if premise_strands:
            premise_settled = settle_field(premise_strands, familiarity=0)
            p_eff, p_coll, p_knee = l6_freedom(premise_settled)
        else:
            premise_settled = ()
            p_eff, p_coll, p_knee = 0, 0, 0

        # Encode conclusion
        conc_strand = encode_proposition(arg.conclusion)

        # Settle premises + conclusion together
        all_strands = premise_strands + [conc_strand]
        full_settled = settle_field(all_strands, familiarity=0)
        f_eff, f_coll, f_knee = l6_freedom(full_settled)

        # L6 fires when the conclusion is added and freedom drops
        # below the knee — the conclusion is FORCED by the premises.
        l6_fires = f_eff < f_knee

        # Additional signal: did adding the conclusion INCREASE
        # collapse significantly? If the conclusion is consistent
        # with the premises, adding it should increase collapse
        # (the field agrees). If inconsistent, collapse may decrease
        # or not increase.
        collapse_delta = f_coll - p_coll if premise_settled else f_coll

        details = {
            "premises_collapsed": p_coll,
            "premises_total": len(premise_settled) if premise_settled else 0,
            "full_collapsed": f_coll,
            "full_total": len(full_settled),
            "full_effective": f_eff,
            "full_knee": f_knee,
            "l6_fires": l6_fires,
            "collapse_delta": collapse_delta,
        }
        return l6_fires, details

    def assess(self, arg: Argument) -> Tuple[bool, bool, dict]:
        """Assess whether the engine gets the right answer.

        Returns (correct, fires_valid, details).
        correct: True if fires_valid matches arg.expected_valid.
        """
        fires, details = self.evaluate(arg)
        correct = (fires == arg.expected_valid)
        return correct, fires, details
