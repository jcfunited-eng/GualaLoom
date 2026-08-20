"""C-005 truthful admitted-experience relation transport."""

from __future__ import annotations

from types import SimpleNamespace

from dsf_ai_service import native_production_app as production


def _hop(tick: int, relations: tuple[dict[str, object], ...]) -> dict[str, object]:
    counts = {
        "complete_neuron_fractal_count": 0,
        "current_cohort_evaluation_count": 1,
        "dsf_delivery_count": 1,
        "endogenous_partial_cue_reassembly_count": 0,
        "partial_cue_reassembly_count": 1,
        "physically_transitioned_neuron_count": 2,
        "metabolically_perturbed_body_receptor_count": 0,
        "rest_recovered_neuron_count": 0,
        "rest_drained_dissipation_quanta": 0,
        "unmet_dissipation_quanta": 0,
        "energy_exhausted_interval_count": 0,
        "externally_perturbed_body_receptor_count": 0,
        "recurrent_complete_neuron_fractal_count": 0,
    }
    return {
        **counts,
        "cognitive_mosaic_count": 2,
        "cognitive_trace_count": 0,
        "complete_neuron_count": 43,
        "developmental_resting_neuron_count": 196_509,
        "emitted_neuron_fractals": (),
        "formation_activation_count": 0,
        "predecessor_organism_tick": tick - 1,
        "organism_tick": tick,
        "internally_reassembled_formation_cues": (),
        "receptor_ingress_sense_counts": {
            sense.value: 0 for sense in production.SENSE_ORDER
        },
        "receptor_ingress_changing_count": 0,
        "receptor_ingress_quiescent_count": 0,
        "motor_unit_recruitments": (),
        "body_effector_bindings": (),
        "articulated_body_consequences": (),
        "body_proprioceptive_sources": (),
        "body_proprioceptive_source_extents": (),
        "articulatory_unit_recruitments": (),
        "physical_frontier_routes": (),
        "preceding_distinct_physical_frontier_routes": (),
        "reached_and_foregone_physical_frontier_routes": (),
        "working_causal_continuations": (),
        "settled_working_frontier": (),
        "physical_prediction_alternatives": (),
        "body_consequence_transfers": (),
        "affective_balance_trajectories": (),
        "localized_fluid_chemistry": (),
        "localized_metabolic_strain_evaluated_body_receptor_lineages": (),
        "localized_metabolic_strain": (),
        "organic_mosaic_relations": relations,
        "state_sha256": f"{tick:064x}",
    }


def _quiescent_body_organism() -> SimpleNamespace:
    return SimpleNamespace(
        readiness=lambda: SimpleNamespace(
            articulated_body_state_sha256="44" * 32,
        )
    )


class _UnsealedTestOrganism:
    def __init__(
        self,
        phase_hop: dict[str, object],
        final_hop: dict[str, object],
    ) -> None:
        self.phase_hop = phase_hop
        self.final_hop = final_hop
        self.calls: list[tuple[str, object]] = []

    def readiness(self) -> SimpleNamespace:
        return SimpleNamespace(articulated_body_state_sha256="44" * 32)

    def begin_unsealed_intake_direct(
        self, sources, intervals, *, vestibular_yaw=None
    ) -> SimpleNamespace:
        self.calls.append(("begin", (sources, intervals, vestibular_yaw)))
        return SimpleNamespace(
            token=b"u" * 32,
            provisional_organism_tick=self.phase_hop["organism_tick"],
            articulatory_unit_recruitments=self.phase_hop[
                "articulatory_unit_recruitments"
            ],
        )

    def finalize_unsealed_intake_direct(
        self, token, sources, intervals
    ) -> SimpleNamespace:
        self.calls.append(("finalize", (token, sources, intervals)))
        appended = bool(sources)
        return SimpleNamespace(
            appended_physically_transitioned_neuron_count=(
                self.final_hop["physically_transitioned_neuron_count"]
                if appended
                else 0
            ),
            appended_complete_neuron_fractal_count=(
                self.final_hop["complete_neuron_fractal_count"]
                if appended
                else 0
            ),
            appended_externally_perturbed_body_receptor_count=(
                self.final_hop["externally_perturbed_body_receptor_count"]
                if appended
                else 0
            ),
            appended_articulatory_unit_recruitment_count=0,
        )

    def abort_unsealed_intake(self, token) -> None:
        self.calls.append(("abort", token))


def _episode() -> SimpleNamespace:
    return SimpleNamespace(occurrence_count=1)


def test_frontier_evidence_keeps_only_current_and_preceding_distinct_sets() -> None:
    first = (("01" * 16, 5, 0, "02" * 16, 8, 0, 0, 1),)
    second = (("01" * 16, 5, 0, "03" * 16, 8, 1, 0, 2),)

    current, preceding, reached_and_foregone = production._advance_bounded_frontier_evidence(
        (),
        (),
        (),
        {
            "physical_frontier_routes": first,
            "preceding_distinct_physical_frontier_routes": (),
            "reached_and_foregone_physical_frontier_routes": (),
        },
    )
    current, preceding, reached_and_foregone = production._advance_bounded_frontier_evidence(
        current,
        preceding,
        reached_and_foregone,
        {
            "physical_frontier_routes": second,
            "preceding_distinct_physical_frontier_routes": first,
            "reached_and_foregone_physical_frontier_routes": second,
        },
    )

    assert current == second
    assert preceding == first
    assert reached_and_foregone == second


def test_ordinary_intake_opens_once_appends_self_hearing_and_finalizes_once(
    monkeypatch,
) -> None:
    recruitment = (
        "13" * 16,
        0,
        13,
        (("12" * 16, 12, "13" * 16, 13, 0, 13),),
    )
    calls: list[tuple[str, object]] = []

    class Organism:
        def readiness(self):
            return SimpleNamespace(articulated_body_state_sha256="44" * 32)

        def begin_unsealed_intake_direct(
            self, sources, intervals, *, vestibular_yaw=None
        ):
            calls.append(("begin", (sources, intervals, vestibular_yaw)))
            return SimpleNamespace(
                token=b"u" * 32,
                provisional_organism_tick=11,
                articulatory_unit_recruitments=(recruitment,),
            )

        def finalize_unsealed_intake_direct(self, token, sources, intervals):
            calls.append(("finalize", (token, sources, intervals)))
            return SimpleNamespace(
                appended_physically_transitioned_neuron_count=4,
                appended_complete_neuron_fractal_count=1,
                appended_externally_perturbed_body_receptor_count=4,
                appended_articulatory_unit_recruitment_count=0,
            )

        def abort_unsealed_intake(self, token):
            calls.append(("abort", token))

    organism = Organism()
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(organism=organism, pointer=predecessor),
            SimpleNamespace(),
        ),
    )
    final_hop = _hop(12, ())
    final_hop["articulatory_unit_recruitments"] = (recruitment,)
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: final_hop,
    )
    monkeypatch.setattr(
        production,
        "exact_articulatory_unit_trajectory",
        lambda **_kwargs: (16_000, [1] * 16_000, b"\x01\x00" * 64_000, 1, 1, 1, 1, 13, 0, 1),
    )
    self_hearing = (object(), [])
    monkeypatch.setattr(
        production,
        "_mono_pcm_hop_episodes",
        lambda **_kwargs: [self_hearing],
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=12,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(
        production, "_refresh_public_observation_cache", lambda: None
    )

    result = production._perform_admitted_intake_locked(
        [(_episode(), [])],
        "a009-one-seal",
    )

    assert [name for name, _ in calls] == ["begin", "finalize"]
    _, (_, appended_sources, appended_intervals) = calls[1]
    assert appended_sources == (self_hearing[0],)
    assert appended_intervals == (self_hearing[1],)
    assert result["observation"]["articulation"]["self_hearing_hop_count"] == 1


def test_working_causal_evidence_keeps_one_path_until_that_cause_settles() -> None:
    first = ("01" * 16, "02" * 16, 0, 7)
    second = ("02" * 16, "03" * 16, 0, 5)
    continuation, settlement = production._advance_bounded_working_causal_evidence(
        (),
        (),
        {
            "working_causal_continuations": ((first, second),),
            "settled_working_frontier": (),
        },
    )
    continuation, settlement = production._advance_bounded_working_causal_evidence(
        continuation,
        settlement,
        {
            "working_causal_continuations": (),
            "settled_working_frontier": (first, second),
        },
    )

    assert continuation == ((first, second),)
    assert settlement == (second,)


def test_prediction_evidence_keeps_two_alternatives_until_body_consequence() -> None:
    intrinsic_cause = "01" * 16
    first = ((intrinsic_cause, "02" * 16, 0, 7), ("02" * 16, "04" * 16, 0, 5))
    second = ((intrinsic_cause, "03" * 16, 0, 6), ("03" * 16, "05" * 16, 0, 4))
    consequence = ("06" * 16, "04" * 16, 0, 3)
    alternatives, returned = production._advance_bounded_prediction_evidence(
        (),
        (),
        {
            "physical_prediction_alternatives": (first, second),
            "body_consequence_transfers": (),
        },
    )
    alternatives, returned = production._advance_bounded_prediction_evidence(
        alternatives,
        returned,
        {
            "physical_prediction_alternatives": (),
            "body_consequence_transfers": (consequence,),
        },
    )
    assert alternatives == (first, second)
    assert returned == (consequence,)


def test_prediction_evidence_preserves_later_consequence_inside_ordered_trajectory() -> None:
    intrinsic_cause = "01" * 16
    first = ((intrinsic_cause, "02" * 16, 0, 7), ("02" * 16, "04" * 16, 0, 5))
    second = ((intrinsic_cause, "03" * 16, 0, 6), ("03" * 16, "05" * 16, 0, 4))
    consequence = ("04" * 16, "06" * 16, 0, 3)

    alternatives, returned = production._advance_bounded_prediction_evidence(
        (),
        (),
        {
            "physical_prediction_alternatives": (first, second),
            "body_consequence_transfers": (consequence,),
        },
    )

    assert alternatives == (first, second)
    assert returned == (consequence,)


def test_admitted_experience_preserves_relation_from_nonfinal_hop(
    monkeypatch,
) -> None:
    relation = {
        "predecessor_organism_tick": 10,
        "organism_tick": 11,
        "formation_receipts": ("11" * 32, "22" * 32),
        "shared_neuron_lineages": (),
        "active_physical_bonds": (("01" * 16, "02" * 16, 0),),
        "structural_relation_sha256": "33" * 32,
        "ordered_physical_paths": (),
        "ordered_path_relations": (),
    }
    trajectory_hop = _hop(12, (relation,))
    trajectory_hop["rest_recovered_neuron_count"] = 5
    organism = _UnsealedTestOrganism(trajectory_hop, trajectory_hop)
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(organism=organism, pointer=predecessor),
            SimpleNamespace(),
        ),
    )
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: trajectory_hop,
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=12,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(
        production, "_refresh_public_observation_cache", lambda: None
    )

    result = production._perform_admitted_intake_locked(
        [(_episode(), []), (_episode(), [])],
        "c005-test",
    )

    assert result["observation"]["organism_tick"] == 12
    assert result["observation"]["organic_mosaic_relations"] == (relation,)
    assert result["totals"]["rest_recovered_neuron_count"] == 5
    assert "unmet_dissipation_quanta" not in result["totals"]
    assert result["observation"]["unmet_dissipation_quanta"] == 0
    assert [name for name, _ in organism.calls] == ["begin", "finalize"]
    _, (sources, intervals, vestibular_yaw) = organism.calls[0]
    assert vestibular_yaw is None
    assert len(sources) == 2
    assert len(intervals) == 2


def test_layer_thirteen_discharge_commits_its_own_pressure_as_self_hearing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(production, "_last_tested_articulation_evidence", None)
    monkeypatch.setattr(production, "_last_transition_evidence", None)
    recruitment = (
        "13" * 16,
        0,
        13,
        (("12" * 16, 12, "13" * 16, 13, 0, 13),),
    )
    first = _hop(11, ())
    first["articulatory_unit_recruitments"] = (recruitment,)
    heard = _hop(12, ())
    heard["physically_transitioned_neuron_count"] = 4
    heard["complete_neuron_fractal_count"] = 1
    heard["externally_perturbed_body_receptor_count"] = 4
    # The production boundary deliberately exposes no direct ``organism_tick``
    # method.  The exact committed hop already carries the causal tick used to
    # name its self-hearing occurrence.
    organism = _UnsealedTestOrganism(first, heard)
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(organism=organism, pointer=predecessor),
            SimpleNamespace(),
        ),
    )
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: heard,
    )
    monkeypatch.setattr(
        production,
        "_mono_pcm_hop_episodes",
        lambda **_kwargs: [(object(), [])],
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=12,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(production, "_refresh_public_observation_cache", lambda: None)

    result = production._perform_admitted_intake_locked(
        [(_episode(), [])],
        "c020-test",
    )

    articulation = result["observation"]["articulation"]
    assert articulation["layer_13_recruitment_count"] == 1
    assert articulation["pressure_sample_count"] >= 16_000
    assert articulation["self_hearing_hop_count"] == 1
    assert articulation["self_hearing_transitioned_neuron_count"] == 4
    assert articulation["self_hearing_fractal_count"] == 1
    assert articulation["articulatory_body_port_count"] == 4
    assert articulation["articulatory_body_nonquiescent_port_count"] == 4
    assert articulation["articulatory_body_receptor_ingress_count"] == 4
    assert articulation["articulatory_body_perturbed_neuron_count"] == 4
    production._last_transition_evidence = {"articulation": None}
    retained_observation = production._articulation_record()
    assert retained_observation["available"] is True
    assert (
        retained_observation["status"]
        == "native_articulation_and_self_hearing_committed"
    )
    assert retained_observation["organism_tick"] == 12


def test_self_hearing_hops_share_one_native_trajectory_boundary(monkeypatch) -> None:
    recruitment = (
        "13" * 16,
        0,
        13,
        (("12" * 16, 12, "13" * 16, 13, 0, 13),),
    )
    first = _hop(11, ())
    first["articulatory_unit_recruitments"] = (recruitment,)
    heard = _hop(15, ())
    heard["physically_transitioned_neuron_count"] = 40
    heard["complete_neuron_fractal_count"] = 3
    heard["externally_perturbed_body_receptor_count"] = 16
    organism = _UnsealedTestOrganism(first, heard)
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(organism=organism, pointer=predecessor),
            SimpleNamespace(),
        ),
    )
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: heard,
    )
    self_hearing = tuple((object(), []) for _ in range(4))
    monkeypatch.setattr(
        production,
        "_mono_pcm_hop_episodes",
        lambda **_kwargs: self_hearing,
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=15,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(production, "_refresh_public_observation_cache", lambda: None)

    result = production._perform_admitted_intake_locked(
        [(_episode(), [])],
        "self-hearing-trajectory-boundary-test",
    )

    assert [name for name, _ in organism.calls] == ["begin", "finalize"]
    _, (_, self_hearing_sources, self_hearing_intervals) = organism.calls[1]
    assert len(self_hearing_sources) == 4
    assert len(self_hearing_intervals) == 4
    articulation = result["observation"]["articulation"]
    assert articulation["self_hearing_hop_count"] == 4
    assert articulation["self_hearing_transitioned_neuron_count"] == 40
    assert articulation["self_hearing_fractal_count"] == 3
    assert articulation["articulatory_body_perturbed_neuron_count"] == 16


def test_exact_retained_path_is_bound_to_articulation_and_self_hearing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(production, "_last_tested_articulation_evidence", None)
    monkeypatch.setattr(production, "_last_transition_evidence", None)
    monkeypatch.setattr(
        production, "_active_external_participant_causal_motor_traces", {}
    )
    motor = "12" * 16
    articulatory = "13" * 16
    recruitment = (
        articulatory,
        0,
        13,
        ((motor, 12, articulatory, 13, 0, 13),),
    )
    causal_path = {
        "origin_kind": "retained_formation",
        "origin_lineages": ("01" * 16,),
        "origin_organism_tick": 10,
        "formation_receipt_sha256": "11" * 32,
        "internal_cue_lineages": ("01" * 16,),
        "recurrence_organism_tick": 10,
        "articulation_organism_tick": 11,
        "directed_physical_transfers": (
            ("01" * 16, motor, 0, 17),
            (motor, articulatory, 0, 13),
        ),
        "articulatory_unit_recruitment": {
            "articulatory_lineage": articulatory,
            "articulatory_layer": 13,
            "articulatory_topology_index": 0,
            "outward_elementary_carriers": 13,
            "matched_preparation_transfer": (
                motor,
                12,
                articulatory,
                13,
                0,
                13,
            ),
        },
    }
    first = _hop(11, ())
    first["articulatory_unit_recruitments"] = (recruitment,)
    heard = _hop(12, ())
    heard["physically_transitioned_neuron_count"] = 4
    heard["externally_perturbed_body_receptor_count"] = 4
    organism = _UnsealedTestOrganism(first, heard)
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(organism=organism, pointer=predecessor),
            SimpleNamespace(),
        ),
    )
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: heard,
    )
    monkeypatch.setattr(
        production,
        "_advance_causal_motor_traces",
        lambda _organism, active, completed, _hop, *_args, **_kwargs: (
            active,
            {
                **completed,
                "retained_formation_articulation": causal_path,
            },
        ),
    )
    monkeypatch.setattr(
        production,
        "_mono_pcm_hop_episodes",
        lambda **_kwargs: [(object(), [])],
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=12,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(production, "_refresh_public_observation_cache", lambda: None)

    result = production._perform_admitted_intake_locked(
        [(_episode(), [])],
        "retained-articulation-test",
    )

    causal = result["observation"]["articulatory_causal_cross_context_use"]
    articulation = result["observation"]["articulation"]
    assert causal["formation_receipt_sha256"] == "11" * 32
    assert causal["directed_physical_transfers"] == causal_path[
        "directed_physical_transfers"
    ]
    assert causal["action"]["pressure_sha256"] == articulation[
        "pressure_sha256"
    ]
    assert causal["action"]["applied_motor_quanta"] > 0
    assert causal["sensed_consequence"]["self_hearing_hop_count"] == 1
    assert causal["sensed_consequence"][
        "self_hearing_transitioned_neuron_count"
    ] == 4
    assert articulation["retained_formation_causal_path"] == causal

    production._last_transition_evidence = {"articulation": None}
    retained = production._articulation_record()
    assert retained["retained_formation_causal_path"] == causal


def test_exact_antagonist_cancellation_is_a_lawful_no_vocal_act(
    monkeypatch,
) -> None:
    """Equal vocal antagonists do not invalidate their admitted experience."""

    monkeypatch.setattr(production, "_last_tested_articulation_evidence", None)
    monkeypatch.setattr(production, "_last_transition_evidence", None)
    cancelled = _hop(11, ())
    cancelled["articulatory_unit_recruitments"] = (
        (
            "13" * 16,
            0,
            5,
            (("12" * 16, 12, "13" * 16, 13, 0, 5),),
        ),
        (
            "14" * 16,
            1,
            5,
            (("12" * 16, 12, "14" * 16, 13, 0, 5),),
        ),
    )
    organism = _UnsealedTestOrganism(cancelled, cancelled)
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(organism=organism, pointer=predecessor),
            SimpleNamespace(),
        ),
    )
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: cancelled,
    )

    def exact_cancellation(**_kwargs):
        raise ValueError("CancelledRecruitment")

    monkeypatch.setattr(
        production,
        "exact_articulatory_unit_trajectory",
        exact_cancellation,
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=11,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(
        production,
        "_refresh_public_observation_cache",
        lambda: None,
    )

    result = production._perform_admitted_intake_locked(
        [(_episode(), [])],
        "exact-antagonist-cancellation-test",
    )

    assert result["observation"]["organism_tick"] == 11
    assert result["observation"]["articulation"] is None
    assert result["observation"]["hop_count"] == 1


def test_non_cancellation_articulation_error_still_refuses_intake(
    monkeypatch,
) -> None:
    failed = _hop(11, ())
    failed["articulatory_unit_recruitments"] = (
        ("13" * 16, 0, 5, ()),
    )
    organism = _UnsealedTestOrganism(failed, failed)
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(
                organism=organism, pointer=predecessor
            ),
            SimpleNamespace(),
        ),
    )
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: failed,
    )

    def arithmetic_failure(**_kwargs):
        raise ValueError("ArithmeticWidth")

    monkeypatch.setattr(
        production,
        "exact_articulatory_unit_trajectory",
        arithmetic_failure,
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=11,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(
        production,
        "_refresh_public_observation_cache",
        lambda: None,
    )

    try:
        production._perform_admitted_intake_locked(
            [(_episode(), [])],
            "non-cancellation-articulation-error-test",
        )
    except ValueError as error:
        assert str(error) == "ArithmeticWidth"
        assert [name for name, _ in organism.calls] == ["begin", "abort"]
    else:
        raise AssertionError("non-cancellation articulation failure was hidden")


def test_vestibular_trajectory_articulation_reaches_the_ordinary_aggregate(
    monkeypatch,
) -> None:
    monkeypatch.setattr(production, "_last_tested_articulation_evidence", None)
    monkeypatch.setattr(production, "_last_transition_evidence", None)
    recruitment = (
        "13" * 16,
        0,
        5,
        (("12" * 16, 12, "13" * 16, 13, 0, 5),),
    )
    trajectory = _hop(261, ())
    trajectory["articulatory_unit_recruitments"] = (recruitment,)
    heard = _hop(262, ())
    heard["physically_transitioned_neuron_count"] = 3
    heard["complete_neuron_fractal_count"] = 2
    heard["externally_perturbed_body_receptor_count"] = 4
    organism = _UnsealedTestOrganism(trajectory, heard)
    predecessor = SimpleNamespace(state_sha256="aa" * 32)
    monkeypatch.setattr(
        production,
        "_runtime",
        lambda: (
            SimpleNamespace(organism=organism, pointer=predecessor),
            SimpleNamespace(),
        ),
    )
    monkeypatch.setattr(
        production,
        "_resident_prepare_hop",
        lambda *_args, **_kwargs: heard,
    )
    monkeypatch.setattr(
        production,
        "_mono_pcm_hop_episodes",
        lambda **_kwargs: [(object(), [])],
    )
    monkeypatch.setattr(
        production,
        "_publish_committed_organism",
        lambda *_args: SimpleNamespace(
            pointer=SimpleNamespace(
                organism_tick=262,
                state_bytes=100,
                state_sha256="bb" * 32,
            )
        ),
    )
    monkeypatch.setattr(production, "_refresh_public_observation_cache", lambda: None)

    result = production._perform_admitted_intake_locked(
        [],
        "c020-live-path-test",
        vestibular_yaw=(0, (360,)),
    )

    articulation = result["observation"]["articulation"]
    assert articulation["layer_13_recruitment_count"] == 1
    assert articulation["self_hearing_hop_count"] == 1
    assert articulation["self_hearing_transitioned_neuron_count"] == 3
    assert articulation["self_hearing_fractal_count"] == 2


def test_admitted_hop_carries_native_structure_receipt_after_commit() -> None:
    receipts = ("11" * 32, "22" * 32)
    left_members = ("01" * 16, "02" * 16, "03" * 16)
    right_members = ("04" * 16, "05" * 16, "06" * 16)
    bond = (left_members[0], right_members[0], 0)
    evidence = SimpleNamespace(
        token="commit-token",
        predecessor_organism_tick=10,
        organism_tick=11,
        complete_neuron_fractal_count=0,
        emitted_neuron_fractals=(),
        current_cohort_evaluation_count=1,
        dsf_delivery_count=1,
        partial_cue_reassembly_count=1,
        endogenous_partial_cue_reassembly_count=0,
        internally_reassembled_formation_cues=(),
        externally_reassembled_formation_frontiers=(),
        physically_transitioned_neuron_count=2,
        metabolically_perturbed_body_receptor_count=0,
        rest_recovered_neuron_count=7,
        rest_drained_dissipation_quanta=11,
        unmet_dissipation_quanta=0,
        externally_perturbed_body_receptor_count=0,
        externally_perturbed_neuron_lineages=(),
        receptor_ingress_sense_counts=(0,) * len(production.SENSE_ORDER),
        receptor_ingress_changing_count=0,
        receptor_ingress_quiescent_count=0,
        motor_unit_recruitments=(),
        body_effector_bindings=(),
        articulated_body_consequences=(),
        body_proprioceptive_sources=(),
        body_proprioceptive_source_extents=(),
        articulatory_unit_recruitments=(),
        causal_interval_evidence=(),
        changed_contact_channel_states=(),
        physical_frontier_routes=(),
        preceding_distinct_physical_frontier_routes=(),
        reached_and_foregone_physical_frontier_routes=(),
        working_causal_continuations=(),
        settled_working_frontier=(),
        physical_prediction_alternatives=(),
        body_consequence_transfers=(),
        affective_balance_trajectories=(),
        localized_fluid_chemistry=(),
        localized_metabolic_strain_evaluated_body_receptor_lineages=(),
        localized_metabolic_strain=(),
        organic_mosaic_relations=((receipts, (), (bond,), "33" * 32, (), ()),),
        recurrent_complete_neuron_fractal_count=2,
    )
    observed = SimpleNamespace(
        cognitive_mosaic_count=2,
        cognitive_trace_count=0,
        complete_neuron_count=43,
        developmental_resting_neuron_count=196_509,
        formation_activation_count=1,
        organism_tick=11,
        partial_cue_reassembly_count=1,
        endogenous_partial_cue_reassembly_count=0,
        energy_exhausted=False,
        dissipation_capacity_energy_zeptojoules=(100, 1),
        state_sha256="aa" * 32,
    )

    class Organism:
        committed = False

        @staticmethod
        def prepare_admitted(_episode, _intervals):
            return evidence

        def commit(self, token):
            assert token == "commit-token"
            self.committed = True
            return observed

    hop = production._commit_admitted_hop(Organism(), object(), [])

    assert hop["organic_mosaic_relations"][0]["structural_relation_sha256"] == (
        "33" * 32
    )
    assert hop["rest_recovered_neuron_count"] == 7
    assert hop["rest_drained_dissipation_quanta"] == 11
    assert hop["unmet_dissipation_quanta"] == 0
