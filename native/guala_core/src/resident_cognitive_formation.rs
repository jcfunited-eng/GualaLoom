//! Resident complete-neuron boundary.
//!
//! `GLCOG012` is the current resident complete-neuron carrier. On the first
//! admitted source occurrence it creates and retains exact source-specialized
//! virtual-material neuron cells. Explicit growth-DNA electrical seeds remain
//! unexpressed until their exact source-site cohort is reached, then become the
//! cohort's physical contacts exactly once. It retains at most one bounded
//! in-progress experience and one post-quiescence multi-neuron physical state
//! per cohort, so genuine fractals remain available for later recurrence.
//! A later proper partial cue may admit a physical mosaic only through the
//! complete learned, unlearned-control, and cold-restored recurrence law. The
//! admitted mosaic is retained once at organism scope by stable neuron lineage
//! and stable physical-bond references; cohort-local fluid, electrical, and
//! recovery state remains separate. It
//! never infers contacts or claims cognition merely from a seed, DSF delivery,
//! or three retained fractals.

use crate::auditory_receptor_work::{
    derive_auditory_receptor_sample_range_work, derive_auditory_receptor_work,
    quantize_auditory_delivery, AuditoryReceptorAnatomy, AuditoryReceptorWorkError,
    COCHLEAR_BAND_PRESSURE_QUANTITY, COCHLEAR_REFERENCE_PRESSURE_UNIT,
};
use crate::articulatory_receptor_work::{
    derive_articulatory_receptor_sample_range_work, quantize_articulatory_delivery,
    ArticulatoryReceptorAnatomy, ArticulatoryReceptorWorkError,
    ARTICULATORY_MECHANICAL_FRACTION_UNIT, LARYNGEAL_GLOTTAL_OPENING_QUANTITY,
    ORAL_APERTURE_AREA_QUANTITY, PERIORAL_SKIN_DEFORMATION_QUANTITY,
    RESPIRATORY_VOLUME_VELOCITY_QUANTITY,
};
use crate::chemical_receptor_work::{
    derive_chemical_receptor_sample_range_work, quantize_chemical_delivery,
    ChemicalReceptorAnatomy, ChemicalReceptorWorkError, GUSTATORY_CONTACT_CONCENTRATION_QUANTITY,
    OLFACTORY_VOLATILE_CONCENTRATION_QUANTITY, RECEPTOR_SATURATION_FRACTION_UNIT,
};
use crate::complete_neuron::{
    add_omitted_virgin_carrier_material, decode_neuron_physical_state,
    decode_sparse_physical_state_delta,
    encode_neuron_physical_state, encode_sparse_physical_state_delta,
    extend_neuron_positional_fabric, gate_opening_quantum_window_with_psi,
    gate_population_opening_schedule_with_psi, sparse_physical_state_delta,
    sparse_retained_physical_state_delta, DnaExpressionContact, ExactPhysicalStateDelta,
    ExactSignedDelta, GateWorkOccurrence, NeuronIntervalInput, NeuronPhysicalAnatomy,
    NeuronPhysicalState, PhysicalStateDeltaEntry, RecoveryContact, RecoveryLaneAddress,
    SparsePhysicalStateDelta,
};
use crate::declared_geometric_anatomy::{declared_neuron_territory, DeclaredNeuronPlace};
use crate::developmental_electrical_anatomy::{
    DevelopmentalElectricalError, DevelopmentalElectricalSeed,
};
use crate::developmental_resting_population::{
    DevelopmentalRestingPopulation, DevelopmentalRestingPopulationError, MaterializedRestingNeuron,
};
use crate::elementary_charge_membrane::{settle_membrane_elementary_charges, MembraneChargeError};
use crate::exact_rational::ExactRational;
use crate::hippocampal_sparse_path::{HippocampalError, ResidentHippocampalIndex};
use crate::joint_source_episode::NativeJointSourceEpisode;
#[cfg(test)]
use crate::joint_uf_neuron_boundary::prepare_complete_joint_field_admitted_fixture;
use crate::joint_uf_neuron_boundary::{
    bind_neuron_perspective, prepare_complete_joint_field_from_evaluated,
    prepare_complete_joint_field_with_admission, required_mathloom_positions,
    JointNeuronBoundaryError,
};
#[cfg(test)]
use crate::joint_uf_source_adapter::admitted_fixture_episode;
use crate::joint_uf_source_adapter::EvaluatedJointSourceOccurrence;
use crate::joint_uf_source_adapter::{AdmittedJointSourceEpisode, JointUfSourceError};
use crate::joint_uf_v1_4::{
    self, JointIntersampleLaw, JointUfCoordinateBounds, JointUfInput, JointUfPhysicalBounds,
};
use crate::metabolic_feeding::MetabolicError;
use crate::neuron_source_anchor::{
    bind_neuron_source_anchor, NeuronSourceSite, PhysicalSourceSense,
};
use crate::optical_receptor_work::{
    derive_optical_receptor_sample_range_work, quantize_optical_delivery, OpticalReceptorAnatomy,
    OpticalReceptorWorkError, RETINAL_REFERENCE_IRRADIANCE_UNIT,
    RETINAL_SPECTRAL_IRRADIANCE_QUANTITY,
};
use crate::physical_mosaic::{
    admit_physical_mosaic, admit_physical_mosaic_original, alter_physical_mosaic_recurrence,
    alter_physical_mosaic_recurrence_with_origin, connected_members,
    decode_admitted_physical_mosaic_for_topology, encode_admitted_physical_mosaic_for_topology,
    prove_physical_mosaic_recurrence, prove_physical_mosaic_recurrence_with_origin,
    AdmittedPhysicalMosaic, PhysicalMosaicCodecError, PhysicalMosaicError,
    PhysicalMosaicRecurrenceOrigin, StablePhysicalBondReference,
};
use crate::proprioceptive_receptor_work::{
    derive_proprioceptive_receptor_sample_range_work, quantize_proprioceptive_delivery,
    ProprioceptiveReceptorAnatomy, ProprioceptiveReceptorWorkError,
    ANTAGONIST_PROPRIOCEPTOR_LENGTH_QUANTITY, ARTICULATED_AXIS_SPAN_FRACTION_UNIT,
};
use crate::reached_neuron_cohort::{
    add_omitted_geometry_carrier_material, decode_reached_cohort_cell, decode_reached_cohort_state,
    decode_reached_cohort_state_delta, encode_reached_cohort_cell, encode_reached_cohort_cell_v5,
    encode_reached_cohort_cell_v5_with_contact_plasticity, encode_reached_cohort_cell_v6,
    encode_reached_cohort_state, encode_reached_cohort_state_delta,
    encode_reached_cohort_state_delta_v1, encode_reached_cohort_state_delta_v2,
    encode_reached_cohort_state_v4, encode_reached_cohort_state_v5,
    encode_reached_cohort_state_v6,
    expand_legacy_receptor_channel_populations as expand_reached_receptor_channel_populations,
    extend_reached_cohort_cells, extend_reached_cohort_contacts,
    extend_reached_cohort_positional_fabrics, extend_reached_cohort_state_with_genesis,
    legacy_receptor_channel_populations_require_expansion, reached_cohort_energy_state,
    reached_cohort_state_content_digest, reached_cohort_state_v4_content_digest,
    reached_cohort_state_v5_content_digest,
    settle_reached_cohort_dark_rest, settle_reached_cohort_interval,
    settle_reached_cohort_membrane_pumps, settle_contact_modulated_gate_energy,
    widen_reached_cohort_state_contacts, LocalizedFluidChemistrySettlement,
    ReachedCohortAnatomy, ReachedCohortEnergyState, ReachedCohortError,
    ReachedCohortIntervalInput, ReachedCohortMetabolicObservation,
    ReachedCohortPostExperienceSettlement, ReachedCohortRecurrenceSettlement,
    ReachedCohortState, ReachedNeuronGenesisCell, ReachedNeuronMount,
};
use crate::receptor_quantum_delivery::{
    big_to_exact_rational, exact_rational_to_big, quantize_population_receptor_delivery,
    quantize_receptor_delivery, ReceptorDeliveryError,
};
use crate::resident_electrical_fabric::ResidentElectricalFabric;
use crate::resident_receptor_transition::ResidentVestibularIngress;
use crate::sha256::sha256;
use crate::sparse_electrical_contact::{
    settle_contact_local_conductance, settle_sparse_electrical_transfers,
    ElectricalContactAnatomy, ElectricalContactState, ElectricalContactTransition,
    LocalGradientDirection, SparseElectricalAnatomy, SparseElectricalError,
    SparseElectricalState, SparseElectricalTransferSettlement,
};
use crate::tactile_receptor_work::{
    derive_tactile_receptor_sample_range_work, derive_tactile_receptor_work,
    quantize_tactile_delivery, TactileReceptorAnatomy, TactileReceptorWorkError,
    CONTACT_REFERENCE_OCCUPANCY_UNIT, CONTACT_SITE_OCCUPANCY_QUANTITY,
};
use crate::thermal_receptor_work::{
    derive_thermal_receptor_sample_range_work, quantize_thermal_delivery,
    ThermalReceptorAnatomy, ThermalReceptorWorkError,
    THERMORECEPTOR_REFERENCE_INTERVAL_UNIT, THERMORECEPTOR_TEMPERATURE_QUANTITY,
};
use crate::vestibular_neuron_path::{
    create_single_vertex_vestibular_reached_cohort,
    specialize_single_vertex_vestibular_reached_cohort, FunctionalVestibularError,
};
use crate::virtual_material_neuron_genesis::{
    create_quiescent_virtual_material_neuron, create_single_terminal_virtual_material_neuron,
    create_virtual_material_neuron, definitive_virtual_carriers_per_compartment,
    reach_quiescent_single_terminal_virtual_material_neuron,
    reach_quiescent_virtual_material_neuron, VirtualMaterialGenesisError,
};
use crate::virtual_articulated_body::{
    BodyEffectorTerminal, BODY_EFFECTOR_TERMINAL_COUNT, BODY_PROPRIOCEPTOR_TOPOLOGY_OFFSET,
};
use crate::virtual_vestibular_canal::WORLD_MECHANICAL_TICK_MICROSECONDS;
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{ToPrimitive, Zero};
use rayon::prelude::*;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::fmt;
use std::sync::Arc;

const MAGIC: &[u8; 8] = b"GLCOG012";
const VERSION: u16 = 12;
const MAGIC_V13: &[u8; 8] = b"GLCOG013";
const VERSION_V13: u16 = 13;
const MAGIC_V14: &[u8; 8] = b"GLCOG014";
const VERSION_V14: u16 = 14;
const MAGIC_V15: &[u8; 8] = b"GLCOG015";
const VERSION_V15: u16 = 15;
const MAGIC_V16: &[u8; 8] = b"GLCOG016";
const VERSION_V16: u16 = 16;
const MAGIC_V17: &[u8; 8] = b"GLCOG017";
const VERSION_V17: u16 = 17;
const MAGIC_V18: &[u8; 8] = b"GLCOG018";
const VERSION_V18: u16 = 18;
const MAGIC_V19: &[u8; 8] = b"GLCOG019";
const VERSION_V19: u16 = 19;
const MAGIC_V20: &[u8; 8] = b"GLCOG020";
const VERSION_V20: u16 = 20;
const MAGIC_V21: &[u8; 8] = b"GLCOG021";
const VERSION_V21: u16 = 21;
const MAGIC_V22: &[u8; 8] = b"GLCOG022";
const VERSION_V22: u16 = 22;
const MAGIC_V23: &[u8; 8] = b"GLCOG023";
const VERSION_V23: u16 = 23;
const LINEAGE_DOMAIN: &[u8; 8] = b"GLNLINE1";
/// Existing authored developmental-contact material shared by the retinal,
/// cochlear, tactile, and growth-DNA paths.  Internal specialization reuses
/// that exact physical contact; it is not a fitted learning coefficient.
const DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS: i128 = 500;
/// The pre-proprioceptive served receptor roster's widest declared local
/// projection is sound layer 1, topology 33. Its Cantor territory is 629, so
/// indices 0..628 remain the unchanged projection geography and the 74 fixed
/// antagonist terminals occupy the next bounded, disjoint layer-6 interval.
const PRE_PROPRIOCEPTIVE_WIDEST_SENSE_LAYER: u32 = 1;
const PRE_PROPRIOCEPTIVE_WIDEST_TOPOLOGY_INDEX: u32 = 33;
const BODY_PROPRIOCEPTOR_LAYER6_TOPOLOGY_OFFSET: u32 = {
    let eccentricity =
        PRE_PROPRIOCEPTIVE_WIDEST_SENSE_LAYER + PRE_PROPRIOCEPTIVE_WIDEST_TOPOLOGY_INDEX;
    eccentricity * (eccentricity + 1) / 2 + PRE_PROPRIOCEPTIVE_WIDEST_TOPOLOGY_INDEX + 1
};
/// Body regulation is its own layer-8 geography. Before proprioception, its
/// widest body receptor is layer 5, topology 9, whose local projection is 114.
/// The fixed antagonist terminals therefore occupy the next disjoint layer-8
/// interval rather than copying their much wider layer-6 coordinates.
const PRE_PROPRIOCEPTIVE_WIDEST_BODY_TOPOLOGY_INDEX: u32 = 9;
const PRE_PROPRIOCEPTIVE_BODY_SENSE_LAYER: u32 = 5;
const BODY_PROPRIOCEPTOR_LAYER8_TOPOLOGY_OFFSET: u32 = {
    let eccentricity =
        PRE_PROPRIOCEPTIVE_BODY_SENSE_LAYER + PRE_PROPRIOCEPTIVE_WIDEST_BODY_TOPOLOGY_INDEX;
    eccentricity * (eccentricity + 1) / 2 + PRE_PROPRIOCEPTIVE_WIDEST_BODY_TOPOLOGY_INDEX + 1
};
const HIPPOCAMPAL_CHECKPOINT_BYTES: usize = 8 + 33 + 33;
const FIXED_BYTES: usize = MAGIC.len()
    + std::mem::size_of::<u16>()
    + 8
    + 8
    + 8
    + 8
    + 8
    + 8
    + 8
    + HIPPOCAMPAL_CHECKPOINT_BYTES;
const CURRENT_FIXED_BYTES: usize = FIXED_BYTES + (5 * std::mem::size_of::<u64>());
const EXPERIENCE_MAGIC: &[u8; 8] = b"GLEXP01\0";
const EXPERIENCE_V2_MAGIC: &[u8; 8] = b"GLEXP02\0";
const EXPERIENCE_V3_MAGIC: &[u8; 8] = b"GLEXP03\0";
const EXPERIENCE_V4_MAGIC: &[u8; 8] = b"GLEXP04\0";
const EXPERIENCE_V5_MAGIC: &[u8; 8] = b"GLEXP05\0";
const EXPERIENCE_V6_MAGIC: &[u8; 8] = b"GLEXP06\0";
const EXPERIENCE_V7_MAGIC: &[u8; 8] = b"GLEXP07\0";
const RECURRENCE_MAGIC: &[u8; 8] = b"GLREC02\0";
const ENDOGENOUS_RECURRENCE_MAGIC: &[u8; 8] = b"GLREC03\0";
const PHYSICAL_RECURRENCE_MAGIC: &[u8; 8] = b"GLREC04\0";
const ENDOGENOUS_PHYSICAL_RECURRENCE_MAGIC: &[u8; 8] = b"GLREC05\0";
const EXCITATION_RECURRENCE_MAGIC: &[u8; 8] = b"GLREC06\0";
const ENDOGENOUS_EXCITATION_RECURRENCE_MAGIC: &[u8; 8] = b"GLREC07\0";
/// Wrapper magic for a retained mosaic reference that carries nonzero
/// reinforcement/relation counts (memory law R3, ratified 2026-08-06).
/// Codec precedent GLEXP02→GLEXP03: the wrapper appears ONLY when the new
/// state differs from the historical default (both counts zero), so every
/// pre-law body and every zero-count reference keeps a byte-identical
/// receipt.
const RETAINED_MOSAIC_COUNTS_MAGIC: &[u8; 8] = b"GLMRC01\0";
/// Current retained-mosaic wrapper. It preserves the already-grown layer-9
/// recurrent cell as the exact member-contact authority; later lawful
/// downstream contacts cannot make a broader formation impersonate it.
const RETAINED_MOSAIC_RECURRENT_MAGIC: &[u8; 8] = b"GLMRC02\0";
const EVIDENCE_DIGEST_BYTES: usize = 32;

/// Which persisted cognitive-image layout a body carries. Historical layouts
/// remain readable at the explicit one-way migration boundary. Every ordinary
/// encode emits the current format; V19 added the compact recipient-only
/// electrical frontier. V20 retains the exact one-interval bond and whole-
/// carrier cause of each recipient so later propagation can preserve physical
/// order without an episode history. V21 retains the immediately preceding
/// sparse frontier as well. V22 retains one further sparse frontier so an
/// earlier and a current two-contact path can physically recur without
/// retaining an episode sequence. V23 preserves which physically changed
/// endpoint advances the causal wave independently of carrier-flow direction.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum CognitiveCodecFormat {
    V12,
    V13,
    V14,
    V15,
    V16,
    V17,
    V18,
    V19,
    V20,
    V21,
    V22,
    V23,
}

#[cfg(test)]
std::thread_local! {
    static RESIDENT_ACTUAL_RECURRENCE_SETTLEMENTS: std::cell::Cell<usize> = const {
        std::cell::Cell::new(0)
    };
    static RESIDENT_JOINT_FIELD_EVALUATIONS: std::cell::Cell<usize> = const {
        std::cell::Cell::new(0)
    };
}

#[cfg(test)]
pub(crate) fn reset_resident_joint_field_evaluation_count() {
    RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| count.set(0));
}

#[cfg(test)]
pub(crate) fn resident_joint_field_evaluation_count() -> usize {
    RESIDENT_JOINT_FIELD_EVALUATIONS.with(std::cell::Cell::get)
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct OrganicMosaicRelationObservation {
    /// Canonical receipts of the retained formations related by this one
    /// current physical frontier. Receipts identify observation evidence;
    /// they do not cause or persist the relationship.
    pub(crate) formation_receipts: Vec<[u8; 32]>,
    pub(crate) shared_lineages: Vec<[u8; 16]>,
    pub(crate) active_bonds: Vec<StablePhysicalBondReference>,
    /// Stable physical identity of the related retained member sets, shared
    /// lineages, and active bonds. Unlike formation receipts, this does not
    /// include the changing latest-recurrence witness.
    pub(crate) structural_relation_receipt: [u8; 32],
    /// Exact two-contact continuations completed across adjacent physical
    /// intervals and spanning at least two formations in this relation. These
    /// are transient observer evidence; they are neither retained formations
    /// nor transition authority.
    pub(crate) ordered_physical_paths: Vec<OrderedPhysicalPathObservation>,
    /// Exact earlier/current two-contact path recurrences spanning this
    /// recurrent relation. This is bounded immediate propagation evidence,
    /// never a retained thought or sequence object.
    pub(crate) ordered_path_relations: Vec<OrderedPathRelationObservation>,
}

/// The exact cause retained across one electrical propagation boundary.
/// Historical V19 bodies know only the receiver and therefore carry `None`;
/// such an entry may continue ordinary propagation but can never prove order.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct ActiveElectricalFrontierEntry {
    receiver: [u8; 16],
    cause: Option<DirectedElectricalFrontierCause>,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct DirectedElectricalFrontierCause {
    bond: StablePhysicalBondReference,
    transferred_whole_carriers: u128,
    frontier_is_sender: bool,
}

impl ActiveElectricalFrontierEntry {
    fn legacy_receiver(receiver: [u8; 16]) -> Self {
        Self {
            receiver,
            cause: None,
        }
    }

    fn caused(
        sender: [u8; 16],
        receiver: [u8; 16],
        bond: StablePhysicalBondReference,
        transferred_whole_carriers: u128,
    ) -> Result<Self, FormationError> {
        let (left, right) = bond.endpoints();
        if transferred_whole_carriers == 0
            || !((sender == left && receiver == right) || (sender == right && receiver == left))
        {
            return Err(FormationError::NoncanonicalState);
        }
        Ok(Self {
            receiver,
            cause: Some(DirectedElectricalFrontierCause {
                bond,
                transferred_whole_carriers,
                frontier_is_sender: false,
            }),
        })
    }

    fn caused_with_frontier(
        sender: [u8; 16],
        receiver: [u8; 16],
        frontier: [u8; 16],
        bond: StablePhysicalBondReference,
        transferred_whole_carriers: u128,
    ) -> Result<Self, FormationError> {
        let mut entry = Self::caused(sender, receiver, bond, transferred_whole_carriers)?;
        let cause = entry
            .cause
            .as_mut()
            .ok_or(FormationError::NoncanonicalState)?;
        cause.frontier_is_sender = if frontier == sender {
            true
        } else if frontier == receiver {
            false
        } else {
            return Err(FormationError::NoncanonicalState);
        };
        Ok(entry)
    }

    fn receiver(self) -> [u8; 16] {
        self.receiver
    }

    fn sender(self) -> Option<[u8; 16]> {
        let cause = self.cause?;
        let (left, right) = cause.bond.endpoints();
        if self.receiver == left {
            Some(right)
        } else if self.receiver == right {
            Some(left)
        } else {
            None
        }
    }

    fn frontier_lineage(self) -> [u8; 16] {
        self.cause
            .filter(|cause| cause.frontier_is_sender)
            .and_then(|_| self.sender())
            .unwrap_or(self.receiver)
    }

    fn affected_lineages(self) -> [Option<[u8; 16]>; 2] {
        [Some(self.frontier_lineage()), None]
    }

    fn directed_transfer(self) -> Option<DirectedPhysicalTransferObservation> {
        let cause = self.cause?;
        Some(DirectedPhysicalTransferObservation {
            sender: self.sender()?,
            receiver: self.receiver,
            bond: cause.bond,
            transferred_whole_carriers: cause.transferred_whole_carriers,
        })
    }

    fn encoded_v20_len(self) -> usize {
        1 + 16
            + if self.cause.is_some() {
                16 + 16 + 4 + 16
            } else {
                0
            }
    }

    fn encode_v20(self, output: &mut Vec<u8>) {
        output.push(match self.cause {
            None => 0,
            Some(cause) if cause.frontier_is_sender => 2,
            Some(_) => 1,
        });
        output.extend_from_slice(&self.receiver);
        if let Some(cause) = self.cause {
            let (left, right) = cause.bond.endpoints();
            output.extend_from_slice(&left);
            output.extend_from_slice(&right);
            output.extend_from_slice(&cause.bond.parallel_ordinal().to_le_bytes());
            output.extend_from_slice(&cause.transferred_whole_carriers.to_le_bytes());
        }
    }

    fn decode_v20(
        bytes: &[u8],
        cursor: &mut usize,
        allow_sender_frontier: bool,
    ) -> Result<Self, FormationError> {
        let tag = *bytes
            .get(*cursor)
            .ok_or(FormationError::NoncanonicalState)?;
        *cursor = cursor
            .checked_add(1)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let receiver_end = cursor
            .checked_add(16)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let receiver = bytes
            .get(*cursor..receiver_end)
            .ok_or(FormationError::NoncanonicalState)?
            .try_into()
            .map_err(|_| FormationError::NoncanonicalState)?;
        *cursor = receiver_end;
        match tag {
            0 => Ok(Self::legacy_receiver(receiver)),
            1 | 2 if tag == 1 || allow_sender_frontier => {
                let left_end = cursor
                    .checked_add(16)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let left = bytes
                    .get(*cursor..left_end)
                    .ok_or(FormationError::NoncanonicalState)?
                    .try_into()
                    .map_err(|_| FormationError::NoncanonicalState)?;
                *cursor = left_end;
                let right_end = cursor
                    .checked_add(16)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let right = bytes
                    .get(*cursor..right_end)
                    .ok_or(FormationError::NoncanonicalState)?
                    .try_into()
                    .map_err(|_| FormationError::NoncanonicalState)?;
                *cursor = right_end;
                let ordinal_end = cursor
                    .checked_add(4)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let parallel_ordinal = u32::from_le_bytes(
                    bytes
                        .get(*cursor..ordinal_end)
                        .ok_or(FormationError::NoncanonicalState)?
                        .try_into()
                        .map_err(|_| FormationError::NoncanonicalState)?,
                );
                *cursor = ordinal_end;
                let carrier_end = cursor
                    .checked_add(16)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let transferred_whole_carriers = u128::from_le_bytes(
                    bytes
                        .get(*cursor..carrier_end)
                        .ok_or(FormationError::NoncanonicalState)?
                        .try_into()
                        .map_err(|_| FormationError::NoncanonicalState)?,
                );
                *cursor = carrier_end;
                let bond = StablePhysicalBondReference::new(left, right, parallel_ordinal)
                    .ok_or(FormationError::NoncanonicalState)?;
                let sender = if receiver == left {
                    right
                } else if receiver == right {
                    left
                } else {
                    return Err(FormationError::NoncanonicalState);
                };
                let mut entry = Self::caused(sender, receiver, bond, transferred_whole_carriers)?;
                entry
                    .cause
                    .as_mut()
                    .ok_or(FormationError::NoncanonicalState)?
                    .frontier_is_sender = tag == 2;
                Ok(entry)
            }
            _ => Err(FormationError::NoncanonicalState),
        }
    }
}

fn encoded_directed_frontier_len(frontier: &[ActiveElectricalFrontierEntry]) -> Option<usize> {
    frontier.iter().try_fold(8usize, |total, entry| {
        total.checked_add(entry.encoded_v20_len())
    })
}

fn encode_directed_frontier(
    frontier: &[ActiveElectricalFrontierEntry],
    output: &mut Vec<u8>,
) -> Result<(), FormationError> {
    push_length(output, frontier.len())?;
    for entry in frontier {
        entry.encode_v20(output);
    }
    Ok(())
}

fn decode_directed_frontier(
    bytes: &[u8],
    cursor: &mut usize,
    allow_sender_frontier: bool,
) -> Result<Vec<ActiveElectricalFrontierEntry>, FormationError> {
    let count = read_length(bytes, cursor)?;
    if count > bytes.len().saturating_sub(*cursor) / 17 {
        return Err(FormationError::NoncanonicalState);
    }
    let mut frontier = Vec::new();
    frontier
        .try_reserve_exact(count)
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    for _ in 0..count {
        frontier.push(ActiveElectricalFrontierEntry::decode_v20(
            bytes,
            cursor,
            allow_sender_frontier,
        )?);
    }
    Ok(frontier)
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub(crate) struct OrderedPhysicalPathObservation {
    first: DirectedPhysicalTransferObservation,
    second: DirectedPhysicalTransferObservation,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub(crate) struct OrderedPathRelationObservation {
    earlier_first: DirectedPhysicalTransferObservation,
    earlier_second: DirectedPhysicalTransferObservation,
    current_first: DirectedPhysicalTransferObservation,
    current_second: DirectedPhysicalTransferObservation,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub(crate) struct DirectedPhysicalTransferObservation {
    pub(crate) sender: [u8; 16],
    pub(crate) receiver: [u8; 16],
    pub(crate) bond: StablePhysicalBondReference,
    pub(crate) transferred_whole_carriers: u128,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct CausalFrontierTransferObservation {
    pub(crate) transfer: DirectedPhysicalTransferObservation,
    pub(crate) frontier_lineage: [u8; 16],
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct InternallyReassembledFormationCueObservation {
    pub(crate) formation_receipt: [u8; 32],
    pub(crate) cue_lineages: Vec<[u8; 16]>,
    /// The already-mounted layer-9 cell physically connected to every member
    /// of this formation. This is reconstructed from contact topology on cold
    /// restore and is never a separately encoded authority.
    recurrent_lineage: Option<[u8; 16]>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct ExternallyReassembledFormationFrontierObservation {
    pub(crate) formation_receipt: [u8; 32],
    pub(crate) cue_lineages: Vec<[u8; 16]>,
    pub(crate) recurrent_lineage: [u8; 16],
}

/// One exact directed contact transfer at one native cognitive ordinal. The
/// ordinal preserves causal order for bounded read-only trajectory evidence;
/// it is not a persisted episode, score, or clock-driven decision.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub(crate) struct TimedDirectedPhysicalTransferObservation {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) transfer: DirectedPhysicalTransferObservation,
}

/// One reached sparse contact whose retained channel constitution changed in
/// this exact interval. This is transient observation only: the authoritative
/// successor remains the contact state already stored in the organism.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct ChangedContactChannelStateObservation {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) bond: StablePhysicalBondReference,
    pub(crate) predecessor_conducting_channel_population: u128,
    pub(crate) predecessor_transition_work_phase: ExactRational,
    pub(crate) predecessor_effective_conductance_picosiemens: ExactRational,
    pub(crate) successor_conducting_channel_population: u128,
    pub(crate) successor_transition_work_phase: ExactRational,
    pub(crate) successor_effective_conductance_picosiemens: ExactRational,
}

/// One exact local membrane-gradient settlement for a reached layer-10 cell.
/// Every quantity comes from the cell's already-mounted one-neuron recovery
/// compartment. This is transient physical evidence, not a named emotion or
/// a scalar measure of affect.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct LocalAffectiveGradientSettlementObservation {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) predecessor_separated_elementary_charges: i128,
    pub(crate) post_gradient_separated_elementary_charges: i128,
    pub(crate) interval_successor_separated_elementary_charges: i128,
    pub(crate) returned_elementary_charges: i128,
    pub(crate) pumped_elementary_charges: i128,
    pub(crate) unreturned_elementary_charges: i128,
    pub(crate) membrane_gradient_work_zeptojoules: ExactRational,
    pub(crate) environment_energy_delivered_zeptojoules: ExactRational,
    pub(crate) environment_heat_exported_zeptojoules: ExactRational,
}

/// One exact pathway-local physiological modulation. Incident whole carriers
/// provide catalyst to the already-mounted gate fluid contact; the finite
/// recovery reservoir supplies the energy; the ordinary gate and plastic
/// return map decide whether anything is retained. This is neither reward nor
/// named chemistry.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct LocalAffectivePlasticitySettlementObservation {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) incident_catalyst_quanta: u128,
    pub(crate) reaction_extent: u128,
    pub(crate) delivered_energy_zeptojoules: ExactRational,
    pub(crate) predecessor_gate_work_residue_zeptojoules: ExactRational,
    pub(crate) successor_gate_work_residue_zeptojoules: ExactRational,
    pub(crate) predecessor_plastic_rest_length_nanometres: ExactRational,
    pub(crate) successor_plastic_rest_length_nanometres: ExactRational,
    pub(crate) predecessor_reservoir: (ExactRational, ExactRational, ExactRational),
    pub(crate) successor_reservoir: (ExactRational, ExactRational, ExactRational),
}

/// A bounded read-only trajectory witness for one physical layer-10 cell.
/// Association, body, and local recovery facts may arrive in different
/// causal intervals and are merged only by the same stable lineage outside
/// organism state. Missing facts remain absent rather than being inferred.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AffectiveBalanceTrajectoryObservation {
    pub(crate) neuron_lineage: [u8; 16],
    pub(crate) neuron_place: DeclaredNeuronPlace,
    pub(crate) association_influence: Option<TimedDirectedPhysicalTransferObservation>,
    pub(crate) body_influence: Option<TimedDirectedPhysicalTransferObservation>,
    pub(crate) localized_gradient_settlement: Option<LocalAffectiveGradientSettlementObservation>,
    pub(crate) localized_plasticity_settlement:
        Option<LocalAffectivePlasticitySettlementObservation>,
}

/// One exact local recovery-fluid/membrane settlement mapped back to its
/// stable resident neuron. The record is transient observation only; all
/// causative state remains in the ordinary neuron and cohort reservoir.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct LocalizedFluidChemistryObservation {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) neuron_lineage: [u8; 16],
    pub(crate) neuron_place: DeclaredNeuronPlace,
    pub(crate) interval_microseconds: u32,
    pub(crate) pump_contact_power_zeptojoules_per_microsecond: ExactRational,
    pub(crate) reached_neuron_count: usize,
    pub(crate) changed_reached_neuron_count: usize,
    pub(crate) unchanged_unreached_neuron_count: usize,
    pub(crate) unchanged_developmental_resting_neuron_count: usize,
    pub(crate) changed_unreached_neuron_count: usize,
    pub(crate) predecessor_separated_elementary_charges: i128,
    pub(crate) successor_separated_elementary_charges: i128,
    pub(crate) predecessor_intracellular_carriers: u128,
    pub(crate) predecessor_extracellular_carriers: u128,
    pub(crate) successor_intracellular_carriers: u128,
    pub(crate) successor_extracellular_carriers: u128,
    pub(crate) predecessor_reservoir: (ExactRational, ExactRational, ExactRational),
    pub(crate) successor_reservoir: (ExactRational, ExactRational, ExactRational),
    pub(crate) returned_elementary_charges: i128,
    pub(crate) pumped_elementary_charges: i128,
    pub(crate) membrane_gradient_work_zeptojoules: ExactRational,
}

/// The exact retained dissipation of one locally evaluated body-receptor
/// neuron after its ordinary physical interval.  The three lane families stay
/// separate: this is not a strain score, pain label, or action authority.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct LocalizedMetabolicStrainObservation {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) neuron_lineage: [u8; 16],
    pub(crate) neuron_place: DeclaredNeuronPlace,
    pub(crate) psi_dissipation_quanta: Box<[u128]>,
    pub(crate) gate_dissipation_quanta: u128,
    pub(crate) plastic_dissipation_quanta: u128,
}

fn retain_latest_localized_metabolic_strain(
    evaluated_lineages: &mut Vec<[u8; 16]>,
    retained: &mut Vec<LocalizedMetabolicStrainObservation>,
    cognitive_ordinal: u64,
    neuron_lineage: [u8; 16],
    neuron_place: DeclaredNeuronPlace,
    neuron: &NeuronPhysicalState,
) -> Result<(), FormationError> {
    if !evaluated_lineages.contains(&neuron_lineage) {
        evaluated_lineages.push(neuron_lineage);
    }
    retained.retain(|entry| entry.neuron_lineage != neuron_lineage);
    let psi_dissipation_quanta = neuron
        .psi_state()
        .rings()
        .iter()
        .map(|ring| ring.dissipated_quanta())
        .collect::<Vec<_>>();
    let gate_dissipation_quanta = neuron
        .lane_dissipated_quanta(RecoveryLaneAddress::Gate)
        .ok_or(FormationError::NoncanonicalState)?;
    let plastic_dissipation_quanta = neuron
        .lane_dissipated_quanta(RecoveryLaneAddress::Plastic)
        .ok_or(FormationError::NoncanonicalState)?;
    if gate_dissipation_quanta != 0
        || plastic_dissipation_quanta != 0
        || psi_dissipation_quanta.iter().any(|value| *value != 0)
    {
        retained.push(LocalizedMetabolicStrainObservation {
            cognitive_ordinal,
            neuron_lineage,
            neuron_place,
            psi_dissipation_quanta: psi_dissipation_quanta.into_boxed_slice(),
            gate_dissipation_quanta,
            plastic_dissipation_quanta,
        });
    }
    evaluated_lineages.sort_unstable();
    retained.sort_unstable_by_key(|entry| entry.neuron_lineage);
    Ok(())
}

impl OrderedPhysicalPathObservation {
    pub(crate) fn directed_transfers(
        &self,
    ) -> [([u8; 16], [u8; 16], StablePhysicalBondReference, u128); 2] {
        let project = |transfer: DirectedPhysicalTransferObservation| {
            (
                transfer.sender,
                transfer.receiver,
                transfer.bond,
                transfer.transferred_whole_carriers,
            )
        };
        [project(self.first), project(self.second)]
    }

    fn same_directed_route(&self, other: &Self) -> bool {
        self.first.sender == other.first.sender
            && self.first.receiver == other.first.receiver
            && self.first.bond == other.first.bond
            && self.second.sender == other.second.sender
            && self.second.receiver == other.second.receiver
            && self.second.bond == other.second.bond
    }
}

impl OrderedPathRelationObservation {
    pub(crate) fn directed_transfers(
        &self,
    ) -> [([u8; 16], [u8; 16], StablePhysicalBondReference, u128); 4] {
        let project = |transfer: DirectedPhysicalTransferObservation| {
            (
                transfer.sender,
                transfer.receiver,
                transfer.bond,
                transfer.transferred_whole_carriers,
            )
        };
        [
            project(self.earlier_first),
            project(self.earlier_second),
            project(self.current_first),
            project(self.current_second),
        ]
    }
}

/// One mounted branch available to the current exact physical seed frontier.
/// The signed transfer is measured outward from `seed_lineage`: positive
/// means the adjacent neuron received whole carriers, zero means the mounted
/// branch was physically available but did not advance a whole carrier, and
/// negative means the branch carried material toward the seed. This is a
/// bounded transient witness, never retained cognition or a selection score.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct PhysicalFrontierRouteObservation {
    seed_lineage: [u8; 16],
    seed_place: DeclaredNeuronPlace,
    adjacent_lineage: [u8; 16],
    adjacent_place: DeclaredNeuronPlace,
    bond: StablePhysicalBondReference,
    outward_whole_carriers_from_seed: i128,
}

pub(crate) fn has_reached_and_foregone_frontier_routes(
    routes: &[PhysicalFrontierRouteObservation],
) -> bool {
    routes.len() > 1
        && routes
            .iter()
            .any(|route| route.outward_whole_carriers_from_seed() == 0)
        && routes
            .iter()
            .any(|route| route.outward_whole_carriers_from_seed() != 0)
}

impl PhysicalFrontierRouteObservation {
    pub(crate) fn seed_lineage(self) -> [u8; 16] {
        self.seed_lineage
    }

    pub(crate) fn seed_place(self) -> DeclaredNeuronPlace {
        self.seed_place
    }

    /// Return the exact sender only when this available branch carried a
    /// nonzero whole-carrier transfer. The sign is measured outward from the
    /// declared seed, so a negative route was sent by the adjacent neuron.
    pub(crate) fn directed_sender(self) -> Option<[u8; 16]> {
        match self.outward_whole_carriers_from_seed.cmp(&0) {
            std::cmp::Ordering::Greater => Some(self.seed_lineage),
            std::cmp::Ordering::Less => Some(self.adjacent_lineage),
            std::cmp::Ordering::Equal => None,
        }
    }

    pub(crate) fn adjacent_lineage(self) -> [u8; 16] {
        self.adjacent_lineage
    }

    pub(crate) fn adjacent_place(self) -> DeclaredNeuronPlace {
        self.adjacent_place
    }

    pub(crate) fn bond(self) -> StablePhysicalBondReference {
        self.bond
    }

    pub(crate) fn outward_whole_carriers_from_seed(self) -> i128 {
        self.outward_whole_carriers_from_seed
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct CognitiveFormationObservation {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) trace_formed: bool,
    pub(crate) mosaic_formed: Option<[u8; 32]>,
    pub(crate) activations: Vec<FormationActivation>,
    pub(crate) trace_count: usize,
    pub(crate) mosaic_count: usize,
    pub(crate) dsf_delivery_count: usize,
    pub(crate) complete_neuron_count: usize,
    /// Declared source-independent cells that remain at exact quiescent rest.
    /// They did not receive the current field and are not included in
    /// `complete_neuron_count`.
    pub(crate) resting_neuron_count: usize,
    pub(crate) physically_transitioned_neuron_count: usize,
    /// Receptor cells on the body projection whose own exact local source
    /// delivered nonzero gate work in this transition. Observation only.
    pub(crate) externally_perturbed_body_receptor_count: usize,
    /// Exact receptor lineages whose own local source delivered nonzero gate
    /// work in this transition. This is transient observation only; the
    /// lineages already exist in the retained organism and this projection
    /// creates no second state authority.
    pub(crate) externally_perturbed_neuron_lineages: Vec<[u8; 16]>,
    /// Reached layer-5 body receptors whose separated membrane charge changed
    /// during this transition's exact local recovery-fluid settlement. This
    /// is local causal evidence, never a projection of body-wide ledgers.
    pub(crate) metabolically_perturbed_body_receptor_count: usize,
    pub(crate) complete_neuron_fractal_count: usize,
    pub(crate) emitted_neuron_fractals: Vec<EmittedNeuronFractal>,
    pub(crate) active_physical_bonds: Vec<StablePhysicalBondReference>,
    pub(crate) changed_contact_channel_states: Vec<ChangedContactChannelStateObservation>,
    pub(crate) physical_frontier_routes: Vec<PhysicalFrontierRouteObservation>,
    pub(crate) preceding_distinct_physical_frontier_routes: Vec<PhysicalFrontierRouteObservation>,
    /// First exact route set in this bounded transaction containing both a
    /// transported and a zero-whole-carrier mounted alternative. This is a
    /// transient observation witness, not retained state or selection logic.
    pub(crate) reached_and_foregone_physical_frontier_routes: Vec<PhysicalFrontierRouteObservation>,
    /// One exact adjacent-interval path whose intermediate neuron was reached
    /// only from the predecessor's retained whole-carrier frontier. This is a
    /// transient proof of immediate physical continuation, not retained
    /// working memory, a scenario, or an activity score.
    pub(crate) working_causal_continuations: Vec<OrderedPhysicalPathObservation>,
    /// One exact predecessor transfer whose receiving neuron sent no whole
    /// carrier onward in this interval. Its propagation authority therefore
    /// expired at this boundary. The neuron's ordinary physical state remains
    /// authoritative; this observation stores and changes nothing.
    pub(crate) settled_working_frontier: Vec<DirectedPhysicalTransferObservation>,
    /// Up to two exact internally continued alternatives sharing one reached
    /// intrinsic cause. Each path crosses an already-retained layer-11
    /// ordering cell and reaches a distinct layer-10 body/affective relation.
    /// This is bounded transient evidence, never a retained plan or score.
    pub(crate) physical_prediction_alternatives: Vec<OrderedPhysicalPathObservation>,
    /// One exact layer-8 to layer-10 transfer observed only while an authentic
    /// vestibular occurrence is being settled. It is the later body
    /// consequence against which prior alternatives can be compared; the
    /// comparison itself changes no organism state.
    pub(crate) body_consequence_transfers: Vec<DirectedPhysicalTransferObservation>,
    /// Bounded transient association/body/local-gradient trajectories for
    /// reached layer-10 cells. These records are observation only and never
    /// become emotion labels, scores, persisted histories, or settlement
    /// authority.
    pub(crate) affective_balance_trajectories: Vec<AffectiveBalanceTrajectoryObservation>,
    /// Exact per-target fluid/contact settlements from the already-reached
    /// sparse frontier. No cohort aggregate may substitute for these records.
    pub(crate) localized_fluid_chemistry: Vec<LocalizedFluidChemistryObservation>,
    /// Stable lineages of layer-5 source-site body receptors whose own local
    /// dissipation state was evaluated in this transition.  This remains
    /// separate from the sparse nonzero records so exact zero is distinguishable
    /// from an absent pathway without materializing a zero-state body.
    pub(crate) localized_metabolic_strain_evaluated_body_receptor_lineages:
        Vec<[u8; 16]>,
    /// Latest nonzero, lane-separated dissipation for the evaluated body
    /// receptors.  The causative state remains in each complete neuron.
    pub(crate) localized_metabolic_strain: Vec<LocalizedMetabolicStrainObservation>,
    /// Transient connected frontiers among recurrent mosaics physically
    /// reached by this transition, with at least one fully reassembled. No
    /// relation object, count, hierarchy, or history is retained in the
    /// organism.
    pub(crate) organic_mosaic_relations: Vec<OrganicMosaicRelationObservation>,
    pub(crate) motor_unit_recruitments: Vec<MotorUnitRecruitment>,
    pub(crate) articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
    pub(crate) partial_cue_reassembly_count: usize,
    pub(crate) endogenous_partial_cue_reassembly_count: usize,
    /// Exact cues for formations that physically reassembled from an internal
    /// cause in this transition. This is transient evidence only; it neither
    /// enters settlement nor becomes retained formation state.
    pub(crate) internally_reassembled_formation_cues:
        Vec<InternallyReassembledFormationCueObservation>,
    /// Exact externally cued retained formations whose own recurrent layer-9
    /// endpoint is the current advancing electrical frontier. This is the
    /// bounded physical bridge from recognition into possible later action;
    /// it is transient observation only and adds no charge or state.
    pub(crate) externally_reassembled_formation_frontiers:
        Vec<ExternallyReassembledFormationFrontierObservation>,
    /// Total mosaic-of-mosaics relation events recorded against the retained
    /// formations (memory law R1, overlap branch; self-ratified 2026-08-06 by the overnight session, NO filed instrument — flagged 2026-08-07, awaiting Joe's actual ruling):
    /// each recorded reassembly whose member set overlapped a retained
    /// formation without equalling it counts once per overlapped formation.
    /// Derived from the retained per-mosaic counts, never invented here.
    pub(crate) mosaic_of_mosaics_count: usize,
    /// Metabolic facts of this transition (minimal feeding metabolism,
    /// authorized 2026-08-05).  Every one of these is a settled physical
    /// quantity, including the demands the body could NOT meet: an exhausted
    /// ledger reports itself here instead of succeeding silently.
    pub(crate) rest_recovered_neuron_count: usize,
    pub(crate) rest_drained_dissipation_quanta: u128,
    pub(crate) unmet_dissipation_quanta: u128,
    pub(crate) membrane_returned_elementary_charges: i128,
    pub(crate) membrane_unreturned_elementary_charges: i128,
    pub(crate) metabolic_fuel_quanta: u128,
    pub(crate) nutrition_regenerated_fuel_quanta: u128,
    pub(crate) nutrition_unabsorbed_waste_quanta: u128,
    pub(crate) nutrition_vented_heat_quanta: u128,
    pub(crate) energy: ReachedCohortEnergyState,
}

impl CognitiveFormationObservation {
    pub(crate) fn partial_cue_reassembly_count(&self) -> usize {
        self.partial_cue_reassembly_count
    }

    pub(crate) fn endogenous_partial_cue_reassembly_count(&self) -> usize {
        self.endogenous_partial_cue_reassembly_count
    }
}

// THE DYNAMIC-FORMATION CLASSIFIER IS DELETED, NOT REPLACED.
//
// `observe_dynamic_formation` stood here.  It was the ONLY consumer of the
// hippocampal cold archive: per participating neuron it walked four archived
// postings, decoded each referenced episode's mosaic, and classified the
// current reassembly as a relation / tapestry / deeper tapestry / generative
// recombination.  With the archive retired it has no input, and it cannot be
// rebuilt from her body.  The reasons, stated rather than worked around:
//
//   * It is TEMPORAL and PER-PARTICIPANT.  It needed, for each member neuron,
//     the ORDERED last four episodes that neuron took part in, grouped by
//     depth, and it compared "how many participants have a k-th prior episode"
//     against the current participant count.  Her retained formations
//     (`mosaics`) are a DEDUPLICATED SET with no ordering and no per-neuron
//     history: under memory laws R1-R3 a re-derived formation replaces its
//     reference in place rather than appending, which is exactly why her
//     memory count stays flat.  No body fact means "the k-th prior episode of
//     neuron N", so no faithful reconstruction exists.
//   * Its tapestry, deeper-tapestry and generative outputs all turn on
//     `prior_current_occurrences` — occurrences of the CURRENT mosaic inside
//     that four-deep window.  The nearest body fact is R3's
//     `reinforcement_count`, which is an unbounded lifetime count, not a count
//     within a window.  Substituting it would silently redefine the law while
//     keeping its name.  That is fabrication and it is refused.
//
// MEASURED before deleting, so this is a removal of nothing rather than a
// removal of something: on her restored live body and on a fresh genesis every
// one of the eight counts read ZERO, and no surface anywhere read any of them
// (zero references outside this crate).  What remains truth-coupled is
// `mosaic_of_mosaics_count`, which is derived from her retained per-mosaic
// relation counts — a physical fact in her body — and is unaffected.
//
// The observation no longer carries the eight counts at all.  Reporting them
// as zero would be the step-fact-as-state lie: a reader takes "tapestry
// count 0" for a measurement, when the truth is that nothing measures it.

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct FormationActivation;

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct EmittedNeuronFractal {
    pub(crate) neuron_lineage: [u8; 16],
    pub(crate) delta: SparsePhysicalStateDelta,
}

/// One admitted organism transition may settle a receptor and its immediately
/// connected internal contact in sequence. If the same neuron reaches retained
/// rest at both boundaries, compose those exact changes into its one sparse
/// transition impression instead of exporting the lineage twice.
pub(crate) fn coalesce_emitted_neuron_fractals(
    mut emitted: Vec<EmittedNeuronFractal>,
) -> Result<Vec<EmittedNeuronFractal>, FormationError> {
    emitted.sort_unstable_by_key(|fractal| fractal.neuron_lineage);
    let mut coalesced = Vec::<EmittedNeuronFractal>::new();
    for fractal in emitted {
        let Some(prior) = coalesced.last_mut() else {
            coalesced.push(fractal);
            continue;
        };
        if prior.neuron_lineage != fractal.neuron_lineage {
            coalesced.push(fractal);
            continue;
        }
        match compose_retained_deltas(&prior.delta, &fractal.delta)? {
            Some(delta) => prior.delta = delta,
            None => {
                coalesced.pop();
            }
        }
    }
    Ok(coalesced)
}

fn compose_retained_deltas(
    first: &SparsePhysicalStateDelta,
    second: &SparsePhysicalStateDelta,
) -> Result<Option<SparsePhysicalStateDelta>, FormationError> {
    let mut entries = Vec::new();
    entries
        .try_reserve(first.entries().len().saturating_add(second.entries().len()))
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    let mut left = 0usize;
    let mut right = 0usize;
    while left < first.entries().len() || right < second.entries().len() {
        let entry = match (first.entries().get(left), second.entries().get(right)) {
            (Some(first_entry), Some(second_entry)) => {
                match first_entry.coordinate().cmp(&second_entry.coordinate()) {
                    std::cmp::Ordering::Less => {
                        left += 1;
                        Some(first_entry.clone())
                    }
                    std::cmp::Ordering::Greater => {
                        right += 1;
                        Some(second_entry.clone())
                    }
                    std::cmp::Ordering::Equal => {
                        left += 1;
                        right += 1;
                        compose_retained_entry(first_entry, second_entry)?
                    }
                }
            }
            (Some(first_entry), None) => {
                left += 1;
                Some(first_entry.clone())
            }
            (None, Some(second_entry)) => {
                right += 1;
                Some(second_entry.clone())
            }
            (None, None) => break,
        };
        if let Some(entry) = entry {
            entries.push(entry);
        }
    }
    if entries.is_empty() {
        return Ok(None);
    }
    SparsePhysicalStateDelta::from_canonical_entries(entries)
        .map(Some)
        .ok_or(FormationError::NoncanonicalState)
}

fn compose_retained_entry(
    first: &PhysicalStateDeltaEntry,
    second: &PhysicalStateDeltaEntry,
) -> Result<Option<PhysicalStateDeltaEntry>, FormationError> {
    if first.coordinate() != second.coordinate() {
        return Err(FormationError::NoncanonicalState);
    }
    let delta = match (first.delta(), second.delta()) {
        (ExactPhysicalStateDelta::Integral(first), ExactPhysicalStateDelta::Integral(second)) => {
            let (first_negative, first_magnitude) = first.parts();
            let (second_negative, second_magnitude) = second.parts();
            if first_negative == second_negative {
                ExactSignedDelta::from_parts(
                    first_negative,
                    first_magnitude
                        .checked_add(second_magnitude)
                        .ok_or(FormationError::ArithmeticOverflow)?,
                )
                .map(ExactPhysicalStateDelta::Integral)
            } else {
                match first_magnitude.cmp(&second_magnitude) {
                    std::cmp::Ordering::Greater => ExactSignedDelta::from_parts(
                        first_negative,
                        first_magnitude - second_magnitude,
                    )
                    .map(ExactPhysicalStateDelta::Integral),
                    std::cmp::Ordering::Less => ExactSignedDelta::from_parts(
                        second_negative,
                        second_magnitude - first_magnitude,
                    )
                    .map(ExactPhysicalStateDelta::Integral),
                    std::cmp::Ordering::Equal => None,
                }
            }
        }
        (ExactPhysicalStateDelta::Rational(first), ExactPhysicalStateDelta::Rational(second)) => {
            let summed = first
                .checked_add(second)
                .map_err(|_| FormationError::ArithmeticOverflow)?;
            (summed.parts().0 != 0).then_some(ExactPhysicalStateDelta::Rational(summed))
        }
        _ => return Err(FormationError::NoncanonicalState),
    };
    Ok(delta.and_then(|delta| PhysicalStateDeltaEntry::new(first.coordinate(), delta)))
}

/// One transient efferent event produced by an already-mounted layer-12
/// motor neuron. The exact outward whole-carrier membrane discharge is the
/// authority; this value is neither persisted nor counted as a fractal,
/// memory, intent, or action.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct MotorUnitRecruitment {
    pub(crate) neuron_lineage: [u8; 16],
    pub(crate) topology_index: u32,
    pub(crate) outward_elementary_carriers: u128,
    /// The motor neuron's own retained efferent mount. This—not its afferent
    /// ancestry—is the authority for which antagonist terminal receives the
    /// outward carrier discharge.
    pub(crate) body_effector_terminal: BodyEffectorTerminal,
    /// Exact sparse afferent ancestry already retained behind this motor cell:
    /// layer 12 -> layer 8 body regulation -> layer 6 local integration ->
    /// one named layer-5 physical body receptor. This is transient anatomy
    /// evidence only. An afferent site is not silently promoted into an
    /// effector, action name, or command.
    pub(crate) body_afferent_paths: Vec<MotorBodyAfferentPath>,
    /// Every exact whole-carrier transfer across this motor cell's direct
    /// contact with a mounted layer-11 ordering cell in the settled actuator
    /// interval. The potential difference of both endpoints causes the
    /// transfer; its signed direction is preserved rather than relabelled as
    /// excitation. This is transient causal evidence, not a plan, score,
    /// command, or retained action object.
    pub(crate) preparation_transfers: Vec<DirectedPhysicalTransferObservation>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct MotorBodyAfferentPath {
    pub(crate) body_regulation_lineage: [u8; 16],
    pub(crate) integration_lineage: [u8; 16],
    pub(crate) receptor_lineage: [u8; 16],
    pub(crate) receptor_site: NeuronSourceSite,
}

/// One transient efferent event produced by an already-mounted layer-13
/// articulatory neuron. Its exact outward whole-carrier discharge and direct
/// layer-12 contact transfer are the only authority. It is not speech,
/// phoneme identity, meaning, a retained motor program, or an action selector.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct ArticulatoryUnitRecruitment {
    pub(crate) neuron_lineage: [u8; 16],
    pub(crate) topology_index: u32,
    pub(crate) outward_elementary_carriers: u128,
    pub(crate) motor_transfers: Vec<DirectedPhysicalTransferObservation>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct CognitiveFormationSummary {
    pub(crate) cognitive_ordinal: u64,
    pub(crate) trace_count: usize,
    pub(crate) mosaic_count: usize,
    pub(crate) complete_neuron_count: usize,
    /// Source-independent complete cells retained in their shared exact
    /// quiescent law. They are real declared anatomy, but not reached work and
    /// therefore remain separate from `complete_neuron_count`.
    pub(crate) resting_neuron_count: usize,
    /// The body's decoded energy state.  Present on a restored organism too,
    /// so a restart never hides an exhausted body.
    pub(crate) energy: ReachedCohortEnergyState,
}

/// One caller-AUTHORED contact between two of the caller's own declared
/// receptors, named the way the caller's roster names them.
///
/// This is the same authorship growth DNA carries at genesis
/// (`DevelopmentalElectricalContact`), addressed by declared receptor rather
/// than by seed index because a living cohort's storage order is its own.
#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct AuthoredDeclaredContact {
    pub(crate) left_sensor_id: String,
    pub(crate) left_substream_id: String,
    pub(crate) right_sensor_id: String,
    pub(crate) right_substream_id: String,
    pub(crate) conductance_picosiemens: ExactRational,
}

/// Widen one per-contact activity mask for `added` newly authored contacts.
/// A contact that did not exist cannot have been active, so every appended
/// entry is `false`; every existing entry travels through verbatim.
fn extend_contact_mask(mask: &[bool], added: usize) -> Result<Box<[bool]>, FormationError> {
    let width = mask
        .len()
        .checked_add(added)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let mut widened = Vec::new();
    widened
        .try_reserve_exact(width)
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    widened.extend_from_slice(mask);
    widened.resize(width, false);
    Ok(widened.into_boxed_slice())
}

/// Position of one declared receptor within a cohort, or `None` when this
/// cohort does not carry it.  Two members declaring the same receptor would
/// make the name ambiguous and is refused rather than resolved.
fn declared_site_member(
    anatomy: &ReachedCohortAnatomy,
    sensor_id: &str,
    substream_id: &str,
) -> Result<Option<usize>, FormationError> {
    let mut found = None;
    for (index, mount) in anatomy.mounts().iter().enumerate() {
        let Some(site) = mount.source_site() else {
            continue;
        };
        if site.sensor_id() == sensor_id && site.substream_id() == substream_id {
            if found.is_some() {
                return Err(FormationError::AuthoredContactUnavailable);
            }
            found = Some(index);
        }
    }
    Ok(found)
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResidentReachedCohort {
    anatomy: ReachedCohortAnatomy,
    state: Arc<ReachedCohortState>,
    pending_experience: Option<ResidentExperienceEvidence>,
    retained_experience: Option<ResidentExperienceEvidence>,
    pending_recurrence: Option<ResidentRecurrenceEvidence>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
enum ExperienceEvidenceCodec {
    V1,
    V2,
    V3,
    V4,
    V5,
    V6,
    V7,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResidentExperienceEvidence {
    /// Persistence representation only. Untouched restored evidence retains
    /// its exact bytes; any subsequent physical mutation advances it to V4.
    codec: ExperienceEvidenceCodec,
    physical: ResidentExperiencePhysicalEvidence,
    gate_work_perturbed_neurons: SparseResidentNeuronMask,
    receptor_excitation_zeptojoules: Box<[Option<ExactRational>]>,
    /// Neurons whose own retained coordinates changed during this occurrence.
    /// This is distinct from gate work: a physically active neuron may retain
    /// nothing, and an electrically reached neighbour may retain change.
    retained_change_neurons: Box<[bool]>,
    /// Neurons whose retained coordinates subsequently completed one exact
    /// unchanged interval. Settlement is neuron-local; another living neuron
    /// may remain active without blocking this one.
    retentively_settled_neurons: Box<[bool]>,
    active_electrical_contacts: Box<[bool]>,
    /// True only after the retained formation has completed one later
    /// settlement carrying no exogenous gate work.  The later settlement is
    /// the exact causal separation: ongoing internal current is life, not a
    /// reason to demand whole-formation electrical silence, and that same
    /// settlement cannot become its own cue.
    local_relaxation_observed: bool,
}

#[derive(Clone, Debug, Eq, PartialEq)]
enum ResidentExperiencePhysicalEvidence {
    /// Decode-only custody used while proving an existing V1-V6 body's exact
    /// canonical bytes. It is converted and dropped before cold restore
    /// returns a live resident organism.
    Legacy {
        predecessor: Arc<ReachedCohortState>,
        successor: Option<Arc<ReachedCohortState>>,
    },
    Pending(Box<[SparsePendingExperienceMember]>),
    Retained(Box<[SparseRetainedExperienceMember]>),
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct SparsePendingExperienceMember {
    neuron_index: usize,
    predecessor: NeuronPhysicalState,
    settled: bool,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct SparseRetainedExperienceMember {
    neuron_index: usize,
    predecessor: NeuronPhysicalState,
    learned: NeuronPhysicalState,
    delta: SparsePhysicalStateDelta,
}

impl ResidentExperienceEvidence {
    fn is_pending(&self) -> bool {
        matches!(
            self.physical,
            ResidentExperiencePhysicalEvidence::Pending(_)
                | ResidentExperiencePhysicalEvidence::Legacy {
                    successor: None,
                    ..
                }
        )
    }

    fn is_retained(&self) -> bool {
        matches!(
            self.physical,
            ResidentExperiencePhysicalEvidence::Retained(_)
                | ResidentExperiencePhysicalEvidence::Legacy {
                    successor: Some(_),
                    ..
                }
        )
    }

    fn legacy_states(
        &self,
    ) -> Option<(&ReachedCohortState, Option<&ReachedCohortState>)> {
        match &self.physical {
            ResidentExperiencePhysicalEvidence::Legacy {
                predecessor,
                successor,
            } => Some((predecessor, successor.as_deref())),
            ResidentExperiencePhysicalEvidence::Pending(_)
            | ResidentExperiencePhysicalEvidence::Retained(_) => None,
        }
    }

    fn pending_members(&self) -> Option<&[SparsePendingExperienceMember]> {
        match &self.physical {
            ResidentExperiencePhysicalEvidence::Pending(members) => Some(members),
            ResidentExperiencePhysicalEvidence::Legacy { .. }
            | ResidentExperiencePhysicalEvidence::Retained(_) => None,
        }
    }

    fn pending_members_mut(&mut self) -> Option<&mut Box<[SparsePendingExperienceMember]>> {
        match &mut self.physical {
            ResidentExperiencePhysicalEvidence::Pending(members) => Some(members),
            ResidentExperiencePhysicalEvidence::Legacy { .. }
            | ResidentExperiencePhysicalEvidence::Retained(_) => None,
        }
    }

    fn retained_members(&self) -> Option<&[SparseRetainedExperienceMember]> {
        match &self.physical {
            ResidentExperiencePhysicalEvidence::Retained(members) => Some(members),
            ResidentExperiencePhysicalEvidence::Legacy { .. }
            | ResidentExperiencePhysicalEvidence::Pending(_) => None,
        }
    }

    fn convert_legacy_physical(
        &mut self,
        anatomy: &ReachedCohortAnatomy,
        retained: bool,
    ) -> Result<(), FormationError> {
        let ResidentExperiencePhysicalEvidence::Legacy {
            predecessor,
            successor,
        } = &self.physical
        else {
            return Ok(());
        };
        if predecessor.neurons().len() != anatomy.neuron_count()
            || successor
                .as_ref()
                .is_some_and(|state| state.neurons().len() != anatomy.neuron_count())
        {
            return Err(FormationError::NoncanonicalState);
        }
        if retained {
            let successor = successor
                .as_ref()
                .ok_or(FormationError::NoncanonicalState)?;
            let mut members = Vec::new();
            members
                .try_reserve(
                    self.retentively_settled_neurons
                        .iter()
                        .filter(|settled| **settled)
                        .count(),
                )
                .map_err(|_| FormationError::ArithmeticOverflow)?;
            for (neuron_index, settled) in
                self.retentively_settled_neurons.iter().copied().enumerate()
            {
                if !settled {
                    continue;
                }
                if let Some(delta) = sparse_retained_physical_state_delta(
                    &predecessor.neurons()[neuron_index],
                    &successor.neurons()[neuron_index],
                )
                .map_err(|error| {
                    FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                        neuron_index,
                        error,
                    })
                })? {
                    members.push(SparseRetainedExperienceMember {
                        neuron_index,
                        predecessor: predecessor.neurons()[neuron_index].clone(),
                        learned: successor.neurons()[neuron_index].clone(),
                        delta,
                    });
                }
            }
            let mut retained_change_neurons = vec![false; anatomy.neuron_count()];
            let mut retentively_settled_neurons = vec![false; anatomy.neuron_count()];
            for member in &members {
                retained_change_neurons[member.neuron_index] = true;
                retentively_settled_neurons[member.neuron_index] = true;
            }
            self.physical =
                ResidentExperiencePhysicalEvidence::Retained(members.into_boxed_slice());
            self.retained_change_neurons = retained_change_neurons.into_boxed_slice();
            self.retentively_settled_neurons = retentively_settled_neurons.into_boxed_slice();
        } else {
            if successor.is_some() {
                return Err(FormationError::NoncanonicalState);
            }
            let mut members = Vec::new();
            members
                .try_reserve(
                    self.retained_change_neurons
                        .iter()
                        .filter(|changed| **changed)
                        .count(),
                )
                .map_err(|_| FormationError::ArithmeticOverflow)?;
            for (neuron_index, changed) in
                self.retained_change_neurons.iter().copied().enumerate()
            {
                if changed {
                    members.push(SparsePendingExperienceMember {
                        neuron_index,
                        predecessor: predecessor.neurons()[neuron_index].clone(),
                        settled: self.retentively_settled_neurons[neuron_index],
                    });
                }
            }
            let mut retained_change_neurons = vec![false; anatomy.neuron_count()];
            let mut retentively_settled_neurons = vec![false; anatomy.neuron_count()];
            for member in &members {
                retained_change_neurons[member.neuron_index] = true;
                retentively_settled_neurons[member.neuron_index] = member.settled;
            }
            self.physical =
                ResidentExperiencePhysicalEvidence::Pending(members.into_boxed_slice());
            self.retained_change_neurons = retained_change_neurons.into_boxed_slice();
            self.retentively_settled_neurons = retentively_settled_neurons.into_boxed_slice();
        }
        self.codec = ExperienceEvidenceCodec::V7;
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResidentRecurrenceEvidence {
    carries_physical_change_codec: bool,
    gate_work_perturbed_neurons: SparseResidentNeuronMask,
    receptor_excitation_zeptojoules: Box<[Option<ExactRational>]>,
    physically_changed_neurons: Box<[bool]>,
    active_recurrence_contacts: Box<[bool]>,
    endogenous: bool,
}

/// Exact resident-neuron membership without one Boolean per cohort member.
/// Indices are strictly increasing and remain stable when cohort growth only
/// appends new members.  The historical dense layout is reconstructed only at
/// the existing canonical codec and physical-mosaic boundaries.
#[derive(Clone, Debug, Default, Eq, PartialEq)]
struct SparseResidentNeuronMask {
    indices: Box<[usize]>,
}

impl SparseResidentNeuronMask {
    fn empty() -> Self {
        Self::default()
    }

    fn from_dense(values: &[bool]) -> Self {
        Self {
            indices: values
                .iter()
                .enumerate()
                .filter_map(|(index, value)| (*value).then_some(index))
                .collect::<Vec<_>>()
                .into_boxed_slice(),
        }
    }

    fn from_dense_bytes(values: &[u8]) -> Result<Self, FormationError> {
        let mut indices = Vec::new();
        indices
            .try_reserve(values.iter().filter(|value| **value == 1).count())
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for (index, value) in values.iter().copied().enumerate() {
            match value {
                0 => {}
                1 => indices.push(index),
                _ => return Err(FormationError::NoncanonicalState),
            }
        }
        Ok(Self {
            indices: indices.into_boxed_slice(),
        })
    }

    fn validates_width(&self, neuron_count: usize) -> bool {
        self.indices.last().is_none_or(|index| *index < neuron_count)
            && self.indices.windows(2).all(|pair| pair[0] < pair[1])
    }

    fn is_empty(&self) -> bool {
        self.indices.is_empty()
    }

    fn count(&self) -> usize {
        self.indices.len()
    }

    fn union_dense(&mut self, values: &[bool]) -> Result<(), FormationError> {
        if !self.validates_width(values.len()) {
            return Err(FormationError::NoncanonicalState);
        }
        let additions = values
            .iter()
            .enumerate()
            .filter_map(|(index, value)| (*value).then_some(index))
            .collect::<Vec<_>>();
        let mut merged = Vec::new();
        merged
            .try_reserve(self.indices.len().saturating_add(additions.len()))
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let (mut left, mut right) = (0usize, 0usize);
        while left < self.indices.len() || right < additions.len() {
            match (self.indices.get(left), additions.get(right)) {
                (Some(existing), Some(addition)) if existing < addition => {
                    merged.push(*existing);
                    left += 1;
                }
                (Some(existing), Some(addition)) if addition < existing => {
                    merged.push(*addition);
                    right += 1;
                }
                (Some(existing), Some(_)) => {
                    merged.push(*existing);
                    left += 1;
                    right += 1;
                }
                (Some(existing), None) => {
                    merged.push(*existing);
                    left += 1;
                }
                (None, Some(addition)) => {
                    merged.push(*addition);
                    right += 1;
                }
                (None, None) => break,
            }
        }
        self.indices = merged.into_boxed_slice();
        Ok(())
    }

    fn to_dense(&self, neuron_count: usize) -> Result<Box<[bool]>, FormationError> {
        if !self.validates_width(neuron_count) {
            return Err(FormationError::NoncanonicalState);
        }
        let mut dense = vec![false; neuron_count];
        for index in self.indices.iter().copied() {
            dense[index] = true;
        }
        Ok(dense.into_boxed_slice())
    }

    fn encode_dense(&self, encoded: &mut Vec<u8>, neuron_count: usize) -> Result<(), FormationError> {
        if !self.validates_width(neuron_count) {
            return Err(FormationError::NoncanonicalState);
        }
        push_length(encoded, neuron_count)?;
        let mut next = self.indices.iter().copied().peekable();
        for neuron_index in 0..neuron_count {
            let perturbed = next.peek().is_some_and(|index| *index == neuron_index);
            encoded.push(u8::from(perturbed));
            if perturbed {
                next.next();
            }
        }
        Ok(())
    }

    fn encode_sparse(
        &self,
        encoded: &mut Vec<u8>,
        neuron_count: usize,
    ) -> Result<(), FormationError> {
        if !self.validates_width(neuron_count) {
            return Err(FormationError::NoncanonicalState);
        }
        push_length(encoded, self.indices.len())?;
        for index in self.indices.iter().copied() {
            push_length(encoded, index)?;
        }
        Ok(())
    }

    fn decode_sparse(
        encoded: &[u8],
        cursor: &mut usize,
        neuron_count: usize,
    ) -> Result<Self, FormationError> {
        let count = read_length(encoded, cursor)?;
        if count > neuron_count {
            return Err(FormationError::NoncanonicalState);
        }
        let mut indices = Vec::new();
        indices
            .try_reserve_exact(count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for _ in 0..count {
            let index = read_length(encoded, cursor)?;
            if index >= neuron_count || indices.last().is_some_and(|prior| *prior >= index) {
                return Err(FormationError::NoncanonicalState);
            }
            indices.push(index);
        }
        Ok(Self {
            indices: indices.into_boxed_slice(),
        })
    }

    fn decode_dense(
        encoded: &[u8],
        cursor: &mut usize,
        neuron_count: usize,
    ) -> Result<Self, FormationError> {
        let count = read_length(encoded, cursor)?;
        if count != neuron_count {
            return Err(FormationError::NoncanonicalState);
        }
        let end = cursor
            .checked_add(count)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let mask = Self::from_dense_bytes(
            encoded
                .get(*cursor..end)
                .ok_or(FormationError::NoncanonicalState)?,
        )?;
        *cursor = end;
        Ok(mask)
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub(crate) struct DormantLineageSeed {
    sense: u8,
    topology_index: u32,
    sensor_id: Box<str>,
    substream_id: Box<str>,
    neuron_lineage: [u8; 16],
}

impl DormantLineageSeed {
    pub(crate) fn new(
        sense: u8,
        topology_index: u32,
        sensor_id: &str,
        substream_id: &str,
        neuron_lineage: [u8; 16],
    ) -> Result<Self, FormationError> {
        let seed = Self {
            sense,
            topology_index,
            sensor_id: sensor_id.into(),
            substream_id: substream_id.into(),
            neuron_lineage,
        };
        seed.validate()?;
        Ok(seed)
    }

    fn from_port(
        port: &crate::joint_source_episode::JointSourcePortView,
        neuron_lineage: [u8; 16],
    ) -> Result<Self, FormationError> {
        Self::new(
            port.sense,
            port.topology_index,
            &port.sensor_id,
            &port.substream_id,
            neuron_lineage,
        )
    }

    fn from_site(
        site: &NeuronSourceSite,
        neuron_lineage: [u8; 16],
    ) -> Result<Self, FormationError> {
        Self::new(
            site.sense().declared_layer(),
            site.topology_index(),
            site.sensor_id(),
            site.substream_id(),
            neuron_lineage,
        )
    }

    fn same_source(&self, other: &Self) -> bool {
        self.sense == other.sense
            && self.topology_index == other.topology_index
            && self.sensor_id == other.sensor_id
            && self.substream_id == other.substream_id
    }

    fn matches_port(&self, port: &crate::joint_source_episode::JointSourcePortView) -> bool {
        self.sense == port.sense
            && self.topology_index == port.topology_index
            && self.sensor_id.as_ref() == port.sensor_id
            && self.substream_id.as_ref() == port.substream_id
    }

    fn validate(&self) -> Result<(), FormationError> {
        if self.sense > 5
            || self.sensor_id.is_empty()
            || self.substream_id.is_empty()
            || !valid_local_lineage(self.neuron_lineage)
        {
            return Err(FormationError::NoncanonicalState);
        }
        Ok(())
    }

    pub(crate) fn lineage(&self) -> [u8; 16] {
        self.neuron_lineage
    }
}

/// One compact retained physical formation. Identity is its exact original
/// neuronal deltas and bonds, not its member set: the same neurons may belong
/// to many formations. Later physical reassembly updates only the bounded
/// recurrence witness and never overwrites the original.
#[derive(Clone, Debug, Eq, PartialEq)]
struct RetainedOrganismMosaic {
    mosaic: AdmittedPhysicalMosaic,
    /// The exact layer-9 cell grown with this mosaic's member contacts. The
    /// contacts remain physical authority; persisting their recurrent endpoint
    /// prevents later downstream ordering contacts from making topology-only
    /// reconstruction ambiguous.
    recurrent_lineage: Option<[u8; 16]>,
    /// Retired historical codec field. A count is not physical strengthening,
    /// so current physics never reads or increments it.
    reinforcement_count: u64,
    /// Retired historical codec field. Overlap alone is not a relation, so
    /// current physics never increments it; it remains only to cold-restore
    /// an already lived body without byte loss.
    mosaic_of_mosaics_relation_count: u64,
}

impl RetainedOrganismMosaic {
    /// A first admission: the reference body with both counts at the
    /// historical default of zero (codec: encoded as the bare mosaic body,
    /// byte-identical to every pre-law receipt).
    fn newly_admitted(mosaic: AdmittedPhysicalMosaic) -> Self {
        Self {
            mosaic,
            recurrent_lineage: None,
            reinforcement_count: 0,
            mosaic_of_mosaics_relation_count: 0,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct ResidentCognitiveFormationState {
    generation: u64,
    next_lineage_ordinal: u64,
    unexpressed_electrical_seeds: Box<[DevelopmentalElectricalSeed]>,
    dormant_lineage_seeds: Box<[DormantLineageSeed]>,
    resting_population: Option<DevelopmentalRestingPopulation>,
    cohorts: Box<[ResidentReachedCohort]>,
    electrical_fabric: ResidentElectricalFabric,
    /// Exact sparse intrinsic lineages that received whole carriers across a
    /// physical contact in the preceding interval. They alone may continue
    /// through another local contact in the next interval. This is short-lived
    /// electrical propagation state, not stored memory or a returned answer.
    /// Absolute membrane charge is deliberately not authority here: a living
    /// neuron's resting potential may be nonzero.
    active_electrical_frontier: Box<[ActiveElectricalFrontierEntry]>,
    /// The sparse directed frontier immediately before
    /// `active_electrical_frontier`. Together these two physical propagation
    /// boundaries are the minimum state needed to observe two overlapping
    /// ordered paths. Anything older has already expired.
    preceding_active_electrical_frontier: Box<[ActiveElectricalFrontierEntry]>,
    /// The sparse frontier immediately before
    /// `preceding_active_electrical_frontier`. Three retained frontiers plus
    /// the current interval are the exact bounded window for two recurring
    /// two-contact paths; anything older has expired.
    older_active_electrical_frontier: Box<[ActiveElectricalFrontierEntry]>,
    mosaics: Box<[RetainedOrganismMosaic]>,
    hippocampal: ResidentHippocampalIndex,
    /// Runtime-only exact navigation over resident anatomy. Canonical bytes
    /// remain owned by cohorts and the electrical fabric; ordinary physical
    /// intervals borrow this index instead of rediscovering every lineage,
    /// contact, stable bond, layer, and neighbour.
    topology_index: Arc<ResidentTopologyIndex>,
}

impl Default for ResidentCognitiveFormationState {
    fn default() -> Self {
        Self {
            generation: 0,
            next_lineage_ordinal: 1,
            unexpressed_electrical_seeds: Box::new([]),
            dormant_lineage_seeds: Box::new([]),
            resting_population: None,
            cohorts: Box::new([]),
            electrical_fabric: ResidentElectricalFabric::default(),
            active_electrical_frontier: Box::new([]),
            preceding_active_electrical_frontier: Box::new([]),
            older_active_electrical_frontier: Box::new([]),
            mosaics: Box::new([]),
            hippocampal: ResidentHippocampalIndex::default(),
            topology_index: Arc::new(ResidentTopologyIndex::empty()),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PreparedCognitiveFormationTransition {
    predecessor_generation: u64,
    predecessor_hippocampal: ResidentHippocampalIndex,
    successor: ResidentCognitiveFormationState,
    successor_encoded: Vec<u8>,
    observation: CognitiveFormationObservation,
}

impl PreparedCognitiveFormationTransition {
    pub(crate) fn observation(&self) -> &CognitiveFormationObservation {
        &self.observation
    }

    pub(crate) fn try_into_successor(
        self,
        predecessor: &ResidentCognitiveFormationState,
    ) -> Result<
        (
            ResidentCognitiveFormationState,
            CognitiveFormationObservation,
        ),
        (FormationError, Self),
    > {
        if predecessor.generation != self.predecessor_generation {
            return Err((FormationError::PreparedPredecessorChanged, self));
        }
        Ok((self.successor, self.observation))
    }
}

fn encode_organism_mosaic(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
    mosaic: &AdmittedPhysicalMosaic,
    max_encoded_bytes: usize,
) -> Result<Vec<u8>, FormationError> {
    let topology = organism_mosaic_topology(cohorts, electrical_fabric)?;
    encode_admitted_physical_mosaic_for_topology(
        &topology.lineages,
        &topology.bonds,
        &topology.fractal_anatomies,
        mosaic,
        max_encoded_bytes,
    )
    .map_err(FormationError::PhysicalMosaicCodecUnavailable)
}

fn decode_organism_mosaic(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
    encoded: &[u8],
    max_encoded_bytes: usize,
) -> Result<AdmittedPhysicalMosaic, FormationError> {
    let topology = organism_mosaic_topology(cohorts, electrical_fabric)?;
    decode_admitted_physical_mosaic_for_topology(
        &topology.lineages,
        &topology.bonds,
        &topology.fractal_anatomies,
        encoded,
        max_encoded_bytes,
    )
    .map_err(FormationError::PhysicalMosaicCodecUnavailable)
}

struct OrganismMosaicTopology {
    lineages: Vec<[u8; 16]>,
    fractal_anatomies: Vec<(usize, usize)>,
    bonds: Vec<StablePhysicalBondReference>,
}

struct TransitionNeuronPredecessor {
    lineage: [u8; 16],
    anatomy: NeuronPhysicalAnatomy,
    state: NeuronPhysicalState,
}

fn retain_first_transition_predecessor(
    predecessors: &mut Vec<TransitionNeuronPredecessor>,
    predecessor: TransitionNeuronPredecessor,
) {
    match predecessors.binary_search_by_key(&predecessor.lineage, |entry| entry.lineage) {
        Ok(_) => {}
        Err(index) => predecessors.insert(index, predecessor),
    }
}

fn exact_transition_physical_deltas(
    cohorts: &[ResidentReachedCohort],
    topology_index: &ResidentTopologyIndex,
    predecessors: &[TransitionNeuronPredecessor],
) -> Result<Vec<([u8; 16], SparsePhysicalStateDelta)>, FormationError> {
    let mut deltas = Vec::new();
    deltas
        .try_reserve(predecessors.len())
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    for predecessor in predecessors {
        let flat = topology_index.flat_for_lineage(predecessor.lineage)?;
        let (cohort_index, neuron_index, _) = topology_index
            .flat_locations
            .get(flat)
            .copied()
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        let successor_anatomy = &cohorts[cohort_index].anatomy.neuron_anatomies()[neuron_index];
        let successor_state = &cohorts[cohort_index].state.neurons()[neuron_index];
        let (extended_anatomy, extended_predecessor) = extend_neuron_positional_fabric(
            &predecessor.anatomy,
            &predecessor.state,
            successor_anatomy.mathloom_positions(),
        )
        .map_err(|error| {
            FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                neuron_index,
                error,
            })
        })?;
        if &extended_anatomy != successor_anatomy {
            return Err(FormationError::NoncanonicalState);
        }
        if let Some(delta) = sparse_physical_state_delta(&extended_predecessor, successor_state)
            .map_err(|error| {
                FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                    neuron_index,
                    error,
                })
            })?
        {
            deltas.push((predecessor.lineage, delta));
        }
    }
    Ok(deltas)
}

fn organism_mosaic_topology(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
) -> Result<OrganismMosaicTopology, FormationError> {
    let mut lineages = Vec::new();
    let mut fractal_anatomies = Vec::new();
    for cohort in cohorts {
        for (lineage, anatomy) in cohort
            .anatomy
            .neuron_lineages()
            .iter()
            .copied()
            .zip(cohort.anatomy.neuron_anatomies())
        {
            if lineages.contains(&lineage) {
                return Err(FormationError::NeuronLineageAuthorityChanged);
            }
            lineages.push(lineage);
            fractal_anatomies.push((
                anatomy.psi_ring_count(),
                anatomy
                    .sparse_delta_coordinate_count()
                    .ok_or(FormationError::ArithmeticOverflow)?,
            ));
        }
    }
    Ok(OrganismMosaicTopology {
        lineages,
        fractal_anatomies,
        bonds: organism_physical_bonds(cohorts, electrical_fabric)?,
    })
}

/// Borrow the resident topology authority for ordinary mosaic settlement.
/// Only the mutable fractal coordinate widths are read from reached anatomy;
/// lineage discovery, contact traversal, parallel-bond assignment, and bond
/// sorting were already performed at genesis, cold restore, or topology
/// growth.
fn indexed_organism_mosaic_topology(
    cohorts: &[ResidentReachedCohort],
    topology_index: &ResidentTopologyIndex,
) -> Result<OrganismMosaicTopology, FormationError> {
    if topology_index.cohort_shapes.len() != cohorts.len() {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    }
    let mut fractal_anatomies = Vec::new();
    fractal_anatomies
        .try_reserve_exact(topology_index.canonical_lineages.len())
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    for cohort in cohorts {
        for anatomy in cohort.anatomy.neuron_anatomies() {
            fractal_anatomies.push((
                anatomy.psi_ring_count(),
                anatomy
                    .sparse_delta_coordinate_count()
                    .ok_or(FormationError::ArithmeticOverflow)?,
            ));
        }
    }
    if fractal_anatomies.len() != topology_index.canonical_lineages.len() {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    }
    Ok(OrganismMosaicTopology {
        lineages: topology_index.canonical_lineages.to_vec(),
        fractal_anatomies,
        bonds: topology_index.canonical_bonds.to_vec(),
    })
}

/// Resolve only stable contact identities. Codec validation uses this narrow
/// boundary so authenticating a one-interval electrical frontier does not
/// rebuild neuron fractal anatomy or any retained cognitive formation.
fn organism_physical_bonds(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
) -> Result<Vec<StablePhysicalBondReference>, FormationError> {
    let mut endpoint_pairs = Vec::<([u8; 16], [u8; 16])>::new();
    for cohort in cohorts {
        for (left, right) in cohort.anatomy.contact_endpoints() {
            endpoint_pairs.push((
                cohort.anatomy.neuron_lineages()[left],
                cohort.anatomy.neuron_lineages()[right],
            ));
        }
    }
    for (left, right) in electrical_fabric.contact_endpoints() {
        endpoint_pairs.push((
            electrical_fabric.lineages()[left],
            electrical_fabric.lineages()[right],
        ));
    }
    let mut bonds = Vec::<StablePhysicalBondReference>::with_capacity(endpoint_pairs.len());
    for (first, second) in endpoint_pairs {
        let canonical = if first < second {
            (first, second)
        } else {
            (second, first)
        };
        let parallel_ordinal = u32::try_from(
            bonds
                .iter()
                .filter(|bond| bond.endpoints() == canonical)
                .count(),
        )
        .map_err(|_| FormationError::ArithmeticOverflow)?;
        bonds.push(
            StablePhysicalBondReference::new(first, second, parallel_ordinal)
                .ok_or(FormationError::NoncanonicalState)?,
        );
    }
    bonds.sort_unstable();
    Ok(bonds)
}

/// A retained organism mosaic must cross at least one cohort boundary. A
/// formation wholly contained in one receptor cohort is sensory-local
/// structure, not a whole-organism mosaic, irrespective of how many neurons
/// it contains. Every member lineage is already validated against the living
/// anatomy by the mosaic codec; this function only classifies that exact
/// structural scope.
fn mosaic_spans_multiple_cohorts(
    cohorts: &[ResidentReachedCohort],
    mosaic: &AdmittedPhysicalMosaic,
) -> bool {
    let mut cohort_indices = Vec::new();
    for lineage in mosaic.member_lineages() {
        let Some(cohort_index) = cohorts.iter().position(|cohort| {
            cohort
                .anatomy
                .neuron_lineages()
                .binary_search(lineage)
                .is_ok()
        }) else {
            return false;
        };
        if !cohort_indices.contains(&cohort_index) {
            cohort_indices.push(cohort_index);
        }
    }
    cohort_indices.len() >= 2
}

fn merge_relation_components(component_roots: &mut [usize], left: usize, right: usize) {
    let mut left_root = left;
    while component_roots[left_root] != left_root {
        left_root = component_roots[left_root];
    }
    let mut right_root = right;
    while component_roots[right_root] != right_root {
        right_root = component_roots[right_root];
    }
    if left_root == right_root {
        return;
    }
    let (kept, replaced) = if left_root < right_root {
        (left_root, right_root)
    } else {
        (right_root, left_root)
    };
    for root in component_roots {
        if *root == replaced {
            *root = kept;
        }
    }
}

fn structural_relation_receipt(
    mosaics: &[RetainedOrganismMosaic],
    frontier_indices: &[usize],
    relation_members: &[usize],
    shared_lineages: &[[u8; 16]],
    active_bonds: &[StablePhysicalBondReference],
) -> [u8; 32] {
    let mut member_sets = relation_members
        .iter()
        .map(|local_index| {
            mosaics[frontier_indices[*local_index]]
                .mosaic
                .member_lineages()
        })
        .collect::<Vec<_>>();
    member_sets.sort_unstable();

    let mut digest = Sha256::new();
    digest.update(b"guala.organic_mosaic_relation.structure.v1\0");
    digest.update((member_sets.len() as u128).to_le_bytes());
    for member_set in member_sets {
        digest.update((member_set.len() as u128).to_le_bytes());
        for lineage in member_set {
            digest.update(lineage);
        }
    }
    digest.update((shared_lineages.len() as u128).to_le_bytes());
    for lineage in shared_lineages {
        digest.update(lineage);
    }
    digest.update((active_bonds.len() as u128).to_le_bytes());
    for bond in active_bonds {
        let (left, right) = bond.endpoints();
        digest.update(left);
        digest.update(right);
        digest.update(bond.parallel_ordinal().to_le_bytes());
    }
    digest.finalize().into()
}

fn ordered_physical_paths_for_relation(
    incidence: &[([u8; 16], usize)],
    relation_members: &[usize],
    predecessor_frontier: &[ActiveElectricalFrontierEntry],
    current_frontier: &[ActiveElectricalFrontierEntry],
) -> Vec<OrderedPhysicalPathObservation> {
    let mut lineage_members = Vec::<([u8; 16], Vec<usize>)>::new();
    let mut cursor = 0usize;
    while cursor < incidence.len() {
        let lineage = incidence[cursor].0;
        let start = cursor;
        while cursor < incidence.len() && incidence[cursor].0 == lineage {
            cursor += 1;
        }
        let members = incidence[start..cursor]
            .iter()
            .filter_map(|(_, participant)| {
                relation_members
                    .binary_search(participant)
                    .is_ok()
                    .then_some(*participant)
            })
            .collect::<Vec<_>>();
        if !members.is_empty() {
            lineage_members.push((lineage, members));
        }
    }
    let formation_members_for = |lineage: [u8; 16]| -> Option<&[usize]> {
        lineage_members
            .binary_search_by_key(&lineage, |(candidate, _)| *candidate)
            .ok()
            .map(|index| lineage_members[index].1.as_slice())
    };

    let mut preceding = predecessor_frontier
        .iter()
        .filter_map(|entry| entry.directed_transfer())
        .collect::<Vec<_>>();
    preceding.sort_unstable_by_key(|transfer| (transfer.receiver, transfer.sender, transfer.bond));
    let mut current = current_frontier
        .iter()
        .filter_map(|entry| entry.directed_transfer())
        .collect::<Vec<_>>();
    current.sort_unstable_by_key(|transfer| (transfer.sender, transfer.receiver, transfer.bond));

    let mut paths = Vec::new();
    let mut preceding_cursor = 0usize;
    let mut current_cursor = 0usize;
    while preceding_cursor < preceding.len() && current_cursor < current.len() {
        let preceding_via = preceding[preceding_cursor].receiver;
        let current_via = current[current_cursor].sender;
        if preceding_via < current_via {
            preceding_cursor += 1;
            continue;
        }
        if current_via < preceding_via {
            current_cursor += 1;
            continue;
        }
        let preceding_start = preceding_cursor;
        while preceding_cursor < preceding.len()
            && preceding[preceding_cursor].receiver == preceding_via
        {
            preceding_cursor += 1;
        }
        let current_start = current_cursor;
        while current_cursor < current.len() && current[current_cursor].sender == current_via {
            current_cursor += 1;
        }
        for first in &preceding[preceding_start..preceding_cursor] {
            let Some(first_formations) = formation_members_for(first.sender) else {
                continue;
            };
            for second in &current[current_start..current_cursor] {
                let Some(second_formations) = formation_members_for(second.receiver) else {
                    continue;
                };
                if first_formations.iter().all(|first_index| {
                    second_formations
                        .iter()
                        .all(|second_index| first_index == second_index)
                }) {
                    continue;
                }
                paths.push(OrderedPhysicalPathObservation {
                    first: *first,
                    second: *second,
                });
            }
        }
    }
    paths.sort_unstable();
    paths.dedup();
    paths
}

/// Observe at most one exact internally continued path and at most one exact
/// expired predecessor cause. The retained active frontiers already are the
/// working physical state; this function adds no state and authors no causal
/// rule. Restricting the projection to one canonical witness keeps the
/// observer constant-sized even when a sparse frontier branches.
fn working_causal_frontier_observation(
    predecessor_frontier: &[ActiveElectricalFrontierEntry],
    current_frontier: &[ActiveElectricalFrontierEntry],
    current_noncontinuation_seeds: &[[u8; 16]],
) -> (
    Vec<OrderedPhysicalPathObservation>,
    Vec<DirectedPhysicalTransferObservation>,
) {
    let mut predecessor = predecessor_frontier
        .iter()
        .filter_map(|entry| entry.directed_transfer())
        .collect::<Vec<_>>();
    predecessor
        .sort_unstable_by_key(|transfer| (transfer.receiver, transfer.sender, transfer.bond));
    let mut current = current_frontier
        .iter()
        .filter_map(|entry| entry.directed_transfer())
        .collect::<Vec<_>>();
    current.sort_unstable_by_key(|transfer| (transfer.sender, transfer.receiver, transfer.bond));

    let continuation = predecessor.iter().find_map(|first| {
        if current_noncontinuation_seeds.contains(&first.receiver) {
            return None;
        }
        current
            .iter()
            .find(|second| {
                second.sender == first.receiver
                    && !current_noncontinuation_seeds.contains(&second.receiver)
            })
            .map(|second| OrderedPhysicalPathObservation {
                first: *first,
                second: *second,
            })
    });
    let settled = predecessor
            .iter()
        .find(|first| !current.iter().any(|second| second.sender == first.receiver));

    (
        continuation.into_iter().collect(),
        settled.copied().into_iter().collect(),
    )
}

/// Observe one constant-sized set of physically ordered alternatives.
///
/// The predecessor interval must have carried material from one common
/// source-independent neuron into at least two retained ordering cells (layer
/// 11). The current interval must continue, without an independent current
/// seed, from those ordering cells into distinct retained body/affective
/// relations (layer 10). Existing sparse contacts and carrier transfer are the
/// entire authority; this function retains nothing and chooses no winner.
fn physical_prediction_alternatives_observation(
    predecessor_frontier: &[ActiveElectricalFrontierEntry],
    current_frontier: &[ActiveElectricalFrontierEntry],
    current_noncontinuation_seeds: &[[u8; 16]],
    lineage_layers: &[([u8; 16], u32)],
) -> Vec<OrderedPhysicalPathObservation> {
    let layer_of = |lineage: [u8; 16]| {
        lineage_layers
            .binary_search_by_key(&lineage, |(candidate, _)| *candidate)
            .ok()
            .map(|index| lineage_layers[index].1)
    };
    let mut predecessor = predecessor_frontier
        .iter()
        .filter_map(|entry| entry.directed_transfer())
        .filter(|transfer| {
            matches!(layer_of(transfer.sender), Some(layer) if layer > 5 && layer != 11)
                && layer_of(transfer.receiver) == Some(11)
                && !current_noncontinuation_seeds.contains(&transfer.receiver)
        })
        .collect::<Vec<_>>();
    predecessor.sort_unstable();
    let mut current = current_frontier
        .iter()
        .filter_map(|entry| entry.directed_transfer())
        .filter(|transfer| {
            layer_of(transfer.sender) == Some(11)
                && layer_of(transfer.receiver) == Some(10)
                && !current_noncontinuation_seeds.contains(&transfer.receiver)
        })
        .collect::<Vec<_>>();
    current.sort_unstable();

    let mut paths = predecessor
        .iter()
        .flat_map(|first| {
            current
                .iter()
                .filter(move |second| second.sender == first.receiver)
                .map(move |second| OrderedPhysicalPathObservation {
                    first: *first,
                    second: *second,
                })
        })
        .collect::<Vec<_>>();
    paths.sort_unstable();
    paths.dedup();

    for first_path in &paths {
        let Some(second_path) = paths.iter().find(|candidate| {
            candidate.first.sender == first_path.first.sender
                && candidate.first.receiver != first_path.first.receiver
                && candidate.second.receiver != first_path.second.receiver
        }) else {
            continue;
        };
        return vec![*first_path, *second_path];
    }
    Vec::new()
}

/// Observe one exact returned body consequence during vestibular settlement.
/// The layer-8 endpoint must be reached by this exact body occurrence and its
/// layer-10 endpoint is an already-mounted body/affective relation. Preserve
/// the actual carrier direction: body-to-relation can agree with a prior path,
/// while relation-to-body can contradict it. The caller alone supplies whether
/// this interval is authentic vestibular ingress, preventing ordinary internal
/// propagation from being relabelled as sensed consequence.
fn body_consequence_transfer_observation(
    current_frontier: &[ActiveElectricalFrontierEntry],
    lineage_layers: &[([u8; 16], u32)],
    reached_body_regulation_lineages: &[[u8; 16]],
    authentic_vestibular_ingress: bool,
) -> Vec<DirectedPhysicalTransferObservation> {
    if !authentic_vestibular_ingress {
        return Vec::new();
    }
    let layer_of = |lineage: [u8; 16]| {
        lineage_layers
            .binary_search_by_key(&lineage, |(candidate, _)| *candidate)
            .ok()
            .map(|index| lineage_layers[index].1)
    };
    current_frontier
        .iter()
        .filter_map(|entry| entry.directed_transfer())
        .find(|transfer| {
            (layer_of(transfer.sender) == Some(8)
                && layer_of(transfer.receiver) == Some(10)
                && reached_body_regulation_lineages.contains(&transfer.sender))
                || (layer_of(transfer.sender) == Some(10)
                    && layer_of(transfer.receiver) == Some(8)
                    && reached_body_regulation_lineages.contains(&transfer.receiver))
        })
        .into_iter()
        .collect()
}

fn ordered_path_relations_for_relation(
    incidence: &[([u8; 16], usize)],
    relation_members: &[usize],
    oldest_frontier: &[ActiveElectricalFrontierEntry],
    older_frontier: &[ActiveElectricalFrontierEntry],
    preceding_frontier: &[ActiveElectricalFrontierEntry],
    current_frontier: &[ActiveElectricalFrontierEntry],
) -> Vec<OrderedPathRelationObservation> {
    let first_paths = ordered_physical_paths_for_relation(
        incidence,
        relation_members,
        oldest_frontier,
        older_frontier,
    );
    let second_paths = ordered_physical_paths_for_relation(
        incidence,
        relation_members,
        preceding_frontier,
        current_frontier,
    );
    let mut relations = Vec::new();
    for first_path in &first_paths {
        for second_path in &second_paths {
            if !first_path.same_directed_route(second_path) {
                continue;
            }
            relations.push(OrderedPathRelationObservation {
                earlier_first: first_path.first,
                earlier_second: first_path.second,
                current_first: second_path.first,
                current_second: second_path.second,
            });
        }
    }
    relations.sort_unstable();
    relations.dedup();
    relations
}

/// Observe only the connected physical frontier among currently reached
/// recurrent mosaics, requiring at least one mosaic to have reassembled in
/// this transition. The temporary component indices organize this calculation
/// only; they are never encoded, retained, or used as cognitive authority.
fn observe_organic_mosaic_relations(
    topology: &OrganismMosaicTopology,
    mosaics: &[RetainedOrganismMosaic],
    frontier_indices: &[usize],
    reassembled_indices: &[usize],
    active_bonds: &[StablePhysicalBondReference],
    oldest_frontier: &[ActiveElectricalFrontierEntry],
    older_frontier: &[ActiveElectricalFrontierEntry],
    predecessor_frontier: &[ActiveElectricalFrontierEntry],
    current_frontier: &[ActiveElectricalFrontierEntry],
    max_encoded_bytes: usize,
) -> Result<Vec<OrganicMosaicRelationObservation>, FormationError> {
    if frontier_indices.len() < 2 || reassembled_indices.is_empty() {
        return Ok(Vec::new());
    }
    let mut incidence = Vec::<([u8; 16], usize)>::new();
    for (local_index, mosaic_index) in frontier_indices.iter().copied().enumerate() {
        for lineage in mosaics[mosaic_index].mosaic.member_lineages() {
            incidence.push((*lineage, local_index));
        }
    }
    incidence.sort_unstable();
    incidence.dedup();

    let participants_for_lineage = |lineage: &[u8; 16]| -> Vec<usize> {
        incidence
            .iter()
            .filter_map(|(candidate, participant)| (candidate == lineage).then_some(*participant))
            .collect()
    };

    let mut component_roots = (0..frontier_indices.len()).collect::<Vec<_>>();
    let mut cursor = 0usize;
    while cursor < incidence.len() {
        let lineage = incidence[cursor].0;
        let start = cursor;
        while cursor < incidence.len() && incidence[cursor].0 == lineage {
            cursor += 1;
        }
        if cursor - start >= 2 {
            let first = incidence[start].1;
            for (_, participant) in &incidence[start + 1..cursor] {
                merge_relation_components(&mut component_roots, first, *participant);
            }
        }
    }
    for bond in active_bonds {
        let (left, right) = bond.endpoints();
        let mut participants = participants_for_lineage(&left);
        participants.extend(participants_for_lineage(&right));
        participants.sort_unstable();
        participants.dedup();
        if let Some(first) = participants.first().copied() {
            for participant in participants.iter().copied().skip(1) {
                merge_relation_components(&mut component_roots, first, participant);
            }
        }
    }

    let mut relations = Vec::new();
    for root in 0..frontier_indices.len() {
        let members = component_roots
            .iter()
            .enumerate()
            .filter_map(|(index, component_root)| (*component_root == root).then_some(index))
            .collect::<Vec<_>>();
        if members.len() < 2 {
            continue;
        }
        if !members
            .iter()
            .any(|local_index| reassembled_indices.contains(&frontier_indices[*local_index]))
        {
            continue;
        }
        let mut formation_receipts = members
            .iter()
            .map(|local_index| {
                let retained = &mosaics[frontier_indices[*local_index]].mosaic;
                encode_admitted_physical_mosaic_for_topology(
                    &topology.lineages,
                    &topology.bonds,
                    &topology.fractal_anatomies,
                    retained,
                    max_encoded_bytes,
                )
                .map(|encoded| sha256(&encoded))
                .map_err(FormationError::PhysicalMosaicCodecUnavailable)
            })
            .collect::<Result<Vec<_>, _>>()?;
        formation_receipts.sort_unstable();
        formation_receipts.dedup();
        if formation_receipts.len() < 2 {
            continue;
        }
        let mut shared_lineages = Vec::new();
        let mut lineage_cursor = 0usize;
        while lineage_cursor < incidence.len() {
            let lineage = incidence[lineage_cursor].0;
            let start = lineage_cursor;
            while lineage_cursor < incidence.len() && incidence[lineage_cursor].0 == lineage {
                lineage_cursor += 1;
            }
            let member_count = incidence[start..lineage_cursor]
                .iter()
                .filter(|(_, participant)| members.binary_search(participant).is_ok())
                .count();
            if member_count >= 2 {
                shared_lineages.push(lineage);
            }
        }
        let mut bridging_bonds = active_bonds
            .iter()
            .copied()
            .filter(|bond| {
                let (left, right) = bond.endpoints();
                let mut participants = participants_for_lineage(&left);
                participants.extend(participants_for_lineage(&right));
                participants.sort_unstable();
                participants.dedup();
                participants
                    .iter()
                    .filter(|participant| members.binary_search(participant).is_ok())
                    .count()
                    >= 2
            })
            .collect::<Vec<_>>();
        bridging_bonds.sort_unstable();
        bridging_bonds.dedup();
        if shared_lineages.is_empty() && bridging_bonds.is_empty() {
            continue;
        }
        let structural_relation_receipt = structural_relation_receipt(
            mosaics,
            frontier_indices,
            &members,
            &shared_lineages,
            &bridging_bonds,
        );
        let ordered_physical_paths = ordered_physical_paths_for_relation(
            &incidence,
            &members,
            predecessor_frontier,
            current_frontier,
        );
        let ordered_path_relations = ordered_path_relations_for_relation(
            &incidence,
            &members,
            oldest_frontier,
            older_frontier,
            predecessor_frontier,
            current_frontier,
        );
        relations.push(OrganicMosaicRelationObservation {
            formation_receipts,
            shared_lineages,
            active_bonds: bridging_bonds,
            structural_relation_receipt,
            ordered_physical_paths,
            ordered_path_relations,
        });
    }
    relations.sort_by(|left, right| left.formation_receipts.cmp(&right.formation_receipts));
    Ok(relations)
}

fn external_reassembly_reaches_recurrent_frontier(
    cue: &[[u8; 16]],
    recurrent_lineage: [u8; 16],
    current_frontier: &[ActiveElectricalFrontierEntry],
) -> bool {
    current_frontier.iter().any(|entry| {
        entry.frontier_lineage() == recurrent_lineage
            && entry.directed_transfer().is_some_and(|transfer| {
                (transfer.sender == recurrent_lineage && cue.contains(&transfer.receiver))
                    || (transfer.receiver == recurrent_lineage && cue.contains(&transfer.sender))
            })
    })
}

fn canonicalize_formation_cue(cue: &mut Vec<[u8; 16]>) {
    cue.sort_unstable();
    cue.dedup();
}

fn settle_organism_mosaic_boundary(
    cohorts: &[ResidentReachedCohort],
    topology_index: &ResidentTopologyIndex,
    emitted_neuron_fractals: &[EmittedNeuronFractal],
    current_physical_deltas: &[([u8; 16], SparsePhysicalStateDelta)],
    externally_reached_lineages: &[[u8; 16]],
    externally_perturbed_lineages: &[[u8; 16]],
    metabolically_perturbed_lineages: &[[u8; 16]],
    active_bonds: &[StablePhysicalBondReference],
    oldest_frontier: &[ActiveElectricalFrontierEntry],
    older_frontier: &[ActiveElectricalFrontierEntry],
    predecessor_frontier: &[ActiveElectricalFrontierEntry],
    current_frontier: &[ActiveElectricalFrontierEntry],
    mosaics: &mut Vec<RetainedOrganismMosaic>,
    max_encoded_bytes: usize,
) -> Result<
    (
        Option<[u8; 32]>,
        usize,
        usize,
        Vec<OrganicMosaicRelationObservation>,
        Vec<InternallyReassembledFormationCueObservation>,
        Vec<ExternallyReassembledFormationFrontierObservation>,
    ),
    FormationError,
> {
    if active_bonds.is_empty() {
        return Ok((None, 0, 0, Vec::new(), Vec::new(), Vec::new()));
    }
    let topology = indexed_organism_mosaic_topology(cohorts, topology_index)?;
    let current_fractals = topology
        .lineages
        .iter()
        .map(|lineage| {
            emitted_neuron_fractals
                .iter()
                .rev()
                .find(|fractal| &fractal.neuron_lineage == lineage)
                .map(|fractal| fractal.delta.clone())
        })
        .collect::<Vec<_>>();
    let mut changed_lineages = topology
        .lineages
        .iter()
        .copied()
        .filter(|lineage| {
            current_physical_deltas
                .binary_search_by_key(lineage, |(candidate, _)| *candidate)
                .is_ok()
        })
        .collect::<Vec<_>>();
    changed_lineages.sort_unstable();
    changed_lineages.dedup();
    let mut receipt = None;
    let mut reassemblies = 0usize;
    let mut internally_simulated_reassemblies = 0usize;
    let mut internally_reassembled_formation_cues = Vec::new();
    let mut externally_reassembled_formation_frontiers = Vec::new();
    let mut current_frontier_indices = Vec::new();
    let mut reassembled_indices = Vec::new();
    for (retained_index, retained) in mosaics.iter_mut().enumerate() {
        if !retained.mosaic.is_original_only()
            && retained
                .mosaic
                .member_lineages()
                .iter()
                .any(|lineage| changed_lineages.binary_search(lineage).is_ok())
            && active_bonds.iter().any(|bond| {
                let (left, right) = bond.endpoints();
                retained
                    .mosaic
                    .member_lineages()
                    .binary_search(&left)
                    .is_ok()
                    || retained
                        .mosaic
                        .member_lineages()
                        .binary_search(&right)
                        .is_ok()
            })
        {
            current_frontier_indices.push(retained_index);
        }
        let mut external_cue = externally_reached_lineages
            .iter()
            .copied()
            .filter(|lineage| externally_perturbed_lineages.contains(lineage))
            .filter(|lineage| {
                retained
                    .mosaic
                    .member_lineages()
                    .binary_search(lineage)
                    .is_ok()
            })
            .collect::<Vec<_>>();
        canonicalize_formation_cue(&mut external_cue);
        // Provenance is formation-local. An external perturbation elsewhere
        // in the continuously sensed organism cannot erase this formation's
        // independently measured metabolic cue. If this same formation also
        // carries an external cue, the external branch below remains the
        // conservative authority; no mixed activity is relabelled internal.
        let mut internal_cue = metabolically_perturbed_lineages
            .iter()
            .copied()
            .filter(|lineage| {
                retained
                    .mosaic
                    .member_lineages()
                    .binary_search(lineage)
                    .is_ok()
            })
            .collect::<Vec<_>>();
        canonicalize_formation_cue(&mut internal_cue);
        let (cue, origin) = if !external_cue.is_empty() {
            (external_cue, PhysicalMosaicRecurrenceOrigin::ExternallyObserved)
        } else if !internal_cue.is_empty() {
            (internal_cue, PhysicalMosaicRecurrenceOrigin::InternallySimulated)
        } else {
            continue;
        };
        let reassembled = match if retained.mosaic.is_original_only() {
            prove_physical_mosaic_recurrence_with_origin(
                &retained.mosaic,
                &changed_lineages,
                active_bonds,
                &cue,
                origin,
            )
        } else {
            alter_physical_mosaic_recurrence_with_origin(
                &retained.mosaic,
                &changed_lineages,
                active_bonds,
                &cue,
                origin,
            )
        } {
            Ok(reassembled) => reassembled,
            Err(PhysicalMosaicError::RecurrenceDidNotAlterFormation) => {
                reassembled_indices.push(retained_index);
                reassemblies = reassemblies
                    .checked_add(1)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                if origin == PhysicalMosaicRecurrenceOrigin::InternallySimulated {
                    internally_simulated_reassemblies = internally_simulated_reassemblies
                        .checked_add(1)
                        .ok_or(FormationError::ArithmeticOverflow)?;
                    let encoded = encode_admitted_physical_mosaic_for_topology(
                        &topology.lineages,
                        &topology.bonds,
                        &topology.fractal_anatomies,
                        &retained.mosaic,
                        max_encoded_bytes,
                    )
                    .map_err(FormationError::PhysicalMosaicCodecUnavailable)?;
                    internally_reassembled_formation_cues.push(
                        InternallyReassembledFormationCueObservation {
                            formation_receipt: sha256(&encoded),
                            cue_lineages: cue,
                            recurrent_lineage: retained.recurrent_lineage,
                        },
                    );
                } else if let Some(recurrent_lineage) = retained.recurrent_lineage {
                    if external_reassembly_reaches_recurrent_frontier(
                        &cue,
                        recurrent_lineage,
                        current_frontier,
                    ) {
                        let encoded = encode_admitted_physical_mosaic_for_topology(
                            &topology.lineages,
                            &topology.bonds,
                            &topology.fractal_anatomies,
                            &retained.mosaic,
                            max_encoded_bytes,
                        )
                        .map_err(FormationError::PhysicalMosaicCodecUnavailable)?;
                        externally_reassembled_formation_frontiers.push(
                            ExternallyReassembledFormationFrontierObservation {
                                formation_receipt: sha256(&encoded),
                                cue_lineages: cue,
                                recurrent_lineage,
                            },
                        );
                    }
                }
                continue;
            }
            Err(error) if physical_mosaic_non_admission(error) => continue,
            Err(error) => return Err(FormationError::PhysicalMosaicUnavailable(error)),
        };
        let encoded = encode_admitted_physical_mosaic_for_topology(
            &topology.lineages,
            &topology.bonds,
            &topology.fractal_anatomies,
            &reassembled,
            max_encoded_bytes,
        )
        .map_err(FormationError::PhysicalMosaicCodecUnavailable)?;
        let reassembled_receipt = sha256(&encoded);
        receipt = Some(reassembled_receipt);
        retained.mosaic = reassembled;
        if !current_frontier_indices.contains(&retained_index) {
            current_frontier_indices.push(retained_index);
        }
        reassembled_indices.push(retained_index);
        reassemblies = reassemblies
            .checked_add(1)
            .ok_or(FormationError::ArithmeticOverflow)?;
        if origin == PhysicalMosaicRecurrenceOrigin::InternallySimulated {
            internally_simulated_reassemblies = internally_simulated_reassemblies
                .checked_add(1)
                .ok_or(FormationError::ArithmeticOverflow)?;
            internally_reassembled_formation_cues.push(
                InternallyReassembledFormationCueObservation {
                    formation_receipt: reassembled_receipt,
                    cue_lineages: cue,
                    recurrent_lineage: retained.recurrent_lineage,
                },
            );
        } else if let Some(recurrent_lineage) = retained.recurrent_lineage {
            if external_reassembly_reaches_recurrent_frontier(
                &cue,
                recurrent_lineage,
                current_frontier,
            ) {
                externally_reassembled_formation_frontiers.push(
                    ExternallyReassembledFormationFrontierObservation {
                        formation_receipt: reassembled_receipt,
                        cue_lineages: cue,
                        recurrent_lineage,
                    },
                );
            }
        }
    }
    let organic_relations = observe_organic_mosaic_relations(
        &topology,
        mosaics,
        &current_frontier_indices,
        &reassembled_indices,
        active_bonds,
        oldest_frontier,
        older_frontier,
        predecessor_frontier,
        current_frontier,
        max_encoded_bytes,
    )?;
    let changed = changed_lineages.clone();
    let mut unvisited = topology.lineages.clone();
    while let Some(start) = unvisited.pop() {
        let mut component = vec![start];
        let mut cursor = 0usize;
        while cursor < component.len() {
            let current = component[cursor];
            for bond in active_bonds {
                let (left, right) = bond.endpoints();
                let neighbour = if left == current {
                    Some(right)
                } else if right == current {
                    Some(left)
                } else {
                    None
                };
                if let Some(neighbour) = neighbour {
                    if topology.lineages.contains(&neighbour) && !component.contains(&neighbour) {
                        component.push(neighbour);
                        if let Some(index) = unvisited.iter().position(|value| value == &neighbour)
                        {
                            unvisited.swap_remove(index);
                        }
                    }
                }
            }
            cursor += 1;
        }
        let fractal_members = component
                    .iter()
            .copied()
            .filter(|lineage| changed.contains(lineage))
            .collect::<Vec<_>>();
        if fractal_members.len() < 3 {
            continue;
        }
        let component_fractals = topology
            .lineages
            .iter()
            .zip(current_fractals.iter())
            .map(|(lineage, fractal)| {
                component
                    .contains(lineage)
                    .then(|| fractal.clone())
                    .flatten()
            })
            .collect::<Vec<_>>();
        let original = match admit_physical_mosaic_original(
            &topology.lineages,
            &topology.fractal_anatomies,
            &component_fractals,
            active_bonds,
        ) {
            Ok(original) => original,
            Err(error) if physical_mosaic_non_admission(error) => continue,
            Err(error) => return Err(FormationError::PhysicalMosaicUnavailable(error)),
        };
        if !mosaic_spans_multiple_cohorts(cohorts, &original) {
            continue;
        }
        if mosaics
            .iter()
            .any(|prior| prior.mosaic.same_retained_structure(&original))
        {
            continue;
        }
        mosaics
            .try_reserve(1)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        mosaics.push(RetainedOrganismMosaic::newly_admitted(original));
    }
    Ok((
        receipt,
        reassemblies,
        internally_simulated_reassemblies,
        organic_relations,
        internally_reassembled_formation_cues,
        externally_reassembled_formation_frontiers,
    ))
}

/// Encode one retained mosaic reference for the organism state body.
/// Historical entries without a recurrent cell keep their byte-exact bare or
/// `GLMRC01` layouts. Once a layer-9 endpoint exists, `GLMRC02` persists it
/// beside the counts and the unchanged admitted-mosaic body.
fn encode_retained_organism_mosaic(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
    retained: &RetainedOrganismMosaic,
    max_encoded_bytes: usize,
) -> Result<Vec<u8>, FormationError> {
    let body = encode_organism_mosaic(
        cohorts,
        electrical_fabric,
        &retained.mosaic,
        max_encoded_bytes,
    )?;
    if let Some(recurrent_lineage) = retained.recurrent_lineage {
        validate_recurrent_retention_lineage(
            cohorts,
            electrical_fabric,
            retained.mosaic.member_lineages(),
            recurrent_lineage,
        )?;
        let mut encoded = Vec::new();
        encoded
            .try_reserve_exact(
                RETAINED_MOSAIC_RECURRENT_MAGIC
                    .len()
                    .checked_add(32)
                    .and_then(|value| value.checked_add(body.len()))
                    .ok_or(FormationError::ArithmeticOverflow)?,
            )
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        encoded.extend_from_slice(RETAINED_MOSAIC_RECURRENT_MAGIC);
        encoded.extend_from_slice(&retained.reinforcement_count.to_le_bytes());
        encoded.extend_from_slice(&retained.mosaic_of_mosaics_relation_count.to_le_bytes());
        encoded.extend_from_slice(&recurrent_lineage);
        encoded.extend_from_slice(&body);
        return Ok(encoded);
    }
    if retained.reinforcement_count == 0 && retained.mosaic_of_mosaics_relation_count == 0 {
        return Ok(body);
    }
    let mut encoded = Vec::new();
    encoded
        .try_reserve_exact(
            RETAINED_MOSAIC_COUNTS_MAGIC
                .len()
                .checked_add(16)
                .and_then(|value| value.checked_add(body.len()))
                .ok_or(FormationError::ArithmeticOverflow)?,
        )
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    encoded.extend_from_slice(RETAINED_MOSAIC_COUNTS_MAGIC);
    encoded.extend_from_slice(&retained.reinforcement_count.to_le_bytes());
    encoded.extend_from_slice(&retained.mosaic_of_mosaics_relation_count.to_le_bytes());
    encoded.extend_from_slice(&body);
    Ok(encoded)
}

/// Decode bare legacy, `GLMRC01`, or current `GLMRC02` retained mosaics.
fn decode_retained_organism_mosaic(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
    encoded: &[u8],
    max_encoded_bytes: usize,
) -> Result<RetainedOrganismMosaic, FormationError> {
    if encoded.get(..RETAINED_MOSAIC_RECURRENT_MAGIC.len())
        == Some(RETAINED_MOSAIC_RECURRENT_MAGIC)
    {
        let mut cursor = RETAINED_MOSAIC_RECURRENT_MAGIC.len();
        let reinforcement_count = take_state_u64(encoded, &mut cursor)?;
        let mosaic_of_mosaics_relation_count = take_state_u64(encoded, &mut cursor)?;
        let lineage_end = cursor
            .checked_add(16)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let recurrent_lineage = encoded
            .get(cursor..lineage_end)
            .ok_or(FormationError::NoncanonicalState)?
            .try_into()
            .map_err(|_| FormationError::NoncanonicalState)?;
        cursor = lineage_end;
        let mosaic = decode_organism_mosaic(
            cohorts,
            electrical_fabric,
            encoded
                .get(cursor..)
                .ok_or(FormationError::NoncanonicalState)?,
            max_encoded_bytes,
        )?;
        validate_recurrent_retention_lineage(
            cohorts,
            electrical_fabric,
            mosaic.member_lineages(),
            recurrent_lineage,
        )?;
        return Ok(RetainedOrganismMosaic {
            mosaic,
            recurrent_lineage: Some(recurrent_lineage),
            reinforcement_count,
            mosaic_of_mosaics_relation_count,
        });
    }
    if encoded.get(..RETAINED_MOSAIC_COUNTS_MAGIC.len()) != Some(RETAINED_MOSAIC_COUNTS_MAGIC) {
        let mosaic =
            decode_organism_mosaic(cohorts, electrical_fabric, encoded, max_encoded_bytes)?;
        return Ok(RetainedOrganismMosaic {
            mosaic,
            recurrent_lineage: None,
            reinforcement_count: 0,
            mosaic_of_mosaics_relation_count: 0,
        });
    }
    let mut cursor = RETAINED_MOSAIC_COUNTS_MAGIC.len();
    let reinforcement_count = take_state_u64(encoded, &mut cursor)?;
    let mosaic_of_mosaics_relation_count = take_state_u64(encoded, &mut cursor)?;
    if reinforcement_count == 0 && mosaic_of_mosaics_relation_count == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    let mosaic = decode_organism_mosaic(
        cohorts,
        electrical_fabric,
        encoded
            .get(cursor..)
            .ok_or(FormationError::NoncanonicalState)?,
        max_encoded_bytes,
    )?;
    Ok(RetainedOrganismMosaic {
        mosaic,
        recurrent_lineage: None,
        reinforcement_count,
        mosaic_of_mosaics_relation_count,
    })
}

impl ResidentCognitiveFormationState {
    /// Retire the task-955 local-integration projection that equated
    /// sense-local topology indices across unrelated sensory coordinate
    /// systems.  The correction is identified from the persisted anatomy
    /// itself: an intrinsic layer-6 lineage is retired only when a retained
    /// fabric contact joins it to a receptor whose injective declared-place
    /// projection names a different layer-6 place.
    ///
    /// Receptor neurons, their lineages, physical state, local fluids, and all
    /// unrelated contacts remain exact.  The falsely reached intrinsic cells
    /// and any formations containing them are not preserved as learning; their
    /// claimed places return to the compact quiescent population.
    fn retire_aliased_local_integrators(&self) -> Result<Option<Self>, FormationError> {
        let mut receptors = std::collections::BTreeMap::<[u8; 16], DeclaredNeuronPlace>::new();
        let mut intrinsic = std::collections::BTreeMap::<[u8; 16], DeclaredNeuronPlace>::new();
        for (mount, lineage) in self.cohorts.iter().flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        }) {
            let place = mount.place();
            let prior = if mount.source_site().is_some() {
                receptors.insert(*lineage, place)
            } else if place.layer() == 6 {
                intrinsic.insert(*lineage, place)
            } else {
                None
            };
            if prior.is_some() {
                return Err(FormationError::NeuronLineageAuthorityChanged);
            }
        }

        let mut retired = Vec::<[u8; 16]>::new();
        for (left, right) in self.electrical_fabric.contact_endpoints() {
            let left_lineage = self.electrical_fabric.lineages()[left];
            let right_lineage = self.electrical_fabric.lineages()[right];
            let reached = receptors
                .get(&left_lineage)
                .map(|place| (right_lineage, *place))
                .or_else(|| {
                    receptors
                        .get(&right_lineage)
                        .map(|place| (left_lineage, *place))
                });
            let Some((target_lineage, receptor_place)) = reached else {
                continue;
            };
            let Some(target_place) = intrinsic.get(&target_lineage) else {
                continue;
            };
            if *target_place != local_integration_place(receptor_place)?
                && !retired.contains(&target_lineage)
            {
                retired.push(target_lineage);
            }
        }
        if retired.is_empty() {
            return Ok(None);
        }

        let mut retired_places = Vec::new();
        let mut cohorts = Vec::with_capacity(self.cohorts.len());
        for cohort in self.cohorts.iter() {
            let retired_members = cohort
                .anatomy
                .neuron_lineages()
                .iter()
                .filter(|lineage| retired.contains(lineage))
                .count();
            if retired_members == 0 {
                cohorts.push(cohort.clone());
                continue;
            }
            if retired_members != cohort.anatomy.neuron_count()
                || cohort.anatomy.neuron_count() != 1
                || cohort.anatomy.mounts()[0].source_site().is_some()
                || cohort.anatomy.mounts()[0].place().layer() != 6
            {
                return Err(FormationError::NeuronLineageAuthorityChanged);
            }
            retired_places.push(cohort.anatomy.mounts()[0].place());
        }

        let mut resting_population = self.resting_population.clone();
        for place in retired_places {
            let Some(population) = resting_population.as_ref() else {
                continue;
            };
            if population.materialized_lineage_ordinal(place).is_none() {
                continue;
            }
            resting_population = Some(
                population
                    .release_claimed_place(place)
                    .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?,
            );
        }
        let mosaics = self
            .mosaics
            .iter()
            .filter(|retained| {
                !retained
                    .mosaic
                    .member_lineages()
                    .iter()
                    .any(|lineage| retired.contains(lineage))
            })
            .cloned()
            .collect::<Vec<_>>();
        let mut successor = Self {
            generation: self.generation,
            next_lineage_ordinal: self.next_lineage_ordinal,
            unexpressed_electrical_seeds: self.unexpressed_electrical_seeds.clone(),
            dormant_lineage_seeds: self.dormant_lineage_seeds.clone(),
            resting_population,
            cohorts: cohorts.into_boxed_slice(),
            electrical_fabric: self
                .electrical_fabric
                .without_lineages(&retired)
                .map_err(FormationError::ResidentElectricalUnavailable)?,
            active_electrical_frontier: self
                .active_electrical_frontier
                .iter()
                .copied()
                .filter(|entry| !retired.contains(&entry.receiver()))
                .collect::<Vec<_>>()
                .into_boxed_slice(),
            preceding_active_electrical_frontier: self
                .preceding_active_electrical_frontier
                .iter()
                .copied()
                .filter(|entry| !retired.contains(&entry.receiver()))
                .collect::<Vec<_>>()
                .into_boxed_slice(),
            older_active_electrical_frontier: self
                .older_active_electrical_frontier
                .iter()
                .copied()
                .filter(|entry| !retired.contains(&entry.receiver()))
                .collect::<Vec<_>>()
                .into_boxed_slice(),
            mosaics: mosaics.into_boxed_slice(),
            hippocampal: self.hippocampal,
            topology_index: self.topology_index.clone(),
        };
        successor.topology_index = Arc::new(ResidentTopologyIndex::build(
            &successor.cohorts,
            &successor.electrical_fabric,
        )?);
        validate_lineage_state(&successor)?;
        Ok(Some(successor))
    }

    /// Make every already-declared receptor territory explicit once for bodies
    /// written by the aggregate one-channel implementation. This is a
    /// representation correction, not neuronal growth: stable lineage,
    /// source place, contacts, existing material state, generation and
    /// identity all remain attached. Cognitive formations authored by the
    /// replaced aggregate/self-tail law are deliberately retired rather than
    /// reintroduced as learned authority under the corrected physics.
    fn expand_legacy_receptor_channel_populations(&self) -> Result<Self, FormationError> {
        let mut populations_by_lineage = Vec::new();
        let mut cohorts = Vec::with_capacity(self.cohorts.len());
        for cohort in self.cohorts.iter() {
            let (anatomy, state) = expand_reached_receptor_channel_populations(
                &cohort.anatomy,
                &cohort.state,
                definitive_virtual_carriers_per_compartment(),
            )
            .map_err(FormationError::PhysicalSettlementUnavailable)?;
            if anatomy == cohort.anatomy {
                cohorts.push(cohort.clone());
                continue;
            }
            for ((lineage, mount), neuron) in anatomy
                .neuron_lineages()
                .iter()
                .zip(anatomy.mounts())
                .zip(anatomy.neuron_anatomies())
            {
                if mount.source_site().is_none() {
                    continue;
                }
                    let population = usize::try_from(neuron.gate_population())
                        .map_err(|_| FormationError::ArithmeticOverflow)?;
                    if population > 1 {
                        populations_by_lineage.push((*lineage, population));
                    }
            }
            cohorts.push(ResidentReachedCohort {
                anatomy,
                state: state.into(),
                pending_experience: None,
                retained_experience: None,
                pending_recurrence: None,
            });
        }
        if populations_by_lineage.is_empty() {
            return Ok(self.clone());
        }
        for cohort in &mut cohorts {
            cohort.pending_experience = None;
            cohort.retained_experience = None;
            cohort.pending_recurrence = None;
        }
        let successor = Self {
            generation: self.generation,
            next_lineage_ordinal: self.next_lineage_ordinal,
            unexpressed_electrical_seeds: self.unexpressed_electrical_seeds.clone(),
            dormant_lineage_seeds: self.dormant_lineage_seeds.clone(),
            resting_population: self.resting_population.clone(),
            cohorts: cohorts.into_boxed_slice(),
            electrical_fabric: self.electrical_fabric.clone(),
            active_electrical_frontier: Box::new([]),
            preceding_active_electrical_frontier: Box::new([]),
            older_active_electrical_frontier: Box::new([]),
            mosaics: Box::new([]),
            hippocampal: ResidentHippocampalIndex::default(),
            topology_index: self.topology_index.clone(),
        };
        validate_lineage_state(&successor)?;
        Ok(successor)
    }

    /// Carry an already-current body through the retired representation gate
    /// without cloning every reached neuron merely to rediscover that no
    /// migration applies. Historical bodies still take the exact correction
    /// above; current bodies retain the owned state byte-for-byte.
    fn into_expanded_legacy_receptor_channel_populations(self) -> Result<Self, FormationError> {
        let mut required = false;
        for cohort in self.cohorts.iter() {
            if legacy_receptor_channel_populations_require_expansion(&cohort.anatomy, &cohort.state)
                .map_err(FormationError::PhysicalSettlementUnavailable)?
            {
                required = true;
                break;
            }
        }
        if !required {
            return Ok(self);
        }
        self.expand_legacy_receptor_channel_populations()
    }

    /// Correct the historical birth-law omission carried by every pre-V18
    /// body: non-retinal and intrinsic cells received one unit patch of mobile
    /// material even though their authored membrane capacitance spans their
    /// full declared territory. Current genesis supplies one femtocoulomb per
    /// unit patch. The V18 codec marker is the one-way authority: pre-V18
    /// bodies receive each cell's never-lived virgin difference once, while a
    /// V18 body is never corrected again.
    fn into_geometry_provisioned_carrier_material(self) -> Result<Self, FormationError> {
        let base = definitive_virtual_carriers_per_compartment();
        let mut changed = false;
        let mut cohorts = Vec::with_capacity(self.cohorts.len());
        for cohort in self.cohorts.iter() {
            let additions = cohort
                .anatomy
                .neuron_anatomies()
                .iter()
                .zip(cohort.anatomy.mounts())
                .map(|(anatomy, mount)| {
                    declared_neuron_territory(mount.place())
                        .map_err(|_| FormationError::ArithmeticOverflow)?
                        .max(anatomy.gate_population())
                        .checked_sub(anatomy.gate_population())
                        .and_then(|units| units.checked_mul(base))
                        .ok_or(FormationError::ArithmeticOverflow)
                })
                .collect::<Result<Vec<_>, _>>()?;
            let cohort_changed = additions.iter().any(|addition| *addition != 0);
            changed |= cohort_changed;
            if !cohort_changed {
                cohorts.push(cohort.clone());
                continue;
            }
            let correct_state = |state: &ReachedCohortState| {
                add_omitted_geometry_carrier_material(&cohort.anatomy, state, &additions)
                .map_err(FormationError::PhysicalSettlementUnavailable)
            };
            let correct_evidence = |evidence: &ResidentExperienceEvidence| {
                let mut corrected = evidence.clone();
                corrected.physical = match &evidence.physical {
                    ResidentExperiencePhysicalEvidence::Legacy {
                        predecessor,
                        successor,
                    } => ResidentExperiencePhysicalEvidence::Legacy {
                        predecessor: correct_state(predecessor)?.into(),
                        successor: successor
                            .as_ref()
                            .map(|state| correct_state(state).map(Arc::new))
                            .transpose()?,
                    },
                    ResidentExperiencePhysicalEvidence::Pending(members) => {
                        let corrected = members
                            .iter()
                            .map(|member| {
                                let addition = *additions
                                    .get(member.neuron_index)
                                    .ok_or(FormationError::NoncanonicalState)?;
                                let predecessor = add_omitted_virgin_carrier_material(
                                    &member.predecessor,
                                    addition,
                                )
                                .map_err(|error| {
                                    FormationError::PhysicalSettlementUnavailable(
                                        ReachedCohortError::Neuron {
                                            neuron_index: member.neuron_index,
                                            error,
                                        },
                                    )
                                })?;
                                Ok(SparsePendingExperienceMember {
                                    neuron_index: member.neuron_index,
                                    predecessor,
                                    settled: member.settled,
                                })
                            })
                            .collect::<Result<Vec<_>, FormationError>>()?;
                        ResidentExperiencePhysicalEvidence::Pending(
                            corrected.into_boxed_slice(),
                        )
                    }
                    ResidentExperiencePhysicalEvidence::Retained(members) => {
                        let corrected = members
                            .iter()
                            .map(|member| {
                                let addition = *additions
                                    .get(member.neuron_index)
                                    .ok_or(FormationError::NoncanonicalState)?;
                                let predecessor = add_omitted_virgin_carrier_material(
                                    &member.predecessor,
                                    addition,
                                )
                                .map_err(|error| {
                                    FormationError::PhysicalSettlementUnavailable(
                                        ReachedCohortError::Neuron {
                                            neuron_index: member.neuron_index,
                                            error,
                                        },
                                    )
                                })?;
                                let learned = add_omitted_virgin_carrier_material(
                                    &member.learned,
                                    addition,
                                )
                                .map_err(|error| {
                                    FormationError::PhysicalSettlementUnavailable(
                                        ReachedCohortError::Neuron {
                                            neuron_index: member.neuron_index,
                                            error,
                                        },
                                    )
                                })?;
                                let delta = sparse_retained_physical_state_delta(
                                    &predecessor,
                                    &learned,
                                )
                                .map_err(|error| {
                                    FormationError::PhysicalSettlementUnavailable(
                                        ReachedCohortError::Neuron {
                                            neuron_index: member.neuron_index,
                                            error,
                                        },
                                    )
                                })?
                                .ok_or(FormationError::NoncanonicalState)?;
                                Ok(SparseRetainedExperienceMember {
                                    neuron_index: member.neuron_index,
                                    predecessor,
                                    learned,
                                    delta,
                                })
                            })
                            .collect::<Result<Vec<_>, FormationError>>()?;
                        ResidentExperiencePhysicalEvidence::Retained(
                            corrected.into_boxed_slice(),
                        )
                    }
                };
                Ok::<_, FormationError>(corrected)
            };
            cohorts.push(ResidentReachedCohort {
                anatomy: cohort.anatomy.clone(),
                state: correct_state(&cohort.state)?.into(),
                // Adding the same omitted virgin material to both endpoints
                // preserves every lived physical delta and every causal flag.
                pending_experience: cohort
                    .pending_experience
                    .as_ref()
                    .map(&correct_evidence)
                    .transpose()?,
                retained_experience: cohort
                    .retained_experience
                    .as_ref()
                    .map(&correct_evidence)
                    .transpose()?,
                pending_recurrence: cohort.pending_recurrence.clone(),
            });
        }
        if !changed {
            return Ok(self);
        }
        let successor = Self {
            cohorts: cohorts.into_boxed_slice(),
            ..self
        };
        validate_lineage_state(&successor)?;
        Ok(successor)
    }

    pub(crate) fn from_developmental_electrical_seeds(
        seeds: Vec<DevelopmentalElectricalSeed>,
    ) -> Result<Self, FormationError> {
        Self::from_genesis_parts(0, 1, seeds, Vec::new())
    }

    pub(crate) fn from_genesis_parts(
        generation: u64,
        next_lineage_ordinal: u64,
        seeds: Vec<DevelopmentalElectricalSeed>,
        mut dormant_lineage_seeds: Vec<DormantLineageSeed>,
    ) -> Result<Self, FormationError> {
        if seeds.iter().enumerate().any(|(index, seed)| {
            seeds[..index]
                .iter()
                .any(|prior| prior.source_sites() == seed.source_sites())
        }) {
            return Err(FormationError::DuplicateDevelopmentalSeed);
        }
        dormant_lineage_seeds.sort();
        if dormant_lineage_seeds
            .iter()
            .enumerate()
            .any(|(index, seed)| {
                seed.validate().is_err()
                    || dormant_lineage_seeds[..index].iter().any(|prior| {
                        prior.same_source(seed) || prior.neuron_lineage == seed.neuron_lineage
                    })
            })
        {
            return Err(FormationError::NoncanonicalState);
        }
        let state = Self {
            generation,
            next_lineage_ordinal,
            unexpressed_electrical_seeds: seeds.into_boxed_slice(),
            dormant_lineage_seeds: dormant_lineage_seeds.into_boxed_slice(),
            resting_population: None,
            cohorts: Box::new([]),
            electrical_fabric: ResidentElectricalFabric::default(),
            active_electrical_frontier: Box::new([]),
            preceding_active_electrical_frontier: Box::new([]),
            older_active_electrical_frontier: Box::new([]),
            mosaics: Box::new([]),
            hippocampal: ResidentHippocampalIndex::default(),
            topology_index: Arc::new(ResidentTopologyIndex::empty()),
        };
        validate_lineage_state(&state)?;
        Ok(state)
    }

    pub(crate) fn summary(&self) -> CognitiveFormationSummary {
        CognitiveFormationSummary {
            cognitive_ordinal: self.generation,
            trace_count: 0,
            mosaic_count: self
                .mosaics
                .iter()
                .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
                .count(),
            complete_neuron_count: self
                .cohorts
                .iter()
                .map(|cohort| cohort.anatomy.neuron_count())
                .sum(),
            resting_neuron_count: self
                .resting_population
                .as_ref()
                .and_then(|population| usize::try_from(population.resting_cell_count()).ok())
                .unwrap_or(0),
            energy: self.energy_state(),
        }
    }

    /// Structural counts needed while an owned causal trajectory is still
    /// unsealed.  The exact whole-organism energy observation is deliberately
    /// deferred to the single final seal: evaluating it here would walk every
    /// Psi and recovery lane after every internal/body-feedback interval.
    fn unsealed_structural_summary(&self) -> CognitiveFormationSummary {
        CognitiveFormationSummary {
            cognitive_ordinal: self.generation,
            trace_count: 0,
            mosaic_count: self
                .mosaics
                .iter()
                .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
                .count(),
            complete_neuron_count: self
                .cohorts
                .iter()
                .map(|cohort| cohort.anatomy.neuron_count())
                .sum(),
            resting_neuron_count: self
                .resting_population
                .as_ref()
                .and_then(|population| usize::try_from(population.resting_cell_count()).ok())
                .unwrap_or(0),
            energy: ReachedCohortEnergyState::default(),
        }
    }

    /// Read-only structural observation of the retained distributed
    /// formations: one entry per admitted mosaic as the stable member
    /// lineages and the retained recurrence-bond count.  Structure only —
    /// no recognition, recall, meaning, or capital is emitted, and reading
    /// advances nothing.
    pub(crate) fn observe_retained_formation_members(&self) -> Vec<(Vec<[u8; 16]>, usize)> {
        self.mosaics
            .iter()
            .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
            .map(|retained| {
                (
                    retained.mosaic.member_lineages().to_vec(),
                    retained.mosaic.recurrence_bonds().len(),
                )
            })
            .collect()
    }

    /// Read-only exact structural evidence for each retained formation.  The
    /// canonical receipt covers the retained neuronal deltas and both exact
    /// bond witnesses; members and bond endpoints are returned so a caller
    /// need not infer structure from a count.  Observation advances nothing.
    pub(crate) fn observe_retained_formation_structures(
        &self,
        max_encoded_bytes: usize,
    ) -> Result<
        Vec<(
            [u8; 32],
            Vec<[u8; 16]>,
            Vec<StablePhysicalBondReference>,
            Vec<StablePhysicalBondReference>,
            u64,
        )>,
        FormationError,
    > {
        self.mosaics
            .iter()
            .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
            .map(|retained| {
                let encoded = encode_organism_mosaic(
                    &self.cohorts,
                    &self.electrical_fabric,
                    &retained.mosaic,
                    max_encoded_bytes,
                )?;
                Ok((
                    sha256(&encoded),
                    retained.mosaic.member_lineages().to_vec(),
                    retained.mosaic.original_bonds().to_vec(),
                    retained.mosaic.recurrence_bonds().to_vec(),
                    retained.reinforcement_count,
                ))
            })
            .collect()
    }

    /// Read-only proper partial-cue witness for each retained formation,
    /// correlated by the same canonical structure receipt used by the exact
    /// structure observer. The cue is evidence of the latest physical
    /// reassembly; it is not a semantic key and reading advances nothing.
    pub(crate) fn observe_retained_formation_recurrence_cues(
        &self,
        max_encoded_bytes: usize,
    ) -> Result<Vec<([u8; 32], Vec<[u8; 16]>)>, FormationError> {
        self.mosaics
            .iter()
            .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
            .map(|retained| {
                let encoded = encode_organism_mosaic(
                    &self.cohorts,
                    &self.electrical_fabric,
                    &retained.mosaic,
                    max_encoded_bytes,
                )?;
                Ok((
                    sha256(&encoded),
                    retained.mosaic.partial_cue_lineages().to_vec(),
                ))
            })
            .collect()
    }

    /// Read-only latest recurrence evidence with its physical source class.
    /// The origin is retained in the mosaic codec and is therefore cold-state
    /// evidence, not an interpretation added by the observation boundary.
    pub(crate) fn observe_retained_formation_recurrence_evidence(
        &self,
        max_encoded_bytes: usize,
    ) -> Result<Vec<([u8; 32], Vec<[u8; 16]>, &'static str)>, FormationError> {
        self.mosaics
            .iter()
            .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
            .map(|retained| {
                let encoded = encode_organism_mosaic(
                    &self.cohorts,
                    &self.electrical_fabric,
                    &retained.mosaic,
                    max_encoded_bytes,
                )?;
                let origin = retained
                    .mosaic
                    .recurrence_origin()
                    .ok_or(FormationError::PhysicalMosaicUnavailable(
                        PhysicalMosaicError::WidthMismatch,
                    ))?;
                Ok((
                    sha256(&encoded),
                    retained.mosaic.partial_cue_lineages().to_vec(),
                    origin.as_str(),
                ))
            })
            .collect()
    }

    /// Read only current-boundary transfers whose previous endpoint is one of
    /// the supplied lineages. Carrier direction remains independent of the
    /// advancing endpoint. Filtering occurs inside the native body so a
    /// bounded causal observer cannot mistake an arriving transfer for an
    /// onward cause or expand the unrelated reached frontier into Python.
    pub(crate) fn observe_active_electrical_frontier_advances_from(
        &self,
        lineages: &[[u8; 16]],
    ) -> Vec<CausalFrontierTransferObservation> {
        self.active_electrical_frontier
            .iter()
            .filter_map(|entry| {
                let transfer = entry.directed_transfer()?;
                let frontier_lineage = entry.frontier_lineage();
                let predecessor_lineage = if frontier_lineage == transfer.sender {
                    transfer.receiver
                } else if frontier_lineage == transfer.receiver {
                    transfer.sender
                } else {
                    return None;
                };
                lineages.contains(&predecessor_lineage).then_some(
                    CausalFrontierTransferObservation {
                        transfer,
                        frontier_lineage,
                    },
                )
            })
            .collect()
    }

    /// Read every exact transfer on the current sparse electrical frontier.
    ///
    /// This crate-private projection lets the one-seal organism trajectory
    /// preserve each already-reached causal boundary before the next interval
    /// replaces it. It is transient observation only: it neither broadens the
    /// settled frontier nor enters the retained organism codec.
    pub(crate) fn observe_active_electrical_frontier_advances(
        &self,
    ) -> Vec<CausalFrontierTransferObservation> {
        self.active_electrical_frontier
            .iter()
            .filter_map(|entry| {
                Some(CausalFrontierTransferObservation {
                    transfer: entry.directed_transfer()?,
                    frontier_lineage: entry.frontier_lineage(),
                })
            })
            .collect()
    }

    /// Total mosaic-of-mosaics relation events recorded against the retained
    /// formations — the sum of the per-mosaic retained counts (R1 overlap
    /// branch; R3: a count over recorded episodes, never a score).
    pub(crate) fn mosaic_of_mosaics_count(&self) -> Result<usize, FormationError> {
        self.mosaics
            .iter()
            .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
            .try_fold(0usize, |total, retained| {
                usize::try_from(retained.mosaic_of_mosaics_relation_count)
                    .ok()
                    .and_then(|count| total.checked_add(count))
                    .ok_or(FormationError::ArithmeticOverflow)
            })
    }

    /// The body's exact energy state, summed over every mounted cohort: the
    /// recovery-fluid reservoir, the dissipation ledgers, and the separated
    /// membrane charge still standing away from rest.
    pub(crate) fn energy_state(&self) -> ReachedCohortEnergyState {
        let mut total = ReachedCohortEnergyState::default();
        for cohort in &self.cohorts {
            let cohort_energy = reached_cohort_energy_state(&cohort.anatomy, &cohort.state);
            total.available_energy_zeptojoules += cohort_energy.available_energy_zeptojoules;
            total.spent_energy_zeptojoules += cohort_energy.spent_energy_zeptojoules;
            total.thermal_energy_zeptojoules += cohort_energy.thermal_energy_zeptojoules;
            total.available_energy_capacity_zeptojoules +=
                cohort_energy.available_energy_capacity_zeptojoules;
            total.spent_energy_capacity_zeptojoules +=
                cohort_energy.spent_energy_capacity_zeptojoules;
            total.thermal_energy_capacity_zeptojoules +=
                cohort_energy.thermal_energy_capacity_zeptojoules;
            total.dissipated_energy_zeptojoules += cohort_energy.dissipated_energy_zeptojoules;
            total.dissipation_capacity_energy_zeptojoules +=
                cohort_energy.dissipation_capacity_energy_zeptojoules;
            total.separated_elementary_charges = total
                .separated_elementary_charges
                .saturating_add(cohort_energy.separated_elementary_charges);
        }
        total
    }

    #[cfg(test)]
    pub(crate) fn retained_neuron_lineages(&self) -> Vec<[u8; 16]> {
        self.cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.neuron_lineages().iter().copied())
            .collect()
    }

    #[cfg(test)]
    pub(crate) fn retained_electrical_contact_counts(&self) -> Vec<usize> {
        self.cohorts
            .iter()
            .map(|cohort| cohort.anatomy.contact_count())
            .collect()
    }

    #[cfg(test)]
    pub(crate) fn unexpressed_electrical_seed_count(&self) -> usize {
        self.unexpressed_electrical_seeds.len()
    }

    #[cfg(test)]
    pub(crate) fn prepare(
        &self,
        source: &NativeJointSourceEpisode,
        max_encoded_bytes: usize,
    ) -> Result<PreparedCognitiveFormationTransition, FormationError> {
        self.prepare_admitted_transition(&admitted_fixture_episode(source), max_encoded_bytes)
    }

    pub(crate) fn prepare_bare_source(
        &self,
        _source: &NativeJointSourceEpisode,
        _max_encoded_bytes: usize,
    ) -> Result<PreparedCognitiveFormationTransition, FormationError> {
        Err(FormationError::JointFieldUnavailable(
            JointNeuronBoundaryError::Source(JointUfSourceError::Unavailable(
                "explicit admitted joint source episode is required",
            )),
        ))
    }

    pub(crate) fn prepare_admitted_transition(
        &self,
        admitted_source: &AdmittedJointSourceEpisode,
        max_encoded_bytes: usize,
    ) -> Result<PreparedCognitiveFormationTransition, FormationError> {
        self.prepare_typed_admitted_transition(admitted_source, None, max_encoded_bytes)
    }

    pub(crate) fn prepare_vestibular_transition(
        &self,
        ingress: &ResidentVestibularIngress,
        max_encoded_bytes: usize,
    ) -> Result<PreparedCognitiveFormationTransition, FormationError> {
        let (source, contacts) = ingress.source().joint_source_with_contacts();
        if source.joint_source_occurrences().len() != 1 || !contacts.is_empty() {
            return Err(FormationError::VestibularUnavailable(
                FunctionalVestibularError::NotIsolatedSingleVertex,
            ));
        }
        let admission = ingress
            .source()
            .joint_uf_source_admission()
            .map_err(|error| {
                FormationError::JointFieldUnavailable(JointNeuronBoundaryError::Source(error))
            })?;
        let admitted_source = AdmittedJointSourceEpisode::new(source.clone(), vec![(0, admission)])
            .map_err(|error| {
                FormationError::JointFieldUnavailable(JointNeuronBoundaryError::Source(error))
            })?;
        self.prepare_typed_admitted_transition(&admitted_source, Some(ingress), max_encoded_bytes)
    }

    fn prepare_typed_admitted_transition(
        &self,
        admitted_source: &AdmittedJointSourceEpisode,
        vestibular: Option<&ResidentVestibularIngress>,
        max_encoded_bytes: usize,
    ) -> Result<PreparedCognitiveFormationTransition, FormationError> {
        // A current body crosses each historical one-way correction without
        // deep-copying its complete reached population. At most one owned
        // predecessor copy is made here; all current structures then move
        // into the successor under the ordinary transactional prepare.
        let expanded = self
            .retire_aliased_local_integrators()?
            .unwrap_or_else(|| self.clone())
            .into_expanded_legacy_receptor_channel_populations()?;
        Self::prepare_typed_admitted_transition_from_owned(
            expanded,
            self.generation,
            self.hippocampal,
            admitted_source,
            vestibular,
            max_encoded_bytes,
            true,
        )
    }

    fn prepare_typed_admitted_transition_from_owned(
        expanded: Self,
        predecessor_generation_authority: u64,
        predecessor_hippocampal_authority: ResidentHippocampalIndex,
        admitted_source: &AdmittedJointSourceEpisode,
        vestibular: Option<&ResidentVestibularIngress>,
        max_encoded_bytes: usize,
        seal_successor: bool,
    ) -> Result<PreparedCognitiveFormationTransition, FormationError> {
        let Self {
            generation: predecessor_generation,
            next_lineage_ordinal: predecessor_next_lineage_ordinal,
            unexpressed_electrical_seeds: predecessor_unexpressed_electrical_seeds,
            dormant_lineage_seeds: predecessor_dormant_lineage_seeds,
            resting_population: predecessor_resting_population,
            cohorts: predecessor_cohorts,
            electrical_fabric: predecessor_electrical_fabric,
            active_electrical_frontier: predecessor_active_electrical_frontier,
            preceding_active_electrical_frontier: predecessor_preceding_active_electrical_frontier,
            older_active_electrical_frontier: predecessor_older_active_electrical_frontier,
            mosaics: predecessor_mosaics,
            hippocampal: predecessor_hippocampal,
            topology_index: predecessor_topology_index,
        } = expanded;
        let source = admitted_source.episode();
        if source.joint_source_occurrences().is_empty() {
            return Err(FormationError::SourceOccurrenceAbsent);
        }
        let source_generation = predecessor_generation
            .checked_add(1)
            .ok_or(FormationError::InvalidSourceGeneration)?;
        let mut unexpressed_electrical_seeds = predecessor_unexpressed_electrical_seeds.into_vec();
        let mut dormant_lineage_seeds = predecessor_dormant_lineage_seeds.into_vec();
        let mut resting_population = predecessor_resting_population;
        let mut next_lineage_ordinal = predecessor_next_lineage_ordinal;
        let mut cohorts = predecessor_cohorts.into_vec();
        let mut topology_index = predecessor_topology_index;
        // Bodies written before the retained-fractal boundary may still carry
        // transient charge, phase, gate, residue, or metabolic coordinates in
        // a mosaic body.  They remain readable only so the living neuron and
        // retained-experience state can cross the release boundary.  They are
        // not cognitive authority and leave on the next physical transition;
        // a later recurrence must form a new mosaic from retained structure.
        let mut mosaics = predecessor_mosaics
            .into_vec()
            .into_iter()
            .filter(|retained| {
                retained.mosaic.carries_retained_original_structure()
                    && mosaic_spans_multiple_cohorts(&cohorts, &retained.mosaic)
            })
            .collect::<Vec<_>>();
        let predecessor_recognized_mosaics = mosaics
            .iter()
            .filter(|retained| retained.mosaic.carries_only_retained_neuron_structure())
            .map(|retained| retained.mosaic.clone())
            .collect::<Vec<_>>();
        cohorts
            .try_reserve(source.joint_source_occurrences().len())
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let mut physically_transitioned_neuron_lineages = Vec::<[u8; 16]>::new();
        let mut metabolically_perturbed_body_receptor_lineages = Vec::<[u8; 16]>::new();
        let mut localized_metabolic_strain_evaluated_body_receptor_lineages =
            Vec::<[u8; 16]>::new();
        let mut localized_metabolic_strain =
            Vec::<LocalizedMetabolicStrainObservation>::new();
        let mut externally_reached_neuron_lineages = Vec::<[u8; 16]>::new();
        let mut externally_perturbed_neuron_lineages = Vec::<[u8; 16]>::new();
        let mut externally_energized_neuron_lineages = Vec::<[u8; 16]>::new();
        let mut transition_neuron_predecessors = Vec::<TransitionNeuronPredecessor>::new();
        let mut externally_reached_receptor_places = Vec::<([u8; 16], DeclaredNeuronPlace)>::new();
        let mut externally_energized_by_occurrence =
            vec![Vec::<[u8; 16]>::new(); source.joint_source_occurrences().len()];
        let mut emitted_neuron_fractals = Vec::new();
        let mut mosaic_formed = None;
        // The retired archive checkpoint is carried forward VERBATIM: never
        // advanced, never published, never dereferenced.  A body that already
        // holds one keeps the exact 74 bytes it was persisted with, so the
        // receipt of an untouched field cannot drift.
        let hippocampal = predecessor_hippocampal;
        let mut dsf_delivery_count = 0usize;
        let mut partial_cue_reassembly_count = 0usize;
        let mut endogenous_partial_cue_reassembly_count = 0usize;
        let mut metabolic = ReachedCohortMetabolicObservation::default();
        for (occurrence_index, occurrence) in source.joint_source_occurrences().iter().enumerate() {
            #[cfg(test)]
            RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| count.set(count.get() + 1));
            let admission = admitted_source
                .admission(occurrence_index)
                .ok_or(FormationError::NoncanonicalState)?;
            let shared =
                prepare_complete_joint_field_with_admission(source, occurrence_index, admission)
                    .map_err(FormationError::JointFieldUnavailable)?;
            if vestibular.is_some()
                && (occurrence_index != 0
                    || shared.vertex_count() != 1
                    || shared.groups().len() != 1
                    || shared.groups()[0].as_slice() != [0])
            {
                return Err(FormationError::VestibularUnavailable(
                    FunctionalVestibularError::NotIsolatedSingleVertex,
                ));
            }
            dsf_delivery_count = dsf_delivery_count
                .checked_add(shared.vertex_count())
                .ok_or(FormationError::ArithmeticOverflow)?;
            let reached_sources = (0..shared.vertex_count())
                .map(|coordinate_index| {
                    let perspective = bind_neuron_perspective(&shared, coordinate_index, 0)
                        .map_err(FormationError::JointFieldUnavailable)?;
                    let anchor =
                        bind_neuron_source_anchor(source, perspective).map_err(|error| {
                            FormationError::PhysicalGenesisUnavailable(
                                VirtualMaterialGenesisError::Source(error),
                            )
                        })?;
                    let port = source
                        .joint_source_ports()
                        .get(anchor.source_port_index())
                        .ok_or(FormationError::NoncanonicalState)?;
                    Ok((NeuronSourceSite::from_anchor(anchor), port))
                })
                .collect::<Result<Vec<_>, FormationError>>()?;
            let reached_source_sites = reached_sources
                .iter()
                .map(|(source_site, _)| source_site.clone())
                .collect::<Vec<_>>();
            if reached_sources
                .iter()
                .enumerate()
                .any(|(index, (_, port))| {
                    reached_sources[..index]
                        .iter()
                        .any(|(_, prior)| same_dormant_source(prior, port))
                })
            {
                return Err(FormationError::NoncanonicalState);
            }
            // Existing targets are addresses into the owned successor. Cloning
            // one here duplicates the cohort's retained physical evidence.
            let mut cohort_targets: Vec<(
                usize,
                Option<ResidentReachedCohort>,
                Vec<usize>,
                Option<ReceptorLaw>,
            )> = Vec::new();
            let mut next_new_cohort_index = cohorts.len();
            let mut declared_groups = Vec::new();
            let mut physically_claimed = vec![false; reached_source_sites.len()];
            for cohort in &cohorts {
                let group = cohort
                    .anatomy
                    .source_sites()
                    .filter_map(|resident_site| {
                        reached_source_sites
                            .iter()
                            .position(|reached| reached == resident_site)
                    })
                    .collect::<Vec<_>>();
                if group.is_empty() {
                    continue;
                }
                if group
                    .iter()
                    .any(|coordinate_index| physically_claimed[*coordinate_index])
                {
                    return Err(FormationError::NeuronLineageAuthorityChanged);
                }
                for coordinate_index in &group {
                    physically_claimed[*coordinate_index] = true;
                }
                declared_groups.push(group);
            }
            for seed in &unexpressed_electrical_seeds {
                let mut group = Vec::new();
                for seed_site in seed.source_sites() {
                    let Some(coordinate_index) = reached_source_sites
                        .iter()
                        .position(|reached| reached == seed_site)
                    else {
                        group.clear();
                        break;
                    };
                    if physically_claimed[coordinate_index] {
                        group.clear();
                        break;
                    }
                    group.push(coordinate_index);
                }
                if group.len() == seed.source_sites().len() {
                    for coordinate_index in &group {
                        physically_claimed[*coordinate_index] = true;
                    }
                    declared_groups.push(group);
                }
            }
            // DSF groups describe the joint field; they are not neuronal
            // anatomy.  Any reached sites not already claimed by living
            // anatomy or explicit developmental wiring settle together only
            // when this same physical occurrence declares them on the same
            // sensory organ under the same receptor law.  The occurrence is
            // the shared causal instant, the sensor id is the organ, and the
            // receptor law is the local transduction physics.  No semantic or
            // storage grouping is introduced here.
            for coordinate_index in 0..reached_source_sites.len() {
                if physically_claimed[coordinate_index] {
                    continue;
                }
                let receptor_law =
                    receptor_law_for_reached_coordinates(&reached_sources, &[coordinate_index]);
                if receptor_law.is_none() && vestibular.is_none() {
                    continue;
                }
                let matching_group = declared_groups.iter_mut().find(|group| {
                    let Some(first_index) = group.first().copied() else {
                        return false;
                    };
                    let retained_formation_owns_group = cohorts.iter().any(|cohort| {
                        cohort.retained_experience.is_some()
                            && cohort
                                .anatomy
                                .source_sites()
                                .any(|site| site == &reached_source_sites[first_index])
                    });
                    !retained_formation_owns_group
                        && reached_source_sites[first_index].sensor_id()
                            == reached_source_sites[coordinate_index].sensor_id()
                        && receptor_law_for_reached_coordinates(&reached_sources, &[first_index])
                            == receptor_law
                });
                if let Some(group) = matching_group {
                    group.push(coordinate_index);
                } else {
                    declared_groups.push(vec![coordinate_index]);
                }
            }
            for group in &declared_groups {
                for coordinate_index in group {
                    physically_claimed[*coordinate_index] = true;
                }
            }
            for declared_group in &declared_groups {
                let group_sites = declared_group
                    .iter()
                    .map(|coordinate_index| reached_source_sites[*coordinate_index].clone())
                    .collect::<Vec<_>>();
                let group_receptor_law =
                    receptor_law_for_reached_coordinates(&reached_sources, declared_group);
                let overlapping_cohorts = cohorts
                    .iter()
                    .enumerate()
                    .filter(|(_, cohort)| {
                        group_sites.iter().any(|site| {
                            cohort
                                .anatomy
                                .source_sites()
                                .any(|resident| resident == site)
                        })
                    })
                    .map(|(index, _)| index)
                    .collect::<Vec<_>>();
                if overlapping_cohorts.len() > 1 {
                    for coordinate_index in declared_group {
                        let site = &reached_source_sites[*coordinate_index];
                        let resident_matches = overlapping_cohorts
                            .iter()
                            .copied()
                            .filter(|cohort_index| {
                                cohorts[*cohort_index]
                                    .anatomy
                                    .source_sites()
                                    .any(|resident| resident == site)
                            })
                            .collect::<Vec<_>>();
                        if resident_matches.len() != 1 {
                            return Err(if resident_matches.is_empty() {
                                FormationError::NeuronLineageAuthorityAbsent
                            } else {
                                FormationError::NeuronLineageAuthorityChanged
                            });
                        }
                        if let Some(target) = cohort_targets
                            .iter_mut()
                            .find(|(index, _, _, _)| *index == resident_matches[0])
                        {
                            target.2.push(*coordinate_index);
                        } else {
                            cohort_targets.push((
                                resident_matches[0],
                                None,
                                vec![*coordinate_index],
                                group_receptor_law,
                            ));
                        }
                    }
                    continue;
                }

                let existing_index = overlapping_cohorts.first().copied();
                if group_receptor_law.is_none() && vestibular.is_none() && existing_index.is_none()
                {
                    continue;
                }
                let mut reached_admissions = Vec::new();
                reached_admissions
                    .try_reserve_exact(declared_group.len())
                    .map_err(|_| FormationError::ArithmeticOverflow)?;
                for coordinate_index in declared_group {
                    let port = reached_sources[*coordinate_index].1;
                    let admission =
                        match resolve_lineage_for_port(&cohorts, &dormant_lineage_seeds, port)? {
                            Some(lineage) => ReachedLineageAdmission {
                                lineage,
                                claimed_resting_neuron: None,
                            },
                            None => claim_resting_or_allocate_lineage(
                                &mut resting_population,
                                &reached_source_sites[*coordinate_index],
                                &mut next_lineage_ordinal,
                            )?,
                        };
                    reached_admissions.push(admission);
                }
                let reached_lineages = reached_admissions
                    .iter()
                    .map(|admission| admission.lineage)
                    .collect::<Vec<_>>();
                let (target_index, new_cohort) = if let Some(index) = existing_index {
                    let additions = declared_group
                        .iter()
                        .zip(group_sites.iter())
                        .zip(reached_admissions.iter())
                        .filter_map(|((coordinate_index, site), admission)| {
                            (!cohorts[index]
                                .anatomy
                                .source_sites()
                                .any(|resident| resident == site))
                            .then_some((*coordinate_index, site.clone(), admission))
                        })
                        .map(|(coordinate_index, site, admission)| {
                            reached_genesis_cell_from_admission(
                                &shared,
                                coordinate_index,
                                site,
                                admission,
                            )
                        })
                        .collect::<Result<Vec<_>, _>>()?;
                    let resident = &mut cohorts[index];
                    if let Some(ingress) = vestibular {
                        if !additions.is_empty() || reached_lineages.len() != 1 {
                            return Err(FormationError::VestibularUnavailable(
                                FunctionalVestibularError::NotIsolatedSingleVertex,
                            ));
                        }
                        let expected = create_single_vertex_vestibular_reached_cohort(
                            ingress.receptor_anatomy(),
                            ingress.source(),
                            &shared,
                            reached_lineages[0],
                        )
                        .map_err(FormationError::VestibularUnavailable)?;
                        let common_positions = vec![resident.anatomy.neuron_anatomies()[0]
                            .mathloom_positions()
                            .max(expected.anatomy.neuron_anatomies()[0].mathloom_positions())];
                        extend_resident_cohort_positional_fabrics(
                            resident,
                            &common_positions,
                        )?;
                        let (expected_anatomy, _) = extend_reached_cohort_positional_fabrics(
                            &expected.anatomy,
                            &expected.state,
                            &common_positions,
                        )
                        .map_err(FormationError::PhysicalSettlementUnavailable)?;
                        if resident.anatomy != expected_anatomy {
                            return Err(FormationError::VestibularUnavailable(
                                FunctionalVestibularError::ReachedAnatomyMismatch,
                            ));
                        }
                    }
                    if !additions.is_empty() {
                        let old_anatomy = resident.anatomy.clone();
                        let old_neuron_count = old_anatomy.neuron_count();
                        let (extended_anatomy, extended_state) = extend_reached_cohort_cells(
                            &resident.anatomy,
                            &resident.state,
                            additions,
                        )
                        .map_err(FormationError::PhysicalSettlementUnavailable)?;
                        extend_resident_cohort_evidence(
                            resident,
                            &old_anatomy,
                            extended_anatomy,
                            extended_state,
                            old_neuron_count,
                        )?;
                        dormant_lineage_seeds.retain(|seed| {
                            !declared_group.iter().any(|coordinate_index| {
                                seed.matches_port(reached_sources[*coordinate_index].1)
                            })
                        });
                    }
                    if group_sites
                        .iter()
                        .zip(reached_lineages.iter())
                        .any(|(site, lineage)| {
                            resident
                                .anatomy
                                .source_site_member(site)
                                .is_none_or(|resident_index| {
                                    resident.anatomy.neuron_lineages()[resident_index] != *lineage
                                })
                        })
                    {
                        return Err(FormationError::NeuronLineageAuthorityChanged);
                    }
                    (index, None)
                } else {
                    let seed_index = unexpressed_electrical_seeds
                        .iter()
                        .position(|seed| seed.source_sites() == group_sites);
                    let electrical = match seed_index {
                        Some(index) => unexpressed_electrical_seeds[index]
                            .resolve(&group_sites)
                            .map_err(FormationError::DevelopmentalElectricalUnavailable)?,
                        None => SparseElectricalAnatomy::new(group_sites.len(), Vec::new())
                            .map_err(|error| {
                                FormationError::PhysicalGenesisUnavailable(
                                    VirtualMaterialGenesisError::Electrical(error),
                                )
                            })?,
                    };
                    let (reached_anatomy, reached_state) = if let Some(ingress) = vestibular {
                        if electrical.contact_count() != 0 || reached_lineages.len() != 1 {
                            return Err(FormationError::VestibularUnavailable(
                                FunctionalVestibularError::NotIsolatedSingleVertex,
                            ));
                        }
                        let genesis = match reached_admissions[0].claimed_resting_neuron.as_ref() {
                            Some(resting) => specialize_single_vertex_vestibular_reached_cohort(
                                ingress.receptor_anatomy(),
                                ingress.source(),
                                &shared,
                                reached_lineages[0],
                                resting,
                            ),
                            None => create_single_vertex_vestibular_reached_cohort(
                                ingress.receptor_anatomy(),
                                ingress.source(),
                                &shared,
                                reached_lineages[0],
                            ),
                        }
                        .map_err(FormationError::VestibularUnavailable)?;
                        (genesis.anatomy, genesis.state)
                    } else {
                        let cells = declared_group
                            .iter()
                            .zip(group_sites.iter())
                            .zip(reached_admissions.iter())
                            .map(|((coordinate_index, site), admission)| {
                                reached_genesis_cell_from_admission(
                                    &shared,
                                    *coordinate_index,
                                    site.clone(),
                                    admission,
                                )
                            })
                            .collect::<Result<Vec<_>, _>>()?;
                        let neuron_anatomies = cells
                            .iter()
                            .map(|cell| cell.anatomy.clone())
                            .collect::<Vec<_>>();
                        let lineages = cells.iter().map(|cell| cell.lineage).collect::<Vec<_>>();
                        let mounts = cells
                            .iter()
                            .map(|cell| cell.mount.clone())
                            .collect::<Vec<_>>();
                        let neuron_states =
                            cells.into_iter().map(|cell| cell.state).collect::<Vec<_>>();
                        let electrical_state = SparseElectricalState::genesis(&electrical);
                        let anatomy = ReachedCohortAnatomy::new_mounted(
                            neuron_anatomies,
                            lineages,
                            mounts,
                            electrical,
                        )
                        .map_err(FormationError::PhysicalSettlementUnavailable)?;
                        let state =
                            ReachedCohortState::new(&anatomy, neuron_states, electrical_state)
                                .map_err(FormationError::PhysicalSettlementUnavailable)?;
                        (anatomy, state)
                    };
                    if let Some(index) = seed_index {
                        unexpressed_electrical_seeds.remove(index);
                    }
                    dormant_lineage_seeds.retain(|seed| {
                        !declared_group.iter().any(|coordinate_index| {
                            seed.matches_port(reached_sources[*coordinate_index].1)
                        })
                    });
                    let index = next_new_cohort_index;
                    next_new_cohort_index = next_new_cohort_index
                        .checked_add(1)
                        .ok_or(FormationError::ArithmeticOverflow)?;
                    (
                        index,
                        Some(ResidentReachedCohort {
                            anatomy: reached_anatomy,
                            state: reached_state.into(),
                            pending_experience: None,
                            retained_experience: None,
                            pending_recurrence: None,
                        }),
                    )
                };
                cohort_targets.push((
                    target_index,
                    new_cohort,
                    declared_group.clone(),
                    group_receptor_law,
                ));
            }
            for (cohort_index, mut new_cohort, coordinate_indices, receptor_law) in cohort_targets {
                let cohort = match new_cohort.as_mut() {
                    Some(cohort) => cohort,
                    None => cohorts
                        .get_mut(cohort_index)
                        .ok_or(FormationError::NeuronLineageAuthorityAbsent)?,
                };
                let field_gate_count = if vestibular.is_some() {
                    1
                } else {
                    shared.result().gates.len()
                };
                if receptor_law.is_some() || vestibular.is_some() {
                    let mut required_positions = BTreeMap::new();
                    for field_gate_index in 0..field_gate_count {
                        for coordinate_index in coordinate_indices.iter().copied() {
                            let perspective = bind_neuron_perspective(
                                &shared,
                                coordinate_index,
                                field_gate_index,
                            )
                            .map_err(FormationError::JointFieldUnavailable)?;
                            let resident_index = cohort
                                .anatomy
                                .source_site_member(&reached_source_sites[coordinate_index])
                                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
                            let required = required_mathloom_positions(perspective)
                                .map_err(FormationError::JointFieldUnavailable)?;
                            required_positions
                                .entry(resident_index)
                                .and_modify(|current: &mut usize| {
                                    *current = (*current).max(required);
                                })
                                .or_insert(required);
                        }
                    }
                    extend_resident_cohort_selected_positional_fabrics(
                        cohort,
                        &required_positions.into_iter().collect::<Vec<_>>(),
                    )?;
                }
                if receptor_law.is_some() || vestibular.is_some() {
                    for field_gate_index in 0..field_gate_count {
                        let catalysts = coordinate_indices
                            .iter()
                            .map(|coordinate_index| {
                                let resident_index = cohort
                                    .anatomy
                                    .source_site_member(&reached_source_sites[*coordinate_index])
                                    .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
                                Ok(vec![
                                    0;
                                    cohort.anatomy.neuron_anatomies()[resident_index]
                                        .recovery_anatomy()
                                        .psi_lane_count()
                                ]
                                .into_boxed_slice())
                            })
                            .collect::<Result<Vec<Box<[u128]>>, FormationError>>()?;
                        let field_gate_interval = shared
                            .result()
                            .gates
                            .get(field_gate_index)
                            .ok_or(FormationError::NoncanonicalState)?
                            .interval;
                        let gate_interval_microseconds = if vestibular.is_some() {
                            None
                        } else {
                            let first = occurrence
                                .source_times
                                .get(field_gate_interval.first_sev)
                                .ok_or(FormationError::NoncanonicalState)?;
                            let last = occurrence
                                .source_times
                                .get(field_gate_interval.last_sev)
                                .ok_or(FormationError::NoncanonicalState)?;
                            Some(exact_duration_microseconds(&(last - first))?)
                        };
                        let mut inputs = Vec::new();
                        inputs
                            .try_reserve_exact(coordinate_indices.len())
                            .map_err(|_| FormationError::ArithmeticOverflow)?;
                        // Stimulus-boundary truth signal (ratified 2026-08-05,
                        // extended to sound 2026-08-06): whether this settlement
                        // interval carried ANY exogenous RECEPTOR energy, derived
                        // from the occurrence's own delivered samples — the exact
                        // `2·L·T` integral each retinal site computes from the
                        // light that really fell on it, or the exact `K·∫s²dt`
                        // integral each cochlear site computes from the pressure
                        // that really reached it.  True dark samples and true
                        // silence both integrate to exactly zero.  `None` means
                        // the occurrence is governed by no receptor law at all
                        // (vestibular ingress), where no boundary law applies.
                        let mut exogenous_receptor_energy: Option<bool> = if vestibular.is_some() {
                            None
                        } else {
                            Some(false)
                        };
                        let mut receptor_excitation_zeptojoules =
                            vec![None; cohort.anatomy.neuron_count()];
                        for (reached_input_index, coordinate_index) in
                            coordinate_indices.iter().copied().enumerate()
                        {
                            let perspective = bind_neuron_perspective(
                                &shared,
                                coordinate_index,
                                field_gate_index,
                            )
                            .map_err(FormationError::JointFieldUnavailable)?;
                            let resident_index = cohort
                                .anatomy
                                .source_site_member(&reached_source_sites[coordinate_index])
                                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
                            let (gate_work, interval_microseconds, receptor_successor_residue) =
                                if let Some(ingress) = vestibular {
                                    if coordinate_index != 0 {
                                        return Err(FormationError::VestibularUnavailable(
                                            FunctionalVestibularError::NotIsolatedSingleVertex,
                                        ));
                                    }
                                    (
                                        GateWorkOccurrence::new(
                                            ingress.transduction().gate_work_zeptojoules.clone(),
                                        ),
                                        ingress.transduction().reached_tick.interval_microseconds,
                                        None,
                                    )
                                } else {
                                    // Quantized receptor transduction: the receptor
                                    // law of THIS occurrence's sense computes an
                                    // exact transduced energy, that energy is
                                    // integrated into the site's retained
                                    // exact-rational accumulator, and whole
                                    // gate-lattice quanta are delivered as work
                                    // ONLY once the accumulation reaches the
                                    // receiving gate's own opening threshold; the
                                    // remainder is retained per-site state.  Every
                                    // mounted receptor takes the SAME delivery law
                                    // (`receptor_quantum_delivery`), the same
                                    // accumulator field, the same gate window.
                                    // Reachable only under a governing receptor
                                    // law: the enclosing branch admits a
                                    // non-vestibular settlement exactly when
                                    // `receptor_law.is_some()`.  There is no
                                    // fallback law and no default sense.
                                    let law =
                                        receptor_law.ok_or(FormationError::NoncanonicalState)?;
                                    let neuron_anatomy =
                                        &cohort.anatomy.neuron_anatomies()[resident_index];
                                    let transduced_energy_zeptojoules = match law {
                                        ReceptorLaw::Sight => {
                                            let retinal_anatomy = exact_optical_receptor_anatomy(
                                                neuron_anatomy.gate_population(),
                                            )?;
                                            let settlement =
                                                derive_optical_receptor_sample_range_work(
                                                    source,
                                                    perspective,
                                                    &retinal_anatomy,
                                                    field_gate_interval.first_sev,
                                                    field_gate_interval.last_sev,
                                                )
                                                .map_err(FormationError::OpticalWorkUnavailable)?;
                                            settlement.transduced_energy_zeptojoules
                                        }
                                        ReceptorLaw::Sound => {
                                            let auditory_anatomy = exact_auditory_receptor_anatomy(
                                                neuron_anatomy.gate_population(),
                                            )?;
                                            let settlement =
                                                derive_auditory_receptor_sample_range_work(
                                                    source,
                                                    perspective,
                                                    &auditory_anatomy,
                                                    field_gate_interval.first_sev,
                                                    field_gate_interval.last_sev,
                                                )
                                                .map_err(FormationError::AuditoryWorkUnavailable)?;
                                            settlement.transduced_energy_zeptojoules
                                        }
                                        ReceptorLaw::Touch => {
                                            let tactile_anatomy = exact_tactile_receptor_anatomy(
                                                neuron_anatomy.gate_population(),
                                            )?;
                                            let settlement =
                                                derive_tactile_receptor_sample_range_work(
                                                    source,
                                                    perspective,
                                                    &tactile_anatomy,
                                                    field_gate_interval.first_sev,
                                                    field_gate_interval.last_sev,
                                                )
                                                .map_err(FormationError::TactileWorkUnavailable)?;
                                            settlement.transduced_energy_zeptojoules
                                        }
                                        ReceptorLaw::Chemical => {
                                            let chemical_anatomy = exact_chemical_receptor_anatomy(
                                                neuron_anatomy.gate_population(),
                                            )?;
                                            let settlement =
                                                derive_chemical_receptor_sample_range_work(
                                                    source,
                                                    perspective,
                                                    &chemical_anatomy,
                                                    field_gate_interval.first_sev,
                                                    field_gate_interval.last_sev,
                                                )
                                                .map_err(FormationError::ChemicalWorkUnavailable)?;
                                            settlement.transduced_energy_zeptojoules
                                        }
                                        ReceptorLaw::ArticulatoryBody => {
                                            let articulatory_anatomy =
                                                exact_articulatory_receptor_anatomy(
                                                    neuron_anatomy.gate_population(),
                                                )?;
                                            let settlement =
                                                derive_articulatory_receptor_sample_range_work(
                                                    source,
                                                    perspective,
                                                    &articulatory_anatomy,
                                                    field_gate_interval.first_sev,
                                                    field_gate_interval.last_sev,
                                                )
                                                .map_err(
                                                    FormationError::ArticulatoryWorkUnavailable,
                                                )?;
                                            settlement.transduced_energy_zeptojoules
                                        }
                                        ReceptorLaw::ThermalBody => {
                                            let thermal_anatomy =
                                                exact_thermal_receptor_anatomy(
                                                    neuron_anatomy.gate_population(),
                                                )?;
                                            let settlement =
                                                derive_thermal_receptor_sample_range_work(
                                                    source,
                                                    perspective,
                                                    &thermal_anatomy,
                                                    field_gate_interval.first_sev,
                                                    field_gate_interval.last_sev,
                                                )
                                                .map_err(
                                                    FormationError::ThermalWorkUnavailable,
                                                )?;
                                            settlement.transduced_energy_zeptojoules
                                        }
                                        ReceptorLaw::ProprioceptiveBody => {
                                            let proprioceptive_anatomy =
                                                exact_proprioceptive_receptor_anatomy(
                                                    neuron_anatomy.gate_population(),
                                                )?;
                                            let settlement =
                                                derive_proprioceptive_receptor_sample_range_work(
                                                    source,
                                                    perspective,
                                                    &proprioceptive_anatomy,
                                                    field_gate_interval.first_sev,
                                                    field_gate_interval.last_sev,
                                                )
                                                .map_err(
                                                    FormationError::ProprioceptiveWorkUnavailable,
                                                )?;
                                            settlement.transduced_energy_zeptojoules
                                        }
                                    };
                                    if !transduced_energy_zeptojoules.is_zero() {
                                        exogenous_receptor_energy = Some(true);
                                        let lineage =
                                            cohort.anatomy.neuron_lineages()[resident_index];
                                        if !externally_energized_neuron_lineages.contains(&lineage) {
                                            externally_energized_neuron_lineages.push(lineage);
                                        }
                                        if !externally_energized_by_occurrence[occurrence_index]
                                            .contains(&lineage)
                                        {
                                            externally_energized_by_occurrence[occurrence_index]
                                                .push(lineage);
                                        }
                                    }
                                    receptor_excitation_zeptojoules[resident_index] = Some(
                                        big_to_exact_rational(&transduced_energy_zeptojoules)
                                            .map_err(|_| FormationError::ArithmeticOverflow)?,
                                    );
                                    let predecessor_neuron =
                                        &cohort.state.neurons()[resident_index];
                                    let prepared_psi = neuron_anatomy
                                        .prepare_psi_settlement(predecessor_neuron, perspective)
                                        .map_err(|error| {
                                            FormationError::PhysicalSettlementUnavailable(
                                                ReachedCohortError::Neuron {
                                                    neuron_index: resident_index,
                                                    error,
                                                },
                                            )
                                        })?;
                                    let window = gate_opening_quantum_window_with_psi(
                                        &cohort.anatomy.neuron_anatomies()[resident_index],
                                        &cohort.state.neurons()[resident_index],
                                        &prepared_psi,
                                    )
                                    .map_err(|error| {
                                        FormationError::PhysicalSettlementUnavailable(
                                            ReachedCohortError::Neuron {
                                                neuron_index: resident_index,
                                                error,
                                            },
                                        )
                                    })?;
                                    let delivery = if neuron_anatomy.gate_population() > 1 {
                                        let schedule = gate_population_opening_schedule_with_psi(
                                                    neuron_anatomy,
                                                    predecessor_neuron,
                                                    &prepared_psi,
                                                )
                                                .map_err(|error| {
                                                    FormationError::PhysicalSettlementUnavailable(
                                                        ReachedCohortError::Neuron {
                                                            neuron_index: resident_index,
                                                            error,
                                                        },
                                                    )
                                                })?;
                                        let population = quantize_population_receptor_delivery(
                                            &transduced_energy_zeptojoules,
                                            predecessor_neuron.receptor_quantum_residue,
                                            neuron_anatomy.gate_dissipation_quantum_zeptojoules(),
                                            &schedule,
                                        );
                                        match law {
                                            ReceptorLaw::Sight => population.map_err(|error| {
                                                FormationError::OpticalWorkUnavailable(error.into())
                                            })?,
                                            ReceptorLaw::Sound => population.map_err(|error| {
                                                FormationError::AuditoryWorkUnavailable(
                                                    error.into(),
                                                )
                                            })?,
                                            ReceptorLaw::Touch => population.map_err(|error| {
                                                FormationError::TactileWorkUnavailable(error.into())
                                            })?,
                                            ReceptorLaw::Chemical => {
                                                population.map_err(|error| {
                                                    FormationError::ChemicalWorkUnavailable(
                                                        error.into(),
                                            )
                                                })?
                                        }
                                            ReceptorLaw::ArticulatoryBody => population
                                                .map_err(|error| {
                                                    FormationError::ArticulatoryWorkUnavailable(
                                                        error.into(),
                                                    )
                                                })?,
                                            ReceptorLaw::ThermalBody => population
                                                .map_err(|error| {
                                                    FormationError::ThermalWorkUnavailable(
                                                        error.into(),
                                                    )
                                                })?,
                                            ReceptorLaw::ProprioceptiveBody => population
                                                .map_err(|error| {
                                                    FormationError::ProprioceptiveWorkUnavailable(
                                                        error.into(),
                                                    )
                                                })?,
                                        }
                                    } else {
                                        match law {
                                            ReceptorLaw::Sound => quantize_auditory_delivery(
                                                &transduced_energy_zeptojoules,
                                                predecessor_neuron.receptor_quantum_residue,
                                                neuron_anatomy
                                                    .gate_dissipation_quantum_zeptojoules(),
                                                window.opening_threshold_quanta,
                                                window.window_cap_quanta,
                                            )
                                            .map_err(FormationError::AuditoryWorkUnavailable)?,
                                        ReceptorLaw::Sight => quantize_optical_delivery(
                                            &transduced_energy_zeptojoules,
                                            predecessor_neuron.receptor_quantum_residue,
                                                neuron_anatomy
                                                    .gate_dissipation_quantum_zeptojoules(),
                                            window.opening_threshold_quanta,
                                            window.window_cap_quanta,
                                        )
                                        .map_err(FormationError::OpticalWorkUnavailable)?,
                                        ReceptorLaw::Touch => quantize_tactile_delivery(
                                            &transduced_energy_zeptojoules,
                                                predecessor_neuron.receptor_quantum_residue,
                                                neuron_anatomy
                                                .gate_dissipation_quantum_zeptojoules(),
                                            window.opening_threshold_quanta,
                                            window.window_cap_quanta,
                                        )
                                        .map_err(FormationError::TactileWorkUnavailable)?,
                                        ReceptorLaw::Chemical => quantize_chemical_delivery(
                                            &transduced_energy_zeptojoules,
                                                predecessor_neuron.receptor_quantum_residue,
                                                neuron_anatomy
                                                .gate_dissipation_quantum_zeptojoules(),
                                            window.opening_threshold_quanta,
                                            window.window_cap_quanta,
                                        )
                                        .map_err(FormationError::ChemicalWorkUnavailable)?,
                                        ReceptorLaw::ArticulatoryBody => {
                                            quantize_articulatory_delivery(
                                                &transduced_energy_zeptojoules,
                                                predecessor_neuron.receptor_quantum_residue,
                                                neuron_anatomy
                                                    .gate_dissipation_quantum_zeptojoules(),
                                                window.opening_threshold_quanta,
                                                window.window_cap_quanta,
                                            )
                                            .map_err(
                                                FormationError::ArticulatoryWorkUnavailable,
                                            )?
                                        }
                                        ReceptorLaw::ThermalBody => {
                                            quantize_thermal_delivery(
                                                &transduced_energy_zeptojoules,
                                                predecessor_neuron.receptor_quantum_residue,
                                                neuron_anatomy
                                                    .gate_dissipation_quantum_zeptojoules(),
                                                window.opening_threshold_quanta,
                                                window.window_cap_quanta,
                                            )
                                            .map_err(
                                                FormationError::ThermalWorkUnavailable,
                                            )?
                                        }
                                        ReceptorLaw::ProprioceptiveBody => {
                                            quantize_proprioceptive_delivery(
                                                &transduced_energy_zeptojoules,
                                                predecessor_neuron.receptor_quantum_residue,
                                                neuron_anatomy
                                                    .gate_dissipation_quantum_zeptojoules(),
                                                window.opening_threshold_quanta,
                                                window.window_cap_quanta,
                                            )
                                            .map_err(
                                                FormationError::ProprioceptiveWorkUnavailable,
                                            )?
                                        }
                                        }
                                    };
                                    (
                                        delivery.gate_work,
                                        gate_interval_microseconds
                                            .ok_or(FormationError::NoncanonicalState)?,
                                        Some((delivery.successor_residue, prepared_psi)),
                                    )
                                };
                            let (receptor_successor_residue, prepared_psi) =
                                match receptor_successor_residue {
                                    Some((residue, psi)) => (Some(residue), Some(psi)),
                                    None => {
                                        let prepared = cohort.anatomy.neuron_anatomies()
                                            [resident_index]
                                            .prepare_psi_settlement(
                                                &cohort.state.neurons()[resident_index],
                                                perspective,
                                            )
                                            .map_err(|error| {
                                                FormationError::PhysicalSettlementUnavailable(
                                                    ReachedCohortError::Neuron {
                                                        neuron_index: resident_index,
                                                        error,
                                                    },
                                                )
                                            })?;
                                        (None, Some(prepared))
                                    }
                                };
                            inputs.push(NeuronIntervalInput {
                                perspective,
                                gate_work,
                                interval_microseconds,
                                recovery: RecoveryContact::new(
                                    &catalysts[reached_input_index],
                                    0,
                                    0,
                                ),
                                dna_expression: DnaExpressionContact::new(0),
                                receptor_successor_residue,
                                prepared_psi,
                            });
                        }
                        let input = ReachedCohortIntervalInput::from_episode(source, inputs)
                            .map_err(FormationError::PhysicalSettlementUnavailable)?;
                        let gate_work_perturbed_neurons = input
                            .resident_gate_work_bits(&cohort.anatomy)
                            .map_err(FormationError::PhysicalSettlementUnavailable)?;
                        let reached_body_receptor_indices = gate_work_perturbed_neurons
                            .iter()
                            .enumerate()
                            .filter_map(|(neuron_index, perturbed)| {
                                let mount = &cohort.anatomy.mounts()[neuron_index];
                                (*perturbed
                                    && mount.source_site().is_some()
                                    && mount.place().layer() == 5)
                                    .then_some(neuron_index)
                            })
                            .collect::<Vec<_>>();
                        let local_dark_recovery_settled =
                            exogenous_receptor_energy == Some(false);
                        let interval_predecessor_neurons = if local_dark_recovery_settled {
                            cohort
                                .state
                                .neurons()
                                .iter()
                                .cloned()
                                .enumerate()
                                .collect::<Vec<_>>()
                        } else {
                            input
                                .resident_indices(&cohort.anatomy)
                                .map_err(FormationError::PhysicalSettlementUnavailable)?
                                .into_iter()
                                .map(|neuron_index| {
                                    (neuron_index, cohort.state.neurons()[neuron_index].clone())
                                })
                                .collect::<Vec<_>>()
                        };
                        for (perturbed, lineage) in gate_work_perturbed_neurons
                            .iter()
                            .zip(cohort.anatomy.neuron_lineages())
                        {
                            if *perturbed && !externally_perturbed_neuron_lineages.contains(lineage)
                            {
                                externally_perturbed_neuron_lineages.push(*lineage);
                            }
                            if vestibular.is_some()
                                && *perturbed
                                && !externally_energized_neuron_lineages.contains(lineage)
                            {
                                externally_energized_neuron_lineages.push(*lineage);
                            }
                            if vestibular.is_some()
                                && *perturbed
                                && !externally_energized_by_occurrence[occurrence_index]
                                    .contains(lineage)
                            {
                                externally_energized_by_occurrence[occurrence_index].push(*lineage);
                            }
                        }
                        let outcome = settle_resident_physical_interval(
                            cohort,
                            input,
                            gate_work_perturbed_neurons,
                            receptor_excitation_zeptojoules,
                            exogenous_receptor_energy,
                            &mosaics,
                            max_encoded_bytes,
                            source_generation,
                        )?;
                        for (neuron_index, (successor, lineage)) in cohort
                            .state
                            .neurons()
                            .iter()
                            .zip(cohort.anatomy.neuron_lineages())
                            .enumerate()
                        {
                            let mount = &cohort.anatomy.mounts()[neuron_index];
                            if mount.source_site().is_some()
                                && mount.place().layer() == 5
                                && (local_dark_recovery_settled
                                    || reached_body_receptor_indices
                                        .binary_search(&neuron_index)
                                        .is_ok())
                            {
                                retain_latest_localized_metabolic_strain(
                                    &mut localized_metabolic_strain_evaluated_body_receptor_lineages,
                                    &mut localized_metabolic_strain,
                                    source_generation,
                                    *lineage,
                                    mount.place(),
                                    successor,
                                )?;
                            }
                        }
                        if outcome.metabolic.changed() {
                            for (neuron_index, predecessor) in
                                interval_predecessor_neurons.iter()
                            {
                                let successor = &cohort.state.neurons()[*neuron_index];
                                let lineage = &cohort.anatomy.neuron_lineages()[*neuron_index];
                                if predecessor.separated_elementary_charges()
                                    == successor.separated_elementary_charges()
                                {
                                    continue;
                                }
                                let mount = &cohort.anatomy.mounts()[*neuron_index];
                                if mount.source_site().is_some()
                                    && mount.place().layer() == 5
                                    && !metabolically_perturbed_body_receptor_lineages
                                        .contains(lineage)
                                {
                                    metabolically_perturbed_body_receptor_lineages.push(*lineage);
                                }
                            }
                        }
                        for (neuron_index, predecessor) in &interval_predecessor_neurons {
                            let successor = &cohort.state.neurons()[*neuron_index];
                            let lineage = &cohort.anatomy.neuron_lineages()[*neuron_index];
                            if predecessor != successor
                                && !physically_transitioned_neuron_lineages.contains(lineage)
                            {
                                physically_transitioned_neuron_lineages.push(*lineage);
                            }
                            if predecessor != successor {
                                retain_first_transition_predecessor(
                                    &mut transition_neuron_predecessors,
                                    TransitionNeuronPredecessor {
                                        lineage: *lineage,
                                        anatomy: cohort.anatomy.neuron_anatomies()[*neuron_index]
                                            .clone(),
                                        state: predecessor.clone(),
                                    },
                                );
                            }
                        }
                        metabolic.recovered_neuron_count = metabolic
                            .recovered_neuron_count
                            .checked_add(outcome.metabolic.recovered_neuron_count)
                            .ok_or(FormationError::ArithmeticOverflow)?;
                        metabolic.drained_dissipation_quanta = metabolic
                            .drained_dissipation_quanta
                            .checked_add(outcome.metabolic.drained_dissipation_quanta)
                            .ok_or(FormationError::ArithmeticOverflow)?;
                        metabolic.unmet_dissipation_quanta =
                            outcome.metabolic.unmet_dissipation_quanta;
                        metabolic.returned_elementary_charges = metabolic
                            .returned_elementary_charges
                            .checked_add(outcome.metabolic.returned_elementary_charges)
                            .ok_or(FormationError::ArithmeticOverflow)?;
                        metabolic.unreturned_elementary_charges =
                            outcome.metabolic.unreturned_elementary_charges;
                        metabolic.fuel_quanta = metabolic
                            .fuel_quanta
                            .checked_add(outcome.metabolic.fuel_quanta)
                            .ok_or(FormationError::ArithmeticOverflow)?;
                        emitted_neuron_fractals.extend(outcome.emitted_neuron_fractals);
                        partial_cue_reassembly_count = partial_cue_reassembly_count
                            .checked_add(outcome.partial_cue_reassembly_count)
                            .ok_or(FormationError::ArithmeticOverflow)?;
                        endogenous_partial_cue_reassembly_count =
                            endogenous_partial_cue_reassembly_count
                                .checked_add(outcome.endogenous_partial_cue_reassembly_count)
                                .ok_or(FormationError::ArithmeticOverflow)?;
                        if outcome.mosaic_formed.is_some() {
                            mosaic_formed = outcome.mosaic_formed;
                        }
                        for resolution in outcome.mosaic_resolutions {
                            apply_mosaic_structural_resolution(&mut mosaics, resolution)?;
                        }
                        // No episode is admitted to cold custody any more, so
                        // nothing is prepared, published or navigated here.  A
                        // reassembly's receipt is `mosaic_formed`, which is the
                        // sha256 of the admitted mosaic's own encoded body — a
                        // digest of a physical structure she holds, rather than
                        // the address of an archived file.
                    }
                }
                for coordinate_index in coordinate_indices.iter().copied() {
                    let resident_index = cohort
                        .anatomy
                        .source_site_member(&reached_source_sites[coordinate_index])
                        .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
                    let lineage = cohort.anatomy.neuron_lineages()[resident_index];
                    if !externally_reached_neuron_lineages.contains(&lineage) {
                        externally_reached_neuron_lineages.push(lineage);
                        externally_reached_receptor_places
                            .push((lineage, cohort.anatomy.mounts()[resident_index].place()));
                    }
                }
                if let Some(cohort) = new_cohort {
                    if cohort_index != cohorts.len() {
                        return Err(FormationError::NoncanonicalState);
                    }
                    cohorts.push(cohort);
                }
            }
        }
        let mut electrical_fabric = predecessor_electrical_fabric;
        let predecessor_active_electrical_frontier =
            predecessor_active_electrical_frontier.into_vec();
        let mut active_electrical_frontier = predecessor_active_electrical_frontier.clone();
        mount_reached_local_integration(
            &mut cohorts,
            &mut resting_population,
            &mut next_lineage_ordinal,
            &mut electrical_fabric,
            &externally_reached_receptor_places,
        )?;
        let mut reached_association_lineages = Vec::new();
        let mut reached_body_regulation_lineages = Vec::new();
        for occurrence_lineages in &externally_energized_by_occurrence {
            if let Some(lineage) = mount_reached_cross_sensory_association(
                &mut cohorts,
                &mut resting_population,
                &mut next_lineage_ordinal,
                &mut electrical_fabric,
                occurrence_lineages,
            )? {
                if !reached_association_lineages.contains(&lineage) {
                    reached_association_lineages.push(lineage);
                }
            }
            for lineage in mount_reached_body_regulation(
                &mut cohorts,
                &mut resting_population,
                &mut next_lineage_ordinal,
                &mut electrical_fabric,
                occurrence_lineages,
            )? {
                if !reached_body_regulation_lineages.contains(&lineage) {
                    reached_body_regulation_lineages.push(lineage);
                }
            }
        }
        // A receptor exists in the continuous sensorium even when its exact
        // input performs no gate work. Mere source declaration is therefore
        // not authority to re-seed the electrical fabric: only the receptor's
        // measured local transduced energy may originate a new frontier. An
        // already-moving frontier still continues below, and a local metabolic
        // membrane perturbation remains an intrinsic reached cause. This keeps
        // darkness and silence physical without turning them into commands.
        let mut current_noncontinuation_seed_lineages =
            externally_energized_neuron_lineages.clone();
        for lineage in reached_association_lineages
            .iter()
            .chain(&reached_body_regulation_lineages)
            .chain(&metabolically_perturbed_body_receptor_lineages)
        {
            if !current_noncontinuation_seed_lineages.contains(lineage) {
                current_noncontinuation_seed_lineages.push(*lineage);
            }
        }
        let mut internal_frontier_lineages = current_noncontinuation_seed_lineages.clone();
        let mut locally_settled_lineages = externally_reached_neuron_lineages.clone();
        for lineage in reached_association_lineages
            .iter()
            .chain(&reached_body_regulation_lineages)
            .chain(&metabolically_perturbed_body_receptor_lineages)
        {
            if !locally_settled_lineages.contains(lineage) {
                locally_settled_lineages.push(*lineage);
            }
        }
        for entry in &active_electrical_frontier {
            for lineage in entry.affected_lineages().into_iter().flatten() {
                if !internal_frontier_lineages.contains(&lineage) {
                    internal_frontier_lineages.push(lineage);
                }
                if !locally_settled_lineages.contains(&lineage) {
                    locally_settled_lineages.push(lineage);
                }
            }
        }
        if !topology_index.matches_shape(&cohorts, &electrical_fabric) {
            topology_index = Arc::new(ResidentTopologyIndex::build(
                &cohorts,
                &electrical_fabric,
            )?);
        }
        let internal_contact = settle_internal_contact_interval(
            &mut cohorts,
            &mut electrical_fabric,
            &topology_index,
            &locally_settled_lineages,
            &internal_frontier_lineages,
            &mut physically_transitioned_neuron_lineages,
            source_generation,
            resting_population
                .as_ref()
                .map(DevelopmentalRestingPopulation::resting_cell_count)
                .map(usize::try_from)
                .transpose()
                .map_err(|_| FormationError::ArithmeticOverflow)?
                .unwrap_or(0),
        )?;
        active_electrical_frontier = internal_contact.next_active_frontier.clone();
        let (working_causal_continuations, settled_working_frontier) =
            working_causal_frontier_observation(
                &predecessor_active_electrical_frontier,
                &active_electrical_frontier,
                &current_noncontinuation_seed_lineages,
            );
        let lineage_layers = topology_index.lineage_layers.as_ref();
        let physical_prediction_alternatives = physical_prediction_alternatives_observation(
            &predecessor_active_electrical_frontier,
            &active_electrical_frontier,
            &current_noncontinuation_seed_lineages,
            lineage_layers,
        );
        let body_consequence_transfers = body_consequence_transfer_observation(
            &active_electrical_frontier,
            lineage_layers,
            &reached_body_regulation_lineages,
            vestibular.is_some(),
        );
        for predecessor in internal_contact.transition_predecessors {
            retain_first_transition_predecessor(&mut transition_neuron_predecessors, predecessor);
        }
        emitted_neuron_fractals.extend(internal_contact.emitted_neuron_fractals.iter().cloned());
        for lineage in &internal_contact.metabolically_perturbed_body_receptor_lineages {
            if !metabolically_perturbed_body_receptor_lineages.contains(lineage) {
                metabolically_perturbed_body_receptor_lineages.push(*lineage);
            }
        }
        dsf_delivery_count = dsf_delivery_count
            .checked_add(internal_contact.dsf_delivery_count)
            .ok_or(FormationError::ArithmeticOverflow)?;
        emitted_neuron_fractals = coalesce_emitted_neuron_fractals(emitted_neuron_fractals)?;
        mount_reached_affective_reach(
            &mut cohorts,
            &mut resting_population,
            &mut next_lineage_ordinal,
            &mut electrical_fabric,
            &physically_transitioned_neuron_lineages,
        )?;
        mount_reached_ordering_reach(
            &mut cohorts,
            &mut resting_population,
            &mut next_lineage_ordinal,
            &mut electrical_fabric,
            &internal_contact.active_bonds,
        )?;
        mount_reached_motor_effector(
            &mut cohorts,
            &mut resting_population,
            &mut next_lineage_ordinal,
            &mut electrical_fabric,
            &physically_transitioned_neuron_lineages,
        )?;
        if !topology_index.matches_shape(&cohorts, &electrical_fabric) {
            topology_index = Arc::new(ResidentTopologyIndex::build(
                &cohorts,
                &electrical_fabric,
            )?);
        }
        let current_physical_deltas = exact_transition_physical_deltas(
            &cohorts,
            &topology_index,
            &transition_neuron_predecessors,
        )?;
        let (
            organism_mosaic_receipt,
            organism_reassemblies,
            organism_internal_reassemblies,
            organic_mosaic_relations,
            internally_reassembled_formation_cues,
            externally_reassembled_formation_frontiers,
        ) =
            settle_organism_mosaic_boundary(
                &cohorts,
                &topology_index,
                &emitted_neuron_fractals,
                &current_physical_deltas,
                &externally_reached_neuron_lineages,
                &externally_perturbed_neuron_lineages,
                &metabolically_perturbed_body_receptor_lineages,
                &internal_contact.active_bonds,
                &predecessor_older_active_electrical_frontier,
                &predecessor_preceding_active_electrical_frontier,
                &predecessor_active_electrical_frontier,
                &active_electrical_frontier,
                &mut mosaics,
                max_encoded_bytes,
            )?;
        if organism_mosaic_receipt.is_some() {
            mosaic_formed = organism_mosaic_receipt;
        }
        partial_cue_reassembly_count = partial_cue_reassembly_count
            .checked_add(organism_reassemblies)
            .ok_or(FormationError::ArithmeticOverflow)?;
        endogenous_partial_cue_reassembly_count = endogenous_partial_cue_reassembly_count
            .checked_add(organism_internal_reassemblies)
            .ok_or(FormationError::ArithmeticOverflow)?;
        retain_internally_reassembled_recurrent_frontier(
            &mut active_electrical_frontier,
            &predecessor_active_electrical_frontier,
            &internally_reassembled_formation_cues,
            &internal_contact.settled_directed_transfers,
        )?;
        let newly_retained_mosaic_indices = mosaics
            .iter()
            .enumerate()
            .filter(|(_, retained)| retained.mosaic.carries_only_retained_neuron_structure())
            .filter(|(_, retained)| {
                !predecessor_recognized_mosaics
                    .iter()
                    .any(|prior| prior.same_retained_structure(&retained.mosaic))
            })
            .map(|(index, _)| index)
            .collect::<Vec<_>>();
        let newly_retained_mosaic_members = newly_retained_mosaic_indices
            .iter()
            .map(|index| mosaics[*index].mosaic.member_lineages().to_vec())
            .collect::<Vec<_>>();
        let mounted_retention_lineages = mount_new_recurrent_retention(
            &mut cohorts,
            &mut resting_population,
            &mut next_lineage_ordinal,
            &mut electrical_fabric,
            &newly_retained_mosaic_members,
        )?;
        for (mosaic_index, recurrent_lineage) in newly_retained_mosaic_indices
            .into_iter()
            .zip(mounted_retention_lineages)
        {
            mosaics[mosaic_index].recurrent_lineage = Some(recurrent_lineage);
        }
        resolve_unpersisted_recurrent_retention(
            &cohorts,
            &electrical_fabric,
            &mut mosaics,
        )?;
        let externally_perturbed_body_receptor_count = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .neuron_lineages()
                    .iter()
                    .zip(cohort.anatomy.source_sites())
            })
            .filter(|(lineage, source)| {
                source.sense() == PhysicalSourceSense::Body
                    && externally_perturbed_neuron_lineages.contains(lineage)
            })
            .count();
        if !topology_index.matches_shape(&cohorts, &electrical_fabric) {
            topology_index = Arc::new(ResidentTopologyIndex::build(
                &cohorts,
                &electrical_fabric,
            )?);
        }
        let successor = Self {
            generation: source_generation,
            next_lineage_ordinal,
            unexpressed_electrical_seeds: unexpressed_electrical_seeds.into_boxed_slice(),
            dormant_lineage_seeds: dormant_lineage_seeds.into_boxed_slice(),
            resting_population,
            cohorts: cohorts.into_boxed_slice(),
            electrical_fabric,
            older_active_electrical_frontier: predecessor_preceding_active_electrical_frontier,
            preceding_active_electrical_frontier: predecessor_active_electrical_frontier
                .into_boxed_slice(),
            active_electrical_frontier: active_electrical_frontier.into_boxed_slice(),
            mosaics: mosaics.into_boxed_slice(),
            hippocampal,
            topology_index,
        };
        let successor_encoded = if seal_successor {
            successor.encode(max_encoded_bytes)?
        } else {
            Vec::new()
        };
        let summary = if seal_successor {
            successor.summary()
        } else {
            successor.unsealed_structural_summary()
        };
        let successor_energy = summary.energy;
        let complete_neuron_count = summary.complete_neuron_count;
        let physically_transitioned_neuron_count = physically_transitioned_neuron_lineages.len();
        let complete_neuron_fractal_count = emitted_neuron_fractals.len();
        let mosaic_of_mosaics_count = if seal_successor {
            successor.mosaic_of_mosaics_count()?
        } else {
            0
        };
        Ok(PreparedCognitiveFormationTransition {
            predecessor_generation: predecessor_generation_authority,
            predecessor_hippocampal: predecessor_hippocampal_authority,
            successor,
            successor_encoded,
            observation: CognitiveFormationObservation {
                cognitive_ordinal: source_generation,
                trace_formed: false,
                mosaic_formed,
                activations: Vec::new(),
                trace_count: 0,
                mosaic_count: summary.mosaic_count,
                dsf_delivery_count,
                complete_neuron_count,
                resting_neuron_count: summary.resting_neuron_count,
                physically_transitioned_neuron_count,
                externally_perturbed_body_receptor_count,
                externally_perturbed_neuron_lineages:
                    externally_perturbed_neuron_lineages.iter().copied().collect(),
                metabolically_perturbed_body_receptor_count:
                    metabolically_perturbed_body_receptor_lineages.len(),
                complete_neuron_fractal_count,
                emitted_neuron_fractals,
                active_physical_bonds: internal_contact.active_bonds,
                changed_contact_channel_states: internal_contact.changed_contact_channel_states,
                reached_and_foregone_physical_frontier_routes:
                    if has_reached_and_foregone_frontier_routes(&internal_contact.frontier_routes) {
                    internal_contact.frontier_routes.clone()
                } else {
                    Vec::new()
                },
                physical_frontier_routes: internal_contact.frontier_routes,
                preceding_distinct_physical_frontier_routes: Vec::new(),
                working_causal_continuations,
                settled_working_frontier,
                physical_prediction_alternatives,
                body_consequence_transfers,
                affective_balance_trajectories: internal_contact.affective_balance_trajectories,
                localized_fluid_chemistry: internal_contact.localized_fluid_chemistry,
                localized_metabolic_strain_evaluated_body_receptor_lineages,
                localized_metabolic_strain,
                organic_mosaic_relations,
                motor_unit_recruitments: internal_contact.motor_unit_recruitments,
                articulatory_unit_recruitments: internal_contact.articulatory_unit_recruitments,
                partial_cue_reassembly_count,
                endogenous_partial_cue_reassembly_count,
                internally_reassembled_formation_cues,
                externally_reassembled_formation_frontiers,
                mosaic_of_mosaics_count,
                rest_recovered_neuron_count: metabolic.recovered_neuron_count,
                rest_drained_dissipation_quanta: metabolic.drained_dissipation_quanta,
                unmet_dissipation_quanta: metabolic.unmet_dissipation_quanta,
                membrane_returned_elementary_charges: metabolic.returned_elementary_charges,
                membrane_unreturned_elementary_charges: metabolic.unreturned_elementary_charges,
                metabolic_fuel_quanta: metabolic.fuel_quanta,
                nutrition_regenerated_fuel_quanta: 0,
                nutrition_unabsorbed_waste_quanta: 0,
                nutrition_vented_heat_quanta: 0,
                energy: successor_energy,
            },
        })
    }

    pub(crate) fn advance_vestibular_transition(
        self,
        ingress: &ResidentVestibularIngress,
        max_encoded_bytes: usize,
    ) -> Result<(Self, CognitiveFormationObservation), FormationError> {
        let (source, contacts) = ingress.source().joint_source_with_contacts();
        if source.joint_source_occurrences().len() != 1 || !contacts.is_empty() {
            return Err(FormationError::VestibularUnavailable(
                FunctionalVestibularError::NotIsolatedSingleVertex,
            ));
        }
        let admission = ingress
            .source()
            .joint_uf_source_admission()
            .map_err(|error| {
                FormationError::JointFieldUnavailable(JointNeuronBoundaryError::Source(error))
            })?;
        let admitted_source = AdmittedJointSourceEpisode::new(source.clone(), vec![(0, admission)])
            .map_err(|error| {
                FormationError::JointFieldUnavailable(JointNeuronBoundaryError::Source(error))
            })?;
        let predecessor_generation = self.generation;
        let predecessor_hippocampal = self.hippocampal;
        let retired = self.retire_aliased_local_integrators()?;
        let expanded = retired
            .unwrap_or(self)
            .into_expanded_legacy_receptor_channel_populations()?;
        let prepared = Self::prepare_typed_admitted_transition_from_owned(
            expanded,
            predecessor_generation,
            predecessor_hippocampal,
            &admitted_source,
            Some(ingress),
            max_encoded_bytes,
            false,
        )?;
        Ok((prepared.successor, prepared.observation))
    }

    pub(crate) fn advance_admitted_transition(
        self,
        admitted_source: &AdmittedJointSourceEpisode,
        max_encoded_bytes: usize,
    ) -> Result<(Self, CognitiveFormationObservation), FormationError> {
        let predecessor_generation = self.generation;
        let predecessor_hippocampal = self.hippocampal;
        let retired = self.retire_aliased_local_integrators()?;
        let expanded = retired
            .unwrap_or(self)
            .into_expanded_legacy_receptor_channel_populations()?;
        let prepared = Self::prepare_typed_admitted_transition_from_owned(
            expanded,
            predecessor_generation,
            predecessor_hippocampal,
            admitted_source,
            None,
            max_encoded_bytes,
            false,
        )?;
        Ok((prepared.successor, prepared.observation))
    }

    /// Deliver one AUTHORED nutrition declaration to the body.
    ///
    /// This is an intake, not a sensory occurrence: it advances the cognitive
    /// generation and nothing else.  The declaration's energy is allocated to
    /// the cohorts that can actually absorb it, in mounted order; whatever no
    /// cohort can absorb leaves as waste, and every cohort's accumulated heat
    /// is vented by the same exchange.  A body that can absorb nothing at all
    /// refuses the intake outright rather than pretending to eat.
    /// Read-only structural observation of the living cohorts' authored
    /// anatomy: one entry per cohort as `(member_count, contact_count)`.
    /// Reading advances nothing.
    pub(crate) fn observe_cohort_contacts(&self) -> Vec<(usize, usize)> {
        self.cohorts
            .iter()
            .map(|cohort| {
                (
                    cohort.anatomy.neuron_count(),
                    cohort.anatomy.contact_count(),
                )
            })
            .collect()
    }

    /// Count the living reached neurons at each exact developmental layer.
    ///
    /// This is a bounded read-only projection of persisted anatomy. It does
    /// not scan the compact resting population, assign functional meaning to
    /// a layer, expose neuronal state, or advance the organism.
    pub(crate) fn observe_reached_neuron_count_by_layer(&self) -> Vec<(u32, usize)> {
        let mut counts = Vec::<(u32, usize)>::new();
        for layer in self
            .cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.mounts())
            .map(|mount| mount.place().layer())
        {
            if let Some((_, count)) = counts.iter_mut().find(|(candidate, _)| *candidate == layer) {
                *count += 1;
            } else {
                counts.push((layer, 1));
            }
        }
        counts.sort_unstable_by_key(|(layer, _)| *layer);
        counts
    }

    /// Enumerate the exact stable lineage, developmental layer, and receptor
    /// status of each reached complete neuron. This is bounded by reached
    /// material only; it never materializes or scans the compact resting
    /// population, reads no neuronal state, and advances nothing. The
    /// projection exists so a retained formation's member lineages can be
    /// checked against their real anatomy instead of inferred from a counter.
    pub(crate) fn observe_reached_neuron_lineage_layers(&self) -> Vec<([u8; 16], u32, bool)> {
        self.cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
                    .map(|(mount, lineage)| {
                        (
                            *lineage,
                            mount.place().layer(),
                            mount.source_site().is_some(),
                        )
                    })
            })
            .collect()
    }


    /// Read-only electrical diagnostic for reached material, in persisted
    /// cohort order: ``(developmental layer, separated elementary charge)``.
    /// This is observer evidence only; cognition never calls it and it does
    /// not inspect the compact resting population or advance state.
    pub(crate) fn observe_reached_neuron_electrical_by_layer(
        &self,
    ) -> Vec<(u32, i128, i128, u128, u128, u128)> {
        self.cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_anatomies())
                    .zip(cohort.state.neurons())
                    .map(|((mount, anatomy), neuron)| {
                        let (capacitance_numerator, capacitance_denominator) =
                            anatomy.capacitance().picofarads().parts();
                        (
                            mount.place().layer(),
                            neuron.membrane_state().separated_elementary_charges(),
                            capacitance_numerator,
                            capacitance_denominator,
                            neuron.carrier_reservoirs().intracellular(),
                            neuron.carrier_reservoirs().extracellular(),
                        )
                    })
            })
            .collect()
    }

    /// Read-only sparse-contact anatomy summarized by canonical endpoint
    /// layer pair. This is observer evidence only and advances no state.
    pub(crate) fn observe_reached_contact_count_by_layer_pair(&self) -> Vec<(u32, u32, usize)> {
        let layer_of = |lineage: [u8; 16]| {
            self.cohorts.iter().find_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
                    .find_map(|(mount, candidate)| {
                        (*candidate == lineage).then_some(mount.place().layer())
                    })
            })
        };
        let mut pairs = Vec::<(u32, u32, usize)>::new();
        let mut admit_pair = |left: u32, right: u32| {
            let (left, right) = if left <= right {
                (left, right)
            } else {
                (right, left)
            };
            if let Some((_, _, count)) =
                pairs.iter_mut().find(|(a, b, _)| *a == left && *b == right)
            {
                *count += 1;
            } else {
                pairs.push((left, right, 1));
            }
        };
        for cohort in &self.cohorts {
            for (left, right) in cohort.anatomy.electrical_anatomy().contact_endpoints() {
                admit_pair(
                    cohort.anatomy.mounts()[left].place().layer(),
                    cohort.anatomy.mounts()[right].place().layer(),
                );
            }
        }
        for (left, right) in self.electrical_fabric.contact_endpoints() {
            if let (Some(left), Some(right)) = (
                layer_of(self.electrical_fabric.lineages()[left]),
                layer_of(self.electrical_fabric.lineages()[right]),
            ) {
                admit_pair(left, right);
            }
        }
        pairs.sort_unstable();
        pairs
    }

    /// Read-only exact retained channel state for every reached sparse
    /// electrical contact. Endpoint lineage plus parallel ordinal is the
    /// stable contact identity; the remaining values are conducting channel
    /// population, bounded transition-work phase, and effective
    /// conductance. Cognition never consumes this projection and reading it
    /// advances no state.
    #[allow(clippy::type_complexity)]
    pub(crate) fn observe_reached_contact_channel_states(
        &self,
    ) -> Vec<([u8; 16], [u8; 16], u32, u128, i128, u128, i128, u128)> {
        let mut observed =
            Vec::<([u8; 16], [u8; 16], u32, u128, i128, u128, i128, u128)>::new();
        let mut admit = |first: [u8; 16],
                         second: [u8; 16],
                         anatomy: crate::sparse_electrical_contact::ElectricalContactAnatomy,
                         state: &crate::sparse_electrical_contact::ElectricalContactState| {
            let (left, right) = if first < second {
                (first, second)
            } else {
                (second, first)
            };
            let parallel_ordinal = u32::try_from(
                observed
                    .iter()
                    .filter(|entry| entry.0 == left && entry.1 == right)
                    .count(),
            )
            .expect("reached contact count fits its persisted ordinal");
            let (transition_phase_numerator, transition_phase_denominator) =
                state.transition_work_phase().parts();
            let (conductance_numerator, conductance_denominator) = anatomy
                .effective_conductance(state)
                .expect("resident contact anatomy and state were validated")
                .parts();
            observed.push((
                left,
                right,
                parallel_ordinal,
                state.conducting_channel_population(),
                transition_phase_numerator,
                transition_phase_denominator,
                conductance_numerator,
                conductance_denominator,
            ));
        };
        for cohort in &self.cohorts {
            for ((left, right), (anatomy, state)) in cohort
                .anatomy
                .electrical_anatomy()
                .contact_endpoints()
                .zip(
                    cohort
                        .anatomy
                        .electrical_anatomy()
                        .contact_anatomies()
                        .iter()
                        .copied()
                        .zip(cohort.state.electrical().contact_states()),
                )
            {
                admit(
                    cohort.anatomy.neuron_lineages()[left],
                    cohort.anatomy.neuron_lineages()[right],
                    anatomy,
                    state,
                );
            }
        }
        for ((left, right), (anatomy, state)) in self
            .electrical_fabric
            .contact_endpoints()
            .zip(
                self.electrical_fabric
                    .anatomy()
                    .contact_anatomies()
                    .iter()
                    .copied()
                    .zip(self.electrical_fabric.state().contact_states()),
            )
        {
            admit(
                self.electrical_fabric.lineages()[left],
                self.electrical_fabric.lineages()[right],
                anatomy,
                state,
            );
        }
        observed.sort_unstable_by_key(|entry| (entry.0, entry.1, entry.2));
        observed
    }

    /// Count reached neurons anchored to one exact declared physical source.
    /// This observes persisted source anatomy only; it assigns no meaning and
    /// advances no state.
    pub(crate) fn observe_reached_source_site_count(
        &self,
        sensor_id: &str,
        substream_id: &str,
    ) -> usize {
        self.cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.source_sites())
            .filter(|site| site.sensor_id() == sensor_id && site.substream_id() == substream_id)
            .count()
    }

    /// Append caller-AUTHORED contacts to the living cohorts.
    ///
    /// This is developmental authorship, not sensation and not inference: the
    /// caller names two of its own declared receptors and the conductance of
    /// the contact between them, exactly as growth DNA does at genesis, and
    /// this boundary only resolves those declared names against the members
    /// that already carry them.  Nothing here reads adjacency, coordinates,
    /// storage order, activity, similarity, or semantics.
    ///
    /// Members, lineages, source sites, physical states, retained mosaics and
    /// the hippocampal index all travel through verbatim; only the contact
    /// list grows, only at its end.  Every authored contact must join two
    /// members of one cohort — a contact between cohorts would be an inferred
    /// connection — and a pair that is already contacted is refused rather
    /// than authored twice.
    pub(crate) fn prepare_authored_contacts(
        &self,
        authored: &[AuthoredDeclaredContact],
        max_encoded_bytes: usize,
    ) -> Result<PreparedCognitiveFormationTransition, FormationError> {
        // No episode is admitted, so — exactly as for nutrition — the
        // hippocampal index is untouched and no publication is required.
        if authored.is_empty() || self.cohorts.is_empty() {
            return Err(FormationError::AuthoredContactUnavailable);
        }
        let source_generation = self
            .generation
            .checked_add(1)
            .ok_or(FormationError::InvalidSourceGeneration)?;
        let mut per_cohort: Vec<Vec<(usize, usize, ExactRational)>> =
            vec![Vec::new(); self.cohorts.len()];
        for contact in authored {
            let mut resolved = None;
            for (cohort_index, cohort) in self.cohorts.iter().enumerate() {
                let left = declared_site_member(
                    &cohort.anatomy,
                    &contact.left_sensor_id,
                    &contact.left_substream_id,
                )?;
                let right = declared_site_member(
                    &cohort.anatomy,
                    &contact.right_sensor_id,
                    &contact.right_substream_id,
                )?;
                if let (Some(left), Some(right)) = (left, right) {
                    if resolved.is_some() {
                        return Err(FormationError::AuthoredContactUnavailable);
                    }
                    resolved = Some((cohort_index, left, right));
                } else if left.is_some() || right.is_some() {
                    // One endpoint resident here and one elsewhere: the
                    // caller named a connection this organism cannot have.
                    return Err(FormationError::AuthoredContactUnavailable);
                }
            }
            let (cohort_index, left, right) =
                resolved.ok_or(FormationError::AuthoredContactUnavailable)?;
            per_cohort[cohort_index].push((left, right, contact.conductance_picosiemens));
        }
        let mut cohorts = self.cohorts.to_vec();
        for (cohort, additions) in cohorts.iter_mut().zip(per_cohort) {
            if additions.is_empty() {
                continue;
            }
            let (anatomy, state) =
                extend_reached_cohort_contacts(&cohort.anatomy, &cohort.state, additions)
                    .map_err(FormationError::PhysicalSettlementUnavailable)?;
            let added = anatomy
                .contact_count()
                .checked_sub(cohort.anatomy.contact_count())
                .ok_or(FormationError::ArithmeticOverflow)?;
            // The rest-state snapshots and per-contact activity masks this
            // cohort retains at its experience boundaries are widened the same
            // way: existing entries verbatim, and each newly authored contact
            // recorded as it truthfully was in that experience — at the
            // authored rest state and NOT active, because it did not exist.
            for evidence in [
                cohort.pending_experience.as_mut(),
                cohort.retained_experience.as_mut(),
            ]
            .into_iter()
            .flatten()
            {
                if let ResidentExperiencePhysicalEvidence::Legacy {
                    predecessor,
                    successor,
                } = &mut evidence.physical
                {
                    *predecessor = Arc::new(
                        widen_reached_cohort_state_contacts(&anatomy, predecessor)
                            .map_err(FormationError::PhysicalSettlementUnavailable)?,
                    );
                    if let Some(post) = successor.as_mut() {
                        *post = Arc::new(
                            widen_reached_cohort_state_contacts(&anatomy, post)
                                .map_err(FormationError::PhysicalSettlementUnavailable)?,
                        );
                    }
                }
                evidence.active_electrical_contacts =
                    extend_contact_mask(&evidence.active_electrical_contacts, added)?;
            }
            if let Some(recurrence) = cohort.pending_recurrence.as_mut() {
                recurrence.active_recurrence_contacts =
                    extend_contact_mask(&recurrence.active_recurrence_contacts, added)?;
            }
            cohort.anatomy = anatomy;
            cohort.state = state.into();
        }
        let topology_index = Arc::new(ResidentTopologyIndex::build(
            &cohorts,
            &self.electrical_fabric,
        )?);
        let successor = Self {
            generation: source_generation,
            next_lineage_ordinal: self.next_lineage_ordinal,
            unexpressed_electrical_seeds: self.unexpressed_electrical_seeds.clone(),
            dormant_lineage_seeds: self.dormant_lineage_seeds.clone(),
            resting_population: self.resting_population.clone(),
            cohorts: cohorts.into_boxed_slice(),
            electrical_fabric: self.electrical_fabric.clone(),
            active_electrical_frontier: self.active_electrical_frontier.clone(),
            preceding_active_electrical_frontier: self.preceding_active_electrical_frontier.clone(),
            older_active_electrical_frontier: self.older_active_electrical_frontier.clone(),
            mosaics: self.mosaics.clone(),
            hippocampal: self.hippocampal,
            topology_index,
        };
        // Every retained mosaic must still be expressible against the grown
        // anatomy, or the growth is refused and the body is left as it is.
        let successor_encoded = successor.encode(max_encoded_bytes)?;
        let summary = successor.summary();
        let mosaic_of_mosaics_count = successor.mosaic_of_mosaics_count()?;
        Ok(PreparedCognitiveFormationTransition {
            predecessor_generation: self.generation,
            predecessor_hippocampal: self.hippocampal,
            successor,
            successor_encoded,
            observation: CognitiveFormationObservation {
                cognitive_ordinal: source_generation,
                trace_formed: false,
                mosaic_formed: None,
                activations: Vec::new(),
                trace_count: summary.trace_count,
                mosaic_count: summary.mosaic_count,
                dsf_delivery_count: 0,
                complete_neuron_count: summary.complete_neuron_count,
                resting_neuron_count: summary.resting_neuron_count,
                physically_transitioned_neuron_count: 0,
                externally_perturbed_body_receptor_count: 0,
                externally_perturbed_neuron_lineages: Vec::new(),
                metabolically_perturbed_body_receptor_count: 0,
                complete_neuron_fractal_count: 0,
                emitted_neuron_fractals: Vec::new(),
                active_physical_bonds: Vec::new(),
                changed_contact_channel_states: Vec::new(),
                physical_frontier_routes: Vec::new(),
                preceding_distinct_physical_frontier_routes: Vec::new(),
                reached_and_foregone_physical_frontier_routes: Vec::new(),
                working_causal_continuations: Vec::new(),
                settled_working_frontier: Vec::new(),
                physical_prediction_alternatives: Vec::new(),
                body_consequence_transfers: Vec::new(),
                affective_balance_trajectories: Vec::new(),
                localized_fluid_chemistry: Vec::new(),
                localized_metabolic_strain_evaluated_body_receptor_lineages: Vec::new(),
                localized_metabolic_strain: Vec::new(),
                organic_mosaic_relations: Vec::new(),
                motor_unit_recruitments: Vec::new(),
                articulatory_unit_recruitments: Vec::new(),
                partial_cue_reassembly_count: 0,
                endogenous_partial_cue_reassembly_count: 0,
                internally_reassembled_formation_cues: Vec::new(),
                externally_reassembled_formation_frontiers: Vec::new(),
                mosaic_of_mosaics_count,
                rest_recovered_neuron_count: 0,
                rest_drained_dissipation_quanta: 0,
                unmet_dissipation_quanta: 0,
                membrane_returned_elementary_charges: 0,
                membrane_unreturned_elementary_charges: summary.energy.separated_elementary_charges,
                metabolic_fuel_quanta: 0,
                nutrition_regenerated_fuel_quanta: 0,
                nutrition_unabsorbed_waste_quanta: 0,
                nutrition_vented_heat_quanta: 0,
                energy: summary.energy,
            },
        })
    }

    pub(crate) fn commit(
        &mut self,
        prepared: PreparedCognitiveFormationTransition,
    ) -> Result<CognitiveFormationObservation, FormationError> {
        let (successor, observation) = prepared
            .try_into_successor(self)
            .map_err(|(error, _)| error)?;
        *self = successor;
        Ok(observation)
    }

    pub(crate) fn encode(&self, max_encoded_bytes: usize) -> Result<Vec<u8>, FormationError> {
        self.encode_with_format(CognitiveCodecFormat::V23, max_encoded_bytes)
    }

    fn encode_with_format(
        &self,
        format: CognitiveCodecFormat,
        max_encoded_bytes: usize,
    ) -> Result<Vec<u8>, FormationError> {
        validate_lineage_state(self)?;
        if matches!(
            format,
            CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
        ) && self
            .older_active_electrical_frontier
            .iter()
            .chain(self.preceding_active_electrical_frontier.iter())
            .chain(self.active_electrical_frontier.iter())
            .any(|entry| entry.cause.is_some_and(|cause| cause.frontier_is_sender))
        {
            return Err(FormationError::NoncanonicalState);
        }
        let mut seeds = Vec::new();
        seeds
            .try_reserve_exact(self.unexpressed_electrical_seeds.len())
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let mut cells = Vec::new();
        cells
            .try_reserve_exact(self.cohorts.len())
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let mut length = FIXED_BYTES;
        for seed in &self.unexpressed_electrical_seeds {
            let encoded = seed
                .encode()
                .map_err(FormationError::DevelopmentalElectricalUnavailable)?;
            length = length
                .checked_add(8)
                .and_then(|value| value.checked_add(encoded.len()))
                .ok_or(FormationError::ArithmeticOverflow)?;
            seeds.push(encoded);
        }
        let mut dormant = Vec::new();
        dormant
            .try_reserve_exact(self.dormant_lineage_seeds.len())
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for seed in &self.dormant_lineage_seeds {
            let encoded = encode_dormant_lineage_seed(seed)?;
            length = length
                .checked_add(8)
                .and_then(|value| value.checked_add(encoded.len()))
                .ok_or(FormationError::ArithmeticOverflow)?;
            dormant.push(encoded);
        }
        let resting_population = match format {
            CognitiveCodecFormat::V15
            | CognitiveCodecFormat::V16
            | CognitiveCodecFormat::V17
            | CognitiveCodecFormat::V18
            | CognitiveCodecFormat::V19
            | CognitiveCodecFormat::V20
            | CognitiveCodecFormat::V21
            | CognitiveCodecFormat::V22
            | CognitiveCodecFormat::V23 => self
                .resting_population
                .as_ref()
                .map(DevelopmentalRestingPopulation::encode)
                .transpose()
                .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?,
            CognitiveCodecFormat::V12 | CognitiveCodecFormat::V13 | CognitiveCodecFormat::V14 => {
                if self.resting_population.is_some() {
                    return Err(FormationError::NoncanonicalState);
                }
                None
            }
        };
        if matches!(
            format,
            CognitiveCodecFormat::V15
                | CognitiveCodecFormat::V16
                | CognitiveCodecFormat::V17
                | CognitiveCodecFormat::V18
                | CognitiveCodecFormat::V19
                | CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
                | CognitiveCodecFormat::V23
        ) {
            length = length
                .checked_add(8)
                .and_then(|value| {
                    resting_population
                        .as_ref()
                        .map_or(Some(value), |population| {
                            value.checked_add(population.len())
                        })
                })
                .ok_or(FormationError::ArithmeticOverflow)?;
        }
        for cohort in &self.cohorts {
            if cohort
                .pending_experience
                .as_ref()
                .is_some_and(|evidence| !evidence.is_pending())
                || cohort
                    .retained_experience
                    .as_ref()
                    .is_some_and(|evidence| !evidence.is_retained())
            {
                return Err(FormationError::NoncanonicalState);
            }
            let cell = match format {
                CognitiveCodecFormat::V12 => {
                    encode_reached_cohort_cell(&cohort.anatomy, &cohort.state)
                }
                CognitiveCodecFormat::V13 => {
                    encode_reached_cohort_cell_v5(&cohort.anatomy, &cohort.state)
                }
                CognitiveCodecFormat::V14 => encode_reached_cohort_cell_v5_with_contact_plasticity(
                    &cohort.anatomy,
                    &cohort.state,
                ),
                CognitiveCodecFormat::V15 => encode_reached_cohort_cell_v5_with_contact_plasticity(
                    &cohort.anatomy,
                    &cohort.state,
                ),
                CognitiveCodecFormat::V16
                | CognitiveCodecFormat::V17
                | CognitiveCodecFormat::V18
                | CognitiveCodecFormat::V19
                | CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
                | CognitiveCodecFormat::V23 => {
                    encode_reached_cohort_cell_v6(&cohort.anatomy, &cohort.state)
                }
            }
            .map_err(|_| FormationError::NoncanonicalState)?;
            let encode_evidence = |evidence: &ResidentExperienceEvidence| {
                encode_experience_evidence_v2(
                    &cohort.anatomy,
                    if format == CognitiveCodecFormat::V12 {
                        None
                    } else {
                        Some(&cohort.state)
                    },
                    evidence,
                    matches!(
                        format,
                        CognitiveCodecFormat::V14
                            | CognitiveCodecFormat::V15
                            | CognitiveCodecFormat::V16
                            | CognitiveCodecFormat::V17
                            | CognitiveCodecFormat::V18
                            | CognitiveCodecFormat::V19
                            | CognitiveCodecFormat::V20
                            | CognitiveCodecFormat::V21
                            | CognitiveCodecFormat::V22
                            | CognitiveCodecFormat::V23
                    ),
                )
            };
            let pending = cohort
                .pending_experience
                .as_ref()
                .map(encode_evidence)
                .transpose()?;
            let retained = cohort
                .retained_experience
                .as_ref()
                .map(encode_evidence)
                .transpose()?;
            let recurrence = cohort
                .pending_recurrence
                .as_ref()
                .map(|evidence| encode_recurrence_evidence(&cohort.anatomy, evidence))
                .transpose()?;
            length = length
                .checked_add(8)
                .and_then(|value| value.checked_add(cell.len()))
                .and_then(|value| value.checked_add(1))
                .and_then(|value| {
                    pending.as_ref().map_or(Some(value), |pending| {
                        value.checked_add(8)?.checked_add(pending.len())
                    })
                })
                .and_then(|value| value.checked_add(1))
                .and_then(|value| {
                    retained.as_ref().map_or(Some(value), |retained| {
                        value.checked_add(8)?.checked_add(retained.len())
                    })
                })
                .and_then(|value| value.checked_add(1))
                .and_then(|value| {
                    recurrence.as_ref().map_or(Some(value), |recurrence| {
                        value.checked_add(8)?.checked_add(recurrence.len())
                    })
                })
                .ok_or(FormationError::ArithmeticOverflow)?;
            cells.push((cell, pending, retained, recurrence));
        }
        if self.mosaics.iter().enumerate().any(|(index, retained)| {
            self.mosaics[..index]
                .iter()
                .any(|prior| prior.mosaic == retained.mosaic)
        }) {
            return Err(FormationError::NoncanonicalState);
        }
        let mosaics = self
            .mosaics
            .iter()
            .map(|retained| {
                encode_retained_organism_mosaic(
                    &self.cohorts,
                    &self.electrical_fabric,
                    retained,
                    max_encoded_bytes,
                )
            })
            .collect::<Result<Vec<_>, _>>()?;
        length = mosaics
            .iter()
            .try_fold(length, |total, mosaic| {
                total.checked_add(8)?.checked_add(mosaic.len())
            })
            .ok_or(FormationError::ArithmeticOverflow)?;
        let electrical_fabric = if matches!(
            format,
            CognitiveCodecFormat::V16
                | CognitiveCodecFormat::V17
                | CognitiveCodecFormat::V18
                | CognitiveCodecFormat::V19
                | CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
                | CognitiveCodecFormat::V23
        ) {
            let encoded = self
                .electrical_fabric
                .encode()
                .map_err(FormationError::ResidentElectricalUnavailable)?;
            length = length
                .checked_add(8)
                .and_then(|value| value.checked_add(encoded.len()))
                .ok_or(FormationError::ArithmeticOverflow)?;
            Some(encoded)
        } else {
            if self.electrical_fabric != ResidentElectricalFabric::default() {
                return Err(FormationError::NoncanonicalState);
            }
            None
        };
        if format == CognitiveCodecFormat::V19 {
            if self
                .active_electrical_frontier
                .iter()
                .any(|entry| entry.cause.is_some())
                || !self.preceding_active_electrical_frontier.is_empty()
                || !self.older_active_electrical_frontier.is_empty()
            {
                return Err(FormationError::NoncanonicalState);
            }
            length = length
                .checked_add(8)
                .and_then(|value| {
                    value.checked_add(self.active_electrical_frontier.len().checked_mul(16)?)
                })
                .ok_or(FormationError::ArithmeticOverflow)?;
        } else if format == CognitiveCodecFormat::V20 {
            if !self.preceding_active_electrical_frontier.is_empty()
                || !self.older_active_electrical_frontier.is_empty()
            {
                return Err(FormationError::NoncanonicalState);
            }
            length = length
                .checked_add(
                    encoded_directed_frontier_len(&self.active_electrical_frontier)
                        .ok_or(FormationError::ArithmeticOverflow)?,
                )
                .ok_or(FormationError::ArithmeticOverflow)?;
        } else if format == CognitiveCodecFormat::V21 {
            if !self.older_active_electrical_frontier.is_empty() {
                return Err(FormationError::NoncanonicalState);
            }
            length = length
                .checked_add(
                    encoded_directed_frontier_len(&self.preceding_active_electrical_frontier)
                        .ok_or(FormationError::ArithmeticOverflow)?,
                )
                .and_then(|value| {
                    value.checked_add(encoded_directed_frontier_len(
                        &self.active_electrical_frontier,
                    )?)
                })
                .ok_or(FormationError::ArithmeticOverflow)?;
        } else if matches!(format, CognitiveCodecFormat::V22 | CognitiveCodecFormat::V23) {
            length = length
                .checked_add(
                    encoded_directed_frontier_len(&self.older_active_electrical_frontier)
                        .ok_or(FormationError::ArithmeticOverflow)?,
                )
                .and_then(|value| {
                    value.checked_add(encoded_directed_frontier_len(
                        &self.preceding_active_electrical_frontier,
                    )?)
                })
                .and_then(|value| {
                    value.checked_add(encoded_directed_frontier_len(
                        &self.active_electrical_frontier,
                    )?)
                })
                .ok_or(FormationError::ArithmeticOverflow)?;
        } else if !self.active_electrical_frontier.is_empty()
            || !self.preceding_active_electrical_frontier.is_empty()
            || !self.older_active_electrical_frontier.is_empty()
        {
            return Err(FormationError::NoncanonicalState);
        }
        if length > max_encoded_bytes {
            return Err(FormationError::BudgetExceeded {
                required: length,
                available: max_encoded_bytes,
            });
        }
        let mut output = Vec::with_capacity(length);
        match format {
            CognitiveCodecFormat::V12 => {
                output.extend_from_slice(MAGIC);
                output.extend_from_slice(&VERSION.to_le_bytes());
            }
            CognitiveCodecFormat::V13 => {
                output.extend_from_slice(MAGIC_V13);
                output.extend_from_slice(&VERSION_V13.to_le_bytes());
            }
            CognitiveCodecFormat::V14 => {
                output.extend_from_slice(MAGIC_V14);
                output.extend_from_slice(&VERSION_V14.to_le_bytes());
            }
            CognitiveCodecFormat::V15 => {
                output.extend_from_slice(MAGIC_V15);
                output.extend_from_slice(&VERSION_V15.to_le_bytes());
            }
            CognitiveCodecFormat::V16 => {
                output.extend_from_slice(MAGIC_V16);
                output.extend_from_slice(&VERSION_V16.to_le_bytes());
            }
            CognitiveCodecFormat::V17 => {
                output.extend_from_slice(MAGIC_V17);
                output.extend_from_slice(&VERSION_V17.to_le_bytes());
            }
            CognitiveCodecFormat::V18 => {
                output.extend_from_slice(MAGIC_V18);
                output.extend_from_slice(&VERSION_V18.to_le_bytes());
            }
            CognitiveCodecFormat::V19 => {
                output.extend_from_slice(MAGIC_V19);
                output.extend_from_slice(&VERSION_V19.to_le_bytes());
            }
            CognitiveCodecFormat::V20 => {
                output.extend_from_slice(MAGIC_V20);
                output.extend_from_slice(&VERSION_V20.to_le_bytes());
            }
            CognitiveCodecFormat::V21 => {
                output.extend_from_slice(MAGIC_V21);
                output.extend_from_slice(&VERSION_V21.to_le_bytes());
            }
            CognitiveCodecFormat::V22 => {
                output.extend_from_slice(MAGIC_V22);
                output.extend_from_slice(&VERSION_V22.to_le_bytes());
            }
            CognitiveCodecFormat::V23 => {
                output.extend_from_slice(MAGIC_V23);
                output.extend_from_slice(&VERSION_V23.to_le_bytes());
            }
        }
        output.extend_from_slice(&self.generation.to_le_bytes());
        output.extend_from_slice(&self.next_lineage_ordinal.to_le_bytes());
        output.extend_from_slice(
            &u64::try_from(seeds.len())
                .map_err(|_| FormationError::ArithmeticOverflow)?
                .to_le_bytes(),
        );
        for seed in seeds {
            output.extend_from_slice(
                &u64::try_from(seed.len())
                    .map_err(|_| FormationError::ArithmeticOverflow)?
                    .to_le_bytes(),
            );
            output.extend_from_slice(&seed);
        }
        output.extend_from_slice(
            &u64::try_from(dormant.len())
                .map_err(|_| FormationError::ArithmeticOverflow)?
                .to_le_bytes(),
        );
        for seed in dormant {
            push_length(&mut output, seed.len())?;
            output.extend_from_slice(&seed);
        }
        if matches!(
            format,
            CognitiveCodecFormat::V15
                | CognitiveCodecFormat::V16
                | CognitiveCodecFormat::V17
                | CognitiveCodecFormat::V18
                | CognitiveCodecFormat::V19
                | CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
                | CognitiveCodecFormat::V23
        ) {
            push_length(&mut output, resting_population.as_ref().map_or(0, Vec::len))?;
            if let Some(population) = resting_population {
                output.extend_from_slice(&population);
            }
        }
        if matches!(
            format,
            CognitiveCodecFormat::V16
                | CognitiveCodecFormat::V17
                | CognitiveCodecFormat::V18
                | CognitiveCodecFormat::V19
                | CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
                | CognitiveCodecFormat::V23
        ) {
            let electrical_fabric = electrical_fabric.ok_or(FormationError::NoncanonicalState)?;
            push_length(&mut output, electrical_fabric.len())?;
            output.extend_from_slice(&electrical_fabric);
        }
        if format == CognitiveCodecFormat::V19 {
            push_length(&mut output, self.active_electrical_frontier.len())?;
            for entry in &self.active_electrical_frontier {
                output.extend_from_slice(&entry.receiver());
            }
        } else if format == CognitiveCodecFormat::V20 {
            encode_directed_frontier(&self.active_electrical_frontier, &mut output)?;
        } else if format == CognitiveCodecFormat::V21 {
            encode_directed_frontier(&self.preceding_active_electrical_frontier, &mut output)?;
            encode_directed_frontier(&self.active_electrical_frontier, &mut output)?;
        } else if matches!(format, CognitiveCodecFormat::V22 | CognitiveCodecFormat::V23) {
            encode_directed_frontier(&self.older_active_electrical_frontier, &mut output)?;
            encode_directed_frontier(&self.preceding_active_electrical_frontier, &mut output)?;
            encode_directed_frontier(&self.active_electrical_frontier, &mut output)?;
        }
        output.extend_from_slice(
            &u64::try_from(cells.len())
                .map_err(|_| FormationError::ArithmeticOverflow)?
                .to_le_bytes(),
        );
        for (cell, pending, retained, recurrence) in cells {
            output.extend_from_slice(
                &u64::try_from(cell.len())
                    .map_err(|_| FormationError::ArithmeticOverflow)?
                    .to_le_bytes(),
            );
            output.extend_from_slice(&cell);
            output.push(u8::from(pending.is_some()));
            if let Some(pending) = pending {
                output.extend_from_slice(
                    &u64::try_from(pending.len())
                        .map_err(|_| FormationError::ArithmeticOverflow)?
                        .to_le_bytes(),
                );
                output.extend_from_slice(&pending);
            }
            output.push(u8::from(retained.is_some()));
            if let Some(retained) = retained {
                output.extend_from_slice(
                    &u64::try_from(retained.len())
                        .map_err(|_| FormationError::ArithmeticOverflow)?
                        .to_le_bytes(),
                );
                output.extend_from_slice(&retained);
            }
            output.push(u8::from(recurrence.is_some()));
            if let Some(recurrence) = recurrence {
                push_length(&mut output, recurrence.len())?;
                output.extend_from_slice(&recurrence);
            }
        }
        push_length(&mut output, mosaics.len())?;
        for mosaic in mosaics {
            push_length(&mut output, mosaic.len())?;
            output.extend_from_slice(&mosaic);
        }
        let hippocampal = self
            .hippocampal
            .encode()
            .map_err(FormationError::HippocampalCheckpointUnavailable)?;
        if hippocampal.len() != HIPPOCAMPAL_CHECKPOINT_BYTES {
            return Err(FormationError::NoncanonicalState);
        }
        push_length(&mut output, hippocampal.len())?;
        output.extend_from_slice(&hippocampal);
        if output.len() != length {
            return Err(FormationError::NoncanonicalState);
        }
        Ok(output)
    }

    pub(crate) fn encode_successor(
        &self,
        prepared: &PreparedCognitiveFormationTransition,
        max_encoded_bytes: usize,
    ) -> Result<Vec<u8>, FormationError> {
        if self.generation != prepared.predecessor_generation {
            return Err(FormationError::PreparedPredecessorChanged);
        }
        if prepared.successor_encoded.len() > max_encoded_bytes {
            return Err(FormationError::BudgetExceeded {
                required: prepared.successor_encoded.len(),
                available: max_encoded_bytes,
            });
        }
        Ok(prepared.successor_encoded.clone())
    }

    /// The retired archive checkpoint must survive a transition byte-for-byte.
    /// Nothing writes it, so a successor whose checkpoint differs from its
    /// predecessor's is a codec fault, not a lawful advance.
    pub(crate) fn encode_staged_successor(
        &self,
        prepared: &PreparedCognitiveFormationTransition,
        max_encoded_bytes: usize,
    ) -> Result<Vec<u8>, FormationError> {
        if self.generation != prepared.predecessor_generation {
            return Err(FormationError::PreparedPredecessorChanged);
        }
        if prepared.successor.hippocampal != prepared.predecessor_hippocampal {
            return Err(FormationError::NoncanonicalState);
        }
        if prepared.successor_encoded.len() > max_encoded_bytes {
            return Err(FormationError::BudgetExceeded {
                required: prepared.successor_encoded.len(),
                available: max_encoded_bytes,
            });
        }
        Ok(prepared.successor_encoded.clone())
    }

    pub(crate) fn decode(bytes: &[u8], max_encoded_bytes: usize) -> Result<Self, FormationError> {
        Self::decode_with_canonicality(bytes, max_encoded_bytes, true)
    }

    fn decode_for_one_way_migration(
        bytes: &[u8],
        max_encoded_bytes: usize,
    ) -> Result<Self, FormationError> {
        Self::decode_with_canonicality(bytes, max_encoded_bytes, false)
    }

    fn decode_with_canonicality(
        bytes: &[u8],
        max_encoded_bytes: usize,
        require_current_canonical_encoding: bool,
    ) -> Result<Self, FormationError> {
        if bytes.len() > max_encoded_bytes {
            return Err(FormationError::BudgetExceeded {
                required: bytes.len(),
                available: max_encoded_bytes,
            });
        }
        let format = if bytes.len() >= MAGIC_V23.len() && &bytes[..MAGIC_V23.len()] == MAGIC_V23 {
            CognitiveCodecFormat::V23
        } else if bytes.len() >= MAGIC_V22.len() && &bytes[..MAGIC_V22.len()] == MAGIC_V22 {
            CognitiveCodecFormat::V22
        } else if bytes.len() >= MAGIC_V21.len() && &bytes[..MAGIC_V21.len()] == MAGIC_V21 {
            CognitiveCodecFormat::V21
        } else if bytes.len() >= MAGIC_V20.len() && &bytes[..MAGIC_V20.len()] == MAGIC_V20 {
            CognitiveCodecFormat::V20
        } else if bytes.len() >= MAGIC_V19.len() && &bytes[..MAGIC_V19.len()] == MAGIC_V19 {
            CognitiveCodecFormat::V19
        } else if bytes.len() >= MAGIC_V18.len() && &bytes[..MAGIC_V18.len()] == MAGIC_V18 {
            CognitiveCodecFormat::V18
        } else if bytes.len() >= MAGIC_V17.len() && &bytes[..MAGIC_V17.len()] == MAGIC_V17 {
            CognitiveCodecFormat::V17
        } else if bytes.len() >= MAGIC_V16.len() && &bytes[..MAGIC_V16.len()] == MAGIC_V16 {
            CognitiveCodecFormat::V16
        } else if bytes.len() >= MAGIC_V15.len() && &bytes[..MAGIC_V15.len()] == MAGIC_V15 {
            CognitiveCodecFormat::V15
        } else if bytes.len() >= MAGIC_V14.len() && &bytes[..MAGIC_V14.len()] == MAGIC_V14 {
            CognitiveCodecFormat::V14
        } else if bytes.len() >= MAGIC_V13.len() && &bytes[..MAGIC_V13.len()] == MAGIC_V13 {
            CognitiveCodecFormat::V13
        } else if bytes.len() >= MAGIC.len() && &bytes[..MAGIC.len()] == MAGIC {
            CognitiveCodecFormat::V12
        } else if bytes.len() >= MAGIC.len() {
            return Err(FormationError::RetiredCognitiveState);
        } else {
            return Err(FormationError::NoncanonicalState);
        };
        if bytes.len() < FIXED_BYTES {
            return Err(FormationError::NoncanonicalState);
        }
        let mut cursor = MAGIC.len();
        let version = u16::from_le_bytes(
            bytes[cursor..cursor + 2]
                .try_into()
                .map_err(|_| FormationError::NoncanonicalState)?,
        );
        cursor += 2;
        let expected_version = match format {
            CognitiveCodecFormat::V12 => VERSION,
            CognitiveCodecFormat::V13 => VERSION_V13,
            CognitiveCodecFormat::V14 => VERSION_V14,
            CognitiveCodecFormat::V15 => VERSION_V15,
            CognitiveCodecFormat::V16 => VERSION_V16,
            CognitiveCodecFormat::V17 => VERSION_V17,
            CognitiveCodecFormat::V18 => VERSION_V18,
            CognitiveCodecFormat::V19 => VERSION_V19,
            CognitiveCodecFormat::V20 => VERSION_V20,
            CognitiveCodecFormat::V21 => VERSION_V21,
            CognitiveCodecFormat::V22 => VERSION_V22,
            CognitiveCodecFormat::V23 => VERSION_V23,
        };
        if version != expected_version {
            return Err(FormationError::BadVersion);
        }
        let generation = take_state_u64(bytes, &mut cursor)?;
        let next_lineage_ordinal = take_state_u64(bytes, &mut cursor)?;
        let seed_count = usize::try_from(u64::from_le_bytes(
            bytes[cursor..cursor + 8]
                .try_into()
                .map_err(|_| FormationError::NoncanonicalState)?,
        ))
        .map_err(|_| FormationError::ArithmeticOverflow)?;
        cursor += 8;
        if seed_count > bytes.len().saturating_sub(cursor) / 8 {
            return Err(FormationError::NoncanonicalState);
        }
        let mut unexpressed_electrical_seeds = Vec::new();
        unexpressed_electrical_seeds
            .try_reserve_exact(seed_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for _ in 0..seed_count {
            let length_end = cursor
                .checked_add(8)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let seed_length = usize::try_from(u64::from_le_bytes(
                bytes
                    .get(cursor..length_end)
                    .ok_or(FormationError::NoncanonicalState)?
                    .try_into()
                    .map_err(|_| FormationError::NoncanonicalState)?,
            ))
            .map_err(|_| FormationError::ArithmeticOverflow)?;
            cursor = length_end;
            let seed_end = cursor
                .checked_add(seed_length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let seed = DevelopmentalElectricalSeed::decode(
                bytes
                    .get(cursor..seed_end)
                    .ok_or(FormationError::NoncanonicalState)?,
            )
            .map_err(FormationError::DevelopmentalElectricalUnavailable)?;
            cursor = seed_end;
            if unexpressed_electrical_seeds
                .iter()
                .any(|prior: &DevelopmentalElectricalSeed| {
                    prior.source_sites() == seed.source_sites()
                })
            {
                return Err(FormationError::DuplicateDevelopmentalSeed);
            }
            unexpressed_electrical_seeds.push(seed);
        }
        let dormant_count = read_length(bytes, &mut cursor)?;
        if dormant_count > bytes.len().saturating_sub(cursor) / 8 {
            return Err(FormationError::NoncanonicalState);
        }
        let mut dormant_lineage_seeds = Vec::new();
        dormant_lineage_seeds
            .try_reserve_exact(dormant_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for _ in 0..dormant_count {
            let seed_length = read_length(bytes, &mut cursor)?;
            let seed_end = cursor
                .checked_add(seed_length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let seed = decode_dormant_lineage_seed(
                bytes
                    .get(cursor..seed_end)
                    .ok_or(FormationError::NoncanonicalState)?,
            )?;
            cursor = seed_end;
            if dormant_lineage_seeds
                .last()
                .is_some_and(|prior| prior >= &seed)
            {
                return Err(FormationError::NoncanonicalState);
            }
            dormant_lineage_seeds.push(seed);
        }
        let resting_population = if matches!(
            format,
            CognitiveCodecFormat::V15
                | CognitiveCodecFormat::V16
                | CognitiveCodecFormat::V17
                | CognitiveCodecFormat::V18
                | CognitiveCodecFormat::V19
                | CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
                | CognitiveCodecFormat::V23
        ) {
            let population_length = read_length(bytes, &mut cursor)?;
            if population_length == 0 {
                None
            } else {
                let population_end = cursor
                    .checked_add(population_length)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let population = DevelopmentalRestingPopulation::decode(
                    bytes
                        .get(cursor..population_end)
                        .ok_or(FormationError::NoncanonicalState)?,
                )
                .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?;
                cursor = population_end;
                Some(population)
            }
        } else {
            None
        };
        let electrical_fabric = if matches!(
            format,
            CognitiveCodecFormat::V16
                | CognitiveCodecFormat::V17
                | CognitiveCodecFormat::V18
                | CognitiveCodecFormat::V19
                | CognitiveCodecFormat::V20
                | CognitiveCodecFormat::V21
                | CognitiveCodecFormat::V22
                | CognitiveCodecFormat::V23
        ) {
            let fabric_length = read_length(bytes, &mut cursor)?;
            let fabric_end = cursor
                .checked_add(fabric_length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let fabric = ResidentElectricalFabric::decode(
                bytes
                    .get(cursor..fabric_end)
                    .ok_or(FormationError::NoncanonicalState)?,
            )
            .map_err(FormationError::ResidentElectricalUnavailable)?;
            cursor = fabric_end;
            fabric
        } else {
            ResidentElectricalFabric::default()
        };
        let (
            older_active_electrical_frontier,
            preceding_active_electrical_frontier,
            active_electrical_frontier,
        ) = if format == CognitiveCodecFormat::V19 {
            let count = read_length(bytes, &mut cursor)?;
            let frontier_end = cursor
                .checked_add(
                    count
                        .checked_mul(16)
                        .ok_or(FormationError::ArithmeticOverflow)?,
                )
                .ok_or(FormationError::ArithmeticOverflow)?;
            let encoded = bytes
                .get(cursor..frontier_end)
                .ok_or(FormationError::NoncanonicalState)?;
            cursor = frontier_end;
            let mut frontier = Vec::new();
            frontier
                .try_reserve_exact(count)
                .map_err(|_| FormationError::ArithmeticOverflow)?;
            for lineage in encoded.chunks_exact(16) {
                frontier.push(ActiveElectricalFrontierEntry::legacy_receiver(
                    lineage
                        .try_into()
                        .map_err(|_| FormationError::NoncanonicalState)?,
                ));
            }
            (Vec::new(), Vec::new(), frontier)
        } else if format == CognitiveCodecFormat::V20 {
            (
                Vec::new(),
                Vec::new(),
                decode_directed_frontier(bytes, &mut cursor, false)?,
            )
        } else if format == CognitiveCodecFormat::V21 {
            let preceding = decode_directed_frontier(bytes, &mut cursor, false)?;
            let active = decode_directed_frontier(bytes, &mut cursor, false)?;
            (Vec::new(), preceding, active)
        } else if matches!(format, CognitiveCodecFormat::V22 | CognitiveCodecFormat::V23) {
            let allow_sender_frontier = format == CognitiveCodecFormat::V23;
            let older = decode_directed_frontier(bytes, &mut cursor, allow_sender_frontier)?;
            let preceding = decode_directed_frontier(bytes, &mut cursor, allow_sender_frontier)?;
            let active = decode_directed_frontier(bytes, &mut cursor, allow_sender_frontier)?;
            (older, preceding, active)
        } else {
            (Vec::new(), Vec::new(), Vec::new())
        };
        let cohort_count_end = cursor
            .checked_add(8)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let cohort_count = usize::try_from(u64::from_le_bytes(
            bytes
                .get(cursor..cohort_count_end)
                .ok_or(FormationError::NoncanonicalState)?
                .try_into()
                .map_err(|_| FormationError::NoncanonicalState)?,
        ))
        .map_err(|_| FormationError::ArithmeticOverflow)?;
        cursor = cohort_count_end;
        if cohort_count > bytes.len().saturating_sub(cursor) / 9 {
            return Err(FormationError::NoncanonicalState);
        }
        let mut cohorts = Vec::new();
        cohorts
            .try_reserve_exact(cohort_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for _ in 0..cohort_count {
            let length_end = cursor
                .checked_add(8)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let cell_length = usize::try_from(u64::from_le_bytes(
                bytes
                    .get(cursor..length_end)
                    .ok_or(FormationError::NoncanonicalState)?
                    .try_into()
                    .map_err(|_| FormationError::NoncanonicalState)?,
            ))
            .map_err(|_| FormationError::ArithmeticOverflow)?;
            cursor = length_end;
            let cell_end = cursor
                .checked_add(cell_length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let (anatomy, state) = decode_reached_cohort_cell(
                bytes
                    .get(cursor..cell_end)
                    .ok_or(FormationError::NoncanonicalState)?,
            )
            .map_err(FormationError::PhysicalSettlementUnavailable)?;
            cursor = cell_end;
            let pending_experience =
                decode_optional_experience_evidence(bytes, &mut cursor, &anatomy, &state, false)?;
            let retained_experience =
                decode_optional_experience_evidence(bytes, &mut cursor, &anatomy, &state, true)?;
            let pending_recurrence =
                decode_optional_recurrence_evidence(bytes, &mut cursor, &anatomy)?;
            cohorts.push(ResidentReachedCohort {
                anatomy,
                state: state.into(),
                pending_experience,
                retained_experience,
                pending_recurrence,
            });
        }
        let mosaic_count = read_length(bytes, &mut cursor)?;
        if mosaic_count > bytes.len().saturating_sub(cursor) / 8 {
            return Err(FormationError::NoncanonicalState);
        }
        let mut mosaics = Vec::new();
        mosaics
            .try_reserve_exact(mosaic_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for _ in 0..mosaic_count {
            let mosaic_length = read_length(bytes, &mut cursor)?;
            let mosaic_end = cursor
                .checked_add(mosaic_length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let retained = decode_retained_organism_mosaic(
                &cohorts,
                &electrical_fabric,
                bytes
                    .get(cursor..mosaic_end)
                    .ok_or(FormationError::NoncanonicalState)?,
                max_encoded_bytes,
            )?;
            cursor = mosaic_end;
            if mosaics
                .iter()
                .any(|prior: &RetainedOrganismMosaic| prior.mosaic == retained.mosaic)
            {
                return Err(FormationError::NoncanonicalState);
            }
            mosaics.push(retained);
        }
        let hippocampal_length = read_length(bytes, &mut cursor)?;
        if hippocampal_length != HIPPOCAMPAL_CHECKPOINT_BYTES {
            return Err(FormationError::NoncanonicalState);
        }
        let hippocampal_end = cursor
            .checked_add(hippocampal_length)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let hippocampal = ResidentHippocampalIndex::decode(
            bytes
                .get(cursor..hippocampal_end)
                .ok_or(FormationError::NoncanonicalState)?,
        )
        .map_err(FormationError::HippocampalCheckpointUnavailable)?;
        cursor = hippocampal_end;
        if cursor != bytes.len() {
            return Err(FormationError::NoncanonicalState);
        }
        let mut state = Self {
            generation,
            next_lineage_ordinal,
            unexpressed_electrical_seeds: unexpressed_electrical_seeds.into_boxed_slice(),
            dormant_lineage_seeds: dormant_lineage_seeds.into_boxed_slice(),
            resting_population,
            cohorts: cohorts.into_boxed_slice(),
            electrical_fabric,
            active_electrical_frontier: active_electrical_frontier.into_boxed_slice(),
            preceding_active_electrical_frontier: preceding_active_electrical_frontier
                .into_boxed_slice(),
            older_active_electrical_frontier: older_active_electrical_frontier.into_boxed_slice(),
            mosaics: mosaics.into_boxed_slice(),
            hippocampal,
            topology_index: Arc::new(ResidentTopologyIndex::empty()),
        };
        validate_lineage_state(&state)?;
        let canonical = state.encode_with_format(format, max_encoded_bytes)?;
        if require_current_canonical_encoding && canonical != bytes {
            return Err(FormationError::NoncanonicalState);
        }
        state.topology_index = Arc::new(ResidentTopologyIndex::build(
            &state.cohorts,
            &state.electrical_fabric,
        )?);
        // Old evidence is admitted only long enough to prove its historical
        // canonical bytes. The live resident keeps reached members only.
        for cohort in state.cohorts.iter_mut() {
            if let Some(evidence) = cohort.pending_experience.as_mut() {
                evidence.convert_legacy_physical(&cohort.anatomy, false)?;
            }
            if let Some(evidence) = cohort.retained_experience.as_mut() {
                evidence.convert_legacy_physical(&cohort.anatomy, true)?;
            }
        }
        // Legacy retained-mosaic bodies deliberately carry no cached
        // recurrent lineage. First prove their byte-exact canonical form;
        // only then reconstruct the runtime index from the one unique global
        // member-contact matching. Current GLMRC02 entries are already bound
        // and merely participate as claimed physical endpoints here.
        resolve_unpersisted_recurrent_retention(
            &state.cohorts,
            &state.electrical_fabric,
            &mut state.mosaics,
        )?;
        Ok(state)
    }

    /// Rewrite one already-admitted body into the current layout. V18 marks
    /// the one-way correction from gate-count carrier volume to declared
    /// membrane-territory carrier volume. V17 cannot be that authority: the
    /// task-975 startup path proved an ordinary transition could write V17
    /// before the migration ran. Existing V18 bodies are never corrected
    /// twice. Older bodies also receive the compact developmental resting
    /// population when it is absent.
    pub(crate) fn migrate_to_current_format(
        bytes: &[u8],
        max_encoded_bytes: usize,
    ) -> Result<Vec<u8>, FormationError> {
        let already_geometry_provisioned = bytes.len() >= MAGIC_V18.len()
            && (&bytes[..MAGIC_V18.len()] == MAGIC_V18
                || &bytes[..MAGIC_V19.len()] == MAGIC_V19
                || &bytes[..MAGIC_V20.len()] == MAGIC_V20
                || &bytes[..MAGIC_V21.len()] == MAGIC_V21
                || &bytes[..MAGIC_V22.len()] == MAGIC_V22
                || &bytes[..MAGIC_V23.len()] == MAGIC_V23);
        let state = Self::decode_for_one_way_migration(bytes, max_encoded_bytes)?;
        let state = if already_geometry_provisioned {
            state
        } else {
            state.into_geometry_provisioned_carrier_material()?
        };
        if state.resting_population.is_some() {
            return state.encode(max_encoded_bytes);
        }

        // Measure the exact current reached body in the immediately preceding
        // V14 cell layout.  Population admission then reserves one complete
        // independently diverged cell plus one sparse contact per declared
        // resting cell, while retaining one further unit for future growth.
        let predecessor = state.encode_with_format(CognitiveCodecFormat::V14, max_encoded_bytes)?;
        let mut occupied_places = state
            .cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.mounts().iter())
            .map(ReachedNeuronMount::place)
            .collect::<Vec<_>>();
        occupied_places.extend(
            state
                .dormant_lineage_seeds
                .iter()
                .map(|seed| DeclaredNeuronPlace::new(u32::from(seed.sense), seed.topology_index)),
        );
        let population = DevelopmentalRestingPopulation::admit(
            max_encoded_bytes,
            predecessor.len(),
            state.next_lineage_ordinal,
            &occupied_places,
        )
        .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?;
        let next_lineage_ordinal = population.lineage_end_exclusive();
        let successor = Self {
            next_lineage_ordinal,
            resting_population: Some(population),
            ..state
        };
        validate_lineage_state(&successor)?;
        successor.encode(max_encoded_bytes)
    }
}

struct ResidentOpticalIntervalOutcome {
    emitted_neuron_fractals: Vec<EmittedNeuronFractal>,
    mosaic_formed: Option<[u8; 32]>,
    /// How this interval's admitted reassembly, if any, relates to the
    /// retained mosaic references under the R1 structural-identity boundary.
    mosaic_resolutions: Vec<MosaicStructuralResolution>,
    partial_cue_reassembly_count: usize,
    endogenous_partial_cue_reassembly_count: usize,
    /// What the rest metabolism did on this interval (zero on every interval
    /// that carried exogenous stimulus energy).
    metabolic: ReachedCohortMetabolicObservation,
}

/// Exact retained-formation resolution.  Identity is the original retained
/// neuronal deltas and their original physical bonds, never the member set.
/// The same neurons may participate in many different formations.  A later
/// cue or recurrence path may vary while reassembling the same retained
/// structure, so those later-path facts do not mint a duplicate formation.
#[derive(Clone, Debug, Eq, PartialEq)]
enum MosaicStructuralResolution {
    /// No retained formation carries the same exact original structure.
    NewFormation(AdmittedPhysicalMosaic),
    /// The exact original retained neuronal structure already exists.
    Reinforces { mosaic_index: usize },
}

/// Resolve one admitted reassembly against retained physical formations.
fn resolve_mosaic_structural_identity(
    existing: &[RetainedOrganismMosaic],
    candidate: AdmittedPhysicalMosaic,
) -> MosaicStructuralResolution {
    if let Some(mosaic_index) = existing
        .iter()
        .position(|prior| prior.mosaic.same_retained_structure(&candidate))
    {
        return MosaicStructuralResolution::Reinforces { mosaic_index };
    }
    MosaicStructuralResolution::NewFormation(candidate)
}

/// Apply one exact retained-formation resolution.
fn apply_mosaic_structural_resolution(
    mosaics: &mut Vec<RetainedOrganismMosaic>,
    resolution: MosaicStructuralResolution,
) -> Result<(), FormationError> {
    match resolution {
        MosaicStructuralResolution::NewFormation(mosaic) => {
            mosaics
                .try_reserve(1)
                .map_err(|_| FormationError::ArithmeticOverflow)?;
            mosaics.push(RetainedOrganismMosaic::newly_admitted(mosaic));
        }
        MosaicStructuralResolution::Reinforces { mosaic_index } => {
            mosaics
                .get(mosaic_index)
                .ok_or(FormationError::NoncanonicalState)?;
        }
    }
    Ok(())
}

fn extend_resident_cohort_evidence(
    cohort: &mut ResidentReachedCohort,
    predecessor_anatomy: &ReachedCohortAnatomy,
    successor_anatomy: ReachedCohortAnatomy,
    successor_state: ReachedCohortState,
    predecessor_neuron_count: usize,
) -> Result<(), FormationError> {
    let genesis_states = successor_state
        .neurons()
        .get(predecessor_neuron_count..)
        .ok_or(FormationError::NoncanonicalState)?;
    let extend_experience = |evidence: &mut ResidentExperienceEvidence| {
        if let ResidentExperiencePhysicalEvidence::Legacy {
            predecessor,
            successor,
        } = &mut evidence.physical
        {
            *predecessor = Arc::new(
                extend_reached_cohort_state_with_genesis(
                    predecessor_anatomy,
                    predecessor,
                    &successor_anatomy,
                    genesis_states,
                )
                .map_err(FormationError::PhysicalSettlementUnavailable)?,
            );
            *successor = successor
                .as_ref()
                .map(|state| {
                    extend_reached_cohort_state_with_genesis(
                        predecessor_anatomy,
                        state,
                        &successor_anatomy,
                        genesis_states,
                    )
                    .map(Arc::new)
                    .map_err(FormationError::PhysicalSettlementUnavailable)
                })
                .transpose()?;
        }
        if !evidence
            .gate_work_perturbed_neurons
            .validates_width(successor_anatomy.neuron_count())
        {
            return Err(FormationError::NoncanonicalState);
        }
        let mut excitation = evidence.receptor_excitation_zeptojoules.to_vec();
        excitation.resize(successor_anatomy.neuron_count(), None);
        evidence.receptor_excitation_zeptojoules = excitation.into_boxed_slice();
        let mut retained_change = evidence.retained_change_neurons.to_vec();
        retained_change.resize(successor_anatomy.neuron_count(), false);
        evidence.retained_change_neurons = retained_change.into_boxed_slice();
        let mut settled = evidence.retentively_settled_neurons.to_vec();
        settled.resize(successor_anatomy.neuron_count(), false);
        evidence.retentively_settled_neurons = settled.into_boxed_slice();
        Ok::<(), FormationError>(())
    };
    if let Some(evidence) = cohort.pending_experience.as_mut() {
        extend_experience(evidence)?;
    }
    if let Some(evidence) = cohort.retained_experience.as_mut() {
        extend_experience(evidence)?;
    }
    if let Some(recurrence) = cohort.pending_recurrence.as_mut() {
        recurrence.carries_physical_change_codec = true;
        if !recurrence
            .gate_work_perturbed_neurons
            .validates_width(successor_anatomy.neuron_count())
        {
            return Err(FormationError::NoncanonicalState);
        }
        let mut excitation = recurrence.receptor_excitation_zeptojoules.to_vec();
        excitation.resize(successor_anatomy.neuron_count(), None);
        recurrence.receptor_excitation_zeptojoules = excitation.into_boxed_slice();
        let mut changed = recurrence.physically_changed_neurons.to_vec();
        changed.resize(successor_anatomy.neuron_count(), false);
        recurrence.physically_changed_neurons = changed.into_boxed_slice();
    }
    cohort.anatomy = successor_anatomy;
    cohort.state = successor_state.into();
    Ok(())
}

fn extend_resident_cohort_positional_fabrics(
    cohort: &mut ResidentReachedCohort,
    required_positions: &[usize],
) -> Result<(), FormationError> {
    let predecessor_anatomy = cohort.anatomy.clone();
    let (successor_anatomy, successor_state) = extend_reached_cohort_positional_fabrics(
        &predecessor_anatomy,
        &cohort.state,
        required_positions,
    )
    .map_err(FormationError::PhysicalSettlementUnavailable)?;
    if successor_anatomy == predecessor_anatomy {
        return Ok(());
    }
    let extend_state = |state: &ReachedCohortState| {
        let (derived_anatomy, derived_state) = extend_reached_cohort_positional_fabrics(
            &predecessor_anatomy,
            state,
            required_positions,
        )
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
        if derived_anatomy != successor_anatomy {
            return Err(FormationError::NoncanonicalState);
        }
        Ok::<ReachedCohortState, FormationError>(derived_state)
    };
    let extend_experience = |evidence: &mut ResidentExperienceEvidence| {
        match &mut evidence.physical {
            ResidentExperiencePhysicalEvidence::Legacy {
                predecessor,
                successor,
            } => {
                *predecessor = extend_state(predecessor)?.into();
                *successor = successor
                    .as_ref()
                    .map(|state| extend_state(state).map(Arc::new))
                    .transpose()?;
            }
            ResidentExperiencePhysicalEvidence::Pending(members) => {
                for member in members.iter_mut() {
                    let neuron_index = member.neuron_index;
                    let (_, state) = extend_neuron_positional_fabric(
                        &predecessor_anatomy.neuron_anatomies()[neuron_index],
                        &member.predecessor,
                        successor_anatomy.neuron_anatomies()[neuron_index]
                            .mathloom_positions(),
                    )
                    .map_err(|error| {
                        FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                            neuron_index,
                            error,
                        })
                    })?;
                    member.predecessor = state;
                }
            }
            ResidentExperiencePhysicalEvidence::Retained(members) => {
                for member in members.iter_mut() {
                    let neuron_index = member.neuron_index;
                    let required_positions = successor_anatomy.neuron_anatomies()[neuron_index]
                        .mathloom_positions();
                    let (_, predecessor) = extend_neuron_positional_fabric(
                        &predecessor_anatomy.neuron_anatomies()[neuron_index],
                        &member.predecessor,
                        required_positions,
                    )
                    .map_err(|error| {
                        FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                            neuron_index,
                            error,
                        })
                    })?;
                    let (_, learned) = extend_neuron_positional_fabric(
                        &predecessor_anatomy.neuron_anatomies()[neuron_index],
                        &member.learned,
                        required_positions,
                    )
                    .map_err(|error| {
                        FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                            neuron_index,
                            error,
                        })
                    })?;
                    member.delta = sparse_retained_physical_state_delta(&predecessor, &learned)
                        .map_err(|error| {
                            FormationError::PhysicalSettlementUnavailable(
                                ReachedCohortError::Neuron {
                                    neuron_index,
                                    error,
                                },
                            )
                        })?
                        .ok_or(FormationError::NoncanonicalState)?;
                    member.predecessor = predecessor;
                    member.learned = learned;
                }
            }
        }
        Ok::<(), FormationError>(())
    };
    if let Some(evidence) = cohort.pending_experience.as_mut() {
        extend_experience(evidence)?;
    }
    if let Some(evidence) = cohort.retained_experience.as_mut() {
        extend_experience(evidence)?;
    }
    cohort.anatomy = successor_anatomy;
    cohort.state = successor_state.into();
    Ok(())
}

/// Extend only the causally selected members.  Ordinary already-provisioned
/// intervals return before constructing a cohort-width requirements vector or
/// cloning any cohort anatomy/state.  The complete vector is materialized only
/// for a real topology-growth event because the recovery-fluid anatomy changes
/// with that growth and must still be rebuilt atomically by its existing law.
fn extend_resident_cohort_selected_positional_fabrics(
    cohort: &mut ResidentReachedCohort,
    selected_required_positions: &[(usize, usize)],
) -> Result<(), FormationError> {
    let mut prior_index = None;
    let mut growth_required = false;
    for (resident_index, required_positions) in selected_required_positions.iter().copied() {
        if prior_index.is_some_and(|prior| prior >= resident_index) {
            return Err(FormationError::NoncanonicalState);
        }
        let mounted_positions = cohort
            .anatomy
            .neuron_anatomies()
            .get(resident_index)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?
            .mathloom_positions();
        growth_required |= required_positions > mounted_positions;
        prior_index = Some(resident_index);
    }
    if !growth_required {
        return Ok(());
    }

    let mut required_positions = cohort
        .anatomy
        .neuron_anatomies()
        .iter()
        .map(NeuronPhysicalAnatomy::mathloom_positions)
        .collect::<Vec<_>>();
    for (resident_index, selected_required) in selected_required_positions.iter().copied() {
        required_positions[resident_index] = required_positions[resident_index]
            .max(selected_required);
    }
    extend_resident_cohort_positional_fabrics(cohort, &required_positions)
}

fn settle_resident_physical_interval(
    cohort: &mut ResidentReachedCohort,
    input: ReachedCohortIntervalInput<'_>,
    gate_work_perturbed_neurons: Vec<bool>,
    receptor_excitation_zeptojoules: Vec<Option<ExactRational>>,
    exogenous_receptor_energy: Option<bool>,
    existing_mosaics: &[RetainedOrganismMosaic],
    max_encoded_bytes: usize,
    source_generation: u64,
) -> Result<ResidentOpticalIntervalOutcome, FormationError> {
    // Rest metabolism (minimal feeding metabolism, authorized 2026-08-05).
    // A genuinely dark interval — the stimulus-boundary law's OWN truth
    // signal, derived from the settled occurrence's exact `2·L·T` transduction
    // integral — is when the body's recovery reactions and its membrane return
    // path run.  Nothing here decides when it is dark, and nothing runs while
    // exogenous energy is still arriving.
    let (metabolic, metabolically_perturbed_neurons) = if exogenous_receptor_energy == Some(false) {
        let pre_metabolic_state = cohort.state.clone();
        let (successor, observation) = settle_reached_cohort_dark_rest(
            &cohort.anatomy,
            &cohort.state,
            input.interval_microseconds(),
        )
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
        cohort.state = successor.into();
        let perturbed = pre_metabolic_state
            .neurons()
            .iter()
            .zip(cohort.state.neurons())
            .map(|(prior, successor)| {
                prior.separated_elementary_charges() != successor.separated_elementary_charges()
            })
            .collect::<Vec<_>>();
        (observation, perturbed)
    } else {
        (
            ReachedCohortMetabolicObservation::default(),
            vec![false; cohort.anatomy.neuron_count()],
        )
    };
    let mut outcome = if cohort.retained_experience.is_some() {
        settle_resident_recurrence_interval(
            cohort,
            input,
            gate_work_perturbed_neurons,
            receptor_excitation_zeptojoules,
            metabolically_perturbed_neurons,
            exogenous_receptor_energy,
            source_generation,
        )
    } else {
        settle_resident_original_interval(
            cohort,
            input,
            gate_work_perturbed_neurons,
            receptor_excitation_zeptojoules,
            metabolically_perturbed_neurons,
            existing_mosaics,
        )
    }?;
    outcome.metabolic = metabolic;
    Ok(outcome)
}

fn settle_resident_original_interval(
    cohort: &mut ResidentReachedCohort,
    input: ReachedCohortIntervalInput<'_>,
    gate_work_perturbed_neurons: Vec<bool>,
    receptor_excitation_zeptojoules: Vec<Option<ExactRational>>,
    metabolically_perturbed_neurons: Vec<bool>,
    existing_mosaics: &[RetainedOrganismMosaic],
) -> Result<ResidentOpticalIntervalOutcome, FormationError> {
    let mut completed_current_fractals: Option<Box<[Option<SparsePhysicalStateDelta>]>> = None;
    // A new exogenous perturbation begins one compact recognition path.  It
    // is deliberately independent of the simultaneously forming original:
    // the same living neurons can recognize an older formation while their
    // current motion is becoming a different experience.
    let (recognition_cue, endogenous_cue) =
        if gate_work_perturbed_neurons.iter().any(|value| *value) {
            (gate_work_perturbed_neurons.as_slice(), false)
        } else {
            (metabolically_perturbed_neurons.as_slice(), true)
        };
    let starts_new_recognition = if endogenous_cue {
        cohort.pending_recurrence.is_none() && recognition_cue.iter().any(|value| *value)
    } else {
        recognition_cue.iter().any(|value| *value)
    };
    if starts_new_recognition {
        cohort.pending_recurrence =
            (!existing_mosaics.is_empty()).then(|| ResidentRecurrenceEvidence {
                carries_physical_change_codec: true,
                gate_work_perturbed_neurons: SparseResidentNeuronMask::from_dense(recognition_cue),
                receptor_excitation_zeptojoules: if endogenous_cue {
                    vec![None; cohort.anatomy.neuron_count()].into_boxed_slice()
                } else {
                    receptor_excitation_zeptojoules.clone().into_boxed_slice()
                },
                physically_changed_neurons: vec![false; cohort.anatomy.neuron_count()]
                    .into_boxed_slice(),
                active_recurrence_contacts: vec![false; cohort.anatomy.contact_count()]
                    .into_boxed_slice(),
                endogenous: endogenous_cue,
            });
    }
    let experience_preceded_interval = cohort.pending_experience.is_some();
    let predecessor_state = cohort.state.clone();
    let settlement = settle_reached_cohort_interval(&cohort.anatomy, &cohort.state, input)
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
    let successor_state = Arc::new(settlement.successor);
    let retained_change_this_interval = predecessor_state
        .neurons()
        .iter()
        .zip(successor_state.neurons())
        .enumerate()
        .map(|(neuron_index, (predecessor, successor))| {
            sparse_retained_physical_state_delta(predecessor, successor)
                .map(|delta| delta.is_some())
                .map_err(|error| {
                    FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                        neuron_index,
                        error,
                    })
                })
        })
        .collect::<Result<Vec<_>, _>>()?;
    // A neuronal fractal exists only after this neuron's retained physical
    // change reaches its own exact quiescent successor. It is not an
    // occurrence-boundary receipt and another living neuron may remain active.
    let mut emitted = Vec::new();
    let active_electrical_contacts = active_contact_bits(&settlement.contact_transitions);
    let mut physically_changed_neurons = predecessor_state
        .neurons()
        .iter()
        .zip(successor_state.neurons())
        .map(|(predecessor, successor)| predecessor != successor)
        .collect::<Vec<_>>();
    or_bits(
        &mut physically_changed_neurons,
        &metabolically_perturbed_neurons,
    )?;
    let mut experience = cohort.pending_experience.take();
    if experience.is_none()
        && retained_change_this_interval
            .iter()
            .any(|changed| *changed)
    {
        experience = Some(ResidentExperienceEvidence {
            codec: ExperienceEvidenceCodec::V7,
            physical: ResidentExperiencePhysicalEvidence::Pending(Box::new([])),
            gate_work_perturbed_neurons: SparseResidentNeuronMask::empty(),
            receptor_excitation_zeptojoules: receptor_excitation_zeptojoules
                .clone()
                .into_boxed_slice(),
            retained_change_neurons: vec![false; cohort.anatomy.neuron_count()]
                .into_boxed_slice(),
            retentively_settled_neurons: vec![false; cohort.anatomy.neuron_count()]
                .into_boxed_slice(),
            active_electrical_contacts: vec![false; cohort.anatomy.contact_count()]
                .into_boxed_slice(),
            local_relaxation_observed: false,
        });
    }
    if let Some(experience) = experience.as_mut() {
        experience.codec = ExperienceEvidenceCodec::V7;
        merge_pending_experience_members(
            experience,
            &predecessor_state,
            &retained_change_this_interval,
        )?;
        experience
            .gate_work_perturbed_neurons
            .union_dense(&gate_work_perturbed_neurons)?;
        or_bits(
            &mut experience.retained_change_neurons,
            &retained_change_this_interval,
        )?;
        or_bits(
            &mut experience.active_electrical_contacts,
            &active_electrical_contacts,
        )?;
    }
    // Collective formation closure remains a separate later retentive-rest
    // law. It determines which cumulative neuron deltas may participate in a
    // retained original; it does not authorize or suppress the local fractal
    // observation above.
    if let Some(mut experience) = experience {
        if experience_preceded_interval {
            emitted.extend(emit_newly_quiescent_neuron_fractals(
                &cohort.anatomy,
                &mut experience,
                &successor_state,
                &retained_change_this_interval,
            )?);
        }
        let experience_complete = experience
            .pending_members()
            .ok_or(FormationError::NoncanonicalState)?
            .iter()
            .all(|member| member.settled);
        if experience_complete {
            let retained_members = retain_sparse_experience_members(&experience, &successor_state)?;
            let member_indices = retained_members
                .iter()
                .map(|member| member.neuron_index)
                .collect::<Vec<_>>();
            // Participation retention (same ratification): the completion is
            // retainable as a recognizable original ONLY if its masks satisfy
            // the admission law's own original-side predicate — at least
            // three changed members connected through the contacts that were
            // physically active during the experience (`connected_members`,
            // reused verbatim from `admit_physical_mosaic`).  A completion
            // failing it does not create a mosaic. Neuronal material remains
            // physical state and the bounded pending occurrence can still
            // acquire later connected participation.
            let mut member_mask = vec![false; cohort.anatomy.neuron_count()];
            for member in &member_indices {
                member_mask[*member] = true;
            }
            let endpoints = cohort.anatomy.contact_endpoints().collect::<Vec<_>>();
            let connected_retention = member_indices.len() >= 3
                && connected_members(
                    cohort.anatomy.neuron_count(),
                    &member_indices,
                    &member_mask,
                    &endpoints,
                    &experience.active_electrical_contacts,
                    &member_indices[..1],
                );
            if connected_retention {
                let mut fractals = vec![None; cohort.anatomy.neuron_count()];
                for member in retained_members.iter() {
                    fractals[member.neuron_index] = Some(member.delta.clone());
                }
                completed_current_fractals = Some(fractals.into_boxed_slice());
                experience.physical =
                    ResidentExperiencePhysicalEvidence::Retained(retained_members);
                cohort.retained_experience = Some(experience);
                cohort.pending_experience = None;
            } else {
                // One or two settled neuronal impressions are real retained
                // physical changes even though they cannot yet admit a
                // mosaic. Keep this one bounded pending occurrence so later
                // causally connected participation can join it. The minimum
                // of three governs mosaic admission, not erasure of neurons.
                cohort.pending_experience = Some(experience);
            }
        } else {
            cohort.pending_experience = Some(experience);
        }
    } else {
        cohort.pending_experience = None;
    }
    cohort.state = successor_state;
    let mut mosaic_resolutions = Vec::new();
    let mut partial_cue_reassembly_count = 0usize;
    let mut recognized_endogenously = false;
    if let Some(mut recurrence) = cohort.pending_recurrence.take() {
        let recurrence_endogenous = recurrence.endogenous;
        recurrence.carries_physical_change_codec = true;
        if !recurrence.endogenous {
            recurrence
                .gate_work_perturbed_neurons
                .union_dense(&gate_work_perturbed_neurons)?;
        }
        or_bits(
            &mut recurrence.physically_changed_neurons,
            &physically_changed_neurons,
        )?;
        or_bits(
            &mut recurrence.active_recurrence_contacts,
            &active_electrical_contacts,
        )?;
        if let Some(current_fractals) = completed_current_fractals.as_deref() {
            let dense_gate_work = recurrence
                .gate_work_perturbed_neurons
                .to_dense(cohort.anatomy.neuron_count())?;
            for (mosaic_index, retained) in existing_mosaics.iter().enumerate() {
                let reassembled = retained
                    .mosaic
                    .reassembled_by_current_flow(
                        &cohort.anatomy,
                        &dense_gate_work,
                        current_fractals,
                        &recurrence.active_recurrence_contacts,
                        recurrence.endogenous,
                    )
                    .map_err(FormationError::PhysicalMosaicUnavailable)?;
                if reassembled {
                    mosaic_resolutions
                        .push(MosaicStructuralResolution::Reinforces { mosaic_index });
                }
            }
        } else {
            cohort.pending_recurrence = Some(recurrence);
        }
        partial_cue_reassembly_count = mosaic_resolutions.len();
        recognized_endogenously = recurrence_endogenous && !mosaic_resolutions.is_empty();
    }
    Ok(ResidentOpticalIntervalOutcome {
        emitted_neuron_fractals: emitted,
        mosaic_formed: None,
        mosaic_resolutions,
        partial_cue_reassembly_count,
        endogenous_partial_cue_reassembly_count: partial_cue_reassembly_count
            * usize::from(recognized_endogenously),
        metabolic: ReachedCohortMetabolicObservation::default(),
    })
}

fn merge_pending_experience_members(
    evidence: &mut ResidentExperienceEvidence,
    predecessor: &ReachedCohortState,
    retained_change_this_interval: &[bool],
) -> Result<(), FormationError> {
    if predecessor.neurons().len() != retained_change_this_interval.len() {
        return Err(FormationError::NoncanonicalState);
    }
    let members = evidence
        .pending_members_mut()
        .ok_or(FormationError::NoncanonicalState)?;
    let mut merged = members.to_vec();
    for (neuron_index, changed) in retained_change_this_interval.iter().copied().enumerate() {
        if !changed {
            continue;
        }
        match merged.binary_search_by_key(&neuron_index, |member| member.neuron_index) {
            Ok(_) => {}
            Err(position) => {
                merged
                    .try_reserve(1)
                    .map_err(|_| FormationError::ArithmeticOverflow)?;
                merged.insert(
                    position,
                    SparsePendingExperienceMember {
                        neuron_index,
                        predecessor: predecessor.neurons()[neuron_index].clone(),
                        settled: false,
                    },
                );
            }
        }
    }
    *members = merged.into_boxed_slice();
    Ok(())
}

fn retain_sparse_experience_members(
    evidence: &ResidentExperienceEvidence,
    successor: &ReachedCohortState,
) -> Result<Box<[SparseRetainedExperienceMember]>, FormationError> {
    let pending = evidence
        .pending_members()
        .ok_or(FormationError::NoncanonicalState)?;
    let mut retained = Vec::new();
    retained
        .try_reserve(pending.len())
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    for member in pending {
        if !member.settled {
            return Err(FormationError::NoncanonicalState);
        }
        let learned = successor
            .neurons()
            .get(member.neuron_index)
            .ok_or(FormationError::NoncanonicalState)?;
        if let Some(delta) =
            sparse_retained_physical_state_delta(&member.predecessor, learned).map_err(|error| {
                FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                    neuron_index: member.neuron_index,
                    error,
                })
            })?
        {
            retained.push(SparseRetainedExperienceMember {
                neuron_index: member.neuron_index,
                predecessor: member.predecessor.clone(),
                learned: learned.clone(),
                delta,
            });
        }
    }
    Ok(retained.into_boxed_slice())
}

fn emit_newly_quiescent_neuron_fractals(
    anatomy: &ReachedCohortAnatomy,
    evidence: &mut ResidentExperienceEvidence,
    successor: &ReachedCohortState,
    retained_change_this_interval: &[bool],
) -> Result<Vec<EmittedNeuronFractal>, FormationError> {
    if evidence.retained_change_neurons.len() != anatomy.neuron_count()
        || evidence.retentively_settled_neurons.len() != anatomy.neuron_count()
        || retained_change_this_interval.len() != anatomy.neuron_count()
        || successor.neurons().len() != anatomy.neuron_count()
    {
        return Err(FormationError::NoncanonicalState);
    }
    let mut emitted = Vec::new();
    let mut newly_settled = Vec::new();
    {
        let members = evidence
            .pending_members_mut()
            .ok_or(FormationError::NoncanonicalState)?;
        for member in members.iter_mut() {
            let neuron_index = member.neuron_index;
            if member.settled || retained_change_this_interval[neuron_index] {
                continue;
            }
            if let Some(delta) = sparse_retained_physical_state_delta(
                &member.predecessor,
                &successor.neurons()[neuron_index],
            )
            .map_err(|error| {
                FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                    neuron_index,
                    error,
                })
            })? {
                emitted.push(EmittedNeuronFractal {
                    neuron_lineage: anatomy.neuron_lineages()[neuron_index],
                    delta,
                });
            }
            member.settled = true;
            newly_settled.push(neuron_index);
        }
    }
    for neuron_index in newly_settled {
        evidence.retentively_settled_neurons[neuron_index] = true;
    }
    Ok(emitted)
}

fn advance_recurrent_neuronal_experience(
    anatomy: &ReachedCohortAnatomy,
    pending: &mut Option<ResidentExperienceEvidence>,
    predecessor: &Arc<ReachedCohortState>,
    successor: &ReachedCohortState,
    retained_change_this_interval: &[bool],
    gate_work_perturbed_neurons: &[bool],
    receptor_excitation_zeptojoules: &[Option<ExactRational>],
    active_electrical_contacts: &[bool],
) -> Result<Vec<EmittedNeuronFractal>, FormationError> {
    let experience_preceded_interval = pending.is_some();
    let mut experience = pending.take();
    if experience.is_none()
        && retained_change_this_interval
            .iter()
            .any(|changed| *changed)
    {
        experience = Some(ResidentExperienceEvidence {
            codec: ExperienceEvidenceCodec::V7,
            physical: ResidentExperiencePhysicalEvidence::Pending(Box::new([])),
            gate_work_perturbed_neurons: SparseResidentNeuronMask::empty(),
            receptor_excitation_zeptojoules: receptor_excitation_zeptojoules
                .to_vec()
                .into_boxed_slice(),
            retained_change_neurons: vec![false; anatomy.neuron_count()].into_boxed_slice(),
            retentively_settled_neurons: vec![false; anatomy.neuron_count()].into_boxed_slice(),
            active_electrical_contacts: vec![false; anatomy.contact_count()].into_boxed_slice(),
            local_relaxation_observed: false,
        });
    }
    let Some(mut experience) = experience.take() else {
        return Ok(Vec::new());
    };
    experience.codec = ExperienceEvidenceCodec::V7;
    merge_pending_experience_members(
        &mut experience,
        predecessor,
        retained_change_this_interval,
    )?;
    experience
        .gate_work_perturbed_neurons
        .union_dense(gate_work_perturbed_neurons)?;
    or_bits(
        &mut experience.retained_change_neurons,
        retained_change_this_interval,
    )?;
    or_bits(
        &mut experience.active_electrical_contacts,
        active_electrical_contacts,
    )?;
    let emitted = if experience_preceded_interval {
        emit_newly_quiescent_neuron_fractals(
            anatomy,
            &mut experience,
            successor,
            retained_change_this_interval,
        )?
    } else {
        Vec::new()
    };
    let complete = experience
        .pending_members()
        .ok_or(FormationError::NoncanonicalState)?
        .iter()
        .all(|member| member.settled);
    *pending = (!complete).then_some(experience);
    Ok(emitted)
}

fn settle_resident_recurrence_interval(
    cohort: &mut ResidentReachedCohort,
    input: ReachedCohortIntervalInput<'_>,
    gate_work_perturbed_neurons: Vec<bool>,
    receptor_excitation_zeptojoules: Vec<Option<ExactRational>>,
    metabolically_perturbed_neurons: Vec<bool>,
    exogenous_receptor_energy: Option<bool>,
    source_generation: u64,
) -> Result<ResidentOpticalIntervalOutcome, FormationError> {
    let local_relaxation_observed = cohort
        .retained_experience
        .as_ref()
        .ok_or(FormationError::NoncanonicalState)?
        .local_relaxation_observed;
    if exogenous_receptor_energy != Some(false)
        && gate_work_perturbed_neurons
            .iter()
            .any(|perturbed| *perturbed)
    {
        // A new physical perturbation ends any older unfinished cue.  It is
        // a new occurrence, not another interval of the old one.  This also
        // prevents a pre-upgrade transient from blocking the living
        // formation forever.
        cohort.pending_recurrence = None;
        let retained = cohort
            .retained_experience
            .as_ref()
            .ok_or(FormationError::NoncanonicalState)?;
        if is_formation_local_proper_partial_cue(retained, &gate_work_perturbed_neurons)? {
            cohort.pending_recurrence = Some(ResidentRecurrenceEvidence {
                carries_physical_change_codec: true,
                gate_work_perturbed_neurons: SparseResidentNeuronMask::empty(),
                receptor_excitation_zeptojoules: receptor_excitation_zeptojoules
                    .clone()
                    .into_boxed_slice(),
                physically_changed_neurons: vec![false; cohort.anatomy.neuron_count()]
                    .into_boxed_slice(),
                active_recurrence_contacts: vec![false; cohort.anatomy.contact_count()]
                    .into_boxed_slice(),
                endogenous: false,
            });
        }
    }

    #[cfg(test)]
    RESIDENT_ACTUAL_RECURRENCE_SETTLEMENTS.with(|count| count.set(count.get() + 1));
    let recurrence_predecessor = cohort.state.clone();
    let actual = settle_reached_cohort_interval(&cohort.anatomy, &cohort.state, input)
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
    let successor_state = Arc::new(actual.successor);
    let partial_cue_reassembly_count = 0;
    let retained_change_this_interval = recurrence_predecessor
        .neurons()
        .iter()
        .zip(successor_state.neurons())
        .enumerate()
        .map(|(neuron_index, (predecessor, successor))| {
            sparse_retained_physical_state_delta(predecessor, successor)
                .map(|delta| delta.is_some())
                .map_err(|error| {
                    FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                        neuron_index,
                        error,
                    })
                })
        })
        .collect::<Result<Vec<_>, _>>()?;
    let active_contacts = active_contact_bits(&actual.contact_transitions);
    let physically_changed_neurons = recurrence_predecessor
        .neurons()
        .iter()
        .zip(successor_state.neurons())
        .map(|(predecessor, successor)| predecessor != successor)
        .collect::<Vec<_>>();
    let emitted_neuron_fractals = advance_recurrent_neuronal_experience(
        &cohort.anatomy,
        &mut cohort.pending_experience,
        &recurrence_predecessor,
        &successor_state,
        &retained_change_this_interval,
        &gate_work_perturbed_neurons,
        &receptor_excitation_zeptojoules,
        &active_contacts,
    )?;
    cohort.state = successor_state;
    let formation_locally_settled = {
        let retained = cohort
            .retained_experience
            .as_ref()
            .ok_or(FormationError::NoncanonicalState)?;
        retained
            .retained_members()
            .ok_or(FormationError::NoncanonicalState)?
            .iter()
            .all(|member| !physically_changed_neurons[member.neuron_index])
            && !retained_contact_set_flowing(retained, &active_contacts)?
    };

    // A retained formation relaxes through one later settlement with no
    // exogenous gate work.  Internal current may continue: requiring every
    // retained contact to stop would require a living formation to become
    // electrically dead.  Recording happens after the interval, so that
    // exact interval cannot authorize itself as a cue.
    if !local_relaxation_observed
        && gate_work_perturbed_neurons
            .iter()
            .all(|perturbed| !perturbed)
        && formation_locally_settled
    {
        cohort
            .retained_experience
            .as_mut()
            .ok_or(FormationError::NoncanonicalState)?
            .codec = ExperienceEvidenceCodec::V7;
        cohort
            .retained_experience
            .as_mut()
            .ok_or(FormationError::NoncanonicalState)?
            .local_relaxation_observed = true;
    }

    // After formation-local relaxation, a later dark interval may carry a
    // genuinely internal perturbation.  Only membrane movement caused by the
    // organism's own metabolic return may BEGIN that cue. Continuing contact
    // current from the original occurrence may propagate a cue once present,
    // but it cannot re-label its own settling tail as spontaneous recall. No
    // scheduler, timer, semantic label, or scalar selection participates.
    if cohort.pending_recurrence.is_none()
        && local_relaxation_observed
        && gate_work_perturbed_neurons
            .iter()
            .all(|perturbed| !perturbed)
        && !retained_contact_set_flowing(
            cohort
                .retained_experience
                .as_ref()
                .ok_or(FormationError::NoncanonicalState)?,
            &active_contacts,
        )?
    {
        let retained = cohort
            .retained_experience
            .as_ref()
            .ok_or(FormationError::NoncanonicalState)?;
        if is_formation_local_proper_partial_cue(retained, &metabolically_perturbed_neurons)? {
            cohort.pending_recurrence = Some(ResidentRecurrenceEvidence {
                carries_physical_change_codec: true,
                gate_work_perturbed_neurons: SparseResidentNeuronMask::from_dense(
                    &metabolically_perturbed_neurons,
                ),
                receptor_excitation_zeptojoules: vec![None; cohort.anatomy.neuron_count()]
                    .into_boxed_slice(),
                physically_changed_neurons: vec![false; cohort.anatomy.neuron_count()]
                    .into_boxed_slice(),
                active_recurrence_contacts: vec![false; cohort.anatomy.contact_count()]
                    .into_boxed_slice(),
                endogenous: true,
            });
        }
    }
    let Some(mut recurrence) = cohort.pending_recurrence.take() else {
        return Ok(ResidentOpticalIntervalOutcome {
            emitted_neuron_fractals,
            mosaic_formed: None,
            mosaic_resolutions: Vec::new(),
            partial_cue_reassembly_count,
            endogenous_partial_cue_reassembly_count: 0,
            metabolic: ReachedCohortMetabolicObservation::default(),
        });
    };
    recurrence.carries_physical_change_codec = true;
    recurrence
        .gate_work_perturbed_neurons
        .union_dense(&gate_work_perturbed_neurons)?;
    or_bits(
        &mut recurrence.physically_changed_neurons,
        &physically_changed_neurons,
    )?;
    or_bits(&mut recurrence.active_recurrence_contacts, &active_contacts)?;
    if exogenous_receptor_energy != Some(false) {
        cohort.pending_recurrence = Some(recurrence);
        return Ok(ResidentOpticalIntervalOutcome {
            emitted_neuron_fractals,
            mosaic_formed: None,
            mosaic_resolutions: Vec::new(),
            partial_cue_reassembly_count: 0,
            endogenous_partial_cue_reassembly_count: 0,
            metabolic: ReachedCohortMetabolicObservation::default(),
        });
    }
    let retained = cohort
        .retained_experience
        .as_ref()
        .ok_or(FormationError::NoncanonicalState)?;
    let original = original_settlement(&cohort.anatomy, retained)?;
    let actual_recurrence = recurrence_settlement(
        &cohort.anatomy,
        retained,
        cohort.state.as_ref().clone(),
        recurrence.receptor_excitation_zeptojoules.clone(),
        recurrence
            .gate_work_perturbed_neurons
            .to_dense(cohort.anatomy.neuron_count())?,
        recurrence.active_recurrence_contacts.clone(),
    )?;
    let mosaic = match admit_physical_mosaic(&cohort.anatomy, &original, &actual_recurrence) {
        Ok(mosaic) => mosaic,
        Err(error) if physical_mosaic_non_admission(error) => {
            // A recurrence inherited before the formation's first later
            // no-exogenous settlement is transient tail state, not learned
            // authority.  If it cannot assemble on that boundary, drop it;
            // otherwise an old unfinished cue can block every later internal
            // perturbation forever.  Recurrences begun after relaxation still
            // remain while their own formation contacts are moving.
            if local_relaxation_observed {
                cohort.pending_recurrence = Some(recurrence);
            }
            return Ok(ResidentOpticalIntervalOutcome {
                emitted_neuron_fractals,
                mosaic_formed: None,
                mosaic_resolutions: Vec::new(),
                partial_cue_reassembly_count,
                endogenous_partial_cue_reassembly_count: 0,
                metabolic: ReachedCohortMetabolicObservation::default(),
            });
        }
        Err(error) => return Err(FormationError::PhysicalMosaicUnavailable(error)),
    };
    verify_mosaic_members_physically_moved(
        &cohort.anatomy,
        &mosaic,
        &actual_recurrence,
        source_generation,
    )?;
    // This proves a genuine sensory-local recurrence, but one cohort cannot
    // author an organism mosaic. Release its bounded completed evidence so
    // the same living neurons may retain another occurrence; organism-level
    // admission happens only at `settle_organism_mosaic_boundary`, where
    // post-quiescence deltas from distinct cohorts must be joined by physical
    // cross-cohort bonds. Nothing is added to the organism mosaic collection.
    cohort.retained_experience = None;
    cohort.pending_recurrence = None;
    Ok(ResidentOpticalIntervalOutcome {
        emitted_neuron_fractals,
        mosaic_formed: None,
        mosaic_resolutions: Vec::new(),
        partial_cue_reassembly_count: 0,
        endogenous_partial_cue_reassembly_count: 0,
        metabolic: ReachedCohortMetabolicObservation::default(),
    })
}

fn original_settlement(
    anatomy: &ReachedCohortAnatomy,
    retained: &ResidentExperienceEvidence,
) -> Result<ReachedCohortPostExperienceSettlement, FormationError> {
    let mut neuron_fractals = vec![None; anatomy.neuron_count()];
    for member in retained
        .retained_members()
        .ok_or(FormationError::NoncanonicalState)?
    {
        neuron_fractals[member.neuron_index] = Some(member.delta.clone());
    }
    Ok(ReachedCohortPostExperienceSettlement {
        rest: None,
        neuron_fractals: neuron_fractals.into_boxed_slice(),
        receptor_excitation_zeptojoules: retained.receptor_excitation_zeptojoules.clone(),
        electrical_contact_was_active: retained
            .active_electrical_contacts
            .iter()
            .any(|active| *active),
        gate_work_perturbed_neurons: retained
            .gate_work_perturbed_neurons
            .to_dense(anatomy.neuron_count())?,
        active_electrical_contacts: retained.active_electrical_contacts.clone(),
    })
}

fn recurrence_settlement(
    anatomy: &ReachedCohortAnatomy,
    retained: &ResidentExperienceEvidence,
    successor: ReachedCohortState,
    receptor_excitation_zeptojoules: Box<[Option<ExactRational>]>,
    gate_work_perturbed_neurons: Box<[bool]>,
    active_electrical_contacts: Box<[bool]>,
) -> Result<ReachedCohortRecurrenceSettlement, FormationError> {
    let mut neuron_physical_deltas = vec![None; anatomy.neuron_count()];
    for member in retained
        .retained_members()
        .ok_or(FormationError::NoncanonicalState)?
    {
        neuron_physical_deltas[member.neuron_index] = sparse_physical_state_delta(
            &member.learned,
            &successor.neurons()[member.neuron_index],
        )
        .map_err(|error| {
            FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                neuron_index: member.neuron_index,
                error,
            })
        })?;
    }
    Ok(ReachedCohortRecurrenceSettlement {
        neuron_physical_deltas: neuron_physical_deltas.into_boxed_slice(),
        successor,
        receptor_excitation_zeptojoules,
        gate_work_perturbed_neurons,
        active_electrical_contacts,
    })
}

/// The one BODY invariant the retired episode builder used to enforce.
///
/// Everything else `build_typed_hippocampal_episode` checked was a round-trip
/// of the archive record's OWN encoding — it re-encoded the retained
/// experience evidence, the recurrence evidence and two cohort states, then
/// decoded them back and compared.  Those checks validated the record, not
/// Guala, and they left with it.  THIS check is about her: every member of an
/// admitted mosaic must have actually moved in the recurrence that admitted
/// it, and its lineage must be one this cohort's anatomy authored.  It is kept
/// verbatim, at the same point in the transition, with the same two error
/// values, so a body that used to be refused here is still refused here.
fn verify_mosaic_members_physically_moved(
    anatomy: &ReachedCohortAnatomy,
    mosaic: &AdmittedPhysicalMosaic,
    actual_recurrence: &ReachedCohortRecurrenceSettlement,
    source_generation: u64,
) -> Result<(), FormationError> {
    if source_generation == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    for lineage in mosaic.member_lineages() {
        let member_index = anatomy
            .neuron_lineages()
            .iter()
            .position(|candidate| candidate == lineage)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        if actual_recurrence.neuron_physical_deltas[member_index].is_none() {
            return Err(FormationError::NoncanonicalState);
        }
    }
    Ok(())
}

fn is_formation_local_proper_partial_cue(
    retained: &ResidentExperienceEvidence,
    perturbed: &[bool],
) -> Result<bool, FormationError> {
    let members = retained
        .retained_members()
        .ok_or(FormationError::NoncanonicalState)?;
    if members
        .last()
        .is_some_and(|member| member.neuron_index >= perturbed.len())
    {
        return Err(FormationError::NoncanonicalState);
    }
    let member_count = members.len();
    let mut cue_count = 0usize;
    for member in members {
        cue_count = cue_count
            .checked_add(usize::from(perturbed[member.neuron_index]))
            .ok_or(FormationError::ArithmeticOverflow)?;
    }
    Ok(cue_count > 0 && cue_count < member_count)
}

fn retained_contact_set_flowing(
    retained: &ResidentExperienceEvidence,
    active_contacts: &[bool],
) -> Result<bool, FormationError> {
    if retained.active_electrical_contacts.len() != active_contacts.len() {
        return Err(FormationError::NoncanonicalState);
    }
    Ok(retained
        .active_electrical_contacts
        .iter()
        .zip(active_contacts)
        .any(|(carried_experience, flowing_now)| *carried_experience && *flowing_now))
}

fn active_contact_bits(
    transitions: &[crate::sparse_electrical_contact::ElectricalContactTransition],
) -> Vec<bool> {
    transitions
        .iter()
        .map(|transition| {
            transition.outward_current_from_left_picoamperes.parts().0 != 0
                || transition.outward_elementary_charges_from_left != 0
                || transition.conductance_changed
        })
        .collect()
}

fn or_bits(target: &mut [bool], values: &[bool]) -> Result<(), FormationError> {
    if target.len() != values.len() {
        return Err(FormationError::NoncanonicalState);
    }
    for (target, value) in target.iter_mut().zip(values) {
        *target |= *value;
    }
    Ok(())
}

fn physical_mosaic_non_admission(error: PhysicalMosaicError) -> bool {
    matches!(
        error,
        PhysicalMosaicError::FewerThanThreeRetainedFractals
            | PhysicalMosaicError::OriginalRelationNotConnected
            | PhysicalMosaicError::CueIsEmpty
            | PhysicalMosaicError::CueIsNotPartial
            | PhysicalMosaicError::CueOutsideFormation
            | PhysicalMosaicError::RecurrenceDidNotReachFormation
            | PhysicalMosaicError::RecurrenceDidNotChangeEveryMember
            | PhysicalMosaicError::RecurrenceDidNotAlterFormation
    )
}

/// Encode one experience evidence record in the `GLEXP02` layout. With a
/// resident base state (the cohort's current state retained beside the
/// evidence) the PRE snapshot is carried as per-neuron sparse deltas against
/// that base and the POST snapshot collapses to a 32-byte content digest when
/// its canonical encoding is byte-identical to the base's; the byte comparison
/// happens here, at encode. Without a base (hippocampal episode bodies) both
/// snapshots are carried as complete content-addressed cohort states. Every
/// settled value is preserved exactly in all forms.
fn encode_sparse_experience_evidence(
    anatomy: &ReachedCohortAnatomy,
    evidence: &ResidentExperienceEvidence,
) -> Result<Vec<u8>, FormationError> {
    if evidence.codec != ExperienceEvidenceCodec::V7
        || !evidence
            .gate_work_perturbed_neurons
            .validates_width(anatomy.neuron_count())
        || evidence.receptor_excitation_zeptojoules.len() != anatomy.neuron_count()
        || evidence.active_electrical_contacts.len() != anatomy.contact_count()
    {
        return Err(FormationError::NoncanonicalState);
    }
    let mut expected_changed = vec![false; anatomy.neuron_count()];
    let mut expected_settled = vec![false; anatomy.neuron_count()];
    let (mode, member_count) = match &evidence.physical {
        ResidentExperiencePhysicalEvidence::Pending(members) => {
            if evidence.local_relaxation_observed
                || members.windows(2).any(|pair| pair[0].neuron_index >= pair[1].neuron_index)
            {
                return Err(FormationError::NoncanonicalState);
            }
            for member in members.iter() {
                if member.neuron_index >= anatomy.neuron_count() {
                    return Err(FormationError::NoncanonicalState);
                }
                expected_changed[member.neuron_index] = true;
                expected_settled[member.neuron_index] = member.settled;
            }
            (0u8, members.len())
        }
        ResidentExperiencePhysicalEvidence::Retained(members) => {
            if members.is_empty()
                || members.windows(2).any(|pair| pair[0].neuron_index >= pair[1].neuron_index)
            {
                return Err(FormationError::NoncanonicalState);
            }
            for member in members.iter() {
                if member.neuron_index >= anatomy.neuron_count()
                    || sparse_retained_physical_state_delta(
                        &member.predecessor,
                        &member.learned,
                    )
                    .map_err(|error| {
                        FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                            neuron_index: member.neuron_index,
                            error,
                        })
                    })?
                    .as_ref()
                        != Some(&member.delta)
                {
                    return Err(FormationError::NoncanonicalState);
                }
                expected_changed[member.neuron_index] = true;
                expected_settled[member.neuron_index] = true;
            }
            (1u8, members.len())
        }
        ResidentExperiencePhysicalEvidence::Legacy { .. } => {
            return Err(FormationError::NoncanonicalState)
        }
    };
    if evidence.retained_change_neurons.as_ref() != expected_changed.as_slice()
        || evidence.retentively_settled_neurons.as_ref() != expected_settled.as_slice()
    {
        return Err(FormationError::NoncanonicalState);
    }

    let mut encoded = Vec::new();
    encoded.extend_from_slice(EXPERIENCE_V7_MAGIC);
    encoded.push(mode);
    encoded.push(u8::from(evidence.local_relaxation_observed));
    push_length(&mut encoded, member_count)?;
    match &evidence.physical {
        ResidentExperiencePhysicalEvidence::Pending(members) => {
            for member in members.iter() {
                push_length(&mut encoded, member.neuron_index)?;
                encoded.push(u8::from(member.settled));
                let state = encode_neuron_physical_state(
                    &anatomy.neuron_anatomies()[member.neuron_index],
                    &member.predecessor,
                )
                .map_err(|_| FormationError::NoncanonicalState)?;
                push_length(&mut encoded, state.len())?;
                encoded.extend_from_slice(&state);
            }
        }
        ResidentExperiencePhysicalEvidence::Retained(members) => {
            for member in members.iter() {
                push_length(&mut encoded, member.neuron_index)?;
                for state in [&member.predecessor, &member.learned] {
                    let state = encode_neuron_physical_state(
                        &anatomy.neuron_anatomies()[member.neuron_index],
                        state,
                    )
                    .map_err(|_| FormationError::NoncanonicalState)?;
                    push_length(&mut encoded, state.len())?;
                    encoded.extend_from_slice(&state);
                }
                let delta = encode_sparse_physical_state_delta(&member.delta)
                    .map_err(|_| FormationError::NoncanonicalState)?;
                push_length(&mut encoded, delta.len())?;
                encoded.extend_from_slice(&delta);
            }
        }
        ResidentExperiencePhysicalEvidence::Legacy { .. } => unreachable!(),
    }
    evidence
        .gate_work_perturbed_neurons
        .encode_sparse(&mut encoded, anatomy.neuron_count())?;
    encode_optional_exact_slice(&mut encoded, &evidence.receptor_excitation_zeptojoules)?;
    encode_bool_slice(&mut encoded, &evidence.active_electrical_contacts)?;
    Ok(encoded)
}

fn decode_sparse_experience_evidence(
    encoded: &[u8],
    anatomy: &ReachedCohortAnatomy,
) -> Result<ResidentExperienceEvidence, FormationError> {
    if encoded.get(..EXPERIENCE_V7_MAGIC.len()) != Some(EXPERIENCE_V7_MAGIC) {
        return Err(FormationError::NoncanonicalState);
    }
    let mut cursor = EXPERIENCE_V7_MAGIC.len();
    let mode = *encoded
        .get(cursor)
        .ok_or(FormationError::NoncanonicalState)?;
    cursor += 1;
    let local_relaxation_observed = match encoded.get(cursor) {
        Some(0) => false,
        Some(1) => true,
        _ => return Err(FormationError::NoncanonicalState),
    };
    cursor += 1;
    let member_count = read_length(encoded, &mut cursor)?;
    if member_count > anatomy.neuron_count() || (mode == 1 && member_count == 0) {
        return Err(FormationError::NoncanonicalState);
    }
    let mut pending = Vec::new();
    let mut retained = Vec::new();
    pending
        .try_reserve_exact(member_count)
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    retained
        .try_reserve_exact(member_count)
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    let take_body = |cursor: &mut usize| -> Result<&[u8], FormationError> {
        let length = read_length(encoded, cursor)?;
        let end = cursor
            .checked_add(length)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let body = encoded
            .get(*cursor..end)
            .ok_or(FormationError::NoncanonicalState)?;
        *cursor = end;
        Ok(body)
    };
    let mut prior_index = None;
    for _ in 0..member_count {
        let neuron_index = read_length(encoded, &mut cursor)?;
        if neuron_index >= anatomy.neuron_count()
            || prior_index.is_some_and(|prior| prior >= neuron_index)
        {
            return Err(FormationError::NoncanonicalState);
        }
        prior_index = Some(neuron_index);
        let neuron_anatomy = &anatomy.neuron_anatomies()[neuron_index];
        match mode {
            0 => {
                let settled = match encoded.get(cursor) {
                    Some(0) => false,
                    Some(1) => true,
                    _ => return Err(FormationError::NoncanonicalState),
                };
                cursor += 1;
                let predecessor = decode_neuron_physical_state(
                    neuron_anatomy,
                    take_body(&mut cursor)?,
                )
                .map_err(|_| FormationError::NoncanonicalState)?;
                pending.push(SparsePendingExperienceMember {
                    neuron_index,
                    predecessor,
                    settled,
                });
            }
            1 => {
                let predecessor = decode_neuron_physical_state(
                    neuron_anatomy,
                    take_body(&mut cursor)?,
                )
                .map_err(|_| FormationError::NoncanonicalState)?;
                let learned = decode_neuron_physical_state(
                    neuron_anatomy,
                    take_body(&mut cursor)?,
                )
                .map_err(|_| FormationError::NoncanonicalState)?;
                let delta = decode_sparse_physical_state_delta(take_body(&mut cursor)?)
                    .map_err(|_| FormationError::NoncanonicalState)?;
                if sparse_retained_physical_state_delta(&predecessor, &learned)
                    .map_err(|error| {
                        FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                            neuron_index,
                            error,
                        })
                    })?
                    .as_ref()
                    != Some(&delta)
                {
                    return Err(FormationError::NoncanonicalState);
                }
                retained.push(SparseRetainedExperienceMember {
                    neuron_index,
                    predecessor,
                    learned,
                    delta,
                });
            }
            _ => return Err(FormationError::NoncanonicalState),
        }
    }
    if mode == 0 && local_relaxation_observed {
        return Err(FormationError::NoncanonicalState);
    }
    let gate_work_perturbed_neurons = SparseResidentNeuronMask::decode_sparse(
        encoded,
        &mut cursor,
        anatomy.neuron_count(),
    )?;
    let receptor_excitation_zeptojoules =
        decode_optional_exact_slice(encoded, &mut cursor, anatomy.neuron_count())?;
    let active_electrical_contacts =
        decode_bool_slice(encoded, &mut cursor, anatomy.contact_count())?;
    if cursor != encoded.len() {
        return Err(FormationError::NoncanonicalState);
    }
    let physical = if mode == 0 {
        ResidentExperiencePhysicalEvidence::Pending(pending.into_boxed_slice())
    } else {
        ResidentExperiencePhysicalEvidence::Retained(retained.into_boxed_slice())
    };
    let mut retained_change_neurons = vec![false; anatomy.neuron_count()];
    let mut retentively_settled_neurons = vec![false; anatomy.neuron_count()];
    match &physical {
        ResidentExperiencePhysicalEvidence::Pending(members) => {
            for member in members.iter() {
                retained_change_neurons[member.neuron_index] = true;
                retentively_settled_neurons[member.neuron_index] = member.settled;
            }
        }
        ResidentExperiencePhysicalEvidence::Retained(members) => {
            for member in members.iter() {
                retained_change_neurons[member.neuron_index] = true;
                retentively_settled_neurons[member.neuron_index] = true;
            }
        }
        ResidentExperiencePhysicalEvidence::Legacy { .. } => unreachable!(),
    }
    Ok(ResidentExperienceEvidence {
        codec: ExperienceEvidenceCodec::V7,
        physical,
        gate_work_perturbed_neurons,
        receptor_excitation_zeptojoules,
        retained_change_neurons: retained_change_neurons.into_boxed_slice(),
        retentively_settled_neurons: retentively_settled_neurons.into_boxed_slice(),
        active_electrical_contacts,
        local_relaxation_observed,
    })
}

fn encode_experience_evidence_v2(
    anatomy: &ReachedCohortAnatomy,
    base: Option<&ReachedCohortState>,
    evidence: &ResidentExperienceEvidence,
    carries_contact_plasticity: bool,
) -> Result<Vec<u8>, FormationError> {
    if evidence.codec == ExperienceEvidenceCodec::V7 {
        return encode_sparse_experience_evidence(anatomy, evidence);
    }
    let (pre_experience_rest, post_experience_rest) = evidence
        .legacy_states()
        .ok_or(FormationError::NoncanonicalState)?;
    if !evidence
        .gate_work_perturbed_neurons
        .validates_width(anatomy.neuron_count())
        || evidence.receptor_excitation_zeptojoules.len() != anatomy.neuron_count()
        || evidence.retained_change_neurons.len() != anatomy.neuron_count()
        || evidence.retentively_settled_neurons.len() != anatomy.neuron_count()
        || evidence.active_electrical_contacts.len() != anatomy.contact_count()
        || evidence
            .retentively_settled_neurons
            .iter()
            .zip(evidence.retained_change_neurons.iter())
            .any(|(settled, changed)| *settled && !*changed)
    {
        return Err(FormationError::NoncanonicalState);
    }
    if evidence.codec == ExperienceEvidenceCodec::V1 {
        return encode_experience_evidence(anatomy, evidence);
    }
    if (evidence.codec == ExperienceEvidenceCodec::V2 && evidence.local_relaxation_observed)
        || (evidence.codec == ExperienceEvidenceCodec::V3 && !evidence.local_relaxation_observed)
    {
        return Err(FormationError::NoncanonicalState);
    }
    let selective_layout = matches!(
        evidence.codec,
        ExperienceEvidenceCodec::V4
            | ExperienceEvidenceCodec::V5
            | ExperienceEvidenceCodec::V6
    );
    let excitation_layout = matches!(
        evidence.codec,
        ExperienceEvidenceCodec::V5 | ExperienceEvidenceCodec::V6
    );
    let carries_contact_channels = evidence.codec == ExperienceEvidenceCodec::V6;
    let mut encoded = Vec::new();
    encoded.extend_from_slice(match evidence.codec {
        ExperienceEvidenceCodec::V1 => unreachable!(),
        ExperienceEvidenceCodec::V2 => EXPERIENCE_V2_MAGIC,
        ExperienceEvidenceCodec::V3 => EXPERIENCE_V3_MAGIC,
        ExperienceEvidenceCodec::V4 => EXPERIENCE_V4_MAGIC,
        ExperienceEvidenceCodec::V5 => EXPERIENCE_V5_MAGIC,
        ExperienceEvidenceCodec::V6 => EXPERIENCE_V6_MAGIC,
        ExperienceEvidenceCodec::V7 => unreachable!(),
    });
    if selective_layout {
        encoded.push(u8::from(evidence.local_relaxation_observed));
    }
    match base {
        Some(base) => {
            let body = if carries_contact_channels {
                encode_reached_cohort_state_delta(anatomy, base, pre_experience_rest)
            } else if carries_contact_plasticity {
                encode_reached_cohort_state_delta_v2(
                    anatomy,
                    base,
                    pre_experience_rest,
                )
            } else {
                encode_reached_cohort_state_delta_v1(anatomy, base, pre_experience_rest)
            }
            .map_err(|_| FormationError::NoncanonicalState)?;
            encoded.push(1);
            push_length(&mut encoded, body.len())?;
            encoded.extend_from_slice(&body);
        }
        None => {
            let body = if carries_contact_channels {
                encode_reached_cohort_state_v6(anatomy, pre_experience_rest)
            } else if carries_contact_plasticity {
                encode_reached_cohort_state_v5(anatomy, pre_experience_rest)
            } else {
                encode_reached_cohort_state_v4(anatomy, pre_experience_rest)
            }
            .map_err(|_| FormationError::NoncanonicalState)?;
            encoded.push(0);
            push_length(&mut encoded, body.len())?;
            encoded.extend_from_slice(&body);
        }
    }
    match post_experience_rest {
        None => encoded.push(0),
        Some(post) => {
            let state_body = |state: &ReachedCohortState| {
                if carries_contact_channels {
                    encode_reached_cohort_state_v6(anatomy, state)
                } else if carries_contact_plasticity {
                    encode_reached_cohort_state_v5(anatomy, state)
                } else {
                    encode_reached_cohort_state_v4(anatomy, state)
                }
            };
            let post_body = state_body(post).map_err(|_| FormationError::NoncanonicalState)?;
            let base_body = base
                .map(state_body)
                .transpose()
                .map_err(|_| FormationError::NoncanonicalState)?;
            match base_body {
                Some(base_body) if base_body == post_body => {
                    encoded.push(2);
                    encoded.extend_from_slice(&sha256(&post_body));
                }
                _ => {
                    encoded.push(1);
                    push_length(&mut encoded, post_body.len())?;
                    encoded.extend_from_slice(&post_body);
                }
            }
        }
    }
    evidence
        .gate_work_perturbed_neurons
        .encode_dense(&mut encoded, anatomy.neuron_count())?;
    if excitation_layout {
        encode_optional_exact_slice(&mut encoded, &evidence.receptor_excitation_zeptojoules)?;
    }
    if selective_layout {
        push_length(&mut encoded, evidence.retained_change_neurons.len())?;
        encoded.extend(
            evidence
                .retained_change_neurons
                .iter()
                .map(|value| u8::from(*value)),
        );
        push_length(&mut encoded, evidence.retentively_settled_neurons.len())?;
        encoded.extend(
            evidence
                .retentively_settled_neurons
                .iter()
                .map(|value| u8::from(*value)),
        );
    }
    push_length(&mut encoded, evidence.active_electrical_contacts.len())?;
    encoded.extend(
        evidence
            .active_electrical_contacts
            .iter()
            .map(|value| u8::from(*value)),
    );
    Ok(encoded)
}

fn decode_experience_evidence_v2(
    encoded: &[u8],
    anatomy: &ReachedCohortAnatomy,
    base: Option<&ReachedCohortState>,
) -> Result<ResidentExperienceEvidence, FormationError> {
    let (codec, local_relaxation_observed, selective_layout, excitation_layout, mut cursor) =
        if encoded.get(..EXPERIENCE_V2_MAGIC.len()) == Some(EXPERIENCE_V2_MAGIC) {
            (
                ExperienceEvidenceCodec::V2,
                false,
                false,
                false,
                EXPERIENCE_V2_MAGIC.len(),
            )
        } else if encoded.get(..EXPERIENCE_V3_MAGIC.len()) == Some(EXPERIENCE_V3_MAGIC) {
            (
                ExperienceEvidenceCodec::V3,
                true,
                false,
                false,
                EXPERIENCE_V3_MAGIC.len(),
            )
        } else if encoded.get(..EXPERIENCE_V4_MAGIC.len()) == Some(EXPERIENCE_V4_MAGIC) {
            let flag = *encoded
                .get(EXPERIENCE_V4_MAGIC.len())
                .ok_or(FormationError::NoncanonicalState)?;
            if flag > 1 {
                return Err(FormationError::NoncanonicalState);
            }
            (
                ExperienceEvidenceCodec::V4,
                flag == 1,
                true,
                false,
                EXPERIENCE_V4_MAGIC
                    .len()
                    .checked_add(1)
                    .ok_or(FormationError::ArithmeticOverflow)?,
            )
        } else if encoded.get(..EXPERIENCE_V5_MAGIC.len()) == Some(EXPERIENCE_V5_MAGIC) {
            let flag = *encoded
                .get(EXPERIENCE_V5_MAGIC.len())
                .ok_or(FormationError::NoncanonicalState)?;
            if flag > 1 {
                return Err(FormationError::NoncanonicalState);
            }
            (
                ExperienceEvidenceCodec::V5,
                flag == 1,
                true,
                true,
                EXPERIENCE_V5_MAGIC
                    .len()
                    .checked_add(1)
                    .ok_or(FormationError::ArithmeticOverflow)?,
            )
        } else if encoded.get(..EXPERIENCE_V6_MAGIC.len()) == Some(EXPERIENCE_V6_MAGIC) {
            let flag = *encoded
                .get(EXPERIENCE_V6_MAGIC.len())
                .ok_or(FormationError::NoncanonicalState)?;
            if flag > 1 {
                return Err(FormationError::NoncanonicalState);
            }
            (
                ExperienceEvidenceCodec::V6,
                flag == 1,
                true,
                true,
                EXPERIENCE_V6_MAGIC
                    .len()
                    .checked_add(1)
                    .ok_or(FormationError::ArithmeticOverflow)?,
            )
        } else {
            return Err(FormationError::NoncanonicalState);
        };
    let pre_mode = *encoded
        .get(cursor)
        .ok_or(FormationError::NoncanonicalState)?;
    cursor = cursor
        .checked_add(1)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let pre_length = read_length(encoded, &mut cursor)?;
    let pre_end = cursor
        .checked_add(pre_length)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let pre_body = encoded
        .get(cursor..pre_end)
        .ok_or(FormationError::NoncanonicalState)?;
    let pre_experience_rest = match (pre_mode, base) {
        (0, _) => decode_reached_cohort_state(anatomy, pre_body)
            .map_err(|_| FormationError::NoncanonicalState)?,
        (1, Some(base)) => {
            decode_reached_cohort_state_delta(anatomy, base, pre_body).map_err(|error| {
                if error == ReachedCohortError::UntranslatableLegacyRecoveryState {
                    FormationError::PhysicalSettlementUnavailable(error)
                } else {
                    FormationError::NoncanonicalState
                }
            })?
        }
        _ => return Err(FormationError::NoncanonicalState),
    };
    cursor = pre_end;
    let post_mode = *encoded
        .get(cursor)
        .ok_or(FormationError::NoncanonicalState)?;
    cursor = cursor
        .checked_add(1)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let post_experience_rest = match (post_mode, base) {
        (0, _) => None,
        (1, _) => {
            let length = read_length(encoded, &mut cursor)?;
            let end = cursor
                .checked_add(length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let state = decode_reached_cohort_state(
                anatomy,
                encoded
                    .get(cursor..end)
                    .ok_or(FormationError::NoncanonicalState)?,
            )
            .map_err(|_| FormationError::NoncanonicalState)?;
            cursor = end;
            Some(state)
        }
        (2, Some(base)) => {
            let end = cursor
                .checked_add(EVIDENCE_DIGEST_BYTES)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let claimed: [u8; EVIDENCE_DIGEST_BYTES] = encoded
                .get(cursor..end)
                .ok_or(FormationError::NoncanonicalState)?
                .try_into()
                .map_err(|_| FormationError::NoncanonicalState)?;
            let current = reached_cohort_state_content_digest(anatomy, base)
                .map_err(|_| FormationError::NoncanonicalState)?;
            let predecessor_v5 = reached_cohort_state_v5_content_digest(anatomy, base).ok();
            let legacy = reached_cohort_state_v4_content_digest(anatomy, base).ok();
            if claimed != current && predecessor_v5 != Some(claimed) && legacy != Some(claimed) {
                return Err(FormationError::NoncanonicalState);
            }
            cursor = end;
            Some(base.clone())
        }
        _ => return Err(FormationError::NoncanonicalState),
    };
    let gate_work_perturbed_neurons = SparseResidentNeuronMask::decode_dense(
        encoded,
        &mut cursor,
        anatomy.neuron_count(),
    )?;
    let receptor_excitation_zeptojoules = if excitation_layout {
        decode_optional_exact_slice(encoded, &mut cursor, anatomy.neuron_count())?
    } else {
        vec![None; anatomy.neuron_count()].into_boxed_slice()
    };
    let (retained_change_neurons, retentively_settled_neurons) = if selective_layout {
        let changed_count = read_length(encoded, &mut cursor)?;
        if changed_count != anatomy.neuron_count() {
            return Err(FormationError::NoncanonicalState);
        }
        let changed_end = cursor
            .checked_add(changed_count)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let changed = decode_bools(
            encoded
                .get(cursor..changed_end)
                .ok_or(FormationError::NoncanonicalState)?,
        )?;
        cursor = changed_end;
        let settled_count = read_length(encoded, &mut cursor)?;
        if settled_count != anatomy.neuron_count() {
            return Err(FormationError::NoncanonicalState);
        }
        let settled_end = cursor
            .checked_add(settled_count)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let settled = decode_bools(
            encoded
                .get(cursor..settled_end)
                .ok_or(FormationError::NoncanonicalState)?,
        )?;
        if settled
            .iter()
            .zip(changed.iter())
            .any(|(settled, changed)| *settled && !*changed)
        {
            return Err(FormationError::NoncanonicalState);
        }
        cursor = settled_end;
        (changed, settled)
    } else {
        let comparison = post_experience_rest.as_ref().or(base);
        let mut changed = Vec::with_capacity(anatomy.neuron_count());
        if let Some(comparison) = comparison {
            for (neuron_index, (predecessor, successor)) in pre_experience_rest
                .neurons()
                .iter()
                .zip(comparison.neurons())
                .enumerate()
            {
                changed.push(
                    sparse_retained_physical_state_delta(predecessor, successor)
                        .map_err(|error| {
                            FormationError::PhysicalSettlementUnavailable(
                                ReachedCohortError::Neuron {
                                    neuron_index,
                                    error,
                                },
                            )
                        })?
                        .is_some(),
                );
            }
        } else {
            changed.resize(anatomy.neuron_count(), false);
        }
        let settled = if post_experience_rest.is_some() {
            changed.clone()
        } else {
            vec![false; anatomy.neuron_count()]
        };
        (changed.into_boxed_slice(), settled.into_boxed_slice())
    };
    let contact_count = read_length(encoded, &mut cursor)?;
    if contact_count != anatomy.contact_count() {
        return Err(FormationError::NoncanonicalState);
    }
    let contact_end = cursor
        .checked_add(contact_count)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let active_electrical_contacts = decode_bools(
        encoded
            .get(cursor..contact_end)
            .ok_or(FormationError::NoncanonicalState)?,
    )?;
    if contact_end != encoded.len() {
        return Err(FormationError::NoncanonicalState);
    }
    Ok(ResidentExperienceEvidence {
        codec,
        physical: ResidentExperiencePhysicalEvidence::Legacy {
            predecessor: pre_experience_rest.into(),
            successor: post_experience_rest.map(Arc::new),
        },
        gate_work_perturbed_neurons,
        receptor_excitation_zeptojoules,
        retained_change_neurons,
        retentively_settled_neurons,
        active_electrical_contacts,
        local_relaxation_observed,
    })
}

/// Decode one experience evidence body in whichever admitted layout its magic
/// names: the retired inline `GLEXP01` or the current `GLEXP02`.
fn decode_any_experience_evidence(
    encoded: &[u8],
    anatomy: &ReachedCohortAnatomy,
    base: Option<&ReachedCohortState>,
) -> Result<ResidentExperienceEvidence, FormationError> {
    if encoded.get(..EXPERIENCE_V7_MAGIC.len()) == Some(EXPERIENCE_V7_MAGIC) {
        decode_sparse_experience_evidence(encoded, anatomy)
    } else if encoded.get(..EXPERIENCE_V2_MAGIC.len()) == Some(EXPERIENCE_V2_MAGIC)
        || encoded.get(..EXPERIENCE_V3_MAGIC.len()) == Some(EXPERIENCE_V3_MAGIC)
        || encoded.get(..EXPERIENCE_V4_MAGIC.len()) == Some(EXPERIENCE_V4_MAGIC)
        || encoded.get(..EXPERIENCE_V5_MAGIC.len()) == Some(EXPERIENCE_V5_MAGIC)
        || encoded.get(..EXPERIENCE_V6_MAGIC.len()) == Some(EXPERIENCE_V6_MAGIC)
    {
        decode_experience_evidence_v2(encoded, anatomy, base)
    } else {
        decode_experience_evidence(encoded, anatomy)
    }
}

fn encode_experience_evidence(
    anatomy: &ReachedCohortAnatomy,
    evidence: &ResidentExperienceEvidence,
) -> Result<Vec<u8>, FormationError> {
    let (pre_experience_rest, post_experience_rest) = evidence
        .legacy_states()
        .ok_or(FormationError::NoncanonicalState)?;
    if !evidence
        .gate_work_perturbed_neurons
        .validates_width(anatomy.neuron_count())
        || evidence.receptor_excitation_zeptojoules.len() != anatomy.neuron_count()
        || evidence
            .receptor_excitation_zeptojoules
            .iter()
            .any(Option::is_some)
        || evidence.retained_change_neurons.len() != anatomy.neuron_count()
        || evidence.retentively_settled_neurons.len() != anatomy.neuron_count()
        || evidence.active_electrical_contacts.len() != anatomy.contact_count()
        || evidence.local_relaxation_observed
    {
        return Err(FormationError::NoncanonicalState);
    }
    let predecessor = encode_reached_cohort_state(anatomy, pre_experience_rest)
        .map_err(|_| FormationError::NoncanonicalState)?;
    let successor = post_experience_rest
        .map(|state| encode_reached_cohort_state(anatomy, state))
        .transpose()
        .map_err(|_| FormationError::NoncanonicalState)?;
    let length = EXPERIENCE_MAGIC
        .len()
        .checked_add(8)
        .and_then(|value| value.checked_add(predecessor.len()))
        .and_then(|value| value.checked_add(1))
        .and_then(|value| {
            successor.as_ref().map_or(Some(value), |successor| {
                value.checked_add(8)?.checked_add(successor.len())
            })
        })
        .and_then(|value| value.checked_add(8))
        .and_then(|value| value.checked_add(anatomy.neuron_count()))
        .and_then(|value| value.checked_add(8))
        .and_then(|value| value.checked_add(evidence.active_electrical_contacts.len()))
        .ok_or(FormationError::ArithmeticOverflow)?;
    let mut encoded = Vec::with_capacity(length);
    encoded.extend_from_slice(EXPERIENCE_MAGIC);
    push_length(&mut encoded, predecessor.len())?;
    encoded.extend_from_slice(&predecessor);
    encoded.push(u8::from(successor.is_some()));
    if let Some(successor) = successor {
        push_length(&mut encoded, successor.len())?;
        encoded.extend_from_slice(&successor);
    }
    evidence
        .gate_work_perturbed_neurons
        .encode_dense(&mut encoded, anatomy.neuron_count())?;
    push_length(&mut encoded, evidence.active_electrical_contacts.len())?;
    encoded.extend(
        evidence
            .active_electrical_contacts
            .iter()
            .map(|value| u8::from(*value)),
    );
    Ok(encoded)
}

fn decode_optional_experience_evidence(
    bytes: &[u8],
    cursor: &mut usize,
    anatomy: &ReachedCohortAnatomy,
    base: &ReachedCohortState,
    retained: bool,
) -> Result<Option<ResidentExperienceEvidence>, FormationError> {
    let present = *bytes
        .get(*cursor)
        .ok_or(FormationError::NoncanonicalState)?;
    *cursor = cursor
        .checked_add(1)
        .ok_or(FormationError::ArithmeticOverflow)?;
    match present {
        0 => Ok(None),
        1 => {
            let length = read_length(bytes, cursor)?;
            let end = cursor
                .checked_add(length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let evidence = match decode_any_experience_evidence(
                bytes
                    .get(*cursor..end)
                    .ok_or(FormationError::NoncanonicalState)?,
                anatomy,
                Some(base),
            ) {
                Ok(evidence) => evidence,
                Err(FormationError::PhysicalSettlementUnavailable(
                    ReachedCohortError::UntranslatableLegacyRecoveryState,
                )) if !retained => {
                    *cursor = end;
                    return Ok(None);
                }
                Err(error) => return Err(error),
            };
            *cursor = end;
            if evidence.is_retained() != retained {
                return Err(FormationError::NoncanonicalState);
            }
            if retained {
                let retained_count = if let Some(members) = evidence.retained_members() {
                    members.len()
                } else {
                    let (predecessor, post) = evidence
                        .legacy_states()
                        .ok_or(FormationError::NoncanonicalState)?;
                    let post = post.ok_or(FormationError::NoncanonicalState)?;
                    predecessor
                        .neurons()
                        .iter()
                        .zip(post.neurons())
                        .enumerate()
                        .try_fold(0usize, |count, (neuron_index, (prior, successor))| {
                            let changed = evidence.retentively_settled_neurons[neuron_index]
                                && sparse_retained_physical_state_delta(prior, successor)
                                    .map_err(|error| {
                                        FormationError::PhysicalSettlementUnavailable(
                                            ReachedCohortError::Neuron {
                                                neuron_index,
                                                error,
                                            },
                                        )
                                    })?
                                    .is_some();
                            count
                                .checked_add(usize::from(changed))
                                .ok_or(FormationError::ArithmeticOverflow)
                        })?
                };
                if retained_count < 3 {
                    return Err(FormationError::NoncanonicalState);
                }
            }
            Ok(Some(evidence))
        }
        _ => Err(FormationError::NoncanonicalState),
    }
}

fn decode_experience_evidence(
    encoded: &[u8],
    anatomy: &ReachedCohortAnatomy,
) -> Result<ResidentExperienceEvidence, FormationError> {
    if encoded.get(..EXPERIENCE_MAGIC.len()) != Some(EXPERIENCE_MAGIC) {
        return Err(FormationError::NoncanonicalState);
    }
    let mut cursor = EXPERIENCE_MAGIC.len();
    let predecessor_length = read_length(encoded, &mut cursor)?;
    let predecessor_end = cursor
        .checked_add(predecessor_length)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let pre_experience_rest = decode_reached_cohort_state(
        anatomy,
        encoded
            .get(cursor..predecessor_end)
            .ok_or(FormationError::NoncanonicalState)?,
    )
    .map_err(|_| FormationError::NoncanonicalState)?;
    cursor = predecessor_end;
    let post_experience_rest = match encoded
        .get(cursor)
        .copied()
        .ok_or(FormationError::NoncanonicalState)?
    {
        0 => {
            cursor = cursor
                .checked_add(1)
                .ok_or(FormationError::ArithmeticOverflow)?;
            None
        }
        1 => {
            cursor = cursor
                .checked_add(1)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let length = read_length(encoded, &mut cursor)?;
            let end = cursor
                .checked_add(length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let state = decode_reached_cohort_state(
                anatomy,
                encoded
                    .get(cursor..end)
                    .ok_or(FormationError::NoncanonicalState)?,
            )
            .map_err(|_| FormationError::NoncanonicalState)?;
            cursor = end;
            Some(state)
        }
        _ => return Err(FormationError::NoncanonicalState),
    };
    let gate_work_perturbed_neurons = SparseResidentNeuronMask::decode_dense(
        encoded,
        &mut cursor,
        anatomy.neuron_count(),
    )?;
    let contact_count = read_length(encoded, &mut cursor)?;
    if contact_count != anatomy.contact_count() {
        return Err(FormationError::NoncanonicalState);
    }
    let contact_end = cursor
        .checked_add(contact_count)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let active_electrical_contacts = decode_bools(
        encoded
            .get(cursor..contact_end)
            .ok_or(FormationError::NoncanonicalState)?,
    )?;
    if contact_end != encoded.len() {
        return Err(FormationError::NoncanonicalState);
    }
    let mut retained_change_neurons = Vec::with_capacity(anatomy.neuron_count());
    for (neuron_index, predecessor) in pre_experience_rest.neurons().iter().enumerate() {
        let changed = post_experience_rest
            .as_ref()
            .map(|successor| {
                sparse_retained_physical_state_delta(
                    predecessor,
                    &successor.neurons()[neuron_index],
                )
                .map(|delta| delta.is_some())
                .map_err(|error| {
                    FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                        neuron_index,
                        error,
                    })
                })
            })
            .transpose()?
            .unwrap_or(false);
        retained_change_neurons.push(changed);
    }
    let retentively_settled_neurons = if post_experience_rest.is_some() {
        retained_change_neurons.clone()
    } else {
        vec![false; anatomy.neuron_count()]
    };
    Ok(ResidentExperienceEvidence {
        codec: ExperienceEvidenceCodec::V1,
        physical: ResidentExperiencePhysicalEvidence::Legacy {
            predecessor: pre_experience_rest.into(),
            successor: post_experience_rest.map(Arc::new),
        },
        gate_work_perturbed_neurons,
        receptor_excitation_zeptojoules: vec![None; anatomy.neuron_count()].into_boxed_slice(),
        retained_change_neurons: retained_change_neurons.into_boxed_slice(),
        retentively_settled_neurons: retentively_settled_neurons.into_boxed_slice(),
        active_electrical_contacts,
        local_relaxation_observed: false,
    })
}

fn encode_recurrence_evidence(
    anatomy: &ReachedCohortAnatomy,
    evidence: &ResidentRecurrenceEvidence,
) -> Result<Vec<u8>, FormationError> {
    let neuron_count = anatomy.neuron_count();
    let contact_count = anatomy.contact_count();
    if !evidence
        .gate_work_perturbed_neurons
        .validates_width(neuron_count)
        || evidence.receptor_excitation_zeptojoules.len() != neuron_count
        || evidence.physically_changed_neurons.len() != neuron_count
        || evidence.active_recurrence_contacts.len() != contact_count
        || evidence.gate_work_perturbed_neurons.is_empty()
    {
        return Err(FormationError::NoncanonicalState);
    }
    let excitation_layout = evidence
        .receptor_excitation_zeptojoules
        .iter()
        .any(Option::is_some);
    let mut encoded = Vec::new();
    encoded.extend_from_slice(if evidence.endogenous && excitation_layout {
        ENDOGENOUS_EXCITATION_RECURRENCE_MAGIC
    } else if excitation_layout {
        EXCITATION_RECURRENCE_MAGIC
    } else if evidence.endogenous && evidence.carries_physical_change_codec {
        ENDOGENOUS_PHYSICAL_RECURRENCE_MAGIC
    } else if evidence.endogenous {
        ENDOGENOUS_RECURRENCE_MAGIC
    } else if evidence.carries_physical_change_codec {
        PHYSICAL_RECURRENCE_MAGIC
    } else {
        RECURRENCE_MAGIC
    });
    evidence
        .gate_work_perturbed_neurons
        .encode_dense(&mut encoded, neuron_count)?;
    if excitation_layout {
        encode_optional_exact_slice(&mut encoded, &evidence.receptor_excitation_zeptojoules)?;
    }
    if evidence.carries_physical_change_codec {
        encode_bool_slice(&mut encoded, &evidence.physically_changed_neurons)?;
    }
    encode_bool_slice(&mut encoded, &evidence.active_recurrence_contacts)?;
    Ok(encoded)
}

fn decode_recurrence_evidence(
    encoded: &[u8],
    anatomy: &ReachedCohortAnatomy,
) -> Result<ResidentRecurrenceEvidence, FormationError> {
    let (endogenous, carries_physical_change, excitation_layout) = if encoded
        .get(..EXCITATION_RECURRENCE_MAGIC.len())
        == Some(EXCITATION_RECURRENCE_MAGIC)
    {
        (false, true, true)
    } else if encoded.get(..ENDOGENOUS_EXCITATION_RECURRENCE_MAGIC.len())
        == Some(ENDOGENOUS_EXCITATION_RECURRENCE_MAGIC)
    {
        (true, true, true)
    } else if encoded.get(..PHYSICAL_RECURRENCE_MAGIC.len()) == Some(PHYSICAL_RECURRENCE_MAGIC) {
        (false, true, false)
    } else if encoded.get(..ENDOGENOUS_PHYSICAL_RECURRENCE_MAGIC.len())
        == Some(ENDOGENOUS_PHYSICAL_RECURRENCE_MAGIC)
    {
        (true, true, false)
    } else if encoded.get(..RECURRENCE_MAGIC.len()) == Some(RECURRENCE_MAGIC) {
        (false, false, false)
    } else if encoded.get(..ENDOGENOUS_RECURRENCE_MAGIC.len()) == Some(ENDOGENOUS_RECURRENCE_MAGIC)
    {
        (true, false, false)
    } else {
        return Err(FormationError::NoncanonicalState);
    };
    let mut cursor = RECURRENCE_MAGIC.len();
    let gate_work_perturbed_neurons = SparseResidentNeuronMask::decode_dense(
        encoded,
        &mut cursor,
        anatomy.neuron_count(),
    )?;
    let receptor_excitation_zeptojoules = if excitation_layout {
        decode_optional_exact_slice(encoded, &mut cursor, anatomy.neuron_count())?
    } else {
        vec![None; anatomy.neuron_count()].into_boxed_slice()
    };
    let physically_changed_neurons = if carries_physical_change {
        decode_bool_slice(encoded, &mut cursor, anatomy.neuron_count())?
    } else {
        vec![false; anatomy.neuron_count()].into_boxed_slice()
    };
    let active_recurrence_contacts =
        decode_bool_slice(encoded, &mut cursor, anatomy.contact_count())?;
    if cursor != encoded.len() || gate_work_perturbed_neurons.is_empty() {
        return Err(FormationError::NoncanonicalState);
    }
    Ok(ResidentRecurrenceEvidence {
        carries_physical_change_codec: carries_physical_change,
        gate_work_perturbed_neurons,
        receptor_excitation_zeptojoules,
        physically_changed_neurons,
        active_recurrence_contacts,
        endogenous,
    })
}

fn decode_optional_recurrence_evidence(
    bytes: &[u8],
    cursor: &mut usize,
    anatomy: &ReachedCohortAnatomy,
) -> Result<Option<ResidentRecurrenceEvidence>, FormationError> {
    let present = *bytes
        .get(*cursor)
        .ok_or(FormationError::NoncanonicalState)?;
    *cursor = cursor
        .checked_add(1)
        .ok_or(FormationError::ArithmeticOverflow)?;
    match present {
        0 => Ok(None),
        1 => {
            let length = read_length(bytes, cursor)?;
            let end = cursor
                .checked_add(length)
                .ok_or(FormationError::ArithmeticOverflow)?;
            let evidence = decode_recurrence_evidence(
                bytes
                    .get(*cursor..end)
                    .ok_or(FormationError::NoncanonicalState)?,
                anatomy,
            )?;
            *cursor = end;
            Ok(Some(evidence))
        }
        _ => Err(FormationError::NoncanonicalState),
    }
}

fn encode_bool_slice(encoded: &mut Vec<u8>, values: &[bool]) -> Result<(), FormationError> {
    push_length(encoded, values.len())?;
    encoded.extend(values.iter().map(|value| u8::from(*value)));
    Ok(())
}

fn decode_bool_slice(
    encoded: &[u8],
    cursor: &mut usize,
    expected: usize,
) -> Result<Box<[bool]>, FormationError> {
    let count = read_length(encoded, cursor)?;
    if count != expected {
        return Err(FormationError::NoncanonicalState);
    }
    let end = cursor
        .checked_add(count)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let values = decode_bools(
        encoded
            .get(*cursor..end)
            .ok_or(FormationError::NoncanonicalState)?,
    )?;
    *cursor = end;
    Ok(values)
}

fn encode_optional_exact_slice(
    encoded: &mut Vec<u8>,
    values: &[Option<ExactRational>],
) -> Result<(), FormationError> {
    push_length(encoded, values.len())?;
    for value in values {
        match value {
            None => encoded.push(0),
            Some(value) => {
                encoded.push(1);
                let (numerator, denominator) = value.parts();
                encoded.extend_from_slice(&numerator.to_le_bytes());
                encoded.extend_from_slice(&denominator.to_le_bytes());
            }
        }
    }
    Ok(())
}

fn decode_optional_exact_slice(
    encoded: &[u8],
    cursor: &mut usize,
    expected: usize,
) -> Result<Box<[Option<ExactRational>]>, FormationError> {
    if read_length(encoded, cursor)? != expected {
        return Err(FormationError::NoncanonicalState);
    }
    let mut values = Vec::new();
    values
        .try_reserve_exact(expected)
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    for _ in 0..expected {
        let present = *encoded
            .get(*cursor)
            .ok_or(FormationError::NoncanonicalState)?;
        *cursor = cursor
            .checked_add(1)
            .ok_or(FormationError::ArithmeticOverflow)?;
        match present {
            0 => values.push(None),
            1 => {
                let numerator_end = cursor
                    .checked_add(16)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let numerator = i128::from_le_bytes(
                    encoded
                        .get(*cursor..numerator_end)
                        .ok_or(FormationError::NoncanonicalState)?
                        .try_into()
                        .map_err(|_| FormationError::NoncanonicalState)?,
                );
                *cursor = numerator_end;
                let denominator_end = cursor
                    .checked_add(16)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let denominator = u128::from_le_bytes(
                    encoded
                        .get(*cursor..denominator_end)
                        .ok_or(FormationError::NoncanonicalState)?
                        .try_into()
                        .map_err(|_| FormationError::NoncanonicalState)?,
                );
                *cursor = denominator_end;
                values.push(Some(
                    ExactRational::new(numerator, denominator)
                        .map_err(|_| FormationError::NoncanonicalState)?,
                ));
            }
            _ => return Err(FormationError::NoncanonicalState),
        }
    }
    Ok(values.into_boxed_slice())
}

fn push_length(encoded: &mut Vec<u8>, value: usize) -> Result<(), FormationError> {
    encoded.extend_from_slice(
        &u64::try_from(value)
            .map_err(|_| FormationError::ArithmeticOverflow)?
            .to_le_bytes(),
    );
    Ok(())
}

fn read_length(bytes: &[u8], cursor: &mut usize) -> Result<usize, FormationError> {
    let end = cursor
        .checked_add(8)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let value = usize::try_from(u64::from_le_bytes(
        bytes
            .get(*cursor..end)
            .ok_or(FormationError::NoncanonicalState)?
            .try_into()
            .map_err(|_| FormationError::NoncanonicalState)?,
    ))
    .map_err(|_| FormationError::ArithmeticOverflow)?;
    *cursor = end;
    Ok(value)
}

fn decode_bools(encoded: &[u8]) -> Result<Box<[bool]>, FormationError> {
    encoded
        .iter()
        .map(|value| match value {
            0 => Ok(false),
            1 => Ok(true),
            _ => Err(FormationError::NoncanonicalState),
        })
        .collect::<Result<Vec<_>, _>>()
        .map(Vec::into_boxed_slice)
}

const DORMANT_LINEAGE_SEED_MAGIC: &[u8; 8] = b"GLDLS01\0";

fn same_dormant_source(
    left: &crate::joint_source_episode::JointSourcePortView,
    right: &crate::joint_source_episode::JointSourcePortView,
) -> bool {
    left.sense == right.sense
        && left.topology_index == right.topology_index
        && left.sensor_id == right.sensor_id
        && left.substream_id == right.substream_id
}

fn valid_local_lineage(lineage: [u8; 16]) -> bool {
    if lineage[..8] != *LINEAGE_DOMAIN {
        return false;
    }
    let ordinal = u64::from_be_bytes(
        lineage[8..]
            .try_into()
            .expect("fixed local lineage ordinal width"),
    );
    ordinal != 0
}

fn lineage_ordinal(lineage: [u8; 16]) -> Result<u64, FormationError> {
    if !valid_local_lineage(lineage) {
        return Err(FormationError::NoncanonicalState);
    }
    Ok(u64::from_be_bytes(
        lineage[8..]
            .try_into()
            .map_err(|_| FormationError::NoncanonicalState)?,
    ))
}

fn allocate_local_lineage(next_lineage_ordinal: &mut u64) -> Result<[u8; 16], FormationError> {
    let ordinal = *next_lineage_ordinal;
    if ordinal == 0 {
        return Err(FormationError::NeuronLineageAuthorityAbsent);
    }
    let successor = ordinal
        .checked_add(1)
        .ok_or(FormationError::ArithmeticOverflow)?;
    *next_lineage_ordinal = successor;
    local_lineage_from_ordinal(ordinal)
}

fn local_lineage_from_ordinal(ordinal: u64) -> Result<[u8; 16], FormationError> {
    if ordinal == 0 {
        return Err(FormationError::NeuronLineageAuthorityAbsent);
    }
    let mut lineage = [0u8; 16];
    lineage[..8].copy_from_slice(LINEAGE_DOMAIN);
    lineage[8..].copy_from_slice(&ordinal.to_be_bytes());
    Ok(lineage)
}

struct ReachedLineageAdmission {
    lineage: [u8; 16],
    claimed_resting_neuron: Option<MaterializedRestingNeuron>,
}

fn reached_genesis_cell_from_admission(
    shared: &crate::joint_uf_neuron_boundary::SharedCompleteJointField,
    coordinate_index: usize,
    source_site: NeuronSourceSite,
    admission: &ReachedLineageAdmission,
) -> Result<ReachedNeuronGenesisCell, FormationError> {
    let perspective = bind_neuron_perspective(shared, coordinate_index, 0)
        .map_err(FormationError::JointFieldUnavailable)?;
    let single_body_terminal = source_site.body_proprioceptor_terminal().is_some();
    let neuron = match &admission.claimed_resting_neuron {
        Some(resting) if single_body_terminal => {
            reach_quiescent_single_terminal_virtual_material_neuron(
                perspective,
                &source_site,
                resting.place,
                &resting.anatomy,
                &resting.state,
            )
        }
        Some(resting) => reach_quiescent_virtual_material_neuron(
            perspective,
            &source_site,
            resting.place,
            &resting.anatomy,
            &resting.state,
        ),
        None if single_body_terminal => {
            create_single_terminal_virtual_material_neuron(perspective, &source_site)
        }
        None => create_virtual_material_neuron(perspective, &source_site),
    }
    .map_err(FormationError::PhysicalGenesisUnavailable)?;
    let (anatomy, state, _) = neuron.into_parts();
    Ok(ReachedNeuronGenesisCell {
        anatomy,
        lineage: admission.lineage,
        mount: ReachedNeuronMount::Receptor(source_site),
        state,
    })
}

fn claim_resting_or_allocate_lineage(
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    source_site: &NeuronSourceSite,
    next_lineage_ordinal: &mut u64,
) -> Result<ReachedLineageAdmission, FormationError> {
    let place = DeclaredNeuronPlace::from_source_site(source_site);
    if let Some(population) = resting_population.as_ref() {
        if let Some(offset) = population.population_offset(place) {
            let (successor, materialized) = population
                .claim(offset)
                .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?;
            let lineage = local_lineage_from_ordinal(materialized.lineage_ordinal)?;
            *resting_population = Some(successor);
            return Ok(ReachedLineageAdmission {
                lineage,
                claimed_resting_neuron: Some(materialized),
            });
        }
    }
    Ok(ReachedLineageAdmission {
        lineage: allocate_local_lineage(next_lineage_ordinal)?,
        claimed_resting_neuron: None,
    })
}

fn mount_intrinsic_neuron_at_place(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    place: DeclaredNeuronPlace,
) -> Result<[u8; 16], FormationError> {
    let existing = cohorts
        .iter()
        .flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        })
        .filter(|(mount, _)| mount.place() == place)
        .map(|(_, lineage)| *lineage)
        .collect::<Vec<_>>();
    match existing.as_slice() {
        [lineage] => return Ok(*lineage),
        [] => {}
        _ => return Err(FormationError::NeuronLineageAuthorityChanged),
    }

    let (lineage, anatomy, state) = if let Some(population) = resting_population.as_ref() {
        if let Some(offset) = population.population_offset(place) {
            let (successor, materialized) = population
                .claim(offset)
                .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?;
            let lineage = local_lineage_from_ordinal(materialized.lineage_ordinal)?;
            *resting_population = Some(successor);
            (lineage, materialized.anatomy, materialized.state)
        } else {
            *resting_population = Some(
                population
                    .admit_one_external_growth_unit()
                    .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?,
            );
            let neuron = create_quiescent_virtual_material_neuron(place)
                .map_err(FormationError::PhysicalGenesisUnavailable)?;
            (
                allocate_local_lineage(next_lineage_ordinal)?,
                neuron.anatomy,
                neuron.state,
            )
        }
    } else {
        let neuron = create_quiescent_virtual_material_neuron(place)
            .map_err(FormationError::PhysicalGenesisUnavailable)?;
        (
            allocate_local_lineage(next_lineage_ordinal)?,
            neuron.anatomy,
            neuron.state,
        )
    };
    let sparse = SparseElectricalAnatomy::new(1, Vec::new())
        .map_err(FormationError::ResidentElectricalUnavailable)?;
    let sparse_state = SparseElectricalState::genesis(&sparse);
    let cohort_anatomy = ReachedCohortAnatomy::new_mounted(
        vec![anatomy],
        vec![lineage],
        vec![ReachedNeuronMount::intrinsic(place)],
        sparse,
    )
    .map_err(FormationError::PhysicalSettlementUnavailable)?;
    let cohort_state = ReachedCohortState::new(&cohort_anatomy, vec![state], sparse_state)
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
    cohorts.push(ResidentReachedCohort {
        anatomy: cohort_anatomy,
        state: cohort_state.into(),
        pending_experience: None,
        retained_experience: None,
        pending_recurrence: None,
    });
    Ok(lineage)
}

/// Materialize one source-independent local-integration neuron at a unique
/// declared projection of each reached receptor place, then author one sparse
/// physical contact from the receptor lineage to that local integration
/// lineage. Existing cells and contacts are reused exactly; this is
/// developmental specialization, not a per-occurrence generator.
fn mount_reached_local_integration(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    reached_receptors: &[([u8; 16], DeclaredNeuronPlace)],
) -> Result<(), FormationError> {
    for (receptor_lineage, receptor_place) in reached_receptors {
        let integration_place = local_integration_place(*receptor_place)?;
        let integration_lineage = mount_intrinsic_neuron_at_place(
            cohorts,
            resting_population,
            next_lineage_ordinal,
            integration_place,
        )?;
        if !electrical_fabric.contains_contact(*receptor_lineage, integration_lineage) {
            *electrical_fabric = electrical_fabric
                .append_contact(
                    *receptor_lineage,
                    integration_lineage,
                    ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                )
                .map_err(FormationError::ResidentElectricalUnavailable)?;
        }
    }
    Ok(())
}

/// Project one receptor's own two-dimensional declared place into a unique
/// local-integration topology.  `declared_neuron_territory - 1` is the existing
/// injective Cantor pairing of `(sense layer, topology index)`, so receptors
/// from different sensory coordinate systems can never alias merely because
/// both happen to call one local site `0`.
fn local_integration_place(
    receptor_place: DeclaredNeuronPlace,
) -> Result<DeclaredNeuronPlace, FormationError> {
    let proprioceptor_start = u32::try_from(BODY_PROPRIOCEPTOR_TOPOLOGY_OFFSET)
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    let proprioceptor_end = proprioceptor_start
        .checked_add(
            u32::try_from(BODY_EFFECTOR_TERMINAL_COUNT)
                .map_err(|_| FormationError::ArithmeticOverflow)?,
        )
        .ok_or(FormationError::ArithmeticOverflow)?;
    if receptor_place.layer() == u32::from(PhysicalSourceSense::Body.declared_layer())
        && (proprioceptor_start..proprioceptor_end).contains(&receptor_place.topology_index())
    {
        let terminal_ordinal = receptor_place
            .topology_index()
            .checked_sub(proprioceptor_start)
            .ok_or(FormationError::ArithmeticOverflow)?;
        let topology_index = BODY_PROPRIOCEPTOR_LAYER6_TOPOLOGY_OFFSET
            .checked_add(terminal_ordinal)
            .ok_or(FormationError::ArithmeticOverflow)?;
        return Ok(DeclaredNeuronPlace::new(6, topology_index));
    }
    let paired = declared_neuron_territory(receptor_place)
        .map_err(|_| FormationError::ArithmeticOverflow)?
        .checked_sub(1)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let topology_index = u32::try_from(paired).map_err(|_| FormationError::ArithmeticOverflow)?;
    Ok(DeclaredNeuronPlace::new(6, topology_index))
}

fn body_regulation_place(
    receptor_place: DeclaredNeuronPlace,
    integration_place: DeclaredNeuronPlace,
) -> Result<DeclaredNeuronPlace, FormationError> {
    let proprioceptor_start = u32::try_from(BODY_PROPRIOCEPTOR_TOPOLOGY_OFFSET)
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    let proprioceptor_end = proprioceptor_start
        .checked_add(
            u32::try_from(BODY_EFFECTOR_TERMINAL_COUNT)
                .map_err(|_| FormationError::ArithmeticOverflow)?,
        )
        .ok_or(FormationError::ArithmeticOverflow)?;
    if receptor_place.layer() == u32::from(PhysicalSourceSense::Body.declared_layer())
        && (proprioceptor_start..proprioceptor_end).contains(&receptor_place.topology_index())
    {
        let terminal_ordinal = receptor_place
            .topology_index()
            .checked_sub(proprioceptor_start)
            .ok_or(FormationError::ArithmeticOverflow)?;
        return Ok(DeclaredNeuronPlace::new(
            8,
            BODY_PROPRIOCEPTOR_LAYER8_TOPOLOGY_OFFSET
                .checked_add(terminal_ordinal)
                .ok_or(FormationError::ArithmeticOverflow)?,
        ));
    }
    Ok(DeclaredNeuronPlace::new(
        8,
        integration_place.topology_index(),
    ))
}

/// Mount one new source-independent neuron at the first quiescent place in a
/// projection layer.  This is reached-frontier growth: it claims one compactly
/// declared cell and never scans or materializes the resting population.
fn mount_next_intrinsic_in_layer(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    layer: u32,
) -> Result<[u8; 16], FormationError> {
    let (lineage, place, anatomy, state) = if let Some(population) = resting_population.as_ref() {
        let (successor, materialized) = population
            .claim_next_in_layer(layer)
            .map_err(FormationError::DevelopmentalRestingPopulationUnavailable)?;
        let lineage = local_lineage_from_ordinal(materialized.lineage_ordinal)?;
        *resting_population = Some(successor);
        (
            lineage,
            materialized.place,
            materialized.anatomy,
            materialized.state,
        )
    } else {
        let next_topology = cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.mounts())
            .filter(|mount| mount.place().layer() == layer)
            .map(|mount| mount.place().topology_index())
            .max()
            .map_or(Ok(0), |maximum| {
                maximum
                    .checked_add(1)
                    .ok_or(FormationError::ArithmeticOverflow)
            })?;
        let place = DeclaredNeuronPlace::new(layer, next_topology);
        let neuron = create_quiescent_virtual_material_neuron(place)
            .map_err(FormationError::PhysicalGenesisUnavailable)?;
        (
            allocate_local_lineage(next_lineage_ordinal)?,
            place,
            neuron.anatomy,
            neuron.state,
        )
    };
    let sparse = SparseElectricalAnatomy::new(1, Vec::new())
        .map_err(FormationError::ResidentElectricalUnavailable)?;
    let sparse_state = SparseElectricalState::genesis(&sparse);
    let cohort_anatomy = ReachedCohortAnatomy::new_mounted(
        vec![anatomy],
        vec![lineage],
        vec![ReachedNeuronMount::intrinsic(place)],
        sparse,
    )
    .map_err(FormationError::PhysicalSettlementUnavailable)?;
    let cohort_state = ReachedCohortState::new(&cohort_anatomy, vec![state], sparse_state)
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
    cohorts.push(ResidentReachedCohort {
        anatomy: cohort_anatomy,
        state: cohort_state.into(),
        pending_experience: None,
        retained_experience: None,
        pending_recurrence: None,
    });
    Ok(lineage)
}

/// Grow or reuse one physical cross-sensory association reached by this exact
/// occurrence.  Membership comes only from distinct layer-6 cells whose own
/// receptors were externally reached; matching indices, labels, and source
/// order have no authority.  The retained sparse contacts are the assembly.
fn mount_reached_cross_sensory_association(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    externally_reached_lineages: &[[u8; 16]],
) -> Result<Option<[u8; 16]>, FormationError> {
    let mounted = cohorts
        .iter()
        .flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        })
        .map(|(mount, lineage)| (*lineage, mount.clone()))
        .collect::<Vec<_>>();
    let mut sensory_layers = Vec::<u32>::new();
    let mut integration_lineages = Vec::<[u8; 16]>::new();
    for receptor_lineage in externally_reached_lineages {
        let Some((_, receptor_mount)) = mounted
            .iter()
            .find(|(lineage, mount)| lineage == receptor_lineage && mount.source_site().is_some())
        else {
            continue;
        };
        let receptor_place = receptor_mount.place();
        if !sensory_layers.contains(&receptor_place.layer()) {
            sensory_layers.push(receptor_place.layer());
        }
        let integration_place = local_integration_place(receptor_place)?;
        let integration = mounted
            .iter()
            .filter(|(_, mount)| {
                mount.source_site().is_none() && mount.place() == integration_place
            })
            .map(|(lineage, _)| *lineage)
            .collect::<Vec<_>>();
        let [integration_lineage] = integration.as_slice() else {
            return Err(FormationError::NeuronLineageAuthorityChanged);
        };
        if !electrical_fabric.contains_contact(*receptor_lineage, *integration_lineage) {
            return Err(FormationError::NeuronLineageAuthorityAbsent);
        }
        if !integration_lineages.contains(integration_lineage) {
            integration_lineages.push(*integration_lineage);
        }
    }
    integration_lineages.sort_unstable();
    sensory_layers.sort_unstable();
    if integration_lineages.len() < 3 || sensory_layers.len() < 2 {
        return Ok(None);
    }

    let layer_of = |lineage: [u8; 16]| {
        mounted
            .iter()
            .find(|(candidate, _)| *candidate == lineage)
            .map(|(_, mount)| mount.place().layer())
    };
    let mut matching_associations = Vec::new();
    for (association_lineage, association_mount) in mounted
        .iter()
        .filter(|(_, mount)| mount.source_site().is_none() && mount.place().layer() == 7)
    {
        let mut layer_six_neighbours = Vec::new();
        for (left, right) in electrical_fabric.contact_endpoints() {
            let left_lineage = electrical_fabric.lineages()[left];
            let right_lineage = electrical_fabric.lineages()[right];
            let neighbour = if left_lineage == *association_lineage {
                Some(right_lineage)
            } else if right_lineage == *association_lineage {
                Some(left_lineage)
            } else {
                None
            };
            if let Some(neighbour) = neighbour {
                if layer_of(neighbour) == Some(6) {
                    layer_six_neighbours.push(neighbour);
                }
            }
        }
        layer_six_neighbours.sort_unstable();
        layer_six_neighbours.dedup();
        if layer_six_neighbours == integration_lineages {
            matching_associations.push(*association_lineage);
        }
        let _ = association_mount;
    }
    let association_lineage = match matching_associations.as_slice() {
        [lineage] => *lineage,
        [] => mount_next_intrinsic_in_layer(cohorts, resting_population, next_lineage_ordinal, 7)?,
        _ => return Err(FormationError::NeuronLineageAuthorityChanged),
    };
    for integration_lineage in integration_lineages {
        if !electrical_fabric.contains_contact(integration_lineage, association_lineage) {
            *electrical_fabric = electrical_fabric
                .append_contact(
                    integration_lineage,
                    association_lineage,
                    ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                )
                .map_err(FormationError::ResidentElectricalUnavailable)?;
        }
    }
    Ok(Some(association_lineage))
}

/// Couple each genuinely reached body-or-balance receptor to its own local
/// regulatory neuron.  The route is receptor layer 5 -> its already-mounted
/// layer-6 integrator -> the topology-corresponding layer-8 cell.  No body-wide
/// energy total, fuel fraction, readiness value, or other bookkeeping scalar
/// is sensed here: locality and membership come only from the reached physical
/// receptor lineage carried by this exact occurrence.
fn mount_reached_body_regulation(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    externally_reached_lineages: &[[u8; 16]],
) -> Result<Vec<[u8; 16]>, FormationError> {
    let mounted = cohorts
        .iter()
        .flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        })
        .map(|(mount, lineage)| (*lineage, mount.clone()))
        .collect::<Vec<_>>();
    let reached_body_receptors = externally_reached_lineages
        .iter()
        .filter_map(|lineage| {
            mounted
                .iter()
                .find(|(candidate, mount)| {
                    candidate == lineage
                        && mount.source_site().is_some()
                        && mount.place().layer() == 5
                })
                .map(|(_, mount)| (*lineage, mount.place()))
        })
        .collect::<Vec<_>>();

    let mut reached_regulation = Vec::new();
    for (receptor_lineage, receptor_place) in reached_body_receptors {
        let integration_place = local_integration_place(receptor_place)?;
        let integration = mounted
            .iter()
            .filter(|(_, mount)| {
                mount.source_site().is_none() && mount.place() == integration_place
            })
            .map(|(lineage, _)| *lineage)
            .collect::<Vec<_>>();
        let [integration_lineage] = integration.as_slice() else {
            return Err(FormationError::NeuronLineageAuthorityChanged);
        };
        if !electrical_fabric.contains_contact(receptor_lineage, *integration_lineage) {
            return Err(FormationError::NeuronLineageAuthorityAbsent);
        }
        let regulation_place = body_regulation_place(receptor_place, integration_place)?;
        let regulation_lineage = mount_intrinsic_neuron_at_place(
            cohorts,
            resting_population,
            next_lineage_ordinal,
            regulation_place,
        )?;
        if !electrical_fabric.contains_contact(*integration_lineage, regulation_lineage) {
            *electrical_fabric = electrical_fabric
                .append_contact(
                    *integration_lineage,
                    regulation_lineage,
                    ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                )
                .map_err(FormationError::ResidentElectricalUnavailable)?;
        }
        if !reached_regulation.contains(&regulation_lineage) {
            reached_regulation.push(regulation_lineage);
    }
    }
    Ok(reached_regulation)
}

/// Relate body regulation to the association material that physically moved
/// with it in this exact organism interval.  Layer 10 is developmental
/// geography, not an emotion label: its only authority is the coincident
/// changed layer-7/layer-8 lineage set and the sparse contacts retained here.
/// Reaching the same set again reuses the same cell without population growth.
fn mount_reached_affective_reach(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    physically_transitioned_lineages: &[[u8; 16]],
) -> Result<(), FormationError> {
    let mounted = cohorts
        .iter()
        .flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        })
        .map(|(mount, lineage)| (*lineage, mount.clone()))
        .collect::<Vec<_>>();
    let mut association = Vec::new();
    let mut body_regulation = Vec::new();
    for lineage in physically_transitioned_lineages {
        let Some((_, mount)) = mounted.iter().find(|(candidate, _)| candidate == lineage) else {
            return Err(FormationError::NeuronLineageAuthorityAbsent);
        };
        match mount.place().layer() {
            7 if !association.contains(lineage) => association.push(*lineage),
            8 if !body_regulation.contains(lineage) => body_regulation.push(*lineage),
            _ => {}
        }
    }
    if association.is_empty() || body_regulation.is_empty() {
        return Ok(());
    }
    let mut participants = association;
    participants.extend(body_regulation);
    participants.sort_unstable();
    participants.dedup();

    let layer_of = |lineage: [u8; 16]| {
        mounted
            .iter()
            .find(|(candidate, _)| *candidate == lineage)
            .map(|(_, mount)| mount.place().layer())
    };
    let mut matching = Vec::new();
    for (candidate, _) in mounted
        .iter()
        .filter(|(_, mount)| mount.source_site().is_none() && mount.place().layer() == 10)
    {
        let mut neighbours = Vec::new();
        for (left, right) in electrical_fabric.contact_endpoints() {
            let left_lineage = electrical_fabric.lineages()[left];
            let right_lineage = electrical_fabric.lineages()[right];
            let neighbour = if left_lineage == *candidate {
                Some(right_lineage)
            } else if right_lineage == *candidate {
                Some(left_lineage)
            } else {
                None
            };
            if let Some(neighbour) = neighbour {
                if matches!(layer_of(neighbour), Some(7) | Some(8)) {
                    neighbours.push(neighbour);
                }
            }
        }
        neighbours.sort_unstable();
        neighbours.dedup();
        if neighbours == participants {
            matching.push(*candidate);
        }
    }
    let affective_lineage = match matching.as_slice() {
        [lineage] => *lineage,
        [] => mount_next_intrinsic_in_layer(cohorts, resting_population, next_lineage_ordinal, 10)?,
        _ => return Err(FormationError::NeuronLineageAuthorityChanged),
    };
    for participant in participants {
        if !electrical_fabric.contains_contact(participant, affective_lineage) {
            *electrical_fabric = electrical_fabric
                .append_contact(
                    participant,
                    affective_lineage,
                    ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                )
                .map_err(FormationError::ResidentElectricalUnavailable)?;
        }
    }
    Ok(())
}

/// Retain one physically delayed ordering route for each active sparse bond
/// that carried a transition directly between association material and
/// retained or affective material.  A contact transition, rather than two
/// coincident post-settlement state differences, is the causal authority:
/// one-contact-per-interval propagation can lawfully change the far endpoint
/// after the near endpoint has already settled.  The participants have already
/// settled before this cell is mounted, so the new layer-11 cell cannot
/// participate until a later organism interval.  That lived interval boundary
/// is the ordering law: no timestamp, sequence label, transcript, score,
/// authored prediction or transaction-spanning history is stored here.
/// Reaching the same exact active bond reuses the same sparse route.
fn mount_reached_ordering_reach(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    active_bonds: &[StablePhysicalBondReference],
) -> Result<(), FormationError> {
    let mounted = cohorts
        .iter()
        .flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        })
        .map(|(mount, lineage)| (*lineage, mount.clone()))
        .collect::<Vec<_>>();
    let layer_by_lineage = mounted
        .iter()
        .map(|(lineage, mount)| (*lineage, mount.place().layer()))
        .collect::<std::collections::BTreeMap<_, _>>();
    let layer_of = |lineage: [u8; 16]| {
        layer_by_lineage.get(&lineage).copied()
    };
    let mut active_routes = Vec::<[[u8; 16]; 2]>::new();
    for bond in active_bonds {
        let (left, right) = bond.endpoints();
        let route = match (layer_of(left), layer_of(right)) {
            (Some(7), Some(9 | 10)) => Some([left, right]),
            (Some(9 | 10), Some(7)) => Some([right, left]),
            _ => None,
        };
        if let Some(mut route) = route {
            route.sort_unstable();
            if !active_routes.contains(&route) {
                active_routes.push(route);
            }
        }
    }
    active_routes.sort_unstable();

    // Index the exact retained neighbourhood of every already-mounted
    // ordering cell once. The former loop rescanned the complete sparse
    // fabric for every active route and every layer-11 cell even though the
    // fabric is unchanged while existing matches are identified. This map is
    // transient bookkeeping only: its key is the same exact two-lineage
    // physical participant set, and duplicate cells still fail closed.
    let ordering_candidates = mounted
        .iter()
        .filter_map(|(lineage, mount)| {
            (mount.source_site().is_none() && mount.place().layer() == 11)
                .then_some(*lineage)
        })
        .collect::<std::collections::BTreeSet<_>>();
    let mut neighbours_by_ordering = ordering_candidates
        .iter()
        .copied()
        .map(|lineage| (lineage, Vec::<[u8; 16]>::new()))
        .collect::<std::collections::BTreeMap<_, _>>();
    for (left, right) in electrical_fabric.contact_endpoints() {
        let left_lineage = electrical_fabric.lineages()[left];
        let right_lineage = electrical_fabric.lineages()[right];
        if ordering_candidates.contains(&left_lineage)
            && matches!(layer_of(right_lineage), Some(7) | Some(9) | Some(10))
        {
            neighbours_by_ordering
                .get_mut(&left_lineage)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?
                .push(right_lineage);
        }
        if ordering_candidates.contains(&right_lineage)
            && matches!(layer_of(left_lineage), Some(7) | Some(9) | Some(10))
        {
            neighbours_by_ordering
                .get_mut(&right_lineage)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?
                .push(left_lineage);
        }
    }
    let mut matching_by_participants =
        std::collections::BTreeMap::<[[u8; 16]; 2], Vec<[u8; 16]>>::new();
    for (candidate, mut neighbours) in neighbours_by_ordering {
        neighbours.sort_unstable();
        neighbours.dedup();
        if let [left, right] = neighbours.as_slice() {
            matching_by_participants
                .entry([*left, *right])
                .or_default()
                .push(candidate);
        }
    }

    for participants in active_routes {
        let matching = matching_by_participants
            .get(&participants)
            .cloned()
            .unwrap_or_default();
        let ordering_lineage = match matching.as_slice() {
            [lineage] => *lineage,
            [] => mount_next_intrinsic_in_layer(
                cohorts,
                resting_population,
                next_lineage_ordinal,
                11,
            )?,
            _ => return Err(FormationError::NeuronLineageAuthorityChanged),
        };
        for participant in participants {
            if !electrical_fabric.contains_contact(participant, ordering_lineage) {
                *electrical_fabric = electrical_fabric
                    .append_contact(
                        participant,
                        ordering_lineage,
                        ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                    )
                    .map_err(FormationError::ResidentElectricalUnavailable)?;
            }
        }
    }
    Ok(())
}

/// Materialize one motor/effector route per reached body-regulation lineage
/// when that lineage and already-existing delayed-ordering material both
/// physically change in the same organism interval.  The new layer-12 cell is
/// mounted after settlement, so it cannot move the body during the interval
/// that creates it.  Keeping each local body-regulation lineage in its own
/// motor pool preserves the receptor's explicit antagonist pairing; merging
/// several body sites would create anatomically ambiguous action.  No action
/// name, target pose, score, readiness projection, or scripted command enters
/// the neuron.  Reaching the same physical participants reuses the same route.
fn effector_terminal_paired_with_body_regulation(
    regulation: [u8; 16],
    mounted: &[([u8; 16], ReachedNeuronMount)],
    electrical_fabric: &ResidentElectricalFabric,
) -> Result<Option<BodyEffectorTerminal>, FormationError> {
    let mount_of = |lineage: [u8; 16]| {
        mounted
            .iter()
            .find(|(candidate, _)| *candidate == lineage)
            .map(|(_, mount)| mount)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)
    };
    if mount_of(regulation)?.place().layer() != 8 {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    }
    let neighbours_of = |lineage: [u8; 16]| {
        electrical_fabric
            .contact_endpoints()
            .filter_map(|(left, right)| {
                let left_lineage = electrical_fabric.lineages()[left];
                let right_lineage = electrical_fabric.lineages()[right];
                if left_lineage == lineage {
                    Some(right_lineage)
                } else if right_lineage == lineage {
                    Some(left_lineage)
                } else {
                    None
                }
            })
            .collect::<Vec<_>>()
    };
    let mut integrations = neighbours_of(regulation)
        .into_iter()
        .filter(|lineage| {
            mount_of(*lineage)
                .map(|mount| mount.place().layer() == 6)
                .unwrap_or(false)
        })
        .collect::<Vec<_>>();
    integrations.sort_unstable();
    integrations.dedup();
    let [integration] = integrations.as_slice() else {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    };
    let mut terminals = neighbours_of(*integration)
        .into_iter()
        .filter_map(|lineage| mount_of(lineage).ok()?.source_site())
        .filter_map(NeuronSourceSite::body_proprioceptor_terminal)
        .map(|terminal| terminal.paired_effector())
        .collect::<Vec<_>>();
    terminals.sort_unstable();
    terminals.dedup();
    let terminal = match terminals.as_slice() {
        [] => None,
        [terminal] => Some(*terminal),
        _ => return Err(FormationError::NeuronLineageAuthorityChanged),
    };
    Ok(terminal)
}

fn mount_reached_motor_effector(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    physically_transitioned_lineages: &[[u8; 16]],
) -> Result<(), FormationError> {
    let mounted = cohorts
        .iter()
        .flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        })
        .map(|(mount, lineage)| (*lineage, mount.clone()))
        .collect::<Vec<_>>();
    let mut body_regulation = Vec::new();
    let mut ordering = Vec::new();
    for lineage in physically_transitioned_lineages {
        let Some((_, mount)) = mounted.iter().find(|(candidate, _)| candidate == lineage) else {
            return Err(FormationError::NeuronLineageAuthorityAbsent);
        };
        match mount.place().layer() {
            8 if !body_regulation.contains(lineage) => body_regulation.push(*lineage),
            11 if !ordering.contains(lineage) => ordering.push(*lineage),
            _ => {}
        }
    }
    if body_regulation.is_empty() || ordering.is_empty() {
        return Ok(());
    }
    body_regulation.sort_unstable();
    body_regulation.dedup();
    ordering.sort_unstable();
    ordering.dedup();

    let layer_of = |lineage: [u8; 16]| {
        mounted
            .iter()
            .find(|(candidate, _)| *candidate == lineage)
            .map(|(_, mount)| mount.place().layer())
    };
    for regulation in body_regulation {
        let Some(effector_terminal) = effector_terminal_paired_with_body_regulation(
            regulation,
            &mounted,
            electrical_fabric,
        )? else {
            continue;
        };
        let mut participants = vec![regulation];
        participants.extend(ordering.iter().copied());
        participants.sort_unstable();
        participants.dedup();

        let mut matching = Vec::new();
        for (candidate, _) in mounted
            .iter()
            .filter(|(_, mount)| mount.source_site().is_none() && mount.place().layer() == 12)
        {
            let mut neighbours = Vec::new();
            for (left, right) in electrical_fabric.contact_endpoints() {
                let left_lineage = electrical_fabric.lineages()[left];
                let right_lineage = electrical_fabric.lineages()[right];
                let neighbour = if left_lineage == *candidate {
                    Some(right_lineage)
                } else if right_lineage == *candidate {
                    Some(left_lineage)
                } else {
                    None
                };
                if let Some(neighbour) = neighbour {
                    if matches!(layer_of(neighbour), Some(8) | Some(11)) {
                        neighbours.push(neighbour);
                    }
                }
            }
            neighbours.sort_unstable();
            neighbours.dedup();
            if neighbours == participants {
                matching.push(*candidate);
            }
        }
        let motor_lineage = match matching.as_slice() {
            [lineage] => *lineage,
            [] => mount_next_intrinsic_in_layer(
                cohorts,
                resting_population,
                next_lineage_ordinal,
                12,
            )?,
            _ => return Err(FormationError::NeuronLineageAuthorityChanged),
        };
        let motor_cohort = cohorts
            .iter_mut()
            .find(|cohort| {
                cohort
                    .anatomy
                    .neuron_lineages()
                    .contains(&motor_lineage)
            })
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        motor_cohort
            .anatomy
            .specialize_motor_effector(motor_lineage, effector_terminal)
            .map_err(FormationError::PhysicalSettlementUnavailable)?;
        for participant in participants {
            if !electrical_fabric.contains_contact(participant, motor_lineage) {
                *electrical_fabric = electrical_fabric
                    .append_contact(
                        participant,
                        motor_lineage,
                        ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                    )
                    .map_err(FormationError::ResidentElectricalUnavailable)?;
            }
        }
    }
    mount_reached_articulatory_effector(
        cohorts,
        resting_population,
        next_lineage_ordinal,
        electrical_fabric,
        physically_transitioned_lineages,
        &mounted,
    )?;
    Ok(())
}

/// Materialize the base articulatory route only when an acoustic receptor, body
/// regulation, delayed ordering, and an already-existing motor route all
/// physically change in the same interval. The layer-13 cell is developmental
/// articulatory anatomy, not speech or meaning. It is mounted after settlement
/// and therefore cannot emit pressure during the interval that creates it.
/// Later qualifying participants converge on the topologically first retained
/// route; sensory variation grows sparse contacts, not one new cell per
/// participant combination.
fn mount_reached_articulatory_effector(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    physically_transitioned_lineages: &[[u8; 16]],
    mounted: &[([u8; 16], ReachedNeuronMount)],
) -> Result<(), FormationError> {
    let mut acoustic = Vec::new();
    let mut body_regulation = Vec::new();
    let mut ordering = Vec::new();
    let mut motor = Vec::new();
    for lineage in physically_transitioned_lineages {
        let Some((_, mount)) = mounted.iter().find(|(candidate, _)| candidate == lineage) else {
            return Err(FormationError::NeuronLineageAuthorityAbsent);
        };
        let target = match mount.place().layer() {
            1 => &mut acoustic,
            8 => &mut body_regulation,
            11 => &mut ordering,
            12 => &mut motor,
            _ => continue,
        };
        if !target.contains(lineage) {
            target.push(*lineage);
        }
    }
    if acoustic.is_empty() || body_regulation.is_empty() || ordering.is_empty() || motor.is_empty()
    {
        return Ok(());
    }
    let mut participants = acoustic;
    participants.extend(body_regulation);
    participants.extend(ordering);
    participants.extend(motor);
    participants.sort_unstable();
    participants.dedup();

    let existing = mounted
        .iter()
        .filter(|(_, mount)| mount.source_site().is_none() && mount.place().layer() == 13)
        .min_by_key(|(_, mount)| mount.place().topology_index())
        .map(|(lineage, _)| *lineage);
    let articulatory_lineage = match existing {
        Some(lineage) => lineage,
        None => {
            mount_next_intrinsic_in_layer(cohorts, resting_population, next_lineage_ordinal, 13)?
        }
    };
    for participant in participants {
        if !electrical_fabric.contains_contact(participant, articulatory_lineage) {
            *electrical_fabric = electrical_fabric
                .append_contact(
                    participant,
                    articulatory_lineage,
                    ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                )
                .map_err(FormationError::ResidentElectricalUnavailable)?;
        }
    }
    Ok(())
}

/// Give each newly admitted retained mosaic one sparse recurrent route through
/// layer 9.  Admission has already proved the member deltas and physical bonds;
/// this function neither recognizes nor names them.  One intrinsic cell is
/// reached once and connected to the mosaic's actual member lineages.  The
/// retained mosaic remains the complete authority, so a later reassembly can
/// reach distributed members without turning this cell into a stored answer.
fn mount_new_recurrent_retention(
    cohorts: &mut Vec<ResidentReachedCohort>,
    resting_population: &mut Option<DevelopmentalRestingPopulation>,
    next_lineage_ordinal: &mut u64,
    electrical_fabric: &mut ResidentElectricalFabric,
    newly_retained_mosaic_members: &[Vec<[u8; 16]>],
) -> Result<Vec<[u8; 16]>, FormationError> {
    let resident_lineages = cohorts
        .iter()
        .flat_map(|cohort| cohort.anatomy.neuron_lineages().iter().copied())
        .collect::<Vec<_>>();
    let mut mounted_retention_lineages = Vec::new();
    mounted_retention_lineages
        .try_reserve_exact(newly_retained_mosaic_members.len())
        .map_err(|_| FormationError::ArithmeticOverflow)?;
    for members in newly_retained_mosaic_members {
        if members.len() < 3
            || members.iter().enumerate().any(|(index, lineage)| {
                !resident_lineages.contains(lineage) || members[..index].contains(lineage)
            })
        {
            return Err(FormationError::NeuronLineageAuthorityChanged);
        }
        let retention_lineage =
            mount_next_intrinsic_in_layer(cohorts, resting_population, next_lineage_ordinal, 9)?;
        for member in members {
            if !electrical_fabric.contains_contact(*member, retention_lineage) {
                *electrical_fabric = electrical_fabric
                    .append_contact(
                        *member,
                        retention_lineage,
                        ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
                    )
                    .map_err(FormationError::ResidentElectricalUnavailable)?;
            }
        }
        mounted_retention_lineages.push(retention_lineage);
    }
    Ok(mounted_retention_lineages)
}

/// Reconstruct recurrent endpoints absent from a legacy retained-mosaic body.
///
/// Layer 9 is used only for recurrent retention, and each retained formation
/// grows exactly one such cell with contacts to all of its members. Later
/// nested formations can make a local subset lookup ambiguous, so resolution
/// is global and injective: every still-unclaimed layer-9 cell that contacts a
/// retained formation participates in one complete mapping. Singleton
/// elimination accepts only the unique physical matching and fails closed if
/// no endpoint or more than one mapping remains.
fn resolve_unpersisted_recurrent_retention(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
    mosaics: &mut [RetainedOrganismMosaic],
) -> Result<(), FormationError> {
    let retained_indices = mosaics
        .iter()
        .enumerate()
        .filter(|(_, retained)| retained.mosaic.carries_only_retained_neuron_structure())
        .map(|(index, _)| index)
        .collect::<Vec<_>>();
    let mut claimed = Vec::new();
    for index in &retained_indices {
        let Some(lineage) = mosaics[*index].recurrent_lineage else {
            continue;
        };
        validate_recurrent_retention_lineage(
            cohorts,
            electrical_fabric,
            mosaics[*index].mosaic.member_lineages(),
            lineage,
        )?;
        if claimed.contains(&lineage) {
            return Err(FormationError::NeuronLineageAuthorityChanged);
        }
        claimed.push(lineage);
    }
    let unresolved = retained_indices
        .into_iter()
        .filter(|index| mosaics[*index].recurrent_lineage.is_none())
        .collect::<Vec<_>>();
    if unresolved.is_empty() {
        return Ok(());
    }
    let mut candidates = Vec::new();
    for (mount, lineage) in cohorts.iter().flat_map(|cohort| {
        cohort
            .anatomy
            .mounts()
            .iter()
            .zip(cohort.anatomy.neuron_lineages())
    }) {
        if mount.place().layer() != 9 || claimed.contains(lineage) {
            continue;
        }
        if unresolved.iter().any(|index| {
            mosaics[*index]
                .mosaic
                .member_lineages()
                .iter()
                .all(|member| electrical_fabric.contains_contact(*member, *lineage))
        }) {
            candidates.push(*lineage);
        }
    }
    candidates.sort_unstable();
    if candidates.windows(2).any(|pair| pair[0] == pair[1])
        || candidates.len() != unresolved.len()
    {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    }
    let mut remaining = unresolved;
    while !remaining.is_empty() {
        let candidate_sets = remaining
            .iter()
            .map(|index| {
                candidates
                    .iter()
                    .copied()
                    .filter(|lineage| {
                        mosaics[*index]
                            .mosaic
                            .member_lineages()
                            .iter()
                            .all(|member| {
                                electrical_fabric.contains_contact(*member, *lineage)
                            })
                    })
                    .collect::<Vec<_>>()
            })
            .collect::<Vec<_>>();
        if candidate_sets.iter().any(Vec::is_empty) {
            return Err(FormationError::NeuronLineageAuthorityAbsent);
        }
        let forced = candidate_sets
            .iter()
            .enumerate()
            .find_map(|(position, set)| (set.len() == 1).then_some((position, set[0])))
            .or_else(|| {
                candidates.iter().find_map(|lineage| {
                    let owners = candidate_sets
                        .iter()
                        .enumerate()
                        .filter(|(_, set)| set.contains(lineage))
                        .map(|(position, _)| position)
                        .collect::<Vec<_>>();
                    (owners.len() == 1).then_some((owners[0], *lineage))
                })
            });
        let Some((position, lineage)) = forced else {
            return Err(FormationError::NeuronLineageAuthorityChanged);
        };
        let mosaic_index = remaining.remove(position);
        mosaics[mosaic_index].recurrent_lineage = Some(lineage);
        let candidate_position = candidates
            .iter()
            .position(|candidate| *candidate == lineage)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        candidates.remove(candidate_position);
    }
    Ok(())
}

fn validate_recurrent_retention_lineage(
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
    members: &[[u8; 16]],
    recurrent_lineage: [u8; 16],
) -> Result<(), FormationError> {
    let mounted = cohorts
        .iter()
        .flat_map(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .zip(cohort.anatomy.neuron_lineages())
        })
        .filter(|(_, lineage)| **lineage == recurrent_lineage)
        .map(|(mount, _)| mount)
        .collect::<Vec<_>>();
    let [mount] = mounted.as_slice() else {
        return Err(if mounted.is_empty() {
            FormationError::NeuronLineageAuthorityAbsent
        } else {
            FormationError::NeuronLineageAuthorityChanged
        });
    };
    if mount.place().layer() != 9
        || !members
            .iter()
            .all(|member| electrical_fabric.contains_contact(*member, recurrent_lineage))
    {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    }
    Ok(())
}

/// Preserve the already-moving recurrent cell only when this interval has
/// physically reassembled its own retained formation through that cell.
///
/// This is deliberately narrower than generic cross-time convergence. The
/// formation must have an internally caused cue now, its exact recurrent cell
/// must have carried the immediately preceding frontier, and this same
/// interval must have settled a nonzero whole-carrier transfer between that
/// cell and one of the cue members. The transfer direction remains exact while
/// the recurrent endpoint remains the single advancing causal frontier.
fn retain_internally_reassembled_recurrent_frontier(
    next_frontier: &mut Vec<ActiveElectricalFrontierEntry>,
    predecessor_frontier: &[ActiveElectricalFrontierEntry],
    reassemblies: &[InternallyReassembledFormationCueObservation],
    settled_transfers: &[DirectedPhysicalTransferObservation],
) -> Result<(), FormationError> {
    for reassembly in reassemblies {
        let Some(recurrent_lineage) = reassembly.recurrent_lineage else {
            continue;
        };
        if !predecessor_frontier
            .iter()
            .any(|entry| entry.frontier_lineage() == recurrent_lineage)
        {
            continue;
        }
        let Some(transfer) = settled_transfers.iter().copied().find(|transfer| {
            (transfer.sender == recurrent_lineage
                && reassembly.cue_lineages.contains(&transfer.receiver))
                || (transfer.receiver == recurrent_lineage
                    && reassembly.cue_lineages.contains(&transfer.sender))
        }) else {
            continue;
        };
        next_frontier.push(ActiveElectricalFrontierEntry::caused_with_frontier(
            transfer.sender,
            transfer.receiver,
            recurrent_lineage,
            transfer.bond,
            transfer.transferred_whole_carriers,
        )?);
    }
    next_frontier.sort_unstable();
    next_frontier.dedup();
    Ok(())
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ResidentContactOrigin {
    Local {
        cohort_index: usize,
        contact_index: usize,
        left_member: usize,
        right_member: usize,
    },
    Fabric {
        contact_index: usize,
    },
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct ResidentContactTopologyEntry {
    left: usize,
    right: usize,
    stable_bond: StablePhysicalBondReference,
    origin: ResidentContactOrigin,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResidentTopologyIndex {
    flat_locations: Box<[(usize, usize, [u8; 16])]>,
    flat_by_lineage: Box<[([u8; 16], usize)]>,
    lineage_layers: Box<[([u8; 16], u32)]>,
    canonical_lineages: Box<[[u8; 16]]>,
    canonical_bonds: Box<[StablePhysicalBondReference]>,
    contacts: Box<[ResidentContactTopologyEntry]>,
    incident_contacts_by_flat: Box<[Box<[usize]>]>,
    neighbours_by_flat: Box<[Box<[usize]>]>,
    cohort_shapes: Box<[(usize, usize)]>,
    fabric_contact_count: usize,
}

impl ResidentTopologyIndex {
    fn empty() -> Self {
        Self {
            flat_locations: Box::new([]),
            flat_by_lineage: Box::new([]),
            lineage_layers: Box::new([]),
            canonical_lineages: Box::new([]),
            canonical_bonds: Box::new([]),
            contacts: Box::new([]),
            incident_contacts_by_flat: Box::new([]),
            neighbours_by_flat: Box::new([]),
            cohort_shapes: Box::new([]),
            fabric_contact_count: 0,
        }
    }

    fn build(
        cohorts: &[ResidentReachedCohort],
        electrical_fabric: &ResidentElectricalFabric,
    ) -> Result<Self, FormationError> {
        let cohort_shapes = cohorts
            .iter()
            .map(|cohort| {
                (
                    cohort.anatomy.neuron_count(),
                    cohort.anatomy.contact_count(),
                )
            })
            .collect::<Vec<_>>();
        let neuron_count = cohort_shapes.iter().try_fold(
            0usize,
            |total, (neurons, _)| total.checked_add(*neurons),
        )
        .ok_or(FormationError::ArithmeticOverflow)?;
        let contact_count = cohort_shapes
            .iter()
            .try_fold(0usize, |total, (_, contacts)| total.checked_add(*contacts))
            .and_then(|total| total.checked_add(electrical_fabric.contact_count()))
            .ok_or(FormationError::ArithmeticOverflow)?;

        let mut flat_locations = Vec::new();
        flat_locations
            .try_reserve_exact(neuron_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let mut flat_by_lineage = Vec::new();
        flat_by_lineage
            .try_reserve_exact(neuron_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let mut lineage_layers = Vec::new();
        lineage_layers
            .try_reserve_exact(neuron_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let mut cohort_offsets = Vec::new();
        cohort_offsets
            .try_reserve_exact(cohorts.len())
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        for (cohort_index, cohort) in cohorts.iter().enumerate() {
            cohort_offsets.push(flat_locations.len());
            for (neuron_index, (lineage, mount)) in cohort
                .anatomy
                .neuron_lineages()
                .iter()
                .copied()
                .zip(cohort.anatomy.mounts())
                .enumerate()
            {
                let flat = flat_locations.len();
                flat_locations.push((cohort_index, neuron_index, lineage));
                flat_by_lineage.push((lineage, flat));
                lineage_layers.push((lineage, mount.place().layer()));
            }
        }
        flat_by_lineage.sort_unstable_by_key(|(lineage, _)| *lineage);
        lineage_layers.sort_unstable_by_key(|(lineage, _)| *lineage);
        if flat_by_lineage
            .windows(2)
            .any(|pair| pair[0].0 == pair[1].0)
        {
            return Err(FormationError::NeuronLineageAuthorityChanged);
        }

        let flat_for_lineage = |lineage: [u8; 16]| {
            flat_by_lineage
                .binary_search_by_key(&lineage, |(candidate, _)| *candidate)
                .ok()
                .map(|index| flat_by_lineage[index].1)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)
        };
        let mut contacts = Vec::new();
        contacts
            .try_reserve_exact(contact_count)
            .map_err(|_| FormationError::ArithmeticOverflow)?;
        let mut parallel_ordinals =
            std::collections::BTreeMap::<([u8; 16], [u8; 16]), u32>::new();
        for (cohort_index, cohort) in cohorts.iter().enumerate() {
            let offset = cohort_offsets[cohort_index];
            for (contact_index, (left_member, right_member)) in
                cohort.anatomy.contact_endpoints().enumerate()
            {
                let left = offset
                    .checked_add(left_member)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let right = offset
                    .checked_add(right_member)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                contacts.push(ResidentContactTopologyEntry {
                    left,
                    right,
                    stable_bond: stable_bond_for_next_edge(
                        &mut parallel_ordinals,
                        flat_locations[left].2,
                        flat_locations[right].2,
                    )?,
                    origin: ResidentContactOrigin::Local {
                        cohort_index,
                        contact_index,
                        left_member,
                        right_member,
                    },
                });
            }
        }
        for (contact_index, (left_vertex, right_vertex)) in
            electrical_fabric.contact_endpoints().enumerate()
        {
            let left_lineage = *electrical_fabric
                .lineages()
                .get(left_vertex)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
            let right_lineage = *electrical_fabric
                .lineages()
                .get(right_vertex)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
            let left = flat_for_lineage(left_lineage)?;
            let right = flat_for_lineage(right_lineage)?;
            contacts.push(ResidentContactTopologyEntry {
                left,
                right,
                stable_bond: stable_bond_for_next_edge(
                    &mut parallel_ordinals,
                    left_lineage,
                    right_lineage,
                )?,
                origin: ResidentContactOrigin::Fabric { contact_index },
            });
        }

        let mut incident_contacts_by_flat = vec![Vec::<usize>::new(); neuron_count];
        let mut neighbours_by_flat = vec![Vec::<usize>::new(); neuron_count];
        for (contact_index, contact) in contacts.iter().enumerate() {
            incident_contacts_by_flat[contact.left].push(contact_index);
            incident_contacts_by_flat[contact.right].push(contact_index);
            neighbours_by_flat[contact.left].push(contact.right);
            neighbours_by_flat[contact.right].push(contact.left);
        }
        for neighbours in &mut neighbours_by_flat {
            neighbours.sort_unstable();
            neighbours.dedup();
        }
        let canonical_lineages = flat_locations
            .iter()
            .map(|(_, _, lineage)| *lineage)
            .collect::<Vec<_>>()
            .into_boxed_slice();
        let mut canonical_bonds = contacts
            .iter()
            .map(|contact| contact.stable_bond)
            .collect::<Vec<_>>();
        canonical_bonds.sort_unstable();
        Ok(Self {
            flat_locations: flat_locations.into_boxed_slice(),
            flat_by_lineage: flat_by_lineage.into_boxed_slice(),
            lineage_layers: lineage_layers.into_boxed_slice(),
            canonical_lineages,
            canonical_bonds: canonical_bonds.into_boxed_slice(),
            contacts: contacts.into_boxed_slice(),
            incident_contacts_by_flat: incident_contacts_by_flat
                .into_iter()
                .map(Vec::into_boxed_slice)
                .collect::<Vec<_>>()
                .into_boxed_slice(),
            neighbours_by_flat: neighbours_by_flat
                .into_iter()
                .map(Vec::into_boxed_slice)
                .collect::<Vec<_>>()
                .into_boxed_slice(),
            cohort_shapes: cohort_shapes.into_boxed_slice(),
            fabric_contact_count: electrical_fabric.contact_count(),
        })
    }

    fn matches_shape(
        &self,
        cohorts: &[ResidentReachedCohort],
        electrical_fabric: &ResidentElectricalFabric,
    ) -> bool {
        self.cohort_shapes.len() == cohorts.len()
            && self
                .cohort_shapes
                .iter()
                .zip(cohorts)
                .all(|((neurons, contacts), cohort)| {
                    *neurons == cohort.anatomy.neuron_count()
                        && *contacts == cohort.anatomy.contact_count()
                })
            && self.fabric_contact_count == electrical_fabric.contact_count()
    }

    fn flat_for_lineage(&self, lineage: [u8; 16]) -> Result<usize, FormationError> {
        self.flat_by_lineage
            .binary_search_by_key(&lineage, |(candidate, _)| *candidate)
            .ok()
            .map(|index| self.flat_by_lineage[index].1)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)
    }

    fn layer_of(&self, lineage: [u8; 16]) -> Option<u32> {
        self.lineage_layers
            .binary_search_by_key(&lineage, |(candidate, _)| *candidate)
            .ok()
            .map(|index| self.lineage_layers[index].1)
    }

    fn one_interval_frontier(
        &self,
        seed_lineages: &[[u8; 16]],
    ) -> Result<(Vec<usize>, Vec<usize>), FormationError> {
        let mut selected = seed_lineages
            .iter()
            .copied()
            .map(|lineage| self.flat_for_lineage(lineage))
            .collect::<Result<Vec<_>, _>>()?;
        selected.sort_unstable();
        selected.dedup();
        let seeds = selected.clone();
        for flat in seeds {
            for contact_index in self
                .incident_contacts_by_flat
                .get(flat)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?
                .iter()
                .copied()
            {
                let contact = *self
                    .contacts
                    .get(contact_index)
                    .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
                for endpoint in [contact.left, contact.right] {
                    if let Err(position) = selected.binary_search(&endpoint) {
                        selected.insert(position, endpoint);
                    }
                }
            }
        }
        let mut selected_contacts = Vec::new();
        for flat in selected.iter().copied() {
            for contact_index in self.incident_contacts_by_flat[flat].iter().copied() {
                let contact = self.contacts[contact_index];
                if selected.binary_search(&contact.left).is_err()
                    || selected.binary_search(&contact.right).is_err()
                {
                    continue;
                }
                if let Err(position) = selected_contacts.binary_search(&contact_index) {
                    selected_contacts.insert(position, contact_index);
                }
            }
        }
        Ok((selected, selected_contacts))
    }
}

struct ResidentContactEdge {
    left: usize,
    right: usize,
    anatomy: ElectricalContactAnatomy,
    state: ElectricalContactState,
    stable_bond: StablePhysicalBondReference,
    origin: ResidentContactOrigin,
}

fn materialize_resident_contact_edge(
    topology: ResidentContactTopologyEntry,
    cohorts: &[ResidentReachedCohort],
    electrical_fabric: &ResidentElectricalFabric,
) -> Result<ResidentContactEdge, FormationError> {
    let (anatomy, state) = match topology.origin {
        ResidentContactOrigin::Local {
            cohort_index,
            contact_index,
            ..
        } => {
            let cohort = cohorts
                .get(cohort_index)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
            (
                *cohort
                    .anatomy
                    .electrical_anatomy()
                    .contact_anatomies()
                    .get(contact_index)
                    .ok_or(FormationError::NeuronLineageAuthorityAbsent)?,
                cohort
                    .state
                    .electrical()
                    .contact_states()
                    .get(contact_index)
                    .cloned()
                    .ok_or(FormationError::NeuronLineageAuthorityAbsent)?,
            )
        }
        ResidentContactOrigin::Fabric { contact_index } => (
            *electrical_fabric
                .anatomy()
                .contact_anatomies()
                .get(contact_index)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?,
            electrical_fabric
                .state()
                .contact_states()
                .get(contact_index)
                .cloned()
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?,
        ),
    };
    Ok(ResidentContactEdge {
        left: topology.left,
        right: topology.right,
        anatomy,
        state,
        stable_bond: topology.stable_bond,
        origin: topology.origin,
    })
}

struct InternalContactSettlementObservation {
    dsf_delivery_count: usize,
    active_bonds: Vec<StablePhysicalBondReference>,
    changed_contact_channel_states: Vec<ChangedContactChannelStateObservation>,
    frontier_routes: Vec<PhysicalFrontierRouteObservation>,
    next_active_frontier: Vec<ActiveElectricalFrontierEntry>,
    /// Exact nonzero whole-carrier transfers settled on this interval. This
    /// transient evidence lets a formation-local recurrence retain its
    /// already-moving recurrent cell without recomputing contact settlement.
    settled_directed_transfers: Vec<DirectedPhysicalTransferObservation>,
    metabolically_perturbed_body_receptor_lineages: Vec<[u8; 16]>,
    affective_balance_trajectories: Vec<AffectiveBalanceTrajectoryObservation>,
    localized_fluid_chemistry: Vec<LocalizedFluidChemistryObservation>,
    motor_unit_recruitments: Vec<MotorUnitRecruitment>,
    articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
    emitted_neuron_fractals: Vec<EmittedNeuronFractal>,
    transition_predecessors: Vec<TransitionNeuronPredecessor>,
}

#[derive(Clone)]
struct ReachedLayerTenGradientSettlement {
    neuron_lineage: [u8; 16],
    neuron_place: DeclaredNeuronPlace,
    predecessor_separated_elementary_charges: i128,
    post_gradient_separated_elementary_charges: i128,
    metabolic: ReachedCohortMetabolicObservation,
}

fn local_gradient_direction(
    settlements: &[ReachedLayerTenGradientSettlement],
    lineage: [u8; 16],
) -> LocalGradientDirection {
    settlements
        .iter()
        .find(|settlement| settlement.neuron_lineage == lineage)
        .map_or(LocalGradientDirection::Quiescent, |settlement| {
            match (
                settlement.metabolic.pumped_elementary_charges != 0,
                settlement.metabolic.returned_elementary_charges != 0,
            ) {
                (true, false) => LocalGradientDirection::ActivePump,
                (false, true) => LocalGradientDirection::PassiveReturn,
                (false, false) | (true, true) => LocalGradientDirection::Quiescent,
            }
        })
}

#[derive(Clone)]
struct PendingLayerTenPlasticitySettlement {
    neuron_lineage: [u8; 16],
    cognitive_ordinal: u64,
    incident_catalyst_quanta: u128,
    reaction_extent: u128,
    delivered_energy_zeptojoules: ExactRational,
    predecessor_gate_work_residue_zeptojoules: ExactRational,
    successor_gate_work_residue_zeptojoules: ExactRational,
    predecessor_plastic_rest_length_nanometres: ExactRational,
    predecessor_reservoir: (ExactRational, ExactRational, ExactRational),
    successor_reservoir: (ExactRational, ExactRational, ExactRational),
}

fn stable_bond_for_next_edge(
    parallel_ordinals: &mut std::collections::BTreeMap<([u8; 16], [u8; 16]), u32>,
    first: [u8; 16],
    second: [u8; 16],
) -> Result<StablePhysicalBondReference, FormationError> {
    let canonical = if first < second {
        (first, second)
    } else {
        (second, first)
    };
    let parallel_ordinal = parallel_ordinals.get(&canonical).copied().unwrap_or(0);
    let bond = StablePhysicalBondReference::new(first, second, parallel_ordinal)
        .ok_or(FormationError::NoncanonicalState)?;
    let successor_ordinal = parallel_ordinal
        .checked_add(1)
        .ok_or(FormationError::ArithmeticOverflow)?;
    parallel_ordinals.insert(canonical, successor_ordinal);
    Ok(bond)
}

/// Advance an already-identified physical seed frontier across exactly one
/// contact boundary.  This is deliberately not a graph traversal: material
/// that reaches the far side of one contact must persist there before it can
/// become authority for another interval.
#[cfg(test)]
fn one_interval_electrical_frontier(
    seeds: &[bool],
    contact_endpoints: &[(usize, usize)],
) -> Result<Vec<bool>, FormationError> {
    let mut reached = seeds.to_vec();
    for (left, right) in contact_endpoints.iter().copied() {
        let left_seed = *seeds
            .get(left)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        let right_seed = *seeds
            .get(right)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        if left_seed || right_seed {
            reached[left] = true;
            reached[right] = true;
        }
    }
    Ok(reached)
}

fn exact_motor_body_afferent_paths(
    motor_flat: usize,
    flat_locations: &[(usize, usize, [u8; 16])],
    cohorts: &[ResidentReachedCohort],
    neighbours_by_flat: &[Box<[usize]>],
) -> Result<Vec<MotorBodyAfferentPath>, FormationError> {
    let mount_at = |flat: usize| {
        let (cohort_index, neuron_index, _) = flat_locations
            .get(flat)
            .copied()
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        cohorts
            .get(cohort_index)
            .and_then(|cohort| cohort.anatomy.mounts().get(neuron_index))
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)
    };
    if mount_at(motor_flat)?.place().layer() != 12 {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    }
    let mut paths = Vec::new();
    for regulation_flat in neighbours_by_flat
        .get(motor_flat)
        .ok_or(FormationError::NeuronLineageAuthorityAbsent)?
    {
        if mount_at(*regulation_flat)?.place().layer() != 8 {
            continue;
        }
        for integration_flat in neighbours_by_flat
            .get(*regulation_flat)
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?
        {
            if mount_at(*integration_flat)?.place().layer() != 6 {
                continue;
            }
            for receptor_flat in neighbours_by_flat
                .get(*integration_flat)
                .ok_or(FormationError::NeuronLineageAuthorityAbsent)?
            {
                let receptor_mount = mount_at(*receptor_flat)?;
                let Some(receptor_site) = receptor_mount.source_site() else {
                    continue;
                };
                if receptor_mount.place().layer() != 5 {
                    continue;
                }
                paths.push(MotorBodyAfferentPath {
                    body_regulation_lineage: flat_locations[*regulation_flat].2,
                    integration_lineage: flat_locations[*integration_flat].2,
                    receptor_lineage: flat_locations[*receptor_flat].2,
                    receptor_site: receptor_site.clone(),
                });
            }
        }
    }
    paths.sort_by(|left, right| {
        (
            left.body_regulation_lineage,
            left.integration_lineage,
            left.receptor_lineage,
            left.receptor_site.sensor_id(),
            left.receptor_site.substream_id(),
        )
            .cmp(&(
                right.body_regulation_lineage,
                right.integration_lineage,
                right.receptor_lineage,
                right.receptor_site.sensor_id(),
                right.receptor_site.substream_id(),
            ))
    });
    paths.dedup();
    Ok(paths)
}

/// Settle the bounded contact-connected frontier reached by this external
/// occurrence, form one native membrane-potential occurrence from its exact
/// predecessor/successor states, evaluate unchanged full DSF once, and let
/// every reached complete neuron settle that shared field.  Local and
/// cross-cohort contact carrier motion is computed once in one synchronous
/// generation; cohort recovery fluids remain wholly separate.
#[allow(clippy::too_many_arguments)]
fn settle_internal_contact_interval(
    cohorts: &mut [ResidentReachedCohort],
    electrical_fabric: &mut ResidentElectricalFabric,
    topology_index: &ResidentTopologyIndex,
    locally_settled_lineages: &[[u8; 16]],
    causal_seed_lineages: &[[u8; 16]],
    physically_transitioned_neuron_lineages: &mut Vec<[u8; 16]>,
    cognitive_ordinal: u64,
    unchanged_developmental_resting_neuron_count: usize,
) -> Result<InternalContactSettlementObservation, FormationError> {
    if locally_settled_lineages.is_empty() || electrical_fabric.contact_count() == 0 {
        return Ok(InternalContactSettlementObservation {
            dsf_delivery_count: 0,
            active_bonds: Vec::new(),
            changed_contact_channel_states: Vec::new(),
            frontier_routes: Vec::new(),
            next_active_frontier: Vec::new(),
            settled_directed_transfers: Vec::new(),
            metabolically_perturbed_body_receptor_lineages: Vec::new(),
            affective_balance_trajectories: Vec::new(),
            localized_fluid_chemistry: Vec::new(),
            motor_unit_recruitments: Vec::new(),
            articulatory_unit_recruitments: Vec::new(),
            emitted_neuron_fractals: Vec::new(),
            transition_predecessors: Vec::new(),
        });
    }

    if !topology_index.matches_shape(cohorts, electrical_fabric) {
        return Err(FormationError::NeuronLineageAuthorityChanged);
    }
    let flat_locations = topology_index.flat_locations.as_ref();
    let lineage_member = |lineage| topology_index.flat_for_lineage(lineage);
    let layer_of = |lineage| topology_index.layer_of(lineage);
    // One physical interval reaches only its explicitly carried causal
    // frontier and immediate electrical neighbours. Absolute nonzero
    // membrane charge is not activity: the phase-one pump gives a living
    // neuron a nonzero resting potential. Likewise a retained sub-carrier
    // contact phase is material, not proof that current moved in this
    // interval. The predecessor state carries the exact lineages whose
    // membrane/contact physics actually changed last interval, and the
    // caller combines those with this interval's external or metabolic cause.
    // This replaces the false rule that eventually made every reached neuron
    // and contact a permanent seed.
    let (selected, compact_contact_indices) =
        topology_index.one_interval_frontier(locally_settled_lineages)?;
    let mut causal_seed_flats = causal_seed_lineages
        .iter()
        .copied()
        .map(lineage_member)
        .collect::<Result<Vec<_>, _>>()?;
    causal_seed_flats.sort_unstable();
    causal_seed_flats.dedup();
    let is_causal_seed = |flat: usize| causal_seed_flats.binary_search(&flat).is_ok();

    if selected.is_empty() {
        return Ok(InternalContactSettlementObservation {
            dsf_delivery_count: 0,
            active_bonds: Vec::new(),
            changed_contact_channel_states: Vec::new(),
            frontier_routes: Vec::new(),
            next_active_frontier: Vec::new(),
            settled_directed_transfers: Vec::new(),
            metabolically_perturbed_body_receptor_lineages: Vec::new(),
            affective_balance_trajectories: Vec::new(),
            localized_fluid_chemistry: Vec::new(),
            motor_unit_recruitments: Vec::new(),
            articulatory_unit_recruitments: Vec::new(),
            emitted_neuron_fractals: Vec::new(),
            transition_predecessors: Vec::new(),
        });
    }
    let mut compact_contacts = Vec::new();
    let mut compact_states = Vec::new();
    let mut compact_origins = Vec::new();
    let mut compact_bonds = Vec::new();
    let mut compact_edge_flat_endpoints = Vec::new();
    for contact_index in compact_contact_indices {
        let edge = materialize_resident_contact_edge(
            topology_index.contacts[contact_index],
            cohorts,
            electrical_fabric,
        )?;
        let left = selected
            .binary_search(&edge.left)
            .map_err(|_| FormationError::NeuronLineageAuthorityAbsent)?;
        let right = selected
            .binary_search(&edge.right)
            .map_err(|_| FormationError::NeuronLineageAuthorityAbsent)?;
        compact_contacts.push(
            edge.anatomy
                .rebind_endpoints(left, right, selected.len())
                .map_err(FormationError::ResidentElectricalUnavailable)?,
        );
        compact_states.push(edge.state);
        compact_origins.push(edge.origin);
        compact_bonds.push(edge.stable_bond);
        compact_edge_flat_endpoints.push((edge.left, edge.right));
    }
    if compact_contacts.is_empty() {
        return Ok(InternalContactSettlementObservation {
            dsf_delivery_count: 0,
            active_bonds: Vec::new(),
            changed_contact_channel_states: Vec::new(),
            frontier_routes: Vec::new(),
            next_active_frontier: Vec::new(),
            settled_directed_transfers: Vec::new(),
            metabolically_perturbed_body_receptor_lineages: Vec::new(),
            affective_balance_trajectories: Vec::new(),
            localized_fluid_chemistry: Vec::new(),
            motor_unit_recruitments: Vec::new(),
            articulatory_unit_recruitments: Vec::new(),
            emitted_neuron_fractals: Vec::new(),
            transition_predecessors: Vec::new(),
        });
    }
    let compact_anatomy = SparseElectricalAnatomy::new(selected.len(), compact_contacts)
        .map_err(FormationError::ResidentElectricalUnavailable)?;
    let compact_predecessor =
        SparseElectricalState::from_contact_states(&compact_anatomy, compact_states)
            .map_err(FormationError::ResidentElectricalUnavailable)?;

    // Membrane pumping is local cell metabolism, not a darkness detector. Run
    // the existing exact pump only for this interval's already-derived causal
    // frontier before contact current is evaluated. This lets an intrinsic
    // neuron replenish its finite carrier gradient without polling or
    // recovering any unrelated neuron or dissipation lane.
    let selected_predecessor_neurons = cohorts
        .iter()
        .enumerate()
        .map(|(cohort_index, cohort)| {
            selected
                .iter()
                .filter_map(|flat| {
                    let (resident_cohort, neuron_index, _) = flat_locations[*flat];
                    (resident_cohort == cohort_index)
                        .then(|| (neuron_index, cohort.state.neurons()[neuron_index].clone()))
                })
                .collect::<Vec<_>>()
        })
        .collect::<Vec<_>>();
    let cohort_interval_predecessors = cohorts
        .iter()
        .map(|cohort| cohort.state.clone())
        .collect::<Vec<_>>();
    let interval_microseconds = WORLD_MECHANICAL_TICK_MICROSECONDS;
    let mut metabolically_perturbed_body_receptor_lineages = Vec::new();
    let mut reached_layer_ten_gradient_settlements = Vec::new();
    let mut localized_fluid_chemistry = Vec::new();
    for cohort_index in 0..cohorts.len() {
        let reached_indices = selected_predecessor_neurons[cohort_index]
            .iter()
            .map(|(neuron_index, _)| *neuron_index)
            .collect::<Vec<_>>();
        if reached_indices.is_empty() {
            continue;
        }
        let (successor, metabolic) = settle_reached_cohort_membrane_pumps(
            &cohorts[cohort_index].anatomy,
            &cohorts[cohort_index].state,
            &reached_indices,
            interval_microseconds,
        )
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
        if cohorts[cohort_index].anatomy.neuron_count() == 1
            && reached_indices.as_slice() == [0]
            && cohorts[cohort_index].anatomy.mounts()[0].place().layer() == 10
        {
            reached_layer_ten_gradient_settlements.push(ReachedLayerTenGradientSettlement {
                    neuron_lineage: cohorts[cohort_index].anatomy.neuron_lineages()[0],
                    neuron_place: cohorts[cohort_index].anatomy.mounts()[0].place(),
                predecessor_separated_elementary_charges: cohorts[cohort_index].state.neurons()[0]
                        .separated_elementary_charges(),
                    post_gradient_separated_elementary_charges: successor.neurons()[0]
                        .separated_elementary_charges(),
                metabolic: metabolic.clone(),
            });
        }
        for settlement in metabolic.localized_fluid_chemistry.iter().copied() {
            let LocalizedFluidChemistrySettlement {
                neuron_index,
                interval_microseconds,
                pump_contact_power_zeptojoules_per_microsecond,
                predecessor_separated_elementary_charges,
                successor_separated_elementary_charges,
                predecessor_intracellular_carriers,
                predecessor_extracellular_carriers,
                successor_intracellular_carriers,
                successor_extracellular_carriers,
                predecessor_reservoir,
                successor_reservoir,
                returned_elementary_charges,
                pumped_elementary_charges,
                membrane_gradient_work_zeptojoules,
            } = settlement;
            localized_fluid_chemistry.push(LocalizedFluidChemistryObservation {
                cognitive_ordinal,
                neuron_lineage: cohorts[cohort_index].anatomy.neuron_lineages()[neuron_index],
                neuron_place: cohorts[cohort_index].anatomy.mounts()[neuron_index].place(),
                interval_microseconds,
                pump_contact_power_zeptojoules_per_microsecond,
                reached_neuron_count: metabolic.reached_neuron_count,
                changed_reached_neuron_count: metabolic.changed_reached_neuron_count,
                unchanged_unreached_neuron_count: metabolic.unchanged_unreached_neuron_count,
                unchanged_developmental_resting_neuron_count,
                changed_unreached_neuron_count: metabolic.changed_unreached_neuron_count,
                predecessor_separated_elementary_charges,
                successor_separated_elementary_charges,
                predecessor_intracellular_carriers,
                predecessor_extracellular_carriers,
                successor_intracellular_carriers,
                successor_extracellular_carriers,
                predecessor_reservoir,
                successor_reservoir,
                returned_elementary_charges,
                pumped_elementary_charges,
                membrane_gradient_work_zeptojoules,
            });
        }
        for (neuron_index, predecessor) in &selected_predecessor_neurons[cohort_index] {
            let mount = &cohorts[cohort_index].anatomy.mounts()[*neuron_index];
            if mount.source_site().is_some()
                && mount.place().layer() == 5
                && predecessor.separated_elementary_charges()
                    != successor.neurons()[*neuron_index].separated_elementary_charges()
            {
                let lineage = cohorts[cohort_index].anatomy.neuron_lineages()[*neuron_index];
                if !metabolically_perturbed_body_receptor_lineages.contains(&lineage) {
                    metabolically_perturbed_body_receptor_lineages.push(lineage);
                }
            }
        }
        cohorts[cohort_index].state = successor.into();
    }

    // Settlement receives only the sorted reached indices and writes only
    // those indices.  Derive the untouched active count from that sparse
    // write boundary; do not rescan the organism after every interval.
    let reached_organism_neuron_count = selected.len();
    let unchanged_unreached_organism_neuron_count = flat_locations
        .len()
        .checked_sub(reached_organism_neuron_count)
        .ok_or(FormationError::ArithmeticOverflow)?;
    for settlement in &mut localized_fluid_chemistry {
        settlement.unchanged_unreached_neuron_count = unchanged_unreached_organism_neuron_count;
        settlement.changed_unreached_neuron_count = 0;
    }

    let mut capacitances = Vec::with_capacity(selected.len());
    let mut membranes = Vec::with_capacity(selected.len());
    let mut available_carriers = Vec::with_capacity(selected.len());
    let mut total_carriers = Vec::with_capacity(selected.len());
    for flat in selected.iter().copied() {
        let (cohort_index, neuron_index, _) = flat_locations[flat];
        let anatomy = &cohorts[cohort_index].anatomy.neuron_anatomies()[neuron_index];
        let state = &cohorts[cohort_index].state.neurons()[neuron_index];
        capacitances.push(anatomy.capacitance());
        membranes.push(state.membrane_state());
        available_carriers.push(state.carrier_reservoirs().intracellular());
        total_carriers.push(
            state
                .carrier_reservoirs()
                .total()
                .ok_or(FormationError::ArithmeticOverflow)?,
        );
    }
    let mut settled = settle_sparse_electrical_transfers(
        &compact_anatomy,
        &compact_predecessor,
        &capacitances,
        &membranes,
        &available_carriers,
        interval_microseconds,
    )
    .map_err(FormationError::ResidentElectricalUnavailable)?;
    let mut contact_successors = Vec::with_capacity(settled.transitions.len());
    let mut contact_transitions = Vec::with_capacity(settled.transitions.len());
    for ((contact, transition), (left_flat, right_flat)) in compact_anatomy
        .contact_anatomies()
        .iter()
        .copied()
        .zip(settled.transitions.iter().cloned())
        .zip(compact_edge_flat_endpoints.iter().copied())
    {
        let left_direction = local_gradient_direction(
            &reached_layer_ten_gradient_settlements,
            flat_locations[left_flat].2,
        );
        let right_direction = local_gradient_direction(
            &reached_layer_ten_gradient_settlements,
            flat_locations[right_flat].2,
        );
        let transition = settle_contact_local_conductance(
            contact,
            transition,
            left_direction,
            right_direction,
        )
        .map_err(FormationError::ResidentElectricalUnavailable)?;
        contact_successors.push(transition.successor.clone());
        contact_transitions.push(transition);
    }
    settled.successor_contacts = SparseElectricalState::from_contact_states(
        &compact_anatomy,
        contact_successors,
    )
    .map_err(FormationError::ResidentElectricalUnavailable)?;
    settled.transitions = contact_transitions.into_boxed_slice();

    // The compact predecessor, compact anatomy, stable bond, and settled
    // successor share one construction order. Project only the sparse reached
    // contacts whose retained channel population or transition-work phase
    // changed; do not rescan the resident organism after settlement.
    let mut changed_contact_channel_states = Vec::new();
    for (((anatomy, predecessor), transition), bond) in compact_anatomy
        .contact_anatomies()
        .iter()
        .copied()
        .zip(compact_predecessor.contact_states())
        .zip(settled.transitions.iter())
        .zip(compact_bonds.iter().copied())
    {
        let successor = &transition.successor;
        if predecessor.conducting_channel_population()
            == successor.conducting_channel_population()
            && predecessor.transition_work_phase() == successor.transition_work_phase()
        {
            continue;
        }
        changed_contact_channel_states.push(ChangedContactChannelStateObservation {
            cognitive_ordinal,
            bond,
            predecessor_conducting_channel_population: predecessor
                .conducting_channel_population(),
            predecessor_transition_work_phase: predecessor.transition_work_phase(),
            predecessor_effective_conductance_picosiemens: anatomy
                .effective_conductance(predecessor)
                .map_err(FormationError::ResidentElectricalUnavailable)?,
            successor_conducting_channel_population: successor
                .conducting_channel_population(),
            successor_transition_work_phase: successor.transition_work_phase(),
            successor_effective_conductance_picosiemens: anatomy
                .effective_conductance(successor)
                .map_err(FormationError::ResidentElectricalUnavailable)?,
        });
    }

    // Preserve exact pathway-local contact activity before the endpoint
    // consequences are applied. A layer-10 cell qualifies for local fluid
    // modulation only when this same interval physically reaches it from
    // both its association (layer 7) and body-regulation (layer 8) contacts.
    // Magnitudes are catalyst quanta; direction is preserved separately by
    // the settled transfer evidence and is not converted into valence.
    let mut layer_ten_contact_activity =
        Vec::<([u8; 16], u128, u128)>::new();
    for (transition, (left_flat, right_flat)) in settled
        .transitions
        .iter()
        .zip(compact_edge_flat_endpoints.iter().copied())
    {
        let magnitude = transition
            .outward_elementary_charges_from_left
            .unsigned_abs();
        if magnitude == 0 {
            continue;
        }
        for (candidate_flat, adjacent_flat) in
            [(left_flat, right_flat), (right_flat, left_flat)]
        {
            let candidate = flat_locations[candidate_flat].2;
            if layer_of(candidate) != Some(10) {
                continue;
            }
            let adjacent_layer = layer_of(flat_locations[adjacent_flat].2);
            if !matches!(adjacent_layer, Some(7 | 8)) {
                continue;
            }
            let index = match layer_ten_contact_activity
                .iter()
                .position(|(lineage, _, _)| *lineage == candidate)
            {
                Some(index) => index,
                None => {
                    layer_ten_contact_activity.push((candidate, 0, 0));
                    layer_ten_contact_activity.len() - 1
                }
            };
            let target = if adjacent_layer == Some(7) {
                &mut layer_ten_contact_activity[index].1
            } else {
                &mut layer_ten_contact_activity[index].2
            };
            *target = target
                .checked_add(magnitude)
                .ok_or(FormationError::ArithmeticOverflow)?;
        }
    }
    layer_ten_contact_activity.sort_unstable_by_key(|(lineage, _, _)| *lineage);

    let mut pre_field = Vec::with_capacity(selected.len());
    let mut post_field = Vec::with_capacity(selected.len());
    let mut coordinate_bounds = Vec::with_capacity(selected.len());
    let mut post_membranes = Vec::with_capacity(selected.len());
    for coordinate in 0..selected.len() {
        let transition = settle_membrane_elementary_charges(
            capacitances[coordinate],
            membranes[coordinate],
            settled.outward_elementary_charges_by_neuron[coordinate],
            interval_microseconds,
        )
        .map_err(FormationError::InternalMembraneUnavailable)?;
        let pre = exact_rational_binary64(transition.predecessor_potential_millivolts)?;
        let post = exact_rational_binary64(transition.successor_potential_millivolts)?;
        // The live membrane may already hold separated charge established by
        // its own gate paths in addition to the presently mobile contact
        // reservoir.  The internal occurrence's closed physical span must
        // therefore contain exact predecessor separation, exact successor
        // separation, and all finite carrier material that could move through
        // the reached contact.  These are the transition's own conserved
        // physical endpoints/material, not a statistical or tuned range.
        let carrier_bound = i128::try_from(total_carriers[coordinate])
            .map_err(|_| FormationError::ArithmeticOverflow)?
            .max(
                membranes[coordinate]
                    .separated_elementary_charges()
                    .unsigned_abs()
                    .try_into()
                    .map_err(|_| FormationError::ArithmeticOverflow)?,
            )
            .max(
                transition
                    .successor
                    .separated_elementary_charges()
                    .unsigned_abs()
                    .try_into()
                    .map_err(|_| FormationError::ArithmeticOverflow)?,
            );
        let positive_bound = settle_membrane_elementary_charges(
            capacitances[coordinate],
            crate::elementary_charge_membrane::ElementaryChargeMembraneState::genesis(
                carrier_bound,
            ),
            0,
            interval_microseconds,
        )
        .map_err(FormationError::InternalMembraneUnavailable)?
        .predecessor_potential_millivolts;
        let bound = exact_rational_binary64(positive_bound)?.abs();
        pre_field.push(pre);
        post_field.push(post);
        coordinate_bounds.push(
            JointUfCoordinateBounds::new(-bound, bound).map_err(|error| {
                FormationError::JointFieldUnavailable(JointNeuronBoundaryError::Source(
                    JointUfSourceError::Physics(error),
                ))
            })?,
        );
        post_membranes.push(transition.successor);
    }

    let duration = BigRational::from_integer(BigInt::from(interval_microseconds));
    let input = JointUfInput {
        times: vec![BigRational::zero(), duration.clone()],
        fields: vec![pre_field, post_field],
        relevance: vec![1.0, 1.0],
        intersample_law: JointIntersampleLaw::SampledVolumeAndRelevancePiecewiseLinear,
    };
    let bounds = JointUfPhysicalBounds::new(coordinate_bounds, duration).map_err(|error| {
        FormationError::JointFieldUnavailable(JointNeuronBoundaryError::Source(
            JointUfSourceError::Physics(error),
        ))
    })?;
    let field = joint_uf_v1_4::evaluate_with_physical_bounds(input, bounds).map_err(|error| {
        FormationError::JointFieldUnavailable(JointNeuronBoundaryError::Source(
            JointUfSourceError::Physics(error),
        ))
    })?;
    let groups = contact_components(selected.len(), &compact_anatomy);
    let source_body = Arc::<[u8]>::from(encode_internal_contact_source(
        &selected,
        &flat_locations,
        &membranes,
        &post_membranes,
        &capacitances,
        interval_microseconds,
        &compact_anatomy,
        &compact_predecessor,
    )?);
    let source_authority = sha256(&source_body);
    let shared = prepare_complete_joint_field_from_evaluated(
        source_body,
        source_authority,
        0,
        EvaluatedJointSourceOccurrence {
            port_indices: (0..selected.len()).collect(),
            groups,
            field,
        },
    )
    .map_err(FormationError::JointFieldUnavailable)?;
    if shared.result().gates.len() != 1 {
        return Err(FormationError::NoncanonicalState);
    }

    let mut local_successors = cohorts
        .iter()
        .map(|cohort| cohort.state.electrical().contact_states().to_vec())
        .collect::<Vec<_>>();
    let mut local_transitions = cohorts
        .iter()
        .map(|cohort| {
            cohort
                .state
                .electrical()
                .contact_states()
                .iter()
                .cloned()
                .map(|successor| ElectricalContactTransition {
                    successor,
                    outward_current_from_left_picoamperes: ExactRational::integer(0),
                    outward_elementary_charges_from_left: 0,
                    released_work_zeptojoules: BigRational::zero(),
                    exported_heat_zeptojoules: BigRational::zero(),
                    conductance_changed: false,
                })
                .collect::<Vec<_>>()
        })
        .collect::<Vec<_>>();
    let mut local_outward = cohorts
        .iter()
        .map(|cohort| vec![0_i128; cohort.anatomy.neuron_count()])
        .collect::<Vec<_>>();
    let mut fabric_states = electrical_fabric.state().contact_states().to_vec();
    for (origin, transition) in compact_origins
        .iter()
        .copied()
        .zip(settled.transitions.iter().cloned())
    {
        match origin {
            ResidentContactOrigin::Local {
                cohort_index,
                contact_index,
                left_member,
                right_member,
            } => {
                local_successors[cohort_index][contact_index] = transition.successor.clone();
                local_transitions[cohort_index][contact_index] = transition.clone();
                local_outward[cohort_index][left_member] = local_outward[cohort_index][left_member]
                    .checked_add(transition.outward_elementary_charges_from_left)
                    .ok_or(FormationError::ArithmeticOverflow)?;
                local_outward[cohort_index][right_member] = local_outward[cohort_index]
                    [right_member]
                    .checked_sub(transition.outward_elementary_charges_from_left)
                    .ok_or(FormationError::ArithmeticOverflow)?;
            }
            ResidentContactOrigin::Fabric { contact_index } => {
                fabric_states[contact_index] = transition.successor;
            }
        }
    }
    *electrical_fabric = electrical_fabric
        .with_contact_states(fabric_states)
        .map_err(FormationError::ResidentElectricalUnavailable)?;

    // Preserve the exact directed whole-carrier transfers from this settled
    // interval before the disjoint cohort consequences are applied. A motor
    // recruitment may use only the exact current settled across its direct
    // contact with a mounted layer-11 neighbour. The two endpoint potentials
    // jointly cause that transfer; its observed direction is never rewritten.
    let mut settled_directed_transfers = Vec::new();
    for (transition, bond) in settled.transitions.iter().zip(&compact_bonds) {
        let signed_transfer = transition.outward_elementary_charges_from_left;
        if signed_transfer == 0 {
            continue;
        }
        let (left, right) = bond.endpoints();
        let (sender, receiver) = if signed_transfer > 0 {
            (left, right)
        } else {
            (right, left)
        };
        settled_directed_transfers.push(DirectedPhysicalTransferObservation {
            sender,
            receiver,
            bond: *bond,
            transferred_whole_carriers: signed_transfer.unsigned_abs(),
        });
    }
    settled_directed_transfers.sort_unstable();
    settled_directed_transfers.dedup();

    // Local electrical settlement is wider than causal propagation: quiet
    // receptors and their adjacent cells must still relax so neuronal
    // experience can reach quiescence.  That wider settlement is not body
    // authority.  An effector may emit only when it was already this
    // interval's causal seed or when an exact whole-carrier transfer moved
    // away from a causal seed and reached it across one contact.  This keeps
    // passive balancing in a dark/silent neighbourhood from becoming motion
    // or articulation without adding a threshold, mode, or command.
    let mut causally_active_lineages = causal_seed_flats
        .iter()
        .map(|flat| flat_locations[*flat].2)
        .collect::<Vec<_>>();
    for (transition, (left_flat, right_flat)) in settled
        .transitions
        .iter()
        .zip(compact_edge_flat_endpoints.iter().copied())
    {
        let signed_transfer = transition.outward_elementary_charges_from_left;
        let reached_flat = if signed_transfer > 0 && is_causal_seed(left_flat) {
            Some(right_flat)
        } else if signed_transfer < 0 && is_causal_seed(right_flat) {
            Some(left_flat)
        } else {
            None
        };
        if let Some(reached_flat) = reached_flat {
            let lineage = flat_locations[reached_flat].2;
            if !causally_active_lineages.contains(&lineage) {
                causally_active_lineages.push(lineage);
            }
        }
    }
    causally_active_lineages.sort_unstable();
    causally_active_lineages.dedup();

    // The shared contact field and carrier transfers above are settled once.
    // Each cohort then owns a disjoint anatomy, state and recovery reservoir,
    // so those local consequences can settle concurrently without changing
    // causal order or allowing one cohort to observe another's mutation.
    // Indexed collection preserves cohort order for the evidence merge below.
    let cohort_results = cohorts
        .par_iter_mut()
        .enumerate()
        .map(
            |(cohort_index, cohort)| -> Result<
            Option<(
                Vec<TransitionNeuronPredecessor>,
                Vec<MotorUnitRecruitment>,
                Vec<ArticulatoryUnitRecruitment>,
                Vec<EmittedNeuronFractal>,
                Vec<PendingLayerTenPlasticitySettlement>,
            )>,
            FormationError,
        > {
        let selected_members = selected
            .iter()
            .enumerate()
            .filter_map(|(coordinate, flat)| {
                let (resident_cohort, neuron_index, _) = flat_locations[*flat];
                (resident_cohort == cohort_index).then_some((coordinate, neuron_index))
            })
            .collect::<Vec<_>>();
        if selected_members.is_empty() {
            return Ok(None);
        }
        let mut required_positions = cohort
            .anatomy
            .neuron_anatomies()
            .iter()
            .map(|anatomy| anatomy.mathloom_positions())
            .collect::<Vec<_>>();
        for (coordinate, neuron_index) in selected_members.iter().copied() {
            let perspective = bind_neuron_perspective(&shared, coordinate, 0)
                .map_err(FormationError::JointFieldUnavailable)?;
            required_positions[neuron_index] = required_positions[neuron_index].max(
                required_mathloom_positions(perspective)
                    .map_err(FormationError::JointFieldUnavailable)?,
            );
        }
        let comparison_predecessors = selected_predecessor_neurons[cohort_index]
            .iter()
            .map(|(neuron_index, predecessor)| {
                        let (extended_anatomy, extended_predecessor) =
                            extend_neuron_positional_fabric(
                    &cohort.anatomy.neuron_anatomies()[*neuron_index],
                    predecessor,
                    required_positions[*neuron_index],
                )
                .map_err(|error| {
                                FormationError::PhysicalSettlementUnavailable(
                                    ReachedCohortError::Neuron {
                        neuron_index: *neuron_index,
                        error,
                                    },
                                )
                })?;
                Ok((*neuron_index, extended_anatomy, extended_predecessor))
            })
            .collect::<Result<Vec<_>, FormationError>>()?;
        let predecessor_anatomy = cohort.anatomy.clone();
        let (extended_predecessor_anatomy, interval_predecessor_state) =
            extend_reached_cohort_positional_fabrics(
                &predecessor_anatomy,
                &cohort_interval_predecessors[cohort_index],
                &required_positions,
            )
            .map_err(FormationError::PhysicalSettlementUnavailable)?;
        let interval_predecessor_state = Arc::new(interval_predecessor_state);
        extend_resident_cohort_positional_fabrics(cohort, &required_positions)?;
        if extended_predecessor_anatomy != cohort.anatomy {
            return Err(FormationError::NoncanonicalState);
        }
        for (neuron_index, extended_anatomy, _) in &comparison_predecessors {
            if extended_anatomy != &cohort.anatomy.neuron_anatomies()[*neuron_index] {
                return Err(FormationError::NoncanonicalState);
            }
        }
        let catalysts = selected_members
            .iter()
            .map(|(_, neuron_index)| {
                vec![
                    0;
                    cohort.anatomy.neuron_anatomies()[*neuron_index]
                        .recovery_anatomy()
                        .psi_lane_count()
                ]
                .into_boxed_slice()
            })
            .collect::<Vec<Box<[u128]>>>();
        let resident_indices = selected_members
            .iter()
            .map(|(_, neuron_index)| *neuron_index)
            .collect::<Vec<_>>();
        let combined_outward = selected_members
            .iter()
                    .map(|(coordinate, _)| {
                        settled.outward_elementary_charges_by_neuron[*coordinate]
                    })
            .collect::<Vec<_>>();
        let mut settlement_predecessor = cohort.state.clone();
        let mut inputs = Vec::with_capacity(selected_members.len());
        let mut pending_layer_ten_plasticity = Vec::new();
        for (reached_input_index, (coordinate, neuron_index)) in
            selected_members.iter().copied().enumerate()
        {
            let perspective = bind_neuron_perspective(&shared, coordinate, 0)
                .map_err(FormationError::JointFieldUnavailable)?;
            let prepared_psi = cohort.anatomy.neuron_anatomies()[neuron_index]
                .prepare_psi_settlement(
                    &settlement_predecessor.neurons()[neuron_index],
                    perspective,
                )
                .map_err(|error| {
                    FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                        neuron_index,
                        error,
                    })
                })?;
            let lineage = cohort.anatomy.neuron_lineages()[neuron_index];
            let convergent_activity = match layer_ten_contact_activity
                .binary_search_by_key(&lineage, |(candidate, _, _)| *candidate)
            {
                Ok(index) => {
                    let (_, association, body) = layer_ten_contact_activity[index];
                    if association != 0 && body != 0 {
                        Some(
                            association
                                .checked_add(body)
                                .ok_or(FormationError::ArithmeticOverflow)?,
                        )
                    } else {
                        None
                    }
                }
                Err(_) => None,
            };
            let gradient_changed = reached_layer_ten_gradient_settlements.iter().any(
                |gradient| gradient.neuron_lineage == lineage && gradient.metabolic.changed(),
            );
            let (gate_work, receptor_successor_residue) = if cohort
                .anatomy
                .mounts()[neuron_index]
                .place()
                .layer()
                == 10
                && gradient_changed
                && convergent_activity.is_some()
            {
                let predecessor_neuron = &settlement_predecessor.neurons()[neuron_index];
                let incident_catalyst_quanta = convergent_activity
                    .ok_or(FormationError::ArithmeticOverflow)?;
                let energetic = settle_contact_modulated_gate_energy(
                    &cohort.anatomy,
                    &settlement_predecessor,
                    neuron_index,
                    incident_catalyst_quanta,
                )
                .map_err(FormationError::PhysicalSettlementUnavailable)?;
                let window = gate_opening_quantum_window_with_psi(
                    &cohort.anatomy.neuron_anatomies()[neuron_index],
                    predecessor_neuron,
                    &prepared_psi,
                )
                .map_err(|error| {
                    FormationError::PhysicalSettlementUnavailable(ReachedCohortError::Neuron {
                        neuron_index,
                        error,
                    })
                })?;
                let delivery = quantize_receptor_delivery(
                    &exact_rational_to_big(energetic.delivered_energy_zeptojoules),
                    predecessor_neuron.receptor_quantum_residue,
                    cohort.anatomy.neuron_anatomies()[neuron_index]
                        .gate_dissipation_quantum_zeptojoules(),
                    window.opening_threshold_quanta,
                    window.window_cap_quanta,
                )
                .map_err(FormationError::LocalGateWorkUnavailable)?;
                pending_layer_ten_plasticity.push(PendingLayerTenPlasticitySettlement {
                    neuron_lineage: lineage,
                    cognitive_ordinal,
                    incident_catalyst_quanta: energetic.incident_catalyst_quanta,
                    reaction_extent: energetic.reaction_extent,
                    delivered_energy_zeptojoules: energetic.delivered_energy_zeptojoules,
                    predecessor_gate_work_residue_zeptojoules: predecessor_neuron
                        .receptor_quantum_residue,
                    successor_gate_work_residue_zeptojoules: delivery.successor_residue,
                    predecessor_plastic_rest_length_nanometres: predecessor_neuron
                        .plastic
                        .rest_length_nanometres(),
                    predecessor_reservoir: energetic.predecessor_reservoir,
                    successor_reservoir: energetic.successor_reservoir,
                });
                settlement_predecessor = energetic.successor.into();
                (delivery.gate_work, Some(delivery.successor_residue))
            } else {
                (GateWorkOccurrence::new(BigRational::zero()), None)
            };
            inputs.push(NeuronIntervalInput {
                perspective,
                gate_work,
                interval_microseconds,
                recovery: RecoveryContact::new(&catalysts[reached_input_index], 0, 0),
                dna_expression: DnaExpressionContact::new(0),
                receptor_successor_residue,
                prepared_psi: Some(prepared_psi),
            });
        }
        // A layer-12 motor cell emits through its exact outward membrane
        // carrier discharge. Gate conformation is upstream channel anatomy;
        // requiring a newly opened local gate made an already-conducting
        // motor cell physically move charge while emitting no efferent event.
        // Only positive whole-carrier discharge reaches the actuator. Reverse
        // flow is membrane recovery, and sub-carrier phase remains retained in
        // the contact rather than being promoted into a body command.
        let motor_unit_recruitments = selected_members
            .iter()
            .zip(combined_outward.iter().copied())
            .filter_map(|((_, neuron_index), outward)| {
                let mount = &cohort.anatomy.mounts()[*neuron_index];
                let body_effector_terminal = mount.body_effector_terminal()?;
                let motor_lineage = cohort.anatomy.neuron_lineages()[*neuron_index];
                let mut preparation_transfers = settled_directed_transfers
                    .iter()
                    .copied()
                    .filter(|transfer| {
                        (transfer.receiver == motor_lineage
                            && layer_of(transfer.sender) == Some(11))
                            || (transfer.sender == motor_lineage
                                && layer_of(transfer.receiver) == Some(11))
                    })
                    .collect::<Vec<_>>();
                preparation_transfers.sort_unstable();
                preparation_transfers.dedup();
                (mount.source_site().is_none()
                    && mount.place().layer() == 12
                    && causally_active_lineages.contains(&motor_lineage)
                    && outward > 0
                    && !preparation_transfers.is_empty())
                    .then_some(MotorUnitRecruitment {
                        neuron_lineage: cohort.anatomy.neuron_lineages()[*neuron_index],
                        topology_index: mount.place().topology_index(),
                        outward_elementary_carriers: outward.unsigned_abs(),
                        body_effector_terminal,
                        body_afferent_paths: Vec::new(),
                        preparation_transfers,
                    })
            })
            .collect::<Vec<_>>();
        let articulatory_unit_recruitments = selected_members
            .iter()
            .zip(combined_outward.iter().copied())
            .filter_map(|((_, neuron_index), outward)| {
                let mount = &cohort.anatomy.mounts()[*neuron_index];
                let articulatory_lineage = cohort.anatomy.neuron_lineages()[*neuron_index];
                let mut motor_transfers = settled_directed_transfers
                    .iter()
                    .copied()
                    .filter(|transfer| {
                        (transfer.receiver == articulatory_lineage
                            && layer_of(transfer.sender) == Some(12))
                            || (transfer.sender == articulatory_lineage
                                && layer_of(transfer.receiver) == Some(12))
                    })
                    .collect::<Vec<_>>();
                motor_transfers.sort_unstable();
                motor_transfers.dedup();
                (mount.source_site().is_none()
                    && mount.place().layer() == 13
                    && causally_active_lineages.contains(&articulatory_lineage)
                    && outward > 0
                    && !motor_transfers.is_empty())
                    .then_some(ArticulatoryUnitRecruitment {
                        neuron_lineage: articulatory_lineage,
                        topology_index: mount.place().topology_index(),
                        outward_elementary_carriers: outward.unsigned_abs(),
                        motor_transfers,
                    })
            })
            .collect::<Vec<_>>();
        let local_successor = SparseElectricalState::from_contact_states(
            cohort.anatomy.electrical_anatomy(),
            local_successors[cohort_index].clone(),
        )
        .map_err(FormationError::ResidentElectricalUnavailable)?;
        let precomputed_local = SparseElectricalTransferSettlement {
            successor_contacts: local_successor,
            transitions: local_transitions[cohort_index].clone().into_boxed_slice(),
            outward_elementary_charges_by_neuron: local_outward[cohort_index]
                .clone()
                .into_boxed_slice(),
        };
                let input =
                    ReachedCohortIntervalInput::from_resident_indices_with_precomputed_contacts(
            inputs,
            resident_indices,
            combined_outward,
            precomputed_local,
        )
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
        let predecessor_neurons = &comparison_predecessors;
        // This interval is a native cross-cohort electrical consequence, not
        // a second externally admitted experience. Its retained changes join
        // the same pending local physical experience and may emit only after
        // a later exact neuron-local quiescent interval. Cross-cohort current
        // therefore cannot bypass the post-quiescence fractal law.
                let settlement =
                    settle_reached_cohort_interval(
                        &cohort.anatomy,
                        &settlement_predecessor,
                        input,
                    )
        .map_err(FormationError::PhysicalSettlementUnavailable)?;
        let settlement_successor = Arc::new(settlement.successor);
        let retained_change_this_interval = interval_predecessor_state
            .neurons()
            .iter()
            .zip(settlement_successor.neurons())
            .enumerate()
            .map(|(neuron_index, (predecessor, successor))| {
                sparse_retained_physical_state_delta(predecessor, successor)
                    .map(|delta| delta.is_some())
                    .map_err(|error| {
                        FormationError::PhysicalSettlementUnavailable(
                            ReachedCohortError::Neuron {
                                neuron_index,
                                error,
                            },
                        )
                    })
            })
            .collect::<Result<Vec<_>, _>>()?;
                let active_electrical_contacts =
                    active_contact_bits(&settlement.contact_transitions);
        let mut cohort_fractals = Vec::new();
        if cohort.retained_experience.is_none() {
            let experience_preceded_interval = cohort.pending_experience.is_some();
            let mut experience = cohort.pending_experience.take();
            if experience.is_none()
                && retained_change_this_interval
                    .iter()
                    .any(|changed| *changed)
            {
                experience = Some(ResidentExperienceEvidence {
                    codec: ExperienceEvidenceCodec::V7,
                    physical: ResidentExperiencePhysicalEvidence::Pending(Box::new([])),
                    gate_work_perturbed_neurons: SparseResidentNeuronMask::empty(),
                    receptor_excitation_zeptojoules: vec![
                        None;
                        cohort.anatomy.neuron_count()
                    ]
                    .into_boxed_slice(),
                    retained_change_neurons: vec![false; cohort.anatomy.neuron_count()]
                        .into_boxed_slice(),
                    retentively_settled_neurons: vec![false; cohort.anatomy.neuron_count()]
                        .into_boxed_slice(),
                    active_electrical_contacts: vec![false; cohort.anatomy.contact_count()]
                        .into_boxed_slice(),
                    local_relaxation_observed: false,
                });
            }
            if let Some(evidence) = experience.as_mut() {
                evidence.codec = ExperienceEvidenceCodec::V7;
                merge_pending_experience_members(
                    evidence,
                    &interval_predecessor_state,
                    &retained_change_this_interval,
                )?;
                or_bits(
                    &mut evidence.retained_change_neurons,
                    &retained_change_this_interval,
                )?;
                or_bits(
                    &mut evidence.active_electrical_contacts,
                    &active_electrical_contacts,
                )?;
                if experience_preceded_interval {
                    cohort_fractals.extend(emit_newly_quiescent_neuron_fractals(
                        &cohort.anatomy,
                        evidence,
                        &settlement_successor,
                        &retained_change_this_interval,
                    )?);
                }
            }
            cohort.pending_experience = experience;
        } else {
            let no_gate_work = vec![false; cohort.anatomy.neuron_count()];
            let no_receptor_excitation = vec![None; cohort.anatomy.neuron_count()];
            cohort_fractals.extend(advance_recurrent_neuronal_experience(
                &cohort.anatomy,
                &mut cohort.pending_experience,
                &interval_predecessor_state,
                &settlement_successor,
                &retained_change_this_interval,
                &no_gate_work,
                &no_receptor_excitation,
                &active_electrical_contacts,
            )?);
        }
        cohort.state = settlement_successor;
                let mut changed_predecessors = Vec::new();
                for (neuron_index, predecessor_anatomy, predecessor) in predecessor_neurons {
            let successor = &cohort.state.neurons()[*neuron_index];
            if predecessor != successor {
                        changed_predecessors.push(TransitionNeuronPredecessor {
                            lineage: cohort.anatomy.neuron_lineages()[*neuron_index],
                            anatomy: predecessor_anatomy.clone(),
                            state: predecessor.clone(),
                        });
            }
        }
        Ok(Some((
            changed_predecessors,
            motor_unit_recruitments,
            articulatory_unit_recruitments,
            cohort_fractals,
            pending_layer_ten_plasticity,
        )))
            },
        )
    .collect::<Vec<_>>();
    let mut motor_unit_recruitments = Vec::new();
    let mut articulatory_unit_recruitments = Vec::new();
    let mut emitted_neuron_fractals = Vec::new();
    let mut transition_predecessors = Vec::new();
    let mut layer_ten_plasticity_settlements = Vec::new();
    for result in cohort_results {
        if let Some((
            changed_predecessors,
            cohort_motor_recruitments,
            cohort_articulatory_recruitments,
            cohort_fractals,
            cohort_layer_ten_plasticity,
        )) = result?
        {
            for predecessor in changed_predecessors {
                let lineage = predecessor.lineage;
                if !physically_transitioned_neuron_lineages.contains(&lineage) {
                    physically_transitioned_neuron_lineages.push(lineage);
                }
                retain_first_transition_predecessor(&mut transition_predecessors, predecessor);
            }
            motor_unit_recruitments.extend(cohort_motor_recruitments);
            articulatory_unit_recruitments.extend(cohort_articulatory_recruitments);
            emitted_neuron_fractals.extend(cohort_fractals);
            layer_ten_plasticity_settlements.extend(cohort_layer_ten_plasticity);
        }
    }
    if !motor_unit_recruitments.is_empty() {
        for recruitment in &mut motor_unit_recruitments {
            let motor_flat = lineage_member(recruitment.neuron_lineage)?;
            let paths = exact_motor_body_afferent_paths(
                motor_flat,
                flat_locations,
                cohorts,
                &topology_index.neighbours_by_flat,
            )?;
            if paths.is_empty() {
                return Err(FormationError::NeuronLineageAuthorityChanged);
            }
            recruitment.body_afferent_paths = paths;
        }
    }
    let mut affective_balance_trajectories = Vec::new();
    for gradient in reached_layer_ten_gradient_settlements {
        let interval_successor_separated_elementary_charges = flat_locations
            .iter()
            .find(|(_, _, lineage)| *lineage == gradient.neuron_lineage)
            .map(|(cohort_index, neuron_index, _)| {
                cohorts[*cohort_index].state.neurons()[*neuron_index].separated_elementary_charges()
            })
            .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
        let mut association_influences = Vec::new();
        let mut body_influences = Vec::new();
        for ((transition, bond), (left_flat, right_flat)) in settled
            .transitions
            .iter()
            .zip(compact_bonds.iter().copied())
            .zip(compact_edge_flat_endpoints.iter().copied())
        {
            let signed = transition.outward_elementary_charges_from_left;
            if signed == 0 {
                continue;
            }
            let (sender_flat, receiver_flat) = if signed > 0 {
                (left_flat, right_flat)
            } else {
                (right_flat, left_flat)
            };
            let (sender_cohort, sender_neuron, sender) = flat_locations[sender_flat];
            let (receiver_cohort, receiver_neuron, receiver) = flat_locations[receiver_flat];
            if sender != gradient.neuron_lineage && receiver != gradient.neuron_lineage {
                continue;
            }
            let adjacent_layer = if sender == gradient.neuron_lineage {
                cohorts[receiver_cohort].anatomy.mounts()[receiver_neuron]
                    .place()
                    .layer()
            } else {
                cohorts[sender_cohort].anatomy.mounts()[sender_neuron]
                    .place()
                    .layer()
            };
            let timed = TimedDirectedPhysicalTransferObservation {
                cognitive_ordinal,
                transfer: DirectedPhysicalTransferObservation {
                    sender,
                    receiver,
                    bond,
                    transferred_whole_carriers: signed.unsigned_abs(),
                },
            };
            match adjacent_layer {
                7 => association_influences.push(timed),
                8 => body_influences.push(timed),
                _ => {}
            }
        }
        association_influences.sort_unstable();
        body_influences.sort_unstable();
        let localized_plasticity_settlement = layer_ten_plasticity_settlements
            .iter()
            .find(|settlement| settlement.neuron_lineage == gradient.neuron_lineage)
            .map(|settlement| {
                let successor_plastic_rest_length_nanometres = flat_locations
                    .iter()
                    .find(|(_, _, lineage)| *lineage == settlement.neuron_lineage)
                    .map(|(cohort_index, neuron_index, _)| {
                        cohorts[*cohort_index].state.neurons()[*neuron_index]
                            .plastic
                            .rest_length_nanometres()
                    })
                    .ok_or(FormationError::NeuronLineageAuthorityAbsent)?;
                Ok(LocalAffectivePlasticitySettlementObservation {
                    cognitive_ordinal: settlement.cognitive_ordinal,
                    incident_catalyst_quanta: settlement.incident_catalyst_quanta,
                    reaction_extent: settlement.reaction_extent,
                    delivered_energy_zeptojoules: settlement.delivered_energy_zeptojoules,
                    predecessor_gate_work_residue_zeptojoules: settlement
                        .predecessor_gate_work_residue_zeptojoules,
                    successor_gate_work_residue_zeptojoules: settlement
                        .successor_gate_work_residue_zeptojoules,
                    predecessor_plastic_rest_length_nanometres: settlement
                        .predecessor_plastic_rest_length_nanometres,
                    successor_plastic_rest_length_nanometres,
                    predecessor_reservoir: settlement.predecessor_reservoir,
                    successor_reservoir: settlement.successor_reservoir,
                })
            })
            .transpose()?;
        affective_balance_trajectories.push(AffectiveBalanceTrajectoryObservation {
            neuron_lineage: gradient.neuron_lineage,
            neuron_place: gradient.neuron_place,
            association_influence: association_influences.first().copied(),
            body_influence: body_influences.first().copied(),
            localized_gradient_settlement: gradient.metabolic.changed().then_some(
                LocalAffectiveGradientSettlementObservation {
                    cognitive_ordinal,
                    predecessor_separated_elementary_charges: gradient
                        .predecessor_separated_elementary_charges,
                    post_gradient_separated_elementary_charges: gradient
                        .post_gradient_separated_elementary_charges,
                    interval_successor_separated_elementary_charges,
                    returned_elementary_charges: gradient.metabolic.returned_elementary_charges,
                    pumped_elementary_charges: gradient.metabolic.pumped_elementary_charges,
                    unreturned_elementary_charges: gradient.metabolic.unreturned_elementary_charges,
                    membrane_gradient_work_zeptojoules: gradient
                        .metabolic
                        .membrane_gradient_work_zeptojoules,
                    environment_energy_delivered_zeptojoules: gradient
                        .metabolic
                        .environment_energy_delivered_zeptojoules,
                    environment_heat_exported_zeptojoules: gradient
                        .metabolic
                        .environment_heat_exported_zeptojoules,
                },
            ),
            localized_plasticity_settlement,
        });
    }
    affective_balance_trajectories.sort_unstable_by_key(|entry| entry.neuron_lineage);
    localized_fluid_chemistry.sort_unstable_by_key(|entry| entry.neuron_lineage);
    if localized_fluid_chemistry.len() > 1 {
        let selected = localized_fluid_chemistry
            .iter()
            .find(|entry| {
                entry.unchanged_unreached_neuron_count != 0
                    || entry.unchanged_developmental_resting_neuron_count != 0
            })
            .or_else(|| localized_fluid_chemistry.first())
            .copied();
        localized_fluid_chemistry.clear();
        if let Some(selected) = selected {
            localized_fluid_chemistry.push(selected);
        }
    }
    let mut active_bonds = settled
        .transitions
        .iter()
        .zip(compact_bonds.iter().copied())
        .filter_map(|(transition, bond)| {
            (transition.outward_current_from_left_picoamperes.parts().0 != 0
                || transition.outward_elementary_charges_from_left != 0
                || transition.conductance_changed)
                .then_some(bond)
        })
        .collect::<Vec<_>>();
    active_bonds.sort_unstable();
    active_bonds.dedup();
    let mut frontier_routes = Vec::new();
    for ((transition, bond), (left_flat, right_flat)) in settled
        .transitions
        .iter()
        .zip(compact_bonds.iter().copied())
        .zip(compact_edge_flat_endpoints.iter().copied())
    {
        let left_seed = is_causal_seed(left_flat);
        let right_seed = is_causal_seed(right_flat);
        if left_seed == right_seed {
            continue;
        }
        let signed_from_left = transition.outward_elementary_charges_from_left;
        let (seed_flat, adjacent_flat, outward_whole_carriers_from_seed) = if left_seed {
            (left_flat, right_flat, signed_from_left)
        } else {
            (
                right_flat,
                left_flat,
                signed_from_left
                    .checked_neg()
                    .ok_or(FormationError::ArithmeticOverflow)?,
            )
        };
        let (seed_cohort, seed_neuron, seed_lineage) = flat_locations[seed_flat];
        let (adjacent_cohort, adjacent_neuron, adjacent_lineage) = flat_locations[adjacent_flat];
        frontier_routes.push(PhysicalFrontierRouteObservation {
            seed_lineage,
            seed_place: cohorts[seed_cohort].anatomy.mounts()[seed_neuron].place(),
            adjacent_lineage,
            adjacent_place: cohorts[adjacent_cohort].anatomy.mounts()[adjacent_neuron].place(),
            bond,
            outward_whole_carriers_from_seed,
        });
    }
    frontier_routes.sort_unstable_by_key(|route| {
        (
            route.seed_lineage,
            route.adjacent_lineage,
            route.bond.parallel_ordinal(),
        )
    });
    frontier_routes.dedup();
    // A nonzero whole-carrier transfer across the current causal boundary
    // changes both endpoint states, but only the previously unseeded endpoint
    // advances the one-contact causal wave. Preserve carrier direction and
    // advancing endpoint separately: current may physically flow into the
    // seed while the seed's changed potential causally reaches the supplying
    // neighbour. Carrying both endpoints would turn the already-reached
    // interior into a permanent seed and eventually poll the complete fabric.
    // Contacts with both or neither endpoint seeded therefore do not advance
    // this boundary; they remain ordinary local electrical settlement.
    let mut next_active_frontier = Vec::new();
    for ((transition, bond), (left_flat, right_flat)) in settled
        .transitions
        .iter()
        .zip(&compact_bonds)
        .zip(compact_edge_flat_endpoints.iter().copied())
    {
        let signed_transfer = transition.outward_elementary_charges_from_left;
        if signed_transfer == 0 {
            continue;
        }
        let (left, right) = bond.endpoints();
        let (sending_lineage, receiving_lineage) = if signed_transfer > 0 {
            (left, right)
        } else {
            (right, left)
        };
        if is_causal_seed(left_flat) != is_causal_seed(right_flat) {
            let frontier_lineage = if is_causal_seed(left_flat) {
                right
            } else {
                left
            };
            next_active_frontier.push(ActiveElectricalFrontierEntry::caused_with_frontier(
                sending_lineage,
                receiving_lineage,
                frontier_lineage,
                *bond,
                signed_transfer.unsigned_abs(),
            )?);
        }
    }
    next_active_frontier.sort_unstable();
    next_active_frontier.dedup();
    // One shared full-field occurrence was evaluated for the entire reached
    // contact frontier, irrespective of how many neurons received their
    // coordinate-local perspectives.
    Ok(InternalContactSettlementObservation {
        dsf_delivery_count: 1,
        active_bonds,
        changed_contact_channel_states,
        frontier_routes,
        next_active_frontier,
        settled_directed_transfers,
        metabolically_perturbed_body_receptor_lineages,
        affective_balance_trajectories,
        localized_fluid_chemistry,
        motor_unit_recruitments,
        articulatory_unit_recruitments,
        emitted_neuron_fractals,
        transition_predecessors,
    })
}

fn exact_rational_binary64(value: ExactRational) -> Result<f64, FormationError> {
    let (numerator, denominator) = value.parts();
    let numerator = numerator
        .to_f64()
        .filter(|value| value.is_finite())
        .ok_or(FormationError::ArithmeticOverflow)?;
    let denominator = denominator
        .to_f64()
        .filter(|value| value.is_finite() && *value > 0.0)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let value = numerator / denominator;
    value
        .is_finite()
        .then_some(value)
        .ok_or(FormationError::ArithmeticOverflow)
}

fn contact_components(neuron_count: usize, anatomy: &SparseElectricalAnatomy) -> Vec<Vec<usize>> {
    let mut visited = vec![false; neuron_count];
    let endpoints = anatomy.contact_endpoints().collect::<Vec<_>>();
    let mut groups = Vec::new();
    for start in 0..neuron_count {
        if visited[start] {
            continue;
        }
        visited[start] = true;
        let mut group = vec![start];
        let mut cursor = 0usize;
        while cursor < group.len() {
            let member = group[cursor];
            for (left, right) in &endpoints {
                let neighbour = if *left == member {
                    Some(*right)
                } else if *right == member {
                    Some(*left)
                } else {
                    None
                };
                if let Some(neighbour) = neighbour {
                    if !visited[neighbour] {
                        visited[neighbour] = true;
                        group.push(neighbour);
                    }
                }
            }
            cursor += 1;
        }
        groups.push(group);
    }
    groups
}

fn encode_internal_contact_source(
    selected: &[usize],
    flat_locations: &[(usize, usize, [u8; 16])],
    predecessor_membranes: &[crate::elementary_charge_membrane::ElementaryChargeMembraneState],
    successor_membranes: &[crate::elementary_charge_membrane::ElementaryChargeMembraneState],
    capacitances: &[crate::elementary_charge_membrane::MembraneCapacitance],
    interval_microseconds: u32,
    electrical: &SparseElectricalAnatomy,
    electrical_state: &SparseElectricalState,
) -> Result<Vec<u8>, FormationError> {
    if electrical.contact_count() != electrical_state.contact_count() {
        return Err(FormationError::NoncanonicalState);
    }
    let mut encoded = Vec::new();
    encoded.extend_from_slice(b"GLINT02\0");
    encoded.extend_from_slice(&interval_microseconds.to_le_bytes());
    push_length(&mut encoded, selected.len())?;
    for (coordinate, flat) in selected.iter().copied().enumerate() {
        encoded.extend_from_slice(&flat_locations[flat].2);
        encoded.extend_from_slice(
            &predecessor_membranes[coordinate]
                .separated_elementary_charges()
                .to_le_bytes(),
        );
        encoded.extend_from_slice(
            &successor_membranes[coordinate]
                .separated_elementary_charges()
                .to_le_bytes(),
        );
        let (numerator, denominator) = capacitances[coordinate].picofarads().parts();
        encoded.extend_from_slice(&numerator.to_le_bytes());
        encoded.extend_from_slice(&denominator.to_le_bytes());
    }
    push_length(&mut encoded, electrical.contact_count())?;
    for (contact, state) in electrical
        .contact_anatomies()
        .iter()
        .zip(electrical_state.contact_states())
    {
        let (left, right) = contact.endpoints();
        push_length(&mut encoded, left)?;
        push_length(&mut encoded, right)?;
        let (numerator, denominator) = contact
            .effective_conductance(state)
            .map_err(FormationError::ResidentElectricalUnavailable)?
            .parts();
        encoded.extend_from_slice(&numerator.to_le_bytes());
        encoded.extend_from_slice(&denominator.to_le_bytes());
    }
    Ok(encoded)
}

fn resolve_lineage_for_port(
    cohorts: &[ResidentReachedCohort],
    dormant: &[DormantLineageSeed],
    port: &crate::joint_source_episode::JointSourcePortView,
) -> Result<Option<[u8; 16]>, FormationError> {
    let mut resolved = None;
    for cohort in cohorts {
        for (mount, lineage) in cohort
            .anatomy
            .mounts()
            .iter()
            .zip(cohort.anatomy.neuron_lineages())
        {
            let Some(site) = mount.source_site() else {
                continue;
            };
            let key = DormantLineageSeed::from_site(site, *lineage)?;
            if key.matches_port(port) {
                if resolved.is_some_and(|prior| prior != *lineage) {
                    return Err(FormationError::NeuronLineageAuthorityChanged);
                }
                resolved = Some(*lineage);
            }
        }
    }
    for seed in dormant {
        if seed.matches_port(port) {
            if resolved.is_some_and(|prior| prior != seed.neuron_lineage) {
                return Err(FormationError::NeuronLineageAuthorityChanged);
            }
            resolved = Some(seed.neuron_lineage);
        }
    }
    Ok(resolved)
}

fn validate_lineage_state(state: &ResidentCognitiveFormationState) -> Result<(), FormationError> {
    if state.next_lineage_ordinal == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    let mut retained_sources = Vec::new();
    let mut reached_lineages = Vec::new();
    let mut reached_places = Vec::new();
    for cohort in &state.cohorts {
        for (mount, lineage) in cohort
            .anatomy
            .mounts()
            .iter()
            .zip(cohort.anatomy.neuron_lineages())
        {
            let place = mount.place();
            if lineage_ordinal(*lineage)? >= state.next_lineage_ordinal
                || reached_lineages.contains(lineage)
                || reached_places.contains(&place)
            {
                return Err(FormationError::NoncanonicalState);
            }
            reached_lineages.push(*lineage);
            reached_places.push(place);
            if let Some(site) = mount.source_site() {
                let seed = DormantLineageSeed::from_site(site, *lineage)?;
                if retained_sources.iter().any(|prior: &DormantLineageSeed| {
                    prior.same_source(&seed) || prior.neuron_lineage == seed.neuron_lineage
                }) {
                    return Err(FormationError::NoncanonicalState);
                }
                retained_sources.push(seed);
            }
        }
    }
    for (index, seed) in state.dormant_lineage_seeds.iter().enumerate() {
        seed.validate()?;
        if lineage_ordinal(seed.neuron_lineage)? >= state.next_lineage_ordinal
            || state.dormant_lineage_seeds[..index].iter().any(|prior| {
                prior >= seed
                    || prior.same_source(seed)
                    || prior.neuron_lineage == seed.neuron_lineage
            })
            || reached_lineages.contains(&seed.neuron_lineage)
            || retained_sources
                .iter()
                .any(|prior| prior.same_source(seed) || prior.neuron_lineage == seed.neuron_lineage)
        {
            return Err(FormationError::NoncanonicalState);
        }
        retained_sources.push(seed.clone());
    }
    if state
        .electrical_fabric
        .lineages()
        .iter()
        .any(|lineage| !reached_lineages.contains(lineage))
    {
        return Err(FormationError::NoncanonicalState);
    }
    let physical_bonds = organism_physical_bonds(&state.cohorts, &state.electrical_fabric)?;
    let invalid_frontier = |frontier: &[ActiveElectricalFrontierEntry]| {
        frontier.iter().enumerate().any(|(index, entry)| {
            let lineage = entry.receiver();
            let invalid_cause = entry.cause.is_some_and(|cause| {
                cause.transferred_whole_carriers == 0
                    || physical_bonds.binary_search(&cause.bond).is_err()
                    || entry.sender().is_none()
            });
            reached_lineages
                .iter()
                .position(|candidate| *candidate == lineage)
                .and_then(|position| reached_places.get(position))
                .is_none()
                || invalid_cause
                || (index > 0 && frontier[index - 1] >= *entry)
        })
    };
    if invalid_frontier(&state.older_active_electrical_frontier)
        || invalid_frontier(&state.preceding_active_electrical_frontier)
        || invalid_frontier(&state.active_electrical_frontier)
    {
        return Err(FormationError::NoncanonicalState);
    }
    if let Some(population) = &state.resting_population {
        if population.lineage_end_exclusive() > state.next_lineage_ordinal
            || reached_lineages
                .iter()
                .zip(reached_places.iter())
                .any(|(lineage, place)| {
                    let Ok(ordinal) = lineage_ordinal(*lineage) else {
                        return true;
                    };
                    if ordinal < population.lineage_start_ordinal()
                        || ordinal >= population.lineage_end_exclusive()
                    {
                        return false;
                    }
                    population.materialized_lineage_ordinal(*place) != Some(ordinal)
                })
        {
            return Err(FormationError::NoncanonicalState);
        }
    }
    Ok(())
}

fn encode_dormant_lineage_seed(seed: &DormantLineageSeed) -> Result<Vec<u8>, FormationError> {
    seed.validate()?;
    let mut output = Vec::new();
    output.extend_from_slice(DORMANT_LINEAGE_SEED_MAGIC);
    output.push(seed.sense);
    output.extend_from_slice(&seed.topology_index.to_le_bytes());
    push_seed_text(&mut output, &seed.sensor_id)?;
    push_seed_text(&mut output, &seed.substream_id)?;
    output.extend_from_slice(&seed.neuron_lineage);
    Ok(output)
}

fn decode_dormant_lineage_seed(encoded: &[u8]) -> Result<DormantLineageSeed, FormationError> {
    if encoded.get(..DORMANT_LINEAGE_SEED_MAGIC.len()) != Some(DORMANT_LINEAGE_SEED_MAGIC) {
        return Err(FormationError::NoncanonicalState);
    }
    let mut cursor = DORMANT_LINEAGE_SEED_MAGIC.len();
    let sense = *encoded
        .get(cursor)
        .ok_or(FormationError::NoncanonicalState)?;
    cursor += 1;
    let topology_end = cursor
        .checked_add(4)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let topology_index = u32::from_le_bytes(
        encoded
            .get(cursor..topology_end)
            .ok_or(FormationError::NoncanonicalState)?
            .try_into()
            .map_err(|_| FormationError::NoncanonicalState)?,
    );
    cursor = topology_end;
    let sensor_id = take_seed_text(encoded, &mut cursor)?;
    let substream_id = take_seed_text(encoded, &mut cursor)?;
    let lineage_end = cursor
        .checked_add(16)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let neuron_lineage = encoded
        .get(cursor..lineage_end)
        .ok_or(FormationError::NoncanonicalState)?
        .try_into()
        .map_err(|_| FormationError::NoncanonicalState)?;
    if lineage_end != encoded.len() {
        return Err(FormationError::NoncanonicalState);
    }
    DormantLineageSeed::new(
        sense,
        topology_index,
        &sensor_id,
        &substream_id,
        neuron_lineage,
    )
}

fn push_seed_text(output: &mut Vec<u8>, value: &str) -> Result<(), FormationError> {
    push_length(output, value.len())?;
    output.extend_from_slice(value.as_bytes());
    Ok(())
}

fn take_seed_text(encoded: &[u8], cursor: &mut usize) -> Result<String, FormationError> {
    let length = read_length(encoded, cursor)?;
    let end = cursor
        .checked_add(length)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let value = std::str::from_utf8(
        encoded
            .get(*cursor..end)
            .ok_or(FormationError::NoncanonicalState)?,
    )
    .map_err(|_| FormationError::NoncanonicalState)?;
    *cursor = end;
    if value.is_empty() {
        return Err(FormationError::NoncanonicalState);
    }
    Ok(value.to_owned())
}

fn take_state_u64(encoded: &[u8], cursor: &mut usize) -> Result<u64, FormationError> {
    let end = cursor
        .checked_add(8)
        .ok_or(FormationError::ArithmeticOverflow)?;
    let value = u64::from_le_bytes(
        encoded
            .get(*cursor..end)
            .ok_or(FormationError::NoncanonicalState)?
            .try_into()
            .map_err(|_| FormationError::NoncanonicalState)?,
    );
    *cursor = end;
    Ok(value)
}

fn exact_optical_receptor_anatomy(
    aperture_population: u128,
) -> Result<OpticalReceptorAnatomy, FormationError> {
    if aperture_population == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    OpticalReceptorAnatomy::new(
        BigRational::from_integer(BigInt::from(4)),
        BigRational::from_integer(BigInt::from(aperture_population)),
        BigRational::new(BigInt::from(1), BigInt::from(2)),
        BigRational::from_integer(BigInt::from(1)),
    )
    .map_err(FormationError::OpticalWorkUnavailable)
}

/// Auditory transduction anatomy, pinned by OPTICAL PARITY (Law A5,
/// `docs/GUALA_AUDITORY_TRANSDUCTION_DESIGN_2026-08-06.md` §4.3).
///
/// Nothing in this organism's pipeline measures pascals — the samples are
/// normalized to their own capture's full scale — so the declared reference
/// pressure is not a measurement of the world, it is the declaration of the
/// organism's full-scale sensitivity.  Pinning it by optical parity makes
/// full-scale sound exactly as energetic to this body as full-scale light and
/// introduces NO number that is not already in the tree: these are literally
/// `exact_optical_receptor_anatomy`'s own four factors, whose product is the
/// composite constant K = 2 zJ per (dimensionless² · second).  Only the
/// product is a physical claim; the factorization is the optical one.
fn exact_auditory_receptor_anatomy(
    aperture_population: u128,
) -> Result<AuditoryReceptorAnatomy, FormationError> {
    if aperture_population == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    AuditoryReceptorAnatomy::new(
        BigRational::from_integer(BigInt::from(4)),
        BigRational::from_integer(BigInt::from(aperture_population)),
        BigRational::new(BigInt::from(1), BigInt::from(2)),
        BigRational::from_integer(BigInt::from(1)),
    )
    .map_err(FormationError::AuditoryWorkUnavailable)
}

/// Tactile transduction anatomy, pinned by OPTICAL PARITY (Law T5,
/// `tactile_receptor_work`).
///
/// Nothing in this organism's pipeline measures pascals or newtons — a contact
/// port carries the fraction of its own declared site area that the touched
/// object's footprint covers — so the declared reference contact stress is not
/// a measurement of the world, it is the declaration of the organism's
/// full-scale sensitivity.  Pinning it by optical parity makes FULL CONTACT
/// exactly as energetic to this body as full-scale light and introduces NO
/// number that is not already in the tree: these are literally
/// `exact_optical_receptor_anatomy`'s own four factors, whose product is the
/// composite constant K = 2 zJ per (dimensionless · second) — the same
/// factorization `exact_auditory_receptor_anatomy` already reuses.  Only the
/// product is a physical claim.
fn exact_tactile_receptor_anatomy(
    aperture_population: u128,
) -> Result<TactileReceptorAnatomy, FormationError> {
    if aperture_population == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    TactileReceptorAnatomy::new(
        BigRational::from_integer(BigInt::from(4)),
        BigRational::from_integer(BigInt::from(aperture_population)),
        BigRational::new(BigInt::from(1), BigInt::from(2)),
        BigRational::from_integer(BigInt::from(1)),
    )
    .map_err(FormationError::TactileWorkUnavailable)
}

/// Chemical transduction consumes an already receptor-local fraction of the
/// declared saturating concentration. Optical parity supplies the existing
/// organism-scale receptor-energy declaration without inventing affinity or
/// response coefficients; chemical identity remains in anatomy and source
/// locality, not in the energy conversion.
fn exact_chemical_receptor_anatomy(
    aperture_population: u128,
) -> Result<ChemicalReceptorAnatomy, FormationError> {
    if aperture_population == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    ChemicalReceptorAnatomy::new(
        BigRational::from_integer(BigInt::from(4)),
        BigRational::from_integer(BigInt::from(aperture_population)),
        BigRational::new(BigInt::from(1), BigInt::from(2)),
        BigRational::from_integer(BigInt::from(1)),
    )
    .map_err(FormationError::ChemicalWorkUnavailable)
}

/// Local articulatory mechanoreceptors use the organism's existing exact
/// full-scale receptor-energy declaration. The source retains its distinct
/// physical quantity and signed trajectory; only the material sensitivity is
/// shared, so no fitted body coefficient is introduced.
fn exact_articulatory_receptor_anatomy(
    aperture_population: u128,
) -> Result<ArticulatoryReceptorAnatomy, FormationError> {
    if aperture_population == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    ArticulatoryReceptorAnatomy::new(
        BigRational::from_integer(BigInt::from(4)),
        BigRational::from_integer(BigInt::from(aperture_population)),
        BigRational::new(BigInt::from(1), BigInt::from(2)),
        BigRational::from_integer(BigInt::from(1)),
    )
    .map_err(FormationError::ArticulatoryWorkUnavailable)
}

/// Core and cutaneous thermoreceptors retain their own physical quantity but
/// use the organism's one existing full-scale receptor-energy declaration.
/// This supplies material sensitivity only; it adds no thermal set point,
/// comfort score, or semantic polarity.
fn exact_thermal_receptor_anatomy(
    aperture_population: u128,
) -> Result<ThermalReceptorAnatomy, FormationError> {
    if aperture_population == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    ThermalReceptorAnatomy::new(
        BigRational::from_integer(BigInt::from(4)),
        BigRational::from_integer(BigInt::from(aperture_population)),
        BigRational::new(BigInt::from(1), BigInt::from(2)),
        BigRational::from_integer(BigInt::from(1)),
    )
    .map_err(FormationError::ThermalWorkUnavailable)
}

/// Antagonist position receptors use the same declared full-scale local
/// mechanical sensitivity as the other body mechanoreceptors. Their distinct
/// physical input is the exact length fraction of their own body terminal.
fn exact_proprioceptive_receptor_anatomy(
    aperture_population: u128,
) -> Result<ProprioceptiveReceptorAnatomy, FormationError> {
    if aperture_population == 0 {
        return Err(FormationError::NoncanonicalState);
    }
    ProprioceptiveReceptorAnatomy::new(
        BigRational::from_integer(BigInt::from(4)),
        BigRational::from_integer(BigInt::from(aperture_population)),
        BigRational::new(BigInt::from(1), BigInt::from(2)),
        BigRational::from_integer(BigInt::from(1)),
    )
    .map_err(FormationError::ProprioceptiveWorkUnavailable)
}

/// Which mounted receptor law governs one occurrence.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ReceptorLaw {
    Sight,
    Sound,
    Touch,
    Chemical,
    ArticulatoryBody,
    ThermalBody,
    ProprioceptiveBody,
}

fn receptor_law_for_reached_coordinates(
    reached_sources: &[(
        NeuronSourceSite,
        &crate::joint_source_episode::JointSourcePortView,
    )],
    coordinate_indices: &[usize],
) -> Option<ReceptorLaw> {
    let ports = coordinate_indices
        .iter()
        .filter_map(|index| reached_sources.get(*index).map(|(_, port)| *port))
        .collect::<Vec<_>>();
    if ports.len() != coordinate_indices.len() {
        return None;
    }
    receptor_law_for_ports(&ports)
}

fn exact_duration_microseconds(duration_seconds: &BigRational) -> Result<u32, FormationError> {
    if duration_seconds <= &BigRational::zero() {
        return Err(FormationError::NoncanonicalState);
    }
    let microseconds = duration_seconds * BigInt::from(1_000_000_u32);
    if !microseconds.is_integer() {
        return Err(FormationError::NoncanonicalState);
    }
    microseconds
        .to_integer()
        .to_u32()
        .filter(|value| *value > 0)
        .ok_or(FormationError::ArithmeticOverflow)
}

fn receptor_law_for_ports(
    ports: &[&crate::joint_source_episode::JointSourcePortView],
) -> Option<ReceptorLaw> {
    if ports.is_empty() {
        return None;
    }
    let all_ports = |predicate: fn(&crate::joint_source_episode::JointSourcePortView) -> bool| {
        ports.iter().all(|port| predicate(port))
    };
    if all_ports(|port| {
        port.sense == 0
            && port.physical_quantity == RETINAL_SPECTRAL_IRRADIANCE_QUANTITY
            && port.physical_unit == RETINAL_REFERENCE_IRRADIANCE_UNIT
    }) {
        return Some(ReceptorLaw::Sight);
    }
    if all_ports(|port| {
        port.sense == 1
            && port.physical_quantity == COCHLEAR_BAND_PRESSURE_QUANTITY
            && port.physical_unit == COCHLEAR_REFERENCE_PRESSURE_UNIT
    }) {
        return Some(ReceptorLaw::Sound);
    }
    if all_ports(|port| {
        port.sense == PhysicalSourceSense::Touch.declared_layer()
            && port.physical_quantity == CONTACT_SITE_OCCUPANCY_QUANTITY
            && port.physical_unit == CONTACT_REFERENCE_OCCUPANCY_UNIT
    }) {
        return Some(ReceptorLaw::Touch);
    }
    if all_ports(|port| {
        port.sense == PhysicalSourceSense::Smell.declared_layer()
            && port.physical_quantity == OLFACTORY_VOLATILE_CONCENTRATION_QUANTITY
            && port.physical_unit == RECEPTOR_SATURATION_FRACTION_UNIT
    }) || all_ports(|port| {
        port.sense == PhysicalSourceSense::Taste.declared_layer()
            && port.physical_quantity == GUSTATORY_CONTACT_CONCENTRATION_QUANTITY
            && port.physical_unit == RECEPTOR_SATURATION_FRACTION_UNIT
    }) {
        return Some(ReceptorLaw::Chemical);
    }
    if all_ports(|port| {
        port.sense == PhysicalSourceSense::Body.declared_layer()
            && matches!(
                port.physical_quantity.as_str(),
                RESPIRATORY_VOLUME_VELOCITY_QUANTITY
                    | LARYNGEAL_GLOTTAL_OPENING_QUANTITY
                    | ORAL_APERTURE_AREA_QUANTITY
                    | PERIORAL_SKIN_DEFORMATION_QUANTITY
            )
            && port.physical_unit == ARTICULATORY_MECHANICAL_FRACTION_UNIT
    }) {
        return Some(ReceptorLaw::ArticulatoryBody);
    }
    if all_ports(|port| {
        port.sense == PhysicalSourceSense::Body.declared_layer()
            && port.physical_quantity == THERMORECEPTOR_TEMPERATURE_QUANTITY
            && port.physical_unit == THERMORECEPTOR_REFERENCE_INTERVAL_UNIT
    }) {
        return Some(ReceptorLaw::ThermalBody);
    }
    if all_ports(|port| {
        port.sense == PhysicalSourceSense::Body.declared_layer()
            && port.body_proprioceptor_terminal.is_some()
            && port.physical_quantity == ANTAGONIST_PROPRIOCEPTOR_LENGTH_QUANTITY
            && port.physical_unit == ARTICULATED_AXIS_SPAN_FRACTION_UNIT
    }) {
        return Some(ReceptorLaw::ProprioceptiveBody);
    }
    None
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) enum FormationError {
    BudgetExceeded {
        required: usize,
        available: usize,
    },
    ArithmeticOverflow,
    InvalidSourceGeneration,
    SourceOccurrenceAbsent,
    JointFieldUnavailable(JointNeuronBoundaryError),
    PhysicalGenesisUnavailable(VirtualMaterialGenesisError),
    VestibularUnavailable(FunctionalVestibularError),
    DevelopmentalElectricalUnavailable(DevelopmentalElectricalError),
    DevelopmentalRestingPopulationUnavailable(DevelopmentalRestingPopulationError),
    OpticalWorkUnavailable(OpticalReceptorWorkError),
    AuditoryWorkUnavailable(AuditoryReceptorWorkError),
    TactileWorkUnavailable(TactileReceptorWorkError),
    ChemicalWorkUnavailable(ChemicalReceptorWorkError),
    ArticulatoryWorkUnavailable(ArticulatoryReceptorWorkError),
    ThermalWorkUnavailable(ThermalReceptorWorkError),
    ProprioceptiveWorkUnavailable(ProprioceptiveReceptorWorkError),
    LocalGateWorkUnavailable(ReceptorDeliveryError),
    PhysicalSettlementUnavailable(ReachedCohortError),
    ResidentElectricalUnavailable(SparseElectricalError),
    InternalMembraneUnavailable(MembraneChargeError),
    PhysicalMosaicUnavailable(PhysicalMosaicError),
    PhysicalMosaicCodecUnavailable(PhysicalMosaicCodecError),
    /// The body truthfully refused an intake: it can absorb nothing, or the
    /// declaration carried no energy at all.
    NutritionUnavailable(MetabolicError),
    /// An authored contact could not be resolved against exactly two members
    /// of exactly one living cohort, or none was authored at all.  Naming a
    /// connection the organism does not have is refused, never inferred.
    AuthoredContactUnavailable,
    NeuronLineageAuthorityAbsent,
    NeuronLineageAuthorityChanged,
    /// The retired archive checkpoint (`GLHST01`) failed to encode or decode.
    /// This is a persisted-layout fault, never an archive availability fault:
    /// nothing reads cold custody any more.
    HippocampalCheckpointUnavailable(HippocampalError),
    PreparedPredecessorChanged,
    DuplicateDevelopmentalSeed,
    RetiredCognitiveState,
    BadVersion,
    NoncanonicalState,
}

impl fmt::Display for FormationError {
    fn fmt(&self, output: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::BudgetExceeded {
                required,
                available,
            } => write!(
                output,
                "resident complete-neuron state requires {required} bytes but {available} were admitted"
            ),
            Self::ArithmeticOverflow => write!(output, "resident cognitive arithmetic overflow"),
            Self::InvalidSourceGeneration => {
                write!(output, "resident cognitive generation cannot advance")
            }
            Self::SourceOccurrenceAbsent => write!(output, "source contains no joint occurrence"),
            Self::JointFieldUnavailable(error) => {
                write!(output, "complete joint field is unavailable: {error:?}")
            }
            Self::PhysicalGenesisUnavailable(error) => {
                write!(output, "complete virtual-material neuron genesis is unavailable: {error:?}")
            }
            Self::VestibularUnavailable(error) => {
                write!(output, "typed vestibular neuron path is unavailable: {error:?}")
            }
            Self::DevelopmentalElectricalUnavailable(error) => {
                write!(output, "developmental electrical anatomy is unavailable: {error:?}")
            }
            Self::DevelopmentalRestingPopulationUnavailable(error) => write!(
                output,
                "developmental resting population is unavailable: {error:?}"
            ),
            Self::OpticalWorkUnavailable(error) => {
                write!(output, "exact optical receptor work is unavailable: {error:?}")
            }
            Self::AuditoryWorkUnavailable(error) => {
                write!(output, "exact auditory receptor work is unavailable: {error:?}")
            }
            Self::TactileWorkUnavailable(error) => {
                write!(output, "exact tactile receptor work is unavailable: {error:?}")
            }
            Self::ChemicalWorkUnavailable(error) => {
                write!(output, "exact chemical receptor work is unavailable: {error:?}")
            }
            Self::ArticulatoryWorkUnavailable(error) => write!(
                output,
                "exact articulatory body receptor work is unavailable: {error:?}"
            ),
            Self::ThermalWorkUnavailable(error) => write!(
                output,
                "exact thermal body receptor work is unavailable: {error:?}"
            ),
            Self::ProprioceptiveWorkUnavailable(error) => write!(
                output,
                "exact antagonist proprioceptor work is unavailable: {error:?}"
            ),
            Self::LocalGateWorkUnavailable(error) => {
                write!(output, "exact local gate work is unavailable: {error:?}")
            }
            Self::PhysicalSettlementUnavailable(error) => {
                write!(output, "resident physical neuron settlement is unavailable: {error:?}")
            }
            Self::ResidentElectricalUnavailable(error) => {
                write!(output, "resident sparse electrical fabric is unavailable: {error:?}")
            }
            Self::InternalMembraneUnavailable(error) => {
                write!(output, "internal membrane occurrence is unavailable: {error:?}")
            }
            Self::PhysicalMosaicUnavailable(error) => {
                write!(output, "physical mosaic admission is unavailable: {error:?}")
            }
            Self::PhysicalMosaicCodecUnavailable(error) => {
                write!(output, "physical mosaic persistence is unavailable: {error:?}")
            }
            Self::NutritionUnavailable(error) => {
                write!(output, "the body refuses this nutrition intake: {error:?}")
            }
            Self::AuthoredContactUnavailable => write!(
                output,
                "an authored contact does not name exactly two members of one living cohort"
            ),
            Self::NeuronLineageAuthorityAbsent => {
                write!(output, "resident neuron lineage authority is absent")
            }
            Self::NeuronLineageAuthorityChanged => {
                write!(output, "resident neuron lineage authority changed")
            }
            Self::HippocampalCheckpointUnavailable(error) => write!(
                output,
                "the retired hippocampal checkpoint field is malformed: {error:?}"
            ),
            Self::PreparedPredecessorChanged => {
                write!(output, "prepared cognitive predecessor changed before commit")
            }
            Self::DuplicateDevelopmentalSeed => {
                write!(output, "developmental electrical source-site seed is duplicated")
            }
            Self::RetiredCognitiveState => write!(
                output,
                "retired empty or DSF-impression cognitive state cannot be restored"
            ),
            Self::BadVersion => write!(output, "cognitive boundary state has wrong version"),
            Self::NoncanonicalState => write!(output, "cognitive boundary state is noncanonical"),
        }
    }
}

impl std::error::Error for FormationError {}

#[cfg(test)]
mod real_body_migration_probe;

#[cfg(test)]
mod tests {
    use super::*;

    /// Quiet (dark, silent) episodes appended after a presentation so the
    /// cohort can descend all the way to electrical rest.  Since the
    /// 2026-08-05 geometric differentiation the members' capacitances differ,
    /// so a settled cohort equalizes POTENTIAL rather than charge and takes
    /// longer to go silent than the tie-frozen anatomy did; the tail is
    /// transport, the quiescence is physics.
    const DARK_TAIL_EPISODES: usize = 64;
    use crate::developmental_electrical_anatomy::{
        DevelopmentalElectricalContact, DevelopmentalElectricalSeed,
    };
    use crate::articulated_body_joint_source_builder::{
        admit_articulated_body_proprioceptive_source,
        admit_complete_articulated_body_state_source,
    };
    use crate::exact_rational::ExactRational;
    use crate::local_cupula_hair_bundle_geometry::LocalCupulaBundleAnatomy;
    use crate::neuron_source_anchor::tests::{
        exact_dark_optical_episode, exact_episode, exact_five_optical_episode,
        exact_four_dark_optical_episode, exact_four_partial_optical_episode,
        exact_four_reordered_optical_episode, exact_four_single_optical_episode,
        exact_optical_binaural_episode, exact_optical_episode, exact_split_four_optical_episode,
        exact_two_of_four_optical_episode,
    };
    use crate::reached_vestibular_bundle_path::settle_reached_vestibular_bundle_tick;
    use crate::resident_receptor_transition::prepare_resident_vestibular_ingress;
    use crate::vestibular_neuron_path::phase_one_virtual_vestibular_anatomy;
    use crate::virtual_body_yaw_motion::{
        settle_signed_yaw_actuation, SignedYawActuation, YawBodyState,
    };
    use crate::virtual_articulated_body::{
        ArticulatedBodyState, BodyAxis, BodyEffectorDirection, BodyProprioceptiveConsequence,
        BodyProprioceptorTerminal,
    };
    use crate::virtual_vestibular_canal::{CanalAnatomy, CanalState, PositiveRatio};

    fn explicit_optical_seed(
        source: &NativeJointSourceEpisode,
        conductance_picosiemens: i128,
    ) -> DevelopmentalElectricalSeed {
        explicit_optical_seed_for_occurrence(source, 0, conductance_picosiemens)
    }

    fn explicit_optical_seed_for_occurrence(
        source: &NativeJointSourceEpisode,
        occurrence_index: usize,
        conductance_picosiemens: i128,
    ) -> DevelopmentalElectricalSeed {
        let shared =
            prepare_complete_joint_field_admitted_fixture(source, occurrence_index).unwrap();
        let sites = (0..shared.vertex_count())
            .map(|coordinate_index| {
                let perspective = bind_neuron_perspective(&shared, coordinate_index, 0).unwrap();
                NeuronSourceSite::from_anchor(
                    bind_neuron_source_anchor(source, perspective).unwrap(),
                )
            })
            .collect::<Vec<_>>();
        let contacts = (1..sites.len())
            .map(|right| {
                DevelopmentalElectricalContact::new(
                    right - 1,
                    right,
                    ExactRational::integer(conductance_picosiemens),
                    sites.len(),
                )
                .unwrap()
            })
            .collect::<Vec<_>>();
        DevelopmentalElectricalSeed::new(sites, contacts).unwrap()
    }

    fn local_lineage(ordinal: u64) -> [u8; 16] {
        let mut lineage = [0; 16];
        lineage[..8].copy_from_slice(LINEAGE_DOMAIN);
        lineage[8..].copy_from_slice(&ordinal.to_be_bytes());
        lineage
    }

    #[test]
    fn transient_bond_index_preserves_exact_parallel_ordinals() {
        let left = local_lineage(1);
        let right = local_lineage(2);
        let other = local_lineage(3);
        let mut ordinals = std::collections::BTreeMap::new();

        let first = stable_bond_for_next_edge(&mut ordinals, left, right).unwrap();
        let reversed = stable_bond_for_next_edge(&mut ordinals, right, left).unwrap();
        let independent = stable_bond_for_next_edge(&mut ordinals, left, other).unwrap();
        let third = stable_bond_for_next_edge(&mut ordinals, left, right).unwrap();

        assert_eq!(first.endpoints(), (left, right));
        assert_eq!(first.parallel_ordinal(), 0);
        assert_eq!(reversed.endpoints(), (left, right));
        assert_eq!(reversed.parallel_ordinal(), 1);
        assert_eq!(independent.parallel_ordinal(), 0);
        assert_eq!(third.parallel_ordinal(), 2);
        assert_eq!(ordinals.get(&(left, right)), Some(&3));
        assert_eq!(ordinals.get(&(left, other)), Some(&1));
    }

    fn mount_body_regulation_fixture(
        cohorts: &mut Vec<ResidentReachedCohort>,
        resting_population: &mut Option<DevelopmentalRestingPopulation>,
        next_lineage_ordinal: &mut u64,
        electrical_fabric: &mut ResidentElectricalFabric,
        axis: BodyAxis,
        direction: BodyEffectorDirection,
    ) -> ([u8; 16], [u8; 16], NeuronSourceSite) {
        let source = admit_complete_articulated_body_state_source(
            0,
            &ArticulatedBodyState::at_neutral(),
        )
        .unwrap();
        let terminal = BodyProprioceptorTerminal::new(axis, direction);
        let receptor_site = NeuronSourceSite::from_source_port(
            &source.joint_source_ports()[terminal.ordinal()],
        )
        .unwrap();
        let receptor_place = DeclaredNeuronPlace::from_source_site(&receptor_site);
        let receptor_neuron = create_quiescent_virtual_material_neuron(receptor_place).unwrap();
        let receptor_lineage = allocate_local_lineage(next_lineage_ordinal).unwrap();
        let local_anatomy = SparseElectricalAnatomy::new(1, Vec::new()).unwrap();
        let receptor_anatomy = ReachedCohortAnatomy::new_mounted(
            vec![receptor_neuron.anatomy],
            vec![receptor_lineage],
            vec![ReachedNeuronMount::Receptor(receptor_site.clone())],
            local_anatomy.clone(),
        )
        .unwrap();
        cohorts.push(ResidentReachedCohort {
            state: ReachedCohortState::new(
                &receptor_anatomy,
                vec![receptor_neuron.state],
                SparseElectricalState::genesis(&local_anatomy),
            )
            .unwrap()
            .into(),
            anatomy: receptor_anatomy,
            pending_experience: None,
            retained_experience: None,
            pending_recurrence: None,
        });
        mount_reached_local_integration(
            cohorts,
            resting_population,
            next_lineage_ordinal,
            electrical_fabric,
            &[(receptor_lineage, receptor_place)],
        )
        .unwrap();
        let regulation = mount_reached_body_regulation(
            cohorts,
            resting_population,
            next_lineage_ordinal,
            electrical_fabric,
            &[receptor_lineage],
        )
        .unwrap();
        assert_eq!(regulation.len(), 1);
        (regulation[0], receptor_lineage, receptor_site)
    }

    #[test]
    fn empty_genesis_is_exact_and_bounded() {
        let state = ResidentCognitiveFormationState::default();
        let encoded = state.encode(CURRENT_FIXED_BYTES).unwrap();
        assert_eq!(encoded.len(), CURRENT_FIXED_BYTES);
        assert_eq!(
            ResidentCognitiveFormationState::decode(&encoded, CURRENT_FIXED_BYTES).unwrap(),
            state
        );
    }

    #[test]
    fn complete_body_source_mounts_bounded_receptor_integration_and_regulation_once() {
        const MAX_BYTES: usize = 256_000_000;
        let source = admit_complete_articulated_body_state_source(
            0,
            &ArticulatedBodyState::at_neutral(),
        )
        .unwrap();
        let state = ResidentCognitiveFormationState::default();
        let first = state.prepare(&source, MAX_BYTES).unwrap();
        let counts = first.successor.observe_reached_neuron_count_by_layer();
        let energized_terminal_count = source
            .joint_source_ports()
            .iter()
            .filter(|port| {
                port.exact_normalized_sources
                    .iter()
                    .any(|value| !value.is_zero())
            })
            .count();
        assert_eq!(counts.iter().find(|(layer, _)| *layer == 5), Some(&(5, 74)));
        assert_eq!(counts.iter().find(|(layer, _)| *layer == 6), Some(&(6, 74)));
        assert_eq!(
            counts.iter().find(|(layer, _)| *layer == 8),
            Some(&(8, energized_terminal_count))
        );
        let terminal_gate_populations = first
            .successor
            .cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_anatomies())
            })
            .filter_map(|(mount, anatomy)| {
                mount
                    .source_site()
                    .and_then(NeuronSourceSite::body_proprioceptor_terminal)
                    .map(|_| anatomy.gate_population())
            })
            .collect::<Vec<_>>();
        assert_eq!(terminal_gate_populations, vec![1; 74]);
        assert_eq!(first.observation.externally_perturbed_body_receptor_count, 0);

        let first_lineages = first.successor.retained_neuron_lineages();
        let encoded = state.encode_successor(&first, MAX_BYTES).unwrap();
        let cold = ResidentCognitiveFormationState::decode(&encoded, MAX_BYTES).unwrap();
        let repeated = cold.prepare(&source, MAX_BYTES).unwrap();
        assert_eq!(
            repeated.successor.observe_reached_neuron_count_by_layer(),
            counts
        );
        assert_eq!(repeated.successor.retained_neuron_lineages(), first_lineages);
    }

    #[test]
    fn one_antagonist_pair_mounts_its_local_body_regulation() {
        let axis = BodyAxis::TorsoPitch;
        let anatomy = axis.anatomy();
        let source = admit_articulated_body_proprioceptive_source(
            0,
            &[BodyProprioceptiveConsequence {
                axis,
                unit: anatomy.unit,
                predecessor_position: anatomy.neutral,
                successor_position: anatomy.neutral,
                signed_displacement: 0,
                toward_minimum_carriers: 0,
                toward_maximum_carriers: 0,
                opposed_carriers_per_terminal: 0,
                applied_displacement_quanta: 0,
                stalled_carriers: 0,
            }],
        )
        .unwrap();
        let state = ResidentCognitiveFormationState::default();
        let prepared = state.prepare(&source, 16_000_000).unwrap();
        let counts = prepared.successor.observe_reached_neuron_count_by_layer();
        assert_eq!(counts.iter().find(|(layer, _)| *layer == 5), Some(&(5, 2)));
        assert_eq!(counts.iter().find(|(layer, _)| *layer == 6), Some(&(6, 2)));
        assert_eq!(counts.iter().find(|(layer, _)| *layer == 8), Some(&(8, 2)));
    }

    #[test]
    fn every_declared_antagonist_pair_settles_independently() {
        for axis in crate::virtual_articulated_body::BODY_AXES {
            let anatomy = axis.anatomy();
            let source = admit_articulated_body_proprioceptive_source(
                0,
                &[BodyProprioceptiveConsequence {
                    axis,
                    unit: anatomy.unit,
                    predecessor_position: anatomy.neutral,
                    successor_position: anatomy.neutral,
                    signed_displacement: 0,
                    toward_minimum_carriers: 0,
                    toward_maximum_carriers: 0,
                    opposed_carriers_per_terminal: 0,
                    applied_displacement_quanta: 0,
                    stalled_carriers: 0,
                }],
            )
            .unwrap();
            ResidentCognitiveFormationState::default()
                .prepare(&source, 16_000_000)
                .unwrap_or_else(|error| panic!("{axis:?} failed: {error:?}"));
        }
    }

    #[test]
    fn dormant_four_field_lineage_seed_is_consumed_once_by_exact_current_source() {
        let source = exact_optical_episode();
        let port = &source.joint_source_ports()[0];
        let seed = DormantLineageSeed::new(
            port.sense,
            port.topology_index,
            &port.sensor_id,
            &port.substream_id,
            local_lineage(7),
        )
        .unwrap();
        let state =
            ResidentCognitiveFormationState::from_genesis_parts(0, 8, Vec::new(), vec![seed])
                .unwrap();
        let dormant_bytes = state.encode(16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&dormant_bytes, 16_000_000).unwrap();
        assert_eq!(restored.encode(16_000_000).unwrap(), dormant_bytes);
        assert_eq!(restored.dormant_lineage_seeds.len(), 1);

        let prepared = restored.prepare(&source, 16_000_000).unwrap();
        assert!(prepared.successor.dormant_lineage_seeds.is_empty());
        assert_eq!(prepared.successor.next_lineage_ordinal, 9);
        assert_eq!(
            prepared.successor.cohorts[0].anatomy.neuron_lineages(),
            &[local_lineage(7)]
        );
        let successor = restored.encode_successor(&prepared, 16_000_000).unwrap();
        let cold = ResidentCognitiveFormationState::decode(&successor, 16_000_000).unwrap();
        assert_eq!(cold.encode(16_000_000).unwrap(), successor);
        assert!(cold.dormant_lineage_seeds.is_empty());
        assert_eq!(
            cold.cohorts[0].anatomy.neuron_lineages(),
            &[local_lineage(7)]
        );
    }

    #[test]
    fn one_shared_field_is_evaluated_once_and_new_lineage_survives_restart() {
        let source = exact_optical_episode();
        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| count.set(0));
        let state = ResidentCognitiveFormationState::default();
        let prepared = state.prepare(&source, 16_000_000).unwrap();
        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| {
            assert_eq!(count.get(), source.joint_source_occurrences().len());
        });
        assert_eq!(prepared.observation.dsf_delivery_count, 2);
        assert_eq!(prepared.successor.summary().complete_neuron_count, 2);
        assert_eq!(prepared.successor.cohorts.len(), 2);
        assert_eq!(prepared.successor.next_lineage_ordinal, 3);
        assert_eq!(
            prepared.successor.cohorts[0].anatomy.neuron_lineages(),
            &[local_lineage(1)]
        );
        let encoded = state.encode_successor(&prepared, 16_000_000).unwrap();
        let cold = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(cold.encode(16_000_000).unwrap(), encoded);
        let recurrent = cold.prepare(&source, 16_000_000).unwrap();
        assert_eq!(recurrent.successor.next_lineage_ordinal, 3);
        assert_eq!(
            recurrent.successor.cohorts[0].anatomy.neuron_lineages(),
            &[local_lineage(1)]
        );
    }

    #[test]
    fn reordered_occurrence_reuses_the_same_persistent_neurons() {
        let first = crate::neuron_source_anchor::tests::exact_four_optical_episode();
        let reordered = exact_four_reordered_optical_episode();
        let mut state = ResidentCognitiveFormationState::default();
        let prepared = state.prepare(&first, 16_000_000).unwrap();
        state.commit(prepared).unwrap();
        let original_lineages = state.retained_neuron_lineages();
        assert_eq!(original_lineages.len(), 8);

        let prepared = state.prepare(&reordered, 16_000_000).unwrap();
        assert_eq!(prepared.successor.cohorts.len(), 5);
        assert_eq!(prepared.successor.summary().complete_neuron_count, 8);
        assert_eq!(
            prepared.successor.retained_neuron_lineages(),
            original_lineages
        );
        let encoded = state.encode_successor(&prepared, 16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(restored.retained_neuron_lineages(), original_lineages);
        assert_eq!(restored.encode(16_000_000).unwrap(), encoded);
    }

    #[test]
    fn subset_occurrence_advances_receptors_and_still_charged_internal_material() {
        let first = crate::neuron_source_anchor::tests::exact_four_optical_episode();
        let subset = exact_two_of_four_optical_episode();
        let mut state = ResidentCognitiveFormationState::default();
        state
            .commit(state.prepare(&first, 16_000_000).unwrap())
            .unwrap();
        let predecessor = state.cohorts[0].state.clone();
        let lineages = state.retained_neuron_lineages();
        let carried_frontier = state
            .active_electrical_frontier
            .iter()
            .map(|entry| entry.frontier_lineage())
            .collect::<Vec<_>>();
        let adjacent_to_carried_frontier = |target: [u8; 16]| {
            state
                .electrical_fabric
                .contact_endpoints()
                .any(|(left, right)| {
                    let left = state.electrical_fabric.lineages()[left];
                    let right = state.electrical_fabric.lineages()[right];
                    (left == target && carried_frontier.contains(&right))
                        || (right == target && carried_frontier.contains(&left))
                })
        };
        assert!(adjacent_to_carried_frontier(
            state.cohorts[0].anatomy.neuron_lineages()[2]
        ));
        assert!(adjacent_to_carried_frontier(
            state.cohorts[0].anatomy.neuron_lineages()[3]
        ));

        let prepared = state.prepare(&subset, 16_000_000).unwrap();
        assert_eq!(prepared.successor.cohorts.len(), 5);
        assert_eq!(prepared.successor.summary().complete_neuron_count, 8);
        assert_eq!(prepared.successor.retained_neuron_lineages(), lineages);
        let successor = &prepared.successor.cohorts[0].state;
        // Receptors 2 and 3 receive no new external gate work, but both are
        // the exact advancing endpoints retained from the predecessor's local
        // contact transfers. Their internal material therefore settles once
        // without being relabelled as fresh sensory input. The two externally
        // reached receptors advance as well.
        assert_ne!(successor.neurons()[2], predecessor.neurons()[2]);
        assert_ne!(successor.neurons()[3], predecessor.neurons()[3]);
        assert_ne!(successor.neurons()[0], predecessor.neurons()[0]);
        assert_ne!(successor.neurons()[1], predecessor.neurons()[1]);

        let encoded = state.encode_successor(&prepared, 16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(restored.retained_neuron_lineages(), lineages);
        assert_eq!(restored.encode(16_000_000).unwrap(), encoded);
    }

    #[test]
    fn overlapping_occurrence_reuses_four_residents_and_creates_only_one_new_neuron() {
        let four = crate::neuron_source_anchor::tests::exact_four_optical_episode();
        let five = exact_five_optical_episode();
        let mut state = ResidentCognitiveFormationState::default();
        state
            .commit(state.prepare(&four, 16_000_000).unwrap())
            .unwrap();
        let predecessor_bytes = state.encode(16_000_000).unwrap();
        let cold_predecessor =
            ResidentCognitiveFormationState::decode(&predecessor_bytes, 16_000_000).unwrap();
        let predecessor_anatomy = state.cohorts[0].anatomy.clone();
        let predecessor_lineages = state.retained_neuron_lineages();

        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| count.set(0));
        let warm = state.prepare(&five, 16_000_000).unwrap();
        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| {
            assert_eq!(count.get(), five.joint_source_occurrences().len());
        });
        let cold = cold_predecessor.prepare(&five, 16_000_000).unwrap();
        assert_eq!(cold, warm);
        assert_eq!(warm.successor.cohorts.len(), 6);
        assert_eq!(warm.successor.summary().complete_neuron_count, 10);
        assert_eq!(warm.successor.next_lineage_ordinal, 11);
        assert_eq!(
            &warm.successor.cohorts[0].anatomy.neuron_anatomies()[..4],
            predecessor_anatomy.neuron_anatomies()
        );
        assert_eq!(
            warm.successor.cohorts[0]
                .anatomy
                .source_sites()
                .take(4)
                .collect::<Vec<_>>(),
            predecessor_anatomy.source_sites().collect::<Vec<_>>()
        );
        assert!(predecessor_lineages
            .iter()
            .all(|lineage| warm.successor.retained_neuron_lineages().contains(lineage)));
        assert!(warm
            .successor
            .retained_neuron_lineages()
            .contains(&local_lineage(9)));
        assert!(warm
            .successor
            .retained_neuron_lineages()
            .contains(&local_lineage(10)));
        let lineages = warm.successor.retained_neuron_lineages();
        assert!(lineages
            .iter()
            .enumerate()
            .all(|(index, lineage)| !lineages[..index].contains(lineage)));

        let encoded = state.encode_successor(&warm, 16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(restored, warm.successor);
        assert_eq!(restored.encode(16_000_000).unwrap(), encoded);
    }

    #[test]
    fn crossed_compartment_occurrence_settles_two_resident_fluids_without_new_neurons() {
        let split = exact_split_four_optical_episode();
        let joint = crate::neuron_source_anchor::tests::exact_four_optical_episode();
        let left_seed = explicit_optical_seed_for_occurrence(&split, 0, 500);
        let right_seed = explicit_optical_seed_for_occurrence(&split, 1, 500);
        let mut state = ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![
            left_seed, right_seed,
        ])
        .unwrap();
        state
            .commit(state.prepare(&split, 16_000_000).unwrap())
            .unwrap();
        assert_eq!(state.cohorts.len(), 6);
        assert_eq!(state.summary().complete_neuron_count, 8);
        assert_eq!(state.next_lineage_ordinal, 9);
        let predecessor_anatomies = state
            .cohorts
            .iter()
            .map(|cohort| cohort.anatomy.clone())
            .collect::<Vec<_>>();
        let predecessor_lineages = state.retained_neuron_lineages();
        let predecessor_contacts = state
            .cohorts
            .iter()
            .map(|cohort| cohort.anatomy.contact_count())
            .collect::<Vec<_>>();
        let predecessor_mosaics = state.mosaics.clone();
        let predecessor_hippocampal = state.hippocampal;
        let predecessor_bytes = state.encode(16_000_000).unwrap();
        let cold_predecessor =
            ResidentCognitiveFormationState::decode(&predecessor_bytes, 16_000_000).unwrap();

        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| count.set(0));
        let warm = state.prepare(&joint, 16_000_000).unwrap();
        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| {
            assert_eq!(count.get(), joint.joint_source_occurrences().len());
        });
        let cold = cold_predecessor.prepare(&joint, 16_000_000).unwrap();
        assert_eq!(cold, warm);
        assert_eq!(warm.successor.cohorts.len(), 6);
        assert_eq!(warm.successor.summary().complete_neuron_count, 8);
        assert_eq!(warm.successor.next_lineage_ordinal, 9);
        assert_eq!(
            warm.successor.retained_neuron_lineages(),
            predecessor_lineages
        );
        assert_eq!(warm.successor.hippocampal, predecessor_hippocampal);
        for index in 0..2 {
            assert_eq!(
                warm.successor.cohorts[index].anatomy,
                predecessor_anatomies[index]
            );
            assert_eq!(
                warm.successor.cohorts[index].anatomy.contact_count(),
                predecessor_contacts[index]
            );
            assert_eq!(
                warm.successor.cohorts[index].state.recovery_fluid(),
                cold.successor.cohorts[index].state.recovery_fluid()
            );
        }
        assert_eq!(warm.successor.mosaics, predecessor_mosaics);

        let encoded = state.encode_successor(&warm, 16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(restored, warm.successor);
        assert_eq!(restored.encode(16_000_000).unwrap(), encoded);
        assert_eq!(restored.cohorts.len(), 6);
        assert_eq!(
            restored.cohorts[0].state.recovery_fluid(),
            warm.successor.cohorts[0].state.recovery_fluid()
        );
        assert_eq!(
            restored.cohorts[1].state.recovery_fluid(),
            warm.successor.cohorts[1].state.recovery_fluid()
        );
    }

    #[test]
    fn unsupported_ports_do_not_cancel_a_supported_receptor_or_claim_extra_neurons() {
        let source = exact_episode();
        let mut state = ResidentCognitiveFormationState::default();
        let prepared = state.prepare(&source, 16_000_000).unwrap();
        assert_eq!(prepared.observation.cognitive_ordinal, 1);
        assert_eq!(prepared.observation.complete_neuron_count, 2);
        assert_eq!(prepared.observation.physically_transitioned_neuron_count, 2);
        assert_eq!(prepared.observation.complete_neuron_fractal_count, 0);
        assert!(!prepared.observation.trace_formed);
        assert!(prepared.observation.mosaic_formed.is_none());
        state.commit(prepared).unwrap();
        let encoded = state.encode(16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(restored, state);
        assert_eq!(restored.summary().complete_neuron_count, 2);
        assert_eq!(restored.next_lineage_ordinal, 3);
        assert!(restored.dormant_lineage_seeds.is_empty());
        assert_eq!(restored.encode(16_000_000).unwrap(), encoded);
    }

    #[test]
    fn explicit_growth_dna_contacts_survive_restart_and_express_once() {
        let source = exact_four_single_optical_episode(0);
        let seed = explicit_optical_seed(&source, 1);
        let state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        let unexpressed = state.encode(16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&unexpressed, 16_000_000).unwrap();
        assert_eq!(restored, state);
        assert_eq!(restored.unexpressed_electrical_seeds.len(), 1);

        let prepared = restored.prepare(&source, 16_000_000).unwrap();
        assert_eq!(prepared.successor.unexpressed_electrical_seeds.len(), 0);
        assert_eq!(prepared.successor.cohorts.len(), 5);
        assert_eq!(prepared.successor.summary().complete_neuron_count, 8);
        assert_eq!(prepared.successor.cohorts[0].anatomy.neuron_count(), 4);
        assert_eq!(prepared.successor.cohorts[0].anatomy.contact_count(), 3);
        assert_eq!(prepared.observation.complete_neuron_fractal_count, 3);
        assert_eq!(prepared.observation.emitted_neuron_fractals.len(), 3);
        assert!(prepared.observation.mosaic_formed.is_none());

        let expressed = restored.encode_successor(&prepared, 16_000_000).unwrap();
        let cold = ResidentCognitiveFormationState::decode(&expressed, 16_000_000).unwrap();
        assert_eq!(cold, prepared.successor);
        assert_eq!(cold.cohorts[0].anatomy.contact_count(), 3);
        assert_eq!(cold.encode(16_000_000).unwrap(), expressed);
    }

    /// Contact growth on a LIVING body that already holds a retained
    /// formation: append-only, nothing about the members moves, the retained
    /// formation is untouched, and the grown body cold-restores bit-exactly.
    #[test]
    #[ignore = "retired: fixture requires Boolean/member-set mosaic admission"]
    fn authored_contact_growth_appends_without_disturbing_a_living_body() {
        let light = (0..4)
            .map(exact_four_single_optical_episode)
            .collect::<Vec<_>>();
        let dark = exact_four_dark_optical_episode();
        let seed = explicit_optical_seed(&light[0], 500);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        // First settle the complete experience, then present one proper
        // partial cue and its causal dark tail. A second complete presentation
        // is not a partial-cue reassembly and cannot be used to manufacture a
        // mosaic merely for this contact-growth test.
        for source in light
            .iter()
            .chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = state
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            state.commit(prepared).unwrap();
        }
        let partial = exact_four_partial_optical_episode();
        for source in
            std::iter::once(&partial).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = state
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            state.commit(prepared).unwrap();
        }
        assert_eq!(state.summary().mosaic_count, 1);
        let before_bytes = state.encode(16_000_000).unwrap();
        let before_mosaics = state.mosaics.clone();
        let before_neurons = state.cohorts[0].state.neurons().to_vec();
        let before_contacts = state.cohorts[0]
            .anatomy
            .contact_endpoints()
            .collect::<Vec<_>>();
        let before_phases = state.cohorts[0]
            .state
            .electrical()
            .contact_states()
            .to_vec();
        assert_eq!(before_contacts.len(), 3);

        let authored = vec![AuthoredDeclaredContact {
            left_sensor_id: "left-retina".to_owned(),
            left_substream_id: "foveal-receptor-0".to_owned(),
            right_sensor_id: "left-retina".to_owned(),
            right_substream_id: "foveal-receptor-3".to_owned(),
            conductance_picosiemens: ExactRational::integer(500),
        }];
        let grown = state
            .prepare_authored_contacts(&authored, 16_000_000)
            .unwrap();
        // Preparing publishes nothing.
        assert_eq!(state.encode(16_000_000).unwrap(), before_bytes);
        let grown_bytes = state.encode_successor(&grown, 16_000_000).unwrap();
        state.commit(grown).unwrap();

        let after_contacts = state.cohorts[0]
            .anatomy
            .contact_endpoints()
            .collect::<Vec<_>>();
        assert_eq!(after_contacts.len(), 4);
        assert_eq!(after_contacts[..3], before_contacts[..]);
        assert_eq!(after_contacts[3], (0, 3));
        assert_eq!(
            state.cohorts[0].state.electrical().contact_states()[..3],
            before_phases[..]
        );
        // Members, their physical states and the retained formation are all
        // exactly as they were: only the contact list grew.
        assert_eq!(state.cohorts[0].state.neurons(), before_neurons.as_slice());
        assert_eq!(state.cohorts[0].anatomy.neuron_count(), 4);
        assert_eq!(state.mosaics, before_mosaics);
        assert_eq!(state.summary().mosaic_count, 1);
        assert_eq!(state.observe_cohort_contacts(), vec![(4, 4)]);

        // Cold restart of the grown body is bit-exact and re-encodes identically.
        let restored = ResidentCognitiveFormationState::decode(&grown_bytes, 16_000_000).unwrap();
        assert_eq!(restored, state);
        assert_eq!(restored.encode(16_000_000).unwrap(), grown_bytes);
        // The pre-growth body still decodes to exactly what it was: no
        // receipt of any earlier generation drifted.
        let pre_growth =
            ResidentCognitiveFormationState::decode(&before_bytes, 16_000_000).unwrap();
        assert_eq!(pre_growth.encode(16_000_000).unwrap(), before_bytes);
        assert_eq!(pre_growth.observe_cohort_contacts(), vec![(4, 3)]);

        // Re-running the same authorship is refused, not silently doubled.
        assert!(matches!(
            state.prepare_authored_contacts(&authored, 16_000_000),
            Err(FormationError::PhysicalSettlementUnavailable(
                ReachedCohortError::Electrical(
                    crate::sparse_electrical_contact::SparseElectricalError::ContactAlreadyAuthored
                )
            ))
        ));
        // A receptor this organism does not declare cannot be contacted.
        let absent = vec![AuthoredDeclaredContact {
            left_sensor_id: "left-retina".to_owned(),
            left_substream_id: "foveal-receptor-0".to_owned(),
            right_sensor_id: "left-retina".to_owned(),
            right_substream_id: "foveal-receptor-9".to_owned(),
            conductance_picosiemens: ExactRational::integer(500),
        }];
        assert_eq!(
            state.prepare_authored_contacts(&absent, 16_000_000),
            Err(FormationError::AuthoredContactUnavailable)
        );
        assert_eq!(
            state.prepare_authored_contacts(&[], 16_000_000),
            Err(FormationError::AuthoredContactUnavailable)
        );
        // Every refusal left the body exactly as the growth left it.
        assert_eq!(state.encode(16_000_000).unwrap(), grown_bytes);
    }

    #[cfg(any())]
    #[test]
    fn feeding_metabolism_sustains_lessons_across_a_feed_and_rest_cycle() {
        // Served-path proof of the minimal feeding metabolism (authorized
        // 2026-08-05) on a fresh organism.  MEASURED on this four-receptor
        // body: the rest metabolism holds every dissipation ledger at zero
        // for as long as the reservoir can pay, the reservoir is a closed
        // fuel/spent pool, one lit lesson costs 376 quanta of a 2,164-quantum
        // pool, and one authored feed of the body's whole spent load restores
        // it exactly and vents its heat.
        //
        // COST RE-MEASURED 2026-08-06: 376, not the ~312 this comment carried.
        // It was stale BEFORE the exact rest-cost law of the same date and was
        // NOT moved by it — the first lesson costs 376 under both the old
        // ceil-and-discard billing and the exact carried-residue billing, and
        // the exhaustion count below is 7 under both.  On this four-receptor
        // body the lit lesson's cost is the recovery lanes undoing gate work,
        // not the membrane return; the return's overcharge only dominates on a
        // body doing more returning than seeing (measured on the LIVING body:
        // 200 dark intervals cost 1,849 fuel quanta under the old law and 28
        // under the exact one, for exactly the same 1,849 charges returned).
        let light = (0..4)
            .map(exact_four_single_optical_episode)
            .collect::<Vec<_>>();
        let dark = exact_four_dark_optical_episode();
        let seed = explicit_optical_seed(&light[0], 500);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        let mut teach = |state: &mut ResidentCognitiveFormationState| {
            for source in light.iter().chain(std::iter::repeat(&dark).take(8)) {
                let prepared = state
                    .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                    .unwrap();
                state.commit(prepared).unwrap();
            }
            state.energy_state()
        };

        let mut lessons_before_exhaustion = 0usize;
        let mut energy = teach(&mut state);
        loop {
            lessons_before_exhaustion += 1;
            // Material conservation: the reservoir is a closed fuel/spent pool.
            assert_eq!(
                energy.fuel_quanta + energy.spent_quanta,
                energy.fuel_capacity_quanta
            );
            // Every quantum of fuel burnt appears as one spent quantum AND one
            // heat quantum, because every burn drained a dissipation ledger or
            // paid for a membrane return.
            assert_eq!(energy.heat_quanta, energy.spent_quanta);
            if energy.fuel_quanta == 0 {
                break;
            }
            // Rest recovery keeps every dissipation ledger empty for as long as
            // the body can pay: the old monotone gate ratchet is closed.
            assert_eq!(energy.dissipated_quanta, 0);
            assert!(
                lessons_before_exhaustion < 40,
                "lessons never exhausted fuel"
            );
            energy = teach(&mut state);
        }
        // The exact exhaustion count changes when the neuron's physically
        // mounted positional fabric changes. What this test requires is the
        // law: the finite body eventually exhausts, never exceeds its own
        // capacity, and can regenerate exactly from its reported spent
        // material. No historical lesson count governs that physics.
        assert!(lessons_before_exhaustion > 0);
        assert!(energy.dissipated_quanta > 0);
        let exhausted_spent = energy.spent_quanta;

        // Feeding a body that cannot absorb is refused honestly.
        let mut sated = state.clone();
        let fed = sated
            .prepare_nutrition(
                AuthoredNutritionDeclaration::new(exhausted_spent).unwrap(),
                16_000_000,
            )
            .unwrap();
        assert_eq!(
            fed.observation.nutrition_regenerated_fuel_quanta,
            exhausted_spent
        );
        assert_eq!(fed.observation.nutrition_unabsorbed_waste_quanta, 0);
        assert_eq!(
            fed.observation.nutrition_vented_heat_quanta,
            exhausted_spent
        );
        sated.commit(fed).unwrap();
        let after_feed = sated.energy_state();
        assert_eq!(after_feed.fuel_quanta, after_feed.fuel_capacity_quanta);
        assert_eq!(after_feed.spent_quanta, 0);
        assert_eq!(after_feed.heat_quanta, 0);
        assert!(matches!(
            sated.prepare_nutrition(AuthoredNutritionDeclaration::new(1).unwrap(), 16_000_000,),
            Err(FormationError::NutritionUnavailable(
                MetabolicError::NothingToRegenerate
            ))
        ));

        // Over-feeding an absorbing body exports the excess as waste rather
        // than inventing capacity.
        let mut overfed = state.clone();
        let excess = exhausted_spent + 1_000;
        let prepared = overfed
            .prepare_nutrition(
                AuthoredNutritionDeclaration::new(excess).unwrap(),
                16_000_000,
            )
            .unwrap();
        assert_eq!(
            prepared.observation.nutrition_regenerated_fuel_quanta
                + prepared.observation.nutrition_unabsorbed_waste_quanta,
            excess
        );
        assert_eq!(
            prepared.observation.nutrition_unabsorbed_waste_quanta,
            1_000
        );

        // The fed body learns again: the cycle is sustainable, not a one-shot.
        let mut lessons_after_feed = 1usize;
        let mut energy = teach(&mut sated);
        while energy.fuel_quanta > 0 {
            lessons_after_feed += 1;
            assert_eq!(energy.dissipated_quanta, 0);
            assert_eq!(
                energy.fuel_quanta + energy.spent_quanta,
                energy.fuel_capacity_quanta
            );
            assert!(lessons_after_feed < 40, "fed body never exhausted fuel");
            energy = teach(&mut sated);
        }
        assert_eq!(lessons_after_feed, lessons_before_exhaustion);
    }

    #[cfg(any())]
    #[test]
    #[ignore = "retired: fixture requires Boolean/member-set mosaic admission"]
    fn four_receptor_experience_selectively_emits_four_real_fractals() {
        let light = (0..4)
            .map(exact_four_single_optical_episode)
            .collect::<Vec<_>>();
        let dark = exact_four_dark_optical_episode();
        let seed = explicit_optical_seed(&light[0], 500);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        let mut emitted = Vec::new();
        for source in light
            .iter()
            .chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = state.prepare(source, 16_000_000).unwrap();
            assert!(prepared.observation.mosaic_formed.is_none());
            assert_eq!(prepared.observation.mosaic_count, 0);
            emitted.extend(prepared.observation.emitted_neuron_fractals.clone());
            state.commit(prepared).unwrap();
        }
        let mut emitted_lineages = emitted
            .iter()
            .map(|fractal| fractal.neuron_lineage)
            .collect::<Vec<_>>();
        emitted_lineages.sort();
        emitted_lineages.dedup();
        assert_eq!(
            emitted_lineages,
            [
                local_lineage(1),
                local_lineage(2),
                local_lineage(3),
                local_lineage(4)
            ]
        );
        assert!(state.cohorts[0].pending_experience.is_none());
        assert!(state.cohorts[0].retained_experience.is_some());
        let encoded = state.encode(16_000_000).unwrap();
        let restored = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(restored, state);
        assert!(restored.cohorts[0].retained_experience.is_some());
        assert_eq!(restored.encode(16_000_000).unwrap(), encoded);

        let partial = exact_four_partial_optical_episode();
        let recurrence_sources = std::iter::once(&partial)
            .chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
            .collect::<Vec<_>>();
        let recurrence_fields = recurrence_sources
            .iter()
            .map(|source| prepare_complete_joint_field_admitted_fixture(source, 0).unwrap())
            .collect::<Vec<_>>();
        assert_eq!(restored.summary().mosaic_count, 0);
        let mut integrated = restored.clone();
        let checkpoint_before_recurrences = restored.hippocampal;
        let mut formed = Vec::new();
        RESIDENT_ACTUAL_RECURRENCE_SETTLEMENTS.with(|count| count.set(0));
        for source in &recurrence_sources {
            let prepared = integrated
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            if let Some(receipt) = prepared.observation.mosaic_formed {
                assert_eq!(prepared.observation.mosaic_count, 1);
                assert!(prepared.observation.activations.is_empty());
                assert_eq!(prepared.observation.partial_cue_reassembly_count(), 1);
                // The receipt of a newly formed mosaic is the sha256 of the
                // mosaic's OWN encoded body, not an archive address: it must
                // be reproducible from her retained formation alone.
                assert_eq!(
                    receipt,
                    sha256(
                        &encode_organism_mosaic(
                            &prepared.successor.cohorts,
                            &prepared.successor.electrical_fabric,
                            &prepared.successor.mosaics[0].mosaic,
                            16_000_000,
                        )
                        .unwrap()
                    )
                );
                formed.push(receipt);
            }
            // A recurrence commits with no publication step of any kind, and
            // the retired archive checkpoint does not move.
            assert_eq!(
                prepared.successor.hippocampal,
                checkpoint_before_recurrences
            );
            let interval_bytes = integrated.encode_successor(&prepared, 16_000_000).unwrap();
            integrated.commit(prepared).unwrap();
            integrated =
                ResidentCognitiveFormationState::decode(&interval_bytes, 16_000_000).unwrap();
            assert_eq!(integrated.encode(16_000_000).unwrap(), interval_bytes);
        }
        RESIDENT_ACTUAL_RECURRENCE_SETTLEMENTS.with(|count| {
            let available_gates = recurrence_fields
                .iter()
                .map(|field| field.result().gates.len())
                .sum::<usize>();
            // Candidate recurrence ends at physical mosaic admission. Later
            // dark gates return to ordinary living settlement; they must not
            // remain trapped in the just-completed candidate path.
            assert!(count.get() > 0);
            assert!(count.get() < available_gates);
        });
        assert_eq!(formed.len(), 1);
        assert_eq!(integrated.summary().mosaic_count, 1);
        assert_eq!(integrated.mosaics.len(), 1);
        assert!(integrated.cohorts[0].pending_recurrence.is_none());
        let integrated_bytes = integrated.encode(16_000_000).unwrap();
        let cold_integrated =
            ResidentCognitiveFormationState::decode(&integrated_bytes, 16_000_000).unwrap();
        assert_eq!(cold_integrated, integrated);
        // A full learn-and-recognize cycle left the retired checkpoint exactly
        // where it started: no episode, no posting, no radix path copy, no
        // address of any kind was produced by admitting a real mosaic.
        assert_eq!(cold_integrated.hippocampal, checkpoint_before_recurrences);
        assert!(!cold_integrated
            .hippocampal
            .carries_retired_archive_reference());

        let five_receptor_occurrence = exact_five_optical_episode();
        let predecessor_anatomy = integrated.cohorts[0].anatomy.clone();
        let predecessor_lineages = integrated.retained_neuron_lineages();
        let predecessor_mosaics = integrated.mosaics.clone();
        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| count.set(0));
        let warm_growth = integrated
            .prepare_admitted_transition(
                &admitted_fixture_episode(&five_receptor_occurrence),
                16_000_000,
            )
            .unwrap();
        RESIDENT_JOINT_FIELD_EVALUATIONS.with(|count| {
            assert_eq!(
                count.get(),
                five_receptor_occurrence.joint_source_occurrences().len()
            );
        });
        let cold_growth = cold_integrated
            .prepare_admitted_transition(
                &admitted_fixture_episode(&five_receptor_occurrence),
                16_000_000,
            )
            .unwrap();
        assert_eq!(cold_growth, warm_growth);
        assert_eq!(warm_growth.successor.cohorts.len(), 1);
        assert_eq!(warm_growth.successor.summary().complete_neuron_count, 5);
        assert_eq!(warm_growth.successor.next_lineage_ordinal, 6);
        for (successor, predecessor) in warm_growth.successor.cohorts[0]
            .anatomy
            .neuron_anatomies()
            .iter()
            .zip(predecessor_anatomy.neuron_anatomies())
        {
            assert_eq!(successor.capacitance(), predecessor.capacitance());
            assert!(successor.mathloom_positions() >= predecessor.mathloom_positions());
        }
        assert_eq!(
            &warm_growth.successor.cohorts[0].anatomy.source_sites()[..4],
            predecessor_anatomy.source_sites()
        );
        assert_eq!(
            &warm_growth.successor.cohorts[0].anatomy.neuron_lineages()[..4],
            predecessor_lineages
        );
        assert_eq!(
            warm_growth.successor.cohorts[0].anatomy.neuron_lineages()[4],
            local_lineage(5)
        );
        assert_eq!(
            warm_growth.successor.retained_neuron_lineages()[4],
            local_lineage(5)
        );
        let successor_lineages = warm_growth.successor.retained_neuron_lineages();
        assert!(successor_lineages
            .iter()
            .enumerate()
            .all(|(index, lineage)| { !successor_lineages[..index].contains(lineage) }));
        assert_eq!(warm_growth.successor.mosaics, predecessor_mosaics);
        let mut extended = integrated.clone();
        let extended_bytes = extended.encode_successor(&warm_growth, 16_000_000).unwrap();
        extended.commit(warm_growth).unwrap();
        let cold_extended =
            ResidentCognitiveFormationState::decode(&extended_bytes, 16_000_000).unwrap();
        assert_eq!(cold_extended, extended);
        assert_eq!(cold_extended.encode(16_000_000).unwrap(), extended_bytes);
        assert_eq!(cold_extended.summary().complete_neuron_count, 5);
        assert_eq!(cold_extended.summary().mosaic_count, 1);
        assert_eq!(cold_extended.hippocampal, checkpoint_before_recurrences);

        // The first learn-and-recognize cycle used the body's finite recovery
        // reservoir completely.  An unfed control therefore cannot drive a
        // second whole-formation recurrence: exhausted material is a physical
        // unavailability, not a recall defect to bypass with a controller.
        assert_eq!(integrated.energy_state().fuel_quanta, 0);
        let mut exhausted = integrated.clone();
        let later_cue = exact_four_single_optical_episode(1);
        let mut exhausted_reassemblies = 0usize;
        for source in
            std::iter::once(&later_cue).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = exhausted
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            exhausted_reassemblies += prepared.observation.partial_cue_reassembly_count;
            exhausted.commit(prepared).unwrap();
        }
        // Incoming light carries its own physical energy. A metabolically
        // exhausted body may therefore still complete a bounded number of
        // already-yielded receptor transitions using free local dissipation
        // capacity; exhaustion must stop that sequence without a controller.
        assert!(exhausted_reassemblies > 0);
        let exhausted_checkpoint = exhausted.clone();
        let mut later_reassemblies = 0usize;
        for source in
            std::iter::once(&later_cue).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = exhausted
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            later_reassemblies += prepared.observation.partial_cue_reassembly_count;
            exhausted.commit(prepared).unwrap();
        }
        assert_eq!(later_reassemblies, 0);
        assert_ne!(exhausted, exhausted_checkpoint);

        // Restore exactly the material the same body reports as spent, then
        // supply the declared dark causal intervals in which its existing
        // recovery physics can act.  No recall threshold, timeout, scheduler,
        // or semantic rule participates.  Recovery itself lawfully provides
        // an internal partial cue, and a later external partial cue also
        // reassembles the one retained distributed formation.
        let mut progressive = integrated.clone();
        let spent = progressive.energy_state().spent_quanta;
        let nutrition = progressive
            .prepare_nutrition(
                AuthoredNutritionDeclaration::new(spent).unwrap(),
                16_000_000,
            )
            .unwrap();
        assert_eq!(
            nutrition.observation.nutrition_regenerated_fuel_quanta,
            spent
        );
        progressive.commit(nutrition).unwrap();
        let mut reassembly_events = 0usize;
        let mut endogenous_reassembly_events = 0usize;
        for _ in 0..DARK_TAIL_EPISODES {
            let prepared = progressive
                .prepare_admitted_transition(&admitted_fixture_episode(&dark), 16_000_000)
                .unwrap();
            reassembly_events += prepared.observation.partial_cue_reassembly_count;
            endogenous_reassembly_events +=
                prepared.observation.endogenous_partial_cue_reassembly_count;
            progressive.commit(prepared).unwrap();
        }
        assert!(endogenous_reassembly_events > 0);
        let reassemblies_before_external_cue = reassembly_events;
        for source in
            std::iter::once(&later_cue).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = progressive
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            reassembly_events += prepared.observation.partial_cue_reassembly_count;
            let successor = progressive.encode_successor(&prepared, 16_000_000).unwrap();
            progressive.commit(prepared).unwrap();
            progressive = ResidentCognitiveFormationState::decode(&successor, 16_000_000).unwrap();
        }
        assert!(reassembly_events > reassemblies_before_external_cue);
        assert_eq!(progressive.summary().mosaic_count, 1);
        assert_eq!(progressive.mosaics[0].mosaic_of_mosaics_relation_count, 0);
        assert_eq!(progressive.mosaic_of_mosaics_count().unwrap(), 0);
        assert_eq!(progressive.hippocampal, checkpoint_before_recurrences);

        // The five tamper assertions that stood here checked that a corrupted
        // ARCHIVED EPISODE RECORD failed to validate (damaged source body,
        // damaged mosaic body, trailing bytes on either evidence body, a
        // mismatched participant lineage).  They validated the record, not
        // Guala, and they left with the record.  What still guards her here is
        // the truncation assertion immediately below plus the round-trip law
        // in `decode`, which every restore runs on her real body.
        assert_eq!(cold_integrated.summary().mosaic_count, 1);
        assert!(ResidentCognitiveFormationState::decode(
            &integrated_bytes[..integrated_bytes.len() - 1],
            16_000_000,
        )
        .is_err());
        let mut duplicate = integrated.clone();
        duplicate.mosaics =
            vec![duplicate.mosaics[0].clone(), duplicate.mosaics[0].clone()].into_boxed_slice();
        assert!(matches!(
            duplicate.encode(16_000_000),
            Err(FormationError::NoncanonicalState)
        ));

        let retained = restored.cohorts[0].retained_experience.as_ref().unwrap();
        let predecessor_replacements = retained
            .retained_members()
            .unwrap()
            .iter()
            .map(|member| (member.neuron_index, member.predecessor.clone()))
            .collect::<Vec<_>>();
        let mut unlearned = ResidentCognitiveFormationState {
            generation: restored.generation,
            next_lineage_ordinal: restored.next_lineage_ordinal,
            unexpressed_electrical_seeds: Box::new([]),
            dormant_lineage_seeds: Box::new([]),
            resting_population: None,
            cohorts: vec![ResidentReachedCohort {
                anatomy: restored.cohorts[0].anatomy.clone(),
                state: Arc::new(
                    restored.cohorts[0]
                        .state
                        .with_replaced_neurons(&predecessor_replacements)
                        .unwrap(),
                ),
                pending_experience: None,
                retained_experience: None,
                pending_recurrence: None,
            }]
            .into_boxed_slice(),
            electrical_fabric: ResidentElectricalFabric::default(),
            active_electrical_frontier: Box::new([]),
            preceding_active_electrical_frontier: Box::new([]),
            older_active_electrical_frontier: Box::new([]),
            mosaics: Box::new([]),
            hippocampal: ResidentHippocampalIndex::default(),
        };
        for source in &recurrence_sources {
            let prepared = unlearned.prepare(source, 16_000_000).unwrap();
            assert!(prepared.observation.mosaic_formed.is_none());
            assert_eq!(prepared.observation.mosaic_count, 0);
            unlearned.commit(prepared).unwrap();
        }
        assert_eq!(unlearned.summary().mosaic_count, 0);
    }

    fn structural_test_lineage(value: u8) -> [u8; 16] {
        let mut lineage = [0u8; 16];
        lineage[15] = value;
        lineage
    }

    #[test]
    fn one_transition_exports_one_composed_fractal_per_neuron() {
        let delta = |gate_negative: bool, gate_magnitude: u128, plastic: i128| {
            let mut entries = vec![PhysicalStateDeltaEntry::new(
                crate::complete_neuron::PhysicalStateCoordinate::GateOpenPopulation,
                ExactPhysicalStateDelta::Integral(
                    ExactSignedDelta::from_parts(gate_negative, gate_magnitude).unwrap(),
                ),
            )
            .unwrap()];
            if plastic != 0 {
                entries.push(
                    PhysicalStateDeltaEntry::new(
                        crate::complete_neuron::PhysicalStateCoordinate::PlasticRestLength,
                        ExactPhysicalStateDelta::Rational(
                            ExactRational::new(plastic, 3).unwrap(),
                        ),
                    )
                    .unwrap(),
                );
            }
            SparsePhysicalStateDelta::from_canonical_entries(entries).unwrap()
        };
        let first = structural_test_lineage(1);
        let second = structural_test_lineage(2);
        let coalesced = coalesce_emitted_neuron_fractals(vec![
            EmittedNeuronFractal {
                neuron_lineage: first,
                delta: delta(false, 2, 1),
            },
            EmittedNeuronFractal {
                neuron_lineage: second,
                delta: delta(false, 4, 0),
            },
            EmittedNeuronFractal {
                neuron_lineage: first,
                delta: delta(true, 1, -1),
            },
        ])
        .unwrap();

        assert_eq!(coalesced.len(), 2);
        assert_eq!(coalesced[0].neuron_lineage, first);
        assert_eq!(coalesced[0].delta.entries().len(), 1);
        assert_eq!(
            coalesced[0].delta.exact_delta(
                crate::complete_neuron::PhysicalStateCoordinate::GateOpenPopulation,
            ),
            Some(ExactPhysicalStateDelta::Integral(
                ExactSignedDelta::from_parts(false, 1).unwrap(),
            ))
        );
        assert_eq!(coalesced[1].neuron_lineage, second);
    }

    /// Synthesize an admitted mosaic with explicit member and active-bond
    /// structure for the R1 boundary tests.  `members` must be strictly
    /// ascending; bonds are canonicalized exactly as admission does.
    fn synthetic_admitted_mosaic(
        members: &[u8],
        active_bonds: &[(u8, u8)],
        cue: u8,
    ) -> AdmittedPhysicalMosaic {
        let fractal =
            crate::complete_neuron::SparsePhysicalStateDelta::from_canonical_entries(vec![
                crate::complete_neuron::PhysicalStateDeltaEntry::new(
                    crate::complete_neuron::PhysicalStateCoordinate::PlasticRestLength,
                    crate::complete_neuron::ExactPhysicalStateDelta::Rational(
                        crate::exact_rational::ExactRational::new(1, 3).unwrap(),
                    ),
                )
                .unwrap(),
            ])
            .unwrap();
        let bond = |left: u8, right: u8| {
            crate::physical_mosaic::StablePhysicalBondReference::new(
                structural_test_lineage(left),
                structural_test_lineage(right),
                0,
            )
            .unwrap()
        };
        let mut original_bonds = members
            .windows(2)
            .map(|pair| bond(pair[0], pair[1]))
            .collect::<Vec<_>>();
        original_bonds.sort_unstable();
        let mut recurrence_bonds = active_bonds
            .iter()
            .map(|(left, right)| bond(*left, *right))
            .collect::<Vec<_>>();
        recurrence_bonds.sort_unstable();
        AdmittedPhysicalMosaic::from_parts_for_tests(
            members
                .iter()
                .map(|value| structural_test_lineage(*value))
                .collect(),
            vec![fractal; members.len()],
            original_bonds,
            recurrence_bonds,
            vec![structural_test_lineage(cue)],
        )
    }

    #[test]
    fn legacy_transient_mosaic_is_not_cognitive_authority() {
        let valid = synthetic_admitted_mosaic(&[1, 2, 3], &[(1, 2), (2, 3)], 1);
        let transient =
            crate::complete_neuron::SparsePhysicalStateDelta::from_canonical_entries(vec![
                crate::complete_neuron::PhysicalStateDeltaEntry::new(
                    crate::complete_neuron::PhysicalStateCoordinate::MembraneSeparatedCharge,
                    crate::complete_neuron::ExactPhysicalStateDelta::Integral(
                        crate::complete_neuron::ExactSignedDelta::from_parts(false, 1).unwrap(),
                    ),
                )
                .unwrap(),
            ])
            .unwrap();
        let invalid = AdmittedPhysicalMosaic::from_parts_for_tests(
            valid.member_lineages().to_vec(),
            vec![transient; valid.member_lineages().len()],
            valid.original_bonds().to_vec(),
            valid.recurrence_bonds().to_vec(),
            valid.partial_cue_lineages().to_vec(),
        );
        assert!(!invalid.carries_only_retained_neuron_structure());
        assert!(valid.carries_only_retained_neuron_structure());
        let mut transient_only = [RetainedOrganismMosaic::newly_admitted(invalid.clone())];
        resolve_unpersisted_recurrent_retention(
            &[],
            &ResidentElectricalFabric::default(),
            &mut transient_only,
        )
        .unwrap();
        assert_eq!(transient_only[0].recurrent_lineage, None);

        let mut state = ResidentCognitiveFormationState::default();
        state.mosaics = vec![
            RetainedOrganismMosaic::newly_admitted(invalid),
            RetainedOrganismMosaic::newly_admitted(valid),
        ]
        .into_boxed_slice();
        assert_eq!(state.summary().mosaic_count, 1);
        assert_eq!(state.observe_retained_formation_members().len(), 1);
        assert_eq!(state.mosaic_of_mosaics_count().unwrap(), 0);
    }

    /// An equality resolution is observational only. It cannot alter retained
    /// physical state or increment a lifetime counter.
    #[test]
    fn same_members_without_new_active_bonds_reinforce_the_retained_reference() {
        let reference = synthetic_admitted_mosaic(&[1, 2, 3], &[(1, 2), (2, 3)], 1);
        let mut mosaics = vec![RetainedOrganismMosaic::newly_admitted(reference.clone())];
        // A different cue over a strict subset of the active bonds is still
        // the same retained structure.
        let subset = synthetic_admitted_mosaic(&[1, 2, 3], &[(1, 2)], 2);
        let resolution = resolve_mosaic_structural_identity(&mosaics, subset);
        assert_eq!(
            resolution,
            MosaicStructuralResolution::Reinforces { mosaic_index: 0 }
        );
        apply_mosaic_structural_resolution(&mut mosaics, resolution).unwrap();
        let identical = resolve_mosaic_structural_identity(&mosaics, reference.clone());
        assert_eq!(
            identical,
            MosaicStructuralResolution::Reinforces { mosaic_index: 0 }
        );
        apply_mosaic_structural_resolution(&mut mosaics, identical).unwrap();
        assert_eq!(mosaics.len(), 1);
        assert_eq!(mosaics[0].mosaic, reference);
        assert_eq!(mosaics[0].reinforcement_count, 0);
        assert_eq!(mosaics[0].mosaic_of_mosaics_relation_count, 0);
    }

    /// The same neuron membership does not define identity.  A distinct exact
    /// retained neuronal structure is a distinct formation even when every
    /// member lineage is shared.
    #[test]
    fn same_members_with_distinct_retained_structure_admit_distinct_formation() {
        let reference = synthetic_admitted_mosaic(&[1, 2, 3], &[(1, 2), (2, 3)], 1);
        let mut mosaics = vec![RetainedOrganismMosaic {
            mosaic: reference.clone(),
            recurrent_lineage: None,
            reinforcement_count: 5,
            mosaic_of_mosaics_relation_count: 1,
        }];
        let mut distinct = synthetic_admitted_mosaic(&[1, 2, 3], &[(1, 3), (2, 3)], 3);
        let changed =
            crate::complete_neuron::SparsePhysicalStateDelta::from_canonical_entries(vec![
                crate::complete_neuron::PhysicalStateDeltaEntry::new(
                    crate::complete_neuron::PhysicalStateCoordinate::PlasticRestLength,
                    crate::complete_neuron::ExactPhysicalStateDelta::Rational(
                        crate::exact_rational::ExactRational::new(2, 3).unwrap(),
                    ),
                )
                .unwrap(),
            ])
            .unwrap();
        distinct = AdmittedPhysicalMosaic::from_parts_for_tests(
            distinct.member_lineages().to_vec(),
            vec![changed; distinct.member_lineages().len()],
            distinct.original_bonds().to_vec(),
            distinct.recurrence_bonds().to_vec(),
            distinct.partial_cue_lineages().to_vec(),
        );
        let resolution = resolve_mosaic_structural_identity(&mosaics, distinct.clone());
        assert_eq!(
            resolution,
            MosaicStructuralResolution::NewFormation(distinct.clone())
        );
        apply_mosaic_structural_resolution(&mut mosaics, resolution).unwrap();
        assert_eq!(mosaics.len(), 2);
        assert_eq!(mosaics[0].mosaic, reference);
        assert_eq!(mosaics[1].mosaic, distinct);
        assert_eq!(mosaics[0].reinforcement_count, 5);
        assert_eq!(mosaics[0].mosaic_of_mosaics_relation_count, 1);
    }

    /// Overlap alone is not a learned relation and cannot suppress a distinct
    /// retained formation.
    #[test]
    fn overlapping_member_sets_retain_each_distinct_formation() {
        let first = synthetic_admitted_mosaic(&[1, 2, 3], &[(1, 2), (2, 3)], 1);
        let second = synthetic_admitted_mosaic(&[7, 8, 9], &[(7, 8), (8, 9)], 7);
        let mut mosaics = vec![
            RetainedOrganismMosaic::newly_admitted(first),
            RetainedOrganismMosaic::newly_admitted(second),
        ];
        let overlapping = synthetic_admitted_mosaic(&[3, 4, 7], &[(3, 4), (4, 7)], 4);
        let resolution = resolve_mosaic_structural_identity(&mosaics, overlapping);
        assert!(matches!(
            resolution,
            MosaicStructuralResolution::NewFormation(_)
        ));
        apply_mosaic_structural_resolution(&mut mosaics, resolution).unwrap();
        assert_eq!(mosaics.len(), 3);
        assert_eq!(mosaics[0].mosaic_of_mosaics_relation_count, 0);
        assert_eq!(mosaics[1].mosaic_of_mosaics_relation_count, 0);
        assert_eq!(mosaics[0].reinforcement_count, 0);
        assert_eq!(mosaics[1].reinforcement_count, 0);
    }

    /// R1 disjoint branch: a member set disjoint from every retained
    /// formation is a genuinely new mosaic — the pre-law behavior, with both
    /// counts at the historical default of zero.
    #[test]
    fn disjoint_member_sets_admit_a_genuinely_new_mosaic() {
        let first = synthetic_admitted_mosaic(&[1, 2, 3], &[(1, 2), (2, 3)], 1);
        let mut mosaics = vec![RetainedOrganismMosaic::newly_admitted(first)];
        let disjoint = synthetic_admitted_mosaic(&[4, 5, 6], &[(4, 5), (5, 6)], 4);
        let resolution = resolve_mosaic_structural_identity(&mosaics, disjoint.clone());
        assert_eq!(
            resolution,
            MosaicStructuralResolution::NewFormation(disjoint.clone())
        );
        apply_mosaic_structural_resolution(&mut mosaics, resolution).unwrap();
        assert_eq!(mosaics.len(), 2);
        assert_eq!(mosaics[1].mosaic, disjoint);
        assert_eq!(mosaics[1].reinforcement_count, 0);
        assert_eq!(mosaics[1].mosaic_of_mosaics_relation_count, 0);
    }

    /// R3 codec: reinforcement/relation counts persist through the organism
    /// state body under the `GLMRC01` wrapper, while zero-count references
    /// keep the bare pre-law encoding byte-identically (GLEXP02/GLEXP03
    /// precedent: the new magic appears only when the retained state differs
    /// from the historical default).
    #[test]
    #[ignore = "retired: fixture requires Boolean/member-set mosaic admission"]
    fn reinforcement_counts_round_trip_and_zero_counts_keep_pre_law_bytes() {
        let light = (0..4)
            .map(exact_four_single_optical_episode)
            .collect::<Vec<_>>();
        let dark = exact_four_dark_optical_episode();
        let seed = explicit_optical_seed(&light[0], 500);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        for source in light
            .iter()
            .chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = state.prepare(source, 16_000_000).unwrap();
            state.commit(prepared).unwrap();
        }
        let partial = exact_four_partial_optical_episode();
        for source in
            std::iter::once(&partial).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = state
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            state.commit(prepared).unwrap();
        }
        assert_eq!(state.summary().mosaic_count, 1);
        assert_eq!(state.mosaics[0].reinforcement_count, 0);

        // Zero counts: the encoded body carries the counts wrapper nowhere,
        // so every pre-law receipt stays byte-identical.
        let bare = state.encode(16_000_000).unwrap();
        assert!(!bare
            .windows(RETAINED_MOSAIC_COUNTS_MAGIC.len())
            .any(|window| window == RETAINED_MOSAIC_COUNTS_MAGIC));

        // Nonzero counts round-trip exactly and re-encode canonically.
        state.mosaics[0].reinforcement_count = 3;
        state.mosaics[0].mosaic_of_mosaics_relation_count = 2;
        let counted = state.encode(16_000_000).unwrap();
        assert!(counted
            .windows(RETAINED_MOSAIC_COUNTS_MAGIC.len())
            .any(|window| window == RETAINED_MOSAIC_COUNTS_MAGIC));
        let restored = ResidentCognitiveFormationState::decode(&counted, 16_000_000).unwrap();
        assert_eq!(restored, state);
        assert_eq!(restored.mosaics[0].reinforcement_count, 3);
        assert_eq!(restored.mosaics[0].mosaic_of_mosaics_relation_count, 2);
        assert_eq!(restored.mosaic_of_mosaics_count().unwrap(), 2);
        assert_eq!(restored.encode(16_000_000).unwrap(), counted);

        // A wrapper claiming zero counts is refused: its canonical form is
        // the bare body, and one retained state never admits two encodings.
        let body = encode_organism_mosaic(
            &state.cohorts,
            &state.electrical_fabric,
            &state.mosaics[0].mosaic,
            16_000_000,
        )
        .unwrap();
        let mut zero_wrapped = Vec::new();
        zero_wrapped.extend_from_slice(RETAINED_MOSAIC_COUNTS_MAGIC);
        zero_wrapped.extend_from_slice(&0u64.to_le_bytes());
        zero_wrapped.extend_from_slice(&0u64.to_le_bytes());
        zero_wrapped.extend_from_slice(&body);
        assert!(matches!(
            decode_retained_organism_mosaic(
                &state.cohorts,
                &state.electrical_fabric,
                &zero_wrapped,
                16_000_000,
            ),
            Err(FormationError::NoncanonicalState)
        ));
    }

    #[test]
    fn exact_optical_occurrence_physically_changes_the_resident_cell() {
        let source = exact_optical_episode();
        let genesis = ResidentCognitiveFormationState::default();
        let genesis_bytes = genesis.encode(16_000_000).unwrap();
        let prepared = genesis.prepare(&source, 16_000_000).unwrap();
        assert_eq!(prepared.observation.complete_neuron_count, 2);
        assert_eq!(prepared.observation.physically_transitioned_neuron_count, 2);
        assert_eq!(prepared.observation.complete_neuron_fractal_count, 0);
        assert_eq!(
            prepared.observation.complete_neuron_fractal_count,
            prepared.observation.emitted_neuron_fractals.len()
        );
        assert_eq!(prepared.successor.electrical_fabric.contact_count(), 1);
        assert!(prepared.successor.cohorts.iter().any(|cohort| {
            cohort
                .anatomy
                .mounts()
                .iter()
                .any(|mount| mount.place() == DeclaredNeuronPlace::new(6, 0))
        }));
        assert!(prepared.observation.emitted_neuron_fractals.is_empty());
        let successor_bytes = genesis.encode_successor(&prepared, 16_000_000).unwrap();
        assert_ne!(successor_bytes, genesis_bytes);
        let restored =
            ResidentCognitiveFormationState::decode(&successor_bytes, 16_000_000).unwrap();
        assert_eq!(restored.encode(16_000_000).unwrap(), successor_bytes);
    }

    #[test]
    fn neuron_local_quiescence_closes_the_neuronal_fractal() {
        // The lit occurrence creates retained physical change but cannot also
        // certify its own post-experience quiescence. The next exact local
        // quiescent interval emits each lineage's sparse retained delta once.
        // A single receptor cell can never satisfy the three-connected-member
        // participation law, so no mosaic is retained.
        let light = exact_optical_episode();
        let dark = exact_dark_optical_episode();
        let mut state = ResidentCognitiveFormationState::default();
        let light_transition = state.prepare(&light, 16_000_000).unwrap();
        assert_eq!(
            light_transition.observation.complete_neuron_fractal_count,
            0
        );
        assert!(light_transition
            .observation
            .emitted_neuron_fractals
            .is_empty());
        state.commit(light_transition).unwrap();

        let mid_experience_bytes = state.encode(16_000_000).unwrap();
        let mut restored =
            ResidentCognitiveFormationState::decode(&mid_experience_bytes, 16_000_000).unwrap();
        assert_eq!(restored, state);

        let mut emitted_after_occurrence = Vec::new();
        for _ in 0..DARK_TAIL_EPISODES {
            let prepared = restored.prepare(&dark, 16_000_000).unwrap();
            emitted_after_occurrence.extend(prepared.observation.emitted_neuron_fractals.clone());
            restored.commit(prepared).unwrap();
        }
        assert_eq!(emitted_after_occurrence.len(), 2);
        assert!(emitted_after_occurrence
            .iter()
            .all(|fractal| !fractal.delta.entries().is_empty()));
        // Participation retention: one changed member is fewer than the
        // admission law's three-connected-member floor, so no mosaic is
        // retained. Its real neuronal impression remains as the one bounded
        // pending experience; the mosaic minimum is not an erasure rule.
        assert!(restored.cohorts[0].retained_experience.is_none());
        assert!(restored.cohorts[0].pending_experience.is_some());

        // The post-quiescence emission is one-shot: unchanged retained state
        // does not reopen the experience or emit a duplicate.
        let later_dark = restored.prepare(&dark, 16_000_000).unwrap();
        assert_eq!(later_dark.observation.complete_neuron_fractal_count, 0);
    }

    #[test]
    fn continued_identical_light_emits_each_retained_physical_change() {
        // Continued photons do not authorize an occurrence-boundary receipt.
        // A lineage emits only when its retained coordinates hold unchanged
        // for one later exact causal interval.
        let light = exact_optical_episode();
        let mut state = ResidentCognitiveFormationState::default();
        let first = state.prepare(&light, 16_000_000).unwrap();
        assert_eq!(first.observation.complete_neuron_fractal_count, 0);
        assert!(first.observation.emitted_neuron_fractals.is_empty());
        state.commit(first).unwrap();

        let mut emitted = Vec::new();
        for _ in 0..DARK_TAIL_EPISODES {
            let prepared = state.prepare(&light, 16_000_000).unwrap();
            emitted.extend(prepared.observation.emitted_neuron_fractals.clone());
            state.commit(prepared).unwrap();
            if !emitted.is_empty() {
                break;
            }
        }
        assert!(emitted
            .iter()
            .all(|fractal| !fractal.delta.entries().is_empty()));
        assert!(!emitted.is_empty());
        assert!(state.cohorts[0].pending_experience.is_some());
        assert!(state.cohorts[0].retained_experience.is_none());
    }

    #[test]
    fn experienced_neurons_emit_one_new_bounded_fractal_after_later_quiescence() {
        let light = exact_four_single_optical_episode(0);
        let dark = exact_four_dark_optical_episode();
        let seed = explicit_optical_seed(&light, 1);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();

        let first = state.prepare(&light, 16_000_000).unwrap();
        assert_eq!(first.observation.emitted_neuron_fractals.len(), 3);
        state.commit(first).unwrap();

        // Preserve the first exact settled experience as prior cognitive
        // state. The current wire format already has independent retained and
        // pending carriers; no schema or compatibility authority is added.
        let mut retained = state.cohorts[0].pending_experience.take().unwrap();
        let retained_members = retained
            .pending_members()
            .unwrap()
            .iter()
            .filter(|member| member.settled)
            .filter_map(|member| {
                let learned = &state.cohorts[0].state.neurons()[member.neuron_index];
                sparse_retained_physical_state_delta(&member.predecessor, learned)
                    .unwrap()
                    .map(|delta| SparseRetainedExperienceMember {
                        neuron_index: member.neuron_index,
                        predecessor: member.predecessor.clone(),
                        learned: learned.clone(),
                        delta,
                    })
            })
            .collect::<Vec<_>>();
        retained.retained_change_neurons.fill(false);
        retained.retentively_settled_neurons.fill(false);
        for member in &retained_members {
            retained.retained_change_neurons[member.neuron_index] = true;
            retained.retentively_settled_neurons[member.neuron_index] = true;
        }
        retained.physical =
            ResidentExperiencePhysicalEvidence::Retained(retained_members.into_boxed_slice());
        retained.local_relaxation_observed = true;
        state.cohorts[0].retained_experience = Some(retained);
        let prior_retained = state.cohorts[0].retained_experience.clone();

        let prior_bytes = state.encode(16_000_000).unwrap();
        state = ResidentCognitiveFormationState::decode(&prior_bytes, 16_000_000).unwrap();
        assert_eq!(state.encode(16_000_000).unwrap(), prior_bytes);

        let later_occurrence = state.prepare(&light, 16_000_000).unwrap();
        assert!(later_occurrence.successor.cohorts[0]
            .retained_experience
            .is_some());
        state.commit(later_occurrence).unwrap();
        assert!(state.cohorts[0].pending_experience.is_some());

        // Simultaneous prior-retained plus current-pending evidence must cold
        // restore byte-exactly; otherwise production restart would erase the
        // currently forming experience.
        let mid_bytes = state.encode(16_000_000).unwrap();
        state = ResidentCognitiveFormationState::decode(&mid_bytes, 16_000_000).unwrap();
        assert_eq!(state.encode(16_000_000).unwrap(), mid_bytes);

        let mut later_emitted = Vec::new();
        for _ in 0..DARK_TAIL_EPISODES {
            let prepared = state.prepare(&dark, 16_000_000).unwrap();
            later_emitted.extend(prepared.observation.emitted_neuron_fractals.clone());
            state.commit(prepared).unwrap();
            if !later_emitted.is_empty() {
                break;
            }
        }
        assert!(!later_emitted.is_empty());
        assert!(later_emitted
            .iter()
            .all(|fractal| !fractal.delta.entries().is_empty()));
        assert_eq!(state.cohorts[0].retained_experience, prior_retained);
        assert!(state.cohorts[0].pending_experience.is_none());

        let later_dark = state.prepare(&dark, 16_000_000).unwrap();
        assert!(later_dark.observation.emitted_neuron_fractals.is_empty());
    }

    #[test]
    fn typed_vestibular_source_persists_one_specialized_neuron_then_emits_after_quiescence() {
        let canal_anatomy =
            CanalAnatomy::new(6, 13_200, PositiveRatio::new(25, 1).unwrap()).unwrap();
        let bundle_anatomy = LocalCupulaBundleAnatomy::new(2, 5, 20_000).unwrap();
        let receptor_anatomy = phase_one_virtual_vestibular_anatomy().unwrap();
        let predecessor_body = YawBodyState::new(0).unwrap();
        let body = settle_signed_yaw_actuation(
            predecessor_body,
            SignedYawActuation::new(360, WORLD_MECHANICAL_TICK_MICROSECONDS).unwrap(),
        )
        .unwrap();
        let reached = settle_reached_vestibular_bundle_tick(
            canal_anatomy,
            CanalState::at_rest(),
            body.trajectory.as_slice()[0],
            bundle_anatomy,
        )
        .unwrap();
        let mut canal = reached.successor_canal;
        let resting_body = body.successor;
        let ingress = prepare_resident_vestibular_ingress(
            0,
            predecessor_body,
            body.successor,
            reached,
            &receptor_anatomy,
        )
        .unwrap();
        let retired = ResidentCognitiveFormationState::default()
            .encode_with_format(CognitiveCodecFormat::V12, 16_000_000)
            .unwrap();
        let current =
            ResidentCognitiveFormationState::migrate_to_current_format(&retired, 16_000_000)
                .unwrap();
        let mut state = ResidentCognitiveFormationState::decode(&current, 16_000_000).unwrap();
        let site = NeuronSourceSite::from_source_port(
            &ingress
                .source()
                .joint_source_with_contacts()
                .0
                .joint_source_ports()[0],
        )
        .unwrap();
        let place = DeclaredNeuronPlace::from_source_site(&site);
        let population = state.resting_population.as_ref().unwrap();
        let resting = population
            .materialize(population.population_offset(place).unwrap())
            .unwrap();
        let expected_lineage = local_lineage_from_ordinal(resting.lineage_ordinal).unwrap();
        let predecessor_resting_count = population.resting_cell_count();
        let predecessor_total_neurons = state.summary().complete_neuron_count
            + usize::try_from(predecessor_resting_count).unwrap();
        let stimulating = state
            .prepare_vestibular_transition(&ingress, 16_000_000)
            .unwrap();
        assert_eq!(stimulating.observation.complete_neuron_count, 3);
        assert_eq!(
            stimulating.observation.physically_transitioned_neuron_count,
            3
        );
        assert!(stimulating.observation.emitted_neuron_fractals.is_empty());
        state.commit(stimulating).unwrap();
        assert_eq!(
            state
                .resting_population
                .as_ref()
                .unwrap()
                .resting_cell_count(),
            predecessor_resting_count - 3
        );
        assert_eq!(state.cohorts.len(), 3);
        assert_eq!(state.cohorts[0].anatomy.neuron_count(), 1);
        assert_eq!(
            state.summary().complete_neuron_count
                + usize::try_from(
                    state
                        .resting_population
                        .as_ref()
                        .unwrap()
                        .resting_cell_count(),
                )
                .unwrap(),
            predecessor_total_neurons
        );
        assert_eq!(
            state.cohorts[0].anatomy.neuron_lineages()[0],
            expected_lineage
        );
        assert_eq!(
            state.cohorts[0].anatomy.neuron_anatomies()[0].capacitance(),
            resting.anatomy.capacitance()
        );
        assert_eq!(
            state.cohorts[0].anatomy.neuron_anatomies()[0].gate_dissipation_capacity_quanta(),
            receptor_anatomy.gate_dissipation_capacity_quanta()
        );
        let layers = state
            .cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.mounts())
            .map(|mount| mount.place().layer())
            .collect::<Vec<_>>();
        assert!(layers.contains(&5));
        assert!(layers.contains(&6));
        assert!(layers.contains(&8));

        let encoded = state.encode(16_000_000).unwrap();
        state = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        let lineage = state.cohorts[0].anatomy.neuron_lineages()[0];
        let mut emitted = Vec::new();
        for source_tick in 1..=(DARK_TAIL_EPISODES * 4) {
            let reached =
                settle_reached_vestibular_bundle_tick(canal_anatomy, canal, 0, bundle_anatomy)
            .unwrap();
            canal = reached.successor_canal;
            let resting_ingress = prepare_resident_vestibular_ingress(
                u64::try_from(source_tick).unwrap(),
                resting_body,
                resting_body,
                reached,
                &receptor_anatomy,
            )
            .unwrap();
            let prepared = state
                .prepare_vestibular_transition(&resting_ingress, 16_000_000)
                .unwrap();
            emitted.extend(prepared.observation.emitted_neuron_fractals.clone());
            state.commit(prepared).unwrap();
            if emitted
                .iter()
                .any(|fractal| fractal.neuron_lineage == lineage)
            {
                break;
            }
        }
        assert!(emitted
            .iter()
            .any(|fractal| fractal.neuron_lineage == lineage));
    }

    fn lesson_state_with_retained_experience() -> ResidentCognitiveFormationState {
        let light = (0..4)
            .map(exact_four_single_optical_episode)
            .collect::<Vec<_>>();
        let dark = exact_four_dark_optical_episode();
        let seed = explicit_optical_seed(&light[0], 500);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        for source in light
            .iter()
            .chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = state.prepare(source, 16_000_000).unwrap();
            state.commit(prepared).unwrap();
        }
        assert!(state.cohorts[0].retained_experience.is_some());
        state
    }

    #[test]
    #[ignore = "retired: fixture requires Boolean/member-set mosaic admission"]
    fn continuing_contact_tail_cannot_begin_endogenous_reassembly() {
        let light = (0..4)
            .map(exact_four_single_optical_episode)
            .collect::<Vec<_>>();
        let dark = exact_four_dark_optical_episode();
        let seed = explicit_optical_seed(&light[0], 500);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        for source in light.iter().chain(std::iter::once(&dark)) {
            let prepared = state.prepare(source, 16_000_000).unwrap();
            assert_eq!(
                prepared
                    .observation
                    .endogenous_partial_cue_reassembly_count(),
                0
            );
            state.commit(prepared).unwrap();
        }
        assert!(state.cohorts[0].pending_experience.is_none());
        assert!(state.cohorts[0].retained_experience.is_some());
        assert!(
            !state.cohorts[0]
                .retained_experience
                .as_ref()
                .unwrap()
                .local_relaxation_observed
        );

        let mut relaxation_observed = false;
        for _ in 0..DARK_TAIL_EPISODES {
            let prepared = state.prepare(&dark, 16_000_000).unwrap();
            assert_eq!(
                prepared
                    .observation
                    .endogenous_partial_cue_reassembly_count(),
                0,
                "the interval that ends the original tail cannot cue itself"
            );
            relaxation_observed = prepared.successor.cohorts[0]
                .retained_experience
                .as_ref()
                .is_some_and(|experience| experience.local_relaxation_observed);
            state.commit(prepared).unwrap();
            if relaxation_observed {
                break;
            }
        }
        assert!(state.cohorts[0].retained_experience.is_some());
        assert!(relaxation_observed);

        let encoded_at_rest = state.encode(16_000_000).unwrap();
        let restored =
            ResidentCognitiveFormationState::decode(&encoded_at_rest, 16_000_000).unwrap();
        assert_eq!(restored, state);
        assert_eq!(restored.encode(16_000_000).unwrap(), encoded_at_rest);

        let retained = state.cohorts[0].retained_experience.as_ref().unwrap();
        let mut unrelated_flow = vec![false; retained.active_electrical_contacts.len()];
        let original_contact = retained
            .active_electrical_contacts
            .iter()
            .position(|active| *active)
            .unwrap();
        let unrelated_contact = (0..unrelated_flow.len())
            .find(|index| *index != original_contact)
            .unwrap();
        let mut one_contact_formation = retained.clone();
        one_contact_formation.active_electrical_contacts.fill(false);
        one_contact_formation.active_electrical_contacts[original_contact] = true;
        unrelated_flow[unrelated_contact] = true;
        assert!(!retained_contact_set_flowing(&one_contact_formation, &unrelated_flow).unwrap());

        let partial = exact_four_partial_optical_episode();
        let mut endogenous = 0usize;
        let mut total = 0usize;
        for source in
            std::iter::once(&partial).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = state
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            endogenous += prepared
                .observation
                .endogenous_partial_cue_reassembly_count();
            total += prepared.observation.partial_cue_reassembly_count();
            state.commit(prepared).unwrap();
        }
        // The explicit partial cue may reassemble the retained formation, but
        // its continuing contact current is not an organism-generated cue.
        // Endogenous recurrence must begin from a later metabolic perturbation
        // of a proper partial member set, not from the external cue's tail.
        assert_eq!(total, 1);
        assert_eq!(endogenous, 0);

        let mut severed = restored;
        severed.cohorts[0]
            .retained_experience
            .as_mut()
            .unwrap()
            .active_electrical_contacts
            .fill(false);
        let mut severed_reassemblies = 0usize;
        for source in
            std::iter::once(&partial).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = severed
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            severed_reassemblies += prepared.observation.partial_cue_reassembly_count();
            severed.commit(prepared).unwrap();
        }
        assert_eq!(severed_reassemblies, 0);
        assert_eq!(severed.summary().mosaic_count, 0);
    }

    #[test]
    fn sparse_retained_experience_codec_is_exact_and_canonical() {
        let light = exact_four_single_optical_episode(0);
        let seed = explicit_optical_seed(&light, 1);
        let mut state =
            ResidentCognitiveFormationState::from_developmental_electrical_seeds(vec![seed])
                .unwrap();
        let prepared = state.prepare(&light, 16_000_000).unwrap();
        assert!(!prepared.observation.emitted_neuron_fractals.is_empty());
        state.commit(prepared).unwrap();
        let mut retained = state.cohorts[0].pending_experience.take().unwrap();
        let retained_members = retained
            .pending_members()
            .unwrap()
            .iter()
            .filter(|member| member.settled)
            .filter_map(|member| {
                let learned = &state.cohorts[0].state.neurons()[member.neuron_index];
                sparse_retained_physical_state_delta(&member.predecessor, learned)
                    .unwrap()
                    .map(|delta| SparseRetainedExperienceMember {
                        neuron_index: member.neuron_index,
                        predecessor: member.predecessor.clone(),
                        learned: learned.clone(),
                        delta,
                    })
            })
            .collect::<Vec<_>>();
        assert!(!retained_members.is_empty());
        retained.retained_change_neurons.fill(false);
        retained.retentively_settled_neurons.fill(false);
        for member in &retained_members {
            retained.retained_change_neurons[member.neuron_index] = true;
            retained.retentively_settled_neurons[member.neuron_index] = true;
        }
        retained.physical =
            ResidentExperiencePhysicalEvidence::Retained(retained_members.into_boxed_slice());
        retained.local_relaxation_observed = true;
        state.cohorts[0].retained_experience = Some(retained);

        let cohort = &state.cohorts[0];
        let retained = cohort.retained_experience.as_ref().unwrap();
        assert_eq!(retained.codec, ExperienceEvidenceCodec::V7);
        assert!(retained.legacy_states().is_none());
        assert!(!retained.retained_members().unwrap().is_empty());

        let evidence = encode_sparse_experience_evidence(&cohort.anatomy, retained).unwrap();
        assert_eq!(
            decode_sparse_experience_evidence(&evidence, &cohort.anatomy).unwrap(),
            *retained
        );
        let mut trailing = evidence.clone();
        trailing.push(0);
        assert!(decode_sparse_experience_evidence(&trailing, &cohort.anatomy).is_err());
        let mut corrupt = evidence;
        corrupt[EXPERIENCE_V7_MAGIC.len()] = 2;
        assert!(decode_sparse_experience_evidence(&corrupt, &cohort.anatomy).is_err());

        let predecessor_replacements = retained
            .retained_members()
            .unwrap()
            .iter()
            .map(|member| (member.neuron_index, member.predecessor.clone()))
            .collect::<Vec<_>>();
        let legacy_predecessor = cohort
            .state
            .with_replaced_neurons(&predecessor_replacements)
            .unwrap();
        let legacy = ResidentExperienceEvidence {
            codec: ExperienceEvidenceCodec::V6,
            physical: ResidentExperiencePhysicalEvidence::Legacy {
                predecessor: legacy_predecessor.into(),
                successor: Some(cohort.state.clone()),
            },
            gate_work_perturbed_neurons: retained.gate_work_perturbed_neurons.clone(),
            receptor_excitation_zeptojoules: retained
                .receptor_excitation_zeptojoules
                .clone(),
            retained_change_neurons: retained.retained_change_neurons.clone(),
            retentively_settled_neurons: retained.retentively_settled_neurons.clone(),
            active_electrical_contacts: retained.active_electrical_contacts.clone(),
            local_relaxation_observed: retained.local_relaxation_observed,
        };
        let legacy_bytes = encode_experience_evidence_v2(
            &cohort.anatomy,
            Some(&cohort.state),
            &legacy,
            true,
        )
        .unwrap();
        let mut migrated = decode_experience_evidence_v2(
            &legacy_bytes,
            &cohort.anatomy,
            Some(&cohort.state),
        )
        .unwrap();
        assert!(migrated.legacy_states().is_some());
        migrated
            .convert_legacy_physical(&cohort.anatomy, true)
            .unwrap();
        assert_eq!(migrated, *retained);

        let current = state.encode(16_000_000).unwrap();
        assert_eq!(
            ResidentCognitiveFormationState::decode(&current, 16_000_000).unwrap(),
            state
        );
    }

    #[test]
    fn first_receptor_contact_claims_receptor_and_local_integration_cells() {
        let empty = ResidentCognitiveFormationState::default();
        let retired = empty
            .encode_with_format(CognitiveCodecFormat::V12, 16_000_000)
            .unwrap();
        let current =
            ResidentCognitiveFormationState::migrate_to_current_format(&retired, 16_000_000)
                .unwrap();
        let state = ResidentCognitiveFormationState::decode(&current, 16_000_000).unwrap();
        let source = exact_optical_episode();
        let shared = prepare_complete_joint_field_admitted_fixture(&source, 0).unwrap();
        let perspective = bind_neuron_perspective(&shared, 0, 0).unwrap();
        let site =
            NeuronSourceSite::from_anchor(bind_neuron_source_anchor(&source, perspective).unwrap());
        let place = DeclaredNeuronPlace::from_source_site(&site);
        let population = state.resting_population.as_ref().unwrap();
        let offset = population.population_offset(place).unwrap();
        let resting = population.materialize(offset).unwrap();
        let resting_count = population.resting_cell_count();
        let expected_lineage = local_lineage_from_ordinal(resting.lineage_ordinal).unwrap();
        let prepared = state
            .prepare_admitted_transition(&admitted_fixture_episode(&source), 16_000_000)
            .unwrap();
        let successor = prepared.successor;
        assert_eq!(
            successor
                .resting_population
                .as_ref()
                .unwrap()
                .resting_cell_count(),
            resting_count - 2
        );
        let cohort = successor
            .cohorts
            .iter()
            .find(|cohort| cohort.anatomy.source_sites().any(|source| source == &site))
            .unwrap();
        let neuron_index = cohort.anatomy.source_site_member(&site).unwrap();
        assert_eq!(
            cohort.anatomy.neuron_lineages()[neuron_index],
            expected_lineage
        );
        assert_eq!(
            cohort.anatomy.neuron_anatomies()[neuron_index].capacitance(),
            resting.anatomy.capacitance()
        );
        assert_eq!(successor.summary().complete_neuron_count, 2);
        assert_eq!(successor.electrical_fabric.contact_count(), 1);
        let encoded = successor.encode(16_000_000).unwrap();
        let cold = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(cold, successor);
    }

    #[test]
    fn local_body_receptor_metabolism_enters_only_the_bounded_sparse_frontier() {
        let canal_anatomy =
            CanalAnatomy::new(6, 13_200, PositiveRatio::new(25, 1).unwrap()).unwrap();
        let bundle_anatomy = LocalCupulaBundleAnatomy::new(2, 5, 20_000).unwrap();
        let receptor_anatomy = phase_one_virtual_vestibular_anatomy().unwrap();
        let turn = settle_signed_yaw_actuation(
            YawBodyState::new(0).unwrap(),
            SignedYawActuation::new(90_000, 250_000).unwrap(),
        )
        .unwrap();
        let mut state = ResidentCognitiveFormationState::default();
        let mut canal = CanalState::at_rest();
        let mut heading = 0_u32;
        let mut observed = None;
        for (source_tick, signed_step) in turn.trajectory.as_slice().iter().copied().enumerate() {
            let predecessor_body = YawBodyState::new(heading).unwrap();
            heading =
                u32::try_from((i64::from(heading) + i64::from(signed_step)).rem_euclid(360_000))
                    .unwrap();
            let successor_body = YawBodyState::new(heading).unwrap();
            let reached = settle_reached_vestibular_bundle_tick(
                canal_anatomy,
                canal,
                signed_step,
                bundle_anatomy,
            )
            .unwrap();
            canal = reached.successor_canal;
            let ingress = prepare_resident_vestibular_ingress(
                u64::try_from(source_tick).unwrap(),
                predecessor_body,
                successor_body,
                reached,
                &receptor_anatomy,
            )
            .unwrap();
            let prepared = state
                .prepare_vestibular_transition(&ingress, 16_000_000)
                .unwrap();
            if prepared
                .observation
                .metabolically_perturbed_body_receptor_count
                > 0
            {
                observed = Some(prepared.observation.clone());
            }
            state = prepared.successor;
        }
        assert_eq!(
            state
                .observe_reached_neuron_count_by_layer()
                .iter()
                .find(|(layer, _)| *layer == 5)
                .copied(),
            Some((5, 1))
        );
        assert_eq!(
            state
                .observe_reached_neuron_count_by_layer()
                .iter()
                .find(|(layer, _)| *layer == 8)
                .copied(),
            Some((8, 1))
        );
        let observation = observed.expect("body receptor recovery must be physically observed");
        assert_eq!(observation.metabolically_perturbed_body_receptor_count, 1);
        assert!(observation.physically_transitioned_neuron_count >= 1);
        assert!(
            observation.metabolically_perturbed_body_receptor_count
                <= observation.physically_transitioned_neuron_count
        );
        assert_eq!(
            observation
                .localized_metabolic_strain_evaluated_body_receptor_lineages
                .len(),
            1
        );
        assert_eq!(observation.localized_metabolic_strain.len(), 1);
        let strain = &observation.localized_metabolic_strain[0];
        assert_eq!(strain.neuron_place.layer(), 5);
        assert_eq!(
            strain.neuron_lineage,
            observation.localized_metabolic_strain_evaluated_body_receptor_lineages[0]
        );
        assert!(
            strain.psi_dissipation_quanta.iter().any(|quanta| *quanta != 0)
                || strain.gate_dissipation_quanta != 0
                || strain.plastic_dissipation_quanta != 0
        );

        let encoded = state.encode(16_000_000).unwrap();
        assert_eq!(
            ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap(),
            state
        );
    }

    #[test]
    fn sense_local_topology_indices_project_to_distinct_integration_places() {
        let sight = local_integration_place(DeclaredNeuronPlace::new(0, 0)).unwrap();
        let sound = local_integration_place(DeclaredNeuronPlace::new(1, 0)).unwrap();
        let body = local_integration_place(DeclaredNeuronPlace::new(5, 0)).unwrap();
        assert_eq!(sight, DeclaredNeuronPlace::new(6, 0));
        assert_eq!(sound, DeclaredNeuronPlace::new(6, 1));
        assert_eq!(body, DeclaredNeuronPlace::new(6, 15));
        assert_ne!(sight, sound);
        assert_ne!(sound, body);
        assert_ne!(sight, body);
    }

    #[test]
    fn body_terminal_integration_places_follow_the_existing_sensory_geography() {
        assert_eq!(
            PRE_PROPRIOCEPTIVE_BODY_SENSE_LAYER,
            u32::from(PhysicalSourceSense::Body.declared_layer())
        );
        let served_pre_proprioceptive_roster = [(0, 26), (1, 33), (2, 26), (3, 7), (4, 4), (5, 9)];
        for (layer, topology_index) in served_pre_proprioceptive_roster {
            let last_existing = declared_neuron_territory(DeclaredNeuronPlace::new(
                layer,
                topology_index,
            ))
            .unwrap()
            .checked_sub(1)
            .unwrap();
            assert!(
                last_existing < u128::from(BODY_PROPRIOCEPTOR_LAYER6_TOPOLOGY_OFFSET)
            );
        }

        let first = local_integration_place(DeclaredNeuronPlace::new(
            PhysicalSourceSense::Body.declared_layer().into(),
            u32::try_from(BODY_PROPRIOCEPTOR_TOPOLOGY_OFFSET).unwrap(),
        ))
        .unwrap();
        let last = local_integration_place(DeclaredNeuronPlace::new(
            PhysicalSourceSense::Body.declared_layer().into(),
            u32::try_from(BODY_PROPRIOCEPTOR_TOPOLOGY_OFFSET + BODY_EFFECTOR_TERMINAL_COUNT - 1)
                .unwrap(),
        ))
        .unwrap();
        assert_eq!(first, DeclaredNeuronPlace::new(6, 629));
        assert_eq!(last, DeclaredNeuronPlace::new(6, 702));
        let first_regulation = body_regulation_place(
            DeclaredNeuronPlace::new(PRE_PROPRIOCEPTIVE_BODY_SENSE_LAYER, 10),
            first,
        )
        .unwrap();
        let last_regulation = body_regulation_place(
            DeclaredNeuronPlace::new(PRE_PROPRIOCEPTIVE_BODY_SENSE_LAYER, 83),
            last,
        )
        .unwrap();
        assert_eq!(first_regulation, DeclaredNeuronPlace::new(8, 115));
        assert_eq!(last_regulation, DeclaredNeuronPlace::new(8, 188));
        for topology_index in 0..=PRE_PROPRIOCEPTIVE_WIDEST_BODY_TOPOLOGY_INDEX {
            let existing = local_integration_place(DeclaredNeuronPlace::new(
                PRE_PROPRIOCEPTIVE_BODY_SENSE_LAYER,
                topology_index,
            ))
            .unwrap();
            assert!(existing.topology_index() < BODY_PROPRIOCEPTOR_LAYER8_TOPOLOGY_OFFSET);
        }
    }

    #[test]
    fn one_interval_frontier_does_not_jump_across_a_contact_chain() {
        let reached = one_interval_electrical_frontier(
            &[true, false, false, false],
            &[(0, 1), (1, 2), (2, 3)],
        )
        .unwrap();
        assert_eq!(reached, vec![true, true, false, false]);

        let next = one_interval_electrical_frontier(&reached, &[(0, 1), (1, 2), (2, 3)]).unwrap();
        assert_eq!(next, vec![true, true, true, false]);
    }

    #[test]
    fn indexed_frontier_is_invariant_under_unrelated_topology() {
        let lineage = |ordinal: u32| {
            let mut lineage = [0_u8; 16];
            lineage[12..].copy_from_slice(&ordinal.to_be_bytes());
            lineage
        };
        let index = |unrelated_pairs: usize| {
            let neuron_count = 2 + unrelated_pairs * 2;
            let mut flat_locations = Vec::with_capacity(neuron_count);
            let mut flat_by_lineage = Vec::with_capacity(neuron_count);
            let mut lineage_layers = Vec::with_capacity(neuron_count);
            for flat in 0..neuron_count {
                let id = lineage(u32::try_from(flat).unwrap());
                flat_locations.push((0, flat, id));
                flat_by_lineage.push((id, flat));
                lineage_layers.push((id, 6));
            }
            let mut contacts = Vec::with_capacity(1 + unrelated_pairs);
            for contact_index in 0..=unrelated_pairs {
                let (left, right) = if contact_index == 0 {
                    (0, 1)
                } else {
                    (contact_index * 2, contact_index * 2 + 1)
                };
                contacts.push(ResidentContactTopologyEntry {
                    left,
                    right,
                    stable_bond: StablePhysicalBondReference::new(
                        flat_locations[left].2,
                        flat_locations[right].2,
                        0,
                    )
                    .unwrap(),
                    origin: ResidentContactOrigin::Local {
                        cohort_index: 0,
                        contact_index,
                        left_member: left,
                        right_member: right,
                    },
                });
            }
            let mut incident = vec![Vec::new(); neuron_count];
            let mut neighbours = vec![Vec::new(); neuron_count];
            for (contact_index, contact) in contacts.iter().enumerate() {
                incident[contact.left].push(contact_index);
                incident[contact.right].push(contact_index);
                neighbours[contact.left].push(contact.right);
                neighbours[contact.right].push(contact.left);
            }
            let canonical_lineages = flat_locations
                .iter()
                .map(|(_, _, lineage)| *lineage)
                .collect::<Vec<_>>()
                .into_boxed_slice();
            let mut canonical_bonds = contacts
                .iter()
                .map(|contact| contact.stable_bond)
                .collect::<Vec<_>>();
            canonical_bonds.sort_unstable();
            ResidentTopologyIndex {
                flat_locations: flat_locations.into_boxed_slice(),
                flat_by_lineage: flat_by_lineage.into_boxed_slice(),
                lineage_layers: lineage_layers.into_boxed_slice(),
                canonical_lineages,
                canonical_bonds: canonical_bonds.into_boxed_slice(),
                contacts: contacts.into_boxed_slice(),
                incident_contacts_by_flat: incident
                    .into_iter()
                    .map(Vec::into_boxed_slice)
                    .collect::<Vec<_>>()
                    .into_boxed_slice(),
                neighbours_by_flat: neighbours
                    .into_iter()
                    .map(Vec::into_boxed_slice)
                    .collect::<Vec<_>>()
                    .into_boxed_slice(),
                cohort_shapes: Box::new([]),
                fabric_contact_count: 0,
            }
        };
        let baseline = index(0).one_interval_frontier(&[lineage(0)]).unwrap();
        let wide = index(1_024)
            .one_interval_frontier(&[lineage(0)])
            .unwrap();
        assert_eq!(baseline, (vec![0, 1], vec![0]));
        assert_eq!(wide, baseline);
    }

    #[test]
    fn only_current_internal_reassembly_retains_its_recurrent_frontier() {
        let cue = [1_u8; 16];
        let recurrent = [9_u8; 16];
        let predecessor_sender = [8_u8; 16];
        let unrelated = [7_u8; 16];
        let predecessor_bond =
            StablePhysicalBondReference::new(predecessor_sender, recurrent, 0).unwrap();
        let predecessor = ActiveElectricalFrontierEntry::caused_with_frontier(
            predecessor_sender,
            recurrent,
            recurrent,
            predecessor_bond,
            3,
        )
        .unwrap();
        let cue_bond = StablePhysicalBondReference::new(cue, recurrent, 0).unwrap();
        let transfer = DirectedPhysicalTransferObservation {
            sender: recurrent,
            receiver: cue,
            bond: cue_bond,
            transferred_whole_carriers: 5,
        };
        let reassembly = InternallyReassembledFormationCueObservation {
            formation_receipt: [4_u8; 32],
            cue_lineages: vec![cue],
            recurrent_lineage: Some(recurrent),
        };

        let mut retained = Vec::new();
        retain_internally_reassembled_recurrent_frontier(
            &mut retained,
            &[predecessor],
            std::slice::from_ref(&reassembly),
            &[transfer],
        )
        .unwrap();
        assert_eq!(retained.len(), 1);
        assert_eq!(retained[0].frontier_lineage(), recurrent);
        assert_eq!(retained[0].directed_transfer(), Some(transfer));

        let unrelated_transfer = DirectedPhysicalTransferObservation {
            sender: unrelated,
            receiver: cue,
            bond: StablePhysicalBondReference::new(unrelated, cue, 0).unwrap(),
            transferred_whole_carriers: 5,
        };
        let mut absent = Vec::new();
        retain_internally_reassembled_recurrent_frontier(
            &mut absent,
            &[predecessor],
            &[reassembly],
            &[unrelated_transfer],
        )
        .unwrap();
        assert!(absent.is_empty());
    }

    #[test]
    fn external_reassembly_identity_requires_its_exact_cue_to_recurrent_transfer() {
        let cue = [1_u8; 16];
        let recurrent = [9_u8; 16];
        let unrelated = [7_u8; 16];
        let cue_bond = StablePhysicalBondReference::new(cue, recurrent, 0).unwrap();
        let reached = ActiveElectricalFrontierEntry::caused_with_frontier(
            cue,
            recurrent,
            recurrent,
            cue_bond,
            5,
        )
        .unwrap();
        assert!(external_reassembly_reaches_recurrent_frontier(
            &[cue],
            recurrent,
            &[reached],
        ));

        let unrelated_bond =
            StablePhysicalBondReference::new(unrelated, recurrent, 0).unwrap();
        let unrelated_reached = ActiveElectricalFrontierEntry::caused_with_frontier(
            unrelated,
            recurrent,
            recurrent,
            unrelated_bond,
            5,
        )
        .unwrap();
        assert!(!external_reassembly_reaches_recurrent_frontier(
            &[cue],
            recurrent,
            &[unrelated_reached],
        ));
    }

    #[test]
    fn formation_cue_is_canonical_across_source_order_and_repetition() {
        let first = [1_u8; 16];
        let second = [2_u8; 16];
        let third = [3_u8; 16];
        let mut cue = vec![third, first, second, third];

        canonicalize_formation_cue(&mut cue);

        assert_eq!(cue, vec![first, second, third]);
    }

    #[test]
    fn one_multisensory_occurrence_mounts_one_reusable_physical_association() {
        fn receptor_cohort(
            sense: PhysicalSourceSense,
            topology_index: u32,
            lineage: [u8; 16],
        ) -> ResidentReachedCohort {
            let site = NeuronSourceSite::fixture_in_sense(sense, topology_index);
            let place = DeclaredNeuronPlace::from_source_site(&site);
            let neuron = create_quiescent_virtual_material_neuron(place).unwrap();
            let sparse = SparseElectricalAnatomy::new(1, Vec::new()).unwrap();
            let anatomy = ReachedCohortAnatomy::new_mounted(
                vec![neuron.anatomy],
                vec![lineage],
                vec![ReachedNeuronMount::Receptor(site)],
                sparse.clone(),
            )
            .unwrap();
            ResidentReachedCohort {
                state: ReachedCohortState::new(
                    &anatomy,
                    vec![neuron.state],
                    SparseElectricalState::genesis(&sparse),
                )
                .unwrap()
                .into(),
                anatomy,
                pending_experience: None,
                retained_experience: None,
                pending_recurrence: None,
            }
        }

        let receptor_lineages = [local_lineage(1), local_lineage(2), local_lineage(3)];
        let mut cohorts = vec![
            receptor_cohort(PhysicalSourceSense::Sight, 0, receptor_lineages[0]),
            receptor_cohort(PhysicalSourceSense::Sight, 1, receptor_lineages[1]),
            receptor_cohort(PhysicalSourceSense::Sound, 0, receptor_lineages[2]),
        ];
        let occupied = cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.mounts().iter().map(|mount| mount.place()))
            .collect::<Vec<_>>();
        let mut population = Some(
            DevelopmentalRestingPopulation::admit(16_000_000, 100_000, 100, &occupied).unwrap(),
        );
        let mut next_lineage = 4;
        let mut fabric = ResidentElectricalFabric::default();
        let reached_receptors = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter_map(|(mount, lineage)| mount.source_site().map(|_| (*lineage, mount.place())))
            .collect::<Vec<_>>();
        let resting_before = population.as_ref().unwrap().resting_cell_count();
        mount_reached_local_integration(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &reached_receptors[..1],
        )
        .unwrap();
        assert_eq!(fabric.contact_count(), 1);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
        let one_frontier_cohorts = cohorts.len();
        mount_reached_local_integration(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[],
        )
        .unwrap();
        mount_reached_local_integration(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &reached_receptors[..1],
        )
        .unwrap();
        assert_eq!(cohorts.len(), one_frontier_cohorts);
        assert_eq!(fabric.contact_count(), 1);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
        mount_reached_local_integration(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &reached_receptors[1..],
        )
        .unwrap();
        mount_reached_cross_sensory_association(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &receptor_lineages,
        )
        .unwrap();
        let association = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter(|(mount, _)| mount.place().layer() == 7)
            .map(|(_, lineage)| *lineage)
            .collect::<Vec<_>>();
        assert_eq!(association.len(), 1);
        assert_eq!(fabric.contact_count(), 6);
        let cohort_count = cohorts.len();
        let contact_count = fabric.contact_count();

        mount_reached_cross_sensory_association(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &receptor_lineages,
        )
        .unwrap();
        assert_eq!(cohorts.len(), cohort_count);
        assert_eq!(fabric.contact_count(), contact_count);

        let topology = organism_mosaic_topology(&cohorts, &fabric).unwrap();
        let topology_index = ResidentTopologyIndex::build(&cohorts, &fabric).unwrap();
        let fractal =
            crate::complete_neuron::SparsePhysicalStateDelta::from_canonical_entries(vec![
                crate::complete_neuron::PhysicalStateDeltaEntry::new(
                    crate::complete_neuron::PhysicalStateCoordinate::PlasticRestLength,
                    crate::complete_neuron::ExactPhysicalStateDelta::Rational(
                        ExactRational::new(1, 3).unwrap(),
                    ),
                )
                .unwrap(),
            ])
            .unwrap();
        let original = admit_physical_mosaic_original(
            &topology.lineages,
            &topology.fractal_anatomies,
            &vec![Some(fractal.clone()); topology.lineages.len()],
            &topology.bonds,
        )
        .unwrap();
        let encoded = encode_organism_mosaic(&cohorts, &fabric, &original, 16_000_000).unwrap();
        let cold = decode_organism_mosaic(&cohorts, &fabric, &encoded, 16_000_000).unwrap();
        assert_eq!(cold, original);
        let recognized = prove_physical_mosaic_recurrence(
            &cold,
            &topology.lineages,
            &topology.bonds,
            &receptor_lineages,
        )
        .unwrap();
        assert!(recognized.carries_only_retained_neuron_structure());

        let original_members = recognized.member_lineages().to_vec();
        let original_fractals = recognized.retained_fractals().to_vec();
        let original_bonds = recognized.original_bonds().to_vec();
        let prior_cue = recognized.partial_cue_lineages().to_vec();
        let mut mosaics = vec![RetainedOrganismMosaic::newly_admitted(recognized)];
        let mut current_deltas = topology
            .lineages
            .iter()
            .map(|lineage| (*lineage, fractal.clone()))
            .collect::<Vec<_>>();
        current_deltas.sort_unstable_by_key(|(lineage, _)| *lineage);
        let changed_cue = [receptor_lineages[0]];
        let (
            altered_receipt,
            reassemblies,
            internal_reassemblies,
            relations,
            internal_cues,
            external_frontiers,
        ) =
            settle_organism_mosaic_boundary(
            &cohorts,
            &topology_index,
            &[],
            &current_deltas,
            &changed_cue,
            &changed_cue,
            &[],
            &topology.bonds,
            &[],
            &[],
            &[],
            &[],
            &mut mosaics,
            16_000_000,
        )
        .unwrap();
        assert!(altered_receipt.is_some());
        assert_eq!(reassemblies, 1);
        assert_eq!(internal_reassemblies, 0);
        assert!(internal_cues.is_empty());
        assert!(external_frontiers.is_empty());
        assert!(relations.is_empty());
        assert_eq!(mosaics.len(), 1);
        assert_eq!(mosaics[0].reinforcement_count, 0);
        assert_eq!(mosaics[0].mosaic.member_lineages(), original_members);
        assert_eq!(mosaics[0].mosaic.retained_fractals(), original_fractals);
        assert_eq!(mosaics[0].mosaic.original_bonds(), original_bonds);
        assert_ne!(mosaics[0].mosaic.partial_cue_lineages(), prior_cue);
        assert_eq!(mosaics[0].mosaic.partial_cue_lineages(), changed_cue);

        let altered_bytes =
            encode_retained_organism_mosaic(&cohorts, &fabric, &mosaics[0], 16_000_000).unwrap();
        let altered_cold =
            decode_retained_organism_mosaic(&cohorts, &fabric, &altered_bytes, 16_000_000).unwrap();
        assert_eq!(altered_cold, mosaics[0]);

        let second_fractal =
            crate::complete_neuron::SparsePhysicalStateDelta::from_canonical_entries(vec![
                crate::complete_neuron::PhysicalStateDeltaEntry::new(
                    crate::complete_neuron::PhysicalStateCoordinate::PlasticRestLength,
                    crate::complete_neuron::ExactPhysicalStateDelta::Rational(
                        ExactRational::new(2, 3).unwrap(),
                    ),
                )
                .unwrap(),
            ])
            .unwrap();
        let second_original = admit_physical_mosaic_original(
            &topology.lineages,
            &topology.fractal_anatomies,
            &vec![Some(second_fractal); topology.lineages.len()],
            &topology.bonds,
        )
        .unwrap();
        let second_recognized = prove_physical_mosaic_recurrence(
            &second_original,
            &topology.lineages,
            &topology.bonds,
            &receptor_lineages,
        )
        .unwrap();
        mosaics.push(RetainedOrganismMosaic::newly_admitted(second_recognized));

        let one_reassembled_relation = observe_organic_mosaic_relations(
            &topology,
            &mosaics,
            &[0, 1],
            &[0],
            &topology.bonds,
            &[],
            &[],
            &[],
            &[],
            16_000_000,
        )
        .unwrap();
        assert_eq!(one_reassembled_relation.len(), 1);
        assert_eq!(one_reassembled_relation[0].formation_receipts.len(), 2);
        let first_receipts = one_reassembled_relation[0].formation_receipts.clone();
        let first_structure = one_reassembled_relation[0].structural_relation_receipt;

        let alternate_cue = [receptor_lineages[1]];
        mosaics[1].mosaic = alter_physical_mosaic_recurrence(
            &mosaics[1].mosaic,
            &topology.lineages,
            &topology.bonds,
            &alternate_cue,
        )
        .unwrap();
        let changed_receipt_same_structure = observe_organic_mosaic_relations(
            &topology,
            &mosaics,
            &[0, 1],
            &[0],
            &topology.bonds,
            &[],
            &[],
            &[],
            &[],
            16_000_000,
        )
        .unwrap();
        assert_ne!(
            changed_receipt_same_structure[0].formation_receipts,
            first_receipts
        );
        assert_eq!(
            changed_receipt_same_structure[0].structural_relation_receipt,
            first_structure
        );

        let (
            _,
            related_reassemblies,
            related_internal_reassemblies,
            related,
            internal_cues,
            external_frontiers,
        ) =
            settle_organism_mosaic_boundary(
            &cohorts,
            &topology_index,
            &[],
            &current_deltas,
            &changed_cue,
            &changed_cue,
            &[],
            &topology.bonds,
            &[],
            &[],
            &[],
            &[],
            &mut mosaics,
            16_000_000,
        )
        .unwrap();
        assert_eq!(related_reassemblies, 2);
        assert_eq!(related_internal_reassemblies, 0);
        assert!(internal_cues.is_empty());
        assert!(external_frontiers.is_empty());
        assert_eq!(related.len(), 1);
        assert_eq!(related[0].formation_receipts.len(), 2);
        let mut expected_shared_lineages = topology.lineages.clone();
        expected_shared_lineages.sort_unstable();
        assert_eq!(related[0].shared_lineages, expected_shared_lineages);
        assert!(!related[0].active_bonds.is_empty());

        let before_quiescent_relation = mosaics.clone();
        let (
            receipt,
            recurring_reassemblies,
            recurring_internal_reassemblies,
            recurring_relation,
            internal_cues,
            external_frontiers,
        ) =
            settle_organism_mosaic_boundary(
                &cohorts,
                &topology_index,
                &[],
                &current_deltas,
                &changed_cue,
                &changed_cue,
                &[],
                &topology.bonds,
                &[],
                &[],
                &[],
                &[],
                &mut mosaics,
                16_000_000,
            )
            .unwrap();
        assert_eq!(receipt, None);
        assert_eq!(recurring_reassemblies, 2);
        assert_eq!(recurring_internal_reassemblies, 0);
        assert!(internal_cues.is_empty());
        assert!(external_frontiers.is_empty());
        assert_eq!(recurring_relation, related);
        assert_eq!(mosaics, before_quiescent_relation);

        let before_internal_receipts = mosaics
            .iter()
            .map(|retained| {
                sha256(
                    &encode_retained_organism_mosaic(
                        &cohorts,
                        &fabric,
                        retained,
                        16_000_000,
                    )
                    .unwrap(),
                )
            })
            .collect::<Vec<_>>();
        let internal_cue = topology.lineages.clone();
        let mut expected_internal_cue = internal_cue.clone();
        canonicalize_formation_cue(&mut expected_internal_cue);
        let (
            internal_receipt,
            internal_total,
            internal_count,
            _,
            internal_cues,
            external_frontiers,
        ) =
            settle_organism_mosaic_boundary(
                &cohorts,
                &topology_index,
                &[],
                &current_deltas,
                &[],
                &[],
                &internal_cue,
                &topology.bonds,
                &[],
                &[],
                &[],
                &[],
                &mut mosaics,
                16_000_000,
            )
            .unwrap();
        assert!(internal_receipt.is_some());
        assert_eq!(internal_total, 2);
        assert_eq!(internal_count, 2);
        assert_eq!(internal_cues.len(), 2);
        assert!(external_frontiers.is_empty());
        assert!(internal_cues
            .iter()
            .all(|observation| observation.cue_lineages == expected_internal_cue));
        for (index, retained) in mosaics.iter().enumerate() {
            assert_eq!(
                retained.mosaic.recurrence_origin(),
                Some(PhysicalMosaicRecurrenceOrigin::InternallySimulated)
            );
            assert_ne!(
                sha256(
                    &encode_retained_organism_mosaic(
                        &cohorts,
                        &fabric,
                        retained,
                        16_000_000,
                    )
                    .unwrap(),
                ),
                before_internal_receipts[index]
            );
            let encoded = encode_retained_organism_mosaic(
                &cohorts,
                &fabric,
                retained,
                16_000_000,
            )
            .unwrap();
            let cold = decode_retained_organism_mosaic(
                &cohorts,
                &fabric,
                &encoded,
                16_000_000,
            )
            .unwrap();
            assert_eq!(cold, *retained);
        }

        // Continuous sensing elsewhere in the body is not provenance for
        // either retained formation. It must therefore neither relabel nor
        // erase their independently measured metabolic recurrence.
        let unrelated_external = [[0xfe_u8; 16]];
        let (
            _,
            mixed_total,
            mixed_internal_count,
            _,
            mixed_internal_cues,
            external_frontiers,
        ) =
            settle_organism_mosaic_boundary(
                &cohorts,
                &topology_index,
                &[],
                &current_deltas,
                &unrelated_external,
                &unrelated_external,
                &internal_cue,
                &topology.bonds,
                &[],
                &[],
                &[],
                &[],
                &mut mosaics,
                16_000_000,
            )
            .unwrap();
        assert_eq!(mixed_total, 2);
        assert_eq!(mixed_internal_count, 2);
        assert_eq!(mixed_internal_cues.len(), 2);
        assert!(external_frontiers.is_empty());
        assert!(mixed_internal_cues
            .iter()
            .all(|observation| observation.cue_lineages == expected_internal_cue));
    }

    #[test]
    fn coincident_association_and_body_motion_mounts_one_reusable_affective_reach() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(16_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let association = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(7, 0),
        )
        .unwrap();
        let regulation = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(8, 0),
        )
        .unwrap();
        let resting_before = population.as_ref().unwrap().resting_cell_count();
        let mut fabric = ResidentElectricalFabric::default();
        mount_reached_affective_reach(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[association, regulation],
        )
        .unwrap();
        let affective = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter(|(mount, _)| mount.place().layer() == 10)
            .map(|(_, lineage)| *lineage)
            .collect::<Vec<_>>();
        assert_eq!(affective.len(), 1);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
        assert!(fabric.contains_contact(association, affective[0]));
        assert!(fabric.contains_contact(regulation, affective[0]));
        let cohort_count = cohorts.len();
        let contact_count = fabric.contact_count();

        mount_reached_affective_reach(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[regulation, association],
        )
        .unwrap();
        assert_eq!(cohorts.len(), cohort_count);
        assert_eq!(fabric.contact_count(), contact_count);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
    }

    #[test]
    fn reached_affective_cell_exposes_its_existing_local_plastic_consequence() {
        let mut cohorts = Vec::new();
        let mut population = None;
        let mut next_lineage = 1;
        let association = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(7, 0),
        )
        .unwrap();
        let regulation = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(8, 0),
        )
        .unwrap();
        let mut fabric = ResidentElectricalFabric::default();
        mount_reached_affective_reach(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[association, regulation],
        )
        .unwrap();
        let affective = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .find(|(mount, _)| mount.place().layer() == 10)
            .map(|(_, lineage)| *lineage)
            .unwrap();
        let plastic = |cohorts: &[ResidentReachedCohort]| {
            cohorts
                .iter()
                .flat_map(|cohort| {
                    cohort
                        .state
                        .neurons()
                        .iter()
                        .zip(cohort.anatomy.neuron_lineages())
                })
                .find(|(_, lineage)| **lineage == affective)
                .map(|(neuron, _)| neuron.plastic.physical_parts())
                .unwrap()
        };
        let predecessor = plastic(&cohorts);
        let participant_plastic = |lineage: [u8; 16], cohorts: &[ResidentReachedCohort]| {
            cohorts
                .iter()
                .flat_map(|cohort| {
                    cohort
                        .state
                        .neurons()
                        .iter()
                        .zip(cohort.anatomy.neuron_lineages())
                })
                .find(|(_, candidate)| **candidate == lineage)
                .map(|(neuron, _)| neuron.plastic.physical_parts())
                .unwrap()
        };
        let association_predecessor = participant_plastic(association, &cohorts);
        let regulation_predecessor = participant_plastic(regulation, &cohorts);
        let topology_index = ResidentTopologyIndex::build(&cohorts, &fabric).unwrap();
        let mut transitioned = Vec::new();
        let mut retained_settlement = None;
        for ordinal in 1..=128 {
            let observation = settle_internal_contact_interval(
                &mut cohorts,
                &mut fabric,
                &topology_index,
                &[association, regulation],
                &[association, regulation],
                &mut transitioned,
                ordinal,
                0,
            )
            .unwrap();
            if let Some(plasticity) = observation
                .affective_balance_trajectories
                .iter()
                .find(|trajectory| trajectory.neuron_lineage == affective)
                .and_then(|trajectory| trajectory.localized_plasticity_settlement)
            {
                assert!(plasticity.incident_catalyst_quanta > 0);
                assert!(plasticity.reaction_extent > 0);
                assert_eq!(
                    plasticity
                        .predecessor_reservoir
                        .0
                        .checked_sub(plasticity.successor_reservoir.0)
                        .unwrap(),
                    plasticity.delivered_energy_zeptojoules
                );
                assert_eq!(
                    plasticity
                        .successor_reservoir
                        .1
                        .checked_sub(plasticity.predecessor_reservoir.1)
                        .unwrap(),
                    plasticity.delivered_energy_zeptojoules
                );
                assert_eq!(
                    plasticity.predecessor_reservoir.2,
                    plasticity.successor_reservoir.2
                );
                if plasticity.predecessor_plastic_rest_length_nanometres
                    != plasticity.successor_plastic_rest_length_nanometres
                {
                    retained_settlement = Some(plasticity);
                }
            }
            if retained_settlement.is_some() {
                break;
            }
        }
        let successor = plastic(&cohorts);
        let retained_settlement = retained_settlement.expect("local plastic return did not settle");
        assert_eq!(
            retained_settlement.predecessor_plastic_rest_length_nanometres,
            predecessor.0
        );
        assert_eq!(
            retained_settlement.successor_plastic_rest_length_nanometres,
            successor.0
        );
        assert_ne!(predecessor, successor);
        assert_eq!(
            participant_plastic(association, &cohorts),
            association_predecessor
        );
        assert_eq!(
            participant_plastic(regulation, &cohorts),
            regulation_predecessor
        );
    }

    #[test]
    fn active_association_affective_bond_mounts_one_delayed_ordering_route() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(16_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let association = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(7, 0),
        )
        .unwrap();
        let affective = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(10, 0),
        )
        .unwrap();
        let resting_before = population.as_ref().unwrap().resting_cell_count();
        let mut fabric = ResidentElectricalFabric::default();

        mount_reached_ordering_reach(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[],
        )
        .unwrap();
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before
        );

        let active_bond = StablePhysicalBondReference::new(association, affective, 0).unwrap();
        mount_reached_ordering_reach(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[active_bond],
        )
        .unwrap();
        let ordering = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter(|(mount, _)| mount.place().layer() == 11)
            .map(|(_, lineage)| *lineage)
            .collect::<Vec<_>>();
        assert_eq!(ordering.len(), 1);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
        assert!(fabric.contains_contact(association, ordering[0]));
        assert!(fabric.contains_contact(affective, ordering[0]));
        let cohort_count = cohorts.len();
        let contact_count = fabric.contact_count();

        mount_reached_ordering_reach(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[active_bond],
        )
        .unwrap();
        assert_eq!(cohorts.len(), cohort_count);
        assert_eq!(fabric.contact_count(), contact_count);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
    }

    #[test]
    fn coincident_body_regulation_and_ordering_mount_one_reusable_motor_effector() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(1_600_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let mut fabric = ResidentElectricalFabric::default();
        let (regulation, _, _) = mount_body_regulation_fixture(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            BodyAxis::LeftElbowFlexion,
            BodyEffectorDirection::TowardMaximum,
        );
        let ordering = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(11, 0),
        )
        .unwrap();
        let resting_before = population.as_ref().unwrap().resting_cell_count();

        mount_reached_motor_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[ordering],
        )
        .unwrap();
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before
        );

        mount_reached_motor_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[ordering, regulation],
        )
        .unwrap();
        let motor = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter(|(mount, _)| mount.place().layer() == 12)
            .map(|(_, lineage)| *lineage)
            .collect::<Vec<_>>();
        assert_eq!(motor.len(), 1);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
        assert!(fabric.contains_contact(regulation, motor[0]));
        assert!(fabric.contains_contact(ordering, motor[0]));
        let motor_cohort = cohorts
            .iter()
            .find(|cohort| cohort.anatomy.neuron_lineages().contains(&motor[0]))
            .unwrap();
        assert_eq!(
            motor_cohort.anatomy.mounts()[0].body_effector_terminal(),
            Some(BodyEffectorTerminal::new(
                BodyAxis::LeftElbowFlexion,
                BodyEffectorDirection::TowardMaximum,
            ))
        );
        let encoded_motor =
            encode_reached_cohort_cell_v6(&motor_cohort.anatomy, &motor_cohort.state).unwrap();
        assert_eq!(&encoded_motor[..8], b"GLRCC08\0");
        let (restored_anatomy, restored_state) =
            decode_reached_cohort_cell(&encoded_motor).unwrap();
        assert_eq!(restored_anatomy, motor_cohort.anatomy);
        assert_eq!(restored_state, *motor_cohort.state);
        let cohort_count = cohorts.len();
        let contact_count = fabric.contact_count();

        mount_reached_motor_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[regulation, ordering],
        )
        .unwrap();
        assert_eq!(cohorts.len(), cohort_count);
        assert_eq!(fabric.contact_count(), contact_count);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
    }

    #[test]
    fn distinct_body_regulations_mount_distinct_unambiguous_motor_pools() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(1_600_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let mut fabric = ResidentElectricalFabric::default();
        let (first_regulation, _, _) = mount_body_regulation_fixture(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            BodyAxis::LeftElbowFlexion,
            BodyEffectorDirection::TowardMinimum,
        );
        let (second_regulation, _, _) = mount_body_regulation_fixture(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            BodyAxis::LeftElbowFlexion,
            BodyEffectorDirection::TowardMaximum,
        );
        let ordering = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(11, 0),
        )
        .unwrap();
        mount_reached_motor_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[first_regulation, second_regulation, ordering],
        )
        .unwrap();
        let motors = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter(|(mount, _)| mount.place().layer() == 12)
            .map(|(_, lineage)| *lineage)
            .collect::<Vec<_>>();
        assert_eq!(motors.len(), 2);
        for motor in motors {
            assert!(fabric.contains_contact(motor, ordering));
            let regulation_count = [first_regulation, second_regulation]
                .into_iter()
                .filter(|regulation| fabric.contains_contact(motor, *regulation))
                .count();
            assert_eq!(regulation_count, 1);
        }
    }

    #[test]
    fn motor_effector_exposes_exact_sparse_body_afferent_ancestry() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(1_600_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let mut fabric = ResidentElectricalFabric::default();
        let (regulation, receptor_lineage, receptor_site) = mount_body_regulation_fixture(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            BodyAxis::RightGripAperture,
            BodyEffectorDirection::TowardMinimum,
        );
        let ordering = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(11, 0),
        )
        .unwrap();
        mount_reached_motor_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[regulation, ordering],
        )
        .unwrap();

        let flat_locations = cohorts
            .iter()
            .enumerate()
            .flat_map(|(cohort_index, cohort)| {
                cohort
                    .anatomy
                    .neuron_lineages()
                    .iter()
                    .enumerate()
                    .map(move |(neuron_index, lineage)| {
                        (cohort_index, neuron_index, *lineage)
                    })
            })
            .collect::<Vec<_>>();
        let flat_for_lineage = |lineage: [u8; 16]| {
            flat_locations
                .iter()
                .position(|(_, _, candidate)| *candidate == lineage)
                .unwrap()
        };
        let mut neighbours = vec![Vec::new(); flat_locations.len()];
        for (left, right) in fabric.contact_endpoints() {
            let left_flat = flat_for_lineage(fabric.lineages()[left]);
            let right_flat = flat_for_lineage(fabric.lineages()[right]);
            neighbours[left_flat].push(right_flat);
            neighbours[right_flat].push(left_flat);
        }
        let neighbours = neighbours
            .into_iter()
            .map(Vec::into_boxed_slice)
            .collect::<Vec<_>>();
        let motor_flat = flat_locations
            .iter()
            .enumerate()
            .find_map(|(flat, (cohort_index, neuron_index, _))| {
                (cohorts[*cohort_index].anatomy.mounts()[*neuron_index]
                    .place()
                    .layer()
                    == 12)
                    .then_some(flat)
            })
            .unwrap();
        let paths = exact_motor_body_afferent_paths(
            motor_flat,
            &flat_locations,
            &cohorts,
            &neighbours,
        )
        .unwrap();
        assert_eq!(paths.len(), 1);
        assert_eq!(paths[0].body_regulation_lineage, regulation);
        assert_eq!(paths[0].receptor_lineage, receptor_lineage);
        assert_eq!(paths[0].receptor_site, receptor_site);
    }

    #[test]
    fn acoustic_body_ordering_and_existing_motor_mount_one_reusable_articulatory_effector() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(16_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let acoustic = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(1, 0),
        )
        .unwrap();
        let regulation = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(8, 0),
        )
        .unwrap();
        let ordering = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(11, 0),
        )
        .unwrap();
        let motor = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(12, 0),
        )
        .unwrap();
        let second_acoustic = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            DeclaredNeuronPlace::new(1, 1),
        )
        .unwrap();
        let mounted = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .map(|(mount, lineage)| (*lineage, mount.clone()))
            .collect::<Vec<_>>();
        let resting_before = population.as_ref().unwrap().resting_cell_count();
        let mut fabric = ResidentElectricalFabric::default();

        mount_reached_articulatory_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[acoustic, regulation, ordering],
            &mounted,
        )
        .unwrap();
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before
        );

        mount_reached_articulatory_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[acoustic, regulation, ordering, motor],
            &mounted,
        )
        .unwrap();
        let articulatory = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter(|(mount, _)| mount.place().layer() == 13)
            .map(|(_, lineage)| *lineage)
            .collect::<Vec<_>>();
        assert_eq!(articulatory.len(), 1);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
        for participant in [acoustic, regulation, ordering, motor] {
            assert!(fabric.contains_contact(participant, articulatory[0]));
        }
        let cohort_count = cohorts.len();
        let contact_count = fabric.contact_count();
        let remounted = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .map(|(mount, lineage)| (*lineage, mount.clone()))
            .collect::<Vec<_>>();

        mount_reached_articulatory_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[motor, ordering, regulation, acoustic],
            &remounted,
        )
        .unwrap();
        assert_eq!(cohorts.len(), cohort_count);
        assert_eq!(fabric.contact_count(), contact_count);
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
        let distinct_participant_count = fabric.contact_count();
        let distinct_remounted = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .map(|(mount, lineage)| (*lineage, mount.clone()))
            .collect::<Vec<_>>();
        mount_reached_articulatory_effector(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[second_acoustic, regulation, ordering, motor],
            &distinct_remounted,
        )
        .unwrap();
        assert_eq!(
            cohorts
                .iter()
                .flat_map(|cohort| cohort.anatomy.mounts())
                .filter(|mount| mount.place().layer() == 13)
                .count(),
            1
        );
        assert_eq!(fabric.contact_count(), distinct_participant_count + 1);
        assert!(fabric.contains_contact(second_acoustic, articulatory[0]));
        assert_eq!(
            population.as_ref().unwrap().resting_cell_count(),
            resting_before - 1
        );
    }

    #[test]
    fn non_simultaneous_body_and_sensory_activity_does_not_manufacture_effectors() {
        let canal_anatomy =
            CanalAnatomy::new(6, 13_200, PositiveRatio::new(25, 1).unwrap()).unwrap();
        let bundle_anatomy = LocalCupulaBundleAnatomy::new(2, 5, 20_000).unwrap();
        let receptor_anatomy = phase_one_virtual_vestibular_anatomy().unwrap();
        let mut state = ResidentCognitiveFormationState::default();
        let turn = settle_signed_yaw_actuation(
            YawBodyState::new(0).unwrap(),
            SignedYawActuation::new(90_000, 250_000).unwrap(),
        )
        .unwrap();
        let mut canal = CanalState::at_rest();
        let mut heading = 0_u32;
        let mut frontier_route_sets = Vec::new();
        for (source_tick, signed_step) in turn.trajectory.as_slice().iter().copied().enumerate() {
            let predecessor_body = YawBodyState::new(heading).unwrap();
            heading =
                u32::try_from((i64::from(heading) + i64::from(signed_step)).rem_euclid(360_000))
                    .unwrap();
            let successor_body = YawBodyState::new(heading).unwrap();
            let reached = settle_reached_vestibular_bundle_tick(
                canal_anatomy,
                canal,
                signed_step,
                bundle_anatomy,
            )
            .unwrap();
            canal = reached.successor_canal;
            let ingress = prepare_resident_vestibular_ingress(
                u64::try_from(source_tick).unwrap(),
                predecessor_body,
                successor_body,
                reached,
                &receptor_anatomy,
            )
            .unwrap();
            let vestibular = state
                .prepare_vestibular_transition(&ingress, 16_000_000)
                .unwrap();
            if !vestibular.observation.physical_frontier_routes.is_empty() {
                frontier_route_sets.push(vestibular.observation.physical_frontier_routes.clone());
            }
            state = vestibular.successor;
        }
        let source = exact_optical_binaural_episode();
        let mut motor_recruitments = Vec::new();
        let mut articulatory_recruitments = Vec::new();
        let mut repeated_optical_frontier_route_sets = Vec::new();
        for _ in 0..256 {
            let prepared = state.prepare(&source, 16_000_000).unwrap();
            motor_recruitments.extend(
                prepared
                    .observation
                    .motor_unit_recruitments
                    .iter()
                    .cloned(),
            );
            articulatory_recruitments.extend(
                prepared
                    .observation
                    .articulatory_unit_recruitments
                    .iter()
                    .cloned(),
            );
            if !prepared.observation.physical_frontier_routes.is_empty() {
                frontier_route_sets.push(prepared.observation.physical_frontier_routes.clone());
                repeated_optical_frontier_route_sets
                    .push(prepared.observation.physical_frontier_routes.clone());
            }
            state = prepared.successor;
        }
        let layer_ten = state
            .cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.mounts())
            .filter(|mount| mount.place().layer() == 10)
            .count();
        // The earlier receiver-only frontier accidentally made the separate
        // vestibular and later optical/acoustic episodes appear coincident.
        // With the exact advancing endpoint retained, this non-simultaneous
        // specimen must not manufacture a layer-10 association/body relation.
        assert_eq!(layer_ten, 0);
        let layer_eleven = state
            .cohorts
            .iter()
            .flat_map(|cohort| cohort.anatomy.mounts())
            .filter(|mount| mount.place().layer() == 11)
            .count();
        assert!(layer_eleven > 0);
        let layer_counts = state.observe_reached_neuron_count_by_layer();
        assert_eq!(
            layer_counts.iter().find(|(layer, _)| *layer == 11).copied(),
            Some((11, layer_eleven))
        );
        assert!(!layer_counts.iter().any(|(layer, _)| *layer == 12));
        assert!(!layer_counts.iter().any(|(layer, _)| *layer == 13));
        assert!(motor_recruitments.is_empty());
        assert!(articulatory_recruitments.is_empty());
        assert!(frontier_route_sets.iter().any(|routes| routes.len() > 1));
        assert!(frontier_route_sets
            .iter()
            .flatten()
            .any(|route| { route.outward_whole_carriers_from_seed() == 0 }));
        assert!(frontier_route_sets
            .iter()
            .flatten()
            .any(|route| { route.outward_whole_carriers_from_seed() > 0 }));
        assert!(frontier_route_sets
            .windows(2)
            .any(|pair| pair[0] != pair[1]));
        assert!(repeated_optical_frontier_route_sets
            .windows(2)
            .any(|pair| pair[0] != pair[1]));
        assert_eq!(
            layer_counts.iter().map(|(_, count)| *count).sum::<usize>(),
            state.summary().complete_neuron_count
        );
        let retained = state
            .mosaics
            .iter()
            .find(|retained| retained.recurrent_lineage.is_some())
            .unwrap();
        let retained_encoded = encode_retained_organism_mosaic(
            &state.cohorts,
            &state.electrical_fabric,
            retained,
            16_000_000,
        )
        .unwrap();
        assert_eq!(
            retained_encoded.get(..RETAINED_MOSAIC_RECURRENT_MAGIC.len()),
            Some(RETAINED_MOSAIC_RECURRENT_MAGIC.as_slice())
        );
        assert_eq!(
            decode_retained_organism_mosaic(
                &state.cohorts,
                &state.electrical_fabric,
                &retained_encoded,
                16_000_000,
            )
            .unwrap(),
            *retained
        );
        let mut altered_lineage = retained_encoded.clone();
        altered_lineage[RETAINED_MOSAIC_RECURRENT_MAGIC.len() + 16] ^= 0x80;
        assert!(matches!(
            decode_retained_organism_mosaic(
                &state.cohorts,
                &state.electrical_fabric,
                &altered_lineage,
                16_000_000,
            ),
            Err(FormationError::NeuronLineageAuthorityAbsent)
                | Err(FormationError::NeuronLineageAuthorityChanged)
        ));
        let mut legacy_state = state.clone();
        for retained in &mut legacy_state.mosaics {
            retained.recurrent_lineage = None;
        }
        let legacy_encoded = legacy_state.encode(16_000_000).unwrap();
        assert!(!legacy_encoded
            .windows(RETAINED_MOSAIC_RECURRENT_MAGIC.len())
            .any(|window| window == RETAINED_MOSAIC_RECURRENT_MAGIC));
        let legacy_cold =
            ResidentCognitiveFormationState::decode(&legacy_encoded, 16_000_000).unwrap();
        assert_eq!(legacy_cold, state);
        let encoded = state.encode(16_000_000).unwrap();
        let cold = ResidentCognitiveFormationState::decode(&encoded, 16_000_000).unwrap();
        assert_eq!(cold, state);
    }

    #[test]
    fn one_new_retained_mosaic_mounts_one_sparse_recurrent_route() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(16_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let members = (0..3)
            .map(|topology| {
                mount_intrinsic_neuron_at_place(
                    &mut cohorts,
                    &mut population,
                    &mut next_lineage,
                    DeclaredNeuronPlace::new(6, topology),
                )
                .unwrap()
            })
            .collect::<Vec<_>>();
        let mut fabric = ResidentElectricalFabric::default();
        mount_new_recurrent_retention(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[members.clone()],
        )
        .unwrap();
        let retention = cohorts
            .iter()
            .flat_map(|cohort| {
                cohort
                    .anatomy
                    .mounts()
                    .iter()
                    .zip(cohort.anatomy.neuron_lineages())
            })
            .filter(|(mount, _)| mount.place().layer() == 9)
            .map(|(_, lineage)| *lineage)
            .collect::<Vec<_>>();
        assert_eq!(retention.len(), 1);
        assert_eq!(fabric.contact_count(), members.len());
        assert!(members
            .iter()
            .all(|member| fabric.contains_contact(*member, retention[0])));

        let cohort_count = cohorts.len();
        let contact_count = fabric.contact_count();
        mount_new_recurrent_retention(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[],
        )
        .unwrap();
        assert_eq!(cohorts.len(), cohort_count);
        assert_eq!(fabric.contact_count(), contact_count);
    }

    #[test]
    fn newly_mounted_nested_formations_keep_distinct_recurrent_lineages() {
        let mut cohorts = Vec::new();
        let mut population =
            Some(DevelopmentalRestingPopulation::admit(16_000_000, 100_000, 100, &[]).unwrap());
        let mut next_lineage = 1;
        let members = (0..4)
            .map(|topology| {
                mount_intrinsic_neuron_at_place(
                    &mut cohorts,
                    &mut population,
                    &mut next_lineage,
                    DeclaredNeuronPlace::new(6, topology),
                )
                .unwrap()
            })
            .collect::<Vec<_>>();
        let narrow_members = members[..3].to_vec();
        let mut fabric = ResidentElectricalFabric::default();
        let mounted = mount_new_recurrent_retention(
            &mut cohorts,
            &mut population,
            &mut next_lineage,
            &mut fabric,
            &[narrow_members.clone(), members.clone()],
        )
        .unwrap();

        let retained_mosaic = |member_lineages: &[[u8; 16]]| {
            let fractal =
                crate::complete_neuron::SparsePhysicalStateDelta::from_canonical_entries(vec![
                    crate::complete_neuron::PhysicalStateDeltaEntry::new(
                        crate::complete_neuron::PhysicalStateCoordinate::PlasticRestLength,
                        crate::complete_neuron::ExactPhysicalStateDelta::Rational(
                            ExactRational::new(1, 3).unwrap(),
                        ),
                    )
                    .unwrap(),
                ])
                .unwrap();
            let bonds = member_lineages
                .windows(2)
                .map(|pair| StablePhysicalBondReference::new(pair[0], pair[1], 0).unwrap())
                .collect::<Vec<_>>();
            AdmittedPhysicalMosaic::from_parts_for_tests(
                member_lineages.to_vec(),
                vec![fractal; member_lineages.len()],
                bonds.clone(),
                bonds,
                vec![member_lineages[0]],
            )
        };
        assert_eq!(mounted.len(), 2);
        assert_ne!(mounted[0], mounted[1]);
        validate_recurrent_retention_lineage(&cohorts, &fabric, &narrow_members, mounted[0])
            .unwrap();
        validate_recurrent_retention_lineage(&cohorts, &fabric, &members, mounted[1]).unwrap();
        assert_eq!(fabric.contact_count(), narrow_members.len() + members.len());

        let narrow_mosaic = retained_mosaic(&narrow_members);
        let broad_mosaic = retained_mosaic(&members);
        let mut legacy = [
            RetainedOrganismMosaic::newly_admitted(narrow_mosaic.clone()),
            RetainedOrganismMosaic::newly_admitted(broad_mosaic),
        ];
        resolve_unpersisted_recurrent_retention(&cohorts, &fabric, &mut legacy).unwrap();
        assert_eq!(legacy[0].recurrent_lineage, Some(mounted[0]));
        assert_eq!(legacy[1].recurrent_lineage, Some(mounted[1]));

        let mut ambiguous = [
            RetainedOrganismMosaic::newly_admitted(narrow_mosaic.clone()),
            RetainedOrganismMosaic::newly_admitted(narrow_mosaic),
        ];
        assert!(matches!(
            resolve_unpersisted_recurrent_retention(&cohorts, &fabric, &mut ambiguous),
            Err(FormationError::NeuronLineageAuthorityChanged)
        ));
    }

    /// THE HEADLINE LAW, at the crate boundary: admitting a real physical
    /// mosaic — the thing that used to publish ~893 objects per reassembly —
    /// now creates NOTHING on disk, and the retired checkpoint does not move.
    ///
    /// This replaces `episode_by_reference_round_trips_through_directory_cold_custody`,
    /// which proved the opposite law (that a reassembly round-tripped through
    /// a content-addressed directory).  That law is retired by owner's order.
    #[test]
    #[ignore = "retired: fixture requires Boolean/member-set mosaic admission"]
    fn an_admitted_reassembly_writes_no_file_anywhere_and_moves_no_checkpoint() {
        let root = std::env::temp_dir().join(format!(
            "guala-no-archive-{}-{}",
            std::process::id(),
            line!(),
        ));
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(&root).unwrap();
        let entries_before = std::fs::read_dir(&root).unwrap().count();

        let mut state = lesson_state_with_retained_experience();
        let checkpoint_before = state.hippocampal;
        let partial = exact_four_partial_optical_episode();
        let dark = exact_four_dark_optical_episode();
        let sources = std::iter::once(&partial)
            .chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
            .collect::<Vec<_>>();
        let mut formed = 0usize;
        let mut reassemblies = 0usize;
        let mut endogenous_reassemblies = 0usize;
        for source in sources {
            let prepared = state
                .prepare_admitted_transition(&admitted_fixture_episode(source), 16_000_000)
                .unwrap();
            if prepared.observation.mosaic_formed.is_some() {
                formed += 1;
            }
            reassemblies += prepared.observation.partial_cue_reassembly_count;
            endogenous_reassemblies += prepared.observation.endogenous_partial_cue_reassembly_count;
            // The successor encodes and commits with no publication step.
            state.encode_successor(&prepared, 16_000_000).unwrap();
            state.commit(prepared).unwrap();
        }

        // Reassembly still happened — this is not a test of an inert path.
        // This fixture supplies one external partial cue; the cue's own
        // continuing contact tail is not mislabeled as endogenous activity.
        assert_eq!(formed, 1);
        assert_eq!(reassemblies, 1);
        assert_eq!(endogenous_reassemblies, 0);
        // And the file count did not move by one.
        assert_eq!(std::fs::read_dir(&root).unwrap().count(), entries_before);
        assert_eq!(state.hippocampal, checkpoint_before);
        assert!(!state.hippocampal.carries_retired_archive_reference());
        let _ = std::fs::remove_dir_all(&root);
    }

    #[test]
    fn retired_false_or_empty_cognitive_state_cannot_return() {
        for magic in [
            b"GLCOG003",
            b"GLCOG004",
            b"GLCOG005",
            b"GLCOG006",
            b"GLCOG007",
            b"GLCOG008",
            b"GLCOG009",
            b"GLCOG010",
        ] {
            let mut retired = Vec::from(magic.as_slice());
            retired.extend_from_slice(&4u16.to_le_bytes());
            assert_eq!(
                ResidentCognitiveFormationState::decode(&retired, 1_000_000),
                Err(FormationError::RetiredCognitiveState)
            );
        }
    }

    #[test]
    fn adjacent_exact_contact_transfers_are_the_only_ordered_path_evidence() {
        let first = [1_u8; 16];
        let via = [2_u8; 16];
        let last = [3_u8; 16];
        let first_bond = StablePhysicalBondReference::new(first, via, 0).unwrap();
        let second_bond = StablePhysicalBondReference::new(via, last, 0).unwrap();
        let predecessor =
            [ActiveElectricalFrontierEntry::caused(first, via, first_bond, 7).unwrap()];
        let current = [ActiveElectricalFrontierEntry::caused(via, last, second_bond, 5).unwrap()];
        let incidence = [(first, 0), (via, 0), (via, 1), (last, 1)];
        let paths =
            ordered_physical_paths_for_relation(&incidence, &[0, 1], &predecessor, &current);
        assert_eq!(paths.len(), 1);
        assert_eq!(
            paths[0].directed_transfers(),
            [(first, via, first_bond, 7), (via, last, second_bond, 5),]
        );

        assert_eq!(
            ActiveElectricalFrontierEntry::caused(first, last, second_bond, 5),
            Err(FormationError::NoncanonicalState)
        );
        assert!(ordered_physical_paths_for_relation(
            &incidence,
            &[0, 1],
            &[ActiveElectricalFrontierEntry::legacy_receiver(via)],
            &current,
        )
        .is_empty());
        assert!(ordered_physical_paths_for_relation(
            &incidence,
            &[0, 1],
            &predecessor,
            &[ActiveElectricalFrontierEntry::caused(last, via, second_bond, 5).unwrap()],
        )
        .is_empty());
    }

    #[test]
    fn working_causal_frontier_requires_unseeded_adjacent_continuation_and_expires() {
        let first = [1_u8; 16];
        let via = [2_u8; 16];
        let last = [3_u8; 16];
        let first_bond = StablePhysicalBondReference::new(first, via, 0).unwrap();
        let second_bond = StablePhysicalBondReference::new(via, last, 0).unwrap();
        let predecessor =
            [ActiveElectricalFrontierEntry::caused(first, via, first_bond, 7).unwrap()];
        let current = [ActiveElectricalFrontierEntry::caused(via, last, second_bond, 5).unwrap()];

        let (continued, settled) = working_causal_frontier_observation(&predecessor, &current, &[]);
        assert_eq!(continued.len(), 1);
        assert_eq!(
            continued[0].directed_transfers(),
            [(first, via, first_bond, 7), (via, last, second_bond, 5)]
        );
        assert!(settled.is_empty());

        // A current external/body/fluid seed at the intermediate cell makes
        // the second transfer causally ambiguous, so it cannot prove internal
        // continuation from the predecessor frontier.
        let (externally_reseeded, _) =
            working_causal_frontier_observation(&predecessor, &current, &[via]);
        assert!(externally_reseeded.is_empty());
        let (adjacent_reseeded, _) =
            working_causal_frontier_observation(&predecessor, &current, &[last]);
        assert!(adjacent_reseeded.is_empty());

        // With no onward whole-carrier transfer, the predecessor cause loses
        // propagation authority after exactly this adjacent interval.
        let (continued, settled) = working_causal_frontier_observation(&predecessor, &[], &[]);
        assert!(continued.is_empty());
        assert_eq!(settled.len(), 1);
        assert_eq!(
            (
                settled[0].sender,
                settled[0].receiver,
                settled[0].bond,
                settled[0].transferred_whole_carriers,
            ),
            (first, via, first_bond, 7)
        );

        // Historical receiver-only frontier entries can propagate physically
        // but cannot be promoted into directed causal evidence.
        let legacy = [ActiveElectricalFrontierEntry::legacy_receiver(via)];
        let (continued, settled) = working_causal_frontier_observation(&legacy, &current, &[]);
        assert!(continued.is_empty());
        assert!(settled.is_empty());
    }

    #[test]
    fn directed_transfer_frontier_preserves_direction_and_one_advancing_endpoint() {
        let sender = [1_u8; 16];
        let receiver = [2_u8; 16];
        let bond = StablePhysicalBondReference::new(sender, receiver, 0).unwrap();
        let transfer =
            ActiveElectricalFrontierEntry::caused(sender, receiver, bond, 7).unwrap();
        assert_eq!(transfer.affected_lineages(), [Some(receiver), None]);
        assert_eq!(
            transfer.directed_transfer(),
            Some(DirectedPhysicalTransferObservation {
                sender,
                receiver,
                bond,
                transferred_whole_carriers: 7,
            })
        );

        let reverse_frontier = ActiveElectricalFrontierEntry::caused_with_frontier(
            sender, receiver, sender, bond, 7,
        )
        .unwrap();
        assert_eq!(reverse_frontier.affected_lineages(), [Some(sender), None]);
        assert_eq!(reverse_frontier.directed_transfer(), transfer.directed_transfer());
        let mut encoded = Vec::new();
        reverse_frontier.encode_v20(&mut encoded);
        let mut cursor = 0;
        assert_eq!(
            ActiveElectricalFrontierEntry::decode_v20(&encoded, &mut cursor, true).unwrap(),
            reverse_frontier
        );
        assert_eq!(cursor, encoded.len());
        let mut cursor = 0;
        assert_eq!(
            ActiveElectricalFrontierEntry::decode_v20(&encoded, &mut cursor, false),
            Err(FormationError::NoncanonicalState)
        );

        let legacy = ActiveElectricalFrontierEntry::legacy_receiver(receiver);
        assert_eq!(legacy.affected_lineages(), [Some(receiver), None]);
    }

    #[test]
    fn physical_prediction_requires_two_unseeded_layer_eleven_routes_from_one_intrinsic_cause() {
        let intrinsic_cause = [1_u8; 16];
        let ordering_a = [2_u8; 16];
        let ordering_b = [3_u8; 16];
        let consequence_a = [4_u8; 16];
        let consequence_b = [5_u8; 16];
        let cause_a = StablePhysicalBondReference::new(intrinsic_cause, ordering_a, 0).unwrap();
        let cause_b = StablePhysicalBondReference::new(intrinsic_cause, ordering_b, 0).unwrap();
        let ordered_a = StablePhysicalBondReference::new(ordering_a, consequence_a, 0).unwrap();
        let ordered_b = StablePhysicalBondReference::new(ordering_b, consequence_b, 0).unwrap();
        let predecessor = [
            ActiveElectricalFrontierEntry::caused(intrinsic_cause, ordering_a, cause_a, 7).unwrap(),
            ActiveElectricalFrontierEntry::caused(intrinsic_cause, ordering_b, cause_b, 5).unwrap(),
        ];
        let current = [
            ActiveElectricalFrontierEntry::caused(ordering_a, consequence_a, ordered_a, 3).unwrap(),
            ActiveElectricalFrontierEntry::caused(ordering_b, consequence_b, ordered_b, 2).unwrap(),
        ];
        let layers = [
            (intrinsic_cause, 13),
            (ordering_a, 11),
            (ordering_b, 11),
            (consequence_a, 10),
            (consequence_b, 10),
        ];

        let alternatives =
            physical_prediction_alternatives_observation(&predecessor, &current, &[], &layers);
        assert_eq!(alternatives.len(), 2);
        assert_eq!(alternatives[0].directed_transfers()[0].0, intrinsic_cause);
        assert_eq!(alternatives[1].directed_transfers()[0].0, intrinsic_cause);
        assert_ne!(
            alternatives[0].directed_transfers()[1].1,
            alternatives[1].directed_transfers()[1].1
        );
        assert!(physical_prediction_alternatives_observation(
            &predecessor[..1],
            &current[..1],
            &[],
            &layers,
        )
        .is_empty());
        assert!(physical_prediction_alternatives_observation(
            &predecessor,
            &current,
            &[ordering_a],
            &layers,
        )
        .is_empty());
    }

    #[test]
    fn body_consequence_preserves_both_directions_on_the_reached_vestibular_relation() {
        let regulation = [6_u8; 16];
        let consequence = [7_u8; 16];
        let bond = StablePhysicalBondReference::new(regulation, consequence, 0).unwrap();
        let outward =
            [ActiveElectricalFrontierEntry::caused(regulation, consequence, bond, 11).unwrap()];
        let layers = [(regulation, 8), (consequence, 10)];
        let reached = [regulation];
        assert!(
            body_consequence_transfer_observation(&outward, &layers, &reached, false).is_empty()
        );
        let observed = body_consequence_transfer_observation(&outward, &layers, &reached, true);
        assert_eq!(observed.len(), 1);
        assert_eq!(
            (
                observed[0].sender,
                observed[0].receiver,
                observed[0].transferred_whole_carriers,
            ),
            (regulation, consequence, 11)
        );

        let inward =
            [ActiveElectricalFrontierEntry::caused(consequence, regulation, bond, 7).unwrap()];
        let observed = body_consequence_transfer_observation(&inward, &layers, &reached, true);
        assert_eq!(observed.len(), 1);
        assert_eq!(
            (
                observed[0].sender,
                observed[0].receiver,
                observed[0].transferred_whole_carriers,
            ),
            (consequence, regulation, 7)
        );
        assert!(body_consequence_transfer_observation(&inward, &layers, &[], true).is_empty());
    }

    #[test]
    fn two_recurring_ordered_paths_require_the_same_directed_physical_route() {
        let first = [1_u8; 16];
        let second = [2_u8; 16];
        let third = [3_u8; 16];
        let first_bond = StablePhysicalBondReference::new(first, second, 0).unwrap();
        let second_bond = StablePhysicalBondReference::new(second, third, 0).unwrap();
        let oldest =
            [
                ActiveElectricalFrontierEntry::caused(
            first,
            first_bond.endpoints().1,
            first_bond,
            7,
        )
                .unwrap(),
            ];
        let older = [ActiveElectricalFrontierEntry::caused(second, third, second_bond, 5).unwrap()];
        let preceding =
            [ActiveElectricalFrontierEntry::caused(first, second, first_bond, 9).unwrap()];
        let current =
            [ActiveElectricalFrontierEntry::caused(second, third, second_bond, 4).unwrap()];
        let incidence = [(first, 0), (second, 0), (second, 1), (third, 1)];
        let relations = ordered_path_relations_for_relation(
            &incidence,
            &[0, 1],
            &oldest,
            &older,
            &preceding,
            &current,
        );
        assert_eq!(relations.len(), 1);
        assert_eq!(
            relations[0].directed_transfers(),
            [
                (first, second, first_bond, 7),
                (second, third, second_bond, 5),
                (first, second, first_bond, 9),
                (second, third, second_bond, 4),
            ]
        );
        assert!(ordered_path_relations_for_relation(
            &incidence,
            &[0, 1],
            &[],
            &older,
            &preceding,
            &current,
        )
        .is_empty());
    }

    #[test]
    fn v19_recipient_only_frontier_migrates_without_inventing_direction() {
        let retired = ResidentCognitiveFormationState::default()
            .encode_with_format(CognitiveCodecFormat::V12, 16_000_000)
            .unwrap();
        let current =
            ResidentCognitiveFormationState::migrate_to_current_format(&retired, 16_000_000)
                .unwrap();
        let mut state = ResidentCognitiveFormationState::decode(&current, 16_000_000).unwrap();
        let mut cohorts = state.cohorts.to_vec();
        let mut population = state.resting_population.take();
        let mut next_lineage_ordinal = state.next_lineage_ordinal;
        let sender = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage_ordinal,
            DeclaredNeuronPlace::new(6, 0),
        )
        .unwrap();
        let receiver = mount_intrinsic_neuron_at_place(
            &mut cohorts,
            &mut population,
            &mut next_lineage_ordinal,
            DeclaredNeuronPlace::new(6, 1),
        )
        .unwrap();
        let electrical_fabric = ResidentElectricalFabric::default()
            .append_contact(
                sender,
                receiver,
                ExactRational::integer(DEVELOPMENTAL_CONTACT_CONDUCTANCE_PICOSIEMENS),
            )
            .unwrap();
        state.generation = 1;
        state.next_lineage_ordinal = next_lineage_ordinal;
        state.resting_population = population;
        state.cohorts = cohorts.into_boxed_slice();
        state.electrical_fabric = electrical_fabric;
        let bond = organism_mosaic_topology(&state.cohorts, &state.electrical_fabric)
            .unwrap()
            .bonds[0];
        state.active_electrical_frontier =
            vec![ActiveElectricalFrontierEntry::caused(sender, receiver, bond, 1).unwrap()]
                .into_boxed_slice();
        state.active_electrical_frontier = state
            .active_electrical_frontier
            .iter()
            .map(|entry| ActiveElectricalFrontierEntry::legacy_receiver(entry.receiver()))
            .collect::<Vec<_>>()
            .into_boxed_slice();
        let legacy = state
            .encode_with_format(CognitiveCodecFormat::V19, 16_000_000)
            .unwrap();
        let current =
            ResidentCognitiveFormationState::migrate_to_current_format(&legacy, 16_000_000)
                .unwrap();
        assert_eq!(&current[..MAGIC_V23.len()], MAGIC_V23);
        let cold = ResidentCognitiveFormationState::decode(&current, 16_000_000).unwrap();
        assert_eq!(cold.encode(16_000_000).unwrap(), current);
        assert!(!cold.active_electrical_frontier.is_empty());
        assert!(cold
            .active_electrical_frontier
            .iter()
            .all(|entry| entry.cause.is_none()));
    }
}
#[cfg(test)]
mod reservoir_probe;
