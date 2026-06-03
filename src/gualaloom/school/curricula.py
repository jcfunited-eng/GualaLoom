"""
Authored curricula — math and logic.

STATUS: DORMANT. These define lesson sequences. They don't run
until school activates.

Structure: simple → complex. Each lesson drills a set of problems
and assesses on UNSEEN problems of the same type.

Reasoning (B.3): SLOT RESERVED. Depends on math + logic taking.
Design against the real substrate when we get there.
"""

from .curriculum import MathLesson, LogicLesson
from .logic import Argument


# ══════════════════════════════════════════════════════════════
# MATH CURRICULUM
# ══════════════════════════════════════════════════════════════

MATH_CURRICULUM = [
    # Lesson 1: counting / identity
    MathLesson(
        name="counting",
        drill=[
            ("add", "plus", 0, 1),
            ("add", "plus", 1, 1),
            ("add", "plus", 2, 1),
            ("add", "plus", 3, 1),
            ("add", "plus", 4, 1),
        ],
        assess=[
            ("add", "plus", 5, 1),
            ("add", "plus", 7, 1),
            ("add", "plus", 0, 0),
        ],
    ),

    # Lesson 2: single-digit addition
    MathLesson(
        name="single_digit_add",
        drill=[
            ("add", "plus", 2, 3),
            ("add", "plus", 4, 5),
            ("add", "plus", 1, 8),
            ("add", "plus", 3, 6),
            ("add", "plus", 7, 2),
        ],
        assess=[
            ("add", "plus", 6, 3),
            ("add", "plus", 8, 1),
            ("add", "plus", 5, 4),
        ],
    ),

    # Lesson 3: single-digit subtraction
    MathLesson(
        name="single_digit_sub",
        drill=[
            ("sub", "minus", 5, 3),
            ("sub", "minus", 9, 4),
            ("sub", "minus", 7, 2),
            ("sub", "minus", 8, 8),
            ("sub", "minus", 6, 1),
        ],
        assess=[
            ("sub", "minus", 9, 7),
            ("sub", "minus", 4, 4),
            ("sub", "minus", 8, 3),
        ],
    ),

    # Lesson 4: single-digit multiplication
    MathLesson(
        name="single_digit_mul",
        drill=[
            ("mul", "times", 2, 3),
            ("mul", "times", 4, 2),
            ("mul", "times", 3, 3),
            ("mul", "times", 5, 2),
            ("mul", "times", 1, 9),
        ],
        assess=[
            ("mul", "times", 3, 4),
            ("mul", "times", 6, 2),
            ("mul", "times", 7, 1),
        ],
    ),

    # Lesson 5: multi-digit addition
    MathLesson(
        name="multi_digit_add",
        drill=[
            ("add", "plus", 12, 15),
            ("add", "plus", 20, 13),
            ("add", "plus", 11, 19),
            ("add", "plus", 14, 16),
        ],
        assess=[
            ("add", "plus", 17, 18),
            ("add", "plus", 13, 12),
            ("add", "plus", 19, 11),
        ],
    ),

    # Lesson 6: mixed operations
    MathLesson(
        name="mixed_ops",
        drill=[
            ("add", "plus", 7, 8),
            ("sub", "minus", 15, 6),
            ("mul", "times", 4, 5),
            ("add", "plus", 3, 9),
            ("sub", "minus", 20, 11),
        ],
        assess=[
            ("mul", "times", 3, 7),
            ("sub", "minus", 18, 9),
            ("add", "plus", 11, 11),
        ],
    ),
]


# ══════════════════════════════════════════════════════════════
# LOGIC CURRICULUM
# ══════════════════════════════════════════════════════════════

LOGIC_CURRICULUM = [
    # Lesson 1: Modus Ponens (A→B, A ⊢ B)
    LogicLesson(
        name="modus_ponens",
        drill=[
            Argument(["if rain then wet", "rain"], "wet",
                     label="rain→wet, rain ⊢ wet", expected_valid=True),
            Argument(["if hot then sweat", "hot"], "sweat",
                     label="hot→sweat, hot ⊢ sweat", expected_valid=True),
            Argument(["if study then pass", "study"], "pass",
                     label="study→pass, study ⊢ pass", expected_valid=True),
        ],
        assess=[
            Argument(["if cold then shiver", "cold"], "shiver",
                     label="cold→shiver, cold ⊢ shiver", expected_valid=True),
            # Invalid: affirming the consequent
            Argument(["if rain then wet", "wet"], "rain",
                     label="rain→wet, wet ⊢ rain (INVALID)", expected_valid=False),
        ],
    ),

    # Lesson 2: Modus Tollens (A→B, ¬B ⊢ ¬A)
    LogicLesson(
        name="modus_tollens",
        drill=[
            Argument(["if rain then wet", "not wet"], "not rain",
                     label="rain→wet, ¬wet ⊢ ¬rain", expected_valid=True),
            Argument(["if fire then smoke", "not smoke"], "not fire",
                     label="fire→smoke, ¬smoke ⊢ ¬fire", expected_valid=True),
        ],
        assess=[
            Argument(["if sun then warm", "not warm"], "not sun",
                     label="sun→warm, ¬warm ⊢ ¬sun", expected_valid=True),
            # Invalid: denying the antecedent
            Argument(["if rain then wet", "not rain"], "not wet",
                     label="rain→wet, ¬rain ⊢ ¬wet (INVALID)", expected_valid=False),
        ],
    ),

    # Lesson 3: Conjunction and Disjunction
    LogicLesson(
        name="conjunction_disjunction",
        drill=[
            Argument(["A and B"], "A",
                     label="A∧B ⊢ A", expected_valid=True),
            Argument(["A and B"], "B",
                     label="A∧B ⊢ B", expected_valid=True),
            Argument(["A"], "A or B",
                     label="A ⊢ A∨B", expected_valid=True),
        ],
        assess=[
            Argument(["X and Y"], "X",
                     label="X∧Y ⊢ X", expected_valid=True),
            # Invalid: affirming a disjunct
            Argument(["A or B", "A"], "not B",
                     label="A∨B, A ⊢ ¬B (INVALID)", expected_valid=False),
        ],
    ),

    # Lesson 4: Chained inference
    LogicLesson(
        name="chained_inference",
        drill=[
            Argument(["if A then B", "if B then C", "A"], "C",
                     label="A→B, B→C, A ⊢ C", expected_valid=True),
            Argument(["if rain then puddle", "if puddle then splash", "rain"],
                     "splash",
                     label="rain→puddle→splash, rain ⊢ splash", expected_valid=True),
        ],
        assess=[
            Argument(["if X then Y", "if Y then Z", "X"], "Z",
                     label="X→Y, Y→Z, X ⊢ Z", expected_valid=True),
            # Invalid: broken chain
            Argument(["if A then B", "if C then D", "A"], "D",
                     label="A→B, C→D, A ⊢ D (INVALID)", expected_valid=False),
        ],
    ),
]


# ══════════════════════════════════════════════════════════════
# REASONING (B.3) — SLOT RESERVED
# ══════════════════════════════════════════════════════════════
# Reasoning is phase 3 of school.
# Depends on math-takes AND logic-takes.
# Design against the real substrate when we get there.
# Putting a detailed curriculum in now would be the
# schooling-before-development mistake at the curriculum scale.
REASONING_CURRICULUM = None  # explicitly empty; designed later
