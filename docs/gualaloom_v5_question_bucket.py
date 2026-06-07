"""
gualaloom_v5_question_bucket.py — Open questions accumulated during reading

Joe's framing: "as she reads she should be asking questions internally and
should have a bucket full of questions - like a child when engaged externally."

Reading produces questions automatically when she encounters knowledge gaps:
- Subject-class word with incomplete sensory binding ("what does sun taste like?")
- Word with no role classification ("what is X?")
- Topic seen many times but never with certain verbs ("what does X do?")

Conversation surfaces questions when:
- Input topic relates to a bucket question (chi-overlap)
- No recall is possible for the input (she has nothing else to say)
- Pair-bond is active and novelty need is unmet (she initiates)

Three criteria for selective cheat: named (this file), retirement path (templates
become substrate-emitted phrasing once cascade is strong enough),
non-foreclosing (uses real chi from krimelack, real gap detection).
"""
import math
from collections import OrderedDict


# Question kind → template. Templates use substrate vocabulary only.
# Each template's words must exist in the seed corpus so she can compose them.
QUESTION_TEMPLATES = {
    "color":      "what color is {topic}",
    "taste":      "what does {topic} taste like",
    "smell":      "what does {topic} smell like",
    "sound":      "what does {topic} sound like",
    "feel":       "what does {topic} feel like",
    "definition": "what is {topic}",
    "action":     "what does {topic} do",
    "where":      "where is {topic}",
}

# Sensory modality → question kind mapping for gap-detection
MODALITY_TO_KIND = {
    "sight": "color",
    "sound": "sound",
    "smell": "smell",
    "taste": "taste",
    "touch": "feel",
}


class QuestionBucket:
    """Accumulates open questions she's developed during reading.

    Bounded capacity (FIFO eviction). Deduplicated by (topic, kind).
    Already-asked questions remembered separately so she doesn't repeat herself.
    """

    DEFAULT_CAPACITY = 200

    def __init__(self, capacity=None):
        self.capacity = capacity or self.DEFAULT_CAPACITY
        # OrderedDict: keys are (topic, kind), preserves insertion order for FIFO
        self.questions = OrderedDict()
        # Set of (topic, kind) tuples she's already asked aloud
        self.asked = set()

    def add(self, topic, topic_chi, kind, tick, context=None):
        """Queue a question if not already asked or queued.
        Returns True if added, False if duplicate or unknown kind."""
        if kind not in QUESTION_TEMPLATES:
            return False
        key = (topic, kind)
        if key in self.asked:
            return False
        if key in self.questions:
            # Reinforce existing — bump to back (more recent)
            q = self.questions.pop(key)
            q["last_tick"] = tick
            q["weight"] = q.get("weight", 1) + 1
            self.questions[key] = q
            return True
        # New question
        self.questions[key] = {
            "topic": topic,
            "topic_chi": int(topic_chi),
            "kind": kind,
            "template": QUESTION_TEMPLATES[kind].format(topic=topic),
            "first_tick": tick,
            "last_tick": tick,
            "weight": 1,
            "context": context or "",
        }
        # Bounded — evict oldest if over capacity
        while len(self.questions) > self.capacity:
            self.questions.popitem(last=False)
        return True

    def find_for_chis(self, input_chis, band=2, input_words=None):
        """Find the most-reinforced question whose topic_chi is near any input
        chi. If input_words provided, strongly prefer questions whose topic IS
        one of the input content words."""
        if input_words is None:
            input_words = []
        input_words_lower = set(w.lower() for w in input_words)

        # Pass 1: questions whose topic word is literally in input
        direct_hits = [q for q in self.questions.values()
                       if q["topic"].lower() in input_words_lower]
        if direct_hits:
            return max(direct_hits, key=lambda q: q["weight"])

        # Pass 2: questions whose topic_chi is within band of any input chi
        chi_hits = []
        for q in self.questions.values():
            for ic in input_chis:
                if abs(q["topic_chi"] - ic) <= band:
                    chi_hits.append(q)
                    break
        if chi_hits:
            return max(chi_hits, key=lambda q: q["weight"])

        return None

    def find_for_topic_word(self, topic_word):
        """Find any unasked question about a specific topic word."""
        for q in self.questions.values():
            if q["topic"] == topic_word:
                return q
        return None

    def voice(self, question):
        """Mark a question as asked. Removes it from active bucket."""
        key = (question["topic"], question["kind"])
        self.questions.pop(key, None)
        self.asked.add(key)

    def peek_any(self):
        """Return the most-reinforced unasked question, or None."""
        if not self.questions:
            return None
        return max(self.questions.values(), key=lambda q: q["weight"])

    def snapshot(self):
        return {
            "pending": len(self.questions),
            "asked_lifetime": len(self.asked),
            "sample": [q["template"] for q in list(self.questions.values())[:5]],
        }


def generate_questions_from_word(bucket, word, role, sensory_dna_dict, chi, tick,
                                  known_actions_per_topic=None):
    """Reading-time gap detection. Called once per word commit.

    Generates questions based on knowledge gaps:
    1. Unknown word (no role DNA) → "what is X"
    2. Subject-class with missing sensory modalities → "what color/taste/etc is X"

    sensory_dna_dict: pass SENSORY_DNA from krimelack module
    known_actions_per_topic: dict tracking which verbs she's seen with each topic
                             (optional — passed for "what does X do" generation)
    """
    if len(word) < 2:
        return
    if word in {"i", "you", "we", "they", "he", "she", "it", "a", "an", "the",
                "is", "am", "are", "was", "were", "and", "or", "in", "on", "of",
                "to", "from", "with", "for", "at"}:
        return  # function words don't generate questions
    if word.isdigit():
        return  # numbers don't generate "what is" questions

    # 1. Unknown word — what is it?
    if role == "unknown":
        bucket.add(word, chi, "definition", tick)
        return

    # 2. Subject-class with incomplete sensory binding
    if role == "subject":
        existing = set(sensory_dna_dict.get(word, {}).keys())
        # For known things in SENSORY_DNA, ask about missing modalities
        if word in sensory_dna_dict:
            for modality, kind in MODALITY_TO_KIND.items():
                if modality not in existing:
                    bucket.add(word, chi, kind, tick,
                              context=f"missing_{modality}")
        else:
            # Subject-class but not in sensory DNA at all — wonder about senses
            bucket.add(word, chi, "color", tick, context="no_sensory")
            bucket.add(word, chi, "feel", tick, context="no_sensory")
