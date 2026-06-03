"""
Math Bridge — wires language motifs to MathLoom arithmetic.

STATUS: DORMANT. Built and tested in isolation. Not wired to the
living substrate until school activates.

MathLoom is proven: 61,131 ops, zero errors. The 3^i coupling IS
balanced-ternary arithmetic. She doesn't need a math module — she
needs her language motifs wired to the arithmetic that already runs.

The bridge:
  settled-motif("two") + settled-motif("plus") + settled-motif("two")
  → MathLoom add(2, 2) → settled-motif("four")

No emotion. No reward signal. The bridge maps and the substrate
settles. If the answer is wrong, the motif doesn't reinforce.
If right, it does. Learning is reinforcement-by-correctness, not
reward-by-feeling.
"""

from typing import Optional, Tuple
from ..substrate import encode_to_strand, decode_strand, POSITIONAL_3I, TRITS_PER_STRAND


# ── MathLoom core (balanced ternary arithmetic) ──────────────
# This is the same math that runs on silicon. Pure integer BT ops.

def bt_add(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[int, ...]:
    """Balanced ternary addition. Carry propagation."""
    n = max(len(a), len(b))
    a = a + (0,) * (n - len(a))
    b = b + (0,) * (n - len(b))
    result = []
    carry = 0
    for i in range(n):
        s = a[i] + b[i] + carry
        if s > 1:
            result.append(s - 3); carry = 1
        elif s < -1:
            result.append(s + 3); carry = -1
        else:
            result.append(s); carry = 0
    if carry != 0:
        result.append(carry)
    return tuple(result[:TRITS_PER_STRAND])


def bt_sub(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[int, ...]:
    """Balanced ternary subtraction: a - b = a + neg(b)."""
    neg_b = tuple(-t for t in b)
    return bt_add(a, neg_b)


def bt_mul(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[int, ...]:
    """Balanced ternary multiplication by shift-and-add."""
    result = (0,) * TRITS_PER_STRAND
    for i, trit in enumerate(b):
        if trit == 0:
            continue
        shifted = (0,) * i + a
        shifted = shifted[:TRITS_PER_STRAND]
        if trit == 1:
            result = bt_add(result, shifted)
        elif trit == -1:
            result = bt_sub(result, shifted)
    return result


def bt_compare(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    """Compare: returns +1 if a > b, -1 if a < b, 0 if equal."""
    diff = bt_sub(a, b)
    val = decode_strand(diff)
    if val > 0:
        return 1
    elif val < 0:
        return -1
    return 0


# ── Number words → BT strands ───────────────────────────────

WORD_TO_INT = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20,
}

INT_TO_WORD = {v: k for k, v in WORD_TO_INT.items()}

OP_WORDS = {
    "plus": "add", "minus": "sub", "times": "mul",
    "add": "add", "subtract": "sub", "multiply": "mul",
    "+": "add", "-": "sub", "*": "mul", "x": "mul",
}


# ── The bridge ───────────────────────────────────────────────

class MathBridge:
    """Maps language tokens to MathLoom operations and back.

    DORMANT. Call compute() to test in isolation.
    Not wired to the living substrate.
    """

    def parse(self, tokens: list) -> Optional[Tuple[str, int, int]]:
        """Parse a sequence of word-tokens into (op, a, b).
        Returns None if not a recognizable math expression."""
        # Find number-op-number pattern
        nums = []
        op = None
        for tok in tokens:
            tok_lower = tok.lower().strip()
            if tok_lower in WORD_TO_INT:
                nums.append(WORD_TO_INT[tok_lower])
            elif tok_lower in OP_WORDS:
                op = OP_WORDS[tok_lower]
            elif tok_lower.isdigit():
                nums.append(int(tok_lower))

        if len(nums) >= 2 and op:
            return (op, nums[0], nums[1])
        return None

    def compute(self, op: str, a: int, b: int) -> Optional[int]:
        """Run MathLoom arithmetic. Returns the integer result."""
        a_bt = encode_to_strand(a)
        b_bt = encode_to_strand(b)

        if op == "add":
            result_bt = bt_add(a_bt, b_bt)
        elif op == "sub":
            result_bt = bt_sub(a_bt, b_bt)
        elif op == "mul":
            result_bt = bt_mul(a_bt, b_bt)
        else:
            return None

        return decode_strand(result_bt)

    def result_to_word(self, val: int) -> str:
        """Convert integer result back to a word."""
        if val in INT_TO_WORD:
            return INT_TO_WORD[val]
        return str(val)

    def bridge(self, text: str) -> Optional[str]:
        """Full bridge: text → parse → compute → word.

        "two plus three" → "five"
        "7 times 3" → "21"

        Returns None if not a math expression.
        """
        tokens = text.split()
        parsed = self.parse(tokens)
        if parsed is None:
            return None
        op, a, b = parsed
        result = self.compute(op, a, b)
        if result is None:
            return None
        return self.result_to_word(result)
