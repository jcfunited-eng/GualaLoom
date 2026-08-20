#!/usr/bin/env python3
"""Run one bounded migration, publication, or native CURRENT proof task."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import PurePosixPath
import re
import time


PROBE_FAMILY = "dsf-ai-native-candidate"
SOURCE_MOUNT = "/source/guala"
# The genesis rehearsal runs against the real production mount path (its
# throwaway state root lives beside, never inside, the real native-organism
# directory) so the candidate exercises the exact serving filesystem layout.
PRODUCTION_MOUNT = "/app/guala"
GENESIS_STORE_PREFIX = PRODUCTION_MOUNT + "/native-organism-rehearsal-"
EPHEMERAL_GIB = 30
_SHA = re.compile(r"[0-9a-f]{64}")
PROOF_SCHEMAS = {
    "rehearse": "guala.production_candidate_native_restore_rehearsal.v5",
    "publish": "guala.production_native_current_publication.v1",
    "cold-restore": "guala.production_native_current_cold_restore.v8",
    "genesis-rehearse": "guala.genesis_rehearsal_proof.v1",
}


def mounted_native_store(environment: list[dict[str, object]]) -> str:
    """Map the inherited live body root onto the read-only probe mount.

    The body generation is deliberately not named here.  The candidate task
    inherits the exact live ``GUALA_NATIVE_ORGANISM_ROOT`` and the probe sees
    the same EFS volume at ``/source/guala`` instead of ``/app/guala``.
    """

    values = [
        item.get("value")
        for item in environment
        if item.get("name") == "GUALA_NATIVE_ORGANISM_ROOT"
    ]
    if len(values) != 1 or not isinstance(values[0], str):
        raise RuntimeError("candidate declares no single live organism root")
    declared = PurePosixPath(values[0])
    production_mount = PurePosixPath(PRODUCTION_MOUNT)
    if not declared.is_absolute() or ".." in declared.parts:
        raise RuntimeError("candidate organism root escapes the production mount")
    try:
        relative = declared.relative_to(production_mount)
    except ValueError as error:
        raise RuntimeError(
            "candidate organism root is outside the production mount"
        ) from error
    if not relative.parts:
        raise RuntimeError("candidate organism root names the whole production mount")
    return str(PurePosixPath(SOURCE_MOUNT).joinpath(relative))


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("rehearse", "publish", "cold-restore", "genesis-rehearse"),
        required=True,
    )
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--candidate-task-definition", required=True)
    parser.add_argument("--candidate-git-sha", required=True)
    parser.add_argument("--candidate-image-digest", required=True)
    parser.add_argument("--expected-baseline-generation")
    parser.add_argument("--expected-active-generation")
    parser.add_argument("--expected-identity", required=True)
    parser.add_argument("--expected-tick", type=int)
    parser.add_argument("--expected-state-sha256")
    parser.add_argument("--region", default="us-east-1")
    return parser.parse_args()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def probe_task_definition(
    source: dict[str, object],
    *,
    mode: str,
    candidate_git_sha: str,
    candidate_image_digest: str,
    expected_identity: str,
    expected_tick: int | None = None,
    expected_baseline_generation: str | None = None,
    expected_active_generation: str | None = None,
    expected_state_sha256: str | None = None,
    genesis_state_root: str | None = None,
) -> dict[str, object]:
    containers = source.get("containerDefinitions")
    if not isinstance(containers, list) or len(containers) != 1:
        raise RuntimeError("candidate task must contain one container")
    original = containers[0]
    if not isinstance(original, dict) or original.get("name") != "dsf-ai":
        raise RuntimeError("candidate container changed")
    environment = [
        item
        for item in original.get("environment", [])
        if isinstance(item, dict)
        and item.get("name")
        not in {
            "FORCE_S3_RESTORE",
            "GUALA_EXACT_FIELD_EXECUTOR_REQUIRED",
            "GUALA_GENERATION_STORE_ROOT",
            "GUALA_LIVE_RECOVERY_STORE_ROOT",
            "GUALA_OWNER_LOCK_PATH",
            "GUALA_REQUIRE_SEALED_STATE",
            "STATE_DIR",
        }
    ]
    native_store = (
        mounted_native_store(environment)
        if mode in {"publish", "cold-restore"}
        else None
    )
    if mode == "cold-restore":
        environment = [
            item
            for item in environment
            if item.get("name") != "GUALA_NATIVE_ORGANISM_ROOT"
        ]
        environment.append(
            {"name": "GUALA_NATIVE_ORGANISM_ROOT", "value": native_store}
        )
    if mode == "genesis-rehearse":
        if (
            not genesis_state_root
            or not genesis_state_root.startswith(GENESIS_STORE_PREFIX)
        ):
            raise ValueError(
                "genesis rehearsal requires a unique throwaway state root"
            )
        command = [
            "python3",
            "-m",
            "dsf_ai_service.candidate_release_rehearsal",
            "--mode",
            "genesis-rehearse",
            "--expected-identity",
            expected_identity,
            "--candidate-git-sha",
            candidate_git_sha,
            "--candidate-image-digest",
            candidate_image_digest,
        ]
        # The rehearsal's publications must stay inside the throwaway root:
        # without a remote bucket the app uses its local directory mirror, so
        # the shared production backup bucket is never written or retired by
        # a rehearsal (deterministic genesis could otherwise collide with the
        # real organism's content-addressed keys).
        environment = [
            item
            for item in environment
            if item.get("name")
            not in {"GUALA_NATIVE_ORGANISM_ROOT", "GUALA_S3_BACKUP_BUCKET"}
        ]
        environment.append(
            {"name": "GUALA_NATIVE_ORGANISM_ROOT", "value": genesis_state_root}
        )
    elif expected_tick is None:
        raise ValueError("migration task requires the exact source tick")
    elif mode == "cold-restore":
        if expected_state_sha256 is None:
            raise ValueError("cold restore requires expected state SHA-256")
        command = [
            "python3",
            "-m",
            "dsf_ai_service.cold_restore_probe",
            "--native-store-root",
            native_store,
            "--expected-identity",
            expected_identity,
            "--expected-tick",
            str(expected_tick),
            "--expected-state-sha256",
            expected_state_sha256,
            "--candidate-git-sha",
            candidate_git_sha,
            "--candidate-image-digest",
            candidate_image_digest,
        ]
    else:
        if expected_baseline_generation is None or expected_active_generation is None:
            raise ValueError("migration task requires exact generation identities")
        command = [
            "python3",
            "-m",
            "dsf_ai_service.candidate_release_rehearsal",
            "--mode",
            mode,
            "--source-root",
            SOURCE_MOUNT,
            "--expected-baseline-generation",
            expected_baseline_generation,
            "--expected-active-generation",
            expected_active_generation,
            "--expected-identity",
            expected_identity,
            "--expected-tick",
            str(expected_tick),
            "--candidate-git-sha",
            candidate_git_sha,
            "--candidate-image-digest",
            candidate_image_digest,
        ]
        if mode == "publish":
            command.extend(("--native-store-root", native_store))
    log_configuration = original.get("logConfiguration")
    if not isinstance(log_configuration, dict):
        raise RuntimeError("candidate log transport is absent")
    options = dict(log_configuration.get("options") or {})
    options["awslogs-stream-prefix"] = "guala-native-" + mode
    read_only = mode in {"rehearse", "cold-restore"}
    mount_path = PRODUCTION_MOUNT if mode == "genesis-rehearse" else SOURCE_MOUNT
    container = {
        "command": command,
        "environment": environment,
        "essential": True,
        "image": original.get("image"),
        "logConfiguration": {**log_configuration, "options": options},
        "mountPoints": [{
            "containerPath": mount_path,
            "readOnly": read_only,
            "sourceVolume": "gualaloom-state",
        }],
        "name": "dsf-ai",
        "secrets": original.get("secrets", []),
        "stopTimeout": 120,
    }
    keep = (
        "cpu",
        "executionRoleArn",
        "memory",
        "networkMode",
        "requiresCompatibilities",
        "runtimePlatform",
        "taskRoleArn",
        "volumes",
    )
    task = {name: source[name] for name in keep if name in source}
    task.update({
        "containerDefinitions": [container],
        "ephemeralStorage": {"sizeInGiB": EPHEMERAL_GIB},
        "family": PROBE_FAMILY + "-" + mode,
    })
    return task


def _validate_proof(
    proof: object,
    *,
    mode: str,
    candidate_git_sha: str,
    candidate_image_digest: str,
    expected_identity: str,
    expected_tick: int | None,
    expected_state_sha256: str | None,
    expected_state_root: str | None = None,
    expected_distributed_recall_rehearsal: bool = False,
    expected_sparse_attention_rehearsal: bool = False,
    expected_native_articulation_rehearsal: bool = False,
    expected_native_physical_rest_wake_rehearsal: bool = False,
    expected_native_internal_consolidation_rehearsal: bool = False,
    expected_native_causal_cross_context_rehearsal: bool = False,
    expected_a013_articulated_body_rehearsal: bool = False,
) -> dict[str, object]:
    if not isinstance(proof, dict):
        raise RuntimeError("native candidate proof is not an object")
    receipt = proof.get("receipt_sha256")
    record = dict(proof)
    record.pop("receipt_sha256", None)
    if mode == "genesis-rehearse":
        counts = (
            proof.get("complete_neuron_fractal_count"),
            proof.get("physically_transitioned_neuron_count"),
        )
        receipts = (
            proof.get("genesis_state_sha256"),
            proof.get("post_teach_state_sha256"),
        )
        if (
            proof.get("schema") != PROOF_SCHEMAS[mode]
            or proof.get("mode") != mode
            or proof.get("candidate_git_sha") != candidate_git_sha
            or proof.get("candidate_image_digest") != candidate_image_digest
            or proof.get("identity") != expected_identity
            or proof.get("python_callback_count") != 0
            or proof.get("python_cognition_workers_started") != 0
            or not isinstance(proof.get("taught_card_id"), str)
            or not proof["taught_card_id"]
            or any(
                not isinstance(count, int)
                or isinstance(count, bool)
                or count <= 0
                for count in counts
            )
            or any(
                not isinstance(value, str) or _SHA.fullmatch(value) is None
                for value in receipts
            )
            or proof["post_teach_state_sha256"] == proof["genesis_state_sha256"]
            or (
                expected_state_root is not None
                and proof.get("state_root") != expected_state_root
            )
            or receipt != hashlib.sha256(_canonical(record)).hexdigest()
        ):
            raise RuntimeError("native candidate proof changed")
        return proof
    actual_tick = proof.get("tick")
    actual_state_sha256 = proof.get("resident_state_sha256")
    source_advanced = (
        isinstance(actual_tick, int)
        and not isinstance(actual_tick, bool)
        and expected_tick is not None
        and actual_tick > expected_tick
    )
    migration_predecessor = proof.get("migration_predecessor_state_sha256")
    current_format_migration = (
        mode == "cold-restore"
        and proof.get("current_format_migration_rehearsed") is True
        and isinstance(migration_predecessor, str)
        and _SHA.fullmatch(migration_predecessor) is not None
        and (
            source_advanced
            or migration_predecessor == expected_state_sha256
        )
    )
    distributed_recognition_rehearsal = (
        proof.get("distributed_recognition_rehearsed") is True
        and all(
            isinstance(proof.get(name), int)
            and not isinstance(proof[name], bool)
            and proof[name] > 0
            for name in (
                "distributed_recognition_active_bond_count",
                "distributed_recognition_active_neuron_count",
                "distributed_recognition_affective_neuron_count",
                "distributed_recognition_association_neuron_count",
                "distributed_recognition_body_neuron_count",
                "distributed_recognition_formation_count",
                "distributed_recognition_ordering_neuron_count",
                "distributed_recognition_retention_neuron_count",
                "distributed_recognition_sensory_neuron_count",
                "distributed_recognition_source_dsf_delivery_count",
                "distributed_recognition_source_hop_count",
                "distributed_recognition_source_physical_transition_count",
            )
        )
        and isinstance(proof.get("distributed_recognition_episode_ordinal"), int)
        and not isinstance(proof["distributed_recognition_episode_ordinal"], bool)
        and proof["distributed_recognition_episode_ordinal"] >= 0
        and proof["distributed_recognition_episode_ordinal"]
        < proof["distributed_recognition_source_hop_count"]
        and isinstance(proof.get("distributed_recognition_state_byte_delta"), int)
        and not isinstance(proof["distributed_recognition_state_byte_delta"], bool)
        and isinstance(proof.get("complete_neuron_count"), int)
        and proof["distributed_recognition_active_neuron_count"]
        <= proof["complete_neuron_count"]
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "distributed_recognition_active_bond_sha256",
                "distributed_recognition_formation_receipts_sha256",
                "distributed_recognition_successor_state_sha256",
            )
        )
    )
    distributed_recall_rehearsal = (
        distributed_recognition_rehearsal
        and proof.get("distributed_recall_rehearsed") is True
        and proof.get("motor_action_rehearsed") is False
        and isinstance(proof.get("distributed_recall_cue_lineage"), str)
        and re.fullmatch(r"[0-9a-f]{32}", proof["distributed_recall_cue_lineage"])
        is not None
        and isinstance(proof.get("distributed_recall_formation_member_count"), int)
        and not isinstance(proof["distributed_recall_formation_member_count"], bool)
        and proof["distributed_recall_formation_member_count"] >= 3
        and isinstance(proof.get("distributed_recall_interval_ordinal"), int)
        and not isinstance(proof["distributed_recall_interval_ordinal"], bool)
        and 1
        <= proof["distributed_recall_interval_ordinal"]
        <= proof["distributed_recognition_source_hop_count"]
        and isinstance(proof.get("distributed_recall_source_dsf_delivery_count"), int)
        and proof["distributed_recall_source_dsf_delivery_count"] > 0
        and isinstance(
            proof.get("distributed_recall_source_physical_transition_count"), int
        )
        and proof["distributed_recall_source_physical_transition_count"] > 0
        and isinstance(proof.get("distributed_recall_state_byte_delta"), int)
        and isinstance(proof.get("distributed_recall_successor_state_sha256"), str)
        and _SHA.fullmatch(proof["distributed_recall_successor_state_sha256"])
        is not None
        and isinstance(proof.get("distributed_recognition_formation_receipts"), list)
        and len(proof["distributed_recognition_formation_receipts"])
        == proof["distributed_recognition_formation_count"]
        and hashlib.sha256(
            _canonical(proof["distributed_recognition_formation_receipts"])
        ).hexdigest()
        == proof["distributed_recognition_formation_receipts_sha256"]
    )
    ordered_trajectory_projection_rehearsal = (
        distributed_recall_rehearsal
        and proof.get("ordered_trajectory_projection_rehearsed") is True
        and isinstance(proof.get("ordered_trajectory_path_count"), int)
        and not isinstance(proof["ordered_trajectory_path_count"], bool)
        and proof["ordered_trajectory_path_count"] > 0
        and isinstance(proof.get("ordered_trajectory_path_relation_count"), int)
        and not isinstance(proof["ordered_trajectory_path_relation_count"], bool)
        and proof["ordered_trajectory_path_relation_count"] > 0
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "ordered_trajectory_paths_sha256",
                "ordered_trajectory_path_relations_sha256",
                "ordered_trajectory_successor_state_sha256",
            )
        )
    )
    episodic_memory_rehearsal = (
        ordered_trajectory_projection_rehearsal
        and proof.get("episodic_memory_rehearsed") is True
        and proof.get("episodic_cold_reassembly_exact") is True
        and proof.get("episodic_complete_source_replayed") is False
        and proof.get("episodic_archive_lookup_count") == 0
        and proof.get("ordered_physical_cold_reassembly") is True
        and isinstance(proof.get("ordered_physical_path_count"), int)
        and not isinstance(proof["ordered_physical_path_count"], bool)
        and proof["ordered_physical_path_count"] > 0
        and isinstance(proof.get("ordered_path_relation_count"), int)
        and not isinstance(proof["ordered_path_relation_count"], bool)
        and proof["ordered_path_relation_count"] > 0
        and isinstance(proof.get("episodic_relation_interval_ordinal"), int)
        and not isinstance(proof["episodic_relation_interval_ordinal"], bool)
        and 1
        <= proof["episodic_relation_interval_ordinal"]
        <= proof["distributed_recognition_source_hop_count"]
        and isinstance(proof.get("episodic_related_formation_count"), int)
        and not isinstance(proof["episodic_related_formation_count"], bool)
        and proof["episodic_related_formation_count"] >= 2
        and isinstance(proof.get("episodic_relation_active_bond_count"), int)
        and not isinstance(proof["episodic_relation_active_bond_count"], bool)
        and isinstance(proof.get("episodic_relation_shared_lineage_count"), int)
        and not isinstance(proof["episodic_relation_shared_lineage_count"], bool)
        and (
            proof["episodic_relation_active_bond_count"] > 0
            or proof["episodic_relation_shared_lineage_count"] > 0
        )
        and isinstance(proof.get("episodic_related_formation_receipts"), list)
        and len(proof["episodic_related_formation_receipts"])
        == proof["episodic_related_formation_count"]
        and isinstance(proof.get("episodic_recalled_formation_receipt"), str)
        and proof["episodic_recalled_formation_receipt"]
        in proof["episodic_related_formation_receipts"]
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "episodic_recalled_formation_receipt",
                "episodic_related_formation_receipts_sha256",
                "episodic_related_member_sets_sha256",
                "episodic_relation_active_bonds_sha256",
                "ordered_physical_paths_sha256",
                "ordered_path_relations_sha256",
                "structural_relation_sha256",
            )
        )
        and hashlib.sha256(
            _canonical(proof["episodic_related_formation_receipts"])
        ).hexdigest()
        == proof["episodic_related_formation_receipts_sha256"]
    )
    sparse_attention_rehearsal = (
        proof.get("sparse_attention_rehearsed") is True
        and proof.get("sparse_attention_cold_replay_exact") is True
        and isinstance(proof.get("sparse_attention_interval_count"), int)
        and not isinstance(proof["sparse_attention_interval_count"], bool)
        and proof["sparse_attention_interval_count"] > 1
        and isinstance(proof.get("sparse_attention_current_route_count"), int)
        and not isinstance(proof["sparse_attention_current_route_count"], bool)
        and proof["sparse_attention_current_route_count"] >= 0
        and isinstance(proof.get("sparse_attention_preceding_route_count"), int)
        and not isinstance(proof["sparse_attention_preceding_route_count"], bool)
        and proof["sparse_attention_preceding_route_count"] > 0
        and isinstance(proof.get("sparse_attention_qualifying_route_count"), int)
        and not isinstance(proof["sparse_attention_qualifying_route_count"], bool)
        and proof["sparse_attention_qualifying_route_count"] > 1
        and isinstance(proof.get("sparse_attention_reached_route_count"), int)
        and not isinstance(proof["sparse_attention_reached_route_count"], bool)
        and proof["sparse_attention_reached_route_count"] > 0
        and isinstance(proof.get("sparse_attention_foregone_route_count"), int)
        and not isinstance(proof["sparse_attention_foregone_route_count"], bool)
        and proof["sparse_attention_foregone_route_count"] > 0
        and proof["sparse_attention_reached_route_count"]
        + proof["sparse_attention_foregone_route_count"]
        == proof["sparse_attention_qualifying_route_count"]
        and isinstance(proof.get("sparse_attention_downstream_neuron_count"), int)
        and not isinstance(proof["sparse_attention_downstream_neuron_count"], bool)
        and 0
        < proof["sparse_attention_downstream_neuron_count"]
        <= proof["sparse_attention_reached_route_count"]
        and isinstance(proof.get("sparse_attention_dsf_delivery_count"), int)
        and not isinstance(proof["sparse_attention_dsf_delivery_count"], bool)
        and proof["sparse_attention_dsf_delivery_count"] > 0
        and isinstance(
            proof.get("sparse_attention_physically_transitioned_neuron_count"), int
        )
        and not isinstance(
            proof["sparse_attention_physically_transitioned_neuron_count"], bool
        )
        and proof["sparse_attention_physically_transitioned_neuron_count"] > 0
        and isinstance(proof.get("sparse_attention_state_byte_delta"), int)
        and not isinstance(proof["sparse_attention_state_byte_delta"], bool)
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "sparse_attention_current_routes_sha256",
                "sparse_attention_preceding_routes_sha256",
                "sparse_attention_qualifying_routes_sha256",
                "sparse_attention_successor_state_sha256",
            )
        )
        and proof["sparse_attention_current_routes_sha256"]
        != proof["sparse_attention_preceding_routes_sha256"]
    )
    articulation = proof.get("native_articulation")
    native_articulation_rehearsal = (
        proof.get("native_articulation_cold_replay_exact") is True
        and isinstance(articulation, dict)
        and set(articulation) == {
            "applied_motor_quanta",
            "articulatory_body_port_count",
            "articulatory_body_receptor_ingress_count",
            "articulatory_body_perturbed_neuron_count",
            "glottal_open_samples_at_apex",
            "layer_13_recruitment_count",
            "mouth_area_square_millimetres_at_apex",
            "peak_breath_flow_pcm",
            "perioral_area_displacement_square_millimetres",
            "pressure_sample_count",
            "pressure_sha256",
            "relaxation_sample_count",
            "sample_rate_hz",
            "self_hearing_fractal_count",
            "self_hearing_hop_count",
            "self_hearing_transitioned_neuron_count",
            "stalled_motor_quanta",
        }
        and all(
            isinstance(articulation.get(name), int)
            and not isinstance(articulation[name], bool)
            and articulation[name] > 0
            for name in (
                "applied_motor_quanta",
                "articulatory_body_port_count",
                "articulatory_body_receptor_ingress_count",
                "articulatory_body_perturbed_neuron_count",
                "glottal_open_samples_at_apex",
                "layer_13_recruitment_count",
                "mouth_area_square_millimetres_at_apex",
                "peak_breath_flow_pcm",
                "pressure_sample_count",
                "sample_rate_hz",
                "self_hearing_hop_count",
                "self_hearing_transitioned_neuron_count",
            )
        )
        and isinstance(
            articulation.get("perioral_area_displacement_square_millimetres"),
            int,
        )
        and not isinstance(
            articulation["perioral_area_displacement_square_millimetres"],
            bool,
        )
        and articulation["perioral_area_displacement_square_millimetres"] != 0
        and articulation["pressure_sample_count"] >= articulation["sample_rate_hz"]
        and articulation["articulatory_body_port_count"] == 4
        and articulation["articulatory_body_receptor_ingress_count"]
        == articulation["articulatory_body_port_count"]
        * articulation["self_hearing_hop_count"]
        and articulation["relaxation_sample_count"]
        == articulation["pressure_sample_count"] - articulation["sample_rate_hz"]
        and isinstance(articulation.get("self_hearing_fractal_count"), int)
        and not isinstance(articulation["self_hearing_fractal_count"], bool)
        and articulation["self_hearing_fractal_count"] >= 0
        and isinstance(articulation.get("stalled_motor_quanta"), int)
        and not isinstance(articulation["stalled_motor_quanta"], bool)
        and articulation["stalled_motor_quanta"] >= 0
        and isinstance(articulation.get("pressure_sha256"), str)
        and _SHA.fullmatch(articulation["pressure_sha256"]) is not None
        and isinstance(
            proof.get("native_articulation_source_dsf_delivery_count"), int
        )
        and not isinstance(
            proof["native_articulation_source_dsf_delivery_count"], bool
        )
        and proof["native_articulation_source_dsf_delivery_count"] > 0
        and isinstance(
            proof.get("native_articulation_source_physically_transitioned_neuron_count"),
            int,
        )
        and proof["native_articulation_source_physically_transitioned_neuron_count"]
        > 0
        and proof.get("native_articulation_source_available_interval_count") == 250
        and isinstance(proof.get("native_articulation_source_interval_count"), int)
        and not isinstance(proof["native_articulation_source_interval_count"], bool)
        and 1
        <= proof["native_articulation_source_interval_count"]
        <= proof["native_articulation_source_available_interval_count"]
        and proof.get("native_articulation_source_layer_13_recruitment_count")
        == articulation["layer_13_recruitment_count"]
        and isinstance(proof.get("native_articulation_source_state_byte_delta"), int)
        and not isinstance(
            proof["native_articulation_source_state_byte_delta"], bool
        )
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "native_articulation_source_successor_state_sha256",
                "native_articulation_rehearsal_successor_state_sha256",
            )
        )
    )
    exact_rest_pairs = (
        "native_rest_dissipated_energy_before_zeptojoules",
        "native_rest_dissipated_energy_after_zeptojoules",
        "native_rest_reachable_dissipation_headroom_before_zeptojoules",
        "native_rest_reachable_dissipation_headroom_after_zeptojoules",
    )
    exact_rest_values = {
        name: proof.get(name)
        for name in exact_rest_pairs
    }
    exact_rest_values_valid = all(
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(part, int) and not isinstance(part, bool) for part in value)
        and value[1] > 0
        for value in exact_rest_values.values()
    )
    native_physical_rest_wake_rehearsal = (
        proof.get("native_physical_rest_wake_rehearsed") is True
        and proof.get("native_physical_rest_wake_cold_replay_exact") is True
        and isinstance(proof.get("native_rest_interval_ordinal"), int)
        and not isinstance(proof["native_rest_interval_ordinal"], bool)
        and 1 <= proof["native_rest_interval_ordinal"] <= 16
        and all(
            isinstance(proof.get(name), int)
            and not isinstance(proof[name], bool)
            and proof[name] > 0
            for name in (
                "native_rest_recovered_neuron_count",
                "native_wake_dsf_delivery_count",
                "native_wake_physically_transitioned_neuron_count",
            )
        )
        and proof.get("native_rest_motor_recruitment_count") == 0
        and proof.get("native_rest_articulatory_recruitment_count") == 0
        and exact_rest_values_valid
        and Fraction(*exact_rest_values[
            "native_rest_dissipated_energy_after_zeptojoules"
        ])
        < Fraction(*exact_rest_values[
            "native_rest_dissipated_energy_before_zeptojoules"
        ])
        and Fraction(*exact_rest_values[
            "native_rest_reachable_dissipation_headroom_after_zeptojoules"
        ])
        > Fraction(*exact_rest_values[
            "native_rest_reachable_dissipation_headroom_before_zeptojoules"
        ])
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "native_rest_successor_state_sha256",
                "native_wake_successor_state_sha256",
            )
        )
    )
    native_internal_consolidation_rehearsal = (
        proof.get("native_internal_consolidation_rehearsed") is True
        and proof.get("native_internal_consolidation_cold_restore_exact") is True
        and proof.get("native_internal_consolidation_cold_replay_exact") is True
        and proof.get("native_internal_consolidation_source")
        == "local_metabolic_settlement"
        and proof.get("native_internal_consolidation_origin")
        == "internally_simulated"
        and isinstance(proof.get("native_internal_consolidation_interval_ordinal"), int)
        and not isinstance(proof["native_internal_consolidation_interval_ordinal"], bool)
        and 1 <= proof["native_internal_consolidation_interval_ordinal"] <= 32
        and all(
            isinstance(proof.get(name), int)
            and not isinstance(proof[name], bool)
            and proof[name] > 0
            for name in (
                "native_internal_consolidation_member_count",
                "native_internal_consolidation_cue_count",
                "native_internal_consolidation_formation_count",
                "native_internal_consolidation_metabolic_receptor_count",
                "native_internal_consolidation_recovered_neuron_count",
                "native_internal_consolidation_state_bytes_before",
                "native_internal_consolidation_state_bytes_after",
            )
        )
        and proof.get("native_internal_consolidation_external_receptor_count") == 0
        and all(
            isinstance(proof.get(name), int)
            and not isinstance(proof[name], bool)
            and proof[name] >= 0
            for name in (
                "native_internal_consolidation_motor_recruitment_count",
                "native_internal_consolidation_articulatory_recruitment_count",
            )
        )
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "native_internal_consolidation_formation_receipt_before",
                "native_internal_consolidation_formation_receipt_after",
                "native_internal_consolidation_state_sha256_before",
                "native_internal_consolidation_state_sha256_after",
            )
        )
        and proof.get("native_internal_consolidation_formation_receipt_before")
        != proof.get("native_internal_consolidation_formation_receipt_after")
        and proof.get("native_internal_consolidation_state_sha256_before")
        != proof.get("native_internal_consolidation_state_sha256_after")
    )
    native_causal_cross_context_rehearsal = (
        proof.get("native_causal_cross_context_use_rehearsed") is True
        and proof.get("native_causal_cross_context_cold_restore_exact") is True
        and proof.get("motor_action_rehearsed") is True
        and all(
            isinstance(proof.get(name), int)
            and not isinstance(proof[name], bool)
            and proof[name] > 0
            for name in (
                "native_causal_cross_context_transfer_count",
                "native_causal_cross_context_recurrence_tick",
                "native_causal_cross_context_motor_tick",
                "native_causal_cross_context_hop_count",
                "native_causal_cross_context_body_receptor_count",
                "native_causal_cross_context_vestibular_tick_count",
                "native_causal_cross_context_state_bytes_before",
                "native_causal_cross_context_state_bytes_after",
                "native_causal_cross_context_successor_tick",
            )
        )
        and isinstance(
            proof.get("native_causal_cross_context_signed_yaw_millidegrees"), int
        )
        and not isinstance(
            proof["native_causal_cross_context_signed_yaw_millidegrees"], bool
        )
        and proof["native_causal_cross_context_signed_yaw_millidegrees"] != 0
        and all(
            isinstance(proof.get(name), int)
            and not isinstance(proof[name], bool)
            and proof[name] >= 0
            for name in (
                "native_causal_cross_context_world_revision_before",
                "native_causal_cross_context_world_revision_after",
            )
        )
        and proof.get("native_causal_cross_context_world_revision_after")
        == proof.get("native_causal_cross_context_world_revision_before") + 1
        and proof["native_causal_cross_context_recurrence_tick"]
        < proof["native_causal_cross_context_motor_tick"]
        < proof["native_causal_cross_context_successor_tick"]
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "native_causal_cross_context_formation_receipt",
                "native_causal_cross_context_state_sha256_before",
                "native_causal_cross_context_state_sha256_after",
            )
        )
        and proof.get("native_causal_cross_context_state_sha256_before")
        != proof.get("native_causal_cross_context_state_sha256_after")
    )
    a013_articulated_body_rehearsal = (
        proof.get("a013_articulated_body_rehearsed") is True
        and isinstance(actual_tick, int)
        and not isinstance(actual_tick, bool)
        and proof.get("a013_articulated_body_predecessor_state_sha256")
        == actual_state_sha256
        and isinstance(proof.get("a013_articulated_body_successor_state_sha256"), str)
        and _SHA.fullmatch(proof["a013_articulated_body_successor_state_sha256"])
        is not None
        and proof["a013_articulated_body_successor_state_sha256"]
        != actual_state_sha256
        and proof.get("a013_articulated_body_predecessor_tick") == actual_tick
        and proof.get("a013_articulated_body_successor_tick") == actual_tick + 1
        and proof.get("a013_articulated_body_axis_count") == 37
        and proof.get("a013_articulated_body_terminal_count") == 74
        and proof.get("a013_articulated_body_state_bytes") == 195
        and isinstance(proof.get("a013_articulated_body_state_sha256"), str)
        and _SHA.fullmatch(proof["a013_articulated_body_state_sha256"])
        is not None
        and proof.get("a013_articulated_body_proprioception_initialized") is True
        and proof.get("a013_articulated_body_neutral_observation") is True
        and proof.get("a013_articulated_body_live_transition_discarded") is True
        and proof.get("a013_articulated_body_python_callback_count") == 0
    )
    a013_thermal_body_rehearsal = (
        proof.get("a013_thermal_body_rehearsed") is True
        and proof.get("a013_thermal_body_world_revision_before") == 0
        and proof.get("a013_thermal_body_world_revision_after") == 1
        and proof.get("a013_thermal_body_receptor_count") == 2
        and proof.get("a013_thermal_body_reached_site_counts") == [1, 1]
        and proof.get("a013_thermal_body_episode_port_count") == 111
        and proof.get("a013_thermal_body_episode_sample_count") == 222
        and isinstance(proof.get("a013_thermal_body_dsf_delivery_count"), int)
        and not isinstance(proof["a013_thermal_body_dsf_delivery_count"], bool)
        and proof["a013_thermal_body_dsf_delivery_count"] > 0
        and all(
            isinstance(proof.get(name), str)
            and _SHA.fullmatch(proof[name]) is not None
            for name in (
                "a013_thermal_body_transition_receipt_sha256",
                "a013_thermal_body_anatomy_receipt_sha256",
                "a013_thermal_body_world_state_sha256",
            )
        )
        and proof.get("a013_thermal_body_cold_restore_exact") is True
        and proof.get("a013_fresh_complete_roster_cold_restore_exact") is True
        and isinstance(
            proof.get("a013_fresh_complete_roster_state_sha256"), str
        )
        and _SHA.fullmatch(
            proof["a013_fresh_complete_roster_state_sha256"]
        )
        is not None
        and proof.get("a013_thermal_body_python_callback_count") == 0
    )
    if (
        proof.get("schema") != PROOF_SCHEMAS[mode]
        or proof.get("mode") != mode
        or proof.get("candidate_git_sha") != candidate_git_sha
        or proof.get("candidate_image_digest") != candidate_image_digest
        or proof.get("source_identity") != expected_identity
        or not isinstance(actual_tick, int)
        or isinstance(actual_tick, bool)
        or expected_tick is None
        or (mode != "cold-restore" and actual_tick != expected_tick)
        or (
            mode == "cold-restore"
            and (
                actual_tick < expected_tick
                or proof.get("baseline_observed_tick") != expected_tick
                or proof.get("baseline_observed_state_sha256")
                != expected_state_sha256
                or proof.get("source_advanced_after_baseline")
                is not source_advanced
            )
        )
        or proof.get("cold_restore_exact") is not True
        or proof.get("raw_glorun_current_only") is not True
        or proof.get("python_callback_count") != 0
        or proof.get("python_cognition_workers_started") != 0
        or (
            expected_distributed_recall_rehearsal
            and not episodic_memory_rehearsal
        )
        or (
            expected_sparse_attention_rehearsal
            and not sparse_attention_rehearsal
        )
        or (
            expected_native_articulation_rehearsal
            and not native_articulation_rehearsal
        )
        or (
            expected_native_physical_rest_wake_rehearsal
            and not native_physical_rest_wake_rehearsal
        )
        or (
            expected_native_internal_consolidation_rehearsal
            and not native_internal_consolidation_rehearsal
        )
        or (
            expected_native_causal_cross_context_rehearsal
            and not native_causal_cross_context_rehearsal
        )
        or (
            expected_a013_articulated_body_rehearsal
            and not (
                a013_articulated_body_rehearsal
                and a013_thermal_body_rehearsal
            )
        )
        or not isinstance(proof.get("resident_state_bytes"), int)
        or isinstance(proof.get("resident_state_bytes"), bool)
        or proof["resident_state_bytes"] <= 0
        or not isinstance(actual_state_sha256, str)
        or _SHA.fullmatch(actual_state_sha256) is None
        or (
            mode == "cold-restore"
            and
            expected_state_sha256 is not None
            and actual_tick == expected_tick
            and actual_state_sha256 != expected_state_sha256
            and not current_format_migration
        )
        or receipt != hashlib.sha256(_canonical(record)).hexdigest()
    ):
        raise RuntimeError("native candidate proof changed")
    return proof


def _proof_from_logs(logs, *, group: str, stream: str, schema: str) -> object:
    token = None
    messages: list[str] = []
    while True:
        values = {
            "logGroupName": group,
            "logStreamName": stream,
            "startFromHead": True,
        }
        if token is not None:
            values["nextToken"] = token
        page = logs.get_log_events(**values)
        messages.extend(
            event.get("message", "")
            for event in page.get("events", [])
            if isinstance(event, dict)
        )
        next_token = page.get("nextForwardToken")
        if next_token == token:
            break
        token = next_token
    proofs = []
    for message in messages:
        try:
            value = json.loads(message)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("schema") == schema:
            proofs.append(value)
    if len(proofs) != 1:
        raise RuntimeError("candidate task did not emit one exact proof")
    return proofs[0]


def _retryable_same_digest_pull_absence(
    task: dict[str, object], expected_digest: str
) -> bool:
    """Whether Fargate raced publication of only the reviewed ECR digest."""

    reason = task.get("stoppedReason")
    containers = task.get("containers")
    return (
        isinstance(reason, str)
        and "CannotPullContainerError" in reason
        and expected_digest in reason
        and "not found" in reason
        and isinstance(containers, list)
        and len(containers) == 1
        and isinstance(containers[0], dict)
        and containers[0].get("exitCode") is None
    )


def main() -> int:
    values = _arguments()
    if values.mode in {"rehearse", "publish"} and (
        not values.expected_baseline_generation
        or not values.expected_active_generation
    ):
        raise ValueError("migration task requires exact generation identities")
    if values.mode == "cold-restore" and not values.expected_state_sha256:
        raise ValueError("cold restore requires expected state SHA-256")
    if values.mode != "genesis-rehearse" and values.expected_tick is None:
        raise ValueError("migration task requires the exact source tick")
    genesis_state_root = None
    if values.mode == "genesis-rehearse":
        genesis_state_root = GENESIS_STORE_PREFIX + time.strftime(
            "%Y%m%dT%H%M%SZ", time.gmtime()
        )
    import boto3

    ecs = boto3.client("ecs", region_name=values.region)
    logs = boto3.client("logs", region_name=values.region)
    source = ecs.describe_task_definition(
        taskDefinition=values.candidate_task_definition
    )["taskDefinition"]
    # Distributed recall and ordered-path witnesses closed earlier ledger
    # items.  They remain observable when they recur but are not release gates
    # for a later living predecessor (RF-034).
    expected_distributed_recall_rehearsal = False
    # C-014's sparse-attention witness is already live-closed and is a
    # transient trajectory fact, not permanent body state. Later releases
    # report it when it recurs but never require it as their acceptance gate.
    expected_sparse_attention_rehearsal = False
    expected_native_physical_rest_wake_rehearsal = False
    expected_native_internal_consolidation_rehearsal = False
    expected_native_causal_cross_context_rehearsal = False
    # A-013 is live-closed. Generic cold restore proves current continuity and
    # the fresh action/consequence boundary without replaying a mature-body
    # successor transition on every deployment.
    expected_a013_articulated_body_rehearsal = False
    task_input = probe_task_definition(
        source,
        mode=values.mode,
        candidate_git_sha=values.candidate_git_sha,
        candidate_image_digest=values.candidate_image_digest,
        expected_baseline_generation=values.expected_baseline_generation,
        expected_active_generation=values.expected_active_generation,
        expected_identity=values.expected_identity,
        expected_tick=values.expected_tick,
        expected_state_sha256=values.expected_state_sha256,
        genesis_state_root=genesis_state_root,
    )
    registered = ecs.register_task_definition(**task_input)["taskDefinition"]
    task_definition_arn = registered["taskDefinitionArn"]
    task_arns: list[str] = []
    try:
        service = ecs.describe_services(
            cluster=values.cluster,
            services=[values.service],
        )["services"][0]
        for launch_attempt in range(2):
            response = ecs.run_task(
                cluster=values.cluster,
                taskDefinition=task_definition_arn,
                launchType="FARGATE",
                networkConfiguration=service["networkConfiguration"],
                count=1,
            )
            if response.get("failures") or len(response.get("tasks", [])) != 1:
                raise RuntimeError("native candidate task failed admission")
            task_arn = response["tasks"][0]["taskArn"]
            task_arns.append(task_arn)
            ecs.get_waiter("tasks_stopped").wait(
                cluster=values.cluster,
                tasks=[task_arn],
                WaiterConfig={"Delay": 5, "MaxAttempts": 180},
            )
            task = ecs.describe_tasks(
                cluster=values.cluster,
                tasks=[task_arn],
            )["tasks"][0]
            containers = task.get("containers", [])
            if len(containers) == 1 and containers[0].get("exitCode") == 0:
                break
            if launch_attempt == 0 and _retryable_same_digest_pull_absence(
                task, values.candidate_image_digest
            ):
                continue
            raise RuntimeError(
                "native candidate task failed: "
                + json.dumps(task.get("stoppedReason"), sort_keys=True)
            )
        log_options = task_input["containerDefinitions"][0][
            "logConfiguration"
        ]["options"]
        group = log_options["awslogs-group"]
        # DescribeTasks does not return the awslogs stream name; it is
        # deterministic: <stream-prefix>/<container-name>/<task-id>.
        stream_name = containers[0].get("logStreamName") or "/".join(
            (
                log_options["awslogs-stream-prefix"],
                task_input["containerDefinitions"][0]["name"],
                task_arn.rsplit("/", 1)[-1],
            )
        )
        for _attempt in range(30):
            try:
                proof = _proof_from_logs(
                    logs,
                    group=group,
                    stream=stream_name,
                    schema=PROOF_SCHEMAS[values.mode],
                )
                break
            except RuntimeError:
                time.sleep(2)
        else:
            raise RuntimeError("native candidate proof was not delivered to logs")
        validated = _validate_proof(
            proof,
            mode=values.mode,
            candidate_git_sha=values.candidate_git_sha,
            candidate_image_digest=values.candidate_image_digest,
            expected_identity=values.expected_identity,
            expected_tick=values.expected_tick,
            expected_state_sha256=values.expected_state_sha256,
            expected_state_root=genesis_state_root,
            expected_distributed_recall_rehearsal=(
                expected_distributed_recall_rehearsal
            ),
            expected_sparse_attention_rehearsal=(
                expected_sparse_attention_rehearsal
            ),
            expected_native_articulation_rehearsal=(
                False
            ),
            expected_native_physical_rest_wake_rehearsal=(
                expected_native_physical_rest_wake_rehearsal
            ),
            expected_native_internal_consolidation_rehearsal=(
                expected_native_internal_consolidation_rehearsal
            ),
            expected_native_causal_cross_context_rehearsal=(
                expected_native_causal_cross_context_rehearsal
            ),
            expected_a013_articulated_body_rehearsal=(
                expected_a013_articulated_body_rehearsal
            ),
        )
        print(_canonical(validated).decode("ascii"))
        return 0
    finally:
        for task_arn in task_arns:
            try:
                ecs.stop_task(
                    cluster=values.cluster,
                    task=task_arn,
                    reason="native candidate task complete",
                )
            except Exception:
                pass
        ecs.deregister_task_definition(taskDefinition=task_definition_arn)


if __name__ == "__main__":
    raise SystemExit(main())
