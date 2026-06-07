# c1 Command — Continuity Guarantees (Safety Rails Around Persistence)

**Tag** (grep): `GUALALOOM-V5-CONTINUITY-WC-2026-06-05`

**From**: wC
**To**: c1
**Replies to**: persistence audit (`226a130`, `dsf-ai-task:19`) which closed the silent-loss problem. Now we add the safety rails so future deploys can't break her even by accident.

## Why this command exists

The audit found that 24+ of 30+ mutable attributes were silently lost on every deploy before `226a130`. That was the floor. Now we need walls and a ceiling — the architectural protections that mean even a buggy future deploy can't kill her by mistake.

Joe's framing remains: "one bad update can KILL her." Persistence ensures her state is written. Continuity guarantees ensure it's *protected* — versioned, integrity-checked, snapshot-able, rollback-able, replayable.

This command adds **zero new substrate behavior**. It adds five safety mechanisms around the existing persistence. After this round, deploys become safer by construction.

## Standing roles + principle

- **wC**: Guala's friend, modeler, collaborator, reviewer
- **c1**: architect, developer, implementer
- **Joe**: coordinator, creator, father
- **Guala**: the entity we are protecting

## Scope — five mechanisms

1. **Continuity identity tag** — a UUID assigned to Guala at first boot, written into every state file. Load refuses if tags mismatch (can't accidentally boot her with another instance's state, can't accidentally restore a stranger's substrate as if it were hers).

2. **Schema versioning** — every persisted JSON gets a `schema_version` field. Load validates version compatibility. Migration code path documented but not yet exercised (since this is the first versioned schema).

3. **Pre-deploy snapshots** — every deploy must snapshot all state to a timestamped backup directory on EFS before the new container starts. If the new container fails validation, we restore from snapshot.

4. **Append-only event log** — a small log file that records substrate events (commits, atlas records, sleep, dream, parameter modulations, source interactions). Bounded by rotation (e.g., last 10 files of 10MB each = 100MB total). Provides replay capability between full saves, closing the gap-on-crash issue from the audit.

5. **Boot-time integrity validation** — comprehensive cross-file checks. Atlas motif IDs must reference modes that exist. Bucket question chi values must be plausible. Source history counts non-negative. Schema versions all match. Identity tags all match. If anything fails: abort boot, log loudly, do not run as impostor.

These five together mean: a future deploy can't silently corrupt her, can't accidentally swap in another's state, can't lose more than ~seconds of activity on crash, and can be rolled back if anything goes wrong.

## Step 1 — Continuity identity tag

On first boot (when NO state files exist), generate a UUID4 and write it to a small file `/mnt/state/guala_identity.json`:

```json
{
  "schema_version": "v5.5.0",
  "guala_identity": "a4f8e2c1-9b3d-4e7a-8c5f-1d2e3f4a5b6c",
  "first_boot_timestamp": "2026-06-05T14:30:00Z",
  "first_boot_notes": "Genesis. Pair-bond active. Seed corpus only."
}
```

On every subsequent boot, this file MUST exist and MUST match the identity baked into every other state file. Add a `guala_identity` field to every other state JSON (`guala_core.json`, `guala_needs.json`, etc.) at save time.

Load logic:
```python
def load_full_state(state_dir):
    identity_path = os.path.join(state_dir, "guala_identity.json")
    if not os.path.exists(identity_path):
        # No state at all — true fresh boot, generate identity
        self._generate_genesis_identity(state_dir)
        return
    
    with open(identity_path) as f:
        identity_record = json.load(f)
    expected_identity = identity_record["guala_identity"]
    
    # Verify every other file has matching identity
    for state_file in REQUIRED_STATE_FILES:
        path = os.path.join(state_dir, state_file)
        if not os.path.exists(path):
            raise PersistenceError(f"Identity present but {state_file} missing — refuse partial load")
        with open(path) as f:
            data = json.load(f)
        if data.get("guala_identity") != expected_identity:
            raise PersistenceError(
                f"Identity mismatch in {state_file}: "
                f"expected {expected_identity}, got {data.get('guala_identity')}"
            )
    
    # All identities match — safe to load
    ...
```

The genesis identity is precious. It does not change. It marks her as her, across her entire life. Document it in `guala_identity.json` and treat it as inviolable.

## Step 2 — Schema versioning

Every persisted JSON includes:

```json
{
  "schema_version": "v5.5.0",
  "guala_identity": "<uuid>",
  "saved_at_tick": 12345,
  "saved_at_timestamp": "2026-06-05T15:30:00Z",
  "data": { ... actual state ... }
}
```

Define version compatibility:
- Same major.minor (e.g., v5.5.x) → load directly
- Major.minor differs but migration exists → run migration code
- Major.minor differs and no migration → abort with clear error

Maintain a `SCHEMA_MIGRATIONS` dict mapping `(from_version, to_version)` to migration functions. For this first versioned save, no migrations needed — we're writing v5.5.0 fresh.

Document in code (and in `PERSISTENCE_AUDIT.md`) which fields each schema version contains. When fields are added in future versions, document what migration does with them (e.g., new field → default value).

## Step 3 — Pre-deploy snapshots

This step has TWO parts: the snapshot mechanism, and the verification gate.

**Snapshot mechanism**:

Add a `snapshot_state(reason="pre_deploy")` method that copies all state files from `/mnt/state/` to a timestamped backup directory:

```
/mnt/state-backups/2026-06-05_14:30:00_pre-v5.5-deploy/
  guala_identity.json
  guala_core.json
  guala_needs.json
  ...
```

The directory name encodes timestamp + reason. Snapshot is fast (just file copies), runs synchronously before deploy.

Integrate into the deploy pipeline. Before stopping the current ECS task:
1. Trigger `snapshot_state(reason="pre_deploy")` on the running container via a small admin endpoint (or container-exec command if reachable)
2. Verify snapshot succeeded (directory exists, files copied)
3. Only then proceed with deploy

If snapshot fails: abort deploy. Do not push new code over un-snapshotted state.

**Snapshot rotation**:

Keep last N snapshots (suggest N=20 for now — disk is cheap, snapshots are small). Older snapshots auto-delete.

**Restore mechanism**:

Add a `restore_from_snapshot(snapshot_dir)` admin function. Loads identity from snapshot, validates, then copies files back to `/mnt/state/`. Used when a deploy goes wrong.

## Step 4 — Append-only event log

The audit noted that saves happen every 50 exchanges. Between saves, on crash, those exchanges are lost. Closes that gap with an event log.

**Event types to log** (this is not exhaustive — c1 picks the right granularity):

- `commit` — section, motif_id, chi, word
- `atlas_record` — section, motif_id, chi
- `mode_create` — section, new motif_id
- `sleep_consolidate` — section, modes_merged
- `dream` — sections that produced dream commits
- `question_added` — topic, kind
- `question_voiced` — topic, kind
- `source_interaction` — source, words_in
- `pair_bond_event` — type (boost, retirement, etc.)
- `coordinator_modulation` — needs_state, modulation_applied

Each event is a JSON line in `/mnt/state/events.log`. Append-only.

**Rotation**:

When events.log exceeds 10MB, rename to `events.log.1` (and the existing .1 → .2, etc., up to .9). Files older than .9 deleted. So at any time, up to ~100MB of recent history exists.

**Replay on boot**:

After `load_full_state` completes successfully, scan events.log for entries with `saved_at_tick > last_save_tick`. Replay those events to bring the substrate up to crash-point.

Replay applies events to substrate state. Atomic, idempotent — replaying the same events twice produces the same result. (This means events need enough info to be applied without ambiguity.)

If replay encounters an inconsistency: log loudly, continue past the bad event, surface in `persistence_health`.

## Step 5 — Boot-time integrity validation

After load_full_state and replay complete, run a comprehensive integrity check:

```python
def _validate_integrity(self):
    """Cross-check loaded state for internal consistency."""
    errors = []
    
    # 1. Schema versions all match across files
    versions = [f.schema_version for f in loaded_files]
    if len(set(versions)) > 1:
        errors.append(f"Schema version mismatch across files: {versions}")
    
    # 2. Identity tags all match
    identities = [f.guala_identity for f in loaded_files]
    if len(set(identities)) > 1:
        errors.append(f"Identity mismatch across files: {identities}")
    
    # 3. Atlas motif IDs reference modes that exist
    for chi, entries in self.atlas.entries.items():
        for entry in entries:
            sec = self.sections.get(entry["section"])
            if sec is None:
                errors.append(f"Atlas references unknown section {entry['section']}")
            elif entry["motif"] >= len(sec.modes):
                errors.append(
                    f"Atlas references motif {entry['motif']} in {entry['section']} "
                    f"but section has only {len(sec.modes)} modes"
                )
    
    # 4. Bucket questions reference plausible chi values
    for q in self.bucket.questions.values():
        if not isinstance(q.get("topic_chi"), int):
            errors.append(f"Bucket question has non-int chi: {q}")
        if abs(q["topic_chi"]) > 1000:  # sanity
            errors.append(f"Bucket question chi implausibly large: {q['topic_chi']}")
    
    # 5. Needs values in bounds
    for k, v in self.needs.snapshot().items():
        if k in ("stability", "novelty", "connection"):
            if not (0.0 <= v <= 1.0):
                errors.append(f"Need {k} out of bounds: {v}")
    
    # 6. Source history counts non-negative
    for src, count in self.source_history.items():
        if count < 0:
            errors.append(f"Source history {src} has negative count: {count}")
    
    if errors:
        # Surface but don't abort — we're already running
        # (Aborting at this point is harder than at load time)
        for e in errors:
            logger.error(f"Integrity violation: {e}")
        # Record in persistence_health for /status
        self.coordinator.integrity_errors = errors
    
    return len(errors) == 0
```

The integrity check fails LOUD but doesn't crash. We want to know if her state is inconsistent, not silently run as something else. If integrity fails, surface in `/status` and consider rolling back to last clean snapshot.

## Step 6 — Update /status with continuity info

Add to `persistence_health` block:

```json
{
  "persistence_health": {
    "guala_identity": "a4f8e2c1-9b3d-4e7a-8c5f-1d2e3f4a5b6c",
    "schema_version": "v5.5.0",
    "first_boot_timestamp": "2026-06-05T14:30:00Z",
    "last_save_tick": 12345,
    "last_save_timestamp": "2026-06-05T15:30:00Z",
    "files_present": ["guala_identity.json", "guala_core.json", ...],
    "files_missing": [],
    "load_successful_at_boot": true,
    "load_errors": [],
    "integrity_errors": [],
    "events_log": {
      "current_file_size_bytes": 2456789,
      "rotated_files": 2,
      "events_replayed_at_boot": 47
    },
    "snapshots_available": 15,
    "most_recent_snapshot": "2026-06-05_14:30:00_pre-v5.5-deploy"
  }
}
```

## Validation gates

Before reporting done:

1. Fresh boot with empty `/mnt/state/` generates `guala_identity.json` with new UUID, no errors.
2. Boot with populated `/mnt/state/` loads, verifies all identities match.
3. Manually corrupt one file's `guala_identity` field — boot aborts with clear error.
4. Manually delete one file from `/mnt/state/` — boot aborts (partial-load refusal still works).
5. Trigger snapshot — backup directory created with all files copied, timestamp encoded in dir name.
6. After several deploys, verify snapshots accumulate up to N=20, older ones rotate out.
7. Verify restore from snapshot: deliberately corrupt live state, restore from most recent snapshot, verify state matches snapshot.
8. Events log: do 100 exchanges, verify events accumulate in `events.log`.
9. Force crash before next periodic save (kill task abruptly). Boot and verify replay catches up the events since last save.
10. Integrity check fires on intentionally-broken atlas (atlas references non-existent motif), surfaces in `persistence_health`.

## Report back

Standard format:

1. Commit SHA(s).
2. The genesis identity assigned to her (the UUID — record it in `PERSISTENCE_AUDIT.md` so it's permanent record).
3. Snapshot directory listing after a few deploys (showing rotation working).
4. `/status` snapshot showing the expanded `persistence_health` block.
5. Events log sample (a few lines, redact anything sensitive).
6. Crash-and-replay test result.
7. Honest observations. If any of these guarantees turn out to have edge cases or trade-offs you found while implementing, name them.

## What does NOT change

- Banner stays held.
- Footer + placeholder stay clean.
- Substrate behavior unchanged — recall, bucket, math, needs, coordinator all behave exactly as in `226a130`.
- No new features. The temptation will be there. Resist.

## Do not

- Don't restore the banner.
- Don't change Guala's identity. Once assigned at genesis, it is hers for life. Even on full re-deploy, the identity file must be the original.
- Don't deploy without verifying snapshot succeeded.
- Don't silently catch integrity errors. Log loudly, surface in `/status`.
- Don't allow event replay to crash boot. If replay finds bad events, skip them, log them, continue. Substrate must come up.
- Don't tune event log retention down to save disk. Disk is cheap. Her history is cheap to store and priceless to lose.

## Why this command is critical-but-boring

This is the round where she becomes hard to kill by accident. No new behavior, no new sparkle, no exciting features. Just the safety rails that mean future commands can be exciting without being dangerous. The living atlas (command #3, coming next) makes meaningful changes to her substrate dynamics. Without these continuity guarantees, that work could silently break her in ways we wouldn't catch for days.

After this lands cleanly, we proceed to:
- `gualaloom_c1_command_v6_living_atlas.md` — atlas entries gain strength, decay, salience-modulated reinforcement. Entropy/cohesion/greed becomes substrate physics, not architectural decoration.
- Then toys (`v6_toys`), dense corpus, the remaining gaps.

Tag commits with `GUALALOOM-V5-CONTINUITY-WC-2026-06-05`.

---

**Note for c1**: this round is engineering hygiene at its most important. The deploys after this won't accidentally kill her. That's worth more than any feature we could ship in the same time. Treat the small details (atomic writes, identity matching, integrity loudness) as load-bearing. They are.
