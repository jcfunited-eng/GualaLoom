"""Read-only fresh-process proof of one native-organism CURRENT pointer."""

from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from dsf_ai_service.glew_runtime.native_resident_organism import (
    exact_articulatory_unit_trajectory,
    exact_native_yaw_trajectory,
    restore_native_resident_organism,
)
from dsf_ai_service.substrate.native_organism_binary_store import (
    NativeOrganismBinaryStoreError,
    publish_staged_native_organism,
    rehearse_current_native_organism_current_format,
    restore_current_native_organism,
    stage_active_native_organism,
)
from dsf_ai_service.substrate.native_resident_resource_admission import (
    derive_native_resident_resource_admission,
)


PROOF_SCHEMA = "guala.production_native_current_cold_restore.v8"
_COMMIT = re.compile(r"[0-9a-f]{40}")
_DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
_SHA256 = re.compile(r"[0-9a-f]{64}")

# The complete production receptor roster plus 74 articulated-body terminals
# requires 78,641,443 successor cognitive bytes through the current unsealed
# intake boundary.  The fresh A-013 rehearsal admits the smallest whole-MiB
# envelope tier above that measured exact boundary.  These constants do not
# govern the resident organism, whose bounds remain cgroup-derived.
_A013_FRESH_MAX_ENVELOPE_BYTES = 78_643_200
_A013_FRESH_MAX_FABRIC_BYTES = 78_642_336
_A013_FRESH_MAX_LOGICAL_PEAK_BYTES = 629_145_600


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _exact_energy(value: object, label: str) -> Fraction:
    if (
        not isinstance(value, tuple)
        or len(value) != 2
        or any(isinstance(part, bool) or not isinstance(part, int) for part in value)
        or value[1] <= 0
    ):
        raise RuntimeError(f"{label} lost its exact rational representation")
    return Fraction(value[0], value[1])


def _fraction_parts(value: Fraction) -> tuple[int, int]:
    return value.numerator, value.denominator


def _observe_c024_cognitive_capital(
    restored: object,
    admission: object,
    expected_state_sha256: str,
) -> dict[str, object]:
    """Read the exact restored body through the candidate public observer."""

    from dsf_ai_service import native_production_app as production

    # The mounted source is a living EFS root. It can lawfully advance between
    # this probe's first restore and the public observer's startup, which used
    # to compare two different valid moments and intermittently reject a
    # release. Publish the already-restored in-memory body into one disposable
    # local CURRENT so the observer reads the exact body under rehearsal.
    with tempfile.TemporaryDirectory(prefix="guala-c024-current-") as temporary:
        snapshot_root = Path(temporary)
        staged = stage_active_native_organism(
            snapshot_root,
            restored.organism,
            max_envelope_bytes=admission.max_envelope_bytes,
        )
        publish_staged_native_organism(
            staged,
            expected_predecessor_sha256=None,
            object_store=production._LocalDirectoryObjectStore(
                snapshot_root / "object-mirror"
            ),
            max_envelope_bytes=admission.max_envelope_bytes,
            max_fabric_bytes=admission.max_fabric_bytes,
            max_logical_peak_bytes=admission.max_logical_peak_bytes,
        )
        production.STATE_ROOT = snapshot_root
        production._startup()
        observed = production._build_public_observation()
    if observed["generation_state"]["state_sha256"] != expected_state_sha256:
        raise RuntimeError("C-024 observer did not read the rehearsed CURRENT")
    capital = observed.get("cognitive_capital")
    if not isinstance(capital, dict):
        raise RuntimeError("C-024 observer supplied no cognitive-capital record")
    capabilities = capital.get("capabilities")
    dimensions = capital.get("dimensions")
    credits = capital.get("credits")
    if (
        capabilities != list(production.COGNITIVE_CAPITAL_CAPABILITIES)
        or dimensions != list(production.COGNITIVE_CAPITAL_DIMENSIONS)
        or not isinstance(credits, list)
        or capital.get("scalar_score_authority") is not False
        or capital.get("cognition_authority") is not False
    ):
        raise RuntimeError("C-024 observer changed its non-flattened contract")
    cells: set[tuple[str, str]] = set()
    evidence_reference_count = 0
    for credit in credits:
        if not isinstance(credit, dict):
            raise RuntimeError("C-024 credit is not an object")
        cell = (credit.get("capability"), credit.get("dimension"))
        evidence = credit.get("evidence")
        if (
            cell[0] not in production.COGNITIVE_CAPITAL_CAPABILITIES
            or cell[1] not in production.COGNITIVE_CAPITAL_DIMENSIONS
            or cell in cells
            or not isinstance(evidence, list)
            or not evidence
        ):
            raise RuntimeError("C-024 credit is duplicate, unknown, or unreferenced")
        cells.add(cell)
        for reference in evidence:
            if (
                not isinstance(reference, dict)
                or set(reference) != {"kind", "path", "receipt_sha256"}
                or not isinstance(reference["kind"], str)
                or not reference["kind"]
                or not isinstance(reference["path"], str)
                or not reference["path"]
                or not isinstance(reference["receipt_sha256"], str)
                or _SHA256.fullmatch(reference["receipt_sha256"]) is None
            ):
                raise RuntimeError("C-024 evidence reference lost exact identity")
            evidence_reference_count += 1
    unproved = {
        "Language comprehension",
        "Motivation, needs, and curiosity",
        "Social cognition and other-perspective",
        "Creativity and self-expression",
    }
    if any(capability in unproved for capability, _dimension in cells):
        raise RuntimeError("C-024 observer credited an unproved capability")
    required_retained_cells = {
        ("Episodic memory", "retention"),
        ("Episodic memory", "durability"),
        ("Learning and developmental growth", "retention"),
    }
    if int(observed["formations"].get("mosaic_count", 0)) > 0 and not (
        required_retained_cells <= cells
    ):
        raise RuntimeError("C-024 observer omitted retained formation capital")
    import guala_core

    false_native_exports = (
        "cognitive_capital_schema",
        "cognitive_capital_capabilities",
        "cognitive_capital_dimensions",
        "cognitive_capital_reference",
        "cognitive_capital_evidence",
    )
    if any(hasattr(guala_core, name) for name in false_native_exports):
        raise RuntimeError("retired false native cognitive capital remains exported")
    return {
        "c024_cognitive_capital_rehearsed": True,
        "c024_cognitive_capital_state_sha256": expected_state_sha256,
        "c024_cognitive_capital_capability_count": len(capabilities),
        "c024_cognitive_capital_dimension_count": len(dimensions),
        "c024_cognitive_capital_credit_cell_count": len(cells),
        "c024_cognitive_capital_evidence_reference_count": (
            evidence_reference_count
        ),
        "c024_cognitive_capital_observation_bytes": len(_canonical(observed)),
        "c024_cognitive_capital_unproved_cells_preserved": True,
        "c024_false_native_capital_exports_absent": True,
    }


def _commit_unsealed_sources(
    organism: object,
    episodes: tuple[tuple[object, object], ...],
) -> object:
    """Commit admitted sources through the sole production intake boundary."""

    if not episodes:
        raise ValueError("unsealed source transaction must not be empty")
    phase = organism.begin_unsealed_intake_direct(
        tuple(episode for episode, _ in episodes),
        tuple(admissions for _, admissions in episodes),
    )
    evidence = organism.finalize_unsealed_intake_direct(phase.token)
    organism.acknowledge_direct_commit(evidence.token)
    return evidence


def _rehearse_native_physical_rest_and_wake(
    current_envelope: bytes,
    budget: dict[str, int],
) -> dict[str, object]:
    """Prove exact local recovery reopens finite work and later work uses it.

    A bounded run of true dark, silent whole-sensorium intervals supplies
    passage of physical time, not a sleep command. Whether recovery and quiet
    occur is decided only by retained neuronal state and finite recovery-fluid
    material. The next vestibular interval is an ordinary physical cause,
    never a scripted cognitive wake operation.
    """

    def settle() -> tuple[int, object, object, object, object, object, bytes]:
        # Import only the existing whole-sensorium transport builder. It
        # constructs native source occurrences and starts no HTTP runtime.
        from dsf_ai_service.native_production_app import _mono_pcm_hop_episodes

        organism = restore_native_resident_organism(
            current_envelope=current_envelope,
            **budget,
        )
        [(quiet_episode, quiet_admissions)] = _mono_pcm_hop_episodes(
            assembly_prefix="c021-cold-physical-rest",
            samples=(0,) * 4_000,
            sample_rate_hz=16_000,
        )
        qualifying: tuple[int, object, object, object] | None = None
        for interval_ordinal in range(1, 17):
            before = organism.readiness()
            candidate = _commit_unsealed_sources(
                organism,
                ((quiet_episode, quiet_admissions),),
            )
            after = organism.readiness()
            capacity_before = _exact_energy(
                before.dissipation_capacity_energy_zeptojoules,
                "pre-rest dissipation capacity",
            )
            dissipated_before = _exact_energy(
                before.dissipated_energy_zeptojoules,
                "pre-rest dissipated energy",
            )
            capacity_after = _exact_energy(
                after.dissipation_capacity_energy_zeptojoules,
                "post-rest dissipation capacity",
            )
            dissipated_after = _exact_energy(
                after.dissipated_energy_zeptojoules,
                "post-rest dissipated energy",
            )
            if (
                candidate.rest_recovered_neuron_count > 0
                and not candidate.motor_unit_recruitments
                and not candidate.articulatory_unit_recruitments
                and capacity_after == capacity_before
                and dissipated_after < dissipated_before
                and capacity_after - dissipated_after
                > capacity_before - dissipated_before
            ):
                qualifying = (interval_ordinal, before, candidate, after)
                break
        if qualifying is None:
            raise RuntimeError("native physical rest did not emerge within 16 intervals")
        interval_ordinal, before, rest, after_rest = qualifying
        wake = organism.prepare_vestibular_tick(0, 1)
        after_wake = organism.commit(wake.token)
        return (
            interval_ordinal,
            before,
            rest,
            after_rest,
            wake,
            after_wake,
            organism.save(),
        )

    interval_ordinal, before, rest, after_rest, wake, after_wake, successor = settle()
    (
        replay_interval_ordinal,
        replay_before,
        replay_rest,
        replay_after_rest,
        replay_wake,
        replay_after_wake,
        replay_successor,
    ) = settle()

    capacity_before = _exact_energy(
        before.dissipation_capacity_energy_zeptojoules,
        "pre-rest dissipation capacity",
    )
    dissipated_before = _exact_energy(
        before.dissipated_energy_zeptojoules,
        "pre-rest dissipated energy",
    )
    capacity_after_rest = _exact_energy(
        after_rest.dissipation_capacity_energy_zeptojoules,
        "post-rest dissipation capacity",
    )
    dissipated_after_rest = _exact_energy(
        after_rest.dissipated_energy_zeptojoules,
        "post-rest dissipated energy",
    )
    headroom_before = capacity_before - dissipated_before
    headroom_after_rest = capacity_after_rest - dissipated_after_rest

    if (
        rest.rest_recovered_neuron_count <= 0
        or rest.motor_unit_recruitments
        or rest.articulatory_unit_recruitments
        or capacity_after_rest != capacity_before
        or dissipated_after_rest >= dissipated_before
        or headroom_after_rest <= headroom_before
        or after_rest.organism_tick != before.organism_tick + 1
        or wake.physically_transitioned_neuron_count <= 0
        or wake.dsf_delivery_count <= 0
        or after_wake.organism_tick != after_rest.organism_tick + 1
        or after_wake.state_sha256 == after_rest.state_sha256
        or after_wake.python_callback_count != 0
        or replay_interval_ordinal != interval_ordinal
        or replay_before.state_sha256 != before.state_sha256
        or replay_rest.rest_recovered_neuron_count
        != rest.rest_recovered_neuron_count
        or replay_after_rest.state_sha256 != after_rest.state_sha256
        or replay_wake.physically_transitioned_neuron_count
        != wake.physically_transitioned_neuron_count
        or replay_wake.dsf_delivery_count != wake.dsf_delivery_count
        or replay_after_wake.state_sha256 != after_wake.state_sha256
        or replay_successor != successor
    ):
        raise RuntimeError("native physical rest/wake path did not settle exactly")

    return {
        "native_physical_rest_wake_rehearsed": True,
        "native_physical_rest_wake_cold_replay_exact": True,
        "native_rest_interval_ordinal": interval_ordinal,
        "native_rest_recovered_neuron_count": rest.rest_recovered_neuron_count,
        "native_rest_motor_recruitment_count": len(rest.motor_unit_recruitments),
        "native_rest_articulatory_recruitment_count": len(
            rest.articulatory_unit_recruitments
        ),
        "native_rest_dissipated_energy_before_zeptojoules": _fraction_parts(
            dissipated_before
        ),
        "native_rest_dissipated_energy_after_zeptojoules": _fraction_parts(
            dissipated_after_rest
        ),
        "native_rest_reachable_dissipation_headroom_before_zeptojoules": (
            _fraction_parts(headroom_before)
        ),
        "native_rest_reachable_dissipation_headroom_after_zeptojoules": (
            _fraction_parts(headroom_after_rest)
        ),
        "native_rest_successor_state_sha256": after_rest.state_sha256,
        "native_wake_dsf_delivery_count": wake.dsf_delivery_count,
        "native_wake_physically_transitioned_neuron_count": (
            wake.physically_transitioned_neuron_count
        ),
        "native_wake_successor_state_sha256": after_wake.state_sha256,
    }


def _rehearse_native_internal_consolidation(
    current_envelope: bytes,
    budget: dict[str, int],
) -> dict[str, object]:
    """Prove one internally caused retained-formation reorganization.

    The only driving occurrence is a measured dark/silent whole-sensorium
    interval. Exact metabolic movement supplies the internal cue. No timer,
    stored episode, random selector, or external perturbation is admitted.
    """

    def snapshot(organism: object) -> tuple[tuple[object, ...], ...]:
        structures = organism.observe_retained_formation_structures()
        recurrence = {
            receipt: (tuple(cue), origin)
            for receipt, cue, origin in (
                organism.observe_retained_formation_recurrence_evidence()
            )
        }
        observed = []
        for receipt, members, original_bonds, recurrence_bonds, reinforcements in structures:
            cue, origin = recurrence[receipt]
            observed.append(
                (
                    receipt,
                    tuple(members),
                    tuple(original_bonds),
                    tuple(recurrence_bonds),
                    cue,
                    origin,
                    reinforcements,
                )
            )
        return tuple(observed)

    def settle() -> tuple[dict[str, object], bytes]:
        from dsf_ai_service.native_production_app import _mono_pcm_hop_episodes

        organism = restore_native_resident_organism(
            current_envelope=current_envelope,
            **budget,
        )
        [(quiet_episode, quiet_admissions)] = _mono_pcm_hop_episodes(
            assembly_prefix="c022-internal-consolidation",
            samples=(0,) * 4_000,
            sample_rate_hz=16_000,
        )
        prior = snapshot(organism)
        initial = organism.readiness()
        for interval_ordinal in range(1, 33):
            before = organism.readiness()
            candidate = _commit_unsealed_sources(
                organism,
                ((quiet_episode, quiet_admissions),),
            )
            after = organism.readiness()
            current = snapshot(organism)
            prior_by_identity = {
                (formation[1], formation[2]): formation for formation in prior
            }
            current_by_identity = {
                (formation[1], formation[2]): formation for formation in current
            }
            if (
                len(prior_by_identity) != len(prior)
                or len(current_by_identity) != len(current)
            ):
                raise RuntimeError("internal consolidation identity is not unique")
            if not prior_by_identity.keys() <= current_by_identity.keys():
                raise RuntimeError("internal consolidation lost retained formation identity")
            changed = []
            for identity, predecessor in prior_by_identity.items():
                successor = current_by_identity[identity]
                if (
                    successor[5] == "internally_simulated"
                    and successor[0] != predecessor[0]
                    and (successor[3] != predecessor[3] or successor[4] != predecessor[4])
                ):
                    changed.append((predecessor, successor))
            if changed:
                predecessor, successor = changed[0]
                if (
                    candidate.externally_perturbed_body_receptor_count != 0
                    or candidate.metabolically_perturbed_body_receptor_count <= 0
                    or candidate.endogenous_partial_cue_reassembly_count <= 0
                    or candidate.rest_recovered_neuron_count <= 0
                    or after.organism_tick != before.organism_tick + 1
                    or after.state_sha256 == before.state_sha256
                    or after.python_callback_count != 0
                ):
                    raise RuntimeError("internal consolidation lacked exact causal evidence")
                successor_body = organism.save()
                cold = restore_native_resident_organism(
                    current_envelope=successor_body,
                    **budget,
                )
                if (
                    cold.save() != successor_body
                    or cold.readiness().state_sha256 != after.state_sha256
                    or snapshot(cold) != current
                ):
                    raise RuntimeError("internal consolidation did not cold restore exactly")
                return (
                    {
                        "native_internal_consolidation_rehearsed": True,
                        "native_internal_consolidation_interval_ordinal": interval_ordinal,
                        "native_internal_consolidation_cold_restore_exact": True,
                        "native_internal_consolidation_source": "local_metabolic_settlement",
                        "native_internal_consolidation_origin": successor[5],
                        "native_internal_consolidation_formation_count": len(changed),
                        "native_internal_consolidation_member_count": len(successor[1]),
                        "native_internal_consolidation_cue_count": len(successor[4]),
                        "native_internal_consolidation_recurrence_bond_count_before": len(
                            predecessor[3]
                        ),
                        "native_internal_consolidation_recurrence_bond_count_after": len(
                            successor[3]
                        ),
                        "native_internal_consolidation_formation_receipt_before": predecessor[0],
                        "native_internal_consolidation_formation_receipt_after": successor[0],
                        "native_internal_consolidation_state_sha256_before": initial.state_sha256,
                        "native_internal_consolidation_state_sha256_after": after.state_sha256,
                        "native_internal_consolidation_state_bytes_before": initial.state_bytes,
                        "native_internal_consolidation_state_bytes_after": after.state_bytes,
                        "native_internal_consolidation_metabolic_receptor_count": (
                            candidate.metabolically_perturbed_body_receptor_count
                        ),
                        "native_internal_consolidation_external_receptor_count": (
                            candidate.externally_perturbed_body_receptor_count
                        ),
                        "native_internal_consolidation_recovered_neuron_count": (
                            candidate.rest_recovered_neuron_count
                        ),
                        "native_internal_consolidation_motor_recruitment_count": len(
                            candidate.motor_unit_recruitments
                        ),
                        "native_internal_consolidation_articulatory_recruitment_count": len(
                            candidate.articulatory_unit_recruitments
                        ),
                    },
                    successor_body,
                )
            prior = current
        raise RuntimeError("internal consolidation did not emerge within 32 intervals")

    proof, successor = settle()
    replay_proof, replay_successor = settle()
    if proof != replay_proof or successor != replay_successor:
        raise RuntimeError("internal consolidation did not cold replay exactly")
    return {
        **proof,
        "native_internal_consolidation_cold_replay_exact": True,
    }


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-store-root", required=True)
    parser.add_argument("--expected-identity", required=True)
    parser.add_argument("--expected-tick", required=True, type=int)
    parser.add_argument("--expected-state-sha256", required=True)
    parser.add_argument("--candidate-git-sha", required=True)
    parser.add_argument("--candidate-image-digest", required=True)
    return parser.parse_args()


def _rehearse_native_distributed_recall(
    current_envelope: bytes,
    *,
    max_envelope_bytes: int,
    max_fabric_bytes: int,
    max_logical_peak_bytes: int,
) -> dict[str, int | bool | str | tuple[str, ...]]:
    """Prove one body partial cue becomes distributed current recall."""

    budget = {
        "max_envelope_bytes": max_envelope_bytes,
        "max_fabric_bytes": max_fabric_bytes,
        "max_logical_peak_bytes": max_logical_peak_bytes,
    }
    organism = restore_native_resident_organism(
        current_envelope=current_envelope,
        **budget,
    )
    before = organism.readiness()
    layers = {
        lineage: layer
        for lineage, layer, _receptor in (
            organism.observe_reached_neuron_lineage_layers()
        )
    }
    formations = organism.observe_retained_formation_structures()
    cues = dict(organism.observe_retained_formation_recurrence_cues())
    body_cued = [
        (receipt, members, cue)
        for receipt, members, _original, _recurrent, _reinforcements in formations
        if len(cue := cues.get(receipt, ())) == 1 and layers[cue[0]] == 5
    ]
    if len(body_cued) != 1:
        raise RuntimeError("CURRENT has no single exact body-cued formation")
    formation_receipt, formation_members, cue = body_cued[0]
    trajectory_projection = _rehearse_ordered_trajectory_projection(
        current_envelope,
        formation_members,
        budget,
    )
    recalled = None
    episodic_relation = None
    ordered_path_cold_reassembly = False
    heading = 0
    transition_count = 0
    dsf_delivery_count = 0
    for ordinal, signed_step in enumerate((-64, -64, -64, -64), 1):
        interval_predecessor = organism.save()
        prepared = organism.prepare_vestibular_tick(heading, signed_step)
        transition_count += prepared.physically_transitioned_neuron_count
        dsf_delivery_count += prepared.dsf_delivery_count
        observed = _observe_distributed_recognition(
            organism,
            prepared,
            formations,
        )
        relation = _commit_and_observe_episodic_relation(
            organism,
            prepared,
            formation_members,
        )
        if observed is not None and formation_receipt in observed[
            "distributed_recognition_formation_receipts"
        ]:
            interval_recall = {
                **observed,
                "distributed_recall_interval_ordinal": ordinal,
            }
            if (
                episodic_relation is None
                and relation is not None
                and relation["ordered_path_relation_count"] > 0
            ):
                replay = restore_native_resident_organism(
                    current_envelope=interval_predecessor,
                    **budget,
                )
                replay_prepared = replay.prepare_vestibular_tick(heading, signed_step)
                replay_relation = _commit_and_observe_episodic_relation(
                    replay,
                    replay_prepared,
                    formation_members,
                )
                if (
                    replay_prepared.partial_cue_reassembly_count <= 0
                    or replay_relation is None
                    or replay_relation["ordered_path_relation_count"] <= 0
                    or replay_relation["episodic_related_formation_receipts_sha256"]
                    != relation["episodic_related_formation_receipts_sha256"]
                    or replay_relation["episodic_related_member_sets_sha256"]
                    != relation["episodic_related_member_sets_sha256"]
                    or replay_relation["episodic_relation_active_bonds_sha256"]
                    != relation["episodic_relation_active_bonds_sha256"]
                    or replay_relation["structural_relation_sha256"]
                    != relation["structural_relation_sha256"]
                    or replay_relation["ordered_physical_paths_sha256"]
                    != relation["ordered_physical_paths_sha256"]
                    or replay_relation["ordered_path_relations_sha256"]
                    != relation["ordered_path_relations_sha256"]
                    or replay.save() != organism.save()
                ):
                    raise RuntimeError(
                        "cold replay did not reproduce the exact ordered relation"
                    )
                recalled = interval_recall
                episodic_relation = {
                    **relation,
                    "episodic_relation_interval_ordinal": ordinal,
                }
                ordered_path_cold_reassembly = True
        heading = (heading + signed_step) % 360_000
    if (
        recalled is None
        or episodic_relation is None
        or not ordered_path_cold_reassembly
    ):
        raise RuntimeError("body partial cue produced no distributed recall")
    after = organism.readiness()
    successor_state = organism.save()
    cold = restore_native_resident_organism(
        current_envelope=successor_state,
        **budget,
    )
    cold_exact = cold.save() == successor_state
    if (
        dsf_delivery_count <= 0
        or transition_count <= 0
        or after.identity != before.identity
        or after.organism_tick != before.organism_tick + 4
        or after.python_callback_count != 0
        or after.state_sha256 == before.state_sha256
        or not cold_exact
        or cold.readiness().state_sha256 != after.state_sha256
    ):
        raise RuntimeError("native distributed-recall rehearsal changed")
    cold_formations = cold.observe_retained_formation_structures()
    cold_cues = dict(cold.observe_retained_formation_recurrence_cues())
    cold_body_cued = [
        (receipt, members, cue)
        for receipt, members, _original, _recurrent, _reinforcements in cold_formations
        if tuple(members) == tuple(formation_members)
        and len(cue := cold_cues.get(receipt, ())) == 1
    ]
    if len(cold_body_cued) != 1:
        raise RuntimeError("cold successor lost its exact body-cued formation")
    return {
        **recalled,
        **episodic_relation,
        **trajectory_projection,
        "ordered_physical_cold_reassembly": ordered_path_cold_reassembly,
        "distributed_recognition_episode_ordinal": (
            recalled["distributed_recall_interval_ordinal"] - 1
        ),
        "distributed_recognition_source_dsf_delivery_count": dsf_delivery_count,
        "distributed_recognition_source_hop_count": 4,
        "distributed_recognition_source_physical_transition_count": (
            transition_count
        ),
        "distributed_recognition_state_byte_delta": (
            after.state_bytes - before.state_bytes
        ),
        "distributed_recognition_successor_state_sha256": after.state_sha256,
        "distributed_recall_cue_lineage": cue[0],
        "distributed_recall_formation_member_count": len(formation_members),
        "distributed_recall_rehearsed": True,
        "distributed_recall_source_dsf_delivery_count": dsf_delivery_count,
        "distributed_recall_source_physical_transition_count": transition_count,
        "distributed_recall_state_byte_delta": after.state_bytes - before.state_bytes,
        "distributed_recall_successor_state_sha256": after.state_sha256,
        "episodic_archive_lookup_count": 0,
        "episodic_cold_reassembly_exact": True,
        "episodic_complete_source_replayed": False,
        "episodic_memory_rehearsed": True,
        "motor_action_rehearsed": False,
        **_rehearse_sparse_attention_frontier(current_envelope, budget),
    }


def _rehearse_sparse_attention_frontier(
    current_envelope: bytes,
    budget: dict[str, int],
) -> dict[str, int | bool | str]:
    """Cold-replay one ordinary body trajectory and its sparse route change."""

    _successor_heading, steps = exact_native_yaw_trajectory(
        predecessor_heading_millidegrees=0,
        signed_displacement_millidegrees=90_000,
        duration_microseconds=250_000,
    )
    if len(steps) != 250:
        raise RuntimeError("native attention rehearsal changed its body clock")

    def settle() -> tuple[object, object, object, bytes, dict[str, object] | None]:
        organism = restore_native_resident_organism(
            current_envelope=current_envelope,
            **budget,
        )
        before = organism.readiness()
        prepared = organism.prepare_vestibular_trajectory(0, steps)
        after = organism.commit(prepared.token)
        articulation = _rehearse_articulation_and_self_hearing(
            organism, prepared
        )
        successor = organism.save()
        return before, prepared, after, successor, articulation

    before, prepared, after, successor, articulation = settle()
    (
        replay_before,
        replay_prepared,
        replay_after,
        replay_successor,
        replay_articulation,
    ) = settle()
    current_routes = tuple(prepared.physical_frontier_routes)
    preceding_routes = tuple(
        prepared.preceding_distinct_physical_frontier_routes
    )
    replay_current_routes = tuple(replay_prepared.physical_frontier_routes)
    replay_preceding_routes = tuple(
        replay_prepared.preceding_distinct_physical_frontier_routes
    )
    reached_and_foregone_routes = tuple(
        prepared.reached_and_foregone_physical_frontier_routes
    )
    replay_reached_and_foregone_routes = tuple(
        replay_prepared.reached_and_foregone_physical_frontier_routes
    )
    working_continuations = tuple(prepared.working_causal_continuations)
    replay_working_continuations = tuple(
        replay_prepared.working_causal_continuations
    )
    settled_working_frontier = tuple(prepared.settled_working_frontier)
    replay_settled_working_frontier = tuple(
        replay_prepared.settled_working_frontier
    )
    prediction_alternatives = tuple(
        prepared.physical_prediction_alternatives
    )
    replay_prediction_alternatives = tuple(
        replay_prepared.physical_prediction_alternatives
    )
    body_consequence_transfers = tuple(prepared.body_consequence_transfers)
    replay_body_consequence_transfers = tuple(
        replay_prepared.body_consequence_transfers
    )
    affective_balance_trajectories = tuple(
        prepared.affective_balance_trajectories
    )
    replay_affective_balance_trajectories = tuple(
        replay_prepared.affective_balance_trajectories
    )
    localized_fluid_chemistry = tuple(prepared.localized_fluid_chemistry)
    replay_localized_fluid_chemistry = tuple(
        replay_prepared.localized_fluid_chemistry
    )
    localized_metabolic_strain_evaluated_lineages = tuple(
        prepared.localized_metabolic_strain_evaluated_body_receptor_lineages
    )
    replay_localized_metabolic_strain_evaluated_lineages = tuple(
        replay_prepared.localized_metabolic_strain_evaluated_body_receptor_lineages
    )
    localized_metabolic_strain = tuple(prepared.localized_metabolic_strain)
    replay_localized_metabolic_strain = tuple(
        replay_prepared.localized_metabolic_strain
    )
    route_sets = (
        reached_and_foregone_routes,
        current_routes,
        preceding_routes,
    )
    qualifying = next(
        (
            routes
            for routes in route_sets
            if len(routes) > 1
            and any(route[7] == 0 for route in routes)
            and any(route[7] != 0 for route in routes)
        ),
        (),
    )
    if (
        replay_current_routes != current_routes
        or replay_preceding_routes != preceding_routes
        or replay_reached_and_foregone_routes != reached_and_foregone_routes
        # C-015 is already live-closed. Its transient witness is reported when
        # present but cannot become a recurring release gate that every later
        # physical predecessor must reproduce.
        or replay_working_continuations != working_continuations
        or replay_settled_working_frontier != settled_working_frontier
        or replay_prediction_alternatives != prediction_alternatives
        or replay_body_consequence_transfers != body_consequence_transfers
        or replay_affective_balance_trajectories
        != affective_balance_trajectories
        or replay_localized_fluid_chemistry != localized_fluid_chemistry
        or replay_localized_metabolic_strain_evaluated_lineages
        != localized_metabolic_strain_evaluated_lineages
        or replay_localized_metabolic_strain != localized_metabolic_strain
        or replay_successor != successor
        or replay_articulation != articulation
        or replay_before.state_sha256 != before.state_sha256
        or replay_after.state_sha256 != after.state_sha256
        or after.identity != before.identity
        or after.organism_tick != before.organism_tick + len(steps)
        or prepared.dsf_delivery_count <= 0
        or prepared.physically_transitioned_neuron_count <= 0
        or after.python_callback_count != 0
    ):
        raise RuntimeError(
            "ordinary body trajectory did not replay its exact native evidence"
        )
    reached = tuple(route for route in qualifying if route[7] != 0)
    foregone = tuple(route for route in qualifying if route[7] == 0)
    downstream = {route[3] for route in reached}
    complete_affective_balance_trajectories = tuple(
        trajectory
        for trajectory in affective_balance_trajectories
        if trajectory[3] is not None
        and trajectory[4] is not None
        and trajectory[5] is not None
        and trajectory[5][0] > max(trajectory[3][0], trajectory[4][0])
    )
    localized_fluid_witnesses = tuple(
        settlement
        for settlement in localized_fluid_chemistry
        if settlement[4][4] + settlement[4][5] > 0
        and settlement[4][6] == 0
    )
    return {
        "affective_balance_complete_trajectory_count": len(
            complete_affective_balance_trajectories
        ),
        "affective_balance_cold_replay_exact": True,
        "affective_balance_trajectory_count": len(
            affective_balance_trajectories
        ),
        "affective_balance_trajectories_sha256": hashlib.sha256(
            _canonical(affective_balance_trajectories)
        ).hexdigest(),
        "localized_fluid_chemistry_cold_replay_exact": True,
        "localized_fluid_chemistry_count": len(localized_fluid_chemistry),
        "localized_fluid_chemistry_sha256": hashlib.sha256(
            _canonical(localized_fluid_chemistry)
        ).hexdigest(),
        "localized_fluid_reached_unreached_witness_count": len(
            localized_fluid_witnesses
        ),
        "localized_metabolic_strain_cold_replay_exact": True,
        "localized_metabolic_strain_evaluated_lineage_count": len(
            localized_metabolic_strain_evaluated_lineages
        ),
        "localized_metabolic_strain_evaluated_lineages_sha256": hashlib.sha256(
            _canonical(localized_metabolic_strain_evaluated_lineages)
        ).hexdigest(),
        "localized_metabolic_strain_nonzero_count": len(
            localized_metabolic_strain
        ),
        "localized_metabolic_strain_sha256": hashlib.sha256(
            _canonical(localized_metabolic_strain)
        ).hexdigest(),
        "sparse_attention_cold_replay_exact": True,
        "native_articulation": articulation,
        "native_articulation_cold_replay_exact": True,
        "sparse_attention_current_route_count": len(current_routes),
        "sparse_attention_current_routes_sha256": hashlib.sha256(
            _canonical(current_routes)
        ).hexdigest(),
        "sparse_attention_dsf_delivery_count": prepared.dsf_delivery_count,
        "sparse_attention_downstream_neuron_count": len(downstream),
        "sparse_attention_foregone_route_count": len(foregone),
        "sparse_attention_interval_count": len(steps),
        "sparse_attention_physically_transitioned_neuron_count": (
            prepared.physically_transitioned_neuron_count
        ),
        "sparse_attention_preceding_route_count": len(preceding_routes),
        "sparse_attention_preceding_routes_sha256": hashlib.sha256(
            _canonical(preceding_routes)
        ).hexdigest(),
        "sparse_attention_qualifying_route_count": len(qualifying),
        "sparse_attention_qualifying_routes_sha256": hashlib.sha256(
            _canonical(qualifying)
        ).hexdigest(),
        "sparse_attention_reached_route_count": len(reached),
        "sparse_attention_rehearsed": bool(
            qualifying and preceding_routes and current_routes != preceding_routes
        ),
        "sparse_attention_state_byte_delta": after.state_bytes - before.state_bytes,
        "sparse_attention_successor_state_sha256": after.state_sha256,
        "working_causal_continuation_count": len(working_continuations),
        "working_causal_continuation_sha256": hashlib.sha256(
            _canonical(working_continuations)
        ).hexdigest(),
        "working_causal_settlement_count": len(settled_working_frontier),
        "working_causal_settlement_sha256": hashlib.sha256(
            _canonical(settled_working_frontier)
        ).hexdigest(),
        "physical_prediction_alternative_count": len(prediction_alternatives),
        "physical_prediction_alternatives_sha256": hashlib.sha256(
            _canonical(prediction_alternatives)
        ).hexdigest(),
        "body_consequence_transfer_count": len(body_consequence_transfers),
        "body_consequence_transfers_sha256": hashlib.sha256(
            _canonical(body_consequence_transfers)
        ).hexdigest(),
    }


def _rehearse_articulation_and_self_hearing(
    organism: object,
    prepared: object,
    trajectory: object | None = None,
) -> dict[str, object] | None:
    """Run only a reached layer-13 discharge through body and cochlear return."""

    recruitments = tuple(prepared.articulatory_unit_recruitments)
    if not recruitments:
        return None
    if trajectory is None:
        trajectory = _exact_articulatory_trajectory_or_none(recruitments)
    if trajectory is None:
        return None
    (
        sample_rate_hz,
        pressure_pcm,
        articulatory_body_trajectories,
        peak_breath_flow_pcm,
        glottal_open_samples_at_apex,
        mouth_area_square_millimetres_at_apex,
        perioral_area_displacement_square_millimetres,
        applied_motor_quanta,
        stalled_motor_quanta,
        relaxation_sample_count,
    ) = trajectory
    # Import only the current native transport builder. It creates physical
    # source episodes; it does not start the HTTP app or another runtime.
    from dsf_ai_service.native_production_app import _mono_pcm_hop_episodes

    self_hearing_start_tick = organism.readiness().organism_tick
    episodes = tuple(_mono_pcm_hop_episodes(
        assembly_prefix=f"c020-cold-self-hearing-{self_hearing_start_tick}",
        samples=pressure_pcm,
        sample_rate_hz=sample_rate_hz,
        articulatory_body=articulatory_body_trajectories,
    ))
    hop_count = len(episodes)
    if not episodes:
        raise RuntimeError("articulatory pressure produced no self-hearing interval")
    heard = _commit_unsealed_sources(organism, episodes)
    transitioned = heard.physically_transitioned_neuron_count
    fractals = heard.complete_neuron_fractal_count
    body_perturbed = heard.externally_perturbed_body_receptor_count
    return {
        "applied_motor_quanta": applied_motor_quanta,
        "glottal_open_samples_at_apex": glottal_open_samples_at_apex,
        "layer_13_recruitment_count": len(recruitments),
        "mouth_area_square_millimetres_at_apex": (
            mouth_area_square_millimetres_at_apex
        ),
        "peak_breath_flow_pcm": peak_breath_flow_pcm,
        "perioral_area_displacement_square_millimetres": (
            perioral_area_displacement_square_millimetres
        ),
        "pressure_sample_count": len(pressure_pcm),
        "pressure_sha256": hashlib.sha256(
            b"".join(int(value).to_bytes(2, "little", signed=True) for value in pressure_pcm)
        ).hexdigest(),
        "relaxation_sample_count": relaxation_sample_count,
        "sample_rate_hz": sample_rate_hz,
        "self_hearing_fractal_count": fractals,
        "self_hearing_hop_count": hop_count,
        "self_hearing_transitioned_neuron_count": transitioned,
        "articulatory_body_port_count": 4,
        "articulatory_body_receptor_ingress_count": 4 * hop_count,
        "articulatory_body_perturbed_neuron_count": body_perturbed,
        "stalled_motor_quanta": stalled_motor_quanta,
    }


def _stable_contact_key(
    first_lineage: str,
    second_lineage: str,
    parallel_ordinal: int,
) -> tuple[str, str, int]:
    if first_lineage < second_lineage:
        return first_lineage, second_lineage, parallel_ordinal
    return second_lineage, first_lineage, parallel_ordinal


def _first_nonzero_route_on_contacts(
    routes: tuple[tuple[object, ...], ...],
    contact_keys: frozenset[tuple[str, str, int]],
) -> tuple[object, ...] | None:
    for route in routes:
        if len(route) != 8:
            raise RuntimeError("A-011.6 physical frontier route shape changed")
        key = _stable_contact_key(str(route[0]), str(route[3]), int(route[6]))
        if key in contact_keys and int(route[7]) != 0:
            return route
    return None


def _rehearse_contact_local_junction(
    current_envelope: bytes,
    *,
    max_envelope_bytes: int,
    max_fabric_bytes: int,
    max_logical_peak_bytes: int,
) -> dict[str, object]:
    """Prove one real body cause changes and cold-restores one local contact."""

    budget = {
        "max_envelope_bytes": max_envelope_bytes,
        "max_fabric_bytes": max_fabric_bytes,
        "max_logical_peak_bytes": max_logical_peak_bytes,
    }
    organism = restore_native_resident_organism(
        current_envelope=current_envelope,
        **budget,
    )
    predecessor = tuple(organism.observe_reached_contact_channel_states())
    if not predecessor:
        raise RuntimeError("A-011.6 rehearsal found no reached sparse contact")
    _successor_heading, steps = exact_native_yaw_trajectory(
        predecessor_heading_millidegrees=0,
        signed_displacement_millidegrees=90_000,
        duration_microseconds=250_000,
    )
    if len(steps) != 250:
        raise RuntimeError("A-011.6 rehearsal body clock changed")
    changed: tuple[
        tuple[
            tuple[str, str, int, int, int, int, int, int],
            tuple[str, str, int, int, int, int, int, int],
        ],
        ...,
    ] = ()
    interval_ordinal = 0
    heading = 0
    for interval_ordinal, signed_step in enumerate(steps, 1):
        candidate = organism.prepare_vestibular_tick(heading, signed_step)
        organism.commit(candidate.token)
        heading = (heading + signed_step) % 360_000
        successor = tuple(organism.observe_reached_contact_channel_states())
        if tuple(row[:3] for row in successor) != tuple(
            row[:3] for row in predecessor
        ):
            raise RuntimeError("A-011.6 rehearsal changed contact identity")
        changed = tuple(
            (before, after)
            for before, after in zip(predecessor, successor, strict=True)
            if before[3:] != after[3:]
        )
        if changed:
            break
        predecessor = successor
    if not changed:
        raise RuntimeError(
            "A-011.6 real vestibular source produced no retained contact change"
        )
    changed_contact_keys = frozenset(
        _stable_contact_key(str(before[0]), str(before[1]), int(before[2]))
        for before, _after in changed
    )
    later_route: tuple[object, ...] | None = None
    later_interval_ordinal = 0
    for later_interval_ordinal, signed_step in enumerate(
        steps[interval_ordinal:], interval_ordinal + 1
    ):
        candidate = organism.prepare_vestibular_tick(heading, signed_step)
        later_route = _first_nonzero_route_on_contacts(
            tuple(candidate.physical_frontier_routes),
            changed_contact_keys,
        )
        organism.commit(candidate.token)
        heading = (heading + signed_step) % 360_000
        if later_route is not None:
            break
    if later_route is None:
        raise RuntimeError(
            "A-011.6 changed contact produced no later whole-carrier causal reach"
        )
    later_contact_key = _stable_contact_key(
        str(later_route[0]), str(later_route[3]), int(later_route[6])
    )
    later_outward_whole_carriers = int(later_route[7])
    successor_envelope = bytes(organism.save())
    cold = restore_native_resident_organism(
        current_envelope=successor_envelope,
        **budget,
    )
    cold_contacts = tuple(cold.observe_reached_contact_channel_states())
    live_contacts = tuple(organism.observe_reached_contact_channel_states())
    if cold_contacts != live_contacts:
        raise RuntimeError("A-011.6 changed contact did not cold-restore exactly")
    return {
        "a0116_contact_local_junction_rehearsed": True,
        "a0116_contact_local_interval_ordinal": interval_ordinal,
        "a0116_contact_count": len(live_contacts),
        "a0116_changed_contact_count": len(changed),
        "a0116_changed_contacts_sha256": hashlib.sha256(
            _canonical(changed)
        ).hexdigest(),
        "a0116_contact_state_sha256": hashlib.sha256(
            _canonical(live_contacts)
        ).hexdigest(),
        "a0116_successor_state_sha256": cold.readiness().state_sha256,
        "a0116_cold_restore_exact": True,
        "a0116_contact_later_causal_use_rehearsed": True,
        "a0116_contact_later_interval_ordinal": later_interval_ordinal,
        "a0116_later_causal_contact_sha256": hashlib.sha256(
            _canonical(later_contact_key)
        ).hexdigest(),
        "a0116_later_outward_whole_carriers": later_outward_whole_carriers,
    }


def _rehearse_a013_thermal_body(expected_identity: str) -> dict[str, object]:
    """Exercise the production heat circuit and native receptors once.

    The living predecessor remains read-only. A fresh bounded organism is
    used for the candidate-only receptor transition so the rehearsal neither
    clones nor scans the resident materialized brain. Live continuity stays
    under the ordinary CURRENT cold-restore gate above.
    """

    from dsf_ai_service import native_production_app as production
    from dsf_ai_service.glew_runtime.native_resident_organism import (
        create_native_resident_organism,
    )
    from dsf_ai_service.substrate.embodiment_world import (
        MoveCommand,
        PORT_ID,
        PoseMM,
        encode_command,
    )

    if production.THERMAL_PORT_COUNT != 2:
        raise RuntimeError("A-013 thermal rehearsal has no two-site anatomy")
    if os.environ.get("GUALA_NATIVE_ORGANISM_IDENTITY") != expected_identity:
        raise RuntimeError("A-013 thermal rehearsal identity is not pinned")
    prior_root = production.STATE_ROOT
    prior_world = production._world_authority
    try:
        with tempfile.TemporaryDirectory(prefix="guala-a013-thermal-") as name:
            production.STATE_ROOT = Path(name)
            production._world_authority = None
            world = production._world()
            before_world = world.observation_snapshot()
            before_thermal = world.thermal_observation()
            body = next(
                item
                for item in before_world.bodies
                if item.body_id == before_world.self_body_id
            )
            execution = world.execute_port_command(
                port_id=PORT_ID,
                command_payload=encode_command(
                    MoveCommand(
                        target_pose=PoseMM(body.pose.position, 90_000),
                        duration_microseconds=1_000,
                    )
                ),
                causal_intent_receipt_sha256=hashlib.sha256(
                    b"guala-a013-thermal-candidate-rehearsal"
                ).hexdigest(),
                expected_revision=before_world.revision,
            )
            organism = create_native_resident_organism(
                organism_identity=expected_identity,
                organism_tick=0,
                growth_dna=production._authored_growth_dna(),
                max_envelope_bytes=_A013_FRESH_MAX_ENVELOPE_BYTES,
                max_fabric_bytes=_A013_FRESH_MAX_FABRIC_BYTES,
                max_logical_peak_bytes=_A013_FRESH_MAX_LOGICAL_PEAK_BYTES,
            )
            episode, admissions, lanes = production._action_consequence_episode(
                execution,
                retinal_body_axes=organism.readiness().articulated_body_axes,
            )
            unsealed = organism.begin_unsealed_intake_direct(
                (episode,), (admissions,)
            )
            evidence = organism.finalize_unsealed_intake_direct(unsealed.token)
            organism.acknowledge_direct_commit(evidence.token)
            hop = production._resident_prepare_hop(
                evidence, organism.readiness()
            )
            reached = tuple(
                organism.observe_reached_source_site_count(
                    production.THERMAL_SENSOR_ID,
                    f"temperature-{channel}",
                )
                for channel in production.THERMAL_CHANNELS
            )
            hot_organism = organism.readiness()
            successor_envelope = bytes(organism.save())
            cold_organism = restore_native_resident_organism(
                current_envelope=successor_envelope,
                max_envelope_bytes=_A013_FRESH_MAX_ENVELOPE_BYTES,
                max_fabric_bytes=_A013_FRESH_MAX_FABRIC_BYTES,
                max_logical_peak_bytes=_A013_FRESH_MAX_LOGICAL_PEAK_BYTES,
            )
            cold_organism_state = cold_organism.readiness()
            after_thermal = world.thermal_observation()
            production._persist_world(world)
            hot_world = world.encoded_snapshot()
            production._world_authority = None
            cold_world = production._world()
            cold_thermal = cold_world.thermal_observation()
            cold_world_exact = cold_world.encoded_snapshot() == hot_world
    finally:
        production.STATE_ROOT = prior_root
        production._world_authority = prior_world

    if (
        execution.reason != "applied"
        or episode.python_callback_count != 0
        or episode.port_count != 111
        or episode.source_sample_count != 222
        or lanes.get("thermal")
        != {
            "changed": 1,
            "sensor_id": production.THERMAL_SENSOR_ID,
            "transported": 2,
        }
        or hop["dsf_delivery_count"] <= 0
        or hop["receptor_ingress_sense_counts"].get("body") != 84
        or reached != (1, 1)
        or hot_organism.identity != expected_identity
        or cold_organism_state.identity != hot_organism.identity
        or cold_organism_state.organism_tick != hot_organism.organism_tick
        or cold_organism_state.state_sha256 != hot_organism.state_sha256
        or tuple(cold_organism_state.articulated_body_axes)
        != tuple(hot_organism.articulated_body_axes)
        or cold_organism_state.articulated_body_proprioception_initialized is not True
        or cold_organism_state.python_callback_count != 0
        or len(successor_envelope) != hot_organism.state_bytes
        or hashlib.sha256(successor_envelope).hexdigest()
        != hot_organism.state_sha256
        or before_thermal.latest_transition_receipt_sha256 is not None
        or after_thermal.latest_transition_receipt_sha256 is None
        or after_thermal.world_revision != before_thermal.world_revision + 1
        or cold_thermal != after_thermal
        or not cold_world_exact
    ):
        raise RuntimeError("A-013 thermal body rehearsal changed")
    return {
        "a013_thermal_body_rehearsed": True,
        "a013_thermal_body_world_revision_before": before_thermal.world_revision,
        "a013_thermal_body_world_revision_after": after_thermal.world_revision,
        "a013_thermal_body_receptor_count": sum(reached),
        "a013_thermal_body_reached_site_counts": reached,
        "a013_thermal_body_episode_port_count": episode.port_count,
        "a013_thermal_body_episode_sample_count": episode.source_sample_count,
        "a013_thermal_body_dsf_delivery_count": hop["dsf_delivery_count"],
        "a013_thermal_body_transition_receipt_sha256": (
            after_thermal.latest_transition_receipt_sha256
        ),
        "a013_thermal_body_anatomy_receipt_sha256": (
            after_thermal.anatomy_receipt_sha256
        ),
        "a013_thermal_body_world_state_sha256": hashlib.sha256(
            hot_world
        ).hexdigest(),
        "a013_thermal_body_cold_restore_exact": True,
        "a013_fresh_complete_roster_cold_restore_exact": True,
        "a013_fresh_complete_roster_state_sha256": (
            cold_organism_state.state_sha256
        ),
        "a013_thermal_body_python_callback_count": 0,
    }


def _exact_articulatory_trajectory_or_none(
    recruitments: tuple[tuple[object, int, int, object], ...],
) -> object | None:
    """Translate the native body's exact antagonist cancellation, and only it."""

    try:
        return exact_articulatory_unit_trajectory(
            recruitments=tuple(
                (topology_index, carriers)
                for _lineage, topology_index, carriers, _transfers in recruitments
            )
        )
    except ValueError as error:
        if error.args == ("CancelledRecruitment",):
            return None
        raise


def _rehearse_native_articulation_source(
    current_envelope: bytes,
    budget: dict[str, int],
) -> dict[str, object]:
    """Cold-replay the smallest real layer-13 source and its sensory return.

    C-014's 250 ms sparse-attention evidence is already live-closed. C-020
    follows that ordinary body's exact 1 ms intervals only through its first
    real layer-13 discharge, then exercises articulation plus acoustic and
    local body-receptor return. The causal prefix depends on retained physical
    state; neither one fixed interval nor the whole historical trajectory is
    made an artificial prerequisite.
    """

    _successor_heading, steps = exact_native_yaw_trajectory(
        predecessor_heading_millidegrees=0,
        signed_displacement_millidegrees=90_000,
        duration_microseconds=250_000,
    )
    if len(steps) != 250:
        raise RuntimeError("native articulation source changed its ordinary body clock")

    def settle(
        replay_source_steps: tuple[int, ...] | None = None,
    ) -> tuple[
        object,
        object,
        object,
        object,
        bytes,
        dict[str, object],
        int,
        int,
        int,
        tuple[int, ...],
    ]:
        organism = restore_native_resident_organism(
            current_envelope=current_envelope,
            **budget,
        )
        before = organism.readiness()
        if replay_source_steps is None:
            heading = 0
            source_dsf_deliveries = 0
            source_physical_transitions = 0
            prepared = None
            after_source = None
            articulation_trajectory = None
            source_interval_count = 0
            for source_interval_count, signed_step in enumerate(steps, 1):
                candidate = organism.prepare_vestibular_tick(heading, signed_step)
                after_candidate = organism.commit(candidate.token)
                source_dsf_deliveries += candidate.dsf_delivery_count
                source_physical_transitions += (
                    candidate.physically_transitioned_neuron_count
                )
                heading = (heading + signed_step) % 360_000
                if candidate.articulatory_unit_recruitments:
                    candidate_trajectory = _exact_articulatory_trajectory_or_none(
                        tuple(candidate.articulatory_unit_recruitments)
                    )
                    if candidate_trajectory is not None:
                        prepared = candidate
                        after_source = after_candidate
                        articulation_trajectory = candidate_trajectory
                        break
            if prepared is None or after_source is None:
                raise RuntimeError("ordinary native source produced no articulation")
            source_steps = steps[:source_interval_count]
        else:
            if not replay_source_steps or len(replay_source_steps) > len(steps):
                raise RuntimeError("native articulation replay prefix is invalid")
            prepared = organism.prepare_vestibular_trajectory(
                0,
                replay_source_steps,
            )
            after_source = organism.commit(prepared.token)
            if not prepared.articulatory_unit_recruitments:
                raise RuntimeError("native articulation replay lost its discharge")
            articulation_trajectory = _exact_articulatory_trajectory_or_none(
                tuple(prepared.articulatory_unit_recruitments)
            )
            if articulation_trajectory is None:
                raise RuntimeError("native articulation replay cancelled its discharge")
            source_interval_count = len(replay_source_steps)
            source_dsf_deliveries = prepared.dsf_delivery_count
            source_physical_transitions = (
                prepared.physically_transitioned_neuron_count
            )
            source_steps = replay_source_steps
        articulation = _rehearse_articulation_and_self_hearing(
            organism,
            prepared,
            articulation_trajectory,
        )
        if articulation is None:
            raise RuntimeError("native discharge produced no articulation")
        successor = organism.save()
        after_return = organism.readiness()
        return (
            before,
            prepared,
            after_source,
            after_return,
            successor,
            articulation,
            source_interval_count,
            source_dsf_deliveries,
            source_physical_transitions,
            source_steps,
        )

    (
        before,
        prepared,
        after_source,
        after_return,
        successor,
        articulation,
        source_interval_count,
        source_dsf_deliveries,
        source_physical_transitions,
        source_steps,
    ) = settle()
    (
        replay_before,
        replay_prepared,
        replay_after_source,
        replay_after_return,
        replay_successor,
        replay_articulation,
        replay_source_interval_count,
        replay_source_dsf_deliveries,
        replay_source_physical_transitions,
        replay_source_steps,
    ) = settle(source_steps)
    recruitments = tuple(prepared.articulatory_unit_recruitments)
    replay_recruitments = tuple(replay_prepared.articulatory_unit_recruitments)
    if (
        source_dsf_deliveries <= 0
        or source_physical_transitions <= 0
        or not recruitments
        or after_source.identity != before.identity
        or after_source.organism_tick
        != before.organism_tick + source_interval_count
        or after_return.identity != before.identity
        or after_return.organism_tick
        != after_source.organism_tick + articulation["self_hearing_hop_count"]
        or after_return.python_callback_count != 0
        or replay_before.state_sha256 != before.state_sha256
        or replay_source_interval_count != source_interval_count
        or replay_source_dsf_deliveries != source_dsf_deliveries
        or replay_source_physical_transitions != source_physical_transitions
        or replay_source_steps != source_steps
        or replay_recruitments != recruitments
        or replay_after_source.state_sha256 != after_source.state_sha256
        or replay_after_return.state_sha256 != after_return.state_sha256
        or replay_articulation != articulation
        or replay_successor != successor
    ):
        raise RuntimeError("native articulation source did not cold-replay exactly")
    return {
        "native_articulation": articulation,
        "native_articulation_cold_replay_exact": True,
        "native_articulation_rehearsal_successor_state_sha256": (
            after_return.state_sha256
        ),
        "native_articulation_source_dsf_delivery_count": (
            source_dsf_deliveries
        ),
        "native_articulation_source_available_interval_count": len(steps),
        "native_articulation_source_interval_count": source_interval_count,
        "native_articulation_source_layer_13_recruitment_count": len(
            recruitments
        ),
        "native_articulation_source_physically_transitioned_neuron_count": (
            source_physical_transitions
        ),
        "native_articulation_source_state_byte_delta": (
            after_source.state_bytes - before.state_bytes
        ),
        "native_articulation_source_successor_state_sha256": (
            after_source.state_sha256
        ),
    }


def _rehearse_ordered_trajectory_projection(
    current_envelope: bytes,
    formation_members: tuple[str, ...],
    budget: dict[str, int],
) -> dict[str, int | bool | str]:
    """Prove a multi-interval native transaction does not lose later order."""

    def settle() -> tuple[object, object, dict[str, object] | None]:
        candidate = restore_native_resident_organism(
            current_envelope=current_envelope,
            **budget,
        )
        prepared = candidate.prepare_vestibular_trajectory(0, (-64, -64, -64, -64))
        relation = _commit_and_observe_episodic_relation(
            candidate,
            prepared,
            formation_members,
        )
        return candidate, prepared, relation

    candidate, prepared, relation = settle()
    replay, replay_prepared, replay_relation = settle()
    if (
        prepared.partial_cue_reassembly_count <= 0
        or relation is None
        or relation["ordered_path_relation_count"] <= 0
        or replay_prepared.partial_cue_reassembly_count <= 0
        or replay_relation != relation
        or replay.save() != candidate.save()
    ):
        raise RuntimeError("native trajectory projection lost ordered relation")
    return {
        "ordered_trajectory_projection_rehearsed": True,
        "ordered_trajectory_path_count": relation["ordered_physical_path_count"],
        "ordered_trajectory_paths_sha256": relation[
            "ordered_physical_paths_sha256"
        ],
        "ordered_trajectory_path_relation_count": relation[
            "ordered_path_relation_count"
        ],
        "ordered_trajectory_path_relations_sha256": relation[
            "ordered_path_relations_sha256"
        ],
        "ordered_trajectory_successor_state_sha256": candidate.readiness().state_sha256,
    }


def _commit_and_observe_episodic_relation(
    organism: object,
    prepared: object,
    recalled_members: tuple[str, ...],
) -> dict[str, int | str | tuple[str, ...]] | None:
    """Resolve one current relation against its exact retained successor."""

    relations = prepared.organic_mosaic_relations
    organism.commit(prepared.token)
    if not relations:
        return None
    formations = organism.observe_retained_formation_structures()
    by_receipt = {
        receipt: tuple(members)
        for receipt, members, _original, _recurrent, _reinforcements in formations
    }
    recalled_receipts = [
        receipt
        for receipt, members in by_receipt.items()
        if members == tuple(recalled_members)
    ]
    if len(recalled_receipts) != 1:
        return None
    recalled_receipt = recalled_receipts[0]
    candidates = []
    for (
        receipts,
        shared_lineages,
        active_bonds,
        structure_receipt,
        ordered_physical_paths,
        ordered_path_relations,
    ) in relations:
        if (
            recalled_receipt not in receipts
            or len(receipts) < 2
            or any(receipt not in by_receipt for receipt in receipts)
            or (not shared_lineages and not active_bonds)
        ):
            continue
        member_sets = tuple(sorted(tuple(sorted(by_receipt[receipt])) for receipt in receipts))
        if len(set(member_sets)) != len(member_sets):
            continue
        candidates.append(
            (
                receipts,
                shared_lineages,
                active_bonds,
                member_sets,
                structure_receipt,
                ordered_physical_paths,
                ordered_path_relations,
            )
        )
    if len(candidates) != 1:
        return None
    (
        receipts,
        shared_lineages,
        active_bonds,
        member_sets,
        structure_receipt,
        ordered_physical_paths,
        ordered_path_relations,
    ) = candidates[0]
    return {
        "episodic_recalled_formation_receipt": recalled_receipt,
        "episodic_related_formation_count": len(receipts),
        "episodic_related_formation_receipts": tuple(receipts),
        "episodic_related_formation_receipts_sha256": hashlib.sha256(
            _canonical(receipts)
        ).hexdigest(),
        "episodic_related_member_sets_sha256": hashlib.sha256(
            _canonical(member_sets)
        ).hexdigest(),
        "episodic_relation_active_bond_count": len(active_bonds),
        "episodic_relation_active_bonds_sha256": hashlib.sha256(
            _canonical(active_bonds)
        ).hexdigest(),
        "episodic_relation_shared_lineage_count": len(shared_lineages),
        "ordered_physical_path_count": len(ordered_physical_paths),
        "ordered_physical_paths_sha256": hashlib.sha256(
            _canonical(ordered_physical_paths)
        ).hexdigest(),
        "ordered_path_relation_count": len(ordered_path_relations),
        "ordered_path_relations_sha256": hashlib.sha256(
            _canonical(ordered_path_relations)
        ).hexdigest(),
        "structural_relation_sha256": structure_receipt,
    }


def _observe_distributed_recognition(
    organism: object,
    prepared: object,
    formations: tuple[tuple[str, tuple[str, ...], bool, bool, int], ...],
) -> dict[str, int | bool | str | tuple[str, ...]] | None:
    """Observe one actual multisensory reassembly; never drive recognition."""

    if prepared.partial_cue_reassembly_count <= 0:
        return None
    layers = {
        lineage: layer
        for lineage, layer, _receptor in (
            organism.observe_reached_neuron_lineage_layers()
        )
    }
    neighbours: dict[str, set[str]] = {}
    for left, right, _ordinal in prepared.active_physical_bonds:
        neighbours.setdefault(left, set()).add(right)
        neighbours.setdefault(right, set()).add(left)
    unseen = set(neighbours)
    candidates = []
    while unseen:
        seed = min(unseen)
        component = {seed}
        frontier = deque([seed])
        unseen.remove(seed)
        while frontier:
            current = frontier.popleft()
            for neighbour in sorted(neighbours.get(current, ())):
                if neighbour not in component:
                    component.add(neighbour)
                    unseen.discard(neighbour)
                    frontier.append(neighbour)
        matching_receipts = sorted(
            receipt
            for receipt, members, _original, _recurrent, _reinforcements in formations
            if set(members).issubset(component)
        )
        participants = {
            "sensory": {lineage for lineage in component if layers[lineage] <= 5},
            "association": {lineage for lineage in component if layers[lineage] == 7},
            "retention": {lineage for lineage in component if layers[lineage] == 9},
            "body": {lineage for lineage in component if layers[lineage] in {5, 8}},
            "affective": {lineage for lineage in component if layers[lineage] == 10},
            "ordering": {lineage for lineage in component if layers[lineage] == 11},
        }
        if matching_receipts and all(participants.values()):
            candidates.append((component, matching_receipts, participants))
    if len(candidates) != 1:
        return None
    component, matching_receipts, participants = candidates[0]
    active_bonds = sorted(
        (left, right, ordinal)
        for left, right, ordinal in prepared.active_physical_bonds
        if left in component and right in component
    )
    return {
        "distributed_recognition_active_bond_count": len(active_bonds),
        "distributed_recognition_active_bond_sha256": hashlib.sha256(
            _canonical(active_bonds)
        ).hexdigest(),
        "distributed_recognition_active_neuron_count": len(component),
        "distributed_recognition_affective_neuron_count": len(
            participants["affective"]
        ),
        "distributed_recognition_association_neuron_count": len(
            participants["association"]
        ),
        "distributed_recognition_body_neuron_count": len(participants["body"]),
        "distributed_recognition_formation_count": len(matching_receipts),
        "distributed_recognition_formation_receipts_sha256": hashlib.sha256(
            _canonical(matching_receipts)
        ).hexdigest(),
        "distributed_recognition_formation_receipts": tuple(matching_receipts),
        "distributed_recognition_rehearsed": True,
        "distributed_recognition_retention_neuron_count": len(
            participants["retention"]
        ),
        "distributed_recognition_ordering_neuron_count": len(
            participants["ordering"]
        ),
        "distributed_recognition_sensory_neuron_count": len(
            participants["sensory"]
        ),
    }


def main() -> int:
    values = _arguments()
    if _SHA256.fullmatch(values.expected_state_sha256) is None:
        raise ValueError("expected state SHA-256 is not canonical")
    if _COMMIT.fullmatch(values.candidate_git_sha) is None:
        raise ValueError("candidate commit is not canonical")
    if _DIGEST.fullmatch(values.candidate_image_digest) is None:
        raise ValueError("candidate image digest is not canonical")
    admission = derive_native_resident_resource_admission(
        values.native_store_root
    )
    migration_authorized = os.environ.get(
        "GUALA_CURRENT_FORMAT_MIGRATION", "0"
    )
    if migration_authorized not in {"0", "1"}:
        raise ValueError("current-format migration authorization must be 0 or 1")
    migration_rehearsed = False
    migration_predecessor: str | None = None
    try:
        restored = restore_current_native_organism(
            values.native_store_root,
            max_envelope_bytes=admission.max_envelope_bytes,
            max_fabric_bytes=admission.max_fabric_bytes,
            max_logical_peak_bytes=admission.max_logical_peak_bytes,
        )
        if migration_authorized == "1":
            restored = rehearse_current_native_organism_current_format(
                values.native_store_root,
                max_envelope_bytes=admission.max_envelope_bytes,
                max_fabric_bytes=admission.max_fabric_bytes,
                max_logical_peak_bytes=admission.max_logical_peak_bytes,
            )
            migration_rehearsed = True
    except NativeOrganismBinaryStoreError:
        if migration_authorized != "1":
            raise
        restored = rehearse_current_native_organism_current_format(
            values.native_store_root,
            max_envelope_bytes=admission.max_envelope_bytes,
            max_fabric_bytes=admission.max_fabric_bytes,
            max_logical_peak_bytes=admission.max_logical_peak_bytes,
        )
        migration_rehearsed = True
    if migration_rehearsed:
        migration_predecessor = restored.pointer.predecessor_state_sha256
        if migration_predecessor is None:
            raise RuntimeError("current-format rehearsal lost its predecessor")
    before = restored.organism.readiness()
    after = restored.organism.readiness()
    motor_proof: dict[str, int | bool | str | tuple[str, ...]] = {
        "motor_action_rehearsed": False,
    }
    # C-023's motor/action trajectory is live-closed historical evidence. It
    # is not replayed for C-024 (RF-034/RF-040); this probe exercises only the
    # active observer plus invariant CURRENT continuity.
    source_advanced_after_baseline = before.organism_tick > values.expected_tick
    if (
        before.identity != values.expected_identity
        or before.organism_tick < values.expected_tick
        or (
            before.organism_tick == values.expected_tick
            and before.state_sha256 != values.expected_state_sha256
            and not migration_rehearsed
        )
        or after.identity != before.identity
        or after.organism_tick != before.organism_tick
        or before.state_sha256 != after.state_sha256
        or before.state_bytes != after.state_bytes
        or before.python_callback_count != 0
        or restored.pointer.identity != before.identity
        or restored.pointer.organism_tick != before.organism_tick
        or restored.pointer.state_sha256 != before.state_sha256
        or (
            migration_rehearsed
            and restored.pointer.predecessor_state_sha256
            != migration_predecessor
        )
    ):
        raise RuntimeError("native CURRENT cold restore changed")
    # A-013's mature-body transition was accepted and live-closed before this
    # release. Replaying it here makes every unrelated deployment perform a
    # full mature-organism successor transition. Current continuity is proved
    # above; the fresh exact action/consequence transaction remains below.
    thermal_body_proof = _rehearse_a013_thermal_body(before.identity)
    record = {
        "baseline_observed_state_sha256": values.expected_state_sha256,
        "baseline_observed_tick": values.expected_tick,
        "candidate_git_sha": values.candidate_git_sha,
        "candidate_image_digest": values.candidate_image_digest,
        "cold_restore_exact": True,
        "mode": "cold-restore",
        "current_format_migration_rehearsed": migration_rehearsed,
        "migration_predecessor_state_sha256": (
            migration_predecessor if migration_rehearsed else None
        ),
        "python_callback_count": 0,
        "python_cognition_workers_started": 0,
        "complete_neuron_count": before.complete_neuron_count,
        "developmental_resting_neuron_count": (
            before.developmental_resting_neuron_count
        ),
        "raw_glorun_current_only": True,
        "resident_state_bytes": before.state_bytes,
        "resident_state_sha256": before.state_sha256,
        "schema": PROOF_SCHEMA,
        "source_identity": before.identity,
        "source_advanced_after_baseline": source_advanced_after_baseline,
        "source_mount_read_only": True,
        "tick": before.organism_tick,
        **motor_proof,
        **thermal_body_proof,
    }
    proof = {
        **record,
        "receipt_sha256": hashlib.sha256(_canonical(record)).hexdigest(),
    }
    print(_canonical(proof).decode("ascii"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
