"""Fresh-process proof for one raw native CURRENT organism."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import dsf_ai_service.cold_restore_probe as probe


IDENTITY = "1cc4e70a-f2a0-44c5-a111-f4a5bc915cc1"
STATE = b"GLORUN01-native-current-test"
STATE_SHA = hashlib.sha256(STATE).hexdigest()
GIT_SHA = "a" * 40
IMAGE = "sha256:" + "b" * 64


@dataclass
class _Observation:
    identity: str = IDENTITY
    organism_tick: int = 23_723_846
    state_bytes: int = len(STATE)
    state_sha256: str = STATE_SHA
    python_callback_count: int = 0
    joint_field_count: int = 2
    complete_neuron_count: int = 217
    developmental_resting_neuron_count: int = 196_335


class _Organism:
    def __init__(self) -> None:
        self.readiness_calls = 0
        self.save_calls = 0

    def readiness(self) -> _Observation:
        self.readiness_calls += 1
        return _Observation()

    def save(self) -> bytes:
        self.save_calls += 1
        return STATE


@dataclass
class _Pointer:
    identity: str = IDENTITY
    organism_tick: int = 23_723_846
    state_sha256: str = STATE_SHA


@dataclass
class _Restored:
    organism: _Organism = field(default_factory=_Organism)
    pointer: _Pointer = field(default_factory=_Pointer)


@dataclass
class _Admission:
    max_envelope_bytes: int = 1_000
    max_fabric_bytes: int = 900
    max_logical_peak_bytes: int = 3_000


def _arguments(**changes: object) -> SimpleNamespace:
    values = {
        "native_store_root": "/read-only/native-organism",
        "expected_identity": IDENTITY,
        "expected_tick": 23_723_846,
        "expected_state_sha256": STATE_SHA,
        "candidate_git_sha": GIT_SHA,
        "candidate_image_digest": IMAGE,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def test_probe_cannot_import_the_retired_python_organism() -> None:
    source = Path(probe.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "guala_physical_runtime",
        "Guala(",
        "load_full_state",
        "generation_store",
        "owner",
        "exact_field_executor",
    ):
        assert forbidden not in source
    assert "restore_current_native_organism" in source
    assert "raw_glorun_current_only" in source


def test_c024_observer_reads_one_disposable_exact_current(
    monkeypatch,
) -> None:
    from dsf_ai_service import native_production_app as production

    staged = object()
    restored = SimpleNamespace(organism=object())
    admission = _Admission()
    snapshot_roots: list[Path] = []

    def stage(root, organism, *, max_envelope_bytes):
        snapshot_roots.append(Path(root))
        assert organism is restored.organism
        assert max_envelope_bytes == admission.max_envelope_bytes
        return staged

    def publish(value, **kwargs):
        assert value is staged
        assert kwargs["expected_predecessor_sha256"] is None

    def startup() -> None:
        assert production.STATE_ROOT == snapshot_roots[0]

    observed = {
        "generation_state": {"state_sha256": STATE_SHA},
        "cognitive_capital": {
            "capabilities": list(production.COGNITIVE_CAPITAL_CAPABILITIES),
            "dimensions": list(production.COGNITIVE_CAPITAL_DIMENSIONS),
            "credits": [],
            "scalar_score_authority": False,
            "cognition_authority": False,
        },
        "formations": {"mosaic_count": 0},
    }
    monkeypatch.setattr(probe, "stage_active_native_organism", stage)
    monkeypatch.setattr(probe, "publish_staged_native_organism", publish)
    monkeypatch.setattr(production, "_startup", startup)
    monkeypatch.setattr(production, "_build_public_observation", lambda: observed)

    proof = probe._observe_c024_cognitive_capital(
        restored,
        admission,
        STATE_SHA,
    )

    assert proof["c024_cognitive_capital_state_sha256"] == STATE_SHA
    assert len(snapshot_roots) == 1
    assert not snapshot_roots[0].exists()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("expected_state_sha256", "not-a-sha", "state SHA-256"),
        ("candidate_git_sha", "not-a-commit", "commit"),
        ("candidate_image_digest", "latest", "image digest"),
    ),
)
def test_probe_rejects_noncanonical_artifact_coordinates_before_restore(
    monkeypatch,
    field: str,
    value: str,
    message: str,
) -> None:
    monkeypatch.setattr(probe, "_arguments", lambda: _arguments(**{field: value}))
    monkeypatch.setattr(
        probe,
        "derive_native_resident_resource_admission",
        lambda _root: (_ for _ in ()).throw(AssertionError("must not derive")),
    )
    with pytest.raises(ValueError, match=message):
        probe.main()


def test_contact_route_match_is_direction_independent_and_requires_transfer() -> None:
    contact = frozenset({("01" * 16, "02" * 16, 3)})
    zero_route = ("02" * 16, 4, 9, "01" * 16, 5, 7, 3, 0)
    used_route = ("02" * 16, 4, 9, "01" * 16, 5, 7, 3, -11)

    assert probe._first_nonzero_route_on_contacts((zero_route,), contact) is None
    assert probe._first_nonzero_route_on_contacts(
        (zero_route, used_route), contact
    ) == used_route


def test_probe_reads_saves_and_reobserves_without_advancing_state(
    monkeypatch,
    capsys,
) -> None:
    restored = _Restored()
    thermal_proof = {
        "a013_thermal_body_rehearsed": True,
        "a013_thermal_body_receptor_count": 2,
    }
    monkeypatch.setattr(probe, "_arguments", _arguments)
    monkeypatch.setattr(
        probe,
        "derive_native_resident_resource_admission",
        lambda _root: _Admission(),
    )
    monkeypatch.setattr(
        probe,
        "restore_current_native_organism",
        lambda *_args, **_kwargs: restored,
    )
    monkeypatch.setattr(
        probe,
        "_rehearse_a013_thermal_body",
        lambda *_args, **_kwargs: thermal_proof,
    )

    assert probe.main() == 0
    assert restored.organism.readiness_calls == 2
    assert restored.organism.save_calls == 0
    proof = json.loads(capsys.readouterr().out)
    receipt = proof.pop("receipt_sha256")
    assert proof == {
        "baseline_observed_state_sha256": STATE_SHA,
        "baseline_observed_tick": 23_723_846,
        "candidate_git_sha": GIT_SHA,
        "candidate_image_digest": IMAGE,
        "cold_restore_exact": True,
        "complete_neuron_count": 217,
        "current_format_migration_rehearsed": False,
        "developmental_resting_neuron_count": 196_335,
        "migration_predecessor_state_sha256": None,
        "mode": "cold-restore",
        "motor_action_rehearsed": False,
        "python_callback_count": 0,
        "python_cognition_workers_started": 0,
        "raw_glorun_current_only": True,
        "resident_state_bytes": len(STATE),
        "resident_state_sha256": STATE_SHA,
        "schema": probe.PROOF_SCHEMA,
        "source_identity": IDENTITY,
        "source_advanced_after_baseline": False,
        "source_mount_read_only": True,
        "tick": 23_723_846,
        **thermal_proof,
    }
    assert receipt == hashlib.sha256(probe._canonical(proof)).hexdigest()


def test_probe_rejects_state_or_callback_change(monkeypatch) -> None:
    class _ChangedOrganism(_Organism):
        def readiness(self) -> _Observation:
            observed = super().readiness()
            if self.readiness_calls == 2:
                observed.state_sha256 = "f" * 64
                observed.python_callback_count = 1
            return observed

    restored = _Restored(organism=_ChangedOrganism())
    monkeypatch.setattr(probe, "_arguments", _arguments)
    monkeypatch.setattr(
        probe,
        "derive_native_resident_resource_admission",
        lambda _root: _Admission(),
    )
    monkeypatch.setattr(
        probe,
        "restore_current_native_organism",
        lambda *_args, **_kwargs: restored,
    )
    with pytest.raises(RuntimeError, match="cold restore changed"):
        probe.main()


def test_articulation_rehearsal_reads_tick_through_native_observation(
    monkeypatch,
) -> None:
    from dsf_ai_service import native_production_app

    class _ArticulatingOrganism:
        def readiness(self) -> SimpleNamespace:
            return SimpleNamespace(organism_tick=37)

        def begin_unsealed_intake_direct(
            self, episodes, admissions
        ) -> SimpleNamespace:
            assert len(episodes) == 1
            assert len(admissions) == 1
            return SimpleNamespace(token=b"u" * 32)

        def finalize_unsealed_intake_direct(self, token) -> SimpleNamespace:
            assert token == b"u" * 32
            return SimpleNamespace(
                token=b"f" * 32,
                physically_transitioned_neuron_count=2,
                complete_neuron_fractal_count=1,
                externally_perturbed_body_receptor_count=1,
            )

        def acknowledge_direct_commit(self, token: bytes) -> None:
            assert token == b"f" * 32

    monkeypatch.setattr(
        probe,
        "exact_articulatory_unit_trajectory",
        lambda **_kwargs: (
            16_000,
            (1, -1),
            b"\x01\x00\x00\x00" * 4,
            3,
            80,
            265,
            0,
            1,
            0,
            2,
        ),
    )
    observed_prefixes: list[str] = []

    def episodes(**kwargs):
        observed_prefixes.append(kwargs["assembly_prefix"])
        return [(object(), [])]

    monkeypatch.setattr(native_production_app, "_mono_pcm_hop_episodes", episodes)
    prepared = SimpleNamespace(
        articulatory_unit_recruitments=(
            ("13" * 16, 0, 1, (("12" * 16, 12, "13" * 16, 13, 0, 1),)),
        )
    )

    proof = probe._rehearse_articulation_and_self_hearing(
        _ArticulatingOrganism(), prepared
    )

    assert observed_prefixes == ["c020-cold-self-hearing-37"]
    assert proof is not None
    assert proof["self_hearing_transitioned_neuron_count"] == 2
    assert proof["self_hearing_fractal_count"] == 1


def test_physical_rest_reopens_work_and_cold_replays_exactly(monkeypatch) -> None:
    class _RestWakeOrganism:
        def __init__(self) -> None:
            self.phase = 0

        def readiness(self) -> SimpleNamespace:
            states = (
                (40, (7, 1), "10" * 32),
                (41, (3, 1), "20" * 32),
                (42, (5, 1), "30" * 32),
            )
            tick, dissipated, state_sha = states[self.phase]
            return SimpleNamespace(
                organism_tick=tick,
                state_sha256=state_sha,
                python_callback_count=0,
                dissipated_energy_zeptojoules=dissipated,
                dissipation_capacity_energy_zeptojoules=(10, 1),
            )

        def prepare_admitted(
            self, episode: object, admissions: object
        ) -> SimpleNamespace:
            assert self.phase == 0
            assert episode == "quiet"
            assert admissions == "admissions"
            return SimpleNamespace(
                token="rest",
                rest_recovered_neuron_count=2,
                motor_unit_recruitments=(),
                articulatory_unit_recruitments=(),
                physically_transitioned_neuron_count=2,
                dsf_delivery_count=1,
            )

        def prepare_vestibular_tick(
            self, heading: int, signed_step: int
        ) -> SimpleNamespace:
            assert heading == 0
            assert self.phase == 1 and signed_step == 1
            return SimpleNamespace(
                token="wake",
                rest_recovered_neuron_count=0,
                motor_unit_recruitments=(),
                articulatory_unit_recruitments=(),
                physically_transitioned_neuron_count=4,
                dsf_delivery_count=2,
            )

        def commit(self, token: str) -> SimpleNamespace:
            assert token == ("rest" if self.phase == 0 else "wake")
            self.phase += 1
            return self.readiness()

        def save(self) -> bytes:
            return b"rest-wake-successor"

    monkeypatch.setattr(
        probe,
        "restore_native_resident_organism",
        lambda **_kwargs: _RestWakeOrganism(),
    )
    from dsf_ai_service import native_production_app as production

    monkeypatch.setattr(
        production,
        "_mono_pcm_hop_episodes",
        lambda **_kwargs: [("quiet", "admissions")],
    )

    proof = probe._rehearse_native_physical_rest_and_wake(b"body", {})

    assert proof["native_physical_rest_wake_rehearsed"] is True
    assert proof["native_physical_rest_wake_cold_replay_exact"] is True
    assert proof["native_rest_interval_ordinal"] == 1
    assert proof["native_rest_recovered_neuron_count"] == 2
    assert proof["native_rest_dissipated_energy_before_zeptojoules"] == (7, 1)
    assert proof["native_rest_dissipated_energy_after_zeptojoules"] == (3, 1)
    assert (
        proof["native_rest_reachable_dissipation_headroom_before_zeptojoules"]
        == (3, 1)
    )
    assert (
        proof["native_rest_reachable_dissipation_headroom_after_zeptojoules"]
        == (7, 1)
    )
    assert proof["native_wake_physically_transitioned_neuron_count"] == 4


def test_internal_consolidation_changes_one_formation_and_cold_replays(monkeypatch) -> None:
    members = ("01" * 16, "02" * 16, "03" * 16)
    original = ((members[0], members[1], 0), (members[1], members[2], 0))

    class _ConsolidatingOrganism:
        def __init__(self, internal: bool) -> None:
            self.internal = internal

        def readiness(self) -> SimpleNamespace:
            return SimpleNamespace(
                organism_tick=51 if self.internal else 50,
                state_sha256=("2" if self.internal else "1") * 64,
                state_bytes=101 if self.internal else 100,
                python_callback_count=0,
            )

        def observe_retained_formation_structures(self):
            receipt = ("b" if self.internal else "a") * 64
            recurrence = original if self.internal else (original[0],)
            return ((receipt, members, original, recurrence, 0),)

        def observe_retained_formation_recurrence_evidence(self):
            receipt = ("b" if self.internal else "a") * 64
            cue = members if self.internal else members[:1]
            origin = "internally_simulated" if self.internal else "externally_observed"
            return ((receipt, cue, origin),)

        def prepare_admitted(self, episode: object, admissions: object):
            assert not self.internal and episode == "quiet" and admissions == "admissions"
            return SimpleNamespace(
                token="internal",
                externally_perturbed_body_receptor_count=0,
                metabolically_perturbed_body_receptor_count=2,
                endogenous_partial_cue_reassembly_count=1,
                rest_recovered_neuron_count=4,
                motor_unit_recruitments=(("04" * 16, 1, 1, (), ()),),
                articulatory_unit_recruitments=(("05" * 16, 1, 1, ()),),
            )

        def commit(self, token: str):
            assert token == "internal"
            self.internal = True
            return self.readiness()

        def save(self) -> bytes:
            return b"internal-successor" if self.internal else b"body"

    monkeypatch.setattr(
        probe,
        "restore_native_resident_organism",
        lambda *, current_envelope, **_kwargs: _ConsolidatingOrganism(
            current_envelope == b"internal-successor"
        ),
    )
    from dsf_ai_service import native_production_app as production

    monkeypatch.setattr(
        production,
        "_mono_pcm_hop_episodes",
        lambda **_kwargs: [("quiet", "admissions")],
    )

    proof = probe._rehearse_native_internal_consolidation(b"body", {})

    assert proof["native_internal_consolidation_rehearsed"] is True
    assert proof["native_internal_consolidation_cold_restore_exact"] is True
    assert proof["native_internal_consolidation_cold_replay_exact"] is True
    assert proof["native_internal_consolidation_interval_ordinal"] == 1
    assert proof["native_internal_consolidation_origin"] == "internally_simulated"
    assert proof["native_internal_consolidation_member_count"] == 3
    assert proof["native_internal_consolidation_cue_count"] == 3
    assert proof["native_internal_consolidation_formation_count"] == 1
    assert proof["native_internal_consolidation_recovered_neuron_count"] == 4
    assert proof["native_internal_consolidation_motor_recruitment_count"] == 1
    assert proof["native_internal_consolidation_articulatory_recruitment_count"] == 1


def test_articulation_translation_preserves_only_exact_native_cancellation(
    monkeypatch,
) -> None:
    recruitment = (("13" * 16, 1, 5, ()),)

    def cancelled(**_kwargs):
        raise ValueError("CancelledRecruitment")

    monkeypatch.setattr(probe, "exact_articulatory_unit_trajectory", cancelled)
    assert probe._exact_articulatory_trajectory_or_none(recruitment) is None

    def failed(**_kwargs):
        raise ValueError("ArithmeticWidth")

    monkeypatch.setattr(probe, "exact_articulatory_unit_trajectory", failed)
    with pytest.raises(ValueError, match="ArithmeticWidth"):
        probe._exact_articulatory_trajectory_or_none(recruitment)


def test_native_articulation_source_skips_cancelled_recruitment_and_replays_exactly(
    monkeypatch,
) -> None:
    trajectory_calls: list[tuple[int, tuple[int, ...]]] = []
    cancelled = (
        "13" * 16,
        1,
        5,
        (("12" * 16, 12, "13" * 16, 13, 0, 5),),
    )
    recruitment = (
        "13" * 16,
        0,
        5,
        (("12" * 16, 12, "13" * 16, 13, 0, 5),),
    )

    class _SourceOrganism:
        def __init__(self) -> None:
            self.tick = 40
            self.prepared_intervals = 0
            self.pending_tick_advance = 0

        def readiness(self) -> SimpleNamespace:
            return SimpleNamespace(
                identity=IDENTITY,
                organism_tick=self.tick,
                python_callback_count=0,
                state_bytes=1_000 + self.tick,
                state_sha256=f"{self.tick:064x}",
            )

        def prepare_vestibular_tick(
            self, heading: int, signed_step: int
        ) -> SimpleNamespace:
            self.prepared_intervals += 1
            self.pending_tick_advance = 1
            assert heading == 0
            assert signed_step == 0
            return SimpleNamespace(
                token=f"source-{self.prepared_intervals}",
                articulatory_unit_recruitments=(
                    (cancelled,)
                    if self.prepared_intervals == 2
                    else ((recruitment,) if self.prepared_intervals == 3 else ())
                ),
                dsf_delivery_count=2,
                physically_transitioned_neuron_count=10 * self.prepared_intervals,
            )

        def prepare_vestibular_trajectory(
            self, heading: int, steps: tuple[int, ...]
        ) -> SimpleNamespace:
            assert heading == 0
            assert steps == (0, 0, 0)
            trajectory_calls.append((heading, steps))
            self.prepared_intervals = 3
            self.pending_tick_advance = len(steps)
            return SimpleNamespace(
                token="source-3",
                articulatory_unit_recruitments=(recruitment,),
                dsf_delivery_count=6,
                physically_transitioned_neuron_count=60,
            )

        def commit(self, token: str) -> SimpleNamespace:
            assert token == f"source-{self.prepared_intervals}"
            self.tick += self.pending_tick_advance
            self.pending_tick_advance = 0
            return self.readiness()

        def save(self) -> bytes:
            return f"successor-{self.tick}".encode("ascii")

    monkeypatch.setattr(
        probe,
        "exact_native_yaw_trajectory",
        lambda **_kwargs: (90_000, (0,) * 250),
    )
    monkeypatch.setattr(
        probe,
        "restore_native_resident_organism",
        lambda **_kwargs: _SourceOrganism(),
    )
    monkeypatch.setattr(
        probe,
        "_exact_articulatory_trajectory_or_none",
        lambda recruitments: None if recruitments == (cancelled,) else ("trajectory",),
    )

    def articulate(organism, prepared, trajectory):
        assert tuple(prepared.articulatory_unit_recruitments) == (recruitment,)
        assert trajectory == ("trajectory",)
        organism.tick += 4
        return {
            "layer_13_recruitment_count": 1,
            "self_hearing_hop_count": 4,
        }

    monkeypatch.setattr(
        probe,
        "_rehearse_articulation_and_self_hearing",
        articulate,
    )

    proof = probe._rehearse_native_articulation_source(b"body", {})

    assert proof["native_articulation_cold_replay_exact"] is True
    assert proof["native_articulation_source_available_interval_count"] == 250
    assert proof["native_articulation_source_interval_count"] == 3
    assert proof["native_articulation_source_dsf_delivery_count"] == 6
    assert proof["native_articulation_source_layer_13_recruitment_count"] == 1
    assert trajectory_calls == [(0, (0, 0, 0))]
    assert (
        proof["native_articulation_source_physically_transitioned_neuron_count"]
        == 60
    )


def test_episodic_relation_resolves_only_against_retained_successor() -> None:
    recalled = ("01" * 16, "02" * 16, "03" * 16)
    related = ("04" * 16, "05" * 16, "06" * 16)
    recalled_receipt = "1" * 64
    related_receipt = "2" * 64
    bond = (recalled[0], related[0], 0)

    class _EpisodicOrganism:
        committed = False

        def commit(self, token: str) -> None:
            assert token == "prepared-token"
            self.committed = True

        def observe_retained_formation_structures(self):
            assert self.committed
            return (
                (recalled_receipt, recalled, (), (), 0),
                (related_receipt, related, (), (), 0),
            )

    organism = _EpisodicOrganism()
    prepared = SimpleNamespace(
        token="prepared-token",
        organic_mosaic_relations=(
            (
                (recalled_receipt, related_receipt),
                (),
                (bond,),
                "55" * 32,
                (((recalled[0], related[0], 0, 7), (related[0], related[1], 0, 5)),),
                (
                    (
                        (recalled[0], related[0], 0, 7),
                        (related[0], related[1], 0, 5),
                        (recalled[0], related[0], 0, 9),
                        (related[0], related[1], 0, 4),
                    ),
                ),
            ),
        ),
    )
    observed = probe._commit_and_observe_episodic_relation(
        organism,
        prepared,
        recalled,
    )
    assert observed is not None
    assert observed["episodic_recalled_formation_receipt"] == recalled_receipt
    assert observed["episodic_related_formation_count"] == 2
    assert observed["episodic_relation_active_bond_count"] == 1
    assert observed["ordered_physical_path_count"] == 1
    assert observed["ordered_path_relation_count"] == 1
    assert observed["structural_relation_sha256"] == "55" * 32
