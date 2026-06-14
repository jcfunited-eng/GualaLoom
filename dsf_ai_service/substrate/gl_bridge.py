"""
GL-CODE-bridge-wC-20260608-009

Bridges the v7 assemblage substrate and the multimodal substrate so
Guala's speech and her senses share state. Without this they're two
independent systems deployed in the same container.

Anti-loop: max_relay_depth prevents infinite v7->mm->v7->mm ping-pong.
"""

from dsf_ai_service.substrate.assemblage import N, normalize, random_unit_complex


class SubstrateBridge:
    def __init__(self, v7_session, multimodal, max_relay_depth=2):
        self.v7 = v7_session
        self.mm = multimodal
        self.max_relay_depth = max_relay_depth
        self._relay_depth = 0

    def multimodal_winner_to_v7(self, winner_word, salience=0.5):
        """When mm coordinator picks a winner, feed it to v7's listen section."""
        if self._relay_depth >= self.max_relay_depth:
            return None
        if not winner_word or not isinstance(winner_word, str):
            return None
        self._relay_depth += 1
        try:
            vec, slot, was_new = self.v7.lookup_or_install(winner_word)
            if vec is not None:
                self.v7.sys_.hear_speaker(vec, "listen")
                return {"fed_to_v7": winner_word, "slot": slot, "was_new": was_new}
            return None
        finally:
            self._relay_depth -= 1

    def v7_emission_to_multimodal(self, response_tokens):
        """When v7 emits, fire the words in multimodal so senses experience them."""
        if self._relay_depth >= self.max_relay_depth:
            return None
        self._relay_depth += 1
        try:
            fired = []
            for tok in response_tokens:
                word = tok if isinstance(tok, str) else tok.get("token", "")
                if not word:
                    continue
                # Install in multimodal if not already there
                word_modes = getattr(self.mm, "sections", {}).get("word", {})
                if f"{word}" not in word_modes:
                    try:
                        self.mm.install_word(word)
                    except Exception:
                        continue
                try:
                    self.mm.hear_word_with_senses(word)
                    fired.append(word)
                except Exception:
                    continue
            return {"fired_in_mm": fired}
        finally:
            self._relay_depth -= 1

    def step(self):
        """One bridged tick: check mm coordinator winner, relay to v7."""
        result = {}
        winner = getattr(self.mm, "attention_focus", None)
        if winner is not None:
            result["mm_to_v7"] = self.multimodal_winner_to_v7(winner)
        return result
