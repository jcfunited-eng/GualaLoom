from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

import pytest

from dsf_ai_service import candidate_release_rehearsal as rehearsal
from dsf_ai_service import cold_restore_probe
from dsf_ai_service import native_production_app as serving
from tools import run_guala_candidate_rehearsal_task as runner


IDENTITY = "1cc4e70a-f2a0-44c5-a111-f4a5bc915cc1"
BASELINE = "11111111-1111-4111-8111-111111111111"
ACTIVE = "22222222-2222-4222-8222-222222222222"
STATE_SHA = hashlib.sha256(b"x" * 500).hexdigest()


@dataclass
class _Observation:
    identity: str = IDENTITY
    organism_tick: int = 23_723_846
    fabric_bytes: int = 400
    fabric_generation: int = 13
    fabric_sha256: str = "a" * 64
    joint_field_count: int = 2
    joint_neuron_count: int = 96
    mounted_generation: int = 2
    state_bytes: int = 500
    state_sha256: str = STATE_SHA
    cognitive_mosaic_count: int = 0
    cognitive_ordinal: int = 0
    cognitive_trace_count: int = 0
    formation_activation_count: int = 0
    mosaic_of_mosaics_count: int = 0
    complete_neuron_count: int = 0
    developmental_resting_neuron_count: int = 196_335
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
    def articulated_body_axes(
        self,
    ) -> list[tuple[int, str, str, int, int, int, int]]:
        return [
            (ordinal, f"axis_{ordinal}", "millidegree", 0, -1, 0, 1)
            for ordinal in range(37)
        ]

    @property
    def articulated_body_vocal_tract_areas_square_millimetres(
        self,
    ) -> list[int]:
        return [125, 145, 165, 185, 205, 225, 245, 265]


class _Organism:
    def readiness(self):
        return _Observation()

    def save(self):
        return b"x" * 500

    def observe_reached_neuron_count_by_layer(self):
        return ()

    def observe_retained_formation_recurrence_evidence(self):
        return ()


@dataclass
class _Pointer:
    identity: str = IDENTITY
    organism_tick: int = 23_723_846
    state_sha256: str = STATE_SHA


@dataclass
class _Restored:
    organism: object = field(default_factory=_Organism)
    pointer: object = field(default_factory=_Pointer)


@dataclass
class _Admission:
    max_envelope_bytes: int = 1_000
    max_fabric_bytes: int = 900
    max_logical_peak_bytes: int = 3_000
    memory_boundary_source: str = "test"
    derivation: str = "three finite regions"


def test_native_readiness_names_only_truthful_available_state(monkeypatch) -> None:
    monkeypatch.setattr(serving, "_restored", _Restored())
    monkeypatch.setattr(serving, "_admission", _Admission())

    value = serving._readiness()

    assert (
        value["ready_scope"]
        == "http_native_current_and_admitted_sensory_transitions"
    )
    assert value["organism_tick"] == 23_723_846
    assert "active_recovery_tick" not in value
    assert "native_joint_fractal" not in value
    native = value["native_resident"]
    assert native["available"] is True
    assert native["reached_dsf_perspective_count"] == 96
    # Truth-coupling: this fixture observation carries zero cognition, so
    # readiness must refuse to claim any — availability flags follow the
    # observation's actual counts, never the mounted surface.
    assert native["complete_neuron_count"] == 0
    assert native["complete_neuron_available"] is False
    assert native["genuine_neuronal_fractal_available"] is False
    assert native["cognition_available"] is False
    assert native["python_callback_count"] == 0


@pytest.mark.asyncio
async def test_sensory_transports_refuse_truthfully() -> None:
    # An absent sight payload is malformed input; standalone hearing remains
    # gated before the request body is read when its mounted conditions fail.
    sight = serving.sight_frame(None)
    sound = await serving.sound_frame(None)
    assert sight.status_code == 422
    assert b"refused" in sight.body
    assert sound.status_code == 503
    assert b"cochlear ear anatomy is not authorized" in sound.body
    assert serving.pcm_open(None).status_code == 503
    assert serving.pcm_close({"session_id": "x"}).status_code == 503


def test_external_curriculum_routes_are_packaged_and_served() -> None:
    paths = {route.path for route in serving.app.routes}
    assert "/audio" in paths
    assert "/cards" in paths
    assert "/curriculum" in paths
    assert "/curriculum/card_experience_manifest-v1.json" in paths
    response = serving.card_experience_manifest()
    assert str(response.path).endswith("card_experience_manifest-v1.json")


def test_candidate_task_is_read_only_for_rehearsal_and_writable_for_publication() -> None:
    source = {
        "containerDefinitions": [{
            "name": "dsf-ai",
            "image": "example@sha256:" + "c" * 64,
            "environment": [
                {"name": "GUALA_S3_BACKUP_BUCKET", "value": "bucket"},
                {
                    "name": "GUALA_NATIVE_ORGANISM_ROOT",
                    "value": "/app/guala/native-organism",
                },
            ],
            "secrets": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {"awslogs-group": "/ecs/dsf-ai"},
            },
        }],
        "cpu": "4096",
        "memory": "16384",
        "networkMode": "awsvpc",
        "requiresCompatibilities": ["FARGATE"],
        "volumes": [{"name": "gualaloom-state"}],
    }
    common = {
        "candidate_git_sha": "d" * 40,
        "candidate_image_digest": "sha256:" + "c" * 64,
        "expected_baseline_generation": BASELINE,
        "expected_active_generation": ACTIVE,
        "expected_identity": IDENTITY,
        "expected_tick": 23_723_846,
    }
    read_only = runner.probe_task_definition(source, mode="rehearse", **common)
    writable = runner.probe_task_definition(source, mode="publish", **common)
    cold = runner.probe_task_definition(
        source,
        mode="cold-restore",
        candidate_git_sha=common["candidate_git_sha"],
        candidate_image_digest=common["candidate_image_digest"],
        expected_identity=common["expected_identity"],
        expected_tick=common["expected_tick"],
        expected_state_sha256=STATE_SHA,
    )
    assert read_only["containerDefinitions"][0]["mountPoints"][0]["readOnly"] is True
    assert writable["containerDefinitions"][0]["mountPoints"][0]["readOnly"] is False
    assert cold["containerDefinitions"][0]["mountPoints"][0]["readOnly"] is True
    assert "--native-store-root" not in read_only["containerDefinitions"][0]["command"]
    assert "/source/guala/native-organism" in writable["containerDefinitions"][0]["command"]
    assert "dsf_ai_service.cold_restore_probe" in cold["containerDefinitions"][0]["command"]


def test_read_only_content_generation_extracts_exact_core(tmp_path: Path) -> None:
    store = tmp_path / "store"
    generation = store / "generations" / ACTIVE
    chunk_root = store / "content-chunks"
    generation.mkdir(parents=True)
    payload = json.dumps({"data": {}}, sort_keys=True).encode()
    digest = hashlib.sha256(payload).hexdigest()
    chunk = chunk_root / digest[:2] / digest
    chunk.parent.mkdir(parents=True)
    chunk.write_bytes(payload)
    record = {
        "chunks": [{
            "schema": "immutable_generation_content_chunk_v1",
            "sha256": digest,
            "size_bytes": len(payload),
        }],
        "generation_uuid": ACTIVE,
        "identity": IDENTITY,
        "json_payload": True,
        "relative_path": "guala_core.json",
        "schema": "immutable_generation_content_record_v2",
        "sha256": digest,
        "size_bytes": len(payload),
        "tick": 23_723_846,
    }
    manifest = {
        "generation_uuid": ACTIVE,
        "identity": IDENTITY,
        "required_files": [record],
        "schema": "immutable_generation_content_manifest_v2",
        "tick": 23_723_846,
    }
    (generation / "MANIFEST.json").write_bytes(
        rehearsal._generation_canonical(manifest)
    )
    assert rehearsal._stored_payload(
        store,
        ACTIVE,
        expected_identity=IDENTITY,
        expected_tick=23_723_846,
        relative_path="guala_core.json",
    ) == payload


def test_legacy_envelope_generation_is_not_a_migration_authority(
    tmp_path: Path,
) -> None:
    store = tmp_path / "store"
    generation = store / "generations" / ACTIVE
    generation.mkdir(parents=True)
    manifest = {
        "generation_uuid": ACTIVE,
        "identity": IDENTITY,
        "required_files": [],
        "schema": "immutable_generation_manifest_v1",
        "tick": 23_723_846,
    }
    (generation / "MANIFEST.json").write_bytes(
        rehearsal._generation_canonical(manifest)
    )
    with pytest.raises(RuntimeError, match="manifest changed"):
        rehearsal._manifest(
            store,
            ACTIVE,
            expected_identity=IDENTITY,
            expected_tick=23_723_846,
        )


def test_native_current_cold_restore_proof_is_state_bound() -> None:
    record = {
        "baseline_observed_state_sha256": STATE_SHA,
        "baseline_observed_tick": 23_723_846,
        "candidate_git_sha": "d" * 40,
        "candidate_image_digest": "sha256:" + "c" * 64,
        "cold_restore_exact": True,
        "complete_neuron_count": 0,
        "current_format_migration_rehearsed": False,
        "developmental_resting_neuron_count": 196_335,
        "migration_predecessor_state_sha256": None,
        "mode": "cold-restore",
        "motor_action_rehearsed": False,
        "python_callback_count": 0,
        "python_cognition_workers_started": 0,
        "raw_glorun_current_only": True,
        "resident_state_bytes": 500,
        "resident_state_sha256": STATE_SHA,
        "schema": "guala.production_native_current_cold_restore.v8",
        "source_identity": IDENTITY,
        "source_advanced_after_baseline": False,
        "source_mount_read_only": True,
        "tick": 23_723_846,
    }
    proof = {
        **record,
        "receipt_sha256": hashlib.sha256(runner._canonical(record)).hexdigest(),
    }
    assert runner._validate_proof(
        proof,
        mode="cold-restore",
        candidate_git_sha="d" * 40,
        candidate_image_digest="sha256:" + "c" * 64,
        expected_identity=IDENTITY,
        expected_tick=23_723_846,
        expected_state_sha256=STATE_SHA,
    ) == proof
    with pytest.raises(RuntimeError, match="proof changed"):
        runner._validate_proof(
            proof,
            mode="cold-restore",
            candidate_git_sha="d" * 40,
            candidate_image_digest="sha256:" + "c" * 64,
            expected_identity=IDENTITY,
            expected_tick=23_723_846,
            expected_state_sha256="f" * 64,
        )


def test_cold_probe_uses_only_binary_current(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        cold_restore_probe,
        "derive_native_resident_resource_admission",
        lambda _root: _Admission(),
    )
    monkeypatch.setattr(
        cold_restore_probe,
        "restore_current_native_organism",
        lambda *_args, **_kwargs: _Restored(),
    )
    monkeypatch.setattr(
        cold_restore_probe,
        "_rehearse_a013_thermal_body",
        lambda *_args, **_kwargs: {
            "a013_thermal_body_rehearsed": True,
        },
    )
    monkeypatch.setattr(
        cold_restore_probe,
        "_arguments",
        lambda: type("Args", (), {
            "native_store_root": "/state",
            "expected_identity": IDENTITY,
            "expected_tick": 23_723_846,
            "expected_state_sha256": STATE_SHA,
            "candidate_git_sha": "d" * 40,
            "candidate_image_digest": "sha256:" + "c" * 64,
        })(),
    )
    assert cold_restore_probe.main() == 0
    proof = json.loads(capsys.readouterr().out)
    assert proof["schema"] == cold_restore_probe.PROOF_SCHEMA
    assert proof["resident_state_sha256"] == STATE_SHA
