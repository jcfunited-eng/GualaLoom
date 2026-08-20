"""Production mounts only the native resident organism and truthful transport."""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import json
from pathlib import Path

import pytest

from dsf_ai_service import native_production_app as production
from dsf_ai_service.glew_runtime.native_joint_source_episode import (
    NativeJointSourceOccurrenceInput,
    UF_V1_4_SAMPLED_VOLUME_AND_RELEVANCE_PIECEWISE_LINEAR,
    settle_native_joint_source_episode,
)
from dsf_ai_service.glew_runtime.native_resident_organism import (
    create_native_resident_organism,
    exact_native_yaw_trajectory,
)
from dsf_ai_service.glew_runtime.native_sensory_full_field import (
    NativeSensorySubstreamInput,
)
from dsf_ai_service.glew_runtime.sensory_full_field_boundary import (
    NativeAxisCoordinate,
    PhysicalSense,
    SENSE_ORDER,
    SenseBoundaryState,
)


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = "1cc4e70a-f2a0-44c5-a111-f4a5bc915cc1"


def _growth_dna_fixture():
    """Authored growth DNA: a four-receptor sight anatomy episode plus one
    seed group covering its ports as a chain with 500 pS contacts."""

    times = tuple(Fraction(index, 4) for index in range(4))

    def _substream(topology_index: int) -> NativeSensorySubstreamInput:
        return NativeSensorySubstreamInput(
            sense=PhysicalSense.SIGHT,
            sensor_id="sight-organ",
            substream_id=f"sight-{topology_index}",
            topology_index=topology_index,
            coordinates=(
                NativeAxisCoordinate("receptor", str(topology_index)),
            ),
            physical_quantity="normalized_physical_excitation",
            physical_unit="normalized_binary64",
            source_times=times,
            normalized_signal=(0.0, 0.5, -0.25, 1.0),
            phase_turns=(Fraction(0),) * 4,
        )

    observed = {
        PhysicalSense.SIGHT: tuple(_substream(index) for index in range(4)),
    }
    states = {
        sense: (
            SenseBoundaryState.OBSERVED
            if sense in observed
            else SenseBoundaryState.QUIESCENT
        )
        for sense in SENSE_ORDER
    }
    episode = settle_native_joint_source_episode(
        assembly_id="growth-dna-anatomy",
        observed_substreams=observed,
        states=states,
        occurrences=(
            NativeJointSourceOccurrenceInput(
                port_indices=(0, 1, 2, 3),
                source_times=times,
                joint_intersample_profile_payload=(
                    UF_V1_4_SAMPLED_VOLUME_AND_RELEVANCE_PIECEWISE_LINEAR
                ),
                groups=((0, 1, 2, 3),),
                joint_relevance_profile_payload=(
                    b"guala.test.explicit_joint_relevance.v1"
                ),
                joint_relevance=(Fraction(1),) * 4,
            ),
        ),
    )
    port_count = episode.port_count
    seed_groups = [
        (
            list(range(port_count)),
            [(index - 1, index, 500) for index in range(1, port_count)],
        )
    ]
    return (episode, seed_groups)


@dataclass
class _Observation:
    identity: str = IDENTITY
    organism_tick: int = 0
    fabric_bytes: int = 0
    fabric_generation: int = 0
    fabric_sha256: str = "0" * 64
    joint_field_count: int = 0
    joint_neuron_count: int = 0
    mounted_generation: int = 0
    state_bytes: int = 1
    state_sha256: str = "a" * 64
    cognitive_mosaic_count: int = 0
    mosaic_of_mosaics_count: int = 0
    cognitive_ordinal: int = 0
    cognitive_trace_count: int = 0
    complete_neuron_count: int = 0
    physically_transitioned_neuron_count: int = 0
    formation_activation_count: int = 0
    partial_cue_reassembly_count: int = 0
    endogenous_partial_cue_reassembly_count: int = 0
    physical_transition_claimed: bool = False
    python_callback_count: int = 0
    # Energy state (minimal feeding metabolism, 2026-08-05): the readiness
    # observation now carries the decoded energy physics.
    recovery_fuel_quanta: int = 0
    recovery_spent_quanta: int = 0
    recovery_heat_quanta: int = 0
    recovery_fuel_capacity_quanta: int = 0
    dissipated_quanta: int = 0
    dissipation_capacity_quanta: int = 0
    separated_elementary_charges: int = 0
    energy_exhausted: bool = False
    available_energy_zeptojoules: tuple[int, int] = (0, 1)
    spent_energy_zeptojoules: tuple[int, int] = (0, 1)
    thermal_energy_zeptojoules: tuple[int, int] = (0, 1)
    available_energy_capacity_zeptojoules: tuple[int, int] = (0, 1)
    dissipated_energy_zeptojoules: tuple[int, int] = (0, 1)
    dissipation_capacity_energy_zeptojoules: tuple[int, int] = (0, 1)
    articulated_body_state_bytes: int = 195
    articulated_body_state_sha256: str = "b" * 64
    articulated_body_proprioception_initialized: bool = True
    articulated_body_lung_air_microlitres: int = 2_000_000

    @property
    def articulated_body_axes(self):
        return [
            (index, f"axis_{index}", "millidegree", 0, -1, 0, 1)
            for index in range(37)
        ]

    @property
    def articulated_body_vocal_tract_areas_square_millimetres(self):
        return [100] * 8


class _Organism:
    def __init__(self, observation: _Observation | None = None) -> None:
        self.observation = observation or _Observation()

    def readiness(self) -> _Observation:
        return self.observation

    def observe_reached_neuron_count_by_layer(self):
        return ()

    def observe_reached_source_site_count(self, _sensor_id, _substream_id):
        return 0

    def observe_retained_formation_recurrence_evidence(self):
        return ()

    def observe_retained_formations(self):
        return ()


@dataclass
class _Restored:
    organism: _Organism = field(default_factory=_Organism)


@dataclass
class _Admission:
    max_envelope_bytes: int = 1_000
    max_fabric_bytes: int = 900
    max_logical_peak_bytes: int = 3_000
    memory_boundary_source: str = "test"
    derivation: str = "finite native test regions"


def _release_files() -> set[str]:
    manifest = json.loads(
        (ROOT / "deploy" / "guala_release_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    return {
        path
        for category in manifest["categories"]
        for path in category["files"]
    }


def test_release_cannot_boot_the_retired_python_organism() -> None:
    files = _release_files()
    assert "dsf_ai_service/native_production_app.py" in files
    assert "dsf_ai_service/v4/guala_physical_runtime.py" not in files
    assert "dsf_ai_service/substrate_runner.py" not in files
    source = (ROOT / "dsf_ai_service" / "native_production_app.py").read_text(
        encoding="utf-8"
    )
    assert "guala_physical_runtime" not in source
    assert "process_sound_frame" not in source


def test_native_genesis_is_empty_physical_state_not_synthetic_cognition() -> None:
    organism = create_native_resident_organism(
        organism_identity=IDENTITY,
        organism_tick=0,
        growth_dna=_growth_dna_fixture(),
        max_envelope_bytes=67_108_864,
        max_fabric_bytes=67_108_000,
        max_logical_peak_bytes=536_870_912,
    )
    observed = organism.readiness()
    body = organism.save()
    assert body.startswith(b"GLORUN01")
    assert observed.identity == IDENTITY
    assert observed.organism_tick == 0
    assert observed.joint_field_count == 0
    assert observed.joint_neuron_count == 0
    assert observed.cognitive_trace_count == 0
    assert observed.cognitive_mosaic_count == 0
    assert observed.formation_activation_count == 0
    assert observed.partial_cue_reassembly_count == 0
    assert observed.metabolically_perturbed_body_receptor_count == 0
    assert observed.python_callback_count == 0


def test_native_body_trajectory_exports_local_metabolic_afference() -> None:
    organism = create_native_resident_organism(
        organism_identity=IDENTITY,
        organism_tick=0,
        growth_dna=_growth_dna_fixture(),
        max_envelope_bytes=67_108_864,
        max_fabric_bytes=67_108_000,
        max_logical_peak_bytes=536_870_912,
    )
    _successor_heading, trajectory = exact_native_yaw_trajectory(
        predecessor_heading_millidegrees=0,
        signed_displacement_millidegrees=90_000,
        duration_microseconds=250_000,
    )
    phase = organism.begin_unsealed_intake_direct(
        (), (), vestibular_yaw=(0, trajectory)
    )
    assert not phase.motor_unit_recruitments
    prepared = organism.finalize_unsealed_intake_direct(phase.token)
    result = production._resident_prepare_hop(prepared, organism.readiness())
    organism.acknowledge_direct_commit(prepared.token)
    assert result["metabolically_perturbed_body_receptor_count"] > 0
    assert result["metabolically_perturbed_body_receptor_count"] <= len(trajectory)
    committed = organism.readiness()
    assert committed.metabolically_perturbed_body_receptor_count > 0
    assert committed.python_callback_count == 0


@pytest.mark.asyncio
async def test_unmounted_or_malformed_browser_senses_fail_without_touching_organism(
    monkeypatch,
) -> None:
    organism = _Organism()
    monkeypatch.setattr(production, "_restored", _Restored(organism))
    monkeypatch.setattr(production, "_admission", _Admission())
    before = organism.readiness()
    sight = production.sight_frame(None)
    # PIN UPDATED 2026-08-06: standalone hearing is suspended by the
    # ratified two-real-signal doctrine (Joe, 2026-08-05) and refuses 503
    # BEFORE the body is even read; the organism stays untouched.
    sound = await production.sound_frame(None)
    after = organism.readiness()
    assert sight.status_code == 422
    assert b"requires a JSON object body" in sight.body
    assert sound.status_code == 503
    assert b'"accepted":false' in sound.body.replace(b" ", b"")
    assert before == after


def test_startup_rejects_false_step_claims_at_cold_restore(monkeypatch) -> None:
    """A cold restore performs no step, so restored state must not claim one.

    Genuine retained cognition (trace, mosaic, complete-neuron counts) is
    lawful restored state; claimed step effects are not.
    """

    changed = _Observation(physical_transition_claimed=True)
    monkeypatch.setattr(
        production,
        "derive_native_resident_resource_admission",
        lambda _root: _Admission(),
    )
    monkeypatch.setattr(
        production,
        "restore_current_native_organism",
        lambda *_args, **_kwargs: _Restored(_Organism(changed)),
    )
    with pytest.raises(RuntimeError, match="claimed step effects"):
        production._startup()
    assert production._restored is None
    assert production._admission is None

    activated = _Observation(formation_activation_count=1)
    monkeypatch.setattr(
        production,
        "restore_current_native_organism",
        lambda *_args, **_kwargs: _Restored(_Organism(activated)),
    )
    with pytest.raises(RuntimeError, match="claimed step effects"):
        production._startup()


def test_startup_accepts_genuine_restored_native_cognition(monkeypatch) -> None:
    """Retained native cognition (mosaics, complete neurons) restores cleanly."""

    learned = _Observation(
        cognitive_mosaic_count=1,
        cognitive_ordinal=9,
        complete_neuron_count=29,
        joint_field_count=1,
        joint_neuron_count=29,
    )
    monkeypatch.setattr(
        production,
        "derive_native_resident_resource_admission",
        lambda _root: _Admission(),
    )
    monkeypatch.setattr(
        production,
        "restore_current_native_organism",
        lambda *_args, **_kwargs: _Restored(_Organism(learned)),
    )
    production._startup()
    try:
        assert production._restored is not None
        record = production._native_record()
        assert record["cognitive_mosaic_count"] == 1
        assert record["complete_neuron_count"] == 29
    finally:
        production._restored = None
        production._admission = None
        production._public_observation_body = None
        production._public_observation_etag = None


def test_authorized_startup_migrates_before_first_restore(monkeypatch) -> None:
    calls: list[str] = []
    learned = _Observation(
        cognitive_mosaic_count=1,
        complete_neuron_count=29,
        joint_field_count=1,
        joint_neuron_count=29,
    )
    monkeypatch.setenv("GUALA_CURRENT_FORMAT_MIGRATION", "1")
    monkeypatch.setattr(
        production,
        "derive_native_resident_resource_admission",
        lambda _root: _Admission(),
    )
    monkeypatch.setattr(
        production,
        "migrate_current_native_organism_current_format",
        lambda *_args, **_kwargs: calls.append("migrate"),
    )
    monkeypatch.setattr(
        production,
        "restore_current_native_organism",
        lambda *_args, **_kwargs: (
            calls.append("restore") or _Restored(_Organism(learned))
        ),
    )
    monkeypatch.setattr(production, "_refresh_public_observation_cache", lambda: None)

    production._startup()
    try:
        assert calls[:2] == ["migrate", "restore"]
    finally:
        production._restored = None
        production._admission = None
        production._public_observation_body = None
        production._public_observation_etag = None


def test_startup_performs_growth_dna_genesis_when_current_absent(
    monkeypatch, tmp_path
) -> None:
    """An empty state directory births one seeded growth-DNA genesis body."""

    monkeypatch.setattr(production, "STATE_ROOT", tmp_path)
    monkeypatch.setenv("GUALA_CURRENT_FORMAT_MIGRATION", "1")
    production._startup()
    try:
        assert (tmp_path / "CURRENT").is_file()
        observed = production._restored.organism.readiness()
        assert observed.organism_tick == 0
        assert observed.joint_field_count == 0
        assert observed.joint_neuron_count == 0
        assert observed.complete_neuron_count == 0
        assert observed.cognitive_mosaic_count == 0
        assert observed.python_callback_count == 0
        # An explicitly authorized restart sees an already-current body as a
        # physical no-op: no self-predecessor publication and no new receipt.
        first_sha = production._restored.pointer.state_sha256
        production._startup()
        assert production._restored.pointer.state_sha256 == first_sha
    finally:
        production._restored = None
        production._admission = None
        production._public_observation_body = None
        production._public_observation_etag = None
