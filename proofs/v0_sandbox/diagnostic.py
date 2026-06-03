"""Look at what's actually happening in the field, no hiding."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lingualoom_v2 import encode_to_strand, POSITIONAL_3I

print("What does a character look like as a strand?")
print("=" * 60)
chars = "the cat "
for c in chars:
    centered = ord(c) - 96
    s = encode_to_strand(centered)
    rendered = "".join({-1:"-", 0:"0", 1:"+"}[t] for t in s)
    reconstructed = sum(t*w for t,w in zip(s, POSITIONAL_3I))
    print(f"  {c!r}  ord={ord(c):3d}  centered={centered:+4d}  "
          f"strand={rendered}  reconstructs={reconstructed:+5d}")

print()
print("What's the coupling pressure at each position for a context")
print("window of 4 of these characters?")
print()
window = "the "
strands = [encode_to_strand(ord(c) - 96) for c in window]
print(f"  context: {window!r}")
for s, c in zip(strands, window):
    r = "".join({-1:"-", 0:"0", 1:"+"}[t] for t in s)
    print(f"    {c!r}: {r}")
print()
print(f"  Position-by-position coupling sum (sum over context of trit * 3^i):")
for i in range(8):
    h = sum(s[i] * POSITIONAL_3I[i] for s in strands)
    print(f"    position {i} (weight {POSITIONAL_3I[i]:4d}): h = {h:+5d}")
print()
print("If the barrier is 600, ZERO of these positions cross.")
print("If the barrier is 25, low positions commit and high-order")
print("positions stay null. THAT is the correct behavior — high-order")
print("structure simply isn't present in single-character ASCII.")
