"""D2 evidence-only runtime: admitted native transitions and exact custody.

Migrated to the mandatory-admission surface: every native transition is an
explicit ``prepare_admitted`` (caller-authored maximum causal intervals plus a
durable hippocampal cold-custody directory) followed by ``commit``.  The bare
``prepare(source)`` path stays severed by law.

Under the ratified retinal receptor law (``optical_receptor_work.rs``) only an
exact optical occurrence or a vestibular ingress can genesis a cognitive
cohort, and the retired transient "trace" counter is always zero; sound-only
episodes reach the resident mounted joint field but form no cognition on
their own.  The assertions below state exactly that current physics.
"""

from __future__ import annotations

import math
from fractions import Fraction

import dsf_ai_service.app as app_module
from dsf_ai_service.glew_runtime.native_joint_source_episode import (
    NativeJointSourceOccurrenceInput,
    UF_V1_4_SAMPLED_VOLUME_AND_RELEVANCE_PIECEWISE_LINEAR,
    settle_native_joint_source_episode,
)
from dsf_ai_service.glew_runtime.native_resident_organism import (
    create_native_resident_organism,
    restore_native_resident_organism,
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
from dsf_ai_service.substrate.embodiment_world import (
    PORT_ID,
    EmbodimentWorldAuthority,
    MoveCommand,
    PoseMM,
    PositionMM,
    encode_command,
)
from dsf_ai_service.substrate.w1_coupled_material_sensory_physics import (
    build_coupled_six_sense_full_field,
)
from dsf_ai_service.v4.guala_physical_runtime import Guala


IDENTITY = "12345678-9abc-4def-8123-456789abcdef"
BUDGET = {
    "max_envelope_bytes": 67_108_864,
    "max_fabric_bytes": 67_108_000,
    "max_logical_peak_bytes": 536_870_912,
}
# The ratified fixture admission: an explicit five-unit maximum causal
# interval admits every fixture occurrence spanning at most two source-time
# units without changing any evaluated value (joint_uf_source_adapter.rs).
FIXTURE_ADMISSION = (5, 1)
EAR_PORT_COUNT = 2
RETINAL_QUANTITY = "retinal-spectral-irradiance"
RETINAL_UNIT = "fraction-of-declared-retinal-reference-irradiance"

_TIMES = tuple(Fraction(index) for index in range(3))
_LIT = (0.0, 0.5, 1.0)
_DARK = (0.0, 0.0, 0.0)


def _substream(
    sense: PhysicalSense,
    sensor_id: str,
    substream_id: str,
    topology_index: int,
    quantity: str,
    unit: str,
    signal: tuple[float, ...],
    times: tuple[Fraction, ...],
) -> NativeSensorySubstreamInput:
    return NativeSensorySubstreamInput(
        sense=sense,
        sensor_id=sensor_id,
        substream_id=substream_id,
        topology_index=topology_index,
        coordinates=(NativeAxisCoordinate("site", str(topology_index)),),
        physical_quantity=quantity,
        physical_unit=unit,
        source_times=times,
        normalized_signal=signal,
        phase_turns=(Fraction(0),) * len(times),
    )


def _episode(observed, times):
    states = {
        sense: (
            SenseBoundaryState.OBSERVED
            if sense in observed
            else SenseBoundaryState.QUIESCENT
        )
        for sense in SENSE_ORDER
    }
    port_count = sum(len(ports) for ports in observed.values())
    occurrence = NativeJointSourceOccurrenceInput(
        port_indices=tuple(range(port_count)),
        source_times=times,
        joint_intersample_profile_payload=(
            UF_V1_4_SAMPLED_VOLUME_AND_RELEVANCE_PIECEWISE_LINEAR
        ),
        groups=(tuple(range(port_count)),),
        joint_relevance_profile_payload=(
            b"guala.test.explicit_joint_relevance.v1"
        ),
        joint_relevance=(Fraction(1),) * len(times),
    )
    return settle_native_joint_source_episode(
        assembly_id="d2-admitted-occurrence",
        observed_substreams=observed,
        states=states,
        occurrences=(occurrence,),
    )


def _ear_episode(signal: tuple[float, ...], times: tuple[Fraction, ...]):
    """Both co-located organism ears immersed in one pressure field."""

    return _episode(
        {
            PhysicalSense.SOUND: tuple(
                _substream(
                    PhysicalSense.SOUND,
                    "organism-ear-pressure",
                    f"ear-{index}",
                    index,
                    "normalized_physical_excitation",
                    "normalized_binary64",
                    signal,
                    times,
                )
                for index in range(EAR_PORT_COUNT)
            )
        },
        times,
    )


def _optical_episode(signals: list[tuple[float, ...]]):
    return _episode(
        {
            PhysicalSense.SIGHT: tuple(
                _substream(
                    PhysicalSense.SIGHT,
                    "left-retina",
                    f"foveal-receptor-{index}",
                    index,
                    RETINAL_QUANTITY,
                    RETINAL_UNIT,
                    signal,
                    _TIMES,
                )
                for index, signal in enumerate(signals)
            )
        },
        _TIMES,
    )


def _growth_dna(anatomy_episode):
    """One chain seed group over every port at the ratified 500 pS."""

    port_count = anatomy_episode.port_count
    return (
        anatomy_episode,
        [
            (
                list(range(port_count)),
                [(index - 1, index, 500) for index in range(1, port_count)],
            )
        ],
    )


def _organism(anatomy_episode):
    return create_native_resident_organism(
        organism_identity=IDENTITY,
        organism_tick=0,
        growth_dna=_growth_dna(anatomy_episode),
        **BUDGET,
    )


def _admitted_step(organism, episode, cold_root):
    del cold_root
    phase = organism.begin_unsealed_intake_direct(
        (episode,),
        (tuple(FIXTURE_ADMISSION for _ in range(episode.occurrence_count)),),
    )
    prepared = organism.finalize_unsealed_intake_direct(phase.token)
    observed = organism.readiness()
    organism.acknowledge_direct_commit(prepared.token)
    return prepared, observed


def _tone(sample_count: int = 320, sample_rate: int = 16_000):
    times = tuple(
        Fraction(index, sample_rate) for index in range(0, sample_count, 4)
    )
    signal = tuple(
        math.sin(2.0 * math.pi * 440.0 * index / sample_rate) * 0.25
        for index in range(0, sample_count, 4)
    )
    return times, signal


def test_sound_settlement_cold_restores_exact_resident_neuron_evidence(
    tmp_path,
) -> None:
    times, signal = _tone()
    episode = _ear_episode(signal, times)
    organism = _organism(episode)
    prepared, observed = _admitted_step(
        organism, episode, tmp_path / "hippocampal-cold"
    )

    assert observed.joint_field_count == 1
    assert observed.joint_neuron_count == EAR_PORT_COUNT
    assert prepared.dsf_delivery_count == EAR_PORT_COUNT
    assert prepared.current_cohort_evaluation_count == 1
    # Sound alone cannot genesis a cognitive cohort under the ratified
    # retinal receptor law; the mounted joint field is still real evidence.
    assert observed.complete_neuron_count == 0
    assert observed.cognitive_trace_count == 0
    assert observed.cognitive_mosaic_count == 0
    assert observed.python_callback_count == 0

    state = organism.save()
    assert state.startswith(b"GLORUN01")
    assert len(state) == observed.state_bytes

    restored = restore_native_resident_organism(
        current_envelope=state,
        **BUDGET,
    )
    restored_observation = restored.readiness()
    assert restored.save() == state
    assert (
        restored_observation.joint_neuron_count == observed.joint_neuron_count
    )
    assert restored_observation.state_sha256 == observed.state_sha256
    assert restored_observation.cognitive_trace_count == 0
    assert restored_observation.cognitive_mosaic_count == 0


def test_recurrence_forms_one_mosaic_then_stays_byte_bounded(
    tmp_path,
) -> None:
    lit = _optical_episode([_LIT] * 4)
    dark = _optical_episode([_DARK] * 4)
    partial = _optical_episode([_LIT] + [_DARK] * 3)
    organism = _organism(lit)
    cold_root = tmp_path / "hippocampal-cold"

    sizes: list[int] = []
    mosaic_counts: list[int] = []

    def step(episode) -> None:
        _prepared, observed = _admitted_step(organism, episode, cold_root)
        sizes.append(observed.state_bytes)
        mosaic_counts.append(observed.cognitive_mosaic_count)

    # The ratified growth sequence: each receptor reached, quiescence, one
    # partial re-observation, quiescence again; the retained experience is
    # admitted as exactly one physical mosaic.
    for receptor in range(4):
        step(_optical_episode([
            _LIT if index == receptor else _DARK for index in range(4)
        ]))
    for _ in range(8):
        step(dark)
    step(partial)
    attempts = 0
    while mosaic_counts[-1] == 0 and attempts < 8:
        step(dark)
        attempts += 1

    assert mosaic_counts[-1] == 1, "authored growth DNA did not admit a mosaic"
    first_mosaic_index = mosaic_counts.index(1)
    # Exactly one mosaic, never more.
    assert set(mosaic_counts[first_mosaic_index:]) == {1}

    # After the mosaic is admitted, identical quiescent recurrence stays
    # byte-bounded: no unbounded growth.
    post_sizes = []
    for _ in range(4):
        step(dark)
        post_sizes.append(sizes[-1])
    assert len(set(post_sizes)) == 1
    assert set(mosaic_counts[first_mosaic_index:]) == {1}

    state = organism.save()
    assert state.startswith(b"GLORUN01")
    restored = restore_native_resident_organism(
        current_envelope=state,
        **BUDGET,
    )
    assert restored.readiness().cognitive_mosaic_count == 1
    assert restored.readiness().complete_neuron_count == 4
    assert restored.save() == state


def test_virtual_material_and_body_senses_reach_resident_neurons(
    tmp_path,
) -> None:
    world = EmbodimentWorldAuthority(authority_key=b"d2-world-key" * 4)
    before = world.observation_snapshot()
    execution = world.execute_port_command(
        port_id=PORT_ID,
        command_payload=encode_command(MoveCommand(
            PoseMM(PositionMM(1_000, 1_200, 0), 0),
            200_000,
        )),
        causal_intent_receipt_sha256="a" * 64,
        expected_revision=before.revision,
    )
    built = build_coupled_six_sense_full_field(
        assembly_id="d2-virtual-material-body-occurrence",
        source_time_start=Fraction(0),
        source_time_end=Fraction(1, 5),
        world_authority=world,
        execution_receipt=execution,
    )
    states = {
        boundary.sense.value: boundary.state.value
        for boundary in built.boundary.boundaries
    }
    substream_counts = {
        boundary.sense.value: len(boundary.substreams)
        for boundary in built.boundary.boundaries
    }
    episode = built.native_joint_source_episode
    growth_dna = (
        episode,
        [
            (
                list(range(episode.port_count)),
                [(index - 1, index, 500) for index in range(1, episode.port_count)],
            )
        ],
    )
    organism = create_native_resident_organism(
        organism_identity="12345678-9abc-4def-8123-456789abcdef",
        organism_tick=0,
        growth_dna=growth_dna,
        max_envelope_bytes=67_108_864,
        max_fabric_bytes=67_108_000,
        max_logical_peak_bytes=536_870_912,
    )
    phase = organism.begin_unsealed_intake_direct(
        (built.native_joint_source_episode,),
        (tuple((1, 5) for _ in range(episode.occurrence_count)),),
    )
    prepared = organism.finalize_unsealed_intake_direct(phase.token)
    observed = organism.readiness()
    organism.acknowledge_direct_commit(prepared.token)

    assert states == {
        "body": "observed",
        "sight": "observed",
        "smell": "observed",
        "sound": "sensor_unavailable",
        "taste": "observed",
        "touch": "observed",
    }
    assert substream_counts == {
        "body": 4,
        "sight": 162,
        "smell": 8,
        "sound": 0,
        "taste": 5,
        "touch": 6,
    }
    assert observed.joint_field_count == 1
    assert observed.joint_neuron_count == sum(substream_counts.values()) == 185
    # Under the ratified retinal receptor law only the 162 exact optical
    # receptor sites can transition cognitive neurons in this first reached
    # occurrence; every one of the 185 senses still reaches the resident
    # mounted joint field above.
    assert prepared.physically_transitioned_neuron_count == 162
    assert prepared.complete_neuron_count == 162
    assert observed.cognitive_trace_count == 0
    assert observed.cognitive_mosaic_count == 0
    assert observed.python_callback_count == 0


def test_retired_python_autonomy_is_truthfully_unavailable(monkeypatch) -> None:
    monkeypatch.setenv(
        "GUALA_CAUSAL_ACTION_KEY",
        "0123456789abcdef0123456789abcdef",
    )
    monkeypatch.setenv("EVENT_DRIVEN_SUBSTRATE", "0")
    monkeypatch.setenv("WAVE_ATLAS_ENABLED", "0")
    monkeypatch.setenv("WAVE_SUMMARY_ENQUEUE_ENABLED", "0")
    monkeypatch.setenv("SELF_HEARING_ENABLED", "0")
    organism = Guala()
    try:
        assert organism.start_autonomous_experience_driver() == {
            "lifecycle": "unavailable",
            "reason": "legacy_python_autonomy_retired",
            "schema": "guala.autonomous_experience.unavailable.v1",
        }
    finally:
        organism.shutdown()


def test_sealed_boot_does_not_require_retired_curriculum() -> None:
    source = app_module._embedded_post_boot.__code__
    constants = tuple(
        value for value in source.co_consts if isinstance(value, str)
    )
    assert not any(
        "curriculum is absent from the sealed production engine" in value
        for value in constants
    )
    assert any("native tutoring unavailable" in value for value in constants)
