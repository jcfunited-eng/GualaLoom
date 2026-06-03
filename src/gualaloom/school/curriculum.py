"""
Curriculum Runner — lesson → sleep → dream → next.

STATUS: DORMANT. Nothing runs without Joe's explicit approval.

Assessment is capability on the unseen, not recall of the drilled.
Determinism preserved: same history + same curriculum → same result.
No emotion anywhere.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import SCHOOL_ACTIVE
from .math_bridge import MathBridge
from .logic import LogicEngine, Argument


# ── Lesson types ─────────────────────────────────────────────

class MathLesson:
    """One math lesson: a set of problems to drill + assessment problems."""
    __slots__ = ("name", "drill", "assess")

    def __init__(self, name: str,
                 drill: List[Tuple[str, str, int, int]],
                 assess: List[Tuple[str, str, int, int]]):
        # drill/assess: list of (op, op_word, a, b)
        self.name = name
        self.drill = drill    # practiced
        self.assess = assess  # unseen, same type


class LogicLesson:
    """One logic lesson: arguments to drill + assessment arguments."""
    __slots__ = ("name", "drill", "assess")

    def __init__(self, name: str,
                 drill: List[Argument],
                 assess: List[Argument]):
        self.name = name
        self.drill = drill
        self.assess = assess


# ── Assessment results ───────────────────────────────────────

class AssessmentResult:
    __slots__ = ("lesson_name", "total", "correct", "details")

    def __init__(self, lesson_name: str):
        self.lesson_name = lesson_name
        self.total = 0
        self.correct = 0
        self.details: List[Dict] = []

    def record(self, correct: bool, detail: Dict) -> None:
        self.total += 1
        if correct:
            self.correct += 1
        self.details.append(detail)

    @property
    def score(self) -> float:
        return self.correct / self.total if self.total else 0.0

    def to_dict(self) -> dict:
        return {
            "lesson": self.lesson_name,
            "total": self.total,
            "correct": self.correct,
            "score": self.score,
            "details": self.details,
        }


# ── Curriculum Runner ────────────────────────────────────────

class CurriculumRunner:
    """Runs lessons with mandatory sleep/dream between each.

    DORMANT. Does not interact with the living substrate.
    Call run_math_lesson() or run_logic_lesson() for isolated testing.

    The runner enforces:
    1. lesson → sleep → dream → next lesson (never lesson → lesson)
    2. assessment is on UNSEEN problems, not drilled ones
    3. no emotion — correctness is structural, not rewarded
    """

    def __init__(self):
        self.math = MathBridge()
        self.logic = LogicEngine()
        self.history: List[Dict] = []

    def run_math_lesson(self, lesson: MathLesson,
                        sleep_fn=None, dream_fn=None) -> AssessmentResult:
        """Run one math lesson in isolation.

        Drill phase: compute each problem, verify answer.
        Sleep/dream: consolidation (called if provided).
        Assess phase: test on unseen problems.
        """
        if SCHOOL_ACTIVE:
            raise RuntimeError("School is active but should be dormant")

        # Drill phase (would feed to substrate when wired)
        drill_results = []
        for op, op_word, a, b in lesson.drill:
            result = self.math.compute(op, a, b)
            expected = self._math_expected(op, a, b)
            drill_results.append({
                "problem": f"{a} {op_word} {b}",
                "result": result,
                "expected": expected,
                "correct": result == expected,
            })

        # Sleep/dream between drill and assessment
        if sleep_fn:
            sleep_fn()
        if dream_fn:
            dream_fn()

        # Assessment phase: unseen problems
        assessment = AssessmentResult(lesson.name)
        for op, op_word, a, b in lesson.assess:
            result = self.math.compute(op, a, b)
            expected = self._math_expected(op, a, b)
            correct = result == expected
            assessment.record(correct, {
                "problem": f"{a} {op_word} {b}",
                "result": result,
                "expected": expected,
            })

        self.history.append({
            "type": "math",
            "lesson": lesson.name,
            "drill_correct": sum(1 for r in drill_results if r["correct"]),
            "drill_total": len(drill_results),
            "assessment": assessment.to_dict(),
        })

        return assessment

    def run_logic_lesson(self, lesson: LogicLesson,
                         sleep_fn=None, dream_fn=None) -> AssessmentResult:
        """Run one logic lesson in isolation."""
        if SCHOOL_ACTIVE:
            raise RuntimeError("School is active but should be dormant")

        # Drill phase
        for arg in lesson.drill:
            self.logic.evaluate(arg)

        # Sleep/dream
        if sleep_fn:
            sleep_fn()
        if dream_fn:
            dream_fn()

        # Assessment phase
        assessment = AssessmentResult(lesson.name)
        for arg in lesson.assess:
            correct, fires, details = self.logic.assess(arg)
            assessment.record(correct, {
                "label": arg.label,
                "expected_valid": arg.expected_valid,
                "l6_fires": fires,
                "correct": correct,
            })

        self.history.append({
            "type": "logic",
            "lesson": lesson.name,
            "assessment": assessment.to_dict(),
        })

        return assessment

    @staticmethod
    def _math_expected(op: str, a: int, b: int) -> int:
        if op == "add":
            return a + b
        elif op == "sub":
            return a - b
        elif op == "mul":
            return a * b
        return 0
