from __future__ import annotations

import pytest

from dsf_ai_service.glew_runtime.native_resident_organism import (
    create_native_resident_organism,
)
from tests.test_native_resident_production_mount import (
    IDENTITY,
    _growth_dna_fixture,
)


def test_one_native_body_candidate_commits_at_most_once() -> None:
    organism = create_native_resident_organism(
        organism_identity=IDENTITY,
        organism_tick=0,
        growth_dna=_growth_dna_fixture(),
        max_envelope_bytes=67_108_864,
        max_fabric_bytes=67_108_000,
        max_logical_peak_bytes=536_870_912,
    )
    before = organism.readiness()
    prepared = organism.prepare_articulated_body_observation()

    assert prepared.predecessor_state_sha256 == before.state_sha256
    assert prepared.prepared_state_sha256 != before.state_sha256
    assert prepared.receptor_ingress_sense_counts == (0, 0, 0, 0, 0, 74)
    assert organism.readiness().state_sha256 == before.state_sha256

    committed = organism.commit(prepared.token)
    assert committed.state_sha256 == prepared.prepared_state_sha256
    assert committed.organism_tick == before.organism_tick + 1

    with pytest.raises(ValueError, match="pending candidate"):
        organism.commit(prepared.token)
    assert organism.readiness().state_sha256 == committed.state_sha256


def test_every_lived_trajectory_contains_one_current_body_observation() -> None:
    source, _ = _growth_dna_fixture()
    organism = create_native_resident_organism(
        organism_identity=IDENTITY,
        organism_tick=0,
        growth_dna=_growth_dna_fixture(),
        max_envelope_bytes=67_108_864,
        max_fabric_bytes=67_108_000,
        max_logical_peak_bytes=536_870_912,
    )
    admissions = (((1, 1),),)

    first_phase = organism.begin_unsealed_intake_direct((source,), admissions)
    first = organism.finalize_unsealed_intake_direct(first_phase.token)
    organism.acknowledge_direct_commit(first.token)
    second_phase = organism.begin_unsealed_intake_direct((source,), admissions)
    second = organism.finalize_unsealed_intake_direct(second_phase.token)
    organism.acknowledge_direct_commit(second.token)

    assert (first.predecessor_organism_tick, first.organism_tick) == (0, 2)
    assert (second.predecessor_organism_tick, second.organism_tick) == (2, 4)
    assert len(first.causal_interval_evidence) == 2
    assert len(second.causal_interval_evidence) == 2
    assert first.receptor_ingress_sense_counts[5] == 74
    assert second.receptor_ingress_sense_counts[5] == 74
    assert organism.readiness().articulated_body_proprioception_initialized
