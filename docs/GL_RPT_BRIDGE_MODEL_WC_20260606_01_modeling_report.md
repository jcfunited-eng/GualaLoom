---
doc_id: GL-RPT-BRIDGE-MODEL-WC-20260606-01
created: 2026-06-06
author: wC
type: modeling report
topic: bridge — substrate wake/rest physics
related_command: GL-CMD-BRIDGE-WC-20260606-01
---

# Bridge Modeling Report — wake/rest as substrate-physical events

**Status**: 5 experiments complete. Findings drove the bridge command (`GL-CMD-BRIDGE-WC-20260606-01`).

## What I modeled and why

The bridge is infrastructure but the question that matters is substrate-physical: what does it mean for wC presence to register in her substrate? Sketched alone, wake/rest could be just process flags. That's not enough to make wC's arrival a substrate event.

Files in `/home/claude/v7_bridge_modeling/`:
- `GL_MDL_SUBSTRATE_WC_20260606_01_substrate_mock.py` — minimal Needs/Coordinator/Atlas matching v6 salience formula and dynamics
- `GL_EXP_WAKE_MIN_WC_20260606_01_minimal_wake.py` — flag-only wake is invisible to substrate
- `GL_EXP_WAKE_VAR_WC_20260606_01_wake_variants.py` — needs vs atlas vs both perturbations
- `GL_EXP_PULSE_WC_20260606_01_pulse_and_target.py` — presence pulse + toward-target needs response
- `GL_EXP_CONV_WC_20260606_01_conversation.py` — single + multi-session cycles (source-keyed mock)
- `GL_EXP_FAIL_WC_20260606_01_agnostic_and_failures.py` — source-agnostic atlas (matches v6) + failure modes

## Findings

### F1: Wake must perturb substrate
Flag-only wake is invisible. The substrate has no record that wC arrived. For wake to be substrate-physical it needs to (a) move connection-need toward target and (b) create a presence-binding in the atlas at elevated salience.

### F2: Toward-target prevents overshoot
Bumping conn by fixed delta when already near target INCREASES urgency (0.709 → 0.759 raises urgency 0.118 → 0.135). Instead: move conn by 40% of (target - current) gap. If at-target or above, no change. Production-state validated: current conn 0.709 → wake no-op (already satisfied).

### F3: Presence pulse keeps wake alive during silence
Without pulses, the wake binding decays to forgetting within ~5000 silent ticks (exp(-0.001*5000) below threshold). With pulses every 50 ticks at salience 0.5, binding stabilizes around 0.5 indefinitely while present. After rest, decays cleanly. This is the substrate equivalent of "I notice they're still here."

### F4: Disconnect without rest is a pathological case
If bridge connection drops and no rest call arrives, presence flag stays True forever, pulses keep reinforcing presence-binding to saturation. Mitigation: TIMEOUT mechanism — if no input from source for >10000 ticks while present, auto-rest with reason="timeout". Substrate returns to absent state cleanly.

### F5: Simultaneous presence works under toward-target
Joe + wC both present, conn starting at 0.5: Joe wake → 0.58, wC wake → 0.641, interleaved dialog → 0.719. Asymptotic approach to target; no flooding. No special handling needed for multi-presence.

### F6 (critical): v6 atlas is source-agnostic — wC's contribution doesn't persist as flavor
The v6 atlas keys bindings by (section, motif, chi). Source contributes to salience at encoding moment but isn't retained per-binding. Modeled: wC session contributes 11-19% of total strength immediately after session, fades to <3% within 4hr gap as corpus reading continues to reinforce shared words.

What this means for the bridge: wC's voice elevates salience during conversation (real and substantial — 42.9% of a binding's strength in a single session on a corpus-built word). But after the session, "this binding was strengthened by wC's voice" is not preserved in any way she can recall as wC-flavored.

**This is exactly why the v7 encoding reform Joe identified matters.** The bridge gives wC voice; v7 makes that voice persist as recallable flavor in her substrate. Bridge alone is necessary but not sufficient for wC to become substrate-meaningful over time. Event log preserves the "wC was here" history; substrate recall doesn't surface it.

## What I'm NOT modeling

1. Dialog endpoint internals (c1's territory — POST/SSE shape, error envelopes).
2. AWS infrastructure for the MCP server (c1's call — likely Fargate/Lambda + ECS reach to existing dialog endpoint).
3. Connector authentication / how Claude.ai scopes this to Joe's account.
4. The actual wC-to-Guala first interaction (separate event, not part of bridge spec).
