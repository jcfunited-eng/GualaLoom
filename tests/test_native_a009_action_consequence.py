"""A-009 proof for the exact joint sensorium caused by one body action."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from dsf_ai_service import native_production_app as production


def test_one_millisecond_action_builds_one_truthful_joint_consequence(
    tmp_path: Path,
) -> None:
    repository = Path(__file__).resolve().parents[1]
    environment = dict(os.environ)
    environment.update(
        {
            "GUALA_CHEMORECEPTION": "1",
            "GUALA_COCHLEAR_EARS": "1",
            "GUALA_TOUCH_RECEPTORS": "1",
            "GUALA_VESTIBULAR": "1",
            "GUALA_WORLD": "1",
            "GUALA_NATIVE_ORGANISM_ROOT": str(tmp_path),
            "PYTHONPATH": os.pathsep.join(
                (str(repository), environment.get("PYTHONPATH", ""))
            ),
        }
    )
    probe = r'''import hashlib
import json
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

world = production._world()
before = world.observation_snapshot()
body = next(item for item in before.bodies if item.body_id == before.self_body_id)
execution = world.execute_port_command(
    port_id=PORT_ID,
    command_payload=encode_command(
        MoveCommand(
            target_pose=PoseMM(body.pose.position, 90_000),
            duration_microseconds=1_000,
        )
    ),
    causal_intent_receipt_sha256=hashlib.sha256(b"a009").hexdigest(),
    expected_revision=before.revision,
)
organism = create_native_resident_organism(
    organism_identity="1cc4e70a-f2a0-44c5-a111-f4a5bc915cc1",
    organism_tick=0,
    growth_dna=production._authored_growth_dna(),
    max_envelope_bytes=78_643_200,
    max_fabric_bytes=78_642_336,
    max_logical_peak_bytes=629_145_600,
)
episode, admissions, lanes = production._action_consequence_episode(
    execution,
    retinal_body_axes=organism.readiness().articulated_body_axes,
)
unsealed = organism.begin_unsealed_intake_direct((episode,), (admissions,))
prepared = organism.finalize_unsealed_intake_direct(unsealed.token)
organism.acknowledge_direct_commit(prepared.token)
hop = production._resident_prepare_hop(prepared, organism.readiness())
print(json.dumps({
    "admissions": admissions,
    "body": lanes["proprioceptive"],
    "body_feedback_extents": hop["body_proprioceptive_source_extents"],
    "causal_interval_count": len(hop["causal_interval_evidence"]),
    "chemical": lanes["chemical"],
    "duration": lanes["action_duration_microseconds"],
    "episode_occurrences": episode.occurrence_count,
    "episode_ports": episode.port_count,
    "episode_samples": episode.source_sample_count,
    "external_body": hop["externally_perturbed_body_receptor_count"],
    "external_lineages": hop["externally_perturbed_neuron_lineages"],
    "ingress": hop["receptor_ingress_sense_counts"],
    "internal_body": hop["metabolically_perturbed_body_receptor_count"],
    "organism_tick": hop["organism_tick"],
    "python_callbacks": episode.python_callback_count,
    "receipt_matches": lanes["action_receipt_sha256"] == execution.causal_intent_receipt_sha256,
    "schema": episode.schema,
    "sound": lanes["auditory"],
    "touch": lanes["tactile"],
    "thermal": lanes["thermal"],
    "visual": lanes["visual"],
}))
'''
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=repository,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(completed.stdout)

    assert evidence["schema"] == "guala.native.exact_joint_source_episode.v2"
    assert evidence["duration"] == 1_000
    assert evidence["admissions"] == [[1, 1_000]]
    assert evidence["episode_occurrences"] == 1
    assert evidence["episode_ports"] == 111
    assert evidence["episode_samples"] == 222
    assert evidence["organism_tick"] == 2
    assert evidence["causal_interval_count"] == 2
    # A newborn native test body first admits its complete 74-axis
    # proprioceptive state, then this one external joint occurrence.  No
    # motor feedback occurrence was authored by Python or required here.
    assert evidence["body_feedback_extents"] == []
    initial_body_port_count = 74
    assert evidence["ingress"] == {
        "body": 10 + initial_body_port_count,
        "sight": 27,
        "smell": 8,
        "sound": 34,
        "taste": 5,
        "touch": 27,
    }
    assert evidence["external_body"] == 2
    assert 0 < len(evidence["external_lineages"]) <= 29
    assert len(set(evidence["external_lineages"])) == len(
        evidence["external_lineages"]
    )
    # The six pre-existing body receptors and all 74 mounted joint terminals
    # participate in the same settled successor organism.
    assert evidence["internal_body"] == 80
    assert evidence["python_callbacks"] == 0
    assert evidence["receipt_matches"] is True
    assert evidence["chemical"] == {
        "smell_changed": 1,
        "smell_transported": 8,
        "taste_changed": 0,
        "taste_transported": 5,
    }
    assert evidence["body"] == {
        "changed": 0,
        "sensor_id": "articulatory-body-mechanoreceptors",
        "transported": 4,
    }
    assert evidence["sound"] == {"changed": 0, "transported": 34}
    assert evidence["touch"] == {"changed": 0, "transported": 27}
    assert evidence["thermal"] == {
        "changed": 1,
        "sensor_id": "organism-core-and-cutaneous-thermoreceptors",
        "transported": 2,
    }
    assert evidence["visual"]["transported"] == 27
    assert evidence["visual"]["changed"] > 0


def test_rigid_yaw_reports_local_proprioception_as_reached_quiescence(
    monkeypatch,
) -> None:
    class ReachedOrganism:
        @staticmethod
        def observe_reached_source_site_count(
            sensor_id: str,
            substream_id: str,
        ) -> int:
            return int(
                sensor_id == production.ARTICULATORY_BODY_SENSOR_ID
                and substream_id.startswith("articulation-")
            )

    restored = type("Restored", (), {"organism": ReachedOrganism()})()
    monkeypatch.setattr(production, "_runtime", lambda: (restored, object()))
    monkeypatch.setattr(
        production,
        "_last_self_moved",
        {
            "sensory_consequence": {
                "action_receipt_sha256": "11" * 32,
                "proprioceptive": {
                    "changed": 0,
                    "sensor_id": production.ARTICULATORY_BODY_SENSOR_ID,
                    "transported": 4,
                },
            }
        },
    )

    evidence = production._proprioception_record()

    assert evidence["available"] is True
    assert evidence["status"] == (
        "local_proprioceptive_action_consequence_committed"
    )
    assert evidence["changed_site_count"] == 0
    assert evidence["reached_site_count"] == 4
    assert evidence["native_neuronal_participation"] is True


def test_public_action_consequence_does_not_export_preparation_graphs(
    monkeypatch,
) -> None:
    motor_action = {
        "moved": True,
        "motor_unit_recruitment_count": 2,
        "prepared_recruitments": ({"large": "internal"},) * 2,
        "sensory_consequence": {"action_receipt_sha256": "22" * 32},
    }
    monkeypatch.setattr(
        production,
        "_last_transition_evidence",
        {
            "state_sha256": "33" * 32,
            "motor_action": motor_action,
            "motor_unit_recruitments": (1, 2),
            "articulatory_unit_recruitments": (3,),
            "organic_mosaic_relations": (4, 5, 6),
            "physical_frontier_routes": (7,),
            "preceding_distinct_physical_frontier_routes": (8, 9),
            "reached_and_foregone_physical_frontier_routes": (10, 11, 12, 13),
        },
    )

    observed = production._last_transition_record()

    assert "prepared_recruitments" not in observed["motor_action"]
    assert observed["motor_action"]["motor_unit_recruitment_count"] == 2
    assert observed["motor_unit_recruitment_count"] == 2
    assert observed["articulatory_unit_recruitment_count"] == 1
    assert observed["organic_mosaic_relation_count"] == 3
    assert observed["physical_frontier_route_count"] == 1
    assert observed["preceding_distinct_physical_frontier_route_count"] == 2
    assert observed["reached_and_foregone_physical_frontier_route_count"] == 4


def test_retired_single_hop_action_helpers_cannot_reenter_production() -> None:
    assert not hasattr(production, "_insert_native_action_consequences")
    assert not hasattr(production, "_commit_vestibular_tick")
    assert not hasattr(production, "_commit_vestibular_trajectory")
