"""
GL-EXP-RECALL-V3-DEEP-WC-20260608-01

Recall test for deep multimodal cognition.
Includes balanced training — each sensory word gets equal reinforcement.
"""
import sys
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from GL_MDL_MULTIMODAL_DEEP_WC_20260608_03 import DeepMultiModalCognition


GOODNIGHT_MOON = """in the great green room there was a telephone and a red balloon. 
and a picture of the cow jumping over the moon. 
and there were three little bears sitting on chairs.
goodnight room. goodnight moon. 
goodnight cow jumping over the moon. 
goodnight bears. goodnight chairs. 
goodnight kittens. 
goodnight stars. goodnight air. 
goodnight noises everywhere."""

SENSORY_WORDS = ["moon", "cow", "bears", "stars", "kittens", "room"]
OTHER_WORDS = ["the", "and", "a", "in", "was", "goodnight", "of",
               "picture", "over", "there", "were", "three", "little", "sitting", "on",
               "great", "green", "telephone", "red", "balloon",
               "chairs", "jumping", "air", "noises", "everywhere"]


def setup():
    cog = DeepMultiModalCognition()
    for w in SENSORY_WORDS + OTHER_WORDS:
        cog.install_word(w)
    return cog


def balanced_train(cog, n_rounds=8):
    """Balanced training: each sensory word gets equal reinforcement.
    Match-up phase: present word + sensory bundle together repeatedly."""
    for _ in range(n_rounds):
        for w in SENSORY_WORDS:
            cog.hear_word_with_senses(w)
            cog.run(8)


def read_with_senses(cog, text, n_passes=3):
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    for _ in range(n_passes):
        for sent in sentences:
            words = sent.lower().replace(",", "").split()
            for w in words:
                w_clean = "".join(c for c in w if c.isalnum())
                if w_clean in SENSORY_WORDS and w_clean in cog.sections["word"]:
                    cog.hear_word_with_senses(w_clean)
                elif w_clean in cog.sections["word"]:
                    cog.fire("word", w_clean)
                cog.run(3)
            cog.run(4)


def test_recall(cog):
    test_words = ["moon", "cow", "bears", "stars", "kittens", "room"]
    
    print("\n" + "=" * 70)
    print("  TEST 1: hear WORD only — does substrate recall its OWN senses?")
    print("=" * 70)
    
    first_correct = 0
    first_total = 0
    strong_correct = 0
    strong_total = 0
    for tw in test_words:
        cog.emissions.clear()
        cog.run(15)
        cog.emissions.clear()
        cog.fire("word", tw, salience=2.5)
        em = cog.run(25)
        
        print(f"\n  Heard: '{tw}'")
        for modality in ["visual", "audio", "touch", "taste", "smell"]:
            modal_em = [e for e in em if e["section"] == modality]
            if not modal_em:
                continue
            expected = f"{tw}__{modality}"
            first = min(modal_em, key=lambda e: e["tick"])
            strongest = max(modal_em, key=lambda e: e["activation"])
            f_mark = "✓" if first["label"] == expected else "✗"
            s_mark = "✓" if strongest["label"] == expected else "✗"
            first_total += 1
            strong_total += 1
            if first["label"] == expected:
                first_correct += 1
            if strongest["label"] == expected:
                strong_correct += 1
            print(f"    [{modality:6s}] FIRST: {f_mark} {first['label']:25s}  "
                  f"STRONGEST: {s_mark} {strongest['label']:25s} ({strongest['activation']:.2f})")
    
    print(f"\n  First-correct:     {first_correct}/{first_total} = {first_correct/max(first_total,1):.1%}")
    print(f"  Strongest-correct: {strong_correct}/{strong_total} = {strong_correct/max(strong_total,1):.1%}")
    
    print("\n" + "=" * 70)
    print("  TEST 2: visual only → word?")
    print("=" * 70)
    word_correct = 0
    for tw in test_words:
        cog.emissions.clear()
        cog.run(15)
        cog.emissions.clear()
        modal_label = f"{tw}__visual"
        if modal_label not in cog.sections["visual"]:
            continue
        cog.fire("visual", modal_label, salience=2.5)
        em = cog.run(25)
        word_em = [e for e in em if e["section"] == "word"]
        if not word_em:
            print(f"  visual({tw}) → (no word)")
            continue
        strongest = max(word_em, key=lambda e: e["activation"])
        is_correct = strongest["label"] == tw
        word_correct += int(is_correct)
        mark = "✓" if is_correct else "✗"
        unique = []
        for e in word_em:
            if e["label"] not in unique:
                unique.append(e["label"])
        print(f"  {mark} visual({tw}) → top: {unique[:5]}  "
              f"(strongest: '{strongest['label']}' act={strongest['activation']:.2f})")
    print(f"\n  Word-from-visual: {word_correct}/{len(test_words)}")
    
    print("\n" + "=" * 70)
    print("  TEST 3: visual + audio → word?")
    print("=" * 70)
    word_correct = 0
    for tw in test_words:
        cog.emissions.clear()
        cog.run(15)
        cog.emissions.clear()
        for modality in ["visual", "audio"]:
            modal_label = f"{tw}__{modality}"
            if modal_label in cog.sections[modality]:
                cog.fire(modality, modal_label, salience=2.5, set_focus=False)
        em = cog.run(25)
        word_em = [e for e in em if e["section"] == "word"]
        if not word_em:
            print(f"  v+a({tw}) → (no word)")
            continue
        strongest = max(word_em, key=lambda e: e["activation"])
        is_correct = strongest["label"] == tw
        word_correct += int(is_correct)
        mark = "✓" if is_correct else "✗"
        unique = []
        for e in word_em:
            if e["label"] not in unique:
                unique.append(e["label"])
        print(f"  {mark} v+a({tw}) → top: {unique[:5]}  "
              f"(strongest: '{strongest['label']}' act={strongest['activation']:.2f})")
    print(f"\n  Word-from-v+a: {word_correct}/{len(test_words)}")
    
    print("\n" + "=" * 70)
    print("  TEST 4: ALL available senses → word?")
    print("=" * 70)
    word_correct = 0
    for tw in test_words:
        cog.emissions.clear()
        cog.run(15)
        cog.emissions.clear()
        for modality in ["visual", "audio", "touch", "taste", "smell"]:
            modal_label = f"{tw}__{modality}"
            if modal_label in cog.sections[modality]:
                cog.fire(modality, modal_label, salience=2.5, set_focus=False)
        em = cog.run(25)
        word_em = [e for e in em if e["section"] == "word"]
        if not word_em:
            print(f"  all({tw}) → (no word)")
            continue
        strongest = max(word_em, key=lambda e: e["activation"])
        is_correct = strongest["label"] == tw
        word_correct += int(is_correct)
        mark = "✓" if is_correct else "✗"
        unique = []
        for e in word_em:
            if e["label"] not in unique:
                unique.append(e["label"])
        print(f"  {mark} all({tw}) → top: {unique[:5]}  "
              f"(strongest: '{strongest['label']}' act={strongest['activation']:.2f})")
    print(f"\n  Word-from-all-senses: {word_correct}/{len(test_words)}")
    
    return {
        "first_word_to_bundle": first_correct / max(first_total, 1),
        "strong_word_to_bundle": strong_correct / max(strong_total, 1),
        "word_from_v": word_correct,
    }


def main():
    cog = setup()
    print("Phase 1: Balanced training — each sensory word presented equally with its bundle...")
    balanced_train(cog, n_rounds=5)
    print(f"  atlas live bindings: {cog.atlas.live_count()}")
    
    print("\nPhase 2: Reading Goodnight Moon (with sensory bundles where applicable)...")
    read_with_senses(cog, GOODNIGHT_MOON, n_passes=3)
    print(f"  atlas live bindings: {cog.atlas.live_count()}")
    
    test_recall(cog)


if __name__ == "__main__":
    main()
