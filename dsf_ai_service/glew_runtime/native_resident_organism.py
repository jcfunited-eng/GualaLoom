"""Concrete Python boundary for one native resident Guala organism.

The native object is the sole active and pending-state authority.  Python
retains only that object and returns fixed prepare receipts; it never carries
prepared organism bytes or a second materialized-fabric state.
"""

from __future__ import annotations

import hashlib
import importlib
import sys
from dataclasses import dataclass
from typing import Protocol


RUNTIME_SCHEMA = "guala.native.resident_organism_runtime.v3"
OBSERVATION_SCHEMA = "guala.native.resident_organism_observation.v3"
PREPARE_SCHEMA = "guala.native.resident_organism_prepare.v3"

DirectedPhysicalTransferEvidence = tuple[str, str, int, int]
TimedDirectedPhysicalTransferEvidence = tuple[int, DirectedPhysicalTransferEvidence]
ExactRationalEvidence = tuple[int, int]
LocalAffectiveGradientSettlementEvidence = tuple[
    int,
    int,
    int,
    int,
    int,
    int,
    int,
    ExactRationalEvidence,
    ExactRationalEvidence,
    ExactRationalEvidence,
]
LocalAffectivePlasticitySettlementEvidence = tuple[
    int,
    int,
    int,
    ExactRationalEvidence,
    ExactRationalEvidence,
    ExactRationalEvidence,
    ExactRationalEvidence,
    ExactRationalEvidence,
    tuple[ExactRationalEvidence, ExactRationalEvidence, ExactRationalEvidence],
    tuple[ExactRationalEvidence, ExactRationalEvidence, ExactRationalEvidence],
]
AffectiveBalanceTrajectoryEvidence = tuple[
    str,
    int,
    int,
    TimedDirectedPhysicalTransferEvidence | None,
    TimedDirectedPhysicalTransferEvidence | None,
    LocalAffectiveGradientSettlementEvidence | None,
    LocalAffectivePlasticitySettlementEvidence | None,
]
LocalizedFluidChemistryEvidence = tuple[
    str,
    int,
    int,
    int,
    tuple[int, ExactRationalEvidence, int, int, int, int, int],
    tuple[int, int, int, int, int, int, int, int],
    tuple[
        tuple[ExactRationalEvidence, ExactRationalEvidence, ExactRationalEvidence],
        tuple[ExactRationalEvidence, ExactRationalEvidence, ExactRationalEvidence],
        ExactRationalEvidence,
    ],
]
LocalizedMetabolicStrainEvidence = tuple[
    str,
    int,
    int,
    int,
    tuple[int, ...],
    int,
    int,
]

_FACTORY_AUTHORITY = object()


class NativeJointSourceView(Protocol):
    """Annotation only; the native prepare method enforces source type."""

    @property
    def port_count(self) -> int: ...


class NativeResidentObservationView(Protocol):
    @property
    def schema(self) -> str: ...

    @property
    def identity(self) -> str: ...

    @property
    def organism_tick(self) -> int: ...

    @property
    def fabric_generation(self) -> int: ...

    @property
    def mounted_generation(self) -> int: ...

    @property
    def state_bytes(self) -> int: ...

    @property
    def state_sha256(self) -> str: ...

    @property
    def fabric_bytes(self) -> int: ...

    @property
    def fabric_sha256(self) -> str: ...

    @property
    def articulated_body_axes(
        self,
    ) -> list[tuple[int, str, str, int, int, int, int]]: ...

    @property
    def articulated_body_lung_air_microlitres(self) -> int: ...

    @property
    def articulated_body_vocal_tract_areas_square_millimetres(
        self,
    ) -> list[int]: ...

    @property
    def articulated_body_state_bytes(self) -> int: ...

    @property
    def articulated_body_proprioception_initialized(self) -> bool: ...

    @property
    def articulated_body_state_sha256(self) -> str: ...

    @property
    def joint_field_count(self) -> int: ...

    @property
    def joint_neuron_count(self) -> int: ...

    @property
    def complete_neuron_count(self) -> int: ...

    @property
    def developmental_resting_neuron_count(self) -> int: ...

    @property
    def physically_transitioned_neuron_count(self) -> int: ...

    @property
    def metabolically_perturbed_body_receptor_count(self) -> int: ...

    @property
    def rest_recovered_neuron_count(self) -> int: ...

    @property
    def rest_drained_dissipation_quanta(self) -> int: ...

    @property
    def unmet_dissipation_quanta(self) -> int: ...

    @property
    def externally_perturbed_body_receptor_count(self) -> int: ...

    @property
    def externally_perturbed_neuron_lineages(self) -> list[str]: ...

    @property
    def cold_restore_authentication_count(self) -> int: ...

    @property
    def cold_restore_decode_count(self) -> int: ...

    @property
    def cold_restore_rebuilt_field_count(self) -> int: ...

    @property
    def mounted_step_completed(self) -> bool: ...

    @property
    def physical_transition_claimed(self) -> bool: ...

    @property
    def cognitive_formation_claimed(self) -> bool: ...

    @property
    def cognitive_ordinal(self) -> int: ...

    @property
    def cognitive_trace_count(self) -> int: ...

    @property
    def cognitive_mosaic_count(self) -> int: ...

    @property
    def mosaic_of_mosaics_count(self) -> int: ...

    @property
    def physical_frontier_routes(
        self,
    ) -> list[tuple[str, int, int, str, int, int, int, int]]: ...

    @property
    def changed_contact_channel_states(self) -> list[tuple[object, ...]]: ...

    @property
    def preceding_distinct_physical_frontier_routes(
        self,
    ) -> list[tuple[str, int, int, str, int, int, int, int]]: ...

    @property
    def reached_and_foregone_physical_frontier_routes(
        self,
    ) -> list[tuple[str, int, int, str, int, int, int, int]]: ...

    @property
    def working_causal_continuations(
        self,
    ) -> list[tuple[tuple[str, str, int, str], tuple[str, str, int, str]]]: ...

    @property
    def settled_working_frontier(
        self,
    ) -> list[tuple[str, str, int, str]]: ...

    @property
    def physical_prediction_alternatives(
        self,
    ) -> list[tuple[tuple[str, str, int, str], tuple[str, str, int, str]]]: ...

    @property
    def body_consequence_transfers(
        self,
    ) -> list[tuple[str, str, int, str]]: ...

    @property
    def affective_balance_trajectories(
        self,
    ) -> list[
        tuple[
            str,
            int,
            int,
            tuple[int, tuple[str, str, int, str]] | None,
            tuple[int, tuple[str, str, int, str]] | None,
            tuple[
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                tuple[str, str],
                tuple[str, str],
                tuple[str, str],
            ]
            | None,
            tuple[
                int,
                str,
                str,
                tuple[str, str],
                tuple[str, str],
                tuple[str, str],
                tuple[str, str],
                tuple[str, str],
                tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
                tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
            ]
            | None,
        ]
    ]: ...

    @property
    def localized_fluid_chemistry(self) -> list[tuple[object, ...]]: ...

    @property
    def localized_metabolic_strain_evaluated_body_receptor_lineages(
        self,
    ) -> list[str]: ...

    @property
    def localized_metabolic_strain(self) -> list[tuple[object, ...]]: ...

    @property
    def organic_mosaic_relations(
        self,
    ) -> list[
        tuple[
            list[str],
            list[str],
            list[tuple[str, str, int]],
            str,
            list[tuple[tuple[str, str, int, str], tuple[str, str, int, str]]],
            list[
                tuple[
                    tuple[str, str, int, str],
                    tuple[str, str, int, str],
                    tuple[str, str, int, str],
                    tuple[str, str, int, str],
                ]
            ],
        ]
    ]: ...

    @property
    def formation_activation_count(self) -> int: ...

    @property
    def partial_cue_reassembly_count(self) -> int: ...

    @property
    def endogenous_partial_cue_reassembly_count(self) -> int: ...

    @property
    def internally_reassembled_formation_cues(
        self,
    ) -> list[tuple[str, list[str]]]: ...

    @property
    def externally_reassembled_formation_frontiers(
        self,
    ) -> list[tuple[str, list[str], str]]: ...

    @property
    def python_callback_count(self) -> int: ...

    # Exact shared body-energy state. Local neuronal lanes keep their own
    # discrete reaction extents; only exact rational zeptojoules cross this
    # organism boundary.
    @property
    def available_energy_zeptojoules(self) -> tuple[int, int]: ...

    @property
    def spent_energy_zeptojoules(self) -> tuple[int, int]: ...

    @property
    def thermal_energy_zeptojoules(self) -> tuple[int, int]: ...

    @property
    def available_energy_capacity_zeptojoules(self) -> tuple[int, int]: ...

    @property
    def dissipated_energy_zeptojoules(self) -> tuple[int, int]: ...

    @property
    def dissipation_capacity_energy_zeptojoules(self) -> tuple[int, int]: ...

    @property
    def separated_elementary_charges(self) -> int: ...

    @property
    def energy_exhausted(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class ResidentContactGrowthEvidence:
    """Receipts for one prepared AUTHORED contact growth.

    Developmental authorship, not a sensory occurrence: it advances the
    organism tick and the fabric generation and nothing else.  The mounted
    joint generation is unchanged, and this boundary refuses any candidate
    that claims otherwise.
    """

    token: bytes
    token_hex: str
    predecessor_state_sha256: str
    prepared_state_sha256: str
    predecessor_organism_tick: int
    organism_tick: int
    predecessor_fabric_generation: int
    fabric_generation: int
    mounted_generation: int
    authored_contact_count: int


@dataclass(frozen=True, slots=True)
class ResidentCausalIntervalEvidence:
    """One transient exact causal boundary inside a one-seal trajectory."""

    predecessor_organism_tick: int
    organism_tick: int
    externally_perturbed_neuron_lineages: tuple[str, ...]
    internally_reassembled_formation_cues: tuple[
        tuple[str, tuple[str, ...]], ...
    ]
    externally_reassembled_formation_frontiers: tuple[
        tuple[str, tuple[str, ...], str], ...
    ]
    motor_unit_recruitments: tuple[
        tuple[
            str,
            int,
            int,
            tuple[tuple[str, int, str, int, int, int], ...],
            tuple[tuple[str, str, str, int, int, str, str], ...],
        ],
        ...,
    ]
    emitted_neuron_lineages: tuple[str, ...]
    changed_contact_channel_states: tuple[tuple[object, ...], ...]
    affective_balance_trajectories: tuple[
        AffectiveBalanceTrajectoryEvidence, ...
    ]
    causal_frontier_advances: tuple[tuple[str, str, int, int, str], ...]


@dataclass(frozen=True, slots=True)
class ResidentUnsealedIntakeEvidence:
    """Bounded projection from an open native intake before its sole seal."""

    token: bytes
    provisional_organism_tick: int
    pause_interval_ordinal: int | None
    motor_unit_recruitments: tuple[
        tuple[
            str,
            int,
            int,
            tuple[tuple[str, int, str, int, int, int], ...],
            tuple[tuple[str, str, str, int, int, str, str], ...],
        ],
        ...,
    ]
    body_effector_bindings: tuple[tuple[str, str, str, int], ...]
    articulated_body_axes: tuple[
        tuple[int, str, str, int, int, int, int], ...
    ]
    articulated_body_consequences: tuple[
        tuple[int, str, str, int, int, int, int, int, int, int, int], ...
    ]
    articulatory_unit_recruitments: tuple[
        tuple[
            str,
            int,
            int,
            tuple[tuple[str, int, str, int, int, int], ...],
        ],
        ...,
    ]


@dataclass(frozen=True, slots=True)
class ResidentPrepareEvidence:
    """Fixed receipt and causal evidence for one native pending candidate."""

    token: bytes
    token_hex: str
    predecessor_state_sha256: str
    prepared_state_sha256: str
    predecessor_organism_tick: int
    organism_tick: int
    predecessor_fabric_generation: int
    fabric_generation: int
    predecessor_mounted_generation: int
    mounted_generation: int
    predecessor_authentication_count: int
    predecessor_decode_count: int
    predecessor_rebuilt_field_count: int
    current_cohort_evaluation_count: int
    successor_seal_count: int
    dsf_delivery_count: int
    complete_neuron_fractal_count: int
    recurrent_complete_neuron_fractal_count: int
    physical_transition_claimed: bool
    cognitive_formation_claimed: bool
    cognitive_ordinal: int
    cognitive_trace_count: int
    cognitive_mosaic_count: int
    formation_activation_count: int
    partial_cue_reassembly_count: int
    endogenous_partial_cue_reassembly_count: int
    internally_reassembled_formation_cues: tuple[
        tuple[str, tuple[str, ...]], ...
    ]
    externally_reassembled_formation_frontiers: tuple[
        tuple[str, tuple[str, ...], str], ...
    ]
    python_callback_count: int
    complete_neuron_count: int = 0
    developmental_resting_neuron_count: int = 0
    physically_transitioned_neuron_count: int = 0
    metabolically_perturbed_body_receptor_count: int = 0
    rest_recovered_neuron_count: int = 0
    rest_drained_dissipation_quanta: int = 0
    unmet_dissipation_quanta: int = 0
    externally_perturbed_body_receptor_count: int = 0
    externally_perturbed_neuron_lineages: tuple[str, ...] = ()
    receptor_ingress_sense_counts: tuple[int, int, int, int, int, int] = (
        0,
        0,
        0,
        0,
        0,
        0,
    )
    receptor_ingress_changing_count: int = 0
    receptor_ingress_quiescent_count: int = 0
    motor_unit_recruitments: tuple[
        tuple[
            str,
            int,
            int,
            tuple[tuple[str, int, str, int, int, int], ...],
            tuple[tuple[str, str, str, int, int, str, str], ...],
        ],
        ...,
    ] = ()
    appended_physically_transitioned_neuron_count: int = 0
    appended_complete_neuron_fractal_count: int = 0
    appended_externally_perturbed_body_receptor_count: int = 0
    appended_articulatory_unit_recruitment_count: int = 0
    body_effector_bindings: tuple[tuple[str, str, str, int], ...] = ()
    articulated_body_consequences: tuple[
        tuple[int, str, str, int, int, int, int, int, int, int, int], ...
    ] = ()
    body_proprioceptive_sources: tuple[bytes, ...] = ()
    body_proprioceptive_source_extents: tuple[
        tuple[int, int, int, int, int], ...
    ] = ()
    articulatory_unit_recruitments: tuple[
        tuple[
            str,
            int,
            int,
            tuple[tuple[str, int, str, int, int, int], ...],
        ],
        ...,
    ] = ()
    emitted_neuron_fractals: tuple[
        tuple[str, tuple[tuple[str, int, bool, int, int], ...]], ...
    ] = ()
    active_physical_bonds: tuple[tuple[str, str, int], ...] = ()
    changed_contact_channel_states: tuple[tuple[object, ...], ...] = ()
    physical_frontier_routes: tuple[
        tuple[str, int, int, str, int, int, int, int], ...
    ] = ()
    preceding_distinct_physical_frontier_routes: tuple[
        tuple[str, int, int, str, int, int, int, int], ...
    ] = ()
    reached_and_foregone_physical_frontier_routes: tuple[
        tuple[str, int, int, str, int, int, int, int], ...
    ] = ()
    working_causal_continuations: tuple[
        tuple[
            tuple[str, str, int, int],
            tuple[str, str, int, int],
        ],
        ...,
    ] = ()
    settled_working_frontier: tuple[tuple[str, str, int, int], ...] = ()
    physical_prediction_alternatives: tuple[
        tuple[
            tuple[str, str, int, int],
            tuple[str, str, int, int],
        ],
        ...,
    ] = ()
    body_consequence_transfers: tuple[tuple[str, str, int, int], ...] = ()
    affective_balance_trajectories: tuple[
        AffectiveBalanceTrajectoryEvidence, ...
    ] = ()
    localized_fluid_chemistry: tuple[LocalizedFluidChemistryEvidence, ...] = ()
    localized_metabolic_strain_evaluated_body_receptor_lineages: tuple[
        str, ...
    ] = ()
    localized_metabolic_strain: tuple[LocalizedMetabolicStrainEvidence, ...] = ()
    organic_mosaic_relations: tuple[
        tuple[
            tuple[str, ...],
            tuple[str, ...],
            tuple[tuple[str, str, int], ...],
            str,
            tuple[
                tuple[
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                ],
                ...,
            ],
            tuple[
                tuple[
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                ],
                ...,
            ],
        ],
        ...,
    ] = ()
    causal_interval_evidence: tuple[ResidentCausalIntervalEvidence, ...] = ()


def _native_core():
    return importlib.import_module("guala_core")


def _positive_integer(value: object, label: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
        or value > sys.maxsize
    ):
        raise ValueError(f"resident organism {label} must be a positive native integer")
    return value


def _nonnegative_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RuntimeError(f"resident organism {label} is not a nonnegative integer")
    return value


def _signed_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuntimeError(f"resident organism {label} is not an exact signed integer")
    return value


def _positive_exact_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"resident organism {label} is not a positive exact integer")
    return value


def _positive_decimal_integer(value: object, label: str) -> int:
    if (
        not isinstance(value, str)
        or not value
        or any(character not in "0123456789" for character in value)
        or value[0] == "0"
    ):
        raise RuntimeError(f"resident organism {label} is not a positive exact integer")
    return int(value)


def _nonnegative_decimal_integer(value: object, label: str) -> int:
    if (
        not isinstance(value, str)
        or not value
        or any(character not in "0123456789" for character in value)
        or (len(value) > 1 and value[0] == "0")
    ):
        raise RuntimeError(f"resident organism {label} is not a nonnegative exact integer")
    return int(value)


def _canonical_sha256(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise RuntimeError(f"resident organism {label} is not canonical SHA-256")
    return value


def _canonical_lineage_hex(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 32
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise RuntimeError(f"resident organism {label} is not canonical")
    return value


def _articulatory_unit_recruitments(
    value: object,
) -> tuple[
    tuple[
        str,
        int,
        int,
        tuple[tuple[str, int, str, int, int, int], ...],
    ],
    ...,
]:
    """Validate the exact native layer-12/layer-13 transfer projection."""

    if not isinstance(value, list):
        raise RuntimeError("articulatory-unit recruitments changed format")
    validated: list[
        tuple[
            str,
            int,
            int,
            tuple[tuple[str, int, str, int, int, int], ...],
        ]
    ] = []
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 4:
            raise RuntimeError("articulatory-unit recruitment changed format")
        lineage = _canonical_lineage_hex(raw[0], "articulatory-unit lineage")
        topology_index = _nonnegative_integer(
            raw[1], "articulatory-unit topology index"
        )
        outward_elementary_carriers = _positive_integer(
            raw[2], "articulatory-unit outward elementary carriers"
        )
        if not isinstance(raw[3], list) or not raw[3]:
            raise RuntimeError("articulatory-unit motor transfers changed format")
        motor_transfers: list[tuple[str, int, str, int, int, int]] = []
        for transfer in raw[3]:
            if not isinstance(transfer, tuple) or len(transfer) != 6:
                raise RuntimeError("articulatory-unit motor transfer changed format")
            sender = _canonical_lineage_hex(
                transfer[0], "articulatory motor sender"
            )
            sender_layer = _nonnegative_integer(
                transfer[1], "articulatory motor sender layer"
            )
            receiver = _canonical_lineage_hex(
                transfer[2], "articulatory motor receiver"
            )
            receiver_layer = _nonnegative_integer(
                transfer[3], "articulatory motor receiver layer"
            )
            parallel_ordinal = _nonnegative_integer(
                transfer[4], "articulatory motor parallel ordinal"
            )
            transferred_whole_carriers = _positive_integer(
                transfer[5], "articulatory motor transferred whole carriers"
            )
            if sender == receiver or not (
                sender == lineage
                and sender_layer == 13
                and receiver_layer == 12
                or receiver == lineage
                and receiver_layer == 13
                and sender_layer == 12
            ):
                raise RuntimeError(
                    "articulatory-unit preparation is not an exact layer 12/layer 13 contact transfer"
                )
            motor_transfers.append(
                (
                    sender,
                    sender_layer,
                    receiver,
                    receiver_layer,
                    parallel_ordinal,
                    transferred_whole_carriers,
                )
            )
        validated.append(
            (
                lineage,
                topology_index,
                outward_elementary_carriers,
                tuple(motor_transfers),
            )
        )
    return tuple(validated)


def _physical_frontier_route_evidence(
    value: object, label: str
) -> tuple[tuple[str, int, int, str, int, int, int, int], ...]:
    if not isinstance(value, list):
        raise RuntimeError(f"resident organism {label} changed format")
    routes: list[tuple[str, int, int, str, int, int, int, int]] = []
    seen: set[tuple[str, str, int]] = set()
    for raw_route in value:
        if not isinstance(raw_route, tuple) or len(raw_route) != 8:
            raise RuntimeError(f"resident organism {label} changed format")
        route = (
            _canonical_lineage_hex(raw_route[0], f"{label} seed lineage"),
            _nonnegative_integer(raw_route[1], f"{label} seed layer"),
            _nonnegative_integer(raw_route[2], f"{label} seed topology"),
            _canonical_lineage_hex(raw_route[3], f"{label} adjacent lineage"),
            _nonnegative_integer(raw_route[4], f"{label} adjacent layer"),
            _nonnegative_integer(raw_route[5], f"{label} adjacent topology"),
            _nonnegative_integer(raw_route[6], f"{label} parallel ordinal"),
            _signed_integer(raw_route[7], f"{label} outward carriers"),
        )
        if route[0] == route[3]:
            raise RuntimeError(f"resident organism {label} joined one lineage to itself")
        identity = (route[0], route[3], route[6])
        if identity in seen:
            raise RuntimeError(f"resident organism {label} repeated one route")
        seen.add(identity)
        routes.append(route)
    return tuple(routes)


def _changed_contact_channel_state_evidence(
    value: object,
) -> tuple[tuple[object, ...], ...]:
    if not isinstance(value, list):
        raise RuntimeError("resident changed contact-channel evidence changed format")
    changes: list[tuple[object, ...]] = []
    seen: set[tuple[int, str, str, int]] = set()
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 6:
            raise RuntimeError("resident changed contact-channel evidence changed format")
        cognitive_ordinal = _nonnegative_integer(
            raw[0], "changed contact-channel cognitive ordinal"
        )
        left = _canonical_lineage_hex(raw[1], "changed contact-channel left lineage")
        right = _canonical_lineage_hex(raw[2], "changed contact-channel right lineage")
        if left >= right:
            raise RuntimeError("changed contact-channel endpoints are not canonical")
        parallel_ordinal = _nonnegative_integer(
            raw[3], "changed contact-channel parallel ordinal"
        )
        states: list[tuple[object, ...]] = []
        for label, state in (("predecessor", raw[4]), ("successor", raw[5])):
            if not isinstance(state, tuple) or len(state) != 3:
                raise RuntimeError(f"changed contact-channel {label} changed format")
            states.append(
                (
                    _nonnegative_decimal_integer(
                        state[0], f"changed contact-channel {label} population"
                    ),
                    _exact_rational_evidence(
                        state[1], f"changed contact-channel {label} work phase"
                    ),
                    _exact_rational_evidence(
                        state[2], f"changed contact-channel {label} conductance"
                    ),
                )
            )
        if states[0] == states[1]:
            raise RuntimeError("changed contact-channel evidence carried no change")
        identity = (cognitive_ordinal, left, right, parallel_ordinal)
        if identity in seen:
            raise RuntimeError("changed contact-channel evidence repeated one contact")
        seen.add(identity)
        changes.append((cognitive_ordinal, left, right, parallel_ordinal, *states))
    return tuple(changes)


def _internally_reassembled_formation_cue_evidence(
    value: object,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if not isinstance(value, list):
        raise RuntimeError("internally reassembled formation cues changed format")
    observed: list[tuple[str, tuple[str, ...]]] = []
    for raw_cue in value:
        if not isinstance(raw_cue, tuple) or len(raw_cue) != 2:
            raise RuntimeError("internally reassembled formation cue changed format")
        raw_receipt, raw_cues = raw_cue
        if not isinstance(raw_cues, list) or not raw_cues:
            raise RuntimeError("internally reassembled formation cue is empty")
        receipt = _canonical_sha256(
            raw_receipt, "internally reassembled formation receipt"
        )
        cues = tuple(
            _canonical_lineage_hex(lineage, "internal formation cue lineage")
            for lineage in raw_cues
        )
        if tuple(sorted(set(cues))) != cues:
            raise RuntimeError("internally reassembled formation cue is not canonical")
        observed.append((receipt, cues))
    result = tuple(observed)
    if len(set(result)) != len(result):
        raise RuntimeError("internally reassembled formation cue repeated")
    return result


def _externally_reassembled_formation_frontier_evidence(
    value: object,
) -> tuple[tuple[str, tuple[str, ...], str], ...]:
    if not isinstance(value, list):
        raise RuntimeError("externally reassembled formation frontiers changed format")
    observed: list[tuple[str, tuple[str, ...], str]] = []
    for raw_frontier in value:
        if not isinstance(raw_frontier, tuple) or len(raw_frontier) != 3:
            raise RuntimeError("externally reassembled formation frontier changed format")
        raw_receipt, raw_cues, raw_recurrent = raw_frontier
        if not isinstance(raw_cues, list) or not raw_cues:
            raise RuntimeError("externally reassembled formation frontier has no cue")
        receipt = _canonical_sha256(
            raw_receipt, "externally reassembled formation receipt"
        )
        cues = tuple(
            _canonical_lineage_hex(lineage, "external formation cue lineage")
            for lineage in raw_cues
        )
        recurrent = _canonical_lineage_hex(
            raw_recurrent, "external formation recurrent lineage"
        )
        if tuple(sorted(set(cues))) != cues or recurrent in cues:
            raise RuntimeError("externally reassembled formation frontier is not canonical")
        observed.append((receipt, cues, recurrent))
    result = tuple(observed)
    if len(set(result)) != len(result):
        raise RuntimeError("externally reassembled formation frontier repeated")
    return result


def _motor_unit_recruitment_evidence(
    value: object,
) -> tuple[
    tuple[
        str,
        int,
        int,
        tuple[tuple[str, int, str, int, int, int], ...],
        tuple[tuple[str, str, str, int, int, str, str], ...],
    ],
    ...,
]:
    if not isinstance(value, list):
        raise RuntimeError("motor-unit recruitments changed format")
    observed = []
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 5:
            raise RuntimeError("motor-unit recruitment changed format")
        lineage = _canonical_lineage_hex(raw[0], "motor-unit lineage")
        topology_index = _nonnegative_integer(
            raw[1], "motor-unit topology index"
        )
        outward_elementary_carriers = _positive_integer(
            raw[2], "motor-unit outward elementary carriers"
        )
        if not isinstance(raw[3], list) or not raw[3]:
            raise RuntimeError("motor-unit preparation transfers changed format")
        preparation_transfers = []
        for transfer in raw[3]:
            if not isinstance(transfer, tuple) or len(transfer) != 6:
                raise RuntimeError("motor-unit preparation transfer changed format")
            sender = _canonical_lineage_hex(
                transfer[0], "motor preparation sender"
            )
            sender_layer = _nonnegative_integer(
                transfer[1], "motor preparation sender layer"
            )
            receiver = _canonical_lineage_hex(
                transfer[2], "motor preparation receiver"
            )
            receiver_layer = _nonnegative_integer(
                transfer[3], "motor preparation receiver layer"
            )
            parallel_ordinal = _nonnegative_integer(
                transfer[4], "motor preparation parallel ordinal"
            )
            transferred_whole_carriers = _positive_integer(
                transfer[5], "motor preparation transferred whole carriers"
            )
            if sender == receiver or not (
                (
                    sender == lineage
                    and sender_layer == 12
                    and receiver_layer == 11
                )
                or (
                    receiver == lineage
                    and receiver_layer == 12
                    and sender_layer == 11
                )
            ):
                raise RuntimeError(
                    "motor-unit preparation is not an exact layer 11/layer 12 contact transfer"
                )
            preparation_transfers.append(
                (
                    sender,
                    sender_layer,
                    receiver,
                    receiver_layer,
                    parallel_ordinal,
                    transferred_whole_carriers,
                )
            )
        if not isinstance(raw[4], list) or not raw[4]:
            raise RuntimeError("motor-unit body afferent paths changed format")
        body_afferent_paths = []
        for path in raw[4]:
            if not isinstance(path, tuple) or len(path) != 7:
                raise RuntimeError("motor-unit body afferent path changed format")
            regulation = _canonical_lineage_hex(
                path[0], "motor body-regulation lineage"
            )
            integration = _canonical_lineage_hex(
                path[1], "motor body-integration lineage"
            )
            receptor = _canonical_lineage_hex(
                path[2], "motor body-receptor lineage"
            )
            sense_layer = _nonnegative_integer(
                path[3], "motor body-receptor sense layer"
            )
            receptor_topology = _nonnegative_integer(
                path[4], "motor body-receptor topology index"
            )
            sensor_id = path[5]
            substream_id = path[6]
            if (
                sense_layer != 5
                or len({lineage, regulation, integration, receptor}) != 4
                or not isinstance(sensor_id, str)
                or not sensor_id
                or not isinstance(substream_id, str)
                or not substream_id
            ):
                raise RuntimeError("motor-unit body afferent path is not physical")
            body_afferent_paths.append(
                (
                    regulation,
                    integration,
                    receptor,
                    sense_layer,
                    receptor_topology,
                    sensor_id,
                    substream_id,
                )
            )
        if tuple(sorted(set(body_afferent_paths))) != tuple(body_afferent_paths):
            raise RuntimeError("motor-unit body afferent paths are not canonical")
        observed.append(
            (
                lineage,
                topology_index,
                outward_elementary_carriers,
                tuple(preparation_transfers),
                tuple(body_afferent_paths),
            )
        )
    return tuple(observed)


def _articulated_body_axis_evidence(
    value: object,
) -> tuple[tuple[int, str, str, int, int, int, int], ...]:
    if not isinstance(value, list) or len(value) != 37:
        raise RuntimeError("resident articulated body axis count changed")
    observed: list[tuple[int, str, str, int, int, int, int]] = []
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 7:
            raise RuntimeError("resident articulated body axis changed format")
        ordinal = _nonnegative_integer(raw[0], "body axis ordinal")
        name, unit = raw[1], raw[2]
        position = _signed_integer(raw[3], "body axis position")
        minimum = _signed_integer(raw[4], "body axis minimum")
        neutral = _signed_integer(raw[5], "body axis neutral")
        maximum = _signed_integer(raw[6], "body axis maximum")
        if (
            ordinal != len(observed)
            or not isinstance(name, str)
            or not name
            or unit not in {"millidegree", "micrometre", "square_millimetre"}
            or not minimum <= position <= maximum
            or not minimum <= neutral <= maximum
        ):
            raise RuntimeError("resident articulated body anatomy is not canonical")
        observed.append(
            (ordinal, name, unit, position, minimum, neutral, maximum)
        )
    return tuple(observed)


def _articulated_body_consequence_evidence(
    value: object,
    *,
    predecessor_organism_tick: int,
    organism_tick: int,
) -> tuple[tuple[int, str, str, int, int, int, int, int, int, int, int], ...]:
    if not isinstance(value, list):
        raise RuntimeError("articulated body consequences changed format")
    observed: list[
        tuple[int, str, str, int, int, int, int, int, int, int, int]
    ] = []
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 11:
            raise RuntimeError("articulated body consequence changed format")
        source_tick = _nonnegative_integer(raw[0], "body consequence source tick")
        axis, unit = raw[1], raw[2]
        predecessor_position = _signed_integer(raw[3], "body predecessor position")
        successor_position = _signed_integer(raw[4], "body successor position")
        signed_displacement = _signed_integer(raw[5], "body signed displacement")
        toward_minimum = _nonnegative_integer(raw[6], "body toward-minimum carriers")
        toward_maximum = _nonnegative_integer(raw[7], "body toward-maximum carriers")
        opposed = _nonnegative_integer(raw[8], "body opposed carriers")
        applied = _nonnegative_integer(raw[9], "body applied displacement")
        stalled = _nonnegative_integer(raw[10], "body stalled carriers")
        net = abs(toward_maximum - toward_minimum)
        if (
            source_tick < predecessor_organism_tick
            or source_tick >= organism_tick
            or not isinstance(axis, str)
            or not axis
            or unit not in {"millidegree", "micrometre", "square_millimetre"}
            or successor_position - predecessor_position != signed_displacement
            or opposed != min(toward_minimum, toward_maximum)
            or applied != abs(signed_displacement)
            or applied + stalled != net
        ):
            raise RuntimeError("articulated body consequence lost exact mechanics")
        observed.append(
            (
                source_tick,
                axis,
                unit,
                predecessor_position,
                successor_position,
                signed_displacement,
                toward_minimum,
                toward_maximum,
                opposed,
                applied,
                stalled,
            )
        )
    return tuple(observed)


def _causal_interval_evidence(
    value: object,
    predecessor_organism_tick: int,
) -> tuple[ResidentCausalIntervalEvidence, ...]:
    if not isinstance(value, list):
        raise RuntimeError("causal interval evidence changed format")
    intervals = []
    for index, raw in enumerate(value):
        if not isinstance(raw, tuple) or len(raw) != 8:
            raise RuntimeError("causal interval evidence changed format")
        (
            raw_external,
            raw_cues,
            raw_external_frontiers,
            raw_motors,
            raw_emitted,
            raw_changes,
            raw_affect,
            raw_frontier,
        ) = raw
        if not isinstance(raw_external, list):
            raise RuntimeError("causal interval external lineages changed format")
        external = tuple(
            _canonical_lineage_hex(lineage, "causal interval external lineage")
            for lineage in raw_external
        )
        if len(set(external)) != len(external):
            raise RuntimeError("causal interval external lineage repeated")
        if not isinstance(raw_emitted, list):
            raise RuntimeError("causal interval emitted lineages changed format")
        emitted = tuple(
            _canonical_lineage_hex(lineage, "causal interval emitted lineage")
            for lineage in raw_emitted
        )
        if len(set(emitted)) != len(emitted):
            raise RuntimeError("causal interval emitted lineage repeated")
        if not isinstance(raw_frontier, list):
            raise RuntimeError("causal interval frontier changed format")
        frontier = []
        for transfer in raw_frontier:
            if not isinstance(transfer, tuple) or len(transfer) != 5:
                raise RuntimeError("causal interval frontier changed format")
            directed = _directed_physical_transfer_evidence(
                transfer[:4], "causal interval frontier"
            )
            advancing = _canonical_lineage_hex(
                transfer[4], "causal interval advancing lineage"
            )
            if advancing not in directed[:2]:
                raise RuntimeError("causal interval frontier left its contact")
            frontier.append((*directed, advancing))
        canonical_frontier = tuple(frontier)
        if len(set(canonical_frontier)) != len(canonical_frontier):
            raise RuntimeError("causal interval frontier repeated a transfer")
        predecessor_tick = predecessor_organism_tick + index
        intervals.append(
            ResidentCausalIntervalEvidence(
                predecessor_organism_tick=predecessor_tick,
                organism_tick=predecessor_tick + 1,
                externally_perturbed_neuron_lineages=external,
                internally_reassembled_formation_cues=(
                    _internally_reassembled_formation_cue_evidence(raw_cues)
                ),
                externally_reassembled_formation_frontiers=(
                    _externally_reassembled_formation_frontier_evidence(
                        raw_external_frontiers
                    )
                ),
                motor_unit_recruitments=_motor_unit_recruitment_evidence(raw_motors),
                emitted_neuron_lineages=emitted,
                changed_contact_channel_states=(
                    _changed_contact_channel_state_evidence(raw_changes)
                ),
                affective_balance_trajectories=(
                    _affective_balance_trajectory_evidence(raw_affect)
                ),
                causal_frontier_advances=canonical_frontier,
            )
        )
    return tuple(intervals)


def _directed_physical_transfer_evidence(
    value: object, label: str
) -> tuple[str, str, int, int]:
    if not isinstance(value, tuple) or len(value) != 4:
        raise RuntimeError(f"resident organism {label} changed format")
    carriers_text = value[3]
    if not isinstance(carriers_text, str) or not carriers_text.isdecimal():
        raise RuntimeError(f"resident organism {label} lost exact carriers")
    carriers = int(carriers_text)
    if carriers <= 0:
        raise RuntimeError(f"resident organism {label} carried no material")
    sender = _canonical_lineage_hex(value[0], f"{label} sender")
    receiver = _canonical_lineage_hex(value[1], f"{label} receiver")
    if sender == receiver:
        raise RuntimeError(f"resident organism {label} joined one lineage to itself")
    return (
        sender,
        receiver,
        _nonnegative_integer(value[2], f"{label} bond ordinal"),
        carriers,
    )


def _working_causal_continuation_evidence(
    value: object,
) -> tuple[
    tuple[
        tuple[str, str, int, int],
        tuple[str, str, int, int],
    ],
    ...,
]:
    if not isinstance(value, list) or len(value) > 1:
        raise RuntimeError("resident organism working continuation changed bounds")
    paths = []
    for raw_path in value:
        if not isinstance(raw_path, tuple) or len(raw_path) != 2:
            raise RuntimeError("resident organism working continuation changed format")
        first = _directed_physical_transfer_evidence(
            raw_path[0], "working continuation first transfer"
        )
        second = _directed_physical_transfer_evidence(
            raw_path[1], "working continuation second transfer"
        )
        if first[1] != second[0]:
            raise RuntimeError("resident organism working continuation is not adjacent")
        paths.append((first, second))
    return tuple(paths)


def _settled_working_frontier_evidence(
    value: object,
) -> tuple[tuple[str, str, int, int], ...]:
    if not isinstance(value, list) or len(value) > 1:
        raise RuntimeError("resident organism settled working frontier changed bounds")
    return tuple(
        _directed_physical_transfer_evidence(
            transfer, "settled working frontier transfer"
        )
        for transfer in value
    )


def _physical_prediction_alternative_evidence(
    value: object,
) -> tuple[
    tuple[
        tuple[str, str, int, int],
        tuple[str, str, int, int],
    ],
    ...,
]:
    if not isinstance(value, list) or len(value) not in (0, 2):
        raise RuntimeError("resident organism prediction alternatives changed bounds")
    paths = tuple(
        (
            _directed_physical_transfer_evidence(
                raw_path[0], "prediction alternative first transfer"
            ),
            _directed_physical_transfer_evidence(
                raw_path[1], "prediction alternative second transfer"
            ),
        )
        for raw_path in value
        if isinstance(raw_path, tuple) and len(raw_path) == 2
    )
    if len(paths) != len(value):
        raise RuntimeError("resident organism prediction alternative changed format")
    if paths and (
        paths[0][0][1] != paths[0][1][0]
        or paths[1][0][1] != paths[1][1][0]
        or paths[0][0][0] != paths[1][0][0]
        or paths[0][0][1] == paths[1][0][1]
        or paths[0][1][1] == paths[1][1][1]
    ):
        raise RuntimeError("resident organism prediction alternatives lost topology")
    return paths


def _body_consequence_transfer_evidence(
    value: object,
) -> tuple[tuple[str, str, int, int], ...]:
    if not isinstance(value, list) or len(value) > 1:
        raise RuntimeError("resident organism body consequence changed bounds")
    return tuple(
        _directed_physical_transfer_evidence(
            transfer, "body consequence transfer"
        )
        for transfer in value
    )


def _exact_rational_evidence(value: object, label: str) -> ExactRationalEvidence:
    if not isinstance(value, tuple) or len(value) != 2:
        raise RuntimeError(f"resident organism {label} changed format")
    numerator_text, denominator_text = value
    if (
        not isinstance(numerator_text, str)
        or not isinstance(denominator_text, str)
        or not numerator_text.removeprefix("-").isdecimal()
        or not denominator_text.isdecimal()
    ):
        raise RuntimeError(f"resident organism {label} lost exact rational")
    numerator = int(numerator_text)
    denominator = int(denominator_text)
    if denominator <= 0:
        raise RuntimeError(f"resident organism {label} has invalid denominator")
    return numerator, denominator


def _timed_directed_physical_transfer_evidence(
    value: object, label: str
) -> TimedDirectedPhysicalTransferEvidence:
    if not isinstance(value, tuple) or len(value) != 2:
        raise RuntimeError(f"resident organism {label} changed format")
    return (
        _nonnegative_integer(value[0], f"{label} cognitive ordinal"),
        _directed_physical_transfer_evidence(value[1], label),
    )


def _affective_balance_trajectory_evidence(
    value: object,
) -> tuple[AffectiveBalanceTrajectoryEvidence, ...]:
    if not isinstance(value, list):
        raise RuntimeError("resident organism affective-balance trajectory changed format")
    trajectories: list[AffectiveBalanceTrajectoryEvidence] = []
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 7:
            raise RuntimeError(
                "resident organism affective-balance trajectory changed format"
            )
        lineage = _canonical_lineage_hex(raw[0], "affective-balance lineage")
        layer = _nonnegative_integer(raw[1], "affective-balance layer")
        topology = _nonnegative_integer(raw[2], "affective-balance topology")
        if layer != 10:
            raise RuntimeError("resident organism affective-balance cell left layer 10")
        association = (
            None
            if raw[3] is None
            else _timed_directed_physical_transfer_evidence(
                raw[3], "affective-balance association influence"
            )
        )
        body = (
            None
            if raw[4] is None
            else _timed_directed_physical_transfer_evidence(
                raw[4], "affective-balance body influence"
            )
        )
        for influence in (association, body):
            if influence is not None and lineage not in influence[1][:2]:
                raise RuntimeError(
                    "resident organism affective-balance influence missed its cell"
                )
        gradient = None
        if raw[5] is not None:
            if not isinstance(raw[5], tuple) or len(raw[5]) != 10:
                raise RuntimeError(
                    "resident organism affective-balance gradient changed format"
                )
            gradient = (
                _nonnegative_integer(raw[5][0], "affective-balance gradient ordinal"),
                _signed_integer(raw[5][1], "affective-balance predecessor charge"),
                _signed_integer(raw[5][2], "affective-balance post-gradient charge"),
                _signed_integer(raw[5][3], "affective-balance successor charge"),
                _signed_integer(raw[5][4], "affective-balance returned carriers"),
                _signed_integer(raw[5][5], "affective-balance pumped carriers"),
                _signed_integer(raw[5][6], "affective-balance remaining charge"),
                _exact_rational_evidence(raw[5][7], "affective-balance gradient work"),
                _exact_rational_evidence(
                    raw[5][8], "affective-balance environment delivery"
                ),
                _exact_rational_evidence(raw[5][9], "affective-balance heat export"),
            )
        plasticity = None
        if raw[6] is not None:
            if not isinstance(raw[6], tuple) or len(raw[6]) != 10:
                raise RuntimeError(
                    "resident organism affective-balance plasticity changed format"
                )
            predecessor_reservoir = raw[6][8]
            successor_reservoir = raw[6][9]
            if (
                not isinstance(predecessor_reservoir, tuple)
                or len(predecessor_reservoir) != 3
                or not isinstance(successor_reservoir, tuple)
                or len(successor_reservoir) != 3
            ):
                raise RuntimeError(
                    "resident organism affective-balance plastic reservoir changed format"
                )
            plasticity = (
                _nonnegative_integer(raw[6][0], "affective-balance plastic ordinal"),
                _positive_decimal_integer(
                    raw[6][1], "affective-balance incident catalyst"
                ),
                _nonnegative_decimal_integer(
                    raw[6][2], "affective-balance reaction extent"
                ),
                _exact_rational_evidence(raw[6][3], "affective-balance delivered work"),
                _exact_rational_evidence(
                    raw[6][4], "affective-balance predecessor gate residue"
                ),
                _exact_rational_evidence(
                    raw[6][5], "affective-balance successor gate residue"
                ),
                _exact_rational_evidence(
                    raw[6][6], "affective-balance predecessor plastic rest"
                ),
                _exact_rational_evidence(
                    raw[6][7], "affective-balance successor plastic rest"
                ),
                tuple(
                    _exact_rational_evidence(
                        item, "affective-balance predecessor plastic reservoir"
                    )
                    for item in predecessor_reservoir
                ),
                tuple(
                    _exact_rational_evidence(
                        item, "affective-balance successor plastic reservoir"
                    )
                    for item in successor_reservoir
                ),
            )
        trajectories.append(
            (lineage, layer, topology, association, body, gradient, plasticity)
        )
    if tuple(item[0] for item in trajectories) != tuple(
        sorted({item[0] for item in trajectories})
    ):
        raise RuntimeError("resident organism affective-balance trajectories are not canonical")
    return tuple(trajectories)


def _localized_fluid_chemistry_evidence(
    value: object,
) -> tuple[LocalizedFluidChemistryEvidence, ...]:
    if not isinstance(value, list) or len(value) > 1:
        raise RuntimeError("resident organism localized fluid chemistry changed format")
    settlements: list[LocalizedFluidChemistryEvidence] = []
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 7:
            raise RuntimeError("resident organism localized fluid chemistry changed format")
        lineage = _canonical_lineage_hex(raw[0], "localized fluid target lineage")
        layer = _nonnegative_integer(raw[1], "localized fluid target layer")
        topology = _nonnegative_integer(raw[2], "localized fluid target topology")
        ordinal = _positive_integer(raw[3], "localized fluid cognitive ordinal")
        contact = raw[4]
        carrier = raw[5]
        reservoir = raw[6]
        if not isinstance(contact, tuple) or len(contact) != 7:
            raise RuntimeError("resident organism localized fluid contact changed format")
        contact_evidence = (
            _positive_integer(contact[0], "localized fluid interval"),
            _exact_rational_evidence(contact[1], "localized fluid contact power"),
            _positive_integer(contact[2], "localized fluid reached count"),
            _positive_integer(contact[3], "localized fluid changed reached count"),
            _nonnegative_integer(contact[4], "localized fluid unchanged unreached count"),
            _nonnegative_integer(
                contact[5], "localized fluid unchanged developmental resting count"
            ),
            _nonnegative_integer(contact[6], "localized fluid changed unreached count"),
        )
        if contact_evidence[3] > contact_evidence[2] or contact_evidence[6] != 0:
            raise RuntimeError("resident organism localized fluid locality was not preserved")
        if not isinstance(carrier, tuple) or len(carrier) != 8:
            raise RuntimeError("resident organism localized fluid carrier changed format")
        carrier_evidence = (
            _signed_integer(carrier[0], "localized fluid predecessor charge"),
            _signed_integer(carrier[1], "localized fluid successor charge"),
            _nonnegative_decimal_integer(carrier[2], "localized fluid predecessor intracellular"),
            _nonnegative_decimal_integer(carrier[3], "localized fluid predecessor extracellular"),
            _nonnegative_decimal_integer(carrier[4], "localized fluid successor intracellular"),
            _nonnegative_decimal_integer(carrier[5], "localized fluid successor extracellular"),
            _signed_integer(carrier[6], "localized fluid returned carriers"),
            _signed_integer(carrier[7], "localized fluid pumped carriers"),
        )
        if carrier_evidence[2] + carrier_evidence[3] != carrier_evidence[4] + carrier_evidence[5]:
            raise RuntimeError("resident organism localized fluid carrier material changed")
        if not isinstance(reservoir, tuple) or len(reservoir) != 3:
            raise RuntimeError("resident organism localized fluid reservoir changed format")
        reservoir_states: list[
            tuple[ExactRationalEvidence, ExactRationalEvidence, ExactRationalEvidence]
        ] = []
        for index, state in enumerate(reservoir[:2]):
            if not isinstance(state, tuple) or len(state) != 3:
                raise RuntimeError("resident organism localized fluid reservoir changed format")
            reservoir_states.append(
                (
                    _exact_rational_evidence(state[0], f"localized fluid reservoir {index} available"),
                    _exact_rational_evidence(state[1], f"localized fluid reservoir {index} spent"),
                    _exact_rational_evidence(state[2], f"localized fluid reservoir {index} thermal"),
                )
            )
        settlements.append(
            (
                lineage,
                layer,
                topology,
                ordinal,
                contact_evidence,
                carrier_evidence,
                (
                    reservoir_states[0],
                    reservoir_states[1],
                    _exact_rational_evidence(reservoir[2], "localized fluid gradient work"),
                ),
            )
        )
    return tuple(settlements)


def _localized_metabolic_strain_evidence(
    evaluated_lineages: object,
    value: object,
) -> tuple[tuple[str, ...], tuple[LocalizedMetabolicStrainEvidence, ...]]:
    if not isinstance(evaluated_lineages, list):
        raise RuntimeError(
            "resident organism localized metabolic-strain lineage evidence changed format"
        )
    evaluated = tuple(
        _canonical_lineage_hex(lineage, "localized metabolic-strain evaluated lineage")
        for lineage in evaluated_lineages
    )
    if evaluated != tuple(sorted(set(evaluated))):
        raise RuntimeError(
            "resident organism localized metabolic-strain evaluated lineages are not canonical"
        )
    if not isinstance(value, list) or len(value) > len(evaluated):
        raise RuntimeError(
            "resident organism localized metabolic-strain evidence changed format"
        )
    observations: list[LocalizedMetabolicStrainEvidence] = []
    for raw in value:
        if not isinstance(raw, tuple) or len(raw) != 7:
            raise RuntimeError(
                "resident organism localized metabolic-strain evidence changed format"
            )
        lineage = _canonical_lineage_hex(raw[0], "localized metabolic-strain lineage")
        layer = _nonnegative_integer(raw[1], "localized metabolic-strain layer")
        topology = _nonnegative_integer(raw[2], "localized metabolic-strain topology")
        ordinal = _positive_integer(raw[3], "localized metabolic-strain cognitive ordinal")
        if lineage not in evaluated or layer != 5:
            raise RuntimeError(
                "resident organism localized metabolic-strain source identity changed"
            )
        if not isinstance(raw[4], list):
            raise RuntimeError(
                "resident organism localized metabolic-strain Psi lanes changed format"
            )
        psi = tuple(
            _nonnegative_decimal_integer(
                quanta, "localized metabolic-strain Psi dissipation"
            )
            for quanta in raw[4]
        )
        gate = _nonnegative_decimal_integer(
            raw[5], "localized metabolic-strain gate dissipation"
        )
        plastic = _nonnegative_decimal_integer(
            raw[6], "localized metabolic-strain plastic dissipation"
        )
        if not any(psi) and gate == 0 and plastic == 0:
            raise RuntimeError(
                "resident organism localized metabolic-strain sparse evidence retained zero"
            )
        observations.append((lineage, layer, topology, ordinal, psi, gate, plastic))
    if tuple(item[0] for item in observations) != tuple(
        sorted({item[0] for item in observations})
    ):
        raise RuntimeError(
            "resident organism localized metabolic-strain observations are not canonical"
        )
    return evaluated, tuple(observations)


def _validated_causal_intervals(
    maximum_causal_intervals: object,
) -> list[tuple[int, int]]:
    """Validate caller-authored maximum causal intervals.

    One exact positive rational ``(numerator, denominator)`` per source
    occurrence, in exact occurrence order.  Every value is authored by the
    caller as independent environment/anatomy authority; nothing is defaulted
    or derived here.
    """

    if not isinstance(maximum_causal_intervals, (tuple, list)) or not (
        maximum_causal_intervals
    ):
        raise ValueError(
            "resident organism admission requires one authored maximum causal "
            "interval per source occurrence"
        )
    validated: list[tuple[int, int]] = []
    for index, interval in enumerate(maximum_causal_intervals):
        if not isinstance(interval, (tuple, list)) or len(interval) != 2:
            raise TypeError(
                f"authored admission {index} must be (numerator, denominator)"
            )
        numerator, denominator = interval
        if (
            isinstance(numerator, bool)
            or isinstance(denominator, bool)
            or not isinstance(numerator, int)
            or not isinstance(denominator, int)
        ):
            raise TypeError(
                f"authored admission {index} must carry exact integers"
            )
        if denominator == 0:
            raise ValueError(f"authored admission {index} has a zero denominator")
        if numerator * denominator <= 0:
            raise ValueError(
                f"authored admission {index} is not a positive causal interval"
            )
        validated.append((numerator, denominator))
    return validated


def _exact_token(value: object) -> bytes:
    if not isinstance(value, bytes) or len(value) != 32:
        raise ValueError("resident organism token must be exactly 32 immutable bytes")
    return value


def _concrete_class(core: object, name: str) -> type:
    candidate = getattr(core, name, None)
    if not isinstance(candidate, type):
        raise RuntimeError(f"guala_core does not expose concrete {name}")
    return candidate


def _validate_budget(
    max_envelope_bytes: object,
    max_fabric_bytes: object,
    max_logical_peak_bytes: object,
) -> tuple[int, int, int]:
    envelope = _positive_integer(max_envelope_bytes, "envelope budget")
    fabric = _positive_integer(max_fabric_bytes, "fabric budget")
    logical = _positive_integer(max_logical_peak_bytes, "logical peak budget")
    if fabric >= envelope:
        raise ValueError(
            "resident organism fabric budget must fit inside its envelope budget"
        )
    if logical <= 2 * envelope:
        raise ValueError(
            "resident organism logical peak budget must retain two envelopes and workspace"
        )
    return envelope, fabric, logical


def _observation_signature(
    observation: NativeResidentObservationView,
) -> tuple[object, ...]:
    return (
        observation.identity,
        observation.organism_tick,
        observation.fabric_generation,
        observation.mounted_generation,
        observation.state_bytes,
        observation.state_sha256,
        observation.fabric_bytes,
        observation.fabric_sha256,
        observation.joint_field_count,
        observation.joint_neuron_count,
        observation.complete_neuron_count,
        observation.developmental_resting_neuron_count,
        observation.cognitive_ordinal,
        observation.cognitive_trace_count,
        observation.cognitive_mosaic_count,
        tuple(observation.physical_frontier_routes),
        tuple(observation.preceding_distinct_physical_frontier_routes),
        tuple(observation.reached_and_foregone_physical_frontier_routes),
        tuple(observation.working_causal_continuations),
        tuple(observation.settled_working_frontier),
        tuple(observation.physical_prediction_alternatives),
        tuple(observation.body_consequence_transfers),
        tuple(observation.affective_balance_trajectories),
        tuple(observation.localized_fluid_chemistry),
        tuple(
            observation.localized_metabolic_strain_evaluated_body_receptor_lineages
        ),
        tuple(observation.localized_metabolic_strain),
        tuple(
            (
                tuple(receipts),
                tuple(lineages),
                tuple(bonds),
                structure_receipt,
                tuple(ordered_paths),
                tuple(ordered_path_relations),
            )
            for (
                receipts,
                lineages,
                bonds,
                structure_receipt,
                ordered_paths,
                ordered_path_relations,
            ) in observation.organic_mosaic_relations
        ),
        observation.partial_cue_reassembly_count,
        observation.endogenous_partial_cue_reassembly_count,
    )


class NativeResidentOrganism:
    """Factory-only handle retaining exactly one concrete native runtime."""

    __slots__ = (
        "__runtime",
        "__runtime_type",
        "__observation_type",
        "__prepare_type",
        "__unsealed_validation",
        "__unacknowledged_direct_token",
    )

    def __new__(cls, authority: object = None, *args: object, **kwargs: object):
        del args, kwargs
        if authority is not _FACTORY_AUTHORITY:
            raise TypeError(
                "native resident organism must be created by cold restore"
            )
        return super().__new__(cls)

    def __init__(
        self,
        authority: object,
        runtime: object,
        runtime_type: type,
        observation_type: type,
        prepare_type: type,
    ) -> None:
        if authority is not _FACTORY_AUTHORITY or not isinstance(
            runtime, runtime_type
        ):
            raise TypeError("native resident organism runtime is not concrete")
        self.__runtime = runtime
        self.__runtime_type = runtime_type
        self.__observation_type = observation_type
        self.__prepare_type = prepare_type
        self.__unsealed_validation: tuple[
            bytes, NativeResidentObservationView, int, int
        ] | None = None
        self.__unacknowledged_direct_token: bytes | None = None

    def _require_observation(
        self, candidate: object
    ) -> NativeResidentObservationView:
        if not isinstance(candidate, self.__observation_type):
            raise TypeError(
                "resident organism operation returned a structural impostor"
            )
        if candidate.schema != OBSERVATION_SCHEMA:
            raise RuntimeError("resident organism observation schema changed")
        if not isinstance(candidate.identity, str) or not candidate.identity:
            raise RuntimeError("resident organism identity is absent")
        organism_tick = _nonnegative_integer(
            candidate.organism_tick, "organism tick"
        )
        fabric_generation = _nonnegative_integer(
            candidate.fabric_generation, "fabric generation"
        )
        mounted_generation = _nonnegative_integer(
            candidate.mounted_generation, "mounted generation"
        )
        del organism_tick, fabric_generation, mounted_generation
        state_bytes = _positive_integer(candidate.state_bytes, "state bytes")
        fabric_bytes = _positive_integer(candidate.fabric_bytes, "fabric bytes")
        if fabric_bytes >= state_bytes:
            raise RuntimeError("resident organism fabric does not fit its envelope")
        _canonical_sha256(candidate.state_sha256, "state receipt")
        _canonical_sha256(candidate.fabric_sha256, "fabric receipt")
        body_axes = candidate.articulated_body_axes
        if not isinstance(body_axes, list) or len(body_axes) != 37:
            raise RuntimeError("resident articulated body axis count changed")
        seen_body_axes: set[int] = set()
        for raw_axis in body_axes:
            if not isinstance(raw_axis, tuple) or len(raw_axis) != 7:
                raise RuntimeError("resident articulated body axis changed format")
            ordinal, name, unit, position, minimum, neutral, maximum = raw_axis
            ordinal = _nonnegative_integer(ordinal, "body axis ordinal")
            if (
                ordinal in seen_body_axes
                or ordinal != len(seen_body_axes)
                or not isinstance(name, str)
                or not name
                or unit not in {"millidegree", "micrometre", "square_millimetre"}
            ):
                raise RuntimeError("resident articulated body anatomy is not canonical")
            position = _signed_integer(position, "body axis position")
            minimum = _signed_integer(minimum, "body axis minimum")
            neutral = _signed_integer(neutral, "body axis neutral")
            maximum = _signed_integer(maximum, "body axis maximum")
            if not minimum <= position <= maximum or not minimum <= neutral <= maximum:
                raise RuntimeError("resident articulated body axis left its anatomy")
            seen_body_axes.add(ordinal)
        _nonnegative_integer(
            candidate.articulated_body_lung_air_microlitres,
            "body lung air",
        )
        tract_areas = candidate.articulated_body_vocal_tract_areas_square_millimetres
        if (
            not isinstance(tract_areas, list)
            or len(tract_areas) != 8
            or any(_positive_integer(area, "vocal tract area") <= 0 for area in tract_areas)
        ):
            raise RuntimeError("resident vocal tract state changed format")
        if _positive_integer(
            candidate.articulated_body_state_bytes,
            "articulated body state bytes",
        ) != 195:
            raise RuntimeError("resident articulated body state width changed")
        if not isinstance(
            candidate.articulated_body_proprioception_initialized, bool
        ):
            raise RuntimeError(
                "resident articulated body proprioception flag changed format"
            )
        _canonical_sha256(
            candidate.articulated_body_state_sha256,
            "articulated body state receipt",
        )
        _nonnegative_integer(
            candidate.joint_field_count, "joint field count"
        )
        _nonnegative_integer(
            candidate.joint_neuron_count, "joint neuron count"
        )
        if (
            _nonnegative_integer(
                candidate.cold_restore_authentication_count,
                "cold authentication count",
            )
            != 1
            or _nonnegative_integer(
                candidate.cold_restore_decode_count, "cold decode count"
            )
            != 1
        ):
            raise RuntimeError("resident organism did not cold restore exactly once")
        _nonnegative_integer(
            candidate.cold_restore_rebuilt_field_count,
            "cold rebuilt field count",
        )
        cognitive_ordinal = _nonnegative_integer(
            candidate.cognitive_ordinal, "cognitive ordinal"
        )
        cognitive_trace_count = _nonnegative_integer(
            candidate.cognitive_trace_count, "cognitive trace count"
        )
        cognitive_mosaic_count = _nonnegative_integer(
            candidate.cognitive_mosaic_count, "cognitive mosaic count"
        )
        mosaic_of_mosaics_count = _nonnegative_integer(
            candidate.mosaic_of_mosaics_count, "mosaic of mosaics count"
        )
        del mosaic_of_mosaics_count
        activation_count = _nonnegative_integer(
            candidate.formation_activation_count,
            "formation activation count",
        )
        partial_count = _nonnegative_integer(
            candidate.partial_cue_reassembly_count,
            "partial cue reassembly count",
        )
        endogenous_partial_count = _nonnegative_integer(
            candidate.endogenous_partial_cue_reassembly_count,
            "endogenous partial cue reassembly count",
        )
        complete_count = _nonnegative_integer(
            candidate.complete_neuron_count, "complete neuron count"
        )
        resting_count = _nonnegative_integer(
            candidate.developmental_resting_neuron_count,
            "developmental resting neuron count",
        )
        transitioned_count = _nonnegative_integer(
            candidate.physically_transitioned_neuron_count,
            "physically transitioned neuron count",
        )
        metabolic_body_count = _nonnegative_integer(
            candidate.metabolically_perturbed_body_receptor_count,
            "metabolically perturbed body receptor count",
        )
        del cognitive_ordinal, cognitive_trace_count, complete_count, resting_count
        if (
            not isinstance(candidate.mounted_step_completed, bool)
            or not isinstance(candidate.physical_transition_claimed, bool)
            or not isinstance(candidate.cognitive_formation_claimed, bool)
            or candidate.physical_transition_claimed
            != (transitioned_count > 0)
            or metabolic_body_count > transitioned_count
            or candidate.python_callback_count != 0
            or endogenous_partial_count > partial_count
        ):
            raise RuntimeError("resident organism observation made a false claim")
        if not candidate.mounted_step_completed and (
            candidate.physical_transition_claimed
            or candidate.cognitive_formation_claimed
            or activation_count != 0
            or partial_count != 0
            or transitioned_count != 0
        ):
            raise RuntimeError(
                "resident organism cold observation claimed step effects"
            )
        del cognitive_mosaic_count
        return candidate

    def readiness(self) -> NativeResidentObservationView:
        """Observe only the active native state."""

        if not isinstance(self.__runtime, self.__runtime_type):
            raise RuntimeError("resident organism runtime identity changed")
        return self._require_observation(self.__runtime.readiness())

    def save(self) -> bytes:
        """Seal only the active GLORUN envelope."""

        observation = self.readiness()
        state = self.__runtime.save()
        if (
            not isinstance(state, bytes)
            or not state.startswith(b"GLORUN01")
            or len(state) != observation.state_bytes
            or hashlib.sha256(state).hexdigest() != observation.state_sha256
        ):
            raise RuntimeError("resident organism save changed active custody")
        return state

    def observe_retained_formations(self) -> tuple[tuple[tuple[str, ...], int], ...]:
        """Read-only structure of the retained distributed formations.

        One entry per admitted mosaic as ``(member_lineage_hexes,
        recurrence_bond_count)``.  Structure only — no recognition, recall,
        meaning, or capital — and reading advances nothing (verified against
        the active state receipt).
        """

        before = self.readiness()
        formations = self.__runtime.observe_retained_formations()
        validated = []
        for members, bond_count in formations:
            lineages = tuple(str(lineage) for lineage in members)
            if len(lineages) < 3 or any(
                len(lineage) != 32 for lineage in lineages
            ):
                raise RuntimeError(
                    "retained formation observation is structurally invalid"
                )
            validated.append((lineages, _nonnegative_integer(
                bond_count, "recurrence bond count"
            )))
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("formation observation advanced the organism")
        return tuple(validated)

    def observe_reached_neuron_lineage_layers(
        self,
    ) -> tuple[tuple[str, int, bool], ...]:
        """Read reached lineage, developmental layer, and receptor anatomy."""

        before = self.readiness()
        observed = self.__runtime.observe_reached_neuron_lineage_layers()
        validated = []
        seen_lineages: set[str] = set()
        for lineage, layer, receptor in observed:
            lineage = str(lineage)
            layer = _nonnegative_integer(layer, "reached developmental layer")
            if (
                len(lineage) != 32
                or lineage in seen_lineages
                or not isinstance(receptor, bool)
            ):
                raise RuntimeError("reached lineage-layer observation is invalid")
            validated.append((lineage, layer, receptor))
            seen_lineages.add(lineage)
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("lineage-layer observation advanced the organism")
        return tuple(validated)

    def observe_active_electrical_frontier_advances_from(
        self, lineages: tuple[str, ...]
    ) -> tuple[tuple[str, str, int, int, str], ...]:
        """Read exact transfers advancing from supplied causal lineages."""

        canonical = tuple(
            _canonical_lineage_hex(lineage, "active frontier filter lineage")
            for lineage in lineages
        )
        if not canonical or len(set(canonical)) != len(canonical):
            raise ValueError("active frontier filter lineages must be nonempty and unique")
        before = self.readiness()
        observed = self.__runtime.observe_active_electrical_frontier_advances_from(
            list(canonical)
        )
        validated = []
        for raw in observed:
            if not isinstance(raw, tuple) or len(raw) != 5:
                raise RuntimeError("causal frontier advance changed format")
            transfer = _directed_physical_transfer_evidence(
                raw[:4], "causal frontier advance"
            )
            frontier = _canonical_lineage_hex(raw[4], "causal frontier lineage")
            if frontier not in transfer[:2]:
                raise RuntimeError("causal frontier is not a transfer endpoint")
            predecessor = transfer[1] if frontier == transfer[0] else transfer[0]
            if predecessor not in canonical:
                raise RuntimeError("causal frontier did not advance from supplied lineage")
            validated.append((*transfer, frontier))
        result = tuple(validated)
        if len(set(result)) != len(result):
            raise RuntimeError("filtered active electrical frontier is not canonical")
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("filtered active electrical frontier observation advanced the organism")
        return result

    def observe_retained_formation_structures(
        self,
    ) -> tuple[
        tuple[
            str,
            tuple[str, ...],
            tuple[tuple[str, str, int], ...],
            tuple[tuple[str, str, int], ...],
            int,
        ],
        ...,
    ]:
        """Read exact retained structure without assigning meaning."""

        before = self.readiness()
        observed = self.__runtime.observe_retained_formation_structures()
        validated = []
        for receipt, members, original_bonds, recurrence_bonds, reinforcements in observed:
            receipt = str(receipt)
            member_lineages = tuple(str(lineage) for lineage in members)
            if len(receipt) != 64 or len(member_lineages) < 3 or any(
                len(lineage) != 32 for lineage in member_lineages
            ):
                raise RuntimeError("retained formation structure is invalid")

            def bonds(values: object) -> tuple[tuple[str, str, int], ...]:
                canonical = []
                for left, right, ordinal in values:
                    left = str(left)
                    right = str(right)
                    ordinal = _nonnegative_integer(ordinal, "parallel bond ordinal")
                    if len(left) != 32 or len(right) != 32 or left >= right:
                        raise RuntimeError("retained formation bond is invalid")
                    canonical.append((left, right, ordinal))
                return tuple(canonical)

            validated.append(
                (
                    receipt,
                    member_lineages,
                    bonds(original_bonds),
                    bonds(recurrence_bonds),
                    _nonnegative_integer(reinforcements, "reinforcement count"),
                )
            )
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("formation structure observation advanced the organism")
        return tuple(validated)

    def observe_retained_formation_recurrence_cues(
        self,
    ) -> tuple[tuple[str, tuple[str, ...]], ...]:
        """Read the latest proper physical cue for each retained formation."""

        before = self.readiness()
        observed = self.__runtime.observe_retained_formation_recurrence_cues()
        validated = []
        for receipt, cue in observed:
            receipt = str(receipt)
            cue_lineages = tuple(str(lineage) for lineage in cue)
            if (
                len(receipt) != 64
                or not cue_lineages
                or any(len(lineage) != 32 for lineage in cue_lineages)
            ):
                raise RuntimeError("retained formation recurrence cue is invalid")
            validated.append((receipt, cue_lineages))
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("formation cue observation advanced the organism")
        return tuple(validated)

    def observe_retained_formation_recurrence_evidence(
        self,
    ) -> tuple[tuple[str, tuple[str, ...], str], ...]:
        """Read the latest physical recurrence cue and retained origin."""

        before = self.readiness()
        observed = self.__runtime.observe_retained_formation_recurrence_evidence()
        validated = []
        for receipt, cue, origin in observed:
            receipt = str(receipt)
            cue_lineages = tuple(str(lineage) for lineage in cue)
            origin = str(origin)
            if (
                len(receipt) != 64
                or not cue_lineages
                or any(len(lineage) != 32 for lineage in cue_lineages)
                or origin not in {"externally_observed", "internally_simulated"}
            ):
                raise RuntimeError("retained formation recurrence evidence is invalid")
            validated.append((receipt, cue_lineages, origin))
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("formation recurrence evidence advanced the organism")
        return tuple(validated)

    def navigate_hippocampal(self, lineage_hex: str) -> None:
        """Refused: the hippocampal episode archive is retired.

        This walked an archived posting chain and returned episode addresses.
        The archive is no longer written or read: it never carried
        recognition, recall or meaning, and it grew by roughly 893 files per
        recognition.  Her memories are the retained formations in her body —
        read those with :meth:`observe_retained_formations`.
        """

        return self.__runtime.navigate_hippocampal(lineage_hex)

    def prepare(self, source: NativeJointSourceView) -> ResidentPrepareEvidence:
        """Prepare one native candidate and return receipts, never state bytes.

        The bare source path remains severed by the mandatory-admission law:
        the native runtime refuses it because no occurrence admission is
        supplied.  Use :meth:`begin_unsealed_intake_direct`.
        """

        source_port_count = _nonnegative_integer(
            getattr(source, "port_count", None), "source port count"
        )
        active_before = self.readiness()
        candidate = self.__runtime.prepare(source)
        return self._validated_prepare_evidence(
            candidate, source_port_count, active_before
        )

    def prepare_articulated_body_observation(self) -> ResidentPrepareEvidence:
        """Prepare one full fixed-capacity observation of the current body."""

        active_before = self.readiness()
        candidate = self.__runtime.prepare_articulated_body_observation()
        return self._validated_prepare_evidence(candidate, 74, active_before)

    def _validated_unsealed_phase(
        self,
        candidate: object,
        active_before: NativeResidentObservationView,
    ) -> ResidentUnsealedIntakeEvidence:
        token = getattr(candidate, "token", None)
        if not isinstance(token, bytes) or len(token) != 32:
            raise RuntimeError("unsealed intake token changed format")
        provisional_tick = _positive_integer(
            getattr(candidate, "provisional_organism_tick", None),
            "unsealed provisional organism tick",
        )
        if provisional_tick <= active_before.organism_tick:
            raise RuntimeError("unsealed intake did not advance one causal interval")
        motor_recruitments = _motor_unit_recruitment_evidence(
            getattr(candidate, "motor_unit_recruitments", None)
        )
        raw_pause = getattr(candidate, "pause_interval_ordinal", None)
        pause_interval_ordinal = (
            None
            if raw_pause is None
            else _positive_integer(raw_pause, "unsealed pause interval ordinal")
        )
        raw_bindings = getattr(candidate, "body_effector_bindings", None)
        if not isinstance(raw_bindings, list):
            raise RuntimeError("unsealed body effector bindings changed format")
        bindings: list[tuple[str, str, str, int]] = []
        for raw in raw_bindings:
            if not isinstance(raw, tuple) or len(raw) != 4:
                raise RuntimeError("unsealed body effector binding changed format")
            lineage = _canonical_lineage_hex(raw[0], "unsealed motor lineage")
            axis, direction = raw[1], raw[2]
            carriers = _positive_integer(raw[3], "unsealed motor carriers")
            if (
                not isinstance(axis, str)
                or not axis
                or direction not in {"toward_minimum", "toward_maximum"}
            ):
                raise RuntimeError("unsealed body effector binding lost anatomy")
            bindings.append((lineage, axis, direction, carriers))
        body_axes = _articulated_body_axis_evidence(
            getattr(candidate, "articulated_body_axes", None)
        )
        body_consequences = _articulated_body_consequence_evidence(
            getattr(candidate, "articulated_body_consequences", None),
            predecessor_organism_tick=active_before.organism_tick,
            organism_tick=provisional_tick,
        )
        axes_by_name = {axis[1]: axis for axis in body_axes}
        if len(axes_by_name) != len(body_axes):
            raise RuntimeError("resident articulated body axis names are not unique")
        if any(binding[1] not in axes_by_name for binding in bindings):
            raise RuntimeError("unsealed motor binding named no resident body axis")
        consequence_axes: set[str] = set()
        for consequence in body_consequences:
            axis = axes_by_name.get(consequence[1])
            if (
                axis is None
                or consequence[1] in consequence_axes
                or consequence[2] != axis[2]
                or consequence[4] != axis[3]
                or not axis[4] <= consequence[3] <= axis[6]
            ):
                raise RuntimeError(
                    "unsealed body consequence disagrees with resident anatomy"
                )
            consequence_axes.add(consequence[1])
        if motor_recruitments:
            if (
                pause_interval_ordinal
                != provisional_tick - active_before.organism_tick
                or {entry[0] for entry in bindings}
                != {entry[0] for entry in motor_recruitments}
            ):
                raise RuntimeError("unsealed motor pause lost its exact cause")
        elif pause_interval_ordinal is not None or bindings or body_consequences:
            raise RuntimeError("unsealed quiescent phase fabricated an action pause")
        if _observation_signature(self.readiness()) != _observation_signature(
            active_before
        ):
            raise RuntimeError("unsealed intake published before its final seal")
        return ResidentUnsealedIntakeEvidence(
            token=token,
            provisional_organism_tick=provisional_tick,
            pause_interval_ordinal=pause_interval_ordinal,
            motor_unit_recruitments=motor_recruitments,
            body_effector_bindings=tuple(bindings),
            articulated_body_axes=body_axes,
            articulated_body_consequences=body_consequences,
            articulatory_unit_recruitments=_articulatory_unit_recruitments(
                getattr(candidate, "articulatory_unit_recruitments", None)
            ),
        )

    def begin_unsealed_intake_direct(
        self,
        sources: object,
        maximum_causal_intervals: object,
        *,
        vestibular_yaw: tuple[int, tuple[int, ...]] | None = None,
    ) -> ResidentUnsealedIntakeEvidence:
        """Advance one intake in native memory without encoding its successor."""

        if self.__unsealed_validation is not None:
            raise RuntimeError("resident organism already has an unsealed intake")
        if self.__unacknowledged_direct_token is not None:
            raise RuntimeError("resident organism has an unpublished direct successor")
        if not isinstance(sources, tuple):
            raise TypeError("unsealed intake sources must be a tuple")
        if (
            not isinstance(maximum_causal_intervals, tuple)
            or len(maximum_causal_intervals) != len(sources)
        ):
            raise TypeError("unsealed intake intervals must match the source tuple")
        intervals = tuple(
            _validated_causal_intervals(value)
            for value in maximum_causal_intervals
        )
        predecessor_heading: int | None = None
        signed_steps: tuple[int, ...] = ()
        if vestibular_yaw is not None:
            if not isinstance(vestibular_yaw, tuple) or len(vestibular_yaw) != 2:
                raise TypeError("unsealed vestibular trajectory changed format")
            predecessor_heading = _nonnegative_integer(
                vestibular_yaw[0], "vestibular predecessor heading"
            )
            if predecessor_heading >= 360_000:
                raise ValueError(
                    "vestibular predecessor heading must be below 360000"
                )
            signed_steps = vestibular_yaw[1]
            if not isinstance(signed_steps, tuple) or not signed_steps:
                raise TypeError("vestibular trajectory must be a nonempty tuple")
            if any(
                not isinstance(step, int)
                or isinstance(step, bool)
                or not -(1 << 31) <= step < (1 << 31)
                for step in signed_steps
            ):
                raise TypeError(
                    "vestibular trajectory steps must be signed 32-bit integers"
                )
        if not sources and not signed_steps:
            raise ValueError("unsealed intake must contain a physical source")
        active_before = self.readiness()
        requested_source_port_count = len(signed_steps) + sum(
            _nonnegative_integer(
                getattr(source, "port_count", None),
                "unsealed trajectory source port count",
            )
            for source in sources
        )
        requested_interval_count = len(signed_steps) + len(sources)
        if sources:
            requested_source_port_count += 74
            requested_interval_count += 1
        candidate = self.__runtime.begin_unsealed_intake_direct(
            predecessor_heading,
            list(signed_steps),
            list(sources),
            [list(value) for value in intervals],
        )
        try:
            evidence = self._validated_unsealed_phase(candidate, active_before)
        except BaseException:
            token = getattr(candidate, "token", None)
            if isinstance(token, bytes) and len(token) == 32:
                self.__runtime.abort_unsealed_intake(token)
            raise
        self.__unsealed_validation = (
            evidence.token,
            active_before,
            requested_source_port_count,
            requested_interval_count,
        )
        return evidence

    def resume_unsealed_action_direct(
        self,
        token: bytes,
        sources: object,
        maximum_causal_intervals: object,
        *,
        vestibular_yaw: tuple[int, tuple[int, ...]] | None = None,
    ) -> ResidentUnsealedIntakeEvidence:
        """Resume one exact motor pause, stopping at any later discharge."""

        validation = self.__unsealed_validation
        if validation is None:
            raise RuntimeError("resident organism has no unsealed intake")
        expected_token, active_before, source_port_count, interval_count = validation
        if token != expected_token:
            raise ValueError("unsealed intake token mismatch")
        if not isinstance(sources, tuple) or not sources:
            raise TypeError("unsealed action consequence must be a nonempty tuple")
        if (
            not isinstance(maximum_causal_intervals, tuple)
            or len(maximum_causal_intervals) != len(sources)
        ):
            raise TypeError("unsealed action consequence intervals changed cardinality")
        intervals = tuple(
            _validated_causal_intervals(value)
            for value in maximum_causal_intervals
        )
        predecessor_heading: int | None = None
        signed_steps: tuple[int, ...] = ()
        if vestibular_yaw is not None:
            if not isinstance(vestibular_yaw, tuple) or len(vestibular_yaw) != 2:
                raise TypeError("unsealed action vestibular trajectory changed format")
            predecessor_heading = _nonnegative_integer(
                vestibular_yaw[0], "action vestibular predecessor heading"
            )
            if predecessor_heading >= 360_000:
                raise ValueError("action vestibular predecessor heading is not canonical")
            signed_steps = vestibular_yaw[1]
            if (
                not isinstance(signed_steps, tuple)
                or not signed_steps
                or any(
                    not isinstance(step, int)
                    or isinstance(step, bool)
                    or not -(1 << 31) <= step < (1 << 31)
                    for step in signed_steps
                )
            ):
                raise TypeError("action vestibular steps changed format")
        source_port_count += sum(
            _nonnegative_integer(
                getattr(source, "port_count", None),
                "unsealed consequence source port count",
            )
            for source in sources
        ) + len(signed_steps)
        interval_count += len(sources) + len(signed_steps)
        candidate = None
        try:
            candidate = self.__runtime.resume_unsealed_action_direct(
                token,
                predecessor_heading,
                list(signed_steps),
                list(sources),
                [list(value) for value in intervals],
            )
            evidence = self._validated_unsealed_phase(
                candidate, active_before
            )
        except BaseException:
            candidate_token = getattr(candidate, "token", None)
            if isinstance(candidate_token, bytes) and len(candidate_token) == 32:
                try:
                    self.__runtime.abort_unsealed_intake(candidate_token)
                except (RuntimeError, ValueError) as abort_error:
                    raise RuntimeError(
                        "unsealed action phase validation and abort both failed"
                    ) from abort_error
            self.__unsealed_validation = None
            raise
        self.__unsealed_validation = (
            evidence.token,
            active_before,
            source_port_count,
            interval_count,
        )
        return evidence

    def append_unsealed_intake_direct(
        self,
        token: bytes,
        sources: object,
        maximum_causal_intervals: object,
    ) -> ResidentUnsealedIntakeEvidence:
        """Append exact self-hearing without sealing the open successor."""

        validation = self.__unsealed_validation
        if validation is None:
            raise RuntimeError("resident organism has no unsealed intake")
        expected_token, active_before, source_port_count, interval_count = validation
        if token != expected_token:
            raise ValueError("unsealed intake token mismatch")
        if not isinstance(sources, tuple) or not sources:
            raise TypeError("unsealed appended sources must be a nonempty tuple")
        if (
            not isinstance(maximum_causal_intervals, tuple)
            or len(maximum_causal_intervals) != len(sources)
        ):
            raise TypeError("unsealed appended intervals changed cardinality")
        intervals = tuple(
            _validated_causal_intervals(value)
            for value in maximum_causal_intervals
        )
        source_port_count += sum(
            _nonnegative_integer(
                getattr(source, "port_count", None),
                "unsealed appended source port count",
            )
            for source in sources
        )
        interval_count += len(sources)
        candidate = None
        try:
            candidate = self.__runtime.append_unsealed_intake_direct(
                token,
                list(sources),
                [list(value) for value in intervals],
            )
            evidence = self._validated_unsealed_phase(candidate, active_before)
        except BaseException:
            candidate_token = getattr(candidate, "token", None)
            if isinstance(candidate_token, bytes) and len(candidate_token) == 32:
                try:
                    self.__runtime.abort_unsealed_intake(candidate_token)
                except (RuntimeError, ValueError) as abort_error:
                    raise RuntimeError(
                        "unsealed appended phase validation and abort both failed"
                    ) from abort_error
            self.__unsealed_validation = None
            raise
        self.__unsealed_validation = (
            evidence.token,
            active_before,
            source_port_count,
            interval_count,
        )
        return evidence

    def finalize_unsealed_intake_direct(
        self,
        token: bytes,
    ) -> ResidentPrepareEvidence:
        """Seal once after the causal queue and every action pause drain."""

        validation = self.__unsealed_validation
        if validation is None:
            raise RuntimeError("resident organism has no unsealed intake")
        expected_token, active_before, source_port_count, interval_count = validation
        if token != expected_token:
            raise ValueError("unsealed intake token mismatch")
        final_token = None
        try:
            candidate = self.__runtime.finalize_unsealed_intake_direct(token)
            final_token = getattr(candidate, "token", None)
            evidence = self._validated_prepare_evidence_body(
                candidate,
                source_port_count,
                active_before,
                causal_interval_count=interval_count,
                body_feedback_reentered=True,
                candidate_committed=True,
            )
            self.__unacknowledged_direct_token = final_token
            return evidence
        except BaseException:
            if isinstance(final_token, bytes) and len(final_token) == 32:
                try:
                    self.__runtime.rollback_direct_commit(final_token)
                except (RuntimeError, ValueError) as rollback_error:
                    if "has no pending candidate" not in str(rollback_error):
                        raise RuntimeError(
                            "unsealed intake validation and rollback both failed"
                        ) from rollback_error
            raise
        finally:
            self.__unsealed_validation = None

    def acknowledge_direct_commit(self, token: bytes) -> None:
        """Release rollback custody only after durable CURRENT publication."""

        if token != self.__unacknowledged_direct_token:
            raise ValueError("unacknowledged direct token mismatch")
        self.__runtime.acknowledge_direct_commit(token)
        self.__unacknowledged_direct_token = None

    def rollback_direct_commit(self, token: bytes) -> None:
        """Restore the authenticated predecessor before CURRENT publication."""

        if token != self.__unacknowledged_direct_token:
            raise ValueError("unacknowledged direct token mismatch")
        try:
            self.__runtime.rollback_direct_commit(token)
        finally:
            self.__unacknowledged_direct_token = None

    def abort_unsealed_intake(self, token: bytes) -> None:
        """Drop the working successor and restore its authenticated predecessor."""

        validation = self.__unsealed_validation
        if validation is None:
            raise RuntimeError("resident organism has no unsealed intake")
        if token != validation[0]:
            raise ValueError("unsealed intake token mismatch")
        try:
            self.__runtime.abort_unsealed_intake(token)
        finally:
            self.__unsealed_validation = None

    def prepare_vestibular_tick(
        self,
        predecessor_heading_millidegrees: int,
        signed_body_motion_millidegrees: int,
    ) -> ResidentPrepareEvidence:
        """Prepare one native one-millisecond body-and-balance successor."""

        predecessor_heading = _nonnegative_integer(
            predecessor_heading_millidegrees,
            "vestibular predecessor heading",
        )
        if predecessor_heading >= 360_000:
            raise ValueError("vestibular predecessor heading must be below 360000")
        if (
            not isinstance(signed_body_motion_millidegrees, int)
            or isinstance(signed_body_motion_millidegrees, bool)
            or not -(1 << 31)
            <= signed_body_motion_millidegrees
            < (1 << 31)
        ):
            raise TypeError("vestibular signed yaw step must be a signed 32-bit integer")
        active_before = self.readiness()
        candidate = self.__runtime.prepare_vestibular_tick(
            predecessor_heading,
            signed_body_motion_millidegrees,
        )
        return self._validated_prepare_evidence(candidate, 1, active_before)

    def prepare_vestibular_trajectory(
        self,
        predecessor_heading_millidegrees: int,
        signed_body_motion_millidegrees: tuple[int, ...],
    ) -> ResidentPrepareEvidence:
        """Prepare ordered one-millisecond balance intervals and seal once."""

        predecessor_heading = _nonnegative_integer(
            predecessor_heading_millidegrees,
            "vestibular predecessor heading",
        )
        if predecessor_heading >= 360_000:
            raise ValueError("vestibular predecessor heading must be below 360000")
        if (
            not isinstance(signed_body_motion_millidegrees, tuple)
            or not signed_body_motion_millidegrees
        ):
            raise TypeError("vestibular trajectory must be a nonempty tuple")
        if any(
            not isinstance(step, int)
            or isinstance(step, bool)
            or not -(1 << 31) <= step < (1 << 31)
            for step in signed_body_motion_millidegrees
        ):
            raise TypeError(
                "vestibular trajectory steps must be signed 32-bit integers"
            )
        active_before = self.readiness()
        candidate = self.__runtime.prepare_vestibular_trajectory(
            predecessor_heading,
            list(signed_body_motion_millidegrees),
        )
        return self._validated_prepare_evidence(
            candidate,
            len(signed_body_motion_millidegrees),
            active_before,
            causal_interval_count=len(signed_body_motion_millidegrees),
        )

    def _validated_prepare_evidence(
        self,
        candidate: object,
        source_port_count: int,
        active_before: NativeResidentObservationView,
        *,
        causal_interval_count: int = 1,
        body_feedback_reentered: bool = False,
    ) -> ResidentPrepareEvidence:
        """Validate one native candidate or discard its uncommitted custody."""

        try:
            return self._validated_prepare_evidence_body(
                candidate,
                source_port_count,
                active_before,
                causal_interval_count=causal_interval_count,
                body_feedback_reentered=body_feedback_reentered,
            )
        except BaseException:
            if isinstance(candidate, self.__prepare_type):
                token = getattr(candidate, "token", None)
                if isinstance(token, bytes) and len(token) == 32:
                    try:
                        self.discard(token)
                    except (RuntimeError, ValueError) as discard_error:
                        if not any(
                            phrase in str(discard_error)
                            for phrase in (
                                "has no pending candidate",
                                "pending token mismatch",
                            )
                        ):
                            raise RuntimeError(
                                "resident organism candidate validation and "
                                "discard both failed"
                            ) from discard_error
            raise

    def _validated_prepare_evidence_body(
        self,
        candidate: object,
        source_port_count: int,
        active_before: NativeResidentObservationView,
        *,
        causal_interval_count: int = 1,
        body_feedback_reentered: bool = False,
        candidate_committed: bool = False,
    ) -> ResidentPrepareEvidence:
        if not isinstance(candidate, self.__prepare_type):
            raise TypeError("resident organism prepare returned a structural impostor")
        if candidate.schema != PREPARE_SCHEMA:
            raise RuntimeError("resident organism prepare schema changed")
        token = candidate.token
        if (
            not isinstance(token, bytes)
            or len(token) != 32
            or candidate.token_hex != token.hex()
        ):
            raise RuntimeError("resident organism prepare token changed format")
        predecessor_state_sha256 = _canonical_sha256(
            candidate.predecessor_state_sha256, "predecessor state receipt"
        )
        prepared_state_sha256 = _canonical_sha256(
            candidate.prepared_state_sha256, "prepared state receipt"
        )
        predecessor_organism_tick = _nonnegative_integer(
            candidate.predecessor_organism_tick, "predecessor organism tick"
        )
        organism_tick = _nonnegative_integer(
            candidate.organism_tick, "prepared organism tick"
        )
        requested_source_port_count = source_port_count
        requested_causal_interval_count = causal_interval_count
        source_port_count = _nonnegative_integer(
            candidate.reached_source_port_count,
            "reached source port count",
        )
        causal_interval_count = _positive_integer(
            candidate.causal_interval_count,
            "causal interval count",
        )
        if (
            source_port_count < requested_source_port_count
            or causal_interval_count < requested_causal_interval_count
        ):
            raise RuntimeError("native prepare omitted an admitted causal source")
        predecessor_fabric_generation = _nonnegative_integer(
            candidate.predecessor_fabric_generation,
            "predecessor fabric generation",
        )
        fabric_generation = _nonnegative_integer(
            candidate.fabric_generation, "prepared fabric generation"
        )
        predecessor_mounted_generation = _nonnegative_integer(
            candidate.predecessor_mounted_generation,
            "predecessor mounted generation",
        )
        mounted_generation = _nonnegative_integer(
            candidate.mounted_generation, "prepared mounted generation"
        )
        predecessor_authentication_count = _nonnegative_integer(
            candidate.predecessor_authentication_count,
            "prepare predecessor authentication count",
        )
        predecessor_decode_count = _nonnegative_integer(
            candidate.predecessor_decode_count,
            "prepare predecessor decode count",
        )
        predecessor_rebuilt_field_count = _nonnegative_integer(
            candidate.predecessor_rebuilt_field_count,
            "prepare predecessor rebuilt field count",
        )
        current_cohort_evaluation_count = _nonnegative_integer(
            candidate.current_cohort_evaluation_count,
            "current cohort evaluation count",
        )
        successor_seal_count = _nonnegative_integer(
            candidate.successor_seal_count, "successor seal count"
        )
        dsf_delivery_count = _nonnegative_integer(
            candidate.dsf_delivery_count,
            "DSF delivery count",
        )
        complete_neuron_fractal_count = _nonnegative_integer(
            candidate.complete_neuron_fractal_count,
            "complete-neuron fractal count",
        )
        raw_neuron_fractals = candidate.emitted_neuron_fractals
        if not isinstance(raw_neuron_fractals, list):
            raise RuntimeError("neuronal fractal evidence changed format")
        emitted_neuron_fractals: list[
            tuple[str, tuple[tuple[str, int, bool, int, int], ...]]
        ] = []
        emitted_lineages: set[str] = set()
        retained_coordinates = {
            "psi-winding",
            "gate-open-population",
            "plastic-rest-length",
            "dna-expressed-product",
            "receptor-quantum-residue",
        }
        for raw_fractal in raw_neuron_fractals:
            if not isinstance(raw_fractal, tuple) or len(raw_fractal) != 2:
                raise RuntimeError("neuronal fractal evidence changed format")
            lineage = _canonical_lineage_hex(raw_fractal[0], "fractal lineage")
            if lineage in emitted_lineages:
                raise RuntimeError("neuronal fractal lineage was emitted twice")
            emitted_lineages.add(lineage)
            raw_entries = raw_fractal[1]
            if not isinstance(raw_entries, list) or not raw_entries:
                raise RuntimeError("neuronal fractal has no sparse retained delta")
            entries: list[tuple[str, int, bool, int, int]] = []
            seen_coordinates: set[tuple[str, int]] = set()
            for raw_entry in raw_entries:
                if not isinstance(raw_entry, tuple) or len(raw_entry) != 5:
                    raise RuntimeError("neuronal fractal entry changed format")
                coordinate = raw_entry[0]
                if coordinate not in retained_coordinates:
                    raise RuntimeError("neuronal fractal carried a transient coordinate")
                index = _nonnegative_integer(raw_entry[1], "fractal coordinate index")
                if coordinate != "psi-winding" and index != 0:
                    raise RuntimeError("scalar fractal coordinate carried an index")
                key = (coordinate, index)
                if key in seen_coordinates:
                    raise RuntimeError("neuronal fractal repeated a coordinate")
                seen_coordinates.add(key)
                negative = raw_entry[2]
                if not isinstance(negative, bool):
                    raise RuntimeError("neuronal fractal sign changed format")
                magnitude = _positive_decimal_integer(
                    raw_entry[3], "fractal delta magnitude"
                )
                denominator = _positive_decimal_integer(
                    raw_entry[4], "fractal delta denominator"
                )
                entries.append(
                    (coordinate, index, negative, magnitude, denominator)
                )
            emitted_neuron_fractals.append((lineage, tuple(entries)))
        if len(emitted_neuron_fractals) != complete_neuron_fractal_count:
            raise RuntimeError("neuronal fractal count lost its exact evidence")
        raw_active_physical_bonds = candidate.active_physical_bonds
        if not isinstance(raw_active_physical_bonds, list):
            raise RuntimeError("active physical-bond evidence changed format")
        active_physical_bonds: list[tuple[str, str, int]] = []
        for raw_bond in raw_active_physical_bonds:
            if not isinstance(raw_bond, tuple) or len(raw_bond) != 3:
                raise RuntimeError("active physical-bond evidence changed format")
            active_physical_bonds.append(
                (
                    _canonical_lineage_hex(raw_bond[0], "active bond left lineage"),
                    _canonical_lineage_hex(raw_bond[1], "active bond right lineage"),
                    _nonnegative_integer(raw_bond[2], "active bond parallel ordinal"),
                )
            )
        changed_contact_channel_states = _changed_contact_channel_state_evidence(
            candidate.changed_contact_channel_states
        )
        physical_frontier_routes = _physical_frontier_route_evidence(
            candidate.physical_frontier_routes,
            "physical frontier route evidence",
        )
        preceding_distinct_physical_frontier_routes = (
            _physical_frontier_route_evidence(
                candidate.preceding_distinct_physical_frontier_routes,
                "preceding distinct physical frontier route evidence",
            )
        )
        reached_and_foregone_physical_frontier_routes = (
            _physical_frontier_route_evidence(
                candidate.reached_and_foregone_physical_frontier_routes,
                "reached and foregone physical frontier route evidence",
            )
        )
        if reached_and_foregone_physical_frontier_routes and not (
            len(reached_and_foregone_physical_frontier_routes) > 1
            and any(
                route[7] == 0
                for route in reached_and_foregone_physical_frontier_routes
            )
            and any(
                route[7] != 0
                for route in reached_and_foregone_physical_frontier_routes
            )
        ):
            raise RuntimeError(
                "reached and foregone frontier evidence lost its exact distinction"
            )
        working_causal_continuations = _working_causal_continuation_evidence(
            candidate.working_causal_continuations
        )
        settled_working_frontier = _settled_working_frontier_evidence(
            candidate.settled_working_frontier
        )
        physical_prediction_alternatives = (
            _physical_prediction_alternative_evidence(
                candidate.physical_prediction_alternatives
            )
        )
        body_consequence_transfers = _body_consequence_transfer_evidence(
            candidate.body_consequence_transfers
        )
        affective_balance_trajectories = _affective_balance_trajectory_evidence(
            candidate.affective_balance_trajectories
        )
        localized_fluid_chemistry = _localized_fluid_chemistry_evidence(
            candidate.localized_fluid_chemistry
        )
        (
            localized_metabolic_strain_evaluated_body_receptor_lineages,
            localized_metabolic_strain,
        ) = _localized_metabolic_strain_evidence(
            candidate.localized_metabolic_strain_evaluated_body_receptor_lineages,
            candidate.localized_metabolic_strain,
        )
        raw_organic_mosaic_relations = candidate.organic_mosaic_relations
        if not isinstance(raw_organic_mosaic_relations, list):
            raise RuntimeError("organic mosaic-relation evidence changed format")
        organic_mosaic_relations: list[
            tuple[
                tuple[str, ...],
                tuple[str, ...],
                tuple[tuple[str, str, int], ...],
                str,
                tuple[
                    tuple[
                        tuple[str, str, int, int],
                        tuple[str, str, int, int],
                    ],
                    ...,
                ],
                tuple[
                    tuple[
                        tuple[str, str, int, int],
                        tuple[str, str, int, int],
                        tuple[str, str, int, int],
                        tuple[str, str, int, int],
                    ],
                    ...,
                ],
            ]
        ] = []
        for raw_relation in raw_organic_mosaic_relations:
            if not isinstance(raw_relation, tuple) or len(raw_relation) != 6:
                raise RuntimeError("organic mosaic relation changed format")
            (
                raw_receipts,
                raw_lineages,
                raw_bonds,
                raw_structure_receipt,
                raw_ordered_paths,
                raw_ordered_path_relations,
            ) = raw_relation
            if (
                not isinstance(raw_receipts, list)
                or not isinstance(raw_lineages, list)
                or not isinstance(raw_bonds, list)
                or not isinstance(raw_ordered_paths, list)
                or not isinstance(raw_ordered_path_relations, list)
            ):
                raise RuntimeError("organic mosaic relation changed format")
            receipts = tuple(
                _canonical_sha256(value, "related formation receipt")
                for value in raw_receipts
            )
            shared_lineages = tuple(
                _canonical_lineage_hex(value, "shared mosaic lineage")
                for value in raw_lineages
            )
            relation_bonds = tuple(
                (
                    _canonical_lineage_hex(value[0], "relation bond left lineage"),
                    _canonical_lineage_hex(value[1], "relation bond right lineage"),
                    _nonnegative_integer(value[2], "relation bond parallel ordinal"),
                )
                for value in raw_bonds
                if isinstance(value, tuple) and len(value) == 3
            )
            structure_receipt = _canonical_sha256(
                raw_structure_receipt,
                "organic relation structural receipt",
            )
            ordered_paths: list[
                tuple[
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                ]
            ] = []
            for raw_path in raw_ordered_paths:
                if not isinstance(raw_path, tuple) or len(raw_path) != 2:
                    raise RuntimeError("ordered physical path changed format")
                transfers: list[tuple[str, str, int, int]] = []
                for raw_transfer in raw_path:
                    if not isinstance(raw_transfer, tuple) or len(raw_transfer) != 4:
                        raise RuntimeError("directed physical transfer changed format")
                    carriers_text = raw_transfer[3]
                    if (
                        not isinstance(carriers_text, str)
                        or not carriers_text.isdecimal()
                    ):
                        raise RuntimeError("directed physical transfer lost exact carriers")
                    carriers = int(carriers_text)
                    if carriers <= 0:
                        raise RuntimeError("directed physical transfer carried no material")
                    transfers.append(
                        (
                            _canonical_lineage_hex(raw_transfer[0], "transfer sender"),
                            _canonical_lineage_hex(raw_transfer[1], "transfer receiver"),
                            _nonnegative_integer(raw_transfer[2], "transfer bond ordinal"),
                            carriers,
                        )
                    )
                if transfers[0][1] != transfers[1][0]:
                    raise RuntimeError("ordered physical path is not causally continuous")
                ordered_paths.append((transfers[0], transfers[1]))
            ordered_path_relations: list[
                tuple[
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                    tuple[str, str, int, int],
                ]
            ] = []
            for raw_path_relation in raw_ordered_path_relations:
                if not isinstance(raw_path_relation, tuple) or len(raw_path_relation) != 4:
                    raise RuntimeError("ordered path relation changed format")
                transfers = []
                for raw_transfer in raw_path_relation:
                    if not isinstance(raw_transfer, tuple) or len(raw_transfer) != 4:
                        raise RuntimeError("directed physical transfer changed format")
                    carriers_text = raw_transfer[3]
                    if not isinstance(carriers_text, str) or not carriers_text.isdecimal():
                        raise RuntimeError("directed physical transfer lost exact carriers")
                    carriers = int(carriers_text)
                    if carriers <= 0:
                        raise RuntimeError("directed physical transfer carried no material")
                    transfers.append(
                        (
                            _canonical_lineage_hex(raw_transfer[0], "transfer sender"),
                            _canonical_lineage_hex(raw_transfer[1], "transfer receiver"),
                            _nonnegative_integer(raw_transfer[2], "transfer bond ordinal"),
                            carriers,
                        )
                    )
                if (
                    transfers[0][1] != transfers[1][0]
                    or transfers[2][1] != transfers[3][0]
                    or tuple(item[:3] for item in transfers[:2])
                    != tuple(item[:3] for item in transfers[2:])
                ):
                    raise RuntimeError("ordered path relation did not recur physically")
                ordered_path_relations.append(
                    (transfers[0], transfers[1], transfers[2], transfers[3])
                )
            if (
                len(relation_bonds) != len(raw_bonds)
                or len(receipts) < 2
                or tuple(sorted(set(receipts))) != receipts
                or tuple(sorted(set(shared_lineages))) != shared_lineages
                or tuple(sorted(set(relation_bonds))) != relation_bonds
                or (not shared_lineages and not relation_bonds)
            ):
                raise RuntimeError("organic mosaic relation is not canonical physical evidence")
            organic_mosaic_relations.append(
                (
                    receipts,
                    shared_lineages,
                    relation_bonds,
                    structure_receipt,
                    tuple(ordered_paths),
                    tuple(ordered_path_relations),
                )
            )
        recurrent_complete_neuron_fractal_count = _nonnegative_integer(
            candidate.recurrent_complete_neuron_fractal_count,
            "recurrent complete-neuron fractal count",
        )
        cognitive_ordinal = _nonnegative_integer(
            candidate.cognitive_ordinal, "cognitive ordinal"
        )
        cognitive_trace_count = _nonnegative_integer(
            candidate.cognitive_trace_count, "cognitive trace count"
        )
        cognitive_mosaic_count = _nonnegative_integer(
            candidate.cognitive_mosaic_count, "cognitive mosaic count"
        )
        formation_activation_count = _nonnegative_integer(
            candidate.formation_activation_count,
            "formation activation count",
        )
        partial_cue_reassembly_count = _nonnegative_integer(
            candidate.partial_cue_reassembly_count,
            "partial cue reassembly count",
        )
        endogenous_partial_cue_reassembly_count = _nonnegative_integer(
            candidate.endogenous_partial_cue_reassembly_count,
            "endogenous partial cue reassembly count",
        )
        if endogenous_partial_cue_reassembly_count > partial_cue_reassembly_count:
            raise RuntimeError(
                "endogenous partial cue reassembly exceeds total recurrence"
            )
        internally_reassembled_formation_cues = (
            _internally_reassembled_formation_cue_evidence(
                candidate.internally_reassembled_formation_cues
            )
        )
        externally_reassembled_formation_frontiers = (
            _externally_reassembled_formation_frontier_evidence(
                candidate.externally_reassembled_formation_frontiers
            )
        )
        if (
            len(externally_reassembled_formation_frontiers)
            > partial_cue_reassembly_count
            - endogenous_partial_cue_reassembly_count
        ):
            raise RuntimeError(
                "externally reassembled formation frontiers exceed physical recurrence"
            )
        if (
            len(internally_reassembled_formation_cues)
            > endogenous_partial_cue_reassembly_count
        ):
            raise RuntimeError("internally reassembled formation cues exceed physical recurrence")
        complete_neuron_count = _nonnegative_integer(
            candidate.complete_neuron_count, "complete neuron count"
        )
        developmental_resting_neuron_count = _nonnegative_integer(
            candidate.developmental_resting_neuron_count,
            "developmental resting neuron count",
        )
        physically_transitioned_neuron_count = _nonnegative_integer(
            candidate.physically_transitioned_neuron_count,
            "physically transitioned neuron count",
        )
        metabolically_perturbed_body_receptor_count = _nonnegative_integer(
            candidate.metabolically_perturbed_body_receptor_count,
            "metabolically perturbed body receptor count",
        )
        rest_recovered_neuron_count = _nonnegative_integer(
            candidate.rest_recovered_neuron_count,
            "rest recovered neuron count",
        )
        rest_drained_dissipation_quanta = _nonnegative_integer(
            candidate.rest_drained_dissipation_quanta,
            "rest drained dissipation quanta",
        )
        unmet_dissipation_quanta = _nonnegative_integer(
            candidate.unmet_dissipation_quanta,
            "unmet dissipation quanta",
        )
        externally_perturbed_body_receptor_count = _nonnegative_integer(
            candidate.externally_perturbed_body_receptor_count,
            "externally perturbed body receptor count",
        )
        raw_externally_perturbed_neuron_lineages = (
            candidate.externally_perturbed_neuron_lineages
        )
        if not isinstance(raw_externally_perturbed_neuron_lineages, list):
            raise RuntimeError("externally perturbed neuron lineages changed format")
        externally_perturbed_neuron_lineages = tuple(
            _canonical_lineage_hex(lineage, "externally perturbed neuron lineage")
            for lineage in raw_externally_perturbed_neuron_lineages
        )
        if (
            len(set(externally_perturbed_neuron_lineages))
            != len(externally_perturbed_neuron_lineages)
            or externally_perturbed_body_receptor_count
            > len(externally_perturbed_neuron_lineages)
            * causal_interval_count
        ):
            raise RuntimeError("externally perturbed neuron lineages are inconsistent")
        raw_ingress_sense_counts = candidate.receptor_ingress_sense_counts
        if (
            not isinstance(raw_ingress_sense_counts, tuple)
            or len(raw_ingress_sense_counts) != 6
        ):
            raise RuntimeError("receptor ingress sense counts changed format")
        receptor_ingress_sense_counts = tuple(
            _nonnegative_integer(value, "receptor ingress sense count")
            for value in raw_ingress_sense_counts
        )
        receptor_ingress_changing_count = _nonnegative_integer(
            candidate.receptor_ingress_changing_count,
            "receptor ingress changing count",
        )
        receptor_ingress_quiescent_count = _nonnegative_integer(
            candidate.receptor_ingress_quiescent_count,
            "receptor ingress quiescent count",
        )
        if (
            sum(receptor_ingress_sense_counts) != source_port_count
            or receptor_ingress_changing_count
            + receptor_ingress_quiescent_count
            != source_port_count
        ):
            raise RuntimeError("receptor ingress observation lost source ports")
        motor_unit_recruitments = _motor_unit_recruitment_evidence(
            candidate.motor_unit_recruitments
        )
        raw_body_effector_bindings = candidate.body_effector_bindings
        if not isinstance(raw_body_effector_bindings, list):
            raise RuntimeError("body effector bindings changed format")
        body_effector_bindings: list[tuple[str, str, str, int]] = []
        for raw in raw_body_effector_bindings:
            if not isinstance(raw, tuple) or len(raw) != 4:
                raise RuntimeError("body effector binding changed format")
            lineage = _canonical_lineage_hex(raw[0], "body effector motor lineage")
            axis = raw[1]
            direction = raw[2]
            carriers = _positive_integer(raw[3], "body effector carriers")
            if (
                not isinstance(axis, str)
                or not axis
                or direction not in {"toward_minimum", "toward_maximum"}
            ):
                raise RuntimeError("body effector binding is not typed anatomy")
            body_effector_bindings.append((lineage, axis, direction, carriers))
        if len({binding[0] for binding in body_effector_bindings}) != len(
            body_effector_bindings
        ):
            raise RuntimeError("one motor lineage carries multiple body effector bindings")

        raw_body_consequences = candidate.articulated_body_consequences
        if not isinstance(raw_body_consequences, list):
            raise RuntimeError("articulated body consequences changed format")
        articulated_body_consequences: list[
            tuple[int, str, str, int, int, int, int, int, int, int, int]
        ] = []
        for raw in raw_body_consequences:
            if not isinstance(raw, tuple) or len(raw) != 11:
                raise RuntimeError("articulated body consequence changed format")
            source_tick = _nonnegative_integer(raw[0], "body consequence source tick")
            axis = raw[1]
            unit = raw[2]
            predecessor_position = _signed_integer(raw[3], "body predecessor position")
            successor_position = _signed_integer(raw[4], "body successor position")
            signed_displacement = _signed_integer(raw[5], "body signed displacement")
            toward_minimum = _nonnegative_integer(raw[6], "body toward-minimum carriers")
            toward_maximum = _nonnegative_integer(raw[7], "body toward-maximum carriers")
            opposed = _nonnegative_integer(raw[8], "body opposed carriers")
            applied = _nonnegative_integer(raw[9], "body applied displacement")
            stalled = _nonnegative_integer(raw[10], "body stalled carriers")
            net = abs(toward_maximum - toward_minimum)
            if (
                source_tick < predecessor_organism_tick
                or source_tick >= organism_tick
                or not isinstance(axis, str)
                or not axis
                or unit not in {"millidegree", "micrometre", "square_millimetre"}
                or successor_position - predecessor_position != signed_displacement
                or opposed != min(toward_minimum, toward_maximum)
                or applied != abs(signed_displacement)
                or applied + stalled != net
            ):
                raise RuntimeError("articulated body consequence lost exact mechanics")
            articulated_body_consequences.append(
                (
                    source_tick,
                    axis,
                    unit,
                    predecessor_position,
                    successor_position,
                    signed_displacement,
                    toward_minimum,
                    toward_maximum,
                    opposed,
                    applied,
                    stalled,
                )
            )

        raw_body_sources = candidate.body_proprioceptive_sources
        raw_body_source_extents = candidate.body_proprioceptive_source_extents
        if (
            not isinstance(raw_body_sources, list)
            or not isinstance(raw_body_source_extents, list)
            or len(raw_body_sources) != len(raw_body_source_extents)
        ):
            raise RuntimeError("body proprioceptive sources changed format")
        body_proprioceptive_sources: list[bytes] = []
        body_proprioceptive_source_extents: list[
            tuple[int, int, int, int, int]
        ] = []
        prior_source_tick: int | None = None
        for raw_body, raw_extent in zip(
            raw_body_sources, raw_body_source_extents, strict=True
        ):
            if (
                not isinstance(raw_body, bytes)
                or not raw_body.startswith(b"GLJSRC03")
                or not isinstance(raw_extent, tuple)
                or len(raw_extent) != 5
            ):
                raise RuntimeError("body proprioceptive source is not exact GLJSRC03")
            source_tick = _nonnegative_integer(raw_extent[0], "body source tick")
            port_count = _positive_integer(raw_extent[1], "body source port count")
            sample_count = _positive_integer(raw_extent[2], "body source sample count")
            occurrence_count = _positive_integer(
                raw_extent[3], "body source occurrence count"
            )
            frame_count = _positive_integer(raw_extent[4], "body source frame count")
            if (
                source_tick < predecessor_organism_tick
                or source_tick >= organism_tick
                or prior_source_tick is not None
                and source_tick <= prior_source_tick
                or port_count != occurrence_count * 2
                or sample_count != port_count * 2
                or frame_count != occurrence_count * 2
            ):
                raise RuntimeError("body proprioceptive source extents lost causality")
            prior_source_tick = source_tick
            body_proprioceptive_sources.append(raw_body)
            body_proprioceptive_source_extents.append(
                (source_tick, port_count, sample_count, occurrence_count, frame_count)
            )
        if bool(body_proprioceptive_sources) != bool(articulated_body_consequences):
            raise RuntimeError("body consequence and proprioceptive source disagree")
        if body_feedback_reentered:
            if (
                causal_interval_count
                != requested_causal_interval_count
                + len(body_proprioceptive_sources)
                or source_port_count
                != requested_source_port_count
                + sum(extent[1] for extent in body_proprioceptive_source_extents)
            ):
                raise RuntimeError(
                    "native body feedback did not re-enter exactly once"
                )
        elif (
            causal_interval_count != requested_causal_interval_count
            or source_port_count != requested_source_port_count
        ):
            raise RuntimeError("native prepare inserted an unauthorized causal source")
        raw_causal_interval_evidence = getattr(
            candidate, "causal_interval_evidence", None
        )
        causal_interval_evidence = (
            ()
            if raw_causal_interval_evidence is None
            else _causal_interval_evidence(
                raw_causal_interval_evidence,
                predecessor_organism_tick,
            )
        )
        if (
            len(causal_interval_evidence) != causal_interval_count
            and (causal_interval_evidence or causal_interval_count > 1)
        ):
            raise RuntimeError("causal interval evidence lost a physical boundary")
        # Older pure-Python boundary doubles carry no layer-13 observation;
        # absence is exactly an empty transient recruitment list. Native
        # production candidates expose the field explicitly.
        raw_articulatory_recruitments = getattr(
            candidate, "articulatory_unit_recruitments", []
        )
        articulatory_unit_recruitments = _articulatory_unit_recruitments(
            raw_articulatory_recruitments
        )
        appended_physically_transitioned_neuron_count = _nonnegative_integer(
            getattr(candidate, "appended_physically_transitioned_neuron_count", 0),
            "appended physically transitioned neuron count",
        )
        appended_complete_neuron_fractal_count = _nonnegative_integer(
            getattr(candidate, "appended_complete_neuron_fractal_count", 0),
            "appended complete-neuron fractal count",
        )
        appended_externally_perturbed_body_receptor_count = _nonnegative_integer(
            getattr(
                candidate,
                "appended_externally_perturbed_body_receptor_count",
                0,
            ),
            "appended externally perturbed body receptor count",
        )
        appended_articulatory_unit_recruitment_count = _nonnegative_integer(
            getattr(candidate, "appended_articulatory_unit_recruitment_count", 0),
            "appended articulatory-unit recruitment count",
        )
        # A mounted joint cohort exists only where at least two ports share
        # one exact source clock, so a lawful episode can evaluate zero
        # mounted cohorts (cognition still receives its occurrences).
        cohort_count_changed = current_cohort_evaluation_count > (
            source_port_count * causal_interval_count
        )
        reached_neuron_growth = (
            complete_neuron_count - active_before.complete_neuron_count
        )
        claimed_resting_neurons = (
            active_before.developmental_resting_neuron_count
            - developmental_resting_neuron_count
        )
        if (
            predecessor_state_sha256 != active_before.state_sha256
            or predecessor_organism_tick != active_before.organism_tick
            or organism_tick != predecessor_organism_tick + causal_interval_count
            or predecessor_fabric_generation
            != active_before.fabric_generation
            or fabric_generation
            != predecessor_fabric_generation + causal_interval_count
            or predecessor_mounted_generation
            != active_before.mounted_generation
            or mounted_generation
            != predecessor_mounted_generation + causal_interval_count
            or predecessor_authentication_count != 0
            or predecessor_decode_count != 0
            or predecessor_rebuilt_field_count != 0
            or cohort_count_changed
            or successor_seal_count != 1
            or recurrent_complete_neuron_fractal_count
            > complete_neuron_fractal_count
            or reached_neuron_growth < 0
            or claimed_resting_neurons < 0
            or claimed_resting_neurons > reached_neuron_growth
            or endogenous_partial_cue_reassembly_count
            > partial_cue_reassembly_count
            or metabolically_perturbed_body_receptor_count
            > physically_transitioned_neuron_count
            or not isinstance(candidate.physical_transition_claimed, bool)
            or not isinstance(candidate.cognitive_formation_claimed, bool)
            or candidate.physical_transition_claimed
            != (physically_transitioned_neuron_count > 0)
            # A cognitive-formation claim must ride on evidence of the
            # formation kind: mosaic admission, activations, or partial-cue
            # reassembly stand on their own counters; trace/ordinal advance
            # is only lawful in a step that delivered genuine neuronal
            # fractals. A bare-DSF prepare dressing itself in advanced
            # cognitive counters is an impostor.
            or (
                candidate.cognitive_formation_claimed
                and cognitive_mosaic_count <= active_before.cognitive_mosaic_count
                and formation_activation_count == 0
                # Native recurrence counts describe this prepared interval;
                # they are not retained organism totals. One recurrence now
                # remains evidence even when the preceding interval also
                # observed exactly one recurrence.
                and partial_cue_reassembly_count == 0
                and complete_neuron_fractal_count == 0
                and not organic_mosaic_relations
            )
            or candidate.python_callback_count != 0
        ):
            raise RuntimeError("resident organism prepare changed causal physics")
        active_after = self.readiness()
        active_after_signature = _observation_signature(active_after)
        if candidate_committed:
            if (
                active_after.state_sha256 != prepared_state_sha256
                or active_after.organism_tick != organism_tick
                or active_after.fabric_generation != fabric_generation
                or active_after.mounted_generation != mounted_generation
            ):
                raise RuntimeError(
                    "resident direct commit did not publish its prepared state"
                )
        elif active_after_signature != _observation_signature(active_before):
            raise RuntimeError("resident organism prepare published pending state")
        return ResidentPrepareEvidence(
            token=token,
            token_hex=candidate.token_hex,
            predecessor_state_sha256=predecessor_state_sha256,
            prepared_state_sha256=prepared_state_sha256,
            predecessor_organism_tick=predecessor_organism_tick,
            organism_tick=organism_tick,
            predecessor_fabric_generation=predecessor_fabric_generation,
            fabric_generation=fabric_generation,
            predecessor_mounted_generation=predecessor_mounted_generation,
            mounted_generation=mounted_generation,
            predecessor_authentication_count=predecessor_authentication_count,
            predecessor_decode_count=predecessor_decode_count,
            predecessor_rebuilt_field_count=predecessor_rebuilt_field_count,
            current_cohort_evaluation_count=current_cohort_evaluation_count,
            successor_seal_count=successor_seal_count,
            dsf_delivery_count=dsf_delivery_count,
            complete_neuron_fractal_count=complete_neuron_fractal_count,
            recurrent_complete_neuron_fractal_count=(
                recurrent_complete_neuron_fractal_count
            ),
            cognitive_ordinal=cognitive_ordinal,
            cognitive_trace_count=cognitive_trace_count,
            cognitive_mosaic_count=cognitive_mosaic_count,
            formation_activation_count=formation_activation_count,
            partial_cue_reassembly_count=partial_cue_reassembly_count,
            endogenous_partial_cue_reassembly_count=(
                endogenous_partial_cue_reassembly_count
            ),
            internally_reassembled_formation_cues=tuple(
                internally_reassembled_formation_cues
            ),
            externally_reassembled_formation_frontiers=tuple(
                externally_reassembled_formation_frontiers
            ),
            physical_transition_claimed=candidate.physical_transition_claimed,
            cognitive_formation_claimed=candidate.cognitive_formation_claimed,
            python_callback_count=0,
            complete_neuron_count=complete_neuron_count,
            developmental_resting_neuron_count=(
                developmental_resting_neuron_count
            ),
            physically_transitioned_neuron_count=(
                physically_transitioned_neuron_count
            ),
            metabolically_perturbed_body_receptor_count=(
                metabolically_perturbed_body_receptor_count
            ),
            rest_recovered_neuron_count=rest_recovered_neuron_count,
            rest_drained_dissipation_quanta=rest_drained_dissipation_quanta,
            unmet_dissipation_quanta=unmet_dissipation_quanta,
            externally_perturbed_body_receptor_count=(
                externally_perturbed_body_receptor_count
            ),
            externally_perturbed_neuron_lineages=(
                externally_perturbed_neuron_lineages
            ),
            receptor_ingress_sense_counts=receptor_ingress_sense_counts,
            receptor_ingress_changing_count=receptor_ingress_changing_count,
            receptor_ingress_quiescent_count=receptor_ingress_quiescent_count,
            motor_unit_recruitments=tuple(motor_unit_recruitments),
            body_effector_bindings=tuple(body_effector_bindings),
            articulated_body_consequences=tuple(
                articulated_body_consequences
            ),
            body_proprioceptive_sources=tuple(body_proprioceptive_sources),
            body_proprioceptive_source_extents=tuple(
                body_proprioceptive_source_extents
            ),
            articulatory_unit_recruitments=tuple(
                articulatory_unit_recruitments
            ),
            appended_physically_transitioned_neuron_count=(
                appended_physically_transitioned_neuron_count
            ),
            appended_complete_neuron_fractal_count=(
                appended_complete_neuron_fractal_count
            ),
            appended_externally_perturbed_body_receptor_count=(
                appended_externally_perturbed_body_receptor_count
            ),
            appended_articulatory_unit_recruitment_count=(
                appended_articulatory_unit_recruitment_count
            ),
            emitted_neuron_fractals=tuple(emitted_neuron_fractals),
            active_physical_bonds=tuple(active_physical_bonds),
            changed_contact_channel_states=changed_contact_channel_states,
            physical_frontier_routes=physical_frontier_routes,
            preceding_distinct_physical_frontier_routes=(
                preceding_distinct_physical_frontier_routes
            ),
            reached_and_foregone_physical_frontier_routes=(
                reached_and_foregone_physical_frontier_routes
            ),
            working_causal_continuations=working_causal_continuations,
            settled_working_frontier=settled_working_frontier,
            physical_prediction_alternatives=physical_prediction_alternatives,
            body_consequence_transfers=body_consequence_transfers,
            affective_balance_trajectories=affective_balance_trajectories,
            localized_fluid_chemistry=localized_fluid_chemistry,
            localized_metabolic_strain_evaluated_body_receptor_lineages=(
                localized_metabolic_strain_evaluated_body_receptor_lineages
            ),
            localized_metabolic_strain=localized_metabolic_strain,
            organic_mosaic_relations=tuple(organic_mosaic_relations),
            causal_interval_evidence=causal_interval_evidence,
        )

    def prepare_authored_contacts(
        self, contacts: object
    ) -> ResidentContactGrowthEvidence:
        """Prepare one AUTHORED contact growth and return its receipts.

        ``contacts`` is a sequence of ``(left_sensor_id, left_substream_id,
        right_sensor_id, right_substream_id, conductance_picosiemens)``: the
        caller names two of its OWN declared receptors and the conductance of
        the contact between them, exactly the authorship growth DNA carries at
        genesis.  This boundary derives no adjacency and no conductance.

        Growth is append-only in the body: existing contacts keep their index,
        endpoints, conductance and retained carrier phase. A growth carries
        no sensory occurrence, so no fractal may be claimed. The resident
        cognitive generation advances once because the body itself changed.
        """

        authored: list[tuple[str, str, str, str, int]] = []
        for entry in contacts:
            left_sensor, left_substream, right_sensor, right_substream, conductance = (
                entry
            )
            if (
                not isinstance(left_sensor, str)
                or not isinstance(left_substream, str)
                or not isinstance(right_sensor, str)
                or not isinstance(right_substream, str)
                or not left_sensor
                or not left_substream
                or not right_sensor
                or not right_substream
            ):
                raise TypeError("authored contact endpoints must be declared receptor names")
            authored.append(
                (
                    left_sensor,
                    left_substream,
                    right_sensor,
                    right_substream,
                    _positive_integer(conductance, "authored contact conductance"),
                )
            )
        if not authored:
            raise ValueError("authored contact growth requires at least one contact")
        active_before = self.readiness()
        candidate = self.__runtime.prepare_authored_contacts(authored)
        if not isinstance(candidate, self.__prepare_type):
            raise TypeError("resident organism prepare returned a structural impostor")
        if candidate.schema != PREPARE_SCHEMA:
            raise RuntimeError("resident organism prepare schema changed")
        token = candidate.token
        if (
            not isinstance(token, bytes)
            or len(token) != 32
            or candidate.token_hex != token.hex()
        ):
            raise RuntimeError("resident organism prepare token changed format")
        predecessor_state_sha256 = _canonical_sha256(
            candidate.predecessor_state_sha256, "predecessor state receipt"
        )
        prepared_state_sha256 = _canonical_sha256(
            candidate.prepared_state_sha256, "prepared state receipt"
        )
        if (
            predecessor_state_sha256 != active_before.state_sha256
            or candidate.predecessor_organism_tick != active_before.organism_tick
            or candidate.organism_tick != active_before.organism_tick + 1
            or candidate.predecessor_fabric_generation
            != active_before.fabric_generation
            or candidate.fabric_generation != active_before.fabric_generation + 1
            or candidate.mounted_generation
            != active_before.mounted_generation + 1
            or candidate.dsf_delivery_count != 0
            or candidate.complete_neuron_fractal_count != 0
            or candidate.physical_transition_claimed
            or candidate.cognitive_formation_claimed
        ):
            raise RuntimeError(
                "resident organism contact growth changed causal physics"
            )
        active_after = self.readiness()
        if _observation_signature(active_after) != _observation_signature(
            active_before
        ):
            raise RuntimeError("resident organism prepare published pending state")
        return ResidentContactGrowthEvidence(
            token=token,
            token_hex=candidate.token_hex,
            predecessor_state_sha256=predecessor_state_sha256,
            prepared_state_sha256=prepared_state_sha256,
            predecessor_organism_tick=candidate.predecessor_organism_tick,
            organism_tick=candidate.organism_tick,
            predecessor_fabric_generation=candidate.predecessor_fabric_generation,
            fabric_generation=candidate.fabric_generation,
            mounted_generation=candidate.mounted_generation,
            authored_contact_count=len(authored),
        )

    def observe_cohort_contacts(self) -> tuple[tuple[int, int], ...]:
        """Decoded ``(member_count, contact_count)`` per living cohort."""

        return tuple(
            (int(members), int(contacts))
            for members, contacts in self.__runtime.observe_cohort_contacts()
        )

    def observe_reached_neuron_count_by_layer(
        self,
    ) -> tuple[tuple[int, int], ...]:
        """Decoded ``(layer, reached_count)`` from persisted neuron anatomy."""

        observed = tuple(
            (
                _nonnegative_integer(layer, "developmental layer"),
                _nonnegative_integer(count, "reached neuron layer count"),
            )
            for layer, count in (
                self.__runtime.observe_reached_neuron_count_by_layer()
            )
        )
        if any(
            count == 0
            or (index > 0 and observed[index - 1][0] >= layer)
            for index, (layer, count) in enumerate(observed)
        ):
            raise RuntimeError(
                "reached neuron layer distribution is not canonical"
            )
        return observed

    def observe_reached_neuron_electrical_by_layer(
        self,
    ) -> tuple[tuple[int, int, int, int, int, int], ...]:
        """Read-only layer, charge, capacitance and carrier material."""

        before = self.readiness()
        observed = tuple(
            (
                _nonnegative_integer(layer, "developmental layer"),
                int(charge),
                int(capacitance_numerator),
                _positive_integer(
                    capacitance_denominator, "capacitance denominator"
                ),
                _nonnegative_integer(intracellular, "intracellular carriers"),
                _nonnegative_integer(extracellular, "extracellular carriers"),
            )
            for (
                layer,
                charge,
                capacitance_numerator,
                capacitance_denominator,
                intracellular,
                extracellular,
            ) in (
                self.__runtime.observe_reached_neuron_electrical_by_layer()
            )
        )
        if len(observed) != before.complete_neuron_count:
            raise RuntimeError("reached neuron electrical projection changed width")
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("reached neuron electrical observation advanced the organism")
        return observed

    def observe_reached_contact_count_by_layer_pair(
        self,
    ) -> tuple[tuple[int, int, int], ...]:
        """Read-only sparse-contact counts by endpoint layer pair."""

        before = self.readiness()
        observed = tuple(
            (
                _nonnegative_integer(left, "left developmental layer"),
                _nonnegative_integer(right, "right developmental layer"),
                _nonnegative_integer(count, "interlayer contact count"),
            )
            for left, right, count in (
                self.__runtime.observe_reached_contact_count_by_layer_pair()
            )
        )
        if any(left > right or count == 0 for left, right, count in observed):
            raise RuntimeError("reached contact layer projection is not canonical")
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("reached contact observation advanced the organism")
        return observed

    def observe_reached_contact_channel_states(
        self,
    ) -> tuple[tuple[str, str, int, int, int, int, int, int], ...]:
        """Read exact retained channel and sub-transition phase state."""

        before = self.readiness()
        observed = tuple(
            (
                _canonical_lineage_hex(left, "contact left lineage"),
                _canonical_lineage_hex(right, "contact right lineage"),
                _nonnegative_integer(parallel, "contact parallel ordinal"),
                _nonnegative_integer(population, "conducting channel population"),
                _signed_integer(
                    transition_phase_numerator, "contact transition phase numerator"
                ),
                _positive_exact_integer(
                    transition_phase_denominator, "contact transition phase denominator"
                ),
                _signed_integer(conductance_numerator, "contact conductance numerator"),
                _positive_exact_integer(
                    conductance_denominator, "contact conductance denominator"
                ),
            )
            for (
                left,
                right,
                parallel,
                population,
                transition_phase_numerator,
                transition_phase_denominator,
                conductance_numerator,
                conductance_denominator,
            ) in self.__runtime.observe_reached_contact_channel_states()
        )
        if any(
            left >= right
            or population > 6_400
            or transition_phase_numerator < 0
            or transition_phase_numerator >= transition_phase_denominator
            or conductance_numerator <= 0
            or (index > 0 and observed[index - 1][:3] >= row[:3])
            for index, row in enumerate(observed)
            for (
                left,
                right,
                _parallel,
                population,
                transition_phase_numerator,
                transition_phase_denominator,
                conductance_numerator,
                _conductance_denominator,
            ) in (row,)
        ):
            raise RuntimeError("reached contact channel projection is not canonical")
        if self.readiness().state_sha256 != before.state_sha256:
            raise RuntimeError("reached contact channel observation advanced the organism")
        return observed

    def observe_reached_source_site_count(
        self,
        sensor_id: str,
        substream_id: str,
    ) -> int:
        """Count reached cells with one exact persisted physical source."""

        if not isinstance(sensor_id, str) or not sensor_id:
            raise TypeError("reached source sensor identity must be nonempty text")
        if not isinstance(substream_id, str) or not substream_id:
            raise TypeError("reached source substream identity must be nonempty text")
        return _nonnegative_integer(
            self.__runtime.observe_reached_source_site_count(
                sensor_id,
                substream_id,
            ),
            "reached source site count",
        )

    def commit(self, token: bytes) -> NativeResidentObservationView:
        """Commit the native pending candidate selected by its fixed token."""

        self.__runtime.commit(_exact_token(token))
        return self.readiness()

    def discard(self, token: bytes) -> NativeResidentObservationView:
        """Discard the native pending candidate and preserve active state."""

        active_before = self.readiness()
        self.__runtime.discard(_exact_token(token))
        active_after = self.readiness()
        if _observation_signature(active_after) != _observation_signature(
            active_before
        ):
            raise RuntimeError("resident organism discard changed active state")
        return active_after


def restore_native_resident_organism(
    *,
    current_envelope: bytes,
    max_envelope_bytes: int,
    max_fabric_bytes: int,
    max_logical_peak_bytes: int,
) -> NativeResidentOrganism:
    """Cold restore one current GLORUN state into one native resident runtime."""

    if (
        not isinstance(current_envelope, bytes)
        or not current_envelope.startswith(b"GLORUN01")
    ):
        raise TypeError("resident organism cold restore requires GLORUN bytes")
    envelope, fabric, logical = _validate_budget(
        max_envelope_bytes,
        max_fabric_bytes,
        max_logical_peak_bytes,
    )
    core = _native_core()
    runtime_type = _concrete_class(core, "NativeResidentOrganismRuntime")
    observation_type = _concrete_class(
        core, "NativeResidentOrganismObservation"
    )
    prepare_type = _concrete_class(core, "NativeResidentOrganismPrepare")
    restore = getattr(core, "restore_native_resident_organism_runtime", None)
    if not callable(restore):
        raise RuntimeError("guala_core does not expose resident cold restore")
    runtime = restore(current_envelope, envelope, fabric, logical)
    if not isinstance(runtime, runtime_type):
        raise TypeError("resident organism cold restore returned a structural impostor")
    if runtime.schema != RUNTIME_SCHEMA:
        raise RuntimeError("resident organism runtime schema changed")
    organism = NativeResidentOrganism(
        _FACTORY_AUTHORITY,
        runtime,
        runtime_type,
        observation_type,
        prepare_type,
    )
    organism.save()
    return organism


def exact_native_yaw_trajectory(
    *,
    predecessor_heading_millidegrees: int,
    signed_displacement_millidegrees: int,
    duration_microseconds: int,
) -> tuple[int, tuple[int, ...]]:
    """Return the native minimum-jerk yaw path on the 1 ms body clock."""

    trajectory = getattr(_native_core(), "exact_virtual_yaw_trajectory", None)
    if not callable(trajectory):
        raise RuntimeError("guala_core does not expose exact virtual yaw physics")
    successor, steps = trajectory(
        predecessor_heading_millidegrees,
        signed_displacement_millidegrees,
        duration_microseconds,
    )
    return int(successor), tuple(int(step) for step in steps)


def exact_articulatory_unit_trajectory(
    *,
    recruitments: tuple[tuple[int, int], ...],
) -> tuple[int, tuple[int, ...], bytes, int, int, int, int, int, int, int]:
    """Settle native layer-13 discharge through the bounded vocal body."""

    trajectory = getattr(_native_core(), "exact_articulatory_unit_trajectory", None)
    if not callable(trajectory):
        raise RuntimeError(
            "guala_core does not expose native articulatory body physics"
        )
    (
        sample_rate_hz,
        radiated_pressure_pcm,
        body_mechanical_trajectories,
        peak_breath_flow_pcm,
        glottal_open_samples_at_apex,
        mouth_area_square_millimetres_at_apex,
        perioral_area_displacement_square_millimetres,
        applied_motor_quanta,
        stalled_motor_quanta,
        relaxation_sample_count,
    ) = trajectory(list(recruitments))
    return (
        int(sample_rate_hz),
        tuple(int(value) for value in radiated_pressure_pcm),
        bytes(body_mechanical_trajectories),
        int(peak_breath_flow_pcm),
        int(glottal_open_samples_at_apex),
        int(mouth_area_square_millimetres_at_apex),
        int(perioral_area_displacement_square_millimetres),
        int(applied_motor_quanta),
        int(stalled_motor_quanta),
        int(relaxation_sample_count),
    )


def migrate_native_resident_organism_exact_energy(
    *,
    current_envelope: bytes,
    expected_predecessor_sha256: str,
    max_envelope_bytes: int,
    max_fabric_bytes: int,
    max_logical_peak_bytes: int,
) -> bytes:
    """Derive the explicit current-format body from one exact predecessor.

    The native boundary is idempotent: an already-current body is returned
    byte-identically. Publication decides whether that is a no-op; treating
    equality as an error here made every explicitly authorized restart fail.
    """

    if (
        not isinstance(current_envelope, bytes)
        or not current_envelope.startswith(b"GLORUN01")
    ):
        raise TypeError("exact-energy migration requires GLORUN bytes")
    predecessor = _canonical_sha256(
        expected_predecessor_sha256, "exact-energy predecessor receipt"
    )
    if hashlib.sha256(current_envelope).hexdigest() != predecessor:
        raise RuntimeError("exact-energy migration predecessor changed")
    envelope, fabric, logical = _validate_budget(
        max_envelope_bytes,
        max_fabric_bytes,
        max_logical_peak_bytes,
    )
    migrate = getattr(
        _native_core(), "migrate_native_resident_organism_exact_energy", None
    )
    if not callable(migrate):
        raise RuntimeError("guala_core does not expose exact-energy migration")
    migrated = bytes(migrate(current_envelope, envelope, fabric, logical))
    if not migrated.startswith(b"GLORUN01") or len(migrated) > envelope:
        raise RuntimeError("current-format migration produced an invalid body")
    restore_native_resident_organism(
        current_envelope=migrated,
        max_envelope_bytes=envelope,
        max_fabric_bytes=fabric,
        max_logical_peak_bytes=logical,
    )
    return migrated


def _validated_growth_dna(
    growth_dna: object,
    episode_type: type,
) -> tuple[object, list[tuple[list[int], list[tuple[int, int, int]]]]]:
    """Validate authored growth DNA: (anatomy_episode, seed_groups).

    Each seed group is (port_indices, contacts): port_indices name joint
    source ports of the anatomy episode, and each contact is
    (left_seed_index, right_seed_index, conductance_picosiemens). Every value
    is authored by the caller; nothing is defaulted or inferred here.
    """

    if not isinstance(growth_dna, (tuple, list)) or len(growth_dna) != 2:
        raise TypeError(
            "resident organism growth_dna must be (anatomy_episode, seed_groups)"
        )
    anatomy_episode, seed_groups = growth_dna
    if not isinstance(anatomy_episode, episode_type):
        raise TypeError(
            "resident organism growth_dna anatomy episode must be a concrete "
            "native joint source episode"
        )
    if not isinstance(seed_groups, (tuple, list)) or not seed_groups:
        raise ValueError(
            "resident organism growth_dna requires at least one authored seed group"
        )

    def _index(value: object, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"growth_dna {label} must be a nonnegative integer")
        return value

    validated_groups: list[tuple[list[int], list[tuple[int, int, int]]]] = []
    for group_index, group in enumerate(seed_groups):
        if not isinstance(group, (tuple, list)) or len(group) != 2:
            raise TypeError(
                f"growth_dna seed group {group_index} must be "
                "(port_indices, contacts)"
            )
        port_indices, contacts = group
        if not isinstance(port_indices, (tuple, list)) or not port_indices:
            raise ValueError(
                f"growth_dna seed group {group_index} must name at least one "
                "port index"
            )
        validated_ports = [
            _index(port_index, f"seed group {group_index} port index")
            for port_index in port_indices
        ]
        if not isinstance(contacts, (tuple, list)):
            raise TypeError(
                f"growth_dna seed group {group_index} contacts must be a sequence"
            )
        validated_contacts: list[tuple[int, int, int]] = []
        for contact in contacts:
            if not isinstance(contact, (tuple, list)) or len(contact) != 3:
                raise TypeError(
                    f"growth_dna seed group {group_index} contact must be "
                    "(left_seed_index, right_seed_index, conductance_picosiemens)"
                )
            left, right, conductance = contact
            if isinstance(conductance, bool) or not isinstance(conductance, int):
                raise ValueError(
                    f"growth_dna seed group {group_index} conductance must be "
                    "an authored integer picosiemens value"
                )
            validated_contacts.append(
                (
                    _index(left, f"seed group {group_index} contact left index"),
                    _index(right, f"seed group {group_index} contact right index"),
                    conductance,
                )
            )
        validated_groups.append((validated_ports, validated_contacts))
    return anatomy_episode, validated_groups


def create_native_resident_organism(
    *,
    organism_identity: str,
    organism_tick: int = 0,
    growth_dna: object,
    max_envelope_bytes: int,
    max_fabric_bytes: int,
    max_logical_peak_bytes: int,
) -> NativeResidentOrganism:
    """Create the canonical native genesis carrying authored growth DNA.

    ``growth_dna`` is required: growth never invents electrical contacts, so a
    genesis without authored developmental seeds could never form a physical
    mosaic. The seeded genesis is still structurally empty — zero cohorts,
    traces, and mosaics — until its seeds are reached and expressed.
    """

    if not isinstance(organism_identity, str) or not organism_identity:
        raise TypeError("resident organism genesis identity must be text")
    tick = _nonnegative_integer(organism_tick, "genesis organism tick")
    envelope, fabric, logical = _validate_budget(
        max_envelope_bytes,
        max_fabric_bytes,
        max_logical_peak_bytes,
    )
    core = _native_core()
    runtime_type = _concrete_class(core, "NativeResidentOrganismRuntime")
    observation_type = _concrete_class(
        core, "NativeResidentOrganismObservation"
    )
    prepare_type = _concrete_class(core, "NativeResidentOrganismPrepare")
    episode_type = _concrete_class(core, "NativeJointSourceEpisode")
    anatomy_episode, seed_groups = _validated_growth_dna(
        growth_dna, episode_type
    )
    create = getattr(
        core, "create_native_resident_organism_runtime_with_growth_dna", None
    )
    if not callable(create):
        raise RuntimeError(
            "guala_core does not expose resident growth-dna genesis"
        )
    runtime = create(
        organism_identity,
        tick,
        anatomy_episode,
        seed_groups,
        envelope,
        fabric,
        logical,
    )
    if not isinstance(runtime, runtime_type):
        raise TypeError("resident organism genesis returned a structural impostor")
    if runtime.schema != RUNTIME_SCHEMA:
        raise RuntimeError("resident organism genesis runtime schema changed")
    organism = NativeResidentOrganism(
        _FACTORY_AUTHORITY,
        runtime,
        runtime_type,
        observation_type,
        prepare_type,
    )
    observation = organism.readiness()
    if (
        observation.identity != organism_identity
        or observation.organism_tick != tick
        or observation.fabric_generation != 0
        or observation.mounted_generation != 0
        or observation.joint_field_count != 0
        or observation.joint_neuron_count != 0
        or observation.cognitive_ordinal != 0
        or observation.cognitive_trace_count != 0
        or observation.cognitive_mosaic_count != 0
    ):
        raise RuntimeError("resident organism genesis was not structurally empty")
    organism.save()
    return organism


__all__ = (
    "NativeResidentObservationView",
    "NativeResidentOrganism",
    "OBSERVATION_SCHEMA",
    "PREPARE_SCHEMA",
    "RUNTIME_SCHEMA",
    "ResidentCausalIntervalEvidence",
    "ResidentPrepareEvidence",
    "ResidentUnsealedIntakeEvidence",
    "create_native_resident_organism",
    "exact_articulatory_unit_trajectory",
    "exact_native_yaw_trajectory",
    "restore_native_resident_organism",
    "migrate_native_resident_organism_exact_energy",
)
