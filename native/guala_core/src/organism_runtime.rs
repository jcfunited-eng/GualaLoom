//! Smallest truthful native organism runtime step.
//!
//! One step consumes one current `GLORUN01` envelope and one authenticated
//! `NativeJointSourceEpisode`. The current `GLMFAB07` fabric retains exact
//! mounted joint-field delivery state and an explicit empty cognitive section.
//! A DSF delivery is not a neuronal fractal and cannot form cognition. Organism tick,
//! fabric generation, and mounted generation are independent local clocks;
//! each must be contiguous within its own mechanism and none is numerically
//! equated with another.
//!
//! This module makes no membrane, channel, fluid, physical-body,
//! motivation, action, or language claim. Retained hippocampal state is
//! exposed only as a read-only navigation surface (addresses and typed
//! participation; never recognition, recall, or meaning), and reading it
//! advances nothing. It performs no Python callback and owns no
//! persistence, owner, lock, or global clock.

use crate::articulated_body_joint_source_builder::{
    admit_articulated_body_proprioceptive_source, admit_complete_articulated_body_state_source,
};
use crate::complete_neuron::{ExactPhysicalStateDelta, PhysicalStateCoordinate};
use crate::developmental_electrical_anatomy::build_authored_growth_dna_seeds;
use crate::exact_rational::ExactRational;
use crate::joint_source_episode::NativeJointSourceEpisode;
#[cfg(test)]
use crate::joint_uf_source_adapter::admitted_fixture_episode;
use crate::joint_uf_source_adapter::{
    admitted_episode_with_authored_intervals, AdmittedJointSourceEpisode,
};
use crate::materialized_fabric::migrate_authenticated_glmfab03_to_current;
#[cfg(test)]
use crate::mounted_joint_fractal::transition_mounted_joint_dsf;
use crate::mounted_joint_fractal::{
    encode_empty_mounted_joint_state, inspect_mounted_joint_dsf_summary,
    prepare_resident_mounted_generation, restore_resident_mounted_state, MountedJointDsfSummary,
    MountedJointDsfTransition, MountedTransitionPhaseCounts, ResidentMountedRestoreWork,
    ResidentMountedState,
};
use crate::physical_mosaic::StablePhysicalBondReference;
use crate::reached_neuron_cohort::ReachedCohortEnergyState;
use crate::reached_vestibular_bundle_path::settle_reached_vestibular_bundle_tick;
use crate::resident_cognitive_formation::{
    coalesce_emitted_neuron_fractals, has_reached_and_foregone_frontier_routes,
    AffectiveBalanceTrajectoryObservation, ArticulatoryUnitRecruitment, AuthoredDeclaredContact,
    CausalFrontierTransferObservation, ChangedContactChannelStateObservation,
    CognitiveFormationObservation, CognitiveFormationSummary, DirectedPhysicalTransferObservation,
    EmittedNeuronFractal, ExternallyReassembledFormationFrontierObservation,
    InternallyReassembledFormationCueObservation, LocalizedFluidChemistryObservation,
    LocalizedMetabolicStrainObservation, MotorUnitRecruitment, OrderedPhysicalPathObservation,
    OrganicMosaicRelationObservation, PhysicalFrontierRouteObservation,
    PreparedCognitiveFormationTransition, ResidentCognitiveFormationState,
};
use crate::resident_receptor_transition::{
    observe_canonical_receptor_ingress, prepare_resident_vestibular_ingress,
    ResidentReceptorIngressObservation, ResidentVestibularIngress,
};
use crate::sha256::sha256;
use crate::vestibular_neuron_path::{
    decode_functional_vestibular_anatomy, encode_functional_vestibular_anatomy,
    phase_one_virtual_vestibular_anatomy, FunctionalVestibularAnatomy,
    FUNCTIONAL_VESTIBULAR_ANATOMY_CODEC_BYTES,
};
use crate::virtual_articulated_body::{
    settle_body_effector_drives, AdmittedBodyEffectorDrives, ArticulatedBodyState,
    ArticulatedBodyTransition, BodyEffectorDrive, BodyEffectorTerminal,
    BodyProprioceptiveConsequence, ARTICULATED_BODY_STATE_BYTES, BODY_AXES,
    BODY_EFFECTOR_TERMINAL_COUNT,
};
use crate::virtual_articulatory_body::{
    settle_articulatory_unit_discharge, ARTICULATORY_SAMPLE_RATE_HZ,
};
use crate::virtual_body_yaw_motion::{
    settle_signed_yaw_actuation, SignedYawActuation, YawBodyState,
};
use crate::virtual_vestibular_canal::{decode_canal_state, encode_canal_state, CanalState};
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::Zero;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::collections::{BTreeMap, VecDeque};
use std::fmt;
use std::sync::Arc;

const MAGIC: &[u8; 8] = b"GLORUN01";
const VERSION: u16 = 1;
const LEGACY_FABRIC_MAGIC: &[u8; 8] = b"GLMFAB04";
const LEGACY_FABRIC_VERSION: u16 = 4;
const PRE_VESTIBULAR_FABRIC_MAGIC: &[u8; 8] = b"GLMFAB07";
const PRE_VESTIBULAR_FABRIC_VERSION: u16 = 7;
const PRE_ARTICULATED_FABRIC_MAGIC: &[u8; 8] = b"GLMFAB08";
const PRE_ARTICULATED_FABRIC_VERSION: u16 = 8;
const FABRIC_MAGIC: &[u8; 8] = b"GLMFAB09";
const FABRIC_VERSION: u16 = 9;
const CANAL_STATE_BYTES: usize = 32;
const VESTIBULAR_BODY_BYTES: usize =
    FUNCTIONAL_VESTIBULAR_ANATOMY_CODEC_BYTES + CANAL_STATE_BYTES + std::mem::size_of::<u64>();

fn exact_energy_parts(value: &BigRational) -> (BigInt, BigInt) {
    (value.numer().clone(), value.denom().clone())
}
const IDENTITY_BYTES: usize = 36;
const FIXED_BYTES: usize = MAGIC.len()
    + std::mem::size_of::<u16>()
    + IDENTITY_BYTES
    + std::mem::size_of::<u64>()
    + std::mem::size_of::<u32>();
const FABRIC_FIXED_BYTES: usize = FABRIC_MAGIC.len()
    + std::mem::size_of::<u16>()
    + std::mem::size_of::<u64>()
    + std::mem::size_of::<u32>()
    + std::mem::size_of::<u32>()
    + VESTIBULAR_BODY_BYTES
    + ARTICULATED_BODY_STATE_BYTES;
const LEGACY_FABRIC_FIXED_BYTES: usize = LEGACY_FABRIC_MAGIC.len()
    + std::mem::size_of::<u16>()
    + std::mem::size_of::<u64>()
    + std::mem::size_of::<u32>();
const OBSERVATION_SCHEMA: &str = "guala.native.organism_runtime.observation.v5";
const MIGRATION_SCHEMA: &str = "guala.native.task853_organism_runtime_migration.v1";
const MIGRATION_SCOPE: &str = "authenticated_task853_predecessor_migration_only";
const RESIDENT_RUNTIME_SCHEMA: &str = "guala.native.resident_organism_runtime.v3";
const RESIDENT_OBSERVATION_SCHEMA: &str = "guala.native.resident_organism_observation.v3";
const RESIDENT_PREPARE_SCHEMA: &str = "guala.native.resident_organism_prepare.v3";
const PREPARE_TOKEN_MAGIC: &[u8; 8] = b"GLRTPN01";
const RESTORED_SCOPE: &str = "current_native_state_restored";
const MOUNTED_STEP_SCOPE: &str = "canonical_uf_v1_4_neuronal_settlement";
/// Scope name of one authored developmental contact growth.  A transaction
/// label, exactly like the two scopes above; it carries no physics.
const AUTHORED_CONTACT_GROWTH_SCOPE: &str = "authored_contact_growth_without_sensory_occurrence";
type DirectedPhysicalTransferProjection = (String, String, u32, String);
type CausalFrontierTransferProjection = (String, String, u32, String, String);
type InternallyReassembledFormationCueProjection = (String, Vec<String>);
type ExternallyReassembledFormationFrontierProjection = (String, Vec<String>, String);
type MotorUnitRecruitmentProjection = (
    String,
    u32,
    u128,
    Vec<(String, u32, String, u32, u32, u128)>,
    Vec<(String, String, String, u8, u32, String, String)>,
);
type ArticulatedBodyConsequenceProjection = (
    u64,
    String,
    String,
    i32,
    i32,
    i32,
    u128,
    u128,
    u128,
    u128,
    u128,
);
type OrderedPhysicalPathProjection = (
    DirectedPhysicalTransferProjection,
    DirectedPhysicalTransferProjection,
);
type OrderedPathRelationProjection = (
    DirectedPhysicalTransferProjection,
    DirectedPhysicalTransferProjection,
    DirectedPhysicalTransferProjection,
    DirectedPhysicalTransferProjection,
);
type OrganicMosaicRelationProjection = (
    Vec<String>,
    Vec<String>,
    Vec<(String, String, u32)>,
    String,
    Vec<OrderedPhysicalPathProjection>,
    Vec<OrderedPathRelationProjection>,
);
type PhysicalFrontierRouteProjection = (String, u32, u32, String, u32, u32, u32, i128);
type ExactRationalProjection = (String, String);
type ChangedContactChannelStateProjection = (
    u64,
    String,
    String,
    u32,
    (String, ExactRationalProjection, ExactRationalProjection),
    (String, ExactRationalProjection, ExactRationalProjection),
);
type TimedDirectedPhysicalTransferProjection = (u64, DirectedPhysicalTransferProjection);
type LocalAffectiveGradientSettlementProjection = (
    u64,
    i128,
    i128,
    i128,
    i128,
    i128,
    i128,
    ExactRationalProjection,
    ExactRationalProjection,
    ExactRationalProjection,
);
type LocalAffectivePlasticitySettlementProjection = (
    u64,
    String,
    String,
    ExactRationalProjection,
    ExactRationalProjection,
    ExactRationalProjection,
    ExactRationalProjection,
    ExactRationalProjection,
    (
        ExactRationalProjection,
        ExactRationalProjection,
        ExactRationalProjection,
    ),
    (
        ExactRationalProjection,
        ExactRationalProjection,
        ExactRationalProjection,
    ),
);
type AffectiveBalanceTrajectoryProjection = (
    String,
    u32,
    u32,
    Option<TimedDirectedPhysicalTransferProjection>,
    Option<TimedDirectedPhysicalTransferProjection>,
    Option<LocalAffectiveGradientSettlementProjection>,
    Option<LocalAffectivePlasticitySettlementProjection>,
);
type CausalIntervalEvidenceProjection = (
    Vec<String>,
    Vec<InternallyReassembledFormationCueProjection>,
    Vec<ExternallyReassembledFormationFrontierProjection>,
    Vec<MotorUnitRecruitmentProjection>,
    Vec<String>,
    Vec<ChangedContactChannelStateProjection>,
    Vec<AffectiveBalanceTrajectoryProjection>,
    Vec<CausalFrontierTransferProjection>,
);
type LocalizedFluidChemistryProjection = (
    String,
    u32,
    u32,
    u64,
    (
        u32,
        ExactRationalProjection,
        usize,
        usize,
        usize,
        usize,
        usize,
    ),
    (i128, i128, String, String, String, String, i128, i128),
    (
        (
            ExactRationalProjection,
            ExactRationalProjection,
            ExactRationalProjection,
        ),
        (
            ExactRationalProjection,
            ExactRationalProjection,
            ExactRationalProjection,
        ),
        ExactRationalProjection,
    ),
);
type LocalizedMetabolicStrainProjection = (String, u32, u32, u64, Vec<String>, String, String);
const TASK853_IDENTITY: &str = "1cc4e70a-f2a0-44c5-a111-f4a5bc915cc1";
const TASK853_ORGANISM_TICK: u64 = 23_723_846;
const TASK853_GLMFAB03_SHA256: [u8; 32] = [
    0xb1, 0xf5, 0x38, 0xe2, 0x5d, 0x0b, 0xf5, 0x95, 0x84, 0x26, 0x61, 0x72, 0xcc, 0xb4, 0x73, 0xb2,
    0xb2, 0xdb, 0x6a, 0xd7, 0xdd, 0xf1, 0xfc, 0x1f, 0x7f, 0xfa, 0x54, 0x2b, 0xd2, 0xcc, 0x7e, 0x14,
];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct RuntimeBudget {
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
}

impl RuntimeBudget {
    pub(crate) fn new(
        max_envelope_bytes: usize,
        max_fabric_bytes: usize,
        max_logical_peak_bytes: usize,
    ) -> Result<Self, RuntimeError> {
        let budget = Self {
            max_envelope_bytes,
            max_fabric_bytes,
            max_logical_peak_bytes,
        };
        budget.derive()?;
        Ok(budget)
    }

    fn derive(self) -> Result<DerivedRuntimeBudget, RuntimeError> {
        if self.max_envelope_bytes <= FIXED_BYTES || self.max_fabric_bytes <= FABRIC_FIXED_BYTES {
            return Err(RuntimeError::InvalidBudget);
        }
        let retained_envelopes = self
            .max_envelope_bytes
            .checked_mul(2)
            .ok_or(RuntimeError::BudgetArithmeticOverflow)?;
        let max_joint_working_bytes = self
            .max_logical_peak_bytes
            .checked_sub(retained_envelopes)
            .filter(|value| *value > 0)
            .ok_or(RuntimeError::InvalidBudget)?;
        Ok(DerivedRuntimeBudget {
            max_joint_state_bytes: self.max_fabric_bytes - FABRIC_FIXED_BYTES,
            max_joint_working_bytes,
            admitted_predecessor_envelope_bytes: self.max_envelope_bytes,
            admitted_successor_envelope_bytes: self.max_envelope_bytes,
            admitted_logical_peak_bytes: self.max_logical_peak_bytes,
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct DerivedRuntimeBudget {
    pub(crate) max_joint_state_bytes: usize,
    pub(crate) max_joint_working_bytes: usize,
    pub(crate) admitted_predecessor_envelope_bytes: usize,
    pub(crate) admitted_successor_envelope_bytes: usize,
    pub(crate) admitted_logical_peak_bytes: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) enum RuntimeError {
    InvalidBudget,
    BudgetArithmeticOverflow,
    EnvelopeBudgetExceeded,
    FabricBudgetExceeded,
    EnvelopeEndedEarly,
    BadEnvelopeMagic,
    UnsupportedEnvelopeVersion(u16),
    InvalidIdentity,
    FabricLengthOverflow,
    FabricLengthMismatch,
    BadFabricMagic,
    UnsupportedFabricVersion(u16),
    OrganismTickOverflow,
    FabricGenerationOverflow,
    MountedGenerationDiscontinuity,
    MountedSourceSubstitution,
    MountedTransition(String),
    LegacyMigration(String),
    Task853LegacyReceiptMismatch,
    Task853IdentityMismatch,
    Task853TickMismatch,
    MigrationInvariantChanged,
    PendingCandidateExists,
    PendingCandidateMissing,
    PendingTokenMismatch,
    PrepareTokenOrdinalOverflow,
    ResidentMountedInvariantChanged,
    CognitiveFormation(String),
    Vestibular(String),
    ArticulatedBody(String),
    /// The bare (unadmitted) source path stays severed by the
    /// mandatory-admission law.  It used to be refused for want of a cold
    /// custody port; cold custody is gone, so it is refused for the reason it
    /// was always really refused for.
    AdmittedSourceRequired,
    SealedStateChanged,
}

impl fmt::Display for RuntimeError {
    fn fmt(&self, output: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidBudget => write!(
                output,
                "organism runtime budget is not structurally sufficient"
            ),
            Self::BudgetArithmeticOverflow => {
                write!(output, "organism runtime budget arithmetic overflow")
            }
            Self::EnvelopeBudgetExceeded => {
                write!(output, "organism runtime envelope exceeds admitted bytes")
            }
            Self::FabricBudgetExceeded => {
                write!(output, "organism runtime fabric exceeds admitted bytes")
            }
            Self::EnvelopeEndedEarly => write!(output, "organism runtime envelope ended early"),
            Self::BadEnvelopeMagic => write!(output, "organism runtime envelope is not GLORUN01"),
            Self::UnsupportedEnvelopeVersion(version) => {
                write!(output, "unsupported organism runtime version {version}")
            }
            Self::InvalidIdentity => write!(output, "organism identity is not canonical UUID text"),
            Self::FabricLengthOverflow => {
                write!(output, "organism fabric length exceeds its canonical width")
            }
            Self::FabricLengthMismatch => write!(
                output,
                "organism runtime fabric length or trailing bytes changed"
            ),
            Self::BadFabricMagic => {
                write!(output, "organism fabric is neither GLMFAB07 nor GLMFAB04")
            }
            Self::UnsupportedFabricVersion(version) => {
                write!(output, "unsupported materialized fabric version {version}")
            }
            Self::OrganismTickOverflow => write!(output, "organism tick overflow"),
            Self::FabricGenerationOverflow => {
                write!(output, "materialized fabric generation overflow")
            }
            Self::MountedGenerationDiscontinuity => write!(
                output,
                "mounted joint-DSF generation is not locally contiguous"
            ),
            Self::MountedSourceSubstitution => {
                write!(output, "mounted joint-DSF source authority changed")
            }
            Self::MountedTransition(reason) => {
                write!(output, "mounted joint-DSF transition failed: {reason}")
            }
            Self::LegacyMigration(reason) => {
                write!(output, "authenticated legacy migration failed: {reason}")
            }
            Self::Task853LegacyReceiptMismatch => write!(
                output,
                "authenticated legacy receipt is not the task-853 predecessor receipt"
            ),
            Self::Task853IdentityMismatch => write!(
                output,
                "organism identity is not the authenticated task-853 identity"
            ),
            Self::Task853TickMismatch => write!(
                output,
                "organism tick is not the authenticated task-853 predecessor tick"
            ),
            Self::MigrationInvariantChanged => write!(
                output,
                "authenticated migration changed retained current-state authority"
            ),
            Self::PendingCandidateExists => {
                write!(
                    output,
                    "resident organism already has one pending candidate"
                )
            }
            Self::PendingCandidateMissing => {
                write!(output, "resident organism has no pending candidate")
            }
            Self::PendingTokenMismatch => {
                write!(output, "resident organism pending token does not match")
            }
            Self::PrepareTokenOrdinalOverflow => {
                write!(output, "resident organism prepare-token ordinal overflow")
            }
            Self::ResidentMountedInvariantChanged => write!(
                output,
                "resident mounted preparation violated decode, field, or clock continuity"
            ),
            Self::CognitiveFormation(reason) => {
                write!(output, "resident cognitive formation failed: {reason}")
            }
            Self::Vestibular(reason) => {
                write!(
                    output,
                    "resident body-and-balance transition failed: {reason}"
                )
            }
            Self::ArticulatedBody(reason) => {
                write!(output, "resident articulated body failed: {reason}")
            }
            Self::AdmittedSourceRequired => write!(
                output,
                "resident cognition requires an explicit admitted joint source episode"
            ),
            Self::SealedStateChanged => write!(
                output,
                "organism runtime state changed outside its admitted step"
            ),
        }
    }
}

impl std::error::Error for RuntimeError {}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct RuntimeObservation {
    pub(crate) schema: &'static str,
    pub(crate) scope: &'static str,
    pub(crate) identity: [u8; IDENTITY_BYTES],
    pub(crate) predecessor_state_receipt: Option<[u8; 32]>,
    pub(crate) predecessor_organism_tick: Option<u64>,
    pub(crate) organism_tick: u64,
    pub(crate) predecessor_fabric_generation: Option<u64>,
    pub(crate) fabric_generation: u64,
    pub(crate) predecessor_mounted_generation: Option<u64>,
    pub(crate) mounted_generation: u64,
    pub(crate) state_bytes: usize,
    pub(crate) state_receipt: [u8; 32],
    pub(crate) fabric_bytes: usize,
    pub(crate) fabric_receipt: [u8; 32],
    pub(crate) joint_field_count: usize,
    pub(crate) joint_neuron_count: usize,
    pub(crate) dsf_delivery_count: usize,
    pub(crate) complete_neuron_count: usize,
    /// Source-independent declared cells still held at exact quiescent rest.
    /// This is deliberately separate from reached complete neurons.
    pub(crate) developmental_resting_neuron_count: usize,
    pub(crate) physically_transitioned_neuron_count: usize,
    pub(crate) metabolically_perturbed_body_receptor_count: usize,
    pub(crate) externally_perturbed_body_receptor_count: usize,
    pub(crate) externally_perturbed_neuron_lineages: Vec<[u8; 16]>,
    pub(crate) complete_neuron_fractal_count: usize,
    pub(crate) emitted_neuron_fractals: Vec<EmittedNeuronFractal>,
    pub(crate) active_physical_bonds: Vec<StablePhysicalBondReference>,
    pub(crate) changed_contact_channel_states: Vec<ChangedContactChannelStateObservation>,
    pub(crate) physical_frontier_routes: Vec<PhysicalFrontierRouteObservation>,
    pub(crate) preceding_distinct_physical_frontier_routes: Vec<PhysicalFrontierRouteObservation>,
    pub(crate) reached_and_foregone_physical_frontier_routes: Vec<PhysicalFrontierRouteObservation>,
    pub(crate) working_causal_continuations: Vec<OrderedPhysicalPathObservation>,
    pub(crate) settled_working_frontier: Vec<DirectedPhysicalTransferObservation>,
    pub(crate) physical_prediction_alternatives: Vec<OrderedPhysicalPathObservation>,
    pub(crate) body_consequence_transfers: Vec<DirectedPhysicalTransferObservation>,
    pub(crate) affective_balance_trajectories: Vec<AffectiveBalanceTrajectoryObservation>,
    pub(crate) localized_fluid_chemistry: Vec<LocalizedFluidChemistryObservation>,
    pub(crate) localized_metabolic_strain_evaluated_body_receptor_lineages: Vec<[u8; 16]>,
    pub(crate) localized_metabolic_strain: Vec<LocalizedMetabolicStrainObservation>,
    pub(crate) organic_mosaic_relations: Vec<OrganicMosaicRelationObservation>,
    pub(crate) recurrent_complete_neuron_fractal_count: usize,
    pub(crate) source_cohort_l0_l4_evaluation_count: usize,
    pub(crate) successor_l0_l4_replay_count: usize,
    pub(crate) joint_transition_receipt: Option<[u8; 32]>,
    pub(crate) episode_relation_candidate_receipt: Option<[u8; 32]>,
    pub(crate) source_authority: Option<[u8; 32]>,
    pub(crate) mounted_step_completed: bool,
    pub(crate) physical_transition_claimed: bool,
    pub(crate) cognitive_formation_claimed: bool,
    pub(crate) cognitive_ordinal: u64,
    pub(crate) cognitive_trace_count: usize,
    pub(crate) cognitive_mosaic_count: usize,
    /// Total retained mosaic-of-mosaics relation events (memory law R1
    /// overlap branch) — retained state, present on restored observations.
    pub(crate) mosaic_of_mosaics_count: usize,
    pub(crate) formation_activation_count: usize,
    pub(crate) partial_cue_reassembly_count: usize,
    pub(crate) endogenous_partial_cue_reassembly_count: usize,
    pub(crate) internally_reassembled_formation_cues:
        Vec<InternallyReassembledFormationCueObservation>,
    pub(crate) externally_reassembled_formation_frontiers:
        Vec<ExternallyReassembledFormationFrontierObservation>,
    pub(crate) python_callback_count: u64,
    pub(crate) derived_budget: DerivedRuntimeBudget,
    /// The body's energy state and this transition's metabolic facts (minimal
    /// feeding metabolism, 2026-08-05).  Reported on every observation,
    /// including a plain restore, so an exhausted body can never be observed
    /// as a healthy one.
    pub(crate) energy: ReachedCohortEnergyState,
    pub(crate) rest_recovered_neuron_count: usize,
    /// Exact transition work that cleared occupied dissipation lanes and the
    /// exact demand that could not be accepted. These are transient observer
    /// facts, never a distress score or action authority.
    pub(crate) rest_drained_dissipation_quanta: u128,
    pub(crate) unmet_dissipation_quanta: u128,
    pub(crate) membrane_returned_elementary_charges: i128,
}

#[derive(Debug, Eq, PartialEq)]
pub(crate) struct SealedRuntimeState {
    pub(crate) bytes: Vec<u8>,
    pub(crate) receipt: [u8; 32],
}

#[derive(Debug, Eq, PartialEq)]
pub(crate) struct RuntimeStepResult {
    pub(crate) successor: SealedRuntimeState,
    pub(crate) observation: RuntimeObservation,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct NativeResidentD3Transition {
    successor: Vec<u8>,
    state_receipt: [u8; 32],
    source_authority: [u8; 32],
    complete_neuron_count: usize,
    complete_neuron_fractal_count: usize,
    cognitive_mosaic_count: usize,
    partial_cue_reassembly_count: usize,
    endogenous_partial_cue_reassembly_count: usize,
}

impl NativeResidentD3Transition {
    pub fn successor(&self) -> &[u8] {
        &self.successor
    }

    pub fn state_receipt(&self) -> [u8; 32] {
        self.state_receipt
    }

    pub fn source_authority(&self) -> [u8; 32] {
        self.source_authority
    }

    pub fn complete_neuron_count(&self) -> usize {
        self.complete_neuron_count
    }

    pub fn complete_neuron_fractal_count(&self) -> usize {
        self.complete_neuron_fractal_count
    }

    pub fn cognitive_mosaic_count(&self) -> usize {
        self.cognitive_mosaic_count
    }

    pub fn partial_cue_reassembly_count(&self) -> usize {
        self.partial_cue_reassembly_count
    }

    pub fn endogenous_partial_cue_reassembly_count(&self) -> usize {
        self.endogenous_partial_cue_reassembly_count
    }

    pub fn python_callback_count(&self) -> u64 {
        0
    }
}

#[pyclass(frozen, module = "guala_core")]
pub struct NativeOrganismRuntimeTransition {
    payload: Arc<[u8]>,
    observation: RuntimeObservation,
}

#[derive(Debug, Eq, PartialEq)]
struct AuthenticatedTask853RuntimeMigration {
    sealed: SealedRuntimeState,
    observation: RuntimeObservation,
    legacy_fabric_receipt: [u8; 32],
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct LegacyMigrationAuthority {
    identity: &'static str,
    organism_tick: u64,
    fabric_receipt: [u8; 32],
    fabric_generation: u64,
    mounted_generation: u64,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResidentVestibularBody {
    anatomy: FunctionalVestibularAnatomy,
    canal: CanalState,
    source_tick: u64,
}

impl ResidentVestibularBody {
    fn phase_one_genesis() -> Result<Self, RuntimeError> {
        Ok(Self {
            anatomy: phase_one_virtual_vestibular_anatomy()
                .map_err(|error| RuntimeError::Vestibular(format!("{error:?}")))?,
            canal: CanalState::at_rest(),
            source_tick: 0,
        })
    }
}

#[derive(Debug, Eq, PartialEq)]
struct ActiveResidentOrganismState {
    envelope: Vec<u8>,
    mounted: ResidentMountedState,
    cognitive: ResidentCognitiveFormationState,
    vestibular: ResidentVestibularBody,
    articulated_body: ArticulatedBodyState,
    observation: RuntimeObservation,
}

#[derive(Debug, Eq, PartialEq)]
struct PendingResidentOrganismState {
    token: [u8; 32],
    envelope: Vec<u8>,
    mounted: ResidentMountedState,
    cognitive: ResidentCognitiveFormationState,
    vestibular: ResidentVestibularBody,
    articulated_body: ArticulatedBodyState,
    observation: RuntimeObservation,
}

#[derive(Debug, Eq, PartialEq)]
struct UnacknowledgedDirectPredecessor {
    token: [u8; 32],
    envelope: Vec<u8>,
    next_prepare_ordinal: u64,
}

struct UnsealedResidentIntake {
    token: [u8; 32],
    predecessor: RuntimeObservation,
    predecessor_envelope: Vec<u8>,
    predecessor_next_prepare_ordinal: u64,
    cognitive: ResidentCognitiveFormationState,
    vestibular: ResidentVestibularBody,
    articulated_body: ArticulatedBodyState,
    cognitive_observation: Option<CognitiveFormationObservation>,
    receptor_ingress: ResidentReceptorIngressObservation,
    causal_interval_evidence: Vec<CausalIntervalEvidence>,
    articulated_body_consequences: Vec<TimedBodyProprioceptiveConsequence>,
    body_proprioceptive_sources: Vec<BodyProprioceptiveSourceReceipt>,
    causal_authority_entries: Vec<[u8; 32]>,
    pending_inputs: VecDeque<UnsealedCausalInput>,
    paused_motor_unit_recruitments: Option<Vec<MotorUnitRecruitment>>,
    paused_body_feedback: Option<UnsealedCausalInput>,
    paused_articulated_body_consequences: Vec<TimedBodyProprioceptiveConsequence>,
    appended_cognitive_observation: Option<CognitiveFormationObservation>,
    source_port_count: usize,
    source_occurrence_count: usize,
    processed_interval_count: usize,
    observed_articulated_body: bool,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum UnsealedInputScope {
    Causal,
    AppendedSelfHearing,
}

#[derive(Clone)]
enum UnsealedCausalInput {
    Admitted {
        source: NativeJointSourceEpisode,
        maximum_causal_intervals: Vec<(i64, i64)>,
        scope: UnsealedInputScope,
        body_feedback_depth: usize,
    },
    Vestibular {
        predecessor_heading_millidegrees: u32,
        signed_body_motion_millidegrees: i32,
        scope: UnsealedInputScope,
    },
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResidentPrepareReceipt {
    token: [u8; 32],
    observation: RuntimeObservation,
    phase_counts: MountedTransitionPhaseCounts,
    receptor_ingress: ResidentReceptorIngressObservation,
    motor_unit_recruitments: Vec<MotorUnitRecruitment>,
    articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
    causal_interval_evidence: Vec<CausalIntervalEvidence>,
    articulated_body_consequences: Vec<TimedBodyProprioceptiveConsequence>,
    body_proprioceptive_sources: Vec<BodyProprioceptiveSourceReceipt>,
    appended_physically_transitioned_neuron_count: usize,
    appended_complete_neuron_fractal_count: usize,
    appended_externally_perturbed_body_receptor_count: usize,
    appended_articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ResidentUnsealedIntakeReceipt {
    token: [u8; 32],
    provisional_organism_tick: u64,
    pause_interval_ordinal: Option<u64>,
    motor_unit_recruitments: Vec<MotorUnitRecruitment>,
    articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
    articulated_body: ArticulatedBodyState,
    articulated_body_consequences: Vec<TimedBodyProprioceptiveConsequence>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct TimedBodyProprioceptiveConsequence {
    source_tick: u64,
    consequence: BodyProprioceptiveConsequence,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct BodyProprioceptiveSourceReceipt {
    source_tick: u64,
    payload: Vec<u8>,
    port_count: usize,
    sample_count: usize,
    occurrence_count: usize,
    occurrence_frame_count: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct CausalIntervalEvidence {
    externally_perturbed_neuron_lineages: Vec<[u8; 16]>,
    internally_reassembled_formation_cues: Vec<InternallyReassembledFormationCueObservation>,
    externally_reassembled_formation_frontiers:
        Vec<ExternallyReassembledFormationFrontierObservation>,
    motor_unit_recruitments: Vec<MotorUnitRecruitment>,
    emitted_neuron_lineages: Vec<[u8; 16]>,
    changed_contact_channel_states: Vec<ChangedContactChannelStateObservation>,
    affective_balance_trajectories: Vec<AffectiveBalanceTrajectoryObservation>,
    frontier_advances: Vec<CausalFrontierTransferObservation>,
}

struct ResidentOrganismRuntime {
    active: ActiveResidentOrganismState,
    pending: Option<PendingResidentOrganismState>,
    direct_predecessor: Option<UnacknowledgedDirectPredecessor>,
    /// One unsealed external intake. It owns the typed working successor while
    /// Python performs only the irreducible body/acoustic transport needed to
    /// construct a data-dependent self-hearing source. No active state or
    /// durable CURRENT changes until the transaction is finally sealed.
    unsealed_intake: Option<UnsealedResidentIntake>,
    /// One prepared authored contact growth.  Like a feed it carries no
    /// sensory occurrence, so the mounted joint state and its generation
    /// travel through verbatim and only the cognitive body advances.
    pending_contact_growth: Option<PendingNutritionState>,
    budget: RuntimeBudget,
    next_prepare_ordinal: u64,
}

impl std::fmt::Debug for ResidentOrganismRuntime {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        formatter
            .debug_struct("ResidentOrganismRuntime")
            .field("active", &self.active)
            .field("pending", &self.pending)
            .field("direct_predecessor", &self.direct_predecessor)
            .field("has_unsealed_intake", &self.unsealed_intake.is_some())
            .field("pending_contact_growth", &self.pending_contact_growth)
            .field("budget", &self.budget)
            .field("next_prepare_ordinal", &self.next_prepare_ordinal)
            .finish()
    }
}

#[derive(Debug, Eq, PartialEq)]
struct PendingNutritionState {
    token: [u8; 32],
    envelope: Vec<u8>,
    cognitive: PreparedCognitiveFormationTransition,
    observation: RuntimeObservation,
}

#[pyclass(module = "guala_core")]
pub struct NativeResidentOrganismRuntime {
    runtime: ResidentOrganismRuntime,
}

#[pyclass(frozen, module = "guala_core")]
pub struct NativeResidentOrganismObservation {
    observation: RuntimeObservation,
    cold_restore_work: ResidentMountedRestoreWork,
    articulated_body: ArticulatedBodyState,
}

#[pyclass(frozen, module = "guala_core")]
pub struct NativeResidentOrganismPrepare {
    token: [u8; 32],
    observation: RuntimeObservation,
    phase_counts: MountedTransitionPhaseCounts,
    receptor_ingress: ResidentReceptorIngressObservation,
    motor_unit_recruitments: Vec<MotorUnitRecruitment>,
    articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
    causal_interval_evidence: Vec<CausalIntervalEvidence>,
    articulated_body_consequences: Vec<TimedBodyProprioceptiveConsequence>,
    body_proprioceptive_sources: Vec<BodyProprioceptiveSourceReceipt>,
    appended_physically_transitioned_neuron_count: usize,
    appended_complete_neuron_fractal_count: usize,
    appended_externally_perturbed_body_receptor_count: usize,
    appended_articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
}

#[pyclass(frozen, module = "guala_core")]
pub struct NativeResidentUnsealedIntake {
    token: [u8; 32],
    provisional_organism_tick: u64,
    pause_interval_ordinal: Option<u64>,
    motor_unit_recruitments: Vec<MotorUnitRecruitment>,
    articulatory_unit_recruitments: Vec<ArticulatoryUnitRecruitment>,
    articulated_body: ArticulatedBodyState,
    articulated_body_consequences: Vec<TimedBodyProprioceptiveConsequence>,
}

#[pyclass(frozen, module = "guala_core")]
pub struct NativeAuthenticatedTask853RuntimeMigration {
    payload: Arc<[u8]>,
    observation: RuntimeObservation,
    legacy_fabric_receipt: [u8; 32],
}

#[pymethods]
impl NativeAuthenticatedTask853RuntimeMigration {
    #[getter]
    fn schema(&self) -> &'static str {
        MIGRATION_SCHEMA
    }

    #[getter]
    fn scope(&self) -> &'static str {
        MIGRATION_SCOPE
    }

    #[getter]
    fn identity(&self) -> String {
        std::str::from_utf8(&self.observation.identity)
            .expect("validated canonical organism identity")
            .to_owned()
    }

    #[getter]
    fn authenticated_predecessor_organism_tick(&self) -> u64 {
        self.observation.organism_tick
    }

    #[getter]
    fn organism_tick(&self) -> u64 {
        self.observation.organism_tick
    }

    #[getter]
    fn legacy_fabric_sha256(&self) -> String {
        hex_digest(&self.legacy_fabric_receipt)
    }

    #[getter]
    fn state_bytes(&self) -> usize {
        self.observation.state_bytes
    }

    #[getter]
    fn state_sha256(&self) -> String {
        hex_digest(&self.observation.state_receipt)
    }

    #[getter]
    fn fabric_bytes(&self) -> usize {
        self.observation.fabric_bytes
    }

    #[getter]
    fn fabric_sha256(&self) -> String {
        hex_digest(&self.observation.fabric_receipt)
    }

    #[getter]
    fn fabric_generation(&self) -> u64 {
        self.observation.fabric_generation
    }

    #[getter]
    fn mounted_generation(&self) -> u64 {
        self.observation.mounted_generation
    }

    #[getter]
    fn joint_field_count(&self) -> usize {
        self.observation.joint_field_count
    }

    #[getter]
    fn joint_neuron_count(&self) -> usize {
        self.observation.joint_neuron_count
    }

    #[getter]
    fn complete_neuron_count(&self) -> usize {
        self.observation.complete_neuron_count
    }

    #[getter]
    fn developmental_resting_neuron_count(&self) -> usize {
        self.observation.developmental_resting_neuron_count
    }

    #[getter]
    fn physically_transitioned_neuron_count(&self) -> usize {
        self.observation.physically_transitioned_neuron_count
    }

    #[getter]
    fn mounted_step_completed(&self) -> bool {
        false
    }

    #[getter]
    fn physical_transition_claimed(&self) -> bool {
        false
    }

    #[getter]
    fn cognitive_formation_claimed(&self) -> bool {
        false
    }

    #[getter]
    fn python_callback_count(&self) -> u64 {
        0
    }

    fn as_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.payload)
    }
}

#[pymethods]
impl NativeResidentOrganismObservation {
    #[getter]
    fn schema(&self) -> &'static str {
        RESIDENT_OBSERVATION_SCHEMA
    }

    #[getter]
    fn identity(&self) -> String {
        std::str::from_utf8(&self.observation.identity)
            .expect("validated canonical organism identity")
            .to_owned()
    }

    #[getter]
    fn organism_tick(&self) -> u64 {
        self.observation.organism_tick
    }

    #[getter]
    fn fabric_generation(&self) -> u64 {
        self.observation.fabric_generation
    }

    #[getter]
    fn mounted_generation(&self) -> u64 {
        self.observation.mounted_generation
    }

    #[getter]
    fn state_bytes(&self) -> usize {
        self.observation.state_bytes
    }

    #[getter]
    fn state_sha256(&self) -> String {
        hex_digest(&self.observation.state_receipt)
    }

    #[getter]
    fn fabric_bytes(&self) -> usize {
        self.observation.fabric_bytes
    }

    #[getter]
    fn fabric_sha256(&self) -> String {
        hex_digest(&self.observation.fabric_receipt)
    }

    /// Read-only exact local body configuration. Anatomical identifiers are
    /// observation coordinates only; cognition cannot consume this surface.
    #[getter]
    fn articulated_body_axes(&self) -> Vec<(u8, String, String, i32, i32, i32, i32)> {
        BODY_AXES
            .iter()
            .copied()
            .map(|axis| {
                let anatomy = axis.anatomy();
                (
                    u8::try_from(axis.index()).expect("body axis count fits u8"),
                    axis.anatomical_name().to_owned(),
                    anatomy.unit.physical_name().to_owned(),
                    self.articulated_body.axis(axis),
                    anatomy.minimum,
                    anatomy.neutral,
                    anatomy.maximum,
                )
            })
            .collect()
    }

    #[getter]
    fn articulated_body_lung_air_microlitres(&self) -> u32 {
        self.articulated_body.lung_air_microlitres()
    }

    #[getter]
    fn articulated_body_vocal_tract_areas_square_millimetres(&self) -> Vec<i32> {
        self.articulated_body
            .vocal_tract_areas_square_millimetres()
            .to_vec()
    }

    #[getter]
    fn articulated_body_state_bytes(&self) -> usize {
        ArticulatedBodyState::resident_bytes()
    }

    #[getter]
    fn articulated_body_proprioception_initialized(&self) -> bool {
        self.articulated_body.proprioception_initialized()
    }

    #[getter]
    fn articulated_body_state_sha256(&self) -> String {
        let encoded = self
            .articulated_body
            .encode()
            .expect("resident articulated body was admitted before observation");
        hex_digest(&sha256(&encoded))
    }

    #[getter]
    fn joint_field_count(&self) -> usize {
        self.observation.joint_field_count
    }

    #[getter]
    fn joint_neuron_count(&self) -> usize {
        self.observation.joint_neuron_count
    }

    #[getter]
    fn complete_neuron_count(&self) -> usize {
        self.observation.complete_neuron_count
    }

    #[getter]
    fn developmental_resting_neuron_count(&self) -> usize {
        self.observation.developmental_resting_neuron_count
    }

    #[getter]
    fn physically_transitioned_neuron_count(&self) -> usize {
        self.observation.physically_transitioned_neuron_count
    }

    #[getter]
    fn cold_restore_authentication_count(&self) -> usize {
        self.cold_restore_work.authentication_count
    }

    #[getter]
    fn cold_restore_decode_count(&self) -> usize {
        self.cold_restore_work.decode_count
    }

    #[getter]
    fn cold_restore_rebuilt_field_count(&self) -> usize {
        self.cold_restore_work.rebuilt_predecessor_field_count
    }

    #[getter]
    fn mounted_step_completed(&self) -> bool {
        self.observation.mounted_step_completed
    }

    #[getter]
    fn physical_transition_claimed(&self) -> bool {
        self.observation.physical_transition_claimed
    }

    #[getter]
    fn cognitive_formation_claimed(&self) -> bool {
        self.observation.cognitive_formation_claimed
    }

    #[getter]
    fn cognitive_ordinal(&self) -> u64 {
        self.observation.cognitive_ordinal
    }

    #[getter]
    fn cognitive_trace_count(&self) -> usize {
        self.observation.cognitive_trace_count
    }

    #[getter]
    fn cognitive_mosaic_count(&self) -> usize {
        self.observation.cognitive_mosaic_count
    }

    #[getter]
    fn mosaic_of_mosaics_count(&self) -> usize {
        self.observation.mosaic_of_mosaics_count
    }

    #[getter]
    fn organic_mosaic_relations(&self) -> Vec<OrganicMosaicRelationProjection> {
        project_organic_mosaic_relations(&self.observation.organic_mosaic_relations)
    }

    #[getter]
    fn physical_frontier_routes(&self) -> Vec<PhysicalFrontierRouteProjection> {
        project_physical_frontier_routes(&self.observation.physical_frontier_routes)
    }

    #[getter]
    fn preceding_distinct_physical_frontier_routes(&self) -> Vec<PhysicalFrontierRouteProjection> {
        project_physical_frontier_routes(
            &self.observation.preceding_distinct_physical_frontier_routes,
        )
    }

    #[getter]
    fn reached_and_foregone_physical_frontier_routes(
        &self,
    ) -> Vec<PhysicalFrontierRouteProjection> {
        project_physical_frontier_routes(
            &self
                .observation
                .reached_and_foregone_physical_frontier_routes,
        )
    }

    #[getter]
    fn working_causal_continuations(&self) -> Vec<OrderedPhysicalPathProjection> {
        project_ordered_physical_paths(&self.observation.working_causal_continuations)
    }

    #[getter]
    fn settled_working_frontier(&self) -> Vec<DirectedPhysicalTransferProjection> {
        project_directed_physical_transfers(&self.observation.settled_working_frontier)
    }

    #[getter]
    fn physical_prediction_alternatives(&self) -> Vec<OrderedPhysicalPathProjection> {
        project_ordered_physical_paths(&self.observation.physical_prediction_alternatives)
    }

    #[getter]
    fn body_consequence_transfers(&self) -> Vec<DirectedPhysicalTransferProjection> {
        project_directed_physical_transfers(&self.observation.body_consequence_transfers)
    }

    #[getter]
    fn affective_balance_trajectories(&self) -> Vec<AffectiveBalanceTrajectoryProjection> {
        project_affective_balance_trajectories(&self.observation.affective_balance_trajectories)
    }

    #[getter]
    fn localized_fluid_chemistry(&self) -> Vec<LocalizedFluidChemistryProjection> {
        project_localized_fluid_chemistry(&self.observation.localized_fluid_chemistry)
    }

    #[getter]
    fn localized_metabolic_strain_evaluated_body_receptor_lineages(&self) -> Vec<String> {
        self.observation
            .localized_metabolic_strain_evaluated_body_receptor_lineages
            .iter()
            .map(|lineage| hex_bytes(lineage))
            .collect()
    }

    #[getter]
    fn localized_metabolic_strain(&self) -> Vec<LocalizedMetabolicStrainProjection> {
        project_localized_metabolic_strain(&self.observation.localized_metabolic_strain)
    }

    #[getter]
    fn formation_activation_count(&self) -> usize {
        self.observation.formation_activation_count
    }

    #[getter]
    fn partial_cue_reassembly_count(&self) -> usize {
        self.observation.partial_cue_reassembly_count
    }

    #[getter]
    fn endogenous_partial_cue_reassembly_count(&self) -> usize {
        self.observation.endogenous_partial_cue_reassembly_count
    }

    #[getter]
    fn internally_reassembled_formation_cues(
        &self,
    ) -> Vec<InternallyReassembledFormationCueProjection> {
        project_internally_reassembled_formation_cues(
            &self.observation.internally_reassembled_formation_cues,
        )
    }

    #[getter]
    fn externally_reassembled_formation_frontiers(
        &self,
    ) -> Vec<ExternallyReassembledFormationFrontierProjection> {
        project_externally_reassembled_formation_frontiers(
            &self.observation.externally_reassembled_formation_frontiers,
        )
    }

    #[getter]
    fn python_callback_count(&self) -> u64 {
        self.observation.python_callback_count
    }

    #[getter]
    fn available_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.available_energy_zeptojoules)
    }

    #[getter]
    fn spent_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.spent_energy_zeptojoules)
    }

    #[getter]
    fn thermal_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.thermal_energy_zeptojoules)
    }

    #[getter]
    fn available_energy_capacity_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(
            &self
                .observation
                .energy
                .available_energy_capacity_zeptojoules,
        )
    }

    #[getter]
    fn dissipation_capacity_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(
            &self
                .observation
                .energy
                .dissipation_capacity_energy_zeptojoules,
        )
    }

    #[getter]
    fn dissipated_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.dissipated_energy_zeptojoules)
    }

    #[getter]
    fn separated_elementary_charges(&self) -> i128 {
        self.observation.energy.separated_elementary_charges
    }

    #[getter]
    fn energy_exhausted(&self) -> bool {
        // A body with no mounted cohort has no energy system at all; that is
        // "no body", not exhaustion, and it is never reported as exhaustion.
        let zero = BigRational::zero();
        (self
            .observation
            .energy
            .available_energy_capacity_zeptojoules
            != zero
            && self.observation.energy.available_energy_zeptojoules == zero)
            || (self
                .observation
                .energy
                .dissipation_capacity_energy_zeptojoules
                != zero
                && self.observation.energy.dissipated_energy_zeptojoules
                    >= self
                        .observation
                        .energy
                        .dissipation_capacity_energy_zeptojoules)
    }

    #[getter]
    fn rest_recovered_neuron_count(&self) -> usize {
        self.observation.rest_recovered_neuron_count
    }

    #[getter]
    fn rest_drained_dissipation_quanta(&self) -> BigInt {
        BigInt::from(self.observation.rest_drained_dissipation_quanta)
    }

    #[getter]
    fn unmet_dissipation_quanta(&self) -> BigInt {
        BigInt::from(self.observation.unmet_dissipation_quanta)
    }

    #[getter]
    fn metabolically_perturbed_body_receptor_count(&self) -> usize {
        self.observation.metabolically_perturbed_body_receptor_count
    }

    #[getter]
    fn externally_perturbed_body_receptor_count(&self) -> usize {
        self.observation.externally_perturbed_body_receptor_count
    }

    #[getter]
    fn externally_perturbed_neuron_lineages(&self) -> Vec<String> {
        self.observation
            .externally_perturbed_neuron_lineages
            .iter()
            .map(|lineage| hex_bytes(lineage))
            .collect()
    }

    #[getter]
    fn membrane_returned_elementary_charges(&self) -> i128 {
        self.observation.membrane_returned_elementary_charges
    }
}

#[pymethods]
impl NativeResidentUnsealedIntake {
    #[getter]
    fn token<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.token)
    }

    #[getter]
    fn provisional_organism_tick(&self) -> u64 {
        self.provisional_organism_tick
    }

    #[getter]
    fn pause_interval_ordinal(&self) -> Option<u64> {
        self.pause_interval_ordinal
    }

    #[getter]
    fn motor_unit_recruitments(&self) -> Vec<MotorUnitRecruitmentProjection> {
        project_motor_unit_recruitments(&self.motor_unit_recruitments)
    }

    #[getter]
    fn body_effector_bindings(&self) -> Vec<(String, String, String, u128)> {
        self.motor_unit_recruitments
            .iter()
            .map(|recruitment| {
                let terminal = recruitment.body_effector_terminal;
                let direction = match terminal.direction() {
                    crate::virtual_articulated_body::BodyEffectorDirection::TowardMinimum => {
                        "toward_minimum"
                    }
                    crate::virtual_articulated_body::BodyEffectorDirection::TowardMaximum => {
                        "toward_maximum"
                    }
                };
                (
                    hex_bytes(&recruitment.neuron_lineage),
                    terminal.axis().anatomical_name().to_owned(),
                    direction.to_owned(),
                    recruitment.outward_elementary_carriers,
                )
            })
            .collect()
    }

    #[getter]
    fn articulated_body_axes(&self) -> Vec<(u8, String, String, i32, i32, i32, i32)> {
        BODY_AXES
            .iter()
            .copied()
            .map(|axis| {
                let anatomy = axis.anatomy();
                (
                    u8::try_from(axis.index()).expect("body axis count fits u8"),
                    axis.anatomical_name().to_owned(),
                    anatomy.unit.physical_name().to_owned(),
                    self.articulated_body.axis(axis),
                    anatomy.minimum,
                    anatomy.neutral,
                    anatomy.maximum,
                )
            })
            .collect()
    }

    #[getter]
    fn articulated_body_consequences(&self) -> Vec<ArticulatedBodyConsequenceProjection> {
        self.articulated_body_consequences
            .iter()
            .map(|timed| {
                let consequence = timed.consequence;
                (
                    timed.source_tick,
                    consequence.axis.anatomical_name().to_owned(),
                    consequence.unit.physical_name().to_owned(),
                    consequence.predecessor_position,
                    consequence.successor_position,
                    consequence.signed_displacement,
                    consequence.toward_minimum_carriers,
                    consequence.toward_maximum_carriers,
                    consequence.opposed_carriers_per_terminal,
                    consequence.applied_displacement_quanta,
                    consequence.stalled_carriers,
                )
            })
            .collect()
    }

    #[getter]
    fn articulatory_unit_recruitments(
        &self,
    ) -> Vec<(
        String,
        u32,
        u128,
        Vec<(String, u32, String, u32, u32, u128)>,
    )> {
        self.articulatory_unit_recruitments
            .iter()
            .map(|event| {
                (
                    hex_bytes(&event.neuron_lineage),
                    event.topology_index,
                    event.outward_elementary_carriers,
                    event
                        .motor_transfers
                        .iter()
                        .map(|transfer| {
                            let (sender_layer, receiver_layer) =
                                if transfer.sender == event.neuron_lineage {
                                    (13, 12)
                                } else {
                                    (12, 13)
                                };
                            (
                                hex_bytes(&transfer.sender),
                                sender_layer,
                                hex_bytes(&transfer.receiver),
                                receiver_layer,
                                transfer.bond.parallel_ordinal(),
                                transfer.transferred_whole_carriers,
                            )
                        })
                        .collect(),
                )
            })
            .collect()
    }
}

#[pymethods]
impl NativeResidentOrganismPrepare {
    #[getter]
    fn schema(&self) -> &'static str {
        RESIDENT_PREPARE_SCHEMA
    }

    #[getter]
    fn token<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.token)
    }

    #[getter]
    fn token_hex(&self) -> String {
        hex_digest(&self.token)
    }

    #[getter]
    fn predecessor_state_sha256(&self) -> Option<String> {
        self.observation
            .predecessor_state_receipt
            .as_ref()
            .map(hex_digest)
    }

    #[getter]
    fn prepared_state_sha256(&self) -> String {
        hex_digest(&self.observation.state_receipt)
    }

    #[getter]
    fn predecessor_organism_tick(&self) -> Option<u64> {
        self.observation.predecessor_organism_tick
    }

    #[getter]
    fn organism_tick(&self) -> u64 {
        self.observation.organism_tick
    }

    #[getter]
    fn predecessor_fabric_generation(&self) -> Option<u64> {
        self.observation.predecessor_fabric_generation
    }

    #[getter]
    fn fabric_generation(&self) -> u64 {
        self.observation.fabric_generation
    }

    #[getter]
    fn predecessor_mounted_generation(&self) -> Option<u64> {
        self.observation.predecessor_mounted_generation
    }

    #[getter]
    fn mounted_generation(&self) -> u64 {
        self.observation.mounted_generation
    }

    #[getter]
    fn predecessor_authentication_count(&self) -> usize {
        self.phase_counts.predecessor_authentication_count
    }

    #[getter]
    fn predecessor_decode_count(&self) -> usize {
        self.phase_counts.predecessor_decode_count
    }

    #[getter]
    fn predecessor_rebuilt_field_count(&self) -> usize {
        self.phase_counts.predecessor_rebuilt_field_count
    }

    #[getter]
    fn current_cohort_evaluation_count(&self) -> usize {
        self.phase_counts.current_cohort_evaluation_count
    }

    #[getter]
    fn causal_interval_count(&self) -> usize {
        self.causal_interval_evidence.len().max(1)
    }

    #[getter]
    fn reached_source_port_count(&self) -> usize {
        self.phase_counts.reached_neuron_lookup_count
    }

    #[getter]
    fn successor_seal_count(&self) -> usize {
        self.phase_counts.successor_seal_count
    }

    /// Transient native efferent events derived during this candidate. The
    /// exact outward whole-carrier discharge remains the authority; reading
    /// this projection stores and advances nothing.
    #[getter]
    fn motor_unit_recruitments(&self) -> Vec<MotorUnitRecruitmentProjection> {
        project_motor_unit_recruitments(&self.motor_unit_recruitments)
    }

    /// Exact typed motor-to-terminal bindings retained on the motor mounts.
    /// Afferent receptor ancestry and topology never select a terminal.
    #[getter]
    fn body_effector_bindings(&self) -> Vec<(String, String, String, u128)> {
        self.motor_unit_recruitments
            .iter()
            .map(|recruitment| {
                let terminal = recruitment.body_effector_terminal;
                let direction = match terminal.direction() {
                    crate::virtual_articulated_body::BodyEffectorDirection::TowardMinimum => {
                        "toward_minimum"
                    }
                    crate::virtual_articulated_body::BodyEffectorDirection::TowardMaximum => {
                        "toward_maximum"
                    }
                };
                (
                    hex_bytes(&recruitment.neuron_lineage),
                    terminal.axis().anatomical_name().to_owned(),
                    direction.to_owned(),
                    recruitment.outward_elementary_carriers,
                )
            })
            .collect()
    }

    /// Sparse physical body successor facts. These are observation only; the
    /// persisted successor body remains the authority.
    #[getter]
    fn articulated_body_consequences(&self) -> Vec<ArticulatedBodyConsequenceProjection> {
        self.articulated_body_consequences
            .iter()
            .map(|timed| {
                let consequence = timed.consequence;
                (
                    timed.source_tick,
                    consequence.axis.anatomical_name().to_owned(),
                    consequence.unit.physical_name().to_owned(),
                    consequence.predecessor_position,
                    consequence.successor_position,
                    consequence.signed_displacement,
                    consequence.toward_minimum_carriers,
                    consequence.toward_maximum_carriers,
                    consequence.opposed_carriers_per_terminal,
                    consequence.applied_displacement_quanta,
                    consequence.stalled_carriers,
                )
            })
            .collect()
    }

    /// Exact GLJSRC03 proprioceptive occurrence for the next causal organism
    /// interval. Python may transport these bytes but cannot choose meaning.
    #[getter]
    fn body_proprioceptive_sources<'py>(&self, py: Python<'py>) -> Vec<Bound<'py, PyBytes>> {
        self.body_proprioceptive_sources
            .iter()
            .map(|source| PyBytes::new(py, &source.payload))
            .collect()
    }

    #[getter]
    fn body_proprioceptive_source_extents(&self) -> Vec<(u64, usize, usize, usize, usize)> {
        self.body_proprioceptive_sources
            .iter()
            .map(|source| {
                (
                    source.source_tick,
                    source.port_count,
                    source.sample_count,
                    source.occurrence_count,
                    source.occurrence_frame_count,
                )
            })
            .collect()
    }

    /// Exact per-interval causal observation retained only for the lifetime of
    /// one prepared trajectory. The final successor still has one seal; these
    /// bounded records preserve the intervening sparse frontiers so a later
    /// read-only observer does not flatten several physical intervals into one.
    #[getter]
    fn causal_interval_evidence(&self) -> Vec<CausalIntervalEvidenceProjection> {
        self.causal_interval_evidence
            .iter()
            .map(|interval| {
                (
                    interval
                        .externally_perturbed_neuron_lineages
                        .iter()
                        .map(|lineage| hex_bytes(lineage))
                        .collect(),
                    project_internally_reassembled_formation_cues(
                        &interval.internally_reassembled_formation_cues,
                    ),
                    project_externally_reassembled_formation_frontiers(
                        &interval.externally_reassembled_formation_frontiers,
                    ),
                    project_motor_unit_recruitments(&interval.motor_unit_recruitments),
                    interval
                        .emitted_neuron_lineages
                        .iter()
                        .map(|lineage| hex_bytes(lineage))
                        .collect(),
                    project_changed_contact_channel_states(
                        &interval.changed_contact_channel_states,
                    ),
                    project_affective_balance_trajectories(
                        &interval.affective_balance_trajectories,
                    ),
                    project_causal_frontier_transfers(&interval.frontier_advances),
                )
            })
            .collect()
    }

    /// Transient native layer-13 efferent events. Each event is projected
    /// only with the exact direct layer-12 contact transfers that physically
    /// prepared it; no label, phoneme, word, or stored program is introduced.
    #[getter]
    fn articulatory_unit_recruitments(
        &self,
    ) -> Vec<(
        String,
        u32,
        u128,
        Vec<(String, u32, String, u32, u32, u128)>,
    )> {
        self.articulatory_unit_recruitments
            .iter()
            .map(|event| {
                (
                    hex_bytes(&event.neuron_lineage),
                    event.topology_index,
                    event.outward_elementary_carriers,
                    event
                        .motor_transfers
                        .iter()
                        .map(|transfer| {
                            let (sender_layer, receiver_layer) =
                                if transfer.sender == event.neuron_lineage {
                                    (13, 12)
                                } else {
                                    (12, 13)
                                };
                            (
                                hex_bytes(&transfer.sender),
                                sender_layer,
                                hex_bytes(&transfer.receiver),
                                receiver_layer,
                                transfer.bond.parallel_ordinal(),
                                transfer.transferred_whole_carriers,
                            )
                        })
                        .collect(),
                )
            })
            .collect()
    }

    #[getter]
    fn appended_physically_transitioned_neuron_count(&self) -> usize {
        self.appended_physically_transitioned_neuron_count
    }

    #[getter]
    fn appended_complete_neuron_fractal_count(&self) -> usize {
        self.appended_complete_neuron_fractal_count
    }

    #[getter]
    fn appended_externally_perturbed_body_receptor_count(&self) -> usize {
        self.appended_externally_perturbed_body_receptor_count
    }

    #[getter]
    fn appended_articulatory_unit_recruitment_count(&self) -> usize {
        self.appended_articulatory_unit_recruitments.len()
    }

    #[getter]
    fn receptor_ingress_field_count(&self) -> usize {
        self.receptor_ingress.field_count()
    }

    #[getter]
    fn receptor_ingress_witness_count(&self) -> usize {
        self.receptor_ingress.witness_count()
    }

    #[getter]
    fn receptor_ingress_sense_counts(&self) -> (usize, usize, usize, usize, usize, usize) {
        let counts = self.receptor_ingress.sense_counts();
        (
            counts[0], counts[1], counts[2], counts[3], counts[4], counts[5],
        )
    }

    #[getter]
    fn receptor_ingress_changing_count(&self) -> usize {
        self.receptor_ingress.changing_count()
    }

    #[getter]
    fn receptor_ingress_quiescent_count(&self) -> usize {
        self.receptor_ingress.quiescent_count()
    }

    #[getter]
    fn receptor_ingress_reached_neuron_visit_count(&self) -> usize {
        self.receptor_ingress.reached_neuron_visit_count()
    }

    #[getter]
    fn receptor_ingress_witness_construction_count(&self) -> usize {
        self.receptor_ingress.witness_construction_count()
    }

    #[getter]
    fn dsf_delivery_count(&self) -> usize {
        self.observation.dsf_delivery_count
    }

    #[getter]
    fn complete_neuron_fractal_count(&self) -> usize {
        self.observation.complete_neuron_fractal_count
    }

    /// Exact sparse post-quiescence neuronal deltas emitted by this prepared
    /// transition. Reading this transient evidence stores and advances
    /// nothing; each lineage and coordinate remains independently visible.
    #[getter]
    fn emitted_neuron_fractals(
        &self,
    ) -> PyResult<Vec<(String, Vec<(String, usize, bool, String, String)>)>> {
        self.observation
            .emitted_neuron_fractals
            .iter()
            .map(|fractal| {
                let entries = fractal
                    .delta
                    .entries()
                    .iter()
                    .map(|entry| {
                        let (coordinate, index) = match entry.coordinate() {
                            PhysicalStateCoordinate::PsiWinding(index) => ("psi-winding", index),
                            PhysicalStateCoordinate::GateOpenPopulation => {
                                ("gate-open-population", 0)
                            }
                            PhysicalStateCoordinate::PlasticRestLength => {
                                ("plastic-rest-length", 0)
                            }
                            PhysicalStateCoordinate::DnaExpressedProduct => {
                                ("dna-expressed-product", 0)
                            }
                            PhysicalStateCoordinate::ReceptorQuantumResidue => {
                                ("receptor-quantum-residue", 0)
                            }
                            _ => {
                                return Err(PyValueError::new_err(
                                    "neuronal fractal carried a transient coordinate",
                                ));
                            }
                        };
                        let (negative, magnitude, denominator) = match entry.delta() {
                            ExactPhysicalStateDelta::Integral(delta) => {
                                let (negative, magnitude) = delta.parts();
                                (negative, magnitude.to_string(), "1".to_owned())
                            }
                            ExactPhysicalStateDelta::Rational(delta) => {
                                let (numerator, denominator) = delta.parts();
                                (
                                    numerator.is_negative(),
                                    numerator.unsigned_abs().to_string(),
                                    denominator.to_string(),
                                )
                            }
                            ExactPhysicalStateDelta::Energy(_) => {
                                return Err(PyValueError::new_err(
                                    "neuronal fractal carried retained energy",
                                ));
                            }
                        };
                        Ok((
                            coordinate.to_owned(),
                            index,
                            negative,
                            magnitude,
                            denominator,
                        ))
                    })
                    .collect::<PyResult<Vec<_>>>()?;
                Ok((hex_bytes(&fractal.neuron_lineage), entries))
            })
            .collect()
    }

    /// Exact sparse contacts that carried current in this prepared native
    /// transition. Reading the transient witness stores and advances nothing.
    #[getter]
    fn active_physical_bonds(&self) -> Vec<(String, String, u32)> {
        self.observation
            .active_physical_bonds
            .iter()
            .map(|bond| {
                let (left, right) = bond.endpoints();
                (hex_bytes(&left), hex_bytes(&right), bond.parallel_ordinal())
            })
            .collect()
    }

    #[getter]
    fn changed_contact_channel_states(&self) -> Vec<ChangedContactChannelStateProjection> {
        project_changed_contact_channel_states(&self.observation.changed_contact_channel_states)
    }

    #[getter]
    fn physical_frontier_routes(&self) -> Vec<PhysicalFrontierRouteProjection> {
        project_physical_frontier_routes(&self.observation.physical_frontier_routes)
    }

    #[getter]
    fn preceding_distinct_physical_frontier_routes(&self) -> Vec<PhysicalFrontierRouteProjection> {
        project_physical_frontier_routes(
            &self.observation.preceding_distinct_physical_frontier_routes,
        )
    }

    #[getter]
    fn reached_and_foregone_physical_frontier_routes(
        &self,
    ) -> Vec<PhysicalFrontierRouteProjection> {
        project_physical_frontier_routes(
            &self
                .observation
                .reached_and_foregone_physical_frontier_routes,
        )
    }

    #[getter]
    fn working_causal_continuations(&self) -> Vec<OrderedPhysicalPathProjection> {
        project_ordered_physical_paths(&self.observation.working_causal_continuations)
    }

    #[getter]
    fn settled_working_frontier(&self) -> Vec<DirectedPhysicalTransferProjection> {
        project_directed_physical_transfers(&self.observation.settled_working_frontier)
    }

    #[getter]
    fn physical_prediction_alternatives(&self) -> Vec<OrderedPhysicalPathProjection> {
        project_ordered_physical_paths(&self.observation.physical_prediction_alternatives)
    }

    #[getter]
    fn body_consequence_transfers(&self) -> Vec<DirectedPhysicalTransferProjection> {
        project_directed_physical_transfers(&self.observation.body_consequence_transfers)
    }

    #[getter]
    fn affective_balance_trajectories(&self) -> Vec<AffectiveBalanceTrajectoryProjection> {
        project_affective_balance_trajectories(&self.observation.affective_balance_trajectories)
    }

    #[getter]
    fn localized_fluid_chemistry(&self) -> Vec<LocalizedFluidChemistryProjection> {
        project_localized_fluid_chemistry(&self.observation.localized_fluid_chemistry)
    }

    #[getter]
    fn localized_metabolic_strain_evaluated_body_receptor_lineages(&self) -> Vec<String> {
        self.observation
            .localized_metabolic_strain_evaluated_body_receptor_lineages
            .iter()
            .map(|lineage| hex_bytes(lineage))
            .collect()
    }

    #[getter]
    fn localized_metabolic_strain(&self) -> Vec<LocalizedMetabolicStrainProjection> {
        project_localized_metabolic_strain(&self.observation.localized_metabolic_strain)
    }

    #[getter]
    fn complete_neuron_count(&self) -> usize {
        self.observation.complete_neuron_count
    }

    #[getter]
    fn developmental_resting_neuron_count(&self) -> usize {
        self.observation.developmental_resting_neuron_count
    }

    #[getter]
    fn physically_transitioned_neuron_count(&self) -> usize {
        self.observation.physically_transitioned_neuron_count
    }

    #[getter]
    fn recurrent_complete_neuron_fractal_count(&self) -> usize {
        self.observation.recurrent_complete_neuron_fractal_count
    }

    #[getter]
    fn physical_transition_claimed(&self) -> bool {
        self.observation.physical_transition_claimed
    }

    #[getter]
    fn cognitive_formation_claimed(&self) -> bool {
        self.observation.cognitive_formation_claimed
    }

    #[getter]
    fn cognitive_ordinal(&self) -> u64 {
        self.observation.cognitive_ordinal
    }

    #[getter]
    fn cognitive_trace_count(&self) -> usize {
        self.observation.cognitive_trace_count
    }

    #[getter]
    fn cognitive_mosaic_count(&self) -> usize {
        self.observation.cognitive_mosaic_count
    }

    #[getter]
    fn mosaic_of_mosaics_count(&self) -> usize {
        self.observation.mosaic_of_mosaics_count
    }

    #[getter]
    fn organic_mosaic_relations(&self) -> Vec<OrganicMosaicRelationProjection> {
        project_organic_mosaic_relations(&self.observation.organic_mosaic_relations)
    }

    #[getter]
    fn formation_activation_count(&self) -> usize {
        self.observation.formation_activation_count
    }

    #[getter]
    fn partial_cue_reassembly_count(&self) -> usize {
        self.observation.partial_cue_reassembly_count
    }

    #[getter]
    fn endogenous_partial_cue_reassembly_count(&self) -> usize {
        self.observation.endogenous_partial_cue_reassembly_count
    }

    #[getter]
    fn internally_reassembled_formation_cues(
        &self,
    ) -> Vec<InternallyReassembledFormationCueProjection> {
        project_internally_reassembled_formation_cues(
            &self.observation.internally_reassembled_formation_cues,
        )
    }

    #[getter]
    fn externally_reassembled_formation_frontiers(
        &self,
    ) -> Vec<ExternallyReassembledFormationFrontierProjection> {
        project_externally_reassembled_formation_frontiers(
            &self.observation.externally_reassembled_formation_frontiers,
        )
    }

    #[getter]
    fn python_callback_count(&self) -> u64 {
        0
    }

    #[getter]
    fn available_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.available_energy_zeptojoules)
    }

    #[getter]
    fn spent_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.spent_energy_zeptojoules)
    }

    #[getter]
    fn thermal_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.thermal_energy_zeptojoules)
    }

    #[getter]
    fn available_energy_capacity_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(
            &self
                .observation
                .energy
                .available_energy_capacity_zeptojoules,
        )
    }

    #[getter]
    fn dissipated_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(&self.observation.energy.dissipated_energy_zeptojoules)
    }

    #[getter]
    fn dissipation_capacity_energy_zeptojoules(&self) -> (BigInt, BigInt) {
        exact_energy_parts(
            &self
                .observation
                .energy
                .dissipation_capacity_energy_zeptojoules,
        )
    }

    #[getter]
    fn separated_elementary_charges(&self) -> i128 {
        self.observation.energy.separated_elementary_charges
    }

    #[getter]
    fn rest_recovered_neuron_count(&self) -> usize {
        self.observation.rest_recovered_neuron_count
    }

    #[getter]
    fn rest_drained_dissipation_quanta(&self) -> BigInt {
        BigInt::from(self.observation.rest_drained_dissipation_quanta)
    }

    #[getter]
    fn unmet_dissipation_quanta(&self) -> BigInt {
        BigInt::from(self.observation.unmet_dissipation_quanta)
    }

    #[getter]
    fn metabolically_perturbed_body_receptor_count(&self) -> usize {
        self.observation.metabolically_perturbed_body_receptor_count
    }

    #[getter]
    fn externally_perturbed_body_receptor_count(&self) -> usize {
        self.observation.externally_perturbed_body_receptor_count
    }

    #[getter]
    fn externally_perturbed_neuron_lineages(&self) -> Vec<String> {
        self.observation
            .externally_perturbed_neuron_lineages
            .iter()
            .map(|lineage| hex_bytes(lineage))
            .collect()
    }

    #[getter]
    fn membrane_returned_elementary_charges(&self) -> i128 {
        self.observation.membrane_returned_elementary_charges
    }
}

#[pymethods]
impl NativeOrganismRuntimeTransition {
    #[getter]
    fn schema(&self) -> &'static str {
        self.observation.schema
    }

    #[getter]
    fn scope(&self) -> &'static str {
        self.observation.scope
    }

    #[getter]
    fn identity(&self) -> String {
        std::str::from_utf8(&self.observation.identity)
            .expect("validated canonical organism identity")
            .to_owned()
    }

    #[getter]
    fn predecessor_state_sha256(&self) -> Option<String> {
        self.observation
            .predecessor_state_receipt
            .as_ref()
            .map(hex_digest)
    }

    #[getter]
    fn predecessor_organism_tick(&self) -> Option<u64> {
        self.observation.predecessor_organism_tick
    }

    #[getter]
    fn organism_tick(&self) -> u64 {
        self.observation.organism_tick
    }

    #[getter]
    fn predecessor_fabric_generation(&self) -> Option<u64> {
        self.observation.predecessor_fabric_generation
    }

    #[getter]
    fn fabric_generation(&self) -> u64 {
        self.observation.fabric_generation
    }

    #[getter]
    fn predecessor_mounted_generation(&self) -> Option<u64> {
        self.observation.predecessor_mounted_generation
    }

    #[getter]
    fn mounted_generation(&self) -> u64 {
        self.observation.mounted_generation
    }

    #[getter]
    fn state_bytes(&self) -> usize {
        self.observation.state_bytes
    }

    #[getter]
    fn state_sha256(&self) -> String {
        hex_digest(&self.observation.state_receipt)
    }

    #[getter]
    fn fabric_bytes(&self) -> usize {
        self.observation.fabric_bytes
    }

    #[getter]
    fn fabric_sha256(&self) -> String {
        hex_digest(&self.observation.fabric_receipt)
    }

    #[getter]
    fn joint_field_count(&self) -> usize {
        self.observation.joint_field_count
    }

    #[getter]
    fn joint_neuron_count(&self) -> usize {
        self.observation.joint_neuron_count
    }

    #[getter]
    fn dsf_delivery_count(&self) -> usize {
        self.observation.dsf_delivery_count
    }

    #[getter]
    fn complete_neuron_fractal_count(&self) -> usize {
        self.observation.complete_neuron_fractal_count
    }

    #[getter]
    fn complete_neuron_count(&self) -> usize {
        self.observation.complete_neuron_count
    }

    #[getter]
    fn developmental_resting_neuron_count(&self) -> usize {
        self.observation.developmental_resting_neuron_count
    }

    #[getter]
    fn physically_transitioned_neuron_count(&self) -> usize {
        self.observation.physically_transitioned_neuron_count
    }

    #[getter]
    fn recurrent_complete_neuron_fractal_count(&self) -> usize {
        self.observation.recurrent_complete_neuron_fractal_count
    }

    #[getter]
    fn source_cohort_l0_l4_evaluation_count(&self) -> usize {
        self.observation.source_cohort_l0_l4_evaluation_count
    }

    #[getter]
    fn successor_l0_l4_replay_count(&self) -> usize {
        self.observation.successor_l0_l4_replay_count
    }

    #[getter]
    fn joint_transition_sha256(&self) -> Option<String> {
        self.observation
            .joint_transition_receipt
            .as_ref()
            .map(hex_digest)
    }

    #[getter]
    fn episode_relation_candidate_sha256(&self) -> Option<String> {
        self.observation
            .episode_relation_candidate_receipt
            .as_ref()
            .map(hex_digest)
    }

    #[getter]
    fn source_sha256(&self) -> Option<String> {
        self.observation.source_authority.as_ref().map(hex_digest)
    }

    #[getter]
    fn mounted_step_completed(&self) -> bool {
        self.observation.mounted_step_completed
    }

    #[getter]
    fn physical_transition_claimed(&self) -> bool {
        self.observation.physical_transition_claimed
    }

    #[getter]
    fn cognitive_formation_claimed(&self) -> bool {
        self.observation.cognitive_formation_claimed
    }

    #[getter]
    fn cognitive_ordinal(&self) -> u64 {
        self.observation.cognitive_ordinal
    }

    #[getter]
    fn cognitive_trace_count(&self) -> usize {
        self.observation.cognitive_trace_count
    }

    #[getter]
    fn cognitive_mosaic_count(&self) -> usize {
        self.observation.cognitive_mosaic_count
    }

    #[getter]
    fn mosaic_of_mosaics_count(&self) -> usize {
        self.observation.mosaic_of_mosaics_count
    }

    #[getter]
    fn organic_mosaic_relations(&self) -> Vec<OrganicMosaicRelationProjection> {
        project_organic_mosaic_relations(&self.observation.organic_mosaic_relations)
    }

    #[getter]
    fn formation_activation_count(&self) -> usize {
        self.observation.formation_activation_count
    }

    #[getter]
    fn partial_cue_reassembly_count(&self) -> usize {
        self.observation.partial_cue_reassembly_count
    }

    #[getter]
    fn endogenous_partial_cue_reassembly_count(&self) -> usize {
        self.observation.endogenous_partial_cue_reassembly_count
    }

    #[getter]
    fn internally_reassembled_formation_cues(
        &self,
    ) -> Vec<InternallyReassembledFormationCueProjection> {
        project_internally_reassembled_formation_cues(
            &self.observation.internally_reassembled_formation_cues,
        )
    }

    #[getter]
    fn externally_reassembled_formation_frontiers(
        &self,
    ) -> Vec<ExternallyReassembledFormationFrontierProjection> {
        project_externally_reassembled_formation_frontiers(
            &self.observation.externally_reassembled_formation_frontiers,
        )
    }

    #[getter]
    fn python_callback_count(&self) -> u64 {
        self.observation.python_callback_count
    }

    #[getter]
    fn derived_budget(&self) -> (usize, usize, usize, usize, usize) {
        let budget = self.observation.derived_budget;
        (
            budget.max_joint_state_bytes,
            budget.max_joint_working_bytes,
            budget.admitted_predecessor_envelope_bytes,
            budget.admitted_successor_envelope_bytes,
            budget.admitted_logical_peak_bytes,
        )
    }

    fn as_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.payload)
    }
}

fn retain_trajectory_relation_witnesses(
    retained: &mut Vec<OrganicMosaicRelationObservation>,
    observed: &[OrganicMosaicRelationObservation],
) {
    for relation in observed {
        if let Some(prior) = retained
            .iter_mut()
            .find(|prior| prior.structural_relation_receipt == relation.structural_relation_receipt)
        {
            let earliest_ordered_witness = if prior.ordered_physical_paths.is_empty() {
                relation.ordered_physical_paths.clone()
            } else {
                prior.ordered_physical_paths.clone()
            };
            let earliest_deep_ordered_witness = if prior.ordered_path_relations.is_empty() {
                relation.ordered_path_relations.clone()
            } else {
                prior.ordered_path_relations.clone()
            };
            *prior = relation.clone();
            prior.ordered_physical_paths = earliest_ordered_witness;
            prior.ordered_path_relations = earliest_deep_ordered_witness;
        } else {
            retained.push(relation.clone());
        }
    }
}

fn retain_affective_balance_trajectory_evidence(
    retained: &mut Vec<AffectiveBalanceTrajectoryObservation>,
    observed: &[AffectiveBalanceTrajectoryObservation],
) {
    for observation in observed {
        let index = match retained
            .binary_search_by_key(&observation.neuron_lineage, |entry| entry.neuron_lineage)
        {
            Ok(index) => index,
            Err(index) => {
                retained.insert(index, observation.clone());
                index
            }
        };
        let entry = &mut retained[index];
        if entry.neuron_place != observation.neuron_place {
            continue;
        }
        if entry.association_influence.is_none() {
            entry.association_influence = observation.association_influence;
        }
        if entry.body_influence.is_none() {
            entry.body_influence = observation.body_influence;
        }
        let influence_ordinal = entry
            .association_influence
            .zip(entry.body_influence)
            .map(|(association, body)| association.cognitive_ordinal.max(body.cognitive_ordinal));
        if entry
            .localized_gradient_settlement
            .zip(influence_ordinal)
            .is_some_and(|(gradient, influence)| gradient.cognitive_ordinal <= influence)
        {
            entry.localized_gradient_settlement = None;
        }
        if entry.localized_gradient_settlement.is_none() {
            if let Some(gradient) = observation.localized_gradient_settlement {
                if influence_ordinal.is_none_or(|influence| gradient.cognitive_ordinal > influence)
                {
                    entry.localized_gradient_settlement = Some(gradient);
                }
            }
        }
    }
}

fn retain_localized_fluid_chemistry_evidence(
    retained: &mut Vec<LocalizedFluidChemistryObservation>,
    observed: &[LocalizedFluidChemistryObservation],
) {
    let retained_is_multi_neuron = retained.first().is_some_and(|entry| {
        entry.unchanged_unreached_neuron_count != 0
            || entry.unchanged_developmental_resting_neuron_count != 0
    });
    if retained_is_multi_neuron {
        return;
    }
    let selected = observed
        .iter()
        .find(|entry| {
            entry.unchanged_unreached_neuron_count != 0
                || entry.unchanged_developmental_resting_neuron_count != 0
        })
        .or_else(|| observed.first())
        .copied();
    if let Some(selected) = selected {
        retained.clear();
        retained.push(selected);
    }
}

fn retain_localized_metabolic_strain_evidence(
    retained_evaluated_lineages: &mut Vec<[u8; 16]>,
    retained: &mut Vec<LocalizedMetabolicStrainObservation>,
    observed_evaluated_lineages: &[[u8; 16]],
    observed: &[LocalizedMetabolicStrainObservation],
) {
    for lineage in observed_evaluated_lineages {
        retained.retain(|entry| entry.neuron_lineage != *lineage);
        if let Some(observation) = observed
            .iter()
            .find(|entry| entry.neuron_lineage == *lineage)
        {
            retained.push(observation.clone());
        }
        if !retained_evaluated_lineages.contains(lineage) {
            retained_evaluated_lineages.push(*lineage);
        }
    }
    retained_evaluated_lineages.sort_unstable();
    retained.sort_unstable_by_key(|entry| entry.neuron_lineage);
}

fn retain_cognitive_trajectory_observation(
    aggregate: &mut Option<CognitiveFormationObservation>,
    observation: CognitiveFormationObservation,
) -> Result<(), RuntimeError> {
    let Some(total) = aggregate.as_mut() else {
        let mut initial = observation;
        initial.settled_working_frontier.clear();
        initial.body_consequence_transfers.clear();
        for trajectory in &mut initial.affective_balance_trajectories {
            if trajectory
                .localized_gradient_settlement
                .zip(trajectory.association_influence)
                .is_some_and(|(gradient, influence)| {
                    gradient.cognitive_ordinal <= influence.cognitive_ordinal
                })
                || trajectory
                    .localized_gradient_settlement
                    .zip(trajectory.body_influence)
                    .is_some_and(|(gradient, influence)| {
                        gradient.cognitive_ordinal <= influence.cognitive_ordinal
                    })
            {
                trajectory.localized_gradient_settlement = None;
            }
        }
        *aggregate = Some(initial);
        return Ok(());
    };

    total.trace_formed |= observation.trace_formed;
    if observation.mosaic_formed.is_some() {
        total.mosaic_formed = observation.mosaic_formed;
    }
    total
        .activations
        .extend(observation.activations.iter().cloned());
    total.dsf_delivery_count = total
        .dsf_delivery_count
        .checked_add(observation.dsf_delivery_count)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    total.physically_transitioned_neuron_count = total
        .physically_transitioned_neuron_count
        .checked_add(observation.physically_transitioned_neuron_count)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    total.metabolically_perturbed_body_receptor_count = total
        .metabolically_perturbed_body_receptor_count
        .checked_add(observation.metabolically_perturbed_body_receptor_count)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    total.externally_perturbed_body_receptor_count = total
        .externally_perturbed_body_receptor_count
        .checked_add(observation.externally_perturbed_body_receptor_count)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    for lineage in &observation.externally_perturbed_neuron_lineages {
        if !total.externally_perturbed_neuron_lineages.contains(lineage) {
            total.externally_perturbed_neuron_lineages.push(*lineage);
        }
    }
    total
        .emitted_neuron_fractals
        .extend(observation.emitted_neuron_fractals.iter().cloned());
    total.emitted_neuron_fractals =
        coalesce_emitted_neuron_fractals(std::mem::take(&mut total.emitted_neuron_fractals))
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
    total.complete_neuron_fractal_count = total.emitted_neuron_fractals.len();
    for change in &observation.changed_contact_channel_states {
        if !total
            .changed_contact_channel_states
            .iter()
            .any(|retained| retained.bond == change.bond)
        {
            total.changed_contact_channel_states.push(*change);
        }
    }
    total
        .motor_unit_recruitments
        .extend(observation.motor_unit_recruitments.iter().cloned());
    total
        .articulatory_unit_recruitments
        .extend(observation.articulatory_unit_recruitments.iter().cloned());
    if observation.physical_frontier_routes != total.physical_frontier_routes {
        total.preceding_distinct_physical_frontier_routes = total.physical_frontier_routes.clone();
        total.physical_frontier_routes = observation.physical_frontier_routes.clone();
    }
    if total
        .reached_and_foregone_physical_frontier_routes
        .is_empty()
        && has_reached_and_foregone_frontier_routes(&observation.physical_frontier_routes)
    {
        total.reached_and_foregone_physical_frontier_routes =
            observation.physical_frontier_routes.clone();
    }
    let selected_continuation_now = total.working_causal_continuations.is_empty()
        && !observation.working_causal_continuations.is_empty();
    if selected_continuation_now {
        total.working_causal_continuations = observation.working_causal_continuations.clone();
    }
    if !selected_continuation_now && total.settled_working_frontier.is_empty() {
        if let Some(path) = total.working_causal_continuations.first() {
            let [_, continued_transfer] = path.directed_transfers();
            let sent_onward = observation
                .physical_frontier_routes
                .iter()
                .any(|route| route.directed_sender() == Some(continued_transfer.1));
            if !sent_onward {
                total.settled_working_frontier = vec![DirectedPhysicalTransferObservation {
                    sender: continued_transfer.0,
                    receiver: continued_transfer.1,
                    bond: continued_transfer.2,
                    transferred_whole_carriers: continued_transfer.3,
                }];
            }
        }
    }
    let prediction_preceded_this_interval = !total.physical_prediction_alternatives.is_empty();
    if total.physical_prediction_alternatives.is_empty()
        && !observation.physical_prediction_alternatives.is_empty()
    {
        total.physical_prediction_alternatives =
            observation.physical_prediction_alternatives.clone();
    }
    if prediction_preceded_this_interval
        && total.body_consequence_transfers.is_empty()
        && !observation.body_consequence_transfers.is_empty()
    {
        total.body_consequence_transfers = observation.body_consequence_transfers.clone();
    }
    retain_affective_balance_trajectory_evidence(
        &mut total.affective_balance_trajectories,
        &observation.affective_balance_trajectories,
    );
    retain_localized_fluid_chemistry_evidence(
        &mut total.localized_fluid_chemistry,
        &observation.localized_fluid_chemistry,
    );
    retain_localized_metabolic_strain_evidence(
        &mut total.localized_metabolic_strain_evaluated_body_receptor_lineages,
        &mut total.localized_metabolic_strain,
        &observation.localized_metabolic_strain_evaluated_body_receptor_lineages,
        &observation.localized_metabolic_strain,
    );
    retain_trajectory_relation_witnesses(
        &mut total.organic_mosaic_relations,
        &observation.organic_mosaic_relations,
    );
    total.partial_cue_reassembly_count = total
        .partial_cue_reassembly_count
        .checked_add(observation.partial_cue_reassembly_count)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    total.endogenous_partial_cue_reassembly_count = total
        .endogenous_partial_cue_reassembly_count
        .checked_add(observation.endogenous_partial_cue_reassembly_count)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    for cue in &observation.internally_reassembled_formation_cues {
        if !total.internally_reassembled_formation_cues.contains(cue) {
            total
                .internally_reassembled_formation_cues
                .push(cue.clone());
        }
    }
    for frontier in &observation.externally_reassembled_formation_frontiers {
        if !total
            .externally_reassembled_formation_frontiers
            .contains(frontier)
        {
            total
                .externally_reassembled_formation_frontiers
                .push(frontier.clone());
        }
    }
    total.rest_recovered_neuron_count = total
        .rest_recovered_neuron_count
        .checked_add(observation.rest_recovered_neuron_count)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    total.rest_drained_dissipation_quanta = total
        .rest_drained_dissipation_quanta
        .checked_add(observation.rest_drained_dissipation_quanta)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    total.unmet_dissipation_quanta = total
        .unmet_dissipation_quanta
        .checked_add(observation.unmet_dissipation_quanta)
        .ok_or(RuntimeError::OrganismTickOverflow)?;
    total.cognitive_ordinal = observation.cognitive_ordinal;
    total.trace_count = observation.trace_count;
    total.mosaic_count = observation.mosaic_count;
    total.complete_neuron_count = observation.complete_neuron_count;
    total.resting_neuron_count = observation.resting_neuron_count;
    total.mosaic_of_mosaics_count = observation.mosaic_of_mosaics_count;
    total.energy = observation.energy;
    total.membrane_returned_elementary_charges = observation.membrane_returned_elementary_charges;
    total.membrane_unreturned_elementary_charges =
        observation.membrane_unreturned_elementary_charges;
    Ok(())
}

impl ResidentOrganismRuntime {
    fn restore_envelope(envelope: Vec<u8>, budget: RuntimeBudget) -> Result<Self, RuntimeError> {
        let derived_budget = budget.derive()?;
        let (mounted, cognitive, vestibular, articulated_body, observation) =
            {
                let parsed = parse_current_envelope(&envelope, budget)?;
                let vestibular =
                    parsed
                        .vestibular
                        .clone()
                        .ok_or(RuntimeError::UnsupportedFabricVersion(
                            PRE_VESTIBULAR_FABRIC_VERSION,
                        ))?;
                let articulated_body = parsed.articulated_body.clone().ok_or(
                    RuntimeError::UnsupportedFabricVersion(PRE_ARTICULATED_FABRIC_VERSION),
                )?;
                let (mounted, summary) = restore_resident_mounted_state(
                    parsed.joint_bytes,
                    derived_budget.max_joint_state_bytes,
                    derived_budget.max_joint_working_bytes,
                )
                .map_err(RuntimeError::MountedTransition)?;
                let cognitive = restore_cognitive_state(&parsed, budget)?;
                let observation = make_restored_observation(
                    &envelope,
                    parsed,
                    summary,
                    cognitive.summary(),
                    cognitive
                        .mosaic_of_mosaics_count()
                        .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?,
                    derived_budget,
                );
                (
                    mounted,
                    cognitive,
                    vestibular,
                    articulated_body,
                    observation,
                )
            };
        Ok(Self {
            active: ActiveResidentOrganismState {
                envelope,
                mounted,
                cognitive,
                vestibular,
                articulated_body,
                observation,
            },
            pending: None,
            direct_predecessor: None,
            unsealed_intake: None,
            pending_contact_growth: None,
            budget,
            next_prepare_ordinal: 1,
        })
    }

    fn prepare_source(
        &mut self,
        source: &NativeJointSourceEpisode,
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        // The mandatory-admission law: a bare source episode carries no
        // occurrence admissions, so the cognitive boundary refuses it below.
        self.prepare_typed(source, None, None, false)
    }

    fn prepare_articulated_body_observation(
        &mut self,
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        let source = admit_complete_articulated_body_state_source(
            self.active.observation.organism_tick,
            &self.active.articulated_body,
        )
        .map_err(|error| RuntimeError::ArticulatedBody(format!("{error:?}")))?;
        let intervals = vec![(1_i64, 1_000_i64); BODY_AXES.len()];
        let admitted = admitted_episode_with_authored_intervals(&source, &intervals)
            .map_err(RuntimeError::CognitiveFormation)?;
        let prepared = self.prepare_typed(&source, Some(&admitted), None, true)?;
        if prepared.motor_unit_recruitments.is_empty() {
            return Ok(prepared);
        }
        self.pending = None;
        Err(RuntimeError::CognitiveFormation(
            "a body-observation motor discharge requires the unsealed action-consequence boundary"
                .into(),
        ))
    }

    fn prepare_vestibular_tick(
        &mut self,
        predecessor_heading_millidegrees: u32,
        signed_body_motion_millidegrees: i32,
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        self.prepare_vestibular_trajectory(
            predecessor_heading_millidegrees,
            std::slice::from_ref(&signed_body_motion_millidegrees),
        )
    }

    fn begin_unsealed_intake_direct(
        &mut self,
        vestibular: Option<(u32, &[i32])>,
        episodes: &[(NativeJointSourceEpisode, Vec<(i64, i64)>)],
    ) -> Result<ResidentUnsealedIntakeReceipt, RuntimeError> {
        if episodes.is_empty()
            && vestibular
                .as_ref()
                .is_none_or(|(_, signed_steps)| signed_steps.is_empty())
        {
            return Err(RuntimeError::CognitiveFormation(
                "unsealed intake must contain vestibular or admitted source intervals".into(),
            ));
        }
        if self.pending.is_some()
            || self.direct_predecessor.is_some()
            || self.unsealed_intake.is_some()
            || self.pending_contact_growth.is_some()
        {
            return Err(RuntimeError::PendingCandidateExists);
        }
        let predecessor_envelope = std::mem::take(&mut self.active.envelope);
        let initial_cognitive = std::mem::take(&mut self.active.cognitive);
        let mut intake = self.new_unsealed_intake(initial_cognitive, predecessor_envelope);
        let advanced = (|| {
            if let Some((heading, signed_steps)) = vestibular {
                Self::enqueue_unsealed_vestibular(
                    &mut intake.pending_inputs,
                    heading,
                    signed_steps,
                    UnsealedInputScope::Causal,
                );
            }
            if !episodes.is_empty() {
                let current_body_source = admit_complete_articulated_body_state_source(
                    intake.predecessor.organism_tick,
                    &intake.articulated_body,
                )
                .map_err(|error| RuntimeError::ArticulatedBody(format!("{error:?}")))?;
                intake
                    .pending_inputs
                    .push_back(UnsealedCausalInput::Admitted {
                        source: current_body_source,
                        maximum_causal_intervals: vec![(1_i64, 1_000_i64); BODY_AXES.len()],
                        scope: UnsealedInputScope::Causal,
                        body_feedback_depth: 0,
                    });
                intake.observed_articulated_body = true;
                Self::enqueue_unsealed_admitted(
                    &mut intake.pending_inputs,
                    episodes,
                    UnsealedInputScope::Causal,
                );
            }
            let observation = Self::advance_unsealed_until_pause(&mut intake, self.budget)?;
            Self::unsealed_intake_receipt(&mut intake, observation.as_ref())
        })();
        match advanced {
            Ok(receipt) => {
                self.unsealed_intake = Some(intake);
                Ok(receipt)
            }
            Err(error) => {
                let restored = Self::restore_envelope(intake.predecessor_envelope, self.budget);
                match restored {
                    Ok(runtime) => {
                        self.active = runtime.active;
                        self.next_prepare_ordinal = intake.predecessor_next_prepare_ordinal;
                        Err(error)
                    }
                    Err(restore_error) => Err(RuntimeError::CognitiveFormation(format!(
                        "unsealed intake failed ({error}) and predecessor could not be restored ({restore_error})"
                    ))),
                }
            }
        }
    }

    fn resume_unsealed_action_direct(
        &mut self,
        token: [u8; 32],
        vestibular: Option<(u32, &[i32])>,
        consequence_episodes: &[(NativeJointSourceEpisode, Vec<(i64, i64)>)],
    ) -> Result<ResidentUnsealedIntakeReceipt, RuntimeError> {
        let mut intake = self
            .unsealed_intake
            .take()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if intake.token != token {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::PendingTokenMismatch);
        }
        if intake.paused_motor_unit_recruitments.is_none() {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::CognitiveFormation(
                "unsealed intake is not paused for an action consequence".into(),
            ));
        }
        if consequence_episodes.is_empty() {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::CognitiveFormation(
                "an action pause requires one complete consequence source".into(),
            ));
        }
        intake.paused_motor_unit_recruitments = None;
        intake.paused_articulated_body_consequences.clear();
        let mut resumed = VecDeque::new();
        Self::enqueue_unsealed_admitted(
            &mut resumed,
            consequence_episodes,
            UnsealedInputScope::Causal,
        );
        if let Some((heading, signed_steps)) = vestibular {
            Self::enqueue_unsealed_vestibular(
                &mut resumed,
                heading,
                signed_steps,
                UnsealedInputScope::Causal,
            );
        }
        if let Some(feedback) = intake.paused_body_feedback.take() {
            resumed.push_back(feedback);
        }
        while let Some(input) = resumed.pop_back() {
            intake.pending_inputs.push_front(input);
        }
        let advanced =
            Self::advance_unsealed_until_pause(&mut intake, self.budget).and_then(|observation| {
                Self::unsealed_intake_receipt(&mut intake, observation.as_ref())
            });
        match advanced {
            Ok(receipt) => {
                self.unsealed_intake = Some(intake);
                Ok(receipt)
            }
            Err(error) => {
                let restored = Self::restore_envelope(intake.predecessor_envelope, self.budget)?;
                self.active = restored.active;
                self.next_prepare_ordinal = intake.predecessor_next_prepare_ordinal;
                Err(error)
            }
        }
    }

    fn append_unsealed_intake_direct(
        &mut self,
        token: [u8; 32],
        appended_episodes: &[(NativeJointSourceEpisode, Vec<(i64, i64)>)],
    ) -> Result<ResidentUnsealedIntakeReceipt, RuntimeError> {
        let mut intake = self
            .unsealed_intake
            .take()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if intake.token != token {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::PendingTokenMismatch);
        }
        if intake.paused_motor_unit_recruitments.is_some()
            || intake.paused_body_feedback.is_some()
            || !intake.pending_inputs.is_empty()
        {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::CognitiveFormation(
                "unsealed intake must resolve its action pause before appending self-hearing"
                    .into(),
            ));
        }
        if appended_episodes.is_empty() {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::CognitiveFormation(
                "unsealed appended source set must not be empty".into(),
            ));
        }
        Self::enqueue_unsealed_admitted(
            &mut intake.pending_inputs,
            appended_episodes,
            UnsealedInputScope::AppendedSelfHearing,
        );
        let advanced =
            Self::advance_unsealed_until_pause(&mut intake, self.budget).and_then(|observation| {
                Self::unsealed_intake_receipt(&mut intake, observation.as_ref())
            });
        match advanced {
            Ok(receipt) => {
                self.unsealed_intake = Some(intake);
                Ok(receipt)
            }
            Err(error) => {
                let restored = Self::restore_envelope(intake.predecessor_envelope, self.budget)?;
                self.active = restored.active;
                self.next_prepare_ordinal = intake.predecessor_next_prepare_ordinal;
                Err(error)
            }
        }
    }

    fn finalize_unsealed_intake_direct(
        &mut self,
        token: [u8; 32],
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        let mut intake = self
            .unsealed_intake
            .take()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if intake.token != token {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::PendingTokenMismatch);
        }
        if intake.paused_motor_unit_recruitments.is_some()
            || intake.paused_body_feedback.is_some()
            || !intake.pending_inputs.is_empty()
        {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::CognitiveFormation(
                "unsealed intake cannot seal before its action consequence and causal queue".into(),
            ));
        }
        let predecessor_envelope = std::mem::take(&mut intake.predecessor_envelope);
        let predecessor_next_prepare_ordinal = intake.predecessor_next_prepare_ordinal;
        let appended_observation = intake.appended_cognitive_observation.take();
        let sealed = self.seal_unsealed_intake(intake);
        let (pending, mut receipt, next_prepare_ordinal) = match sealed {
            Ok(value) => value,
            Err(error) => {
                let restored = Self::restore_envelope(predecessor_envelope, self.budget)?;
                self.active = restored.active;
                self.next_prepare_ordinal = predecessor_next_prepare_ordinal;
                return Err(error);
            }
        };
        if let Some(observation) = appended_observation {
            receipt.appended_physically_transitioned_neuron_count =
                observation.physically_transitioned_neuron_count;
            receipt.appended_complete_neuron_fractal_count =
                observation.complete_neuron_fractal_count;
            receipt.appended_externally_perturbed_body_receptor_count =
                observation.externally_perturbed_body_receptor_count;
            receipt.appended_articulatory_unit_recruitments =
                observation.articulatory_unit_recruitments;
        }
        let final_token = pending.token;
        self.active = ActiveResidentOrganismState {
            envelope: pending.envelope,
            mounted: pending.mounted,
            cognitive: pending.cognitive,
            vestibular: pending.vestibular,
            articulated_body: pending.articulated_body,
            observation: pending.observation,
        };
        self.direct_predecessor = Some(UnacknowledgedDirectPredecessor {
            token: final_token,
            envelope: predecessor_envelope,
            next_prepare_ordinal: predecessor_next_prepare_ordinal,
        });
        self.next_prepare_ordinal = next_prepare_ordinal;
        Ok(receipt)
    }

    fn abort_unsealed_intake(&mut self, token: [u8; 32]) -> Result<(), RuntimeError> {
        let intake = self
            .unsealed_intake
            .take()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if intake.token != token {
            self.unsealed_intake = Some(intake);
            return Err(RuntimeError::PendingTokenMismatch);
        }
        let restored = Self::restore_envelope(intake.predecessor_envelope, self.budget)?;
        self.active = restored.active;
        self.next_prepare_ordinal = intake.predecessor_next_prepare_ordinal;
        Ok(())
    }

    fn acknowledge_direct_commit(&mut self, token: [u8; 32]) -> Result<(), RuntimeError> {
        let predecessor = self
            .direct_predecessor
            .as_ref()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if predecessor.token != token {
            return Err(RuntimeError::PendingTokenMismatch);
        }
        self.direct_predecessor = None;
        Ok(())
    }

    fn rollback_direct_commit(&mut self, token: [u8; 32]) -> Result<(), RuntimeError> {
        let predecessor = self
            .direct_predecessor
            .as_ref()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if predecessor.token != token {
            return Err(RuntimeError::PendingTokenMismatch);
        }
        let restored = Self::restore_envelope(predecessor.envelope.clone(), self.budget)?;
        let next_prepare_ordinal = predecessor.next_prepare_ordinal;
        self.active = restored.active;
        self.direct_predecessor = None;
        self.next_prepare_ordinal = next_prepare_ordinal;
        Ok(())
    }

    fn new_unsealed_intake(
        &self,
        cognitive: ResidentCognitiveFormationState,
        predecessor_envelope: Vec<u8>,
    ) -> UnsealedResidentIntake {
        UnsealedResidentIntake {
            token: [0; 32],
            predecessor: self.active.observation.clone(),
            predecessor_envelope,
            predecessor_next_prepare_ordinal: self.next_prepare_ordinal,
            cognitive,
            vestibular: self.active.vestibular.clone(),
            articulated_body: self.active.articulated_body.clone(),
            cognitive_observation: None,
            receptor_ingress: ResidentReceptorIngressObservation::default(),
            causal_interval_evidence: Vec::new(),
            articulated_body_consequences: Vec::new(),
            body_proprioceptive_sources: Vec::new(),
            causal_authority_entries: Vec::new(),
            pending_inputs: VecDeque::new(),
            paused_motor_unit_recruitments: None,
            paused_body_feedback: None,
            paused_articulated_body_consequences: Vec::new(),
            appended_cognitive_observation: None,
            source_port_count: 0,
            source_occurrence_count: 0,
            processed_interval_count: 0,
            observed_articulated_body: false,
        }
    }

    fn enqueue_unsealed_admitted(
        queue: &mut VecDeque<UnsealedCausalInput>,
        episodes: &[(NativeJointSourceEpisode, Vec<(i64, i64)>)],
        scope: UnsealedInputScope,
    ) {
        queue.extend(
            episodes
                .iter()
                .cloned()
                .map(
                    |(source, maximum_causal_intervals)| UnsealedCausalInput::Admitted {
                        source,
                        maximum_causal_intervals,
                        scope,
                        body_feedback_depth: 0,
                    },
                ),
        );
    }

    fn enqueue_unsealed_vestibular(
        queue: &mut VecDeque<UnsealedCausalInput>,
        predecessor_heading_millidegrees: u32,
        signed_body_motion_millidegrees: &[i32],
        scope: UnsealedInputScope,
    ) {
        let mut heading = predecessor_heading_millidegrees;
        for signed_step in signed_body_motion_millidegrees.iter().copied() {
            queue.push_back(UnsealedCausalInput::Vestibular {
                predecessor_heading_millidegrees: heading,
                signed_body_motion_millidegrees: signed_step,
                scope,
            });
            heading = (i64::from(heading) + i64::from(signed_step)).rem_euclid(360_000) as u32;
        }
    }

    fn unsealed_intake_receipt(
        intake: &mut UnsealedResidentIntake,
        segment_observation: Option<&CognitiveFormationObservation>,
    ) -> Result<ResidentUnsealedIntakeReceipt, RuntimeError> {
        let authority = causal_intake_authority(&intake.causal_authority_entries)?;
        intake.token = unsealed_intake_token(
            intake.predecessor.state_receipt,
            authority,
            intake.predecessor_next_prepare_ordinal,
        );
        let processed_interval_count = u64::try_from(intake.processed_interval_count)
            .map_err(|_| RuntimeError::OrganismTickOverflow)?;
        let provisional_organism_tick = intake
            .predecessor
            .organism_tick
            .checked_add(processed_interval_count)
            .ok_or(RuntimeError::OrganismTickOverflow)?;
        Ok(ResidentUnsealedIntakeReceipt {
            token: intake.token,
            provisional_organism_tick,
            pause_interval_ordinal: intake
                .paused_motor_unit_recruitments
                .as_ref()
                .map(|_| processed_interval_count),
            motor_unit_recruitments: intake
                .paused_motor_unit_recruitments
                .clone()
                .unwrap_or_default(),
            articulatory_unit_recruitments: segment_observation
                .map(|observation| observation.articulatory_unit_recruitments.clone())
                .unwrap_or_default(),
            articulated_body: intake.articulated_body.clone(),
            articulated_body_consequences: intake.paused_articulated_body_consequences.clone(),
        })
    }

    fn advance_unsealed_until_pause(
        intake: &mut UnsealedResidentIntake,
        budget: RuntimeBudget,
    ) -> Result<Option<CognitiveFormationObservation>, RuntimeError> {
        if intake.paused_motor_unit_recruitments.is_some() {
            return Err(RuntimeError::CognitiveFormation(
                "unsealed intake cannot advance while an action consequence is pending".into(),
            ));
        }
        let cognitive_budget = cognitive_budget_after_joint(
            encode_empty_mounted_joint_state()
                .map_err(RuntimeError::MountedTransition)?
                .len(),
            budget,
        )?;
        let mut segment_observation = None;
        while let Some(input) = intake.pending_inputs.pop_front() {
            let (scope, observation, feedback, consequences) = match input {
                UnsealedCausalInput::Admitted {
                    source,
                    maximum_causal_intervals,
                    scope,
                    body_feedback_depth,
                } => {
                    let admitted = admitted_episode_with_authored_intervals(
                        &source,
                        &maximum_causal_intervals,
                    )
                    .map_err(RuntimeError::CognitiveFormation)?;
                    intake
                        .causal_authority_entries
                        .push(admitted_source_authority(
                            source.joint_source_authority_receipt(),
                            &maximum_causal_intervals,
                        )?);
                    intake.receptor_ingress = intake
                        .receptor_ingress
                        .checked_merge(observe_canonical_receptor_ingress(&source))
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    intake.source_port_count = intake
                        .source_port_count
                        .checked_add(source.joint_source_ports().len())
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    intake.source_occurrence_count = intake
                        .source_occurrence_count
                        .checked_add(source.joint_source_occurrences().len())
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    let cognitive = std::mem::take(&mut intake.cognitive);
                    let (successor, observation) = cognitive
                        .advance_admitted_transition(&admitted, cognitive_budget)
                        .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
                    let source_tick = intake
                        .predecessor
                        .organism_tick
                        .checked_add(
                            u64::try_from(intake.processed_interval_count)
                                .map_err(|_| RuntimeError::OrganismTickOverflow)?,
                        )
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    intake.processed_interval_count = intake
                        .processed_interval_count
                        .checked_add(1)
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    let body_transition = settle_motor_recruitments_into_articulated_body(
                        &intake.articulated_body,
                        &observation.motor_unit_recruitments,
                    )?;
                    let feedback = if let Some((feedback_source, receipt)) =
                        body_proprioceptive_source(
                            source_tick,
                            &body_transition.proprioceptive_consequences,
                        )? {
                        let next_depth = body_feedback_depth
                            .checked_add(1)
                            .ok_or(RuntimeError::OrganismTickOverflow)?;
                        if next_depth > BODY_EFFECTOR_TERMINAL_COUNT {
                            return Err(RuntimeError::ArticulatedBody(
                                "body feedback did not quiesce inside one complete fixed terminal frontier"
                                    .into(),
                            ));
                        }
                        intake.body_proprioceptive_sources.push(receipt);
                        Some(UnsealedCausalInput::Admitted {
                            maximum_causal_intervals: vec![
                                (1_i64, 1_000_i64);
                                feedback_source
                                    .joint_source_occurrences()
                                    .len()
                            ],
                            source: feedback_source,
                            scope,
                            body_feedback_depth: next_depth,
                        })
                    } else {
                        None
                    };
                    let consequences = body_transition
                        .proprioceptive_consequences
                        .iter()
                        .copied()
                        .map(|consequence| TimedBodyProprioceptiveConsequence {
                            source_tick,
                            consequence,
                        })
                        .collect::<Vec<_>>();
                    intake
                        .articulated_body_consequences
                        .extend(consequences.iter().cloned());
                    intake.articulated_body = body_transition.successor;
                    intake
                        .causal_interval_evidence
                        .push(CausalIntervalEvidence {
                            externally_perturbed_neuron_lineages: observation
                                .externally_perturbed_neuron_lineages
                                .clone(),
                            internally_reassembled_formation_cues: observation
                                .internally_reassembled_formation_cues
                                .clone(),
                            externally_reassembled_formation_frontiers: observation
                                .externally_reassembled_formation_frontiers
                                .clone(),
                            motor_unit_recruitments: observation.motor_unit_recruitments.clone(),
                            emitted_neuron_lineages: observation
                                .emitted_neuron_fractals
                                .iter()
                                .map(|fractal| fractal.neuron_lineage)
                                .collect(),
                            changed_contact_channel_states: observation
                                .changed_contact_channel_states
                                .clone(),
                            affective_balance_trajectories: observation
                                .affective_balance_trajectories
                                .clone(),
                            frontier_advances: successor
                                .observe_active_electrical_frontier_advances(),
                        });
                    intake.cognitive = successor;
                    (scope, observation, feedback, consequences)
                }
                UnsealedCausalInput::Vestibular {
                    predecessor_heading_millidegrees,
                    signed_body_motion_millidegrees,
                    scope,
                } => {
                    let ingress = resident_vestibular_tick_ingress(
                        &intake.vestibular,
                        predecessor_heading_millidegrees,
                        signed_body_motion_millidegrees,
                    )?;
                    let (source, _) = ingress.source().joint_source_with_contacts();
                    intake
                        .causal_authority_entries
                        .push(vestibular_trajectory_authority(
                            predecessor_heading_millidegrees,
                            &[signed_body_motion_millidegrees],
                        ));
                    intake.receptor_ingress = intake
                        .receptor_ingress
                        .checked_merge(observe_canonical_receptor_ingress(source))
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    intake.source_port_count = intake
                        .source_port_count
                        .checked_add(source.joint_source_ports().len())
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    intake.source_occurrence_count = intake
                        .source_occurrence_count
                        .checked_add(source.joint_source_occurrences().len())
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    let cognitive = std::mem::take(&mut intake.cognitive);
                    let (successor, observation) = cognitive
                        .advance_vestibular_transition(&ingress, cognitive_budget)
                        .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
                    let source_tick = intake
                        .predecessor
                        .organism_tick
                        .checked_add(
                            u64::try_from(intake.processed_interval_count)
                                .map_err(|_| RuntimeError::OrganismTickOverflow)?,
                        )
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    intake.processed_interval_count = intake
                        .processed_interval_count
                        .checked_add(1)
                        .ok_or(RuntimeError::OrganismTickOverflow)?;
                    let body_transition = settle_motor_recruitments_into_articulated_body(
                        &intake.articulated_body,
                        &observation.motor_unit_recruitments,
                    )?;
                    let feedback = if let Some((feedback_source, receipt)) =
                        body_proprioceptive_source(
                            source_tick,
                            &body_transition.proprioceptive_consequences,
                        )? {
                        intake.body_proprioceptive_sources.push(receipt);
                        Some(UnsealedCausalInput::Admitted {
                            maximum_causal_intervals: vec![
                                (1_i64, 1_000_i64);
                                feedback_source
                                    .joint_source_occurrences()
                                    .len()
                            ],
                            source: feedback_source,
                            scope,
                            body_feedback_depth: 1,
                        })
                    } else {
                        None
                    };
                    let consequences = body_transition
                        .proprioceptive_consequences
                        .iter()
                        .copied()
                        .map(|consequence| TimedBodyProprioceptiveConsequence {
                            source_tick,
                            consequence,
                        })
                        .collect::<Vec<_>>();
                    intake
                        .articulated_body_consequences
                        .extend(consequences.iter().cloned());
                    intake.articulated_body = body_transition.successor;
                    intake.vestibular = ResidentVestibularBody {
                        anatomy: intake.vestibular.anatomy.clone(),
                        canal: ingress.transduction().reached_tick.successor_canal,
                        source_tick: intake
                            .vestibular
                            .source_tick
                            .checked_add(1)
                            .ok_or(RuntimeError::OrganismTickOverflow)?,
                    };
                    intake
                        .causal_interval_evidence
                        .push(CausalIntervalEvidence {
                            externally_perturbed_neuron_lineages: observation
                                .externally_perturbed_neuron_lineages
                                .clone(),
                            internally_reassembled_formation_cues: observation
                                .internally_reassembled_formation_cues
                                .clone(),
                            externally_reassembled_formation_frontiers: observation
                                .externally_reassembled_formation_frontiers
                                .clone(),
                            motor_unit_recruitments: observation.motor_unit_recruitments.clone(),
                            emitted_neuron_lineages: observation
                                .emitted_neuron_fractals
                                .iter()
                                .map(|fractal| fractal.neuron_lineage)
                                .collect(),
                            changed_contact_channel_states: observation
                                .changed_contact_channel_states
                                .clone(),
                            affective_balance_trajectories: observation
                                .affective_balance_trajectories
                                .clone(),
                            frontier_advances: successor
                                .observe_active_electrical_frontier_advances(),
                        });
                    intake.cognitive = successor;
                    (scope, observation, feedback, consequences)
                }
            };
            retain_cognitive_trajectory_observation(
                &mut intake.cognitive_observation,
                observation.clone(),
            )?;
            if scope == UnsealedInputScope::AppendedSelfHearing {
                retain_cognitive_trajectory_observation(
                    &mut intake.appended_cognitive_observation,
                    observation.clone(),
                )?;
            }
            retain_cognitive_trajectory_observation(&mut segment_observation, observation.clone())?;
            if observation.motor_unit_recruitments.is_empty() {
                if let Some(feedback) = feedback {
                    intake.pending_inputs.push_front(feedback);
                }
            } else {
                intake.paused_motor_unit_recruitments =
                    Some(observation.motor_unit_recruitments.clone());
                intake.paused_body_feedback = feedback;
                intake.paused_articulated_body_consequences = consequences;
                break;
            }
        }
        Ok(segment_observation)
    }

    fn seal_unsealed_intake(
        &self,
        mut intake: UnsealedResidentIntake,
    ) -> Result<(PendingResidentOrganismState, ResidentPrepareReceipt, u64), RuntimeError> {
        if intake.observed_articulated_body {
            intake.articulated_body.initialize_proprioception();
        }
        let derived_budget = self.budget.derive()?;
        let joint_state =
            encode_empty_mounted_joint_state().map_err(RuntimeError::MountedTransition)?;
        let cognitive_budget = cognitive_budget_after_joint(joint_state.len(), self.budget)?;
        let interval_count = u64::try_from(intake.processed_interval_count)
            .map_err(|_| RuntimeError::OrganismTickOverflow)?;
        let organism_tick = intake
            .predecessor
            .organism_tick
            .checked_add(interval_count)
            .ok_or(RuntimeError::OrganismTickOverflow)?;
        let fabric_generation = intake
            .predecessor
            .fabric_generation
            .checked_add(interval_count)
            .ok_or(RuntimeError::FabricGenerationOverflow)?;
        let cognitive_observation = intake.cognitive_observation.take().ok_or_else(|| {
            RuntimeError::CognitiveFormation("unsealed intake carried no cognitive interval".into())
        })?;
        let (mounted, _) = restore_resident_mounted_state(
            &joint_state,
            derived_budget.max_joint_state_bytes,
            derived_budget.max_joint_working_bytes,
        )
        .map_err(RuntimeError::MountedTransition)?;
        let cognitive_state = intake
            .cognitive
            .encode(cognitive_budget)
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        let fabric = encode_fabric(
            fabric_generation,
            &joint_state,
            &cognitive_state,
            &intake.vestibular,
            &intake.articulated_body,
            self.budget,
        )?;
        let envelope = encode_envelope(
            intake.predecessor.identity,
            organism_tick,
            &fabric,
            self.budget,
        )?;
        let trajectory_authority = causal_intake_authority(&intake.causal_authority_entries)?;
        let transition = MountedJointDsfTransition {
            joint_field_count: intake.source_occurrence_count,
            joint_neuron_count: 0,
            l0_l4_evaluation_count: intake.source_occurrence_count,
            dsf_delivery_count: cognitive_observation.dsf_delivery_count,
            recurrent_dsf_delivery_count: 0,
            transition_receipt: None,
            episode_relation_candidate_receipt: None,
        };
        let observation = make_step_observation(
            &envelope,
            intake.predecessor.identity,
            intake.predecessor.organism_tick,
            organism_tick,
            intake.predecessor.fabric_generation,
            fabric_generation,
            intake.predecessor.mounted_generation,
            cognitive_observation.cognitive_ordinal,
            &fabric,
            trajectory_authority,
            transition,
            intake.source_occurrence_count,
            derived_budget,
            intake.predecessor.state_receipt,
            &cognitive_observation,
        );
        let next_prepare_ordinal = intake
            .predecessor_next_prepare_ordinal
            .checked_add(1)
            .ok_or(RuntimeError::PrepareTokenOrdinalOverflow)?;
        let token = prepare_token(
            intake.predecessor.state_receipt,
            observation.state_receipt,
            trajectory_authority,
            intake.predecessor_next_prepare_ordinal,
        );
        let pending = PendingResidentOrganismState {
            token,
            envelope,
            mounted,
            cognitive: intake.cognitive,
            vestibular: intake.vestibular,
            articulated_body: intake.articulated_body,
            observation: observation.clone(),
        };
        let receipt = ResidentPrepareReceipt {
            token,
            observation,
            phase_counts: MountedTransitionPhaseCounts {
                predecessor_authentication_count: 0,
                predecessor_decode_count: 0,
                predecessor_rebuilt_field_count: 0,
                retained_neuron_index_entry_count: intake.predecessor.complete_neuron_count,
                reached_neuron_lookup_count: intake.source_port_count,
                current_cohort_evaluation_count: intake.source_occurrence_count,
                successor_seal_count: 1,
            },
            receptor_ingress: intake.receptor_ingress,
            motor_unit_recruitments: cognitive_observation.motor_unit_recruitments,
            articulatory_unit_recruitments: cognitive_observation.articulatory_unit_recruitments,
            causal_interval_evidence: intake.causal_interval_evidence,
            articulated_body_consequences: intake.articulated_body_consequences,
            body_proprioceptive_sources: intake.body_proprioceptive_sources,
            appended_physically_transitioned_neuron_count: 0,
            appended_complete_neuron_fractal_count: 0,
            appended_externally_perturbed_body_receptor_count: 0,
            appended_articulatory_unit_recruitments: Vec::new(),
        };
        Ok((pending, receipt, next_prepare_ordinal))
    }

    fn prepare_vestibular_trajectory(
        &mut self,
        predecessor_heading_millidegrees: u32,
        signed_body_motion_millidegrees: &[i32],
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        if signed_body_motion_millidegrees.is_empty() {
            return Err(RuntimeError::Vestibular(
                "vestibular trajectory must contain at least one interval".into(),
            ));
        }
        if self.pending.is_some()
            || self.direct_predecessor.is_some()
            || self.unsealed_intake.is_some()
            || self.pending_contact_growth.is_some()
        {
            return Err(RuntimeError::PendingCandidateExists);
        }
        let mut intake = self.new_unsealed_intake(self.active.cognitive.clone(), Vec::new());
        Self::enqueue_unsealed_vestibular(
            &mut intake.pending_inputs,
            predecessor_heading_millidegrees,
            signed_body_motion_millidegrees,
            UnsealedInputScope::Causal,
        );
        Self::advance_unsealed_until_pause(&mut intake, self.budget)?;
        if intake.paused_motor_unit_recruitments.is_some() {
            return Err(RuntimeError::CognitiveFormation(
                "a vestibular motor discharge requires the unsealed action-consequence boundary"
                    .into(),
            ));
        }
        let (pending, receipt, next_prepare_ordinal) = self.seal_unsealed_intake(intake)?;
        self.pending = Some(pending);
        self.next_prepare_ordinal = next_prepare_ordinal;
        Ok(receipt)
    }

    fn prepare_typed(
        &mut self,
        source: &NativeJointSourceEpisode,
        admitted_source: Option<&AdmittedJointSourceEpisode>,
        vestibular: Option<&ResidentVestibularIngress>,
        initialize_articulated_body_proprioception: bool,
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        if self.pending.is_some()
            || self.direct_predecessor.is_some()
            || self.unsealed_intake.is_some()
            || self.pending_contact_growth.is_some()
        {
            return Err(RuntimeError::PendingCandidateExists);
        }
        let derived_budget = self.budget.derive()?;
        let predecessor = self.active.observation.clone();
        let organism_tick = predecessor
            .organism_tick
            .checked_add(1)
            .ok_or(RuntimeError::OrganismTickOverflow)?;
        let fabric_generation = predecessor
            .fabric_generation
            .checked_add(1)
            .ok_or(RuntimeError::FabricGenerationOverflow)?;
        let admitted_source_authority = source.joint_source_authority_receipt();
        let receptor_ingress = observe_canonical_receptor_ingress(source);
        let joint_state =
            encode_empty_mounted_joint_state().map_err(RuntimeError::MountedTransition)?;
        let (mounted, _) = restore_resident_mounted_state(
            &joint_state,
            derived_budget.max_joint_state_bytes,
            derived_budget.max_joint_working_bytes,
        )
        .map_err(RuntimeError::MountedTransition)?;
        let phase_counts = MountedTransitionPhaseCounts {
            predecessor_authentication_count: 0,
            predecessor_decode_count: 0,
            predecessor_rebuilt_field_count: 0,
            retained_neuron_index_entry_count: predecessor.complete_neuron_count,
            reached_neuron_lookup_count: source.joint_source_ports().len(),
            current_cohort_evaluation_count: source.joint_source_occurrences().len(),
            successor_seal_count: 1,
        };
        let cognitive_budget = cognitive_budget_after_joint(joint_state.len(), self.budget)?;
        let cognitive = match (vestibular, admitted_source) {
            (Some(vestibular), None) => self
                .active
                .cognitive
                .prepare_vestibular_transition(vestibular, cognitive_budget),
            (None, Some(admitted_source)) => self
                .active
                .cognitive
                .prepare_admitted_transition(admitted_source, cognitive_budget),
            (None, None) => self
                .active
                .cognitive
                .prepare_bare_source(source, cognitive_budget),
            (Some(_), Some(_)) => {
                Err(crate::resident_cognitive_formation::FormationError::NoncanonicalState)
            }
        }
        .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        let cognitive_state = self
            .active
            .cognitive
            .encode_successor(&cognitive, cognitive_budget)
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        let cognitive_observation = cognitive.observation().clone();
        let motor_unit_recruitments = cognitive_observation.motor_unit_recruitments.clone();
        let articulated_body_transition = settle_motor_recruitments_into_articulated_body(
            &self.active.articulated_body,
            &motor_unit_recruitments,
        )?;
        let body_proprioceptive_sources = body_proprioceptive_source(
            predecessor.organism_tick,
            &articulated_body_transition.proprioceptive_consequences,
        )?
        .map(|(_, receipt)| receipt)
        .into_iter()
        .collect();
        let articulated_body_consequences = articulated_body_transition
            .proprioceptive_consequences
            .iter()
            .copied()
            .map(|consequence| TimedBodyProprioceptiveConsequence {
                source_tick: predecessor.organism_tick,
                consequence,
            })
            .collect();
        let mut successor_articulated_body = articulated_body_transition.successor;
        if initialize_articulated_body_proprioception {
            successor_articulated_body.initialize_proprioception();
        }
        let articulatory_unit_recruitments =
            cognitive_observation.articulatory_unit_recruitments.clone();
        let successor_mounted_generation = cognitive_observation.cognitive_ordinal;
        let transition = MountedJointDsfTransition {
            joint_field_count: source.joint_source_occurrences().len(),
            joint_neuron_count: 0,
            l0_l4_evaluation_count: source.joint_source_occurrences().len(),
            dsf_delivery_count: cognitive_observation.dsf_delivery_count,
            recurrent_dsf_delivery_count: 0,
            transition_receipt: None,
            episode_relation_candidate_receipt: None,
        };
        let successor_vestibular = match vestibular {
            Some(ingress) => ResidentVestibularBody {
                anatomy: self.active.vestibular.anatomy.clone(),
                canal: ingress.transduction().reached_tick.successor_canal,
                source_tick: self
                    .active
                    .vestibular
                    .source_tick
                    .checked_add(1)
                    .ok_or(RuntimeError::OrganismTickOverflow)?,
            },
            None => self.active.vestibular.clone(),
        };
        let fabric = encode_fabric(
            fabric_generation,
            &joint_state,
            &cognitive_state,
            &successor_vestibular,
            &successor_articulated_body,
            self.budget,
        )?;
        let envelope = encode_envelope(predecessor.identity, organism_tick, &fabric, self.budget)?;
        let observation = make_step_observation(
            &envelope,
            predecessor.identity,
            predecessor.organism_tick,
            organism_tick,
            predecessor.fabric_generation,
            fabric_generation,
            predecessor.mounted_generation,
            successor_mounted_generation,
            &fabric,
            admitted_source_authority,
            transition,
            phase_counts.current_cohort_evaluation_count,
            derived_budget,
            predecessor.state_receipt,
            &cognitive_observation,
        );
        let next_prepare_ordinal = self
            .next_prepare_ordinal
            .checked_add(1)
            .ok_or(RuntimeError::PrepareTokenOrdinalOverflow)?;
        let token = prepare_token(
            predecessor.state_receipt,
            observation.state_receipt,
            admitted_source_authority,
            self.next_prepare_ordinal,
        );
        let (cognitive, _) = cognitive
            .try_into_successor(&self.active.cognitive)
            .map_err(|(error, _)| RuntimeError::CognitiveFormation(error.to_string()))?;
        self.pending = Some(PendingResidentOrganismState {
            token,
            envelope,
            mounted,
            cognitive,
            vestibular: successor_vestibular,
            articulated_body: successor_articulated_body,
            observation: observation.clone(),
        });
        self.next_prepare_ordinal = next_prepare_ordinal;
        Ok(ResidentPrepareReceipt {
            token,
            observation,
            phase_counts,
            receptor_ingress,
            motor_unit_recruitments,
            articulatory_unit_recruitments,
            causal_interval_evidence: Vec::new(),
            articulated_body_consequences,
            body_proprioceptive_sources,
            appended_physically_transitioned_neuron_count: 0,
            appended_complete_neuron_fractal_count: 0,
            appended_externally_perturbed_body_receptor_count: 0,
            appended_articulatory_unit_recruitments: Vec::new(),
        })
    }

    #[cfg(test)]
    fn prepare(
        &mut self,
        source: &NativeJointSourceEpisode,
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        self.prepare_with_store(source)
    }

    #[cfg(test)]
    fn prepare_with_store(
        &mut self,
        source: &NativeJointSourceEpisode,
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        let admitted_source = admitted_fixture_episode(source);
        self.prepare_typed(source, Some(&admitted_source), None, false)
    }

    fn commit(&mut self, token: [u8; 32]) -> Result<(), RuntimeError> {
        if let Some(pending) = self.pending_contact_growth.as_ref() {
            if pending.token != token {
                return Err(RuntimeError::PendingTokenMismatch);
            }
            let pending = self
                .pending_contact_growth
                .take()
                .expect("validated pending authored contact growth");
            self.active
                .cognitive
                .commit(pending.cognitive)
                .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
            self.active.envelope = pending.envelope;
            self.active.observation = pending.observation;
            return Ok(());
        }
        let pending = self
            .pending
            .as_ref()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if pending.token != token {
            return Err(RuntimeError::PendingTokenMismatch);
        }
        let pending = self
            .pending
            .take()
            .expect("validated resident pending candidate");
        self.active.cognitive = pending.cognitive;
        self.active.envelope = pending.envelope;
        self.active.mounted = pending.mounted;
        self.active.vestibular = pending.vestibular;
        self.active.articulated_body = pending.articulated_body;
        self.active.observation = pending.observation;
        Ok(())
    }

    fn discard(&mut self, token: [u8; 32]) -> Result<(), RuntimeError> {
        if let Some(pending) = self.pending_contact_growth.as_ref() {
            if pending.token != token {
                return Err(RuntimeError::PendingTokenMismatch);
            }
            self.pending_contact_growth = None;
            return Ok(());
        }
        let pending = self
            .pending
            .as_ref()
            .ok_or(RuntimeError::PendingCandidateMissing)?;
        if pending.token != token {
            return Err(RuntimeError::PendingTokenMismatch);
        }
        self.pending = None;
        Ok(())
    }

    /// Prepare one AUTHORED contact growth.
    ///
    /// Developmental authorship, not a sensory occurrence: the mounted joint
    /// state and its generation travel through byte-for-byte, existing
    /// contacts and their retained carrier phases are untouched, and only the
    /// cognitive body, the organism tick and the fabric generation advance.
    /// The body refuses honestly when an authored contact does not name two
    /// members of one living cohort, or is already authored.
    fn prepare_authored_contacts(
        &mut self,
        authored: &[AuthoredDeclaredContact],
    ) -> Result<ResidentPrepareReceipt, RuntimeError> {
        if self.pending.is_some()
            || self.direct_predecessor.is_some()
            || self.unsealed_intake.is_some()
            || self.pending_contact_growth.is_some()
        {
            return Err(RuntimeError::PendingCandidateExists);
        }
        let derived_budget = self.budget.derive()?;
        let predecessor = self.active.observation.clone();
        let organism_tick = predecessor
            .organism_tick
            .checked_add(1)
            .ok_or(RuntimeError::OrganismTickOverflow)?;
        let fabric_generation = predecessor
            .fabric_generation
            .checked_add(1)
            .ok_or(RuntimeError::FabricGenerationOverflow)?;
        let joint_bytes = {
            let parsed = parse_current_envelope(&self.active.envelope, self.budget)?;
            parsed.joint_bytes.to_vec()
        };
        let cognitive_budget = cognitive_budget_after_joint(joint_bytes.len(), self.budget)?;
        let cognitive = self
            .active
            .cognitive
            .prepare_authored_contacts(authored, cognitive_budget)
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        let cognitive_state = self
            .active
            .cognitive
            .encode_successor(&cognitive, cognitive_budget)
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        let cognitive_observation = cognitive.observation().clone();
        let fabric = encode_fabric(
            fabric_generation,
            &joint_bytes,
            &cognitive_state,
            &self.active.vestibular,
            &self.active.articulated_body,
            self.budget,
        )?;
        let envelope = encode_envelope(predecessor.identity, organism_tick, &fabric, self.budget)?;
        let observation = make_authored_contact_observation(
            &envelope,
            &predecessor,
            organism_tick,
            fabric_generation,
            &fabric,
            derived_budget,
            &cognitive_observation,
        );
        let next_prepare_ordinal = self
            .next_prepare_ordinal
            .checked_add(1)
            .ok_or(RuntimeError::PrepareTokenOrdinalOverflow)?;
        let token = prepare_token(
            predecessor.state_receipt,
            observation.state_receipt,
            sha256(AUTHORED_CONTACT_GROWTH_SCOPE.as_bytes()),
            self.next_prepare_ordinal,
        );
        self.pending_contact_growth = Some(PendingNutritionState {
            token,
            envelope,
            cognitive,
            observation: observation.clone(),
        });
        self.next_prepare_ordinal = next_prepare_ordinal;
        Ok(ResidentPrepareReceipt {
            token,
            observation,
            phase_counts: MountedTransitionPhaseCounts::default(),
            receptor_ingress: ResidentReceptorIngressObservation::default(),
            motor_unit_recruitments: Vec::new(),
            articulatory_unit_recruitments: Vec::new(),
            causal_interval_evidence: Vec::new(),
            articulated_body_consequences: Vec::new(),
            body_proprioceptive_sources: Vec::new(),
            appended_physically_transitioned_neuron_count: 0,
            appended_complete_neuron_fractal_count: 0,
            appended_externally_perturbed_body_receptor_count: 0,
            appended_articulatory_unit_recruitments: Vec::new(),
        })
    }

    fn observation(&self) -> RuntimeObservation {
        self.active.observation.clone()
    }

    fn cognitive_state(&self) -> &ResidentCognitiveFormationState {
        &self.active.cognitive
    }

    fn cold_restore_work(&self) -> ResidentMountedRestoreWork {
        self.active.mounted.cold_restore_work()
    }

    fn active_envelope(&self) -> &[u8] {
        &self.active.envelope
    }
}

/// Deliver each motor cell's discharge to its own retained efferent mount.
/// Afferent receptor ancestry remains causal evidence but has no motor
/// direction authority. Work is bounded by sparse recruitment; neither the
/// neuron population nor the body is scanned.
fn settle_motor_recruitments_into_articulated_body(
    predecessor: &ArticulatedBodyState,
    recruitments: &[MotorUnitRecruitment],
) -> Result<ArticulatedBodyTransition, RuntimeError> {
    let mut carriers_by_terminal: BTreeMap<BodyEffectorTerminal, u128> = BTreeMap::new();
    for recruitment in recruitments {
        let terminal = recruitment.body_effector_terminal;
        let existing = carriers_by_terminal.entry(terminal).or_default();
        *existing = existing
            .checked_add(recruitment.outward_elementary_carriers)
            .ok_or_else(|| {
                RuntimeError::ArticulatedBody("motor effector carrier count overflow".into())
            })?;
    }
    let admitted = AdmittedBodyEffectorDrives::admit(
        carriers_by_terminal
            .into_iter()
            .map(
                |(terminal, outward_elementary_carriers)| BodyEffectorDrive {
                    terminal,
                    outward_elementary_carriers,
                },
            )
            .collect(),
    )
    .map_err(|error| RuntimeError::ArticulatedBody(format!("{error:?}")))?;
    settle_body_effector_drives(predecessor, &admitted)
        .map_err(|error| RuntimeError::ArticulatedBody(format!("{error:?}")))
}

fn body_proprioceptive_source(
    source_tick: u64,
    consequences: &[BodyProprioceptiveConsequence],
) -> Result<Option<(NativeJointSourceEpisode, BodyProprioceptiveSourceReceipt)>, RuntimeError> {
    if consequences.is_empty() {
        return Ok(None);
    }
    let source = admit_articulated_body_proprioceptive_source(source_tick, consequences)
        .map_err(|error| RuntimeError::ArticulatedBody(format!("{error:?}")))?;
    let receipt = BodyProprioceptiveSourceReceipt {
        source_tick,
        payload: source.joint_source_body().to_vec(),
        port_count: consequences.len() * 2,
        sample_count: consequences.len() * 4,
        occurrence_count: consequences.len(),
        occurrence_frame_count: consequences.len() * 2,
    };
    Ok(Some((source, receipt)))
}

fn prepare_token(
    predecessor_receipt: [u8; 32],
    successor_receipt: [u8; 32],
    source_authority: [u8; 32],
    prepare_ordinal: u64,
) -> [u8; 32] {
    let mut body = [0_u8; 112];
    body[..8].copy_from_slice(PREPARE_TOKEN_MAGIC);
    body[8..40].copy_from_slice(&predecessor_receipt);
    body[40..72].copy_from_slice(&successor_receipt);
    body[72..104].copy_from_slice(&source_authority);
    body[104..112].copy_from_slice(&prepare_ordinal.to_le_bytes());
    sha256(&body)
}

fn unsealed_intake_token(
    predecessor_receipt: [u8; 32],
    source_authority: [u8; 32],
    prepare_ordinal: u64,
) -> [u8; 32] {
    let mut body = [0_u8; 88];
    body[..16].copy_from_slice(b"GLUNSEALEDINTAKE");
    body[16..48].copy_from_slice(&predecessor_receipt);
    body[48..80].copy_from_slice(&source_authority);
    body[80..].copy_from_slice(&prepare_ordinal.to_le_bytes());
    sha256(&body)
}

fn vestibular_trajectory_authority(
    predecessor_heading_millidegrees: u32,
    signed_body_motion_millidegrees: &[i32],
) -> [u8; 32] {
    let mut body = Vec::with_capacity(16 + signed_body_motion_millidegrees.len() * 4);
    body.extend_from_slice(b"GLVESTR1");
    body.extend_from_slice(&predecessor_heading_millidegrees.to_le_bytes());
    body.extend_from_slice(&(signed_body_motion_millidegrees.len() as u32).to_le_bytes());
    for signed_step in signed_body_motion_millidegrees {
        body.extend_from_slice(&signed_step.to_le_bytes());
    }
    sha256(&body)
}

fn admitted_source_authority(
    source_authority: [u8; 32],
    intervals: &[(i64, i64)],
) -> Result<[u8; 32], RuntimeError> {
    let interval_count =
        u32::try_from(intervals.len()).map_err(|_| RuntimeError::OrganismTickOverflow)?;
    let mut body = Vec::with_capacity(44 + intervals.len() * 16);
    body.extend_from_slice(b"GLADSRC1");
    body.extend_from_slice(&source_authority);
    body.extend_from_slice(&interval_count.to_le_bytes());
    for &(numerator, denominator) in intervals {
        body.extend_from_slice(&numerator.to_le_bytes());
        body.extend_from_slice(&denominator.to_le_bytes());
    }
    Ok(sha256(&body))
}

fn causal_intake_authority(entries: &[[u8; 32]]) -> Result<[u8; 32], RuntimeError> {
    if entries.is_empty() {
        return Err(RuntimeError::CognitiveFormation(
            "unsealed intake carried no physical source".into(),
        ));
    }
    let entry_count =
        u32::try_from(entries.len()).map_err(|_| RuntimeError::OrganismTickOverflow)?;
    let mut body = Vec::with_capacity(12 + entries.len() * 32);
    body.extend_from_slice(b"GLCAUSE1");
    body.extend_from_slice(&entry_count.to_le_bytes());
    for entry in entries {
        body.extend_from_slice(entry);
    }
    Ok(sha256(&body))
}

fn exact_token(value: Vec<u8>) -> Result<[u8; 32], PyErr> {
    value
        .try_into()
        .map_err(|_| PyValueError::new_err("resident organism token must contain exactly 32 bytes"))
}

fn native_resident_observation(
    runtime: &ResidentOrganismRuntime,
) -> NativeResidentOrganismObservation {
    NativeResidentOrganismObservation {
        observation: runtime.observation(),
        cold_restore_work: runtime.cold_restore_work(),
        articulated_body: runtime.active.articulated_body.clone(),
    }
}

fn native_resident_prepare(prepared: ResidentPrepareReceipt) -> NativeResidentOrganismPrepare {
    NativeResidentOrganismPrepare {
        token: prepared.token,
        observation: prepared.observation,
        phase_counts: prepared.phase_counts,
        receptor_ingress: prepared.receptor_ingress,
        motor_unit_recruitments: prepared.motor_unit_recruitments,
        articulatory_unit_recruitments: prepared.articulatory_unit_recruitments,
        causal_interval_evidence: prepared.causal_interval_evidence,
        articulated_body_consequences: prepared.articulated_body_consequences,
        body_proprioceptive_sources: prepared.body_proprioceptive_sources,
        appended_physically_transitioned_neuron_count: prepared
            .appended_physically_transitioned_neuron_count,
        appended_complete_neuron_fractal_count: prepared.appended_complete_neuron_fractal_count,
        appended_externally_perturbed_body_receptor_count: prepared
            .appended_externally_perturbed_body_receptor_count,
        appended_articulatory_unit_recruitments: prepared.appended_articulatory_unit_recruitments,
    }
}

fn native_unsealed_intake(receipt: ResidentUnsealedIntakeReceipt) -> NativeResidentUnsealedIntake {
    NativeResidentUnsealedIntake {
        token: receipt.token,
        provisional_organism_tick: receipt.provisional_organism_tick,
        pause_interval_ordinal: receipt.pause_interval_ordinal,
        motor_unit_recruitments: receipt.motor_unit_recruitments,
        articulatory_unit_recruitments: receipt.articulatory_unit_recruitments,
        articulated_body: receipt.articulated_body,
        articulated_body_consequences: receipt.articulated_body_consequences,
    }
}

fn resident_vestibular_tick_ingress(
    vestibular: &ResidentVestibularBody,
    predecessor_heading_millidegrees: u32,
    signed_body_motion_millidegrees: i32,
) -> Result<ResidentVestibularIngress, RuntimeError> {
    let predecessor_body = YawBodyState::new(predecessor_heading_millidegrees)
        .map_err(|error| RuntimeError::Vestibular(format!("{error:?}")))?;
    let successor_heading = (i64::from(predecessor_heading_millidegrees)
        + i64::from(signed_body_motion_millidegrees))
    .rem_euclid(360_000);
    let successor_body = YawBodyState::new(
        u32::try_from(successor_heading)
            .map_err(|_| RuntimeError::Vestibular("yaw width changed".into()))?,
    )
    .map_err(|error| RuntimeError::Vestibular(format!("{error:?}")))?;
    let reached = settle_reached_vestibular_bundle_tick(
        vestibular.anatomy.canal_anatomy(),
        vestibular.canal,
        signed_body_motion_millidegrees,
        vestibular.anatomy.bundle_anatomy(),
    )
    .map_err(|error| RuntimeError::Vestibular(format!("{error:?}")))?;
    prepare_resident_vestibular_ingress(
        vestibular.source_tick,
        predecessor_body,
        successor_body,
        reached,
        &vestibular.anatomy,
    )
    .map_err(|error| RuntimeError::Vestibular(format!("{error:?}")))
}

#[pymethods]
impl NativeResidentOrganismRuntime {
    #[getter]
    fn schema(&self) -> &'static str {
        RESIDENT_RUNTIME_SCHEMA
    }

    fn prepare(
        &mut self,
        py: Python<'_>,
        source: PyRef<'_, NativeJointSourceEpisode>,
    ) -> PyResult<NativeResidentOrganismPrepare> {
        let source = source.clone();
        let prepared = py
            .allow_threads(|| self.runtime.prepare_source(&source))
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_resident_prepare(prepared))
    }

    /// Prepare one complete, bounded proprioceptive observation of the
    /// currently persisted body. Every terminal keeps its fixed anatomy;
    /// Python supplies no receptor identity, action meaning, or interval.
    fn prepare_articulated_body_observation(
        &mut self,
        py: Python<'_>,
    ) -> PyResult<NativeResidentOrganismPrepare> {
        let prepared = py
            .allow_threads(|| self.runtime.prepare_articulated_body_observation())
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_resident_prepare(prepared))
    }

    /// Prepare an ordered native body-and-balance trajectory as one external
    /// transaction. Every one-millisecond interval settles in causal order;
    /// only the final organism successor is sealed.
    fn prepare_vestibular_trajectory(
        &mut self,
        py: Python<'_>,
        predecessor_heading_millidegrees: u32,
        signed_body_motion_millidegrees: Vec<i32>,
    ) -> PyResult<NativeResidentOrganismPrepare> {
        let prepared = py
            .allow_threads(|| {
                self.runtime.prepare_vestibular_trajectory(
                    predecessor_heading_millidegrees,
                    &signed_body_motion_millidegrees,
                )
            })
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_resident_prepare(prepared))
    }

    /// Begin one native intake without encoding or mutating durable CURRENT.
    /// Vestibular intervals settle first, followed by the ordered sensory
    /// sources and all exact body-feedback intervals they physically cause.
    #[pyo3(signature = (
        predecessor_heading_millidegrees,
        signed_body_motion_millidegrees,
        sources,
        maximum_causal_intervals
    ))]
    fn begin_unsealed_intake_direct(
        &mut self,
        py: Python<'_>,
        predecessor_heading_millidegrees: Option<u32>,
        signed_body_motion_millidegrees: Vec<i32>,
        sources: Vec<Py<NativeJointSourceEpisode>>,
        maximum_causal_intervals: Vec<Vec<(i64, i64)>>,
    ) -> PyResult<NativeResidentUnsealedIntake> {
        if sources.len() != maximum_causal_intervals.len() {
            return Err(PyValueError::new_err(
                "unsealed intake source and interval counts differ",
            ));
        }
        if predecessor_heading_millidegrees.is_none() && !signed_body_motion_millidegrees.is_empty()
        {
            return Err(PyValueError::new_err(
                "unsealed vestibular intervals require a predecessor heading",
            ));
        }
        let episodes = sources
            .iter()
            .zip(maximum_causal_intervals)
            .map(|(source, intervals)| (source.borrow(py).clone(), intervals))
            .collect::<Vec<_>>();
        let vestibular = predecessor_heading_millidegrees
            .map(|heading| (heading, signed_body_motion_millidegrees.as_slice()));
        let receipt = py
            .allow_threads(|| {
                self.runtime
                    .begin_unsealed_intake_direct(vestibular, &episodes)
            })
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_unsealed_intake(receipt))
    }

    /// Resume exactly one outstanding motor pause with its complete sensory
    /// consequence and optional exact vestibular trajectory. The causal queue
    /// stops again at the next motor discharge.
    #[pyo3(signature = (
        token,
        predecessor_heading_millidegrees,
        signed_body_motion_millidegrees,
        sources,
        maximum_causal_intervals
    ))]
    fn resume_unsealed_action_direct(
        &mut self,
        py: Python<'_>,
        token: Vec<u8>,
        predecessor_heading_millidegrees: Option<u32>,
        signed_body_motion_millidegrees: Vec<i32>,
        sources: Vec<Py<NativeJointSourceEpisode>>,
        maximum_causal_intervals: Vec<Vec<(i64, i64)>>,
    ) -> PyResult<NativeResidentUnsealedIntake> {
        if sources.len() != maximum_causal_intervals.len() {
            return Err(PyValueError::new_err(
                "unsealed action consequence source and interval counts differ",
            ));
        }
        if predecessor_heading_millidegrees.is_none() && !signed_body_motion_millidegrees.is_empty()
        {
            return Err(PyValueError::new_err(
                "unsealed action vestibular intervals require a predecessor heading",
            ));
        }
        let token = exact_token(token)?;
        let episodes = sources
            .iter()
            .zip(maximum_causal_intervals)
            .map(|(source, intervals)| (source.borrow(py).clone(), intervals))
            .collect::<Vec<_>>();
        let vestibular = predecessor_heading_millidegrees
            .map(|heading| (heading, signed_body_motion_millidegrees.as_slice()));
        let receipt = py
            .allow_threads(|| {
                self.runtime
                    .resume_unsealed_action_direct(token, vestibular, &episodes)
            })
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_unsealed_intake(receipt))
    }

    /// Append exact self-hearing while the causal queue is empty. A resulting
    /// motor discharge pauses through the same action-consequence boundary.
    fn append_unsealed_intake_direct(
        &mut self,
        py: Python<'_>,
        token: Vec<u8>,
        sources: Vec<Py<NativeJointSourceEpisode>>,
        maximum_causal_intervals: Vec<Vec<(i64, i64)>>,
    ) -> PyResult<NativeResidentUnsealedIntake> {
        if sources.len() != maximum_causal_intervals.len() {
            return Err(PyValueError::new_err(
                "unsealed appended source and interval counts differ",
            ));
        }
        let token = exact_token(token)?;
        let episodes = sources
            .iter()
            .zip(maximum_causal_intervals)
            .map(|(source, intervals)| (source.borrow(py).clone(), intervals))
            .collect::<Vec<_>>();
        let receipt = py
            .allow_threads(|| self.runtime.append_unsealed_intake_direct(token, &episodes))
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_unsealed_intake(receipt))
    }

    /// Seal exactly once after the action/consequence queue and any optional
    /// self-hearing have fully drained.
    fn finalize_unsealed_intake_direct(
        &mut self,
        py: Python<'_>,
        token: Vec<u8>,
    ) -> PyResult<NativeResidentOrganismPrepare> {
        let token = exact_token(token)?;
        let prepared = py
            .allow_threads(|| self.runtime.finalize_unsealed_intake_direct(token))
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_resident_prepare(prepared))
    }

    fn abort_unsealed_intake(&mut self, py: Python<'_>, token: Vec<u8>) -> PyResult<()> {
        let token = exact_token(token)?;
        py.allow_threads(|| self.runtime.abort_unsealed_intake(token))
            .map_err(|error| PyValueError::new_err(error.to_string()))
    }

    fn acknowledge_direct_commit(&mut self, token: Vec<u8>) -> PyResult<()> {
        self.runtime
            .acknowledge_direct_commit(exact_token(token)?)
            .map_err(|error| PyValueError::new_err(error.to_string()))
    }

    fn rollback_direct_commit(&mut self, py: Python<'_>, token: Vec<u8>) -> PyResult<()> {
        let token = exact_token(token)?;
        py.allow_threads(|| self.runtime.rollback_direct_commit(token))
            .map_err(|error| PyValueError::new_err(error.to_string()))
    }

    /// Prepare one exact one-millisecond body-and-balance successor.
    ///
    /// The caller supplies the body's already-applied predecessor heading and
    /// this tick's signed yaw displacement.  Native canal, cupula, bundle,
    /// tip-link, spring, complete-neuron, and full-field state advance as one
    /// pending organism successor; commit or discard retains the ordinary
    /// organism transaction semantics.
    fn prepare_vestibular_tick(
        &mut self,
        py: Python<'_>,
        predecessor_heading_millidegrees: u32,
        signed_body_motion_millidegrees: i32,
    ) -> PyResult<NativeResidentOrganismPrepare> {
        let prepared = py
            .allow_threads(|| {
                self.runtime.prepare_vestibular_tick(
                    predecessor_heading_millidegrees,
                    signed_body_motion_millidegrees,
                )
            })
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_resident_prepare(prepared))
    }

    /// Append AUTHORED contacts to the living cohort.
    ///
    /// Each entry is `(left_sensor_id, left_substream_id, right_sensor_id,
    /// right_substream_id, conductance_picosiemens)`: the caller names two of
    /// its own declared receptors and the conductance of the contact between
    /// them, exactly as growth DNA authors a contact at genesis.  Nothing is
    /// derived here — no adjacency, no conductance, no ordering.
    ///
    /// Append-only: every already-authored contact keeps its index, endpoints,
    /// conductance and retained carrier phase; each new contact starts from
    /// the authored rest state.  A pair that is already contacted is refused
    /// rather than authored twice.
    fn prepare_authored_contacts(
        &mut self,
        py: Python<'_>,
        contacts: Vec<(String, String, String, String, i64)>,
    ) -> PyResult<NativeResidentOrganismPrepare> {
        let mut authored = Vec::with_capacity(contacts.len());
        for (
            left_sensor_id,
            left_substream_id,
            right_sensor_id,
            right_substream_id,
            conductance_picosiemens,
        ) in contacts
        {
            authored.push(AuthoredDeclaredContact {
                left_sensor_id,
                left_substream_id,
                right_sensor_id,
                right_substream_id,
                conductance_picosiemens: ExactRational::integer(i128::from(
                    conductance_picosiemens,
                )),
            });
        }
        let prepared = py
            .allow_threads(|| self.runtime.prepare_authored_contacts(&authored))
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(native_resident_prepare(prepared))
    }

    /// Read-only observation of the living cohorts' authored contact sets:
    /// one entry per cohort as ``(member_count, contact_count)``.  Structure
    /// only; reading advances nothing.
    fn observe_cohort_contacts(&self) -> Vec<(usize, usize)> {
        self.runtime.cognitive_state().observe_cohort_contacts()
    }

    /// Read-only bounded distribution of living reached neurons by their
    /// persisted developmental layer. No neuronal state or reserve cells are
    /// projected and reading advances nothing.
    fn observe_reached_neuron_count_by_layer(&self) -> Vec<(u32, usize)> {
        self.runtime
            .cognitive_state()
            .observe_reached_neuron_count_by_layer()
    }

    /// Read-only exact lineage-to-developmental-layer projection for reached
    /// material. It is observer evidence only and advances no organism state.
    fn observe_reached_neuron_lineage_layers(&self) -> Vec<(String, u32, bool)> {
        self.runtime
            .cognitive_state()
            .observe_reached_neuron_lineage_layers()
            .into_iter()
            .map(|(lineage, layer, receptor)| (hex_bytes(&lineage), layer, receptor))
            .collect()
    }

    /// Read only exact current-boundary transfers advancing from the supplied
    /// lineages. Native filtering and the explicit advancing endpoint prevent
    /// a sparse trace from reversing carrier flow or materializing unrelated
    /// frontier entries across the Python boundary.
    fn observe_active_electrical_frontier_advances_from(
        &self,
        lineage_hexes: Vec<String>,
    ) -> PyResult<Vec<CausalFrontierTransferProjection>> {
        if lineage_hexes.is_empty() {
            return Err(PyValueError::new_err(
                "active electrical frontier filter requires a lineage",
            ));
        }
        let mut lineages = lineage_hexes
            .iter()
            .map(|value| parse_lineage_hex(value))
            .collect::<PyResult<Vec<_>>>()?;
        lineages.sort_unstable();
        lineages.dedup();
        Ok(project_causal_frontier_transfers(
            &self
                .runtime
                .cognitive_state()
                .observe_active_electrical_frontier_advances_from(&lineages),
        ))
    }

    /// Read-only reached-neuron electrical evidence for translation-boundary
    /// diagnosis. Cognition never consumes this observer projection.
    fn observe_reached_neuron_electrical_by_layer(
        &self,
    ) -> Vec<(u32, i128, i128, u128, u128, u128)> {
        self.runtime
            .cognitive_state()
            .observe_reached_neuron_electrical_by_layer()
    }

    /// Read-only sparse-contact counts by canonical developmental layer pair.
    fn observe_reached_contact_count_by_layer_pair(&self) -> Vec<(u32, u32, usize)> {
        self.runtime
            .cognitive_state()
            .observe_reached_contact_count_by_layer_pair()
    }

    /// Read-only exact retained channel state for every reached sparse
    /// contact. This is live evidence only; it supplies no organism authority.
    #[allow(clippy::type_complexity)]
    fn observe_reached_contact_channel_states(
        &self,
    ) -> Vec<(String, String, u32, u128, i128, u128, i128, u128)> {
        self.runtime
            .cognitive_state()
            .observe_reached_contact_channel_states()
            .into_iter()
            .map(
                |(
                    left,
                    right,
                    parallel_ordinal,
                    population,
                    transition_phase_numerator,
                    transition_phase_denominator,
                    conductance_numerator,
                    conductance_denominator,
                )| {
                    (
                        hex_bytes(&left),
                        hex_bytes(&right),
                        parallel_ordinal,
                        population,
                        transition_phase_numerator,
                        transition_phase_denominator,
                        conductance_numerator,
                        conductance_denominator,
                    )
                },
            )
            .collect()
    }

    /// Read-only count of reached cells carrying one exact persisted source
    /// anchor. The caller names physical source identity, not cognition.
    fn observe_reached_source_site_count(
        &self,
        sensor_id: String,
        substream_id: String,
    ) -> PyResult<usize> {
        if sensor_id.is_empty() || substream_id.is_empty() {
            return Err(PyValueError::new_err(
                "reached source observation requires nonempty source identity",
            ));
        }
        Ok(self
            .runtime
            .cognitive_state()
            .observe_reached_source_site_count(&sensor_id, &substream_id))
    }

    fn commit(&mut self, token: Vec<u8>) -> PyResult<()> {
        let token = exact_token(token)?;
        self.runtime
            .commit(token)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(())
    }

    fn discard(&mut self, token: Vec<u8>) -> PyResult<()> {
        let token = exact_token(token)?;
        self.runtime
            .discard(token)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        Ok(())
    }

    fn readiness(&self) -> NativeResidentOrganismObservation {
        native_resident_observation(&self.runtime)
    }

    fn save<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new(py, self.runtime.active_envelope())
    }

    /// Read-only observation of the retained distributed formations: one
    /// entry per admitted mosaic as ``(member_lineage_hexes,
    /// recurrence_bond_count)``.  Structure only — no recognition, recall,
    /// meaning, or capital is emitted — and reading advances nothing.
    fn observe_retained_formations(&self) -> Vec<(Vec<String>, usize)> {
        self.runtime
            .cognitive_state()
            .observe_retained_formation_members()
            .into_iter()
            .map(|(lineages, recurrence_bond_count)| {
                (
                    lineages.iter().map(|lineage| hex_bytes(lineage)).collect(),
                    recurrence_bond_count,
                )
            })
            .collect()
    }

    /// Exact read-only retained-formation evidence as
    /// ``(receipt, members, original_bonds, recurrence_bonds,
    /// reinforcement_count)``.  Each bond is its two stable lineage hexes
    /// and parallel-contact ordinal.  No semantic identity is introduced.
    #[allow(clippy::type_complexity)]
    fn observe_retained_formation_structures(
        &self,
    ) -> PyResult<
        Vec<(
            String,
            Vec<String>,
            Vec<(String, String, u32)>,
            Vec<(String, String, u32)>,
            u64,
        )>,
    > {
        let bond = |reference: &StablePhysicalBondReference| {
            let (left, right) = reference.endpoints();
            (
                hex_bytes(&left),
                hex_bytes(&right),
                reference.parallel_ordinal(),
            )
        };
        self.runtime
            .cognitive_state()
            .observe_retained_formation_structures(self.runtime.budget.max_fabric_bytes)
            .map_err(|error| PyValueError::new_err(error.to_string()))
            .map(|formations| {
                formations
                    .into_iter()
                    .map(|(receipt, members, original, recurrence, reinforcements)| {
                        (
                            hex_bytes(&receipt),
                            members.iter().map(|lineage| hex_bytes(lineage)).collect(),
                            original.iter().map(&bond).collect(),
                            recurrence.iter().map(&bond).collect(),
                            reinforcements,
                        )
                    })
                    .collect()
            })
    }

    /// Exact read-only latest proper-cue evidence as
    /// ``(formation_receipt, cue_member_lineage_hexes)``. The receipt
    /// correlates this witness with `observe_retained_formation_structures`;
    /// neither value drives cognition or advances the organism.
    fn observe_retained_formation_recurrence_cues(&self) -> PyResult<Vec<(String, Vec<String>)>> {
        self.runtime
            .cognitive_state()
            .observe_retained_formation_recurrence_cues(self.runtime.budget.max_fabric_bytes)
            .map_err(|error| PyValueError::new_err(error.to_string()))
            .map(|formations| {
                formations
                    .into_iter()
                    .map(|(receipt, cue)| {
                        (
                            hex_bytes(&receipt),
                            cue.iter().map(|lineage| hex_bytes(lineage)).collect(),
                        )
                    })
                    .collect()
            })
    }

    /// Exact retained recurrence evidence as
    /// ``(formation_receipt, cue_lineages, physical_origin)``.
    fn observe_retained_formation_recurrence_evidence(
        &self,
    ) -> PyResult<Vec<(String, Vec<String>, String)>> {
        self.runtime
            .cognitive_state()
            .observe_retained_formation_recurrence_evidence(self.runtime.budget.max_fabric_bytes)
            .map_err(|error| PyValueError::new_err(error.to_string()))
            .map(|formations| {
                formations
                    .into_iter()
                    .map(|(receipt, cue, origin)| {
                        (
                            hex_bytes(&receipt),
                            cue.iter().map(|lineage| hex_bytes(lineage)).collect(),
                            origin.to_owned(),
                        )
                    })
                    .collect()
            })
    }

    /// The retired archive navigator.
    ///
    /// This used to walk a neuron's archived posting chain and return episode
    /// addresses.  It read the cold archive that is now retired, it was
    /// reachable from no endpoint and called by nothing, and the doctrine it
    /// lived under (docs/GUALA_DARPA_FIRST_PROOF_BOUNDARY_2026-08-04.md §4)
    /// names "database retrieval presented as recall" among the mechanisms
    /// that must not be extended.  It is refused rather than silently absent,
    /// so a caller learns what is gone and why.
    ///
    /// What replaces it for anyone asking what she holds is
    /// `observe_retained_formations`, which reads her BODY.
    fn navigate_hippocampal(&self, _lineage_hex: String) -> PyResult<()> {
        Err(PyValueError::new_err(
            "hippocampal archive navigation is retired: the cold episode \
             archive is no longer written or read, because it never carried \
             recognition, recall or meaning — her memories are the retained \
             formations in her body. Use observe_retained_formations().",
        ))
    }
}

#[pyfunction]
fn exact_virtual_yaw_trajectory(
    predecessor_heading_millidegrees: u32,
    signed_displacement_millidegrees: i32,
    duration_microseconds: u32,
) -> PyResult<(u32, Vec<i32>)> {
    let predecessor = YawBodyState::new(predecessor_heading_millidegrees)
        .map_err(|error| PyValueError::new_err(format!("{error:?}")))?;
    let actuation =
        SignedYawActuation::new(signed_displacement_millidegrees, duration_microseconds)
            .map_err(|error| PyValueError::new_err(format!("{error:?}")))?;
    let settled = settle_signed_yaw_actuation(predecessor, actuation)
        .map_err(|error| PyValueError::new_err(format!("{error:?}")))?;
    Ok((
        settled.successor.heading_millidegrees(),
        settled.trajectory.as_slice().to_vec(),
    ))
}

#[pyfunction]
fn exact_articulatory_unit_trajectory<'py>(
    py: Python<'py>,
    recruitments: Vec<(u32, u128)>,
) -> PyResult<(
    u32,
    Vec<i16>,
    Bound<'py, PyBytes>,
    i32,
    i32,
    i32,
    i32,
    u128,
    u128,
    usize,
)> {
    let settled = settle_articulatory_unit_discharge(&recruitments)
        .map_err(|error| PyValueError::new_err(format!("{error:?}")))?;
    let body_bytes = settled
        .body_mechanical_trajectories
        .iter()
        .flat_map(|trajectory| trajectory.iter())
        .flat_map(|sample| sample.to_le_bytes())
        .collect::<Vec<_>>();
    Ok((
        ARTICULATORY_SAMPLE_RATE_HZ,
        settled.radiated_pressure_pcm,
        PyBytes::new(py, &body_bytes),
        settled.peak_breath_flow_pcm,
        settled.glottal_open_samples_at_apex,
        settled.mouth_area_square_millimetres_at_apex,
        settled.perioral_area_displacement_square_millimetres,
        settled.applied_motor_quanta,
        settled.stalled_motor_quanta,
        settled.relaxation_sample_count,
    ))
}

#[pyfunction]
#[pyo3(signature = (
    current_envelope,
    max_envelope_bytes=67_108_864,
    max_fabric_bytes=67_108_000,
    max_logical_peak_bytes=536_870_912
))]
fn restore_native_resident_organism_runtime(
    py: Python<'_>,
    current_envelope: Vec<u8>,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> PyResult<NativeResidentOrganismRuntime> {
    let runtime = py
        .allow_threads(move || {
            let budget =
                RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)?;
            ResidentOrganismRuntime::restore_envelope(current_envelope, budget)
        })
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    Ok(NativeResidentOrganismRuntime { runtime })
}

fn migrate_resident_organism_exact_energy_envelope(
    current_envelope: Vec<u8>,
    budget: RuntimeBudget,
) -> Result<Vec<u8>, RuntimeError> {
    let (
        identity,
        organism_tick,
        fabric_generation,
        joint,
        migrated_cognitive,
        vestibular,
        articulated_body,
    ) = {
        let parsed = parse_current_envelope(&current_envelope, budget)?;
        let cognitive = parsed
            .cognitive_bytes
            .ok_or_else(|| RuntimeError::CognitiveFormation("cognitive state is absent".into()))?;
        let cognitive_budget = cognitive_budget_after_joint(parsed.joint_bytes.len(), budget)?;
        let migrated =
            ResidentCognitiveFormationState::migrate_to_current_format(cognitive, cognitive_budget)
                .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        (
            parsed.identity,
            parsed.organism_tick,
            parsed.fabric_generation,
            parsed.joint_bytes.to_vec(),
            migrated,
            parsed
                .vestibular
                .unwrap_or(ResidentVestibularBody::phase_one_genesis()?),
            parsed
                .articulated_body
                .unwrap_or_else(ArticulatedBodyState::at_neutral),
        )
    };
    let fabric = encode_fabric(
        fabric_generation,
        &joint,
        &migrated_cognitive,
        &vestibular,
        &articulated_body,
        budget,
    )?;
    let migrated_envelope = encode_envelope(identity, organism_tick, &fabric, budget)?;
    let restored = ResidentOrganismRuntime::restore_envelope(migrated_envelope.clone(), budget)?;
    if restored.observation().identity != identity
        || restored.observation().organism_tick != organism_tick
        || restored.observation().fabric_generation != fabric_generation
    {
        return Err(RuntimeError::MigrationInvariantChanged);
    }
    Ok(migrated_envelope)
}

#[pyfunction]
#[pyo3(signature = (
    current_envelope,
    max_envelope_bytes=67_108_864,
    max_fabric_bytes=67_108_000,
    max_logical_peak_bytes=536_870_912
))]
fn migrate_native_resident_organism_exact_energy(
    py: Python<'_>,
    current_envelope: Vec<u8>,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> PyResult<Vec<u8>> {
    py.allow_threads(move || {
        let budget =
            RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)?;
        migrate_resident_organism_exact_energy_envelope(current_envelope, budget)
    })
    .map_err(|error| PyValueError::new_err(error.to_string()))
}

#[pyfunction]
#[pyo3(signature = (
    organism_identity,
    organism_tick=0,
    max_envelope_bytes=67_108_864,
    max_fabric_bytes=67_108_000,
    max_logical_peak_bytes=536_870_912
))]
fn create_native_resident_organism_runtime(
    py: Python<'_>,
    organism_identity: String,
    organism_tick: u64,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> PyResult<NativeResidentOrganismRuntime> {
    let runtime = py
        .allow_threads(move || {
            let budget =
                RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)?;
            create_resident_genesis(&organism_identity, organism_tick, budget)
        })
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    Ok(NativeResidentOrganismRuntime { runtime })
}

#[pyfunction]
#[pyo3(signature = (
    organism_identity,
    organism_tick,
    anatomy_episode,
    seed_groups,
    max_envelope_bytes=67_108_864,
    max_fabric_bytes=67_108_000,
    max_logical_peak_bytes=536_870_912
))]
fn create_native_resident_organism_runtime_with_growth_dna(
    py: Python<'_>,
    organism_identity: String,
    organism_tick: u64,
    anatomy_episode: PyRef<'_, NativeJointSourceEpisode>,
    seed_groups: Vec<(Vec<usize>, Vec<(usize, usize, i64)>)>,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> PyResult<NativeResidentOrganismRuntime> {
    let anatomy_episode = anatomy_episode.clone();
    let runtime = py
        .allow_threads(move || {
            let budget =
                RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)?;
            create_resident_genesis_with_growth_dna(
                &organism_identity,
                organism_tick,
                &anatomy_episode,
                &seed_groups,
                budget,
            )
        })
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    Ok(NativeResidentOrganismRuntime { runtime })
}

fn create_resident_genesis(
    organism_identity: &str,
    organism_tick: u64,
    budget: RuntimeBudget,
) -> Result<ResidentOrganismRuntime, RuntimeError> {
    create_resident_genesis_from_state(
        organism_identity,
        organism_tick,
        ResidentCognitiveFormationState::default(),
        budget,
    )
}

/// Genesis carrying authored developmental growth DNA.
///
/// Identical to `create_resident_genesis` except that the cognitive state is
/// born with the caller's authored unexpressed electrical seeds. Each seed
/// group names port indices of `anatomy_episode` and authored contacts as
/// `(left_seed_index, right_seed_index, conductance_picosiemens)`. This
/// boundary never chooses a contact; a seed expresses later only when a grown
/// cohort's reached source sites exactly equal the seed's sites.
fn create_resident_genesis_with_growth_dna(
    organism_identity: &str,
    organism_tick: u64,
    anatomy_episode: &NativeJointSourceEpisode,
    seed_groups: &[(Vec<usize>, Vec<(usize, usize, i64)>)],
    budget: RuntimeBudget,
) -> Result<ResidentOrganismRuntime, RuntimeError> {
    let seeds = build_authored_growth_dna_seeds(anatomy_episode, seed_groups)
        .map_err(RuntimeError::CognitiveFormation)?;
    let cognitive = ResidentCognitiveFormationState::from_developmental_electrical_seeds(seeds)
        .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
    create_resident_genesis_from_state(organism_identity, organism_tick, cognitive, budget)
}

fn create_resident_genesis_from_state(
    organism_identity: &str,
    organism_tick: u64,
    cognitive: ResidentCognitiveFormationState,
    budget: RuntimeBudget,
) -> Result<ResidentOrganismRuntime, RuntimeError> {
    let identity = canonical_identity(organism_identity)?;
    let joint = encode_empty_mounted_joint_state().map_err(RuntimeError::MountedTransition)?;
    let cognitive_budget = cognitive_budget_after_joint(joint.len(), budget)?;
    let prepopulation = cognitive
        .encode(cognitive_budget)
        .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
    let cognitive = ResidentCognitiveFormationState::migrate_to_current_format(
        &prepopulation,
        cognitive_budget,
    )
    .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
    let vestibular = ResidentVestibularBody::phase_one_genesis()?;
    let articulated_body = ArticulatedBodyState::at_neutral();
    let fabric = encode_fabric(
        0,
        &joint,
        &cognitive,
        &vestibular,
        &articulated_body,
        budget,
    )?;
    let envelope = encode_envelope(identity, organism_tick, &fabric, budget)?;
    ResidentOrganismRuntime::restore_envelope(envelope, budget)
}

pub fn create_native_resident_d3_genesis(
    organism_identity: &str,
    organism_tick: u64,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> Result<Vec<u8>, String> {
    let budget = RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)
        .map_err(|error| error.to_string())?;
    create_resident_genesis(organism_identity, organism_tick, budget)
        .map(|runtime| runtime.active_envelope().to_vec())
        .map_err(|error| error.to_string())
}

pub fn transition_native_resident_d3(
    current_envelope: Vec<u8>,
    source: &NativeJointSourceEpisode,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> Result<NativeResidentD3Transition, String> {
    let budget = RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)
        .map_err(|error| error.to_string())?;
    let mut runtime = ResidentOrganismRuntime::restore_envelope(current_envelope, budget)
        .map_err(|error| error.to_string())?;
    let prepared = runtime
        .prepare_source(source)
        .map_err(|error| error.to_string())?;
    runtime
        .commit(prepared.token)
        .map_err(|error| error.to_string())?;
    let observation = runtime.observation();
    let successor = runtime.active_envelope().to_vec();
    if sha256(&successor) != observation.state_receipt
        || observation.source_authority != Some(source.joint_source_authority_receipt())
        || observation.python_callback_count != 0
    {
        return Err(RuntimeError::SealedStateChanged.to_string());
    }
    Ok(NativeResidentD3Transition {
        successor,
        state_receipt: observation.state_receipt,
        source_authority: source.joint_source_authority_receipt(),
        complete_neuron_count: observation.complete_neuron_count,
        complete_neuron_fractal_count: observation.complete_neuron_fractal_count,
        cognitive_mosaic_count: observation.cognitive_mosaic_count,
        partial_cue_reassembly_count: observation.partial_cue_reassembly_count,
        endogenous_partial_cue_reassembly_count: observation
            .endogenous_partial_cue_reassembly_count,
    })
}

#[pyfunction]
#[pyo3(signature = (
    prior_envelope,
    source,
    max_envelope_bytes=67_108_864,
    max_fabric_bytes=67_108_000,
    max_logical_peak_bytes=201_326_592
))]
fn transition_native_organism_runtime(
    py: Python<'_>,
    prior_envelope: Vec<u8>,
    source: PyRef<'_, NativeJointSourceEpisode>,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> PyResult<NativeOrganismRuntimeTransition> {
    let source = source.clone();
    let result = py
        .allow_threads(move || {
            let budget =
                RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)?;
            OrganismRuntime::restore_envelope(prior_envelope, budget)?
                .advance_mounted(&source, budget)
        })
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    if result.observation.state_receipt != result.successor.receipt {
        return Err(PyValueError::new_err(
            RuntimeError::SealedStateChanged.to_string(),
        ));
    }
    Ok(NativeOrganismRuntimeTransition {
        payload: Arc::from(result.successor.bytes),
        observation: result.observation,
    })
}

#[pyfunction]
#[pyo3(signature = (
    current_envelope,
    max_envelope_bytes=67_108_864,
    max_fabric_bytes=67_108_000,
    max_logical_peak_bytes=201_326_592
))]
fn restore_native_organism_runtime(
    py: Python<'_>,
    current_envelope: Vec<u8>,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> PyResult<NativeOrganismRuntimeTransition> {
    let result = py
        .allow_threads(move || {
            let budget =
                RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)?;
            let runtime = OrganismRuntime::restore_envelope(current_envelope, budget)?;
            let observation = runtime.observe().clone();
            let sealed = runtime.seal(max_envelope_bytes)?;
            Ok::<_, RuntimeError>((sealed, observation))
        })
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    let (sealed, observation) = result;
    if observation.state_receipt != sealed.receipt {
        return Err(PyValueError::new_err(
            RuntimeError::SealedStateChanged.to_string(),
        ));
    }
    Ok(NativeOrganismRuntimeTransition {
        payload: Arc::from(sealed.bytes),
        observation,
    })
}

#[pyfunction]
#[pyo3(signature = (
    legacy_glmfab03,
    expected_content_sha256,
    organism_identity,
    authenticated_predecessor_tick,
    max_envelope_bytes=67_108_864,
    max_fabric_bytes=67_108_000,
    max_logical_peak_bytes=536_870_912
))]
fn migrate_authenticated_task853_predecessor_to_native_organism_runtime(
    py: Python<'_>,
    legacy_glmfab03: Vec<u8>,
    expected_content_sha256: Vec<u8>,
    organism_identity: String,
    authenticated_predecessor_tick: u64,
    max_envelope_bytes: usize,
    max_fabric_bytes: usize,
    max_logical_peak_bytes: usize,
) -> PyResult<NativeAuthenticatedTask853RuntimeMigration> {
    if expected_content_sha256.len() != 32 {
        return Err(PyValueError::new_err(
            "authenticated task-853 GLMFAB03 SHA-256 must contain exactly 32 bytes",
        ));
    }
    let expected_content_sha256: [u8; 32] = expected_content_sha256
        .try_into()
        .expect("checked SHA-256 width");
    let migrated = py
        .allow_threads(move || {
            let budget =
                RuntimeBudget::new(max_envelope_bytes, max_fabric_bytes, max_logical_peak_bytes)?;
            migrate_authenticated_task853_predecessor(
                legacy_glmfab03,
                expected_content_sha256,
                &organism_identity,
                authenticated_predecessor_tick,
                budget,
            )
        })
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    if migrated.observation.state_receipt != migrated.sealed.receipt {
        return Err(PyValueError::new_err(
            RuntimeError::SealedStateChanged.to_string(),
        ));
    }
    Ok(NativeAuthenticatedTask853RuntimeMigration {
        payload: Arc::from(migrated.sealed.bytes),
        observation: migrated.observation,
        legacy_fabric_receipt: migrated.legacy_fabric_receipt,
    })
}

fn migrate_authenticated_task853_predecessor(
    legacy_glmfab03: Vec<u8>,
    expected_content_sha256: [u8; 32],
    organism_identity: &str,
    authenticated_predecessor_tick: u64,
    budget: RuntimeBudget,
) -> Result<AuthenticatedTask853RuntimeMigration, RuntimeError> {
    migrate_authenticated_legacy_predecessor(
        legacy_glmfab03,
        expected_content_sha256,
        organism_identity,
        authenticated_predecessor_tick,
        budget,
        LegacyMigrationAuthority {
            identity: TASK853_IDENTITY,
            organism_tick: TASK853_ORGANISM_TICK,
            fabric_receipt: TASK853_GLMFAB03_SHA256,
            fabric_generation: 13,
            mounted_generation: 2,
        },
    )
}

fn migrate_authenticated_legacy_predecessor(
    legacy_glmfab03: Vec<u8>,
    expected_content_sha256: [u8; 32],
    organism_identity: &str,
    authenticated_predecessor_tick: u64,
    budget: RuntimeBudget,
    authority: LegacyMigrationAuthority,
) -> Result<AuthenticatedTask853RuntimeMigration, RuntimeError> {
    let identity = canonical_identity(organism_identity)?;
    if identity.as_slice() != authority.identity.as_bytes() {
        return Err(RuntimeError::Task853IdentityMismatch);
    }
    if authenticated_predecessor_tick != authority.organism_tick {
        return Err(RuntimeError::Task853TickMismatch);
    }
    let derived_budget = budget.derive()?;
    let migration = migrate_authenticated_glmfab03_to_current(
        &legacy_glmfab03,
        expected_content_sha256,
        budget.max_fabric_bytes,
        derived_budget.max_joint_working_bytes,
    )
    .map_err(RuntimeError::LegacyMigration)?;
    if migration.legacy_fabric_receipt != authority.fabric_receipt {
        return Err(RuntimeError::Task853LegacyReceiptMismatch);
    }
    let current_fabric_receipt = sha256(&migration.current_fabric);
    let envelope = encode_envelope(
        identity,
        authenticated_predecessor_tick,
        &migration.current_fabric,
        budget,
    )?;
    let parsed = parse_current_envelope(&envelope, budget)?;
    if parsed.identity != identity
        || parsed.organism_tick != authenticated_predecessor_tick
        || sha256(parsed.fabric_bytes) != current_fabric_receipt
        || parsed.fabric_generation != authority.fabric_generation
        || migration.summary.generation != authority.mounted_generation
    {
        return Err(RuntimeError::MigrationInvariantChanged);
    }
    let cognitive = restore_cognitive_state(&parsed, budget)?;
    let observation = make_restored_observation(
        &envelope,
        parsed,
        migration.summary,
        cognitive.summary(),
        cognitive
            .mosaic_of_mosaics_count()
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?,
        derived_budget,
    );
    if observation.mounted_step_completed
        || observation.physical_transition_claimed
        || observation.cognitive_formation_claimed
        || observation.python_callback_count != 0
    {
        return Err(RuntimeError::MigrationInvariantChanged);
    }
    let sealed = SealedRuntimeState {
        receipt: observation.state_receipt,
        bytes: envelope,
    };
    Ok(AuthenticatedTask853RuntimeMigration {
        sealed,
        observation,
        legacy_fabric_receipt: migration.legacy_fabric_receipt,
    })
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<NativeOrganismRuntimeTransition>()?;
    module.add_class::<NativeAuthenticatedTask853RuntimeMigration>()?;
    module.add_class::<NativeResidentOrganismRuntime>()?;
    module.add_class::<NativeResidentOrganismObservation>()?;
    module.add_class::<NativeResidentOrganismPrepare>()?;
    module.add_class::<NativeResidentUnsealedIntake>()?;
    module.add_function(wrap_pyfunction!(
        transition_native_organism_runtime,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(restore_native_organism_runtime, module)?)?;
    module.add_function(wrap_pyfunction!(exact_virtual_yaw_trajectory, module)?)?;
    module.add_function(wrap_pyfunction!(
        exact_articulatory_unit_trajectory,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(
        restore_native_resident_organism_runtime,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(
        migrate_native_resident_organism_exact_energy,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(
        create_native_resident_organism_runtime,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(
        create_native_resident_organism_runtime_with_growth_dna,
        module
    )?)?;
    module.add_function(wrap_pyfunction!(
        migrate_authenticated_task853_predecessor_to_native_organism_runtime,
        module
    )?)?;
    Ok(())
}

#[derive(Debug)]
pub(crate) struct OrganismRuntime {
    envelope: Vec<u8>,
    observation: RuntimeObservation,
}

impl OrganismRuntime {
    pub(crate) fn restore_current(
        identity: &str,
        organism_tick: u64,
        fabric: Vec<u8>,
        budget: RuntimeBudget,
    ) -> Result<Self, RuntimeError> {
        let identity = canonical_identity(identity)?;
        parse_current_fabric(&fabric, budget)?;
        let envelope = encode_envelope(identity, organism_tick, &fabric, budget)?;
        Self::restore_envelope(envelope, budget)
    }

    pub(crate) fn restore_envelope(
        envelope: Vec<u8>,
        budget: RuntimeBudget,
    ) -> Result<Self, RuntimeError> {
        let derived_budget = budget.derive()?;
        let parsed = parse_current_envelope(&envelope, budget)?;
        let joint = inspect_mounted_joint_dsf_summary(
            parsed.joint_bytes,
            derived_budget.max_joint_state_bytes,
            derived_budget.max_joint_working_bytes,
        )
        .map_err(RuntimeError::MountedTransition)?;
        let cognitive = restore_cognitive_state(&parsed, budget)?;
        let observation = make_restored_observation(
            &envelope,
            parsed,
            joint,
            cognitive.summary(),
            cognitive
                .mosaic_of_mosaics_count()
                .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?,
            derived_budget,
        );
        Ok(Self {
            envelope,
            observation,
        })
    }

    pub(crate) fn observe(&self) -> &RuntimeObservation {
        &self.observation
    }

    #[cfg(not(test))]
    pub(crate) fn advance_mounted(
        &self,
        _source: &NativeJointSourceEpisode,
        _budget: RuntimeBudget,
    ) -> Result<RuntimeStepResult, RuntimeError> {
        Err(RuntimeError::AdmittedSourceRequired)
    }

    #[cfg(test)]
    pub(crate) fn advance_mounted(
        &self,
        source: &NativeJointSourceEpisode,
        budget: RuntimeBudget,
    ) -> Result<RuntimeStepResult, RuntimeError> {
        let derived_budget = budget.derive()?;
        let parsed = parse_current_envelope(&self.envelope, budget)?;
        let successor_organism_tick = parsed
            .organism_tick
            .checked_add(1)
            .ok_or(RuntimeError::OrganismTickOverflow)?;
        let successor_fabric_generation = parsed
            .fabric_generation
            .checked_add(1)
            .ok_or(RuntimeError::FabricGenerationOverflow)?;
        let predecessor_mounted_generation = self.observation.mounted_generation;
        // NativeJointSourceEpisode is immutable and its authority was computed
        // once when its canonical source body was admitted. Capture that exact
        // admitted pair before any mounted physics; do not hash it again here.
        let admitted_source_authority = source.joint_source_authority_receipt();
        let admitted_source_body = source.joint_source_body();
        let prepared = transition_mounted_joint_dsf(
            parsed.joint_bytes,
            source,
            derived_budget.max_joint_state_bytes,
            derived_budget.max_joint_working_bytes,
        )
        .map_err(RuntimeError::MountedTransition)?;
        if prepared.predecessor_generation() != predecessor_mounted_generation
            || prepared.predecessor_generation().checked_add(1)
                != Some(prepared.successor_generation())
        {
            return Err(RuntimeError::MountedGenerationDiscontinuity);
        }
        if prepared.source_authority() != admitted_source_authority
            || prepared.source_body() != admitted_source_body.as_ref()
        {
            return Err(RuntimeError::MountedSourceSubstitution);
        }
        let successor_mounted_generation = prepared.successor_generation();
        let source_authority = prepared.source_authority();
        let source_cohort_l0_l4_evaluation_count = prepared.transition().l0_l4_evaluation_count;
        let prepared_dsf_delivery_count = prepared
            .fields()
            .iter()
            .try_fold(0usize, |count, field| {
                count.checked_add(field.neurons().len())
            })
            .ok_or(RuntimeError::BudgetArithmeticOverflow)?;
        if prepared.fields().len() != source_cohort_l0_l4_evaluation_count
            || prepared.transition().joint_field_count != source_cohort_l0_l4_evaluation_count
            || prepared.transition().dsf_delivery_count != prepared_dsf_delivery_count
        {
            return Err(RuntimeError::MountedGenerationDiscontinuity);
        }
        let cognitive_state = restore_cognitive_state(&parsed, budget)?;
        let cognitive_budget = cognitive_budget_after_joint(prepared.state_bytes().len(), budget)?;
        let cognitive = cognitive_state
            .prepare(source, cognitive_budget)
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        let cognitive_bytes = cognitive_state
            .encode_successor(&cognitive, cognitive_budget)
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string()))?;
        let cognitive_observation = cognitive.observation().clone();
        let (joint_state, transition) = prepared.into_serialized_parts();
        let vestibular =
            parsed
                .vestibular
                .as_ref()
                .ok_or(RuntimeError::UnsupportedFabricVersion(
                    PRE_VESTIBULAR_FABRIC_VERSION,
                ))?;
        let articulated_body =
            parsed
                .articulated_body
                .as_ref()
                .ok_or(RuntimeError::UnsupportedFabricVersion(
                    PRE_ARTICULATED_FABRIC_VERSION,
                ))?;
        let fabric = encode_fabric(
            successor_fabric_generation,
            &joint_state,
            &cognitive_bytes,
            vestibular,
            articulated_body,
            budget,
        )?;
        let envelope = encode_envelope(parsed.identity, successor_organism_tick, &fabric, budget)?;
        let observation = make_step_observation(
            &envelope,
            parsed.identity,
            parsed.organism_tick,
            successor_organism_tick,
            parsed.fabric_generation,
            successor_fabric_generation,
            predecessor_mounted_generation,
            successor_mounted_generation,
            &fabric,
            source_authority,
            transition,
            source_cohort_l0_l4_evaluation_count,
            derived_budget,
            self.observation.state_receipt,
            &cognitive_observation,
        );
        let sealed = SealedRuntimeState {
            receipt: observation.state_receipt,
            bytes: envelope,
        };
        Ok(RuntimeStepResult {
            successor: sealed,
            observation,
        })
    }

    pub(crate) fn seal(self, max_encoded_bytes: usize) -> Result<SealedRuntimeState, RuntimeError> {
        if self.envelope.len() > max_encoded_bytes {
            return Err(RuntimeError::EnvelopeBudgetExceeded);
        }
        let receipt = sha256(&self.envelope);
        if self.envelope.len() != self.observation.state_bytes
            || receipt != self.observation.state_receipt
        {
            return Err(RuntimeError::SealedStateChanged);
        }
        Ok(SealedRuntimeState {
            bytes: self.envelope,
            receipt,
        })
    }
}

#[derive(Clone)]
struct ParsedEnvelope<'a> {
    identity: [u8; IDENTITY_BYTES],
    organism_tick: u64,
    fabric_bytes: &'a [u8],
    fabric_generation: u64,
    joint_bytes: &'a [u8],
    cognitive_bytes: Option<&'a [u8]>,
    vestibular: Option<ResidentVestibularBody>,
    articulated_body: Option<ArticulatedBodyState>,
}

fn parse_current_envelope<'a>(
    envelope: &'a [u8],
    budget: RuntimeBudget,
) -> Result<ParsedEnvelope<'a>, RuntimeError> {
    if envelope.len() > budget.max_envelope_bytes {
        return Err(RuntimeError::EnvelopeBudgetExceeded);
    }
    if envelope.len() < FIXED_BYTES {
        return Err(RuntimeError::EnvelopeEndedEarly);
    }
    if &envelope[..MAGIC.len()] != MAGIC {
        return Err(RuntimeError::BadEnvelopeMagic);
    }
    let mut offset = MAGIC.len();
    let version = take_u16(envelope, &mut offset)?;
    if version != VERSION {
        return Err(RuntimeError::UnsupportedEnvelopeVersion(version));
    }
    let identity_end = offset
        .checked_add(IDENTITY_BYTES)
        .ok_or(RuntimeError::EnvelopeEndedEarly)?;
    let identity_text = std::str::from_utf8(
        envelope
            .get(offset..identity_end)
            .ok_or(RuntimeError::EnvelopeEndedEarly)?,
    )
    .map_err(|_| RuntimeError::InvalidIdentity)?;
    let identity = canonical_identity(identity_text)?;
    offset = identity_end;
    let organism_tick = take_u64(envelope, &mut offset)?;
    let fabric_len = take_u32(envelope, &mut offset)? as usize;
    if fabric_len > budget.max_fabric_bytes {
        return Err(RuntimeError::FabricBudgetExceeded);
    }
    let fabric_end = offset
        .checked_add(fabric_len)
        .ok_or(RuntimeError::FabricLengthOverflow)?;
    if fabric_end != envelope.len() {
        return Err(RuntimeError::FabricLengthMismatch);
    }
    let fabric_bytes = &envelope[offset..fabric_end];
    let (fabric_generation, joint_bytes, cognitive_bytes, vestibular, articulated_body) =
        parse_current_fabric(fabric_bytes, budget)?;
    Ok(ParsedEnvelope {
        identity,
        organism_tick,
        fabric_bytes,
        fabric_generation,
        joint_bytes,
        cognitive_bytes,
        vestibular,
        articulated_body,
    })
}

fn parse_current_fabric(
    fabric: &[u8],
    budget: RuntimeBudget,
) -> Result<
    (
        u64,
        &[u8],
        Option<&[u8]>,
        Option<ResidentVestibularBody>,
        Option<ArticulatedBodyState>,
    ),
    RuntimeError,
> {
    if fabric.len() > budget.max_fabric_bytes {
        return Err(RuntimeError::FabricBudgetExceeded);
    }
    if fabric.len() < LEGACY_FABRIC_FIXED_BYTES {
        return Err(RuntimeError::BadFabricMagic);
    }
    let magic = &fabric[..FABRIC_MAGIC.len()];
    if magic != FABRIC_MAGIC
        && magic != PRE_ARTICULATED_FABRIC_MAGIC
        && magic != PRE_VESTIBULAR_FABRIC_MAGIC
        && magic != LEGACY_FABRIC_MAGIC
    {
        return Err(RuntimeError::BadFabricMagic);
    }
    let mut offset = FABRIC_MAGIC.len();
    let version = take_u16(fabric, &mut offset)?;
    let legacy = magic == LEGACY_FABRIC_MAGIC && version == LEGACY_FABRIC_VERSION;
    let pre_vestibular =
        magic == PRE_VESTIBULAR_FABRIC_MAGIC && version == PRE_VESTIBULAR_FABRIC_VERSION;
    let pre_articulated =
        magic == PRE_ARTICULATED_FABRIC_MAGIC && version == PRE_ARTICULATED_FABRIC_VERSION;
    let current = magic == FABRIC_MAGIC && version == FABRIC_VERSION;
    if !legacy && !pre_vestibular && !pre_articulated && !current {
        return Err(RuntimeError::UnsupportedFabricVersion(version));
    }
    let generation = take_u64(fabric, &mut offset)?;
    let joint_len = take_u32(fabric, &mut offset)? as usize;
    let cognitive_len = if current || pre_articulated || pre_vestibular {
        take_u32(fabric, &mut offset)? as usize
    } else {
        0
    };
    let vestibular = if current || pre_articulated {
        let anatomy_end = offset
            .checked_add(FUNCTIONAL_VESTIBULAR_ANATOMY_CODEC_BYTES)
            .ok_or(RuntimeError::FabricLengthOverflow)?;
        let anatomy = decode_functional_vestibular_anatomy(
            fabric
                .get(offset..anatomy_end)
                .ok_or(RuntimeError::EnvelopeEndedEarly)?,
        )
        .map_err(|error| RuntimeError::Vestibular(format!("{error:?}")))?;
        offset = anatomy_end;
        let canal_end = offset
            .checked_add(CANAL_STATE_BYTES)
            .ok_or(RuntimeError::FabricLengthOverflow)?;
        let canal = decode_canal_state(
            anatomy.canal_anatomy(),
            fabric
                .get(offset..canal_end)
                .ok_or(RuntimeError::EnvelopeEndedEarly)?,
        )
        .map_err(|error| RuntimeError::Vestibular(format!("{error:?}")))?;
        offset = canal_end;
        let source_tick = take_u64(fabric, &mut offset)?;
        Some(ResidentVestibularBody {
            anatomy,
            canal,
            source_tick,
        })
    } else {
        None
    };
    let articulated_body = if current {
        let body_end = offset
            .checked_add(ARTICULATED_BODY_STATE_BYTES)
            .ok_or(RuntimeError::FabricLengthOverflow)?;
        let body = ArticulatedBodyState::decode(
            fabric
                .get(offset..body_end)
                .ok_or(RuntimeError::EnvelopeEndedEarly)?,
        )
        .map_err(|error| RuntimeError::ArticulatedBody(format!("{error:?}")))?;
        offset = body_end;
        Some(body)
    } else {
        None
    };
    let joint_end = offset
        .checked_add(joint_len)
        .ok_or(RuntimeError::FabricLengthOverflow)?;
    let cognitive_end = joint_end
        .checked_add(cognitive_len)
        .ok_or(RuntimeError::FabricLengthOverflow)?;
    if cognitive_end != fabric.len() {
        return Err(RuntimeError::FabricLengthMismatch);
    }
    Ok((
        generation,
        &fabric[offset..joint_end],
        (current || pre_articulated || pre_vestibular).then_some(&fabric[joint_end..cognitive_end]),
        vestibular,
        articulated_body,
    ))
}

fn encode_fabric(
    generation: u64,
    joint: &[u8],
    cognitive: &[u8],
    vestibular: &ResidentVestibularBody,
    articulated_body: &ArticulatedBodyState,
    budget: RuntimeBudget,
) -> Result<Vec<u8>, RuntimeError> {
    let length = FABRIC_FIXED_BYTES
        .checked_add(joint.len())
        .and_then(|value| value.checked_add(cognitive.len()))
        .ok_or(RuntimeError::FabricLengthOverflow)?;
    if length > budget.max_fabric_bytes {
        return Err(RuntimeError::FabricBudgetExceeded);
    }
    let mut output = Vec::with_capacity(length);
    output.extend_from_slice(FABRIC_MAGIC);
    output.extend_from_slice(&FABRIC_VERSION.to_le_bytes());
    output.extend_from_slice(&generation.to_le_bytes());
    output.extend_from_slice(
        &u32::try_from(joint.len())
            .map_err(|_| RuntimeError::FabricLengthOverflow)?
            .to_le_bytes(),
    );
    output.extend_from_slice(
        &u32::try_from(cognitive.len())
            .map_err(|_| RuntimeError::FabricLengthOverflow)?
            .to_le_bytes(),
    );
    output.extend_from_slice(&encode_functional_vestibular_anatomy(&vestibular.anatomy));
    output.extend_from_slice(&encode_canal_state(vestibular.canal));
    output.extend_from_slice(&vestibular.source_tick.to_le_bytes());
    output.extend_from_slice(
        &articulated_body
            .encode()
            .map_err(|error| RuntimeError::ArticulatedBody(format!("{error:?}")))?,
    );
    output.extend_from_slice(joint);
    output.extend_from_slice(cognitive);
    Ok(output)
}

fn cognitive_budget_after_joint(
    joint_bytes: usize,
    budget: RuntimeBudget,
) -> Result<usize, RuntimeError> {
    budget
        .max_fabric_bytes
        .checked_sub(FABRIC_FIXED_BYTES)
        .and_then(|value| value.checked_sub(joint_bytes))
        .filter(|value| *value > 0)
        .ok_or(RuntimeError::FabricBudgetExceeded)
}

fn restore_cognitive_state(
    parsed: &ParsedEnvelope<'_>,
    budget: RuntimeBudget,
) -> Result<ResidentCognitiveFormationState, RuntimeError> {
    let cognitive_budget = cognitive_budget_after_joint(parsed.joint_bytes.len(), budget)?;
    match parsed.cognitive_bytes {
        Some(bytes) => ResidentCognitiveFormationState::decode(bytes, cognitive_budget)
            .map_err(|error| RuntimeError::CognitiveFormation(error.to_string())),
        None => Ok(ResidentCognitiveFormationState::default()),
    }
}

fn encode_envelope(
    identity: [u8; IDENTITY_BYTES],
    organism_tick: u64,
    fabric: &[u8],
    budget: RuntimeBudget,
) -> Result<Vec<u8>, RuntimeError> {
    if fabric.len() > budget.max_fabric_bytes {
        return Err(RuntimeError::FabricBudgetExceeded);
    }
    let length = FIXED_BYTES
        .checked_add(fabric.len())
        .ok_or(RuntimeError::FabricLengthOverflow)?;
    if length > budget.max_envelope_bytes {
        return Err(RuntimeError::EnvelopeBudgetExceeded);
    }
    let mut output = Vec::with_capacity(length);
    output.extend_from_slice(MAGIC);
    output.extend_from_slice(&VERSION.to_le_bytes());
    output.extend_from_slice(&identity);
    output.extend_from_slice(&organism_tick.to_le_bytes());
    output.extend_from_slice(
        &u32::try_from(fabric.len())
            .map_err(|_| RuntimeError::FabricLengthOverflow)?
            .to_le_bytes(),
    );
    output.extend_from_slice(fabric);
    Ok(output)
}

fn make_restored_observation(
    envelope: &[u8],
    parsed: ParsedEnvelope<'_>,
    _joint: MountedJointDsfSummary,
    cognitive: CognitiveFormationSummary,
    mosaic_of_mosaics_count: usize,
    derived_budget: DerivedRuntimeBudget,
) -> RuntimeObservation {
    RuntimeObservation {
        schema: OBSERVATION_SCHEMA,
        scope: RESTORED_SCOPE,
        identity: parsed.identity,
        predecessor_state_receipt: None,
        predecessor_organism_tick: None,
        organism_tick: parsed.organism_tick,
        predecessor_fabric_generation: None,
        fabric_generation: parsed.fabric_generation,
        predecessor_mounted_generation: None,
        mounted_generation: cognitive.cognitive_ordinal,
        state_bytes: envelope.len(),
        state_receipt: sha256(envelope),
        fabric_bytes: parsed.fabric_bytes.len(),
        fabric_receipt: sha256(parsed.fabric_bytes),
        joint_field_count: 0,
        joint_neuron_count: 0,
        dsf_delivery_count: 0,
        complete_neuron_count: cognitive.complete_neuron_count,
        developmental_resting_neuron_count: cognitive.resting_neuron_count,
        physically_transitioned_neuron_count: 0,
        metabolically_perturbed_body_receptor_count: 0,
        externally_perturbed_body_receptor_count: 0,
        externally_perturbed_neuron_lineages: Vec::new(),
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
        recurrent_complete_neuron_fractal_count: 0,
        source_cohort_l0_l4_evaluation_count: 0,
        successor_l0_l4_replay_count: 0,
        joint_transition_receipt: None,
        episode_relation_candidate_receipt: None,
        source_authority: None,
        mounted_step_completed: false,
        physical_transition_claimed: false,
        cognitive_formation_claimed: false,
        cognitive_ordinal: cognitive.cognitive_ordinal,
        cognitive_trace_count: cognitive.trace_count,
        cognitive_mosaic_count: cognitive.mosaic_count,
        mosaic_of_mosaics_count,
        formation_activation_count: 0,
        partial_cue_reassembly_count: 0,
        endogenous_partial_cue_reassembly_count: 0,
        internally_reassembled_formation_cues: Vec::new(),
        externally_reassembled_formation_frontiers: Vec::new(),
        python_callback_count: 0,
        derived_budget,
        energy: cognitive.energy.clone(),
        rest_recovered_neuron_count: 0,
        rest_drained_dissipation_quanta: 0,
        unmet_dissipation_quanta: 0,
        membrane_returned_elementary_charges: 0,
    }
}

#[allow(clippy::too_many_arguments)]
fn make_step_observation(
    envelope: &[u8],
    identity: [u8; IDENTITY_BYTES],
    predecessor_organism_tick: u64,
    organism_tick: u64,
    predecessor_fabric_generation: u64,
    fabric_generation: u64,
    predecessor_mounted_generation: u64,
    mounted_generation: u64,
    fabric: &[u8],
    source_authority: [u8; 32],
    transition: MountedJointDsfTransition,
    source_cohort_l0_l4_evaluation_count: usize,
    derived_budget: DerivedRuntimeBudget,
    predecessor_state_receipt: [u8; 32],
    cognitive: &CognitiveFormationObservation,
) -> RuntimeObservation {
    RuntimeObservation {
        schema: OBSERVATION_SCHEMA,
        scope: MOUNTED_STEP_SCOPE,
        identity,
        predecessor_state_receipt: Some(predecessor_state_receipt),
        predecessor_organism_tick: Some(predecessor_organism_tick),
        organism_tick,
        predecessor_fabric_generation: Some(predecessor_fabric_generation),
        fabric_generation,
        predecessor_mounted_generation: Some(predecessor_mounted_generation),
        mounted_generation,
        state_bytes: envelope.len(),
        state_receipt: sha256(envelope),
        fabric_bytes: fabric.len(),
        fabric_receipt: sha256(fabric),
        joint_field_count: transition.joint_field_count,
        joint_neuron_count: transition.joint_neuron_count,
        dsf_delivery_count: transition.dsf_delivery_count,
        complete_neuron_count: cognitive.complete_neuron_count,
        developmental_resting_neuron_count: cognitive.resting_neuron_count,
        physically_transitioned_neuron_count: cognitive.physically_transitioned_neuron_count,
        metabolically_perturbed_body_receptor_count: cognitive
            .metabolically_perturbed_body_receptor_count,
        externally_perturbed_body_receptor_count: cognitive
            .externally_perturbed_body_receptor_count,
        externally_perturbed_neuron_lineages: cognitive
            .externally_perturbed_neuron_lineages
            .clone(),
        complete_neuron_fractal_count: cognitive.complete_neuron_fractal_count,
        emitted_neuron_fractals: cognitive.emitted_neuron_fractals.clone(),
        active_physical_bonds: cognitive.active_physical_bonds.clone(),
        changed_contact_channel_states: cognitive.changed_contact_channel_states.clone(),
        physical_frontier_routes: cognitive.physical_frontier_routes.clone(),
        preceding_distinct_physical_frontier_routes: cognitive
            .preceding_distinct_physical_frontier_routes
            .clone(),
        reached_and_foregone_physical_frontier_routes: cognitive
            .reached_and_foregone_physical_frontier_routes
            .clone(),
        working_causal_continuations: cognitive.working_causal_continuations.clone(),
        settled_working_frontier: cognitive.settled_working_frontier.clone(),
        physical_prediction_alternatives: cognitive.physical_prediction_alternatives.clone(),
        body_consequence_transfers: cognitive.body_consequence_transfers.clone(),
        affective_balance_trajectories: cognitive.affective_balance_trajectories.clone(),
        localized_fluid_chemistry: cognitive.localized_fluid_chemistry.clone(),
        localized_metabolic_strain_evaluated_body_receptor_lineages: cognitive
            .localized_metabolic_strain_evaluated_body_receptor_lineages
            .clone(),
        localized_metabolic_strain: cognitive.localized_metabolic_strain.clone(),
        organic_mosaic_relations: cognitive.organic_mosaic_relations.clone(),
        recurrent_complete_neuron_fractal_count: 0,
        source_cohort_l0_l4_evaluation_count,
        successor_l0_l4_replay_count: 0,
        joint_transition_receipt: transition.transition_receipt,
        episode_relation_candidate_receipt: transition.episode_relation_candidate_receipt,
        source_authority: Some(source_authority),
        mounted_step_completed: true,
        physical_transition_claimed: cognitive.physically_transitioned_neuron_count > 0,
        cognitive_formation_claimed: cognitive.trace_formed
            || cognitive.mosaic_formed.is_some()
            || !cognitive.activations.is_empty()
            || cognitive.partial_cue_reassembly_count() > 0
            || !cognitive.organic_mosaic_relations.is_empty(),
        cognitive_ordinal: cognitive.cognitive_ordinal,
        cognitive_trace_count: cognitive.trace_count,
        cognitive_mosaic_count: cognitive.mosaic_count,
        mosaic_of_mosaics_count: cognitive.mosaic_of_mosaics_count,
        formation_activation_count: cognitive.activations.len(),
        partial_cue_reassembly_count: cognitive.partial_cue_reassembly_count(),
        endogenous_partial_cue_reassembly_count: cognitive
            .endogenous_partial_cue_reassembly_count(),
        internally_reassembled_formation_cues: cognitive
            .internally_reassembled_formation_cues
            .clone(),
        externally_reassembled_formation_frontiers: cognitive
            .externally_reassembled_formation_frontiers
            .clone(),
        python_callback_count: 0,
        derived_budget,
        energy: cognitive.energy.clone(),
        rest_recovered_neuron_count: cognitive.rest_recovered_neuron_count,
        rest_drained_dissipation_quanta: cognitive.rest_drained_dissipation_quanta,
        unmet_dissipation_quanta: cognitive.unmet_dissipation_quanta,
        membrane_returned_elementary_charges: cognitive.membrane_returned_elementary_charges,
    }
}

/// One authored contact-growth observation. No joint field was reached and no
/// neuron transitioned; only the explicitly authored sparse anatomy changed.
fn make_authored_contact_observation(
    envelope: &[u8],
    predecessor: &RuntimeObservation,
    organism_tick: u64,
    fabric_generation: u64,
    fabric: &[u8],
    derived_budget: DerivedRuntimeBudget,
    cognitive: &CognitiveFormationObservation,
) -> RuntimeObservation {
    RuntimeObservation {
        schema: OBSERVATION_SCHEMA,
        scope: AUTHORED_CONTACT_GROWTH_SCOPE,
        identity: predecessor.identity,
        predecessor_state_receipt: Some(predecessor.state_receipt),
        predecessor_organism_tick: Some(predecessor.organism_tick),
        organism_tick,
        predecessor_fabric_generation: Some(predecessor.fabric_generation),
        fabric_generation,
        predecessor_mounted_generation: Some(predecessor.mounted_generation),
        mounted_generation: cognitive.cognitive_ordinal,
        state_bytes: envelope.len(),
        state_receipt: sha256(envelope),
        fabric_bytes: fabric.len(),
        fabric_receipt: sha256(fabric),
        joint_field_count: 0,
        joint_neuron_count: predecessor.joint_neuron_count,
        dsf_delivery_count: 0,
        complete_neuron_count: cognitive.complete_neuron_count,
        developmental_resting_neuron_count: cognitive.resting_neuron_count,
        physically_transitioned_neuron_count: 0,
        metabolically_perturbed_body_receptor_count: 0,
        externally_perturbed_body_receptor_count: 0,
        externally_perturbed_neuron_lineages: Vec::new(),
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
        recurrent_complete_neuron_fractal_count: 0,
        source_cohort_l0_l4_evaluation_count: 0,
        successor_l0_l4_replay_count: 0,
        joint_transition_receipt: None,
        episode_relation_candidate_receipt: None,
        source_authority: None,
        mounted_step_completed: false,
        physical_transition_claimed: false,
        cognitive_formation_claimed: false,
        cognitive_ordinal: cognitive.cognitive_ordinal,
        cognitive_trace_count: cognitive.trace_count,
        cognitive_mosaic_count: cognitive.mosaic_count,
        mosaic_of_mosaics_count: cognitive.mosaic_of_mosaics_count,
        formation_activation_count: 0,
        partial_cue_reassembly_count: 0,
        endogenous_partial_cue_reassembly_count: 0,
        internally_reassembled_formation_cues: Vec::new(),
        externally_reassembled_formation_frontiers: Vec::new(),
        python_callback_count: 0,
        derived_budget,
        energy: cognitive.energy.clone(),
        rest_recovered_neuron_count: 0,
        rest_drained_dissipation_quanta: 0,
        unmet_dissipation_quanta: 0,
        membrane_returned_elementary_charges: 0,
    }
}

fn canonical_identity(value: &str) -> Result<[u8; IDENTITY_BYTES], RuntimeError> {
    let bytes = value.as_bytes();
    if bytes.len() != IDENTITY_BYTES
        || bytes.iter().enumerate().any(|(index, value)| {
            if matches!(index, 8 | 13 | 18 | 23) {
                *value != b'-'
            } else {
                !matches!(*value, b'0'..=b'9' | b'a'..=b'f')
            }
        })
    {
        return Err(RuntimeError::InvalidIdentity);
    }
    let mut identity = [0_u8; IDENTITY_BYTES];
    identity.copy_from_slice(bytes);
    Ok(identity)
}

fn hex_digest(value: &[u8; 32]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(64);
    for byte in value {
        output.push(HEX[(byte >> 4) as usize] as char);
        output.push(HEX[(byte & 0x0f) as usize] as char);
    }
    output
}

fn project_internally_reassembled_formation_cues(
    observations: &[InternallyReassembledFormationCueObservation],
) -> Vec<InternallyReassembledFormationCueProjection> {
    observations
        .iter()
        .map(|observation| {
            (
                hex_digest(&observation.formation_receipt),
                observation
                    .cue_lineages
                    .iter()
                    .map(|lineage| hex_bytes(lineage))
                    .collect(),
            )
        })
        .collect()
}

fn project_externally_reassembled_formation_frontiers(
    observations: &[ExternallyReassembledFormationFrontierObservation],
) -> Vec<ExternallyReassembledFormationFrontierProjection> {
    observations
        .iter()
        .map(|observation| {
            (
                hex_digest(&observation.formation_receipt),
                observation
                    .cue_lineages
                    .iter()
                    .map(|lineage| hex_bytes(lineage))
                    .collect(),
                hex_bytes(&observation.recurrent_lineage),
            )
        })
        .collect()
}

fn project_organic_mosaic_relations(
    relations: &[OrganicMosaicRelationObservation],
) -> Vec<OrganicMosaicRelationProjection> {
    relations
        .iter()
        .map(|relation| {
            let receipts = relation.formation_receipts.iter().map(hex_digest).collect();
            let lineages = relation
                .shared_lineages
                .iter()
                .map(|value| hex_bytes(value))
                .collect();
            let bonds = relation
                .active_bonds
                .iter()
                .map(|bond| {
                    let (left, right) = bond.endpoints();
                    (hex_bytes(&left), hex_bytes(&right), bond.parallel_ordinal())
                })
                .collect();
            let ordered_paths = relation
                .ordered_physical_paths
                .iter()
                .map(|path| {
                    let [first, second] = path.directed_transfers();
                    let project = |(sender, receiver, bond, carriers): (
                        [u8; 16],
                        [u8; 16],
                        StablePhysicalBondReference,
                        u128,
                    )| {
                        (
                            hex_bytes(&sender),
                            hex_bytes(&receiver),
                            bond.parallel_ordinal(),
                            carriers.to_string(),
                        )
                    };
                    (project(first), project(second))
                })
                .collect();
            let ordered_path_relations = relation
                .ordered_path_relations
                .iter()
                .map(|path| {
                    let [earlier_first, earlier_second, current_first, current_second] =
                        path.directed_transfers();
                    let project = |(sender, receiver, bond, carriers): (
                        [u8; 16],
                        [u8; 16],
                        StablePhysicalBondReference,
                        u128,
                    )| {
                        (
                            hex_bytes(&sender),
                            hex_bytes(&receiver),
                            bond.parallel_ordinal(),
                            carriers.to_string(),
                        )
                    };
                    (
                        project(earlier_first),
                        project(earlier_second),
                        project(current_first),
                        project(current_second),
                    )
                })
                .collect();
            (
                receipts,
                lineages,
                bonds,
                hex_digest(&relation.structural_relation_receipt),
                ordered_paths,
                ordered_path_relations,
            )
        })
        .collect()
}

fn project_directed_physical_transfers(
    transfers: &[DirectedPhysicalTransferObservation],
) -> Vec<DirectedPhysicalTransferProjection> {
    transfers
        .iter()
        .map(|transfer| {
            (
                hex_bytes(&transfer.sender),
                hex_bytes(&transfer.receiver),
                transfer.bond.parallel_ordinal(),
                transfer.transferred_whole_carriers.to_string(),
            )
        })
        .collect()
}

fn project_changed_contact_channel_states(
    changes: &[ChangedContactChannelStateObservation],
) -> Vec<ChangedContactChannelStateProjection> {
    let rational = |value: ExactRational| {
        let (numerator, denominator) = value.parts();
        (numerator.to_string(), denominator.to_string())
    };
    changes
        .iter()
        .map(|change| {
            let (left, right) = change.bond.endpoints();
            (
                change.cognitive_ordinal,
                hex_bytes(&left),
                hex_bytes(&right),
                change.bond.parallel_ordinal(),
                (
                    change.predecessor_conducting_channel_population.to_string(),
                    rational(change.predecessor_transition_work_phase),
                    rational(change.predecessor_effective_conductance_picosiemens),
                ),
                (
                    change.successor_conducting_channel_population.to_string(),
                    rational(change.successor_transition_work_phase),
                    rational(change.successor_effective_conductance_picosiemens),
                ),
            )
        })
        .collect()
}

fn project_causal_frontier_transfers(
    transfers: &[CausalFrontierTransferObservation],
) -> Vec<CausalFrontierTransferProjection> {
    transfers
        .iter()
        .map(|observation| {
            let transfer = &observation.transfer;
            (
                hex_bytes(&transfer.sender),
                hex_bytes(&transfer.receiver),
                transfer.bond.parallel_ordinal(),
                transfer.transferred_whole_carriers.to_string(),
                hex_bytes(&observation.frontier_lineage),
            )
        })
        .collect()
}

fn project_motor_unit_recruitments(
    events: &[MotorUnitRecruitment],
) -> Vec<MotorUnitRecruitmentProjection> {
    events
        .iter()
        .map(|event| {
            (
                hex_bytes(&event.neuron_lineage),
                event.topology_index,
                event.outward_elementary_carriers,
                event
                    .preparation_transfers
                    .iter()
                    .map(|transfer| {
                        let (sender_layer, receiver_layer) =
                            if transfer.sender == event.neuron_lineage {
                                (12, 11)
                            } else {
                                (11, 12)
                            };
                        (
                            hex_bytes(&transfer.sender),
                            sender_layer,
                            hex_bytes(&transfer.receiver),
                            receiver_layer,
                            transfer.bond.parallel_ordinal(),
                            transfer.transferred_whole_carriers,
                        )
                    })
                    .collect(),
                event
                    .body_afferent_paths
                    .iter()
                    .map(|path| {
                        (
                            hex_bytes(&path.body_regulation_lineage),
                            hex_bytes(&path.integration_lineage),
                            hex_bytes(&path.receptor_lineage),
                            path.receptor_site.sense().declared_layer(),
                            path.receptor_site.topology_index(),
                            path.receptor_site.sensor_id().to_owned(),
                            path.receptor_site.substream_id().to_owned(),
                        )
                    })
                    .collect(),
            )
        })
        .collect()
}

fn project_affective_balance_trajectories(
    trajectories: &[AffectiveBalanceTrajectoryObservation],
) -> Vec<AffectiveBalanceTrajectoryProjection> {
    let transfer =
        |timed: crate::resident_cognitive_formation::TimedDirectedPhysicalTransferObservation| {
            (
                timed.cognitive_ordinal,
                (
                    hex_bytes(&timed.transfer.sender),
                    hex_bytes(&timed.transfer.receiver),
                    timed.transfer.bond.parallel_ordinal(),
                    timed.transfer.transferred_whole_carriers.to_string(),
                ),
            )
        };
    let rational = |value: crate::exact_rational::ExactRational| {
        let (numerator, denominator) = value.parts();
        (numerator.to_string(), denominator.to_string())
    };
    trajectories
        .iter()
        .map(|trajectory| {
            let place = trajectory.neuron_place;
            (
                hex_bytes(&trajectory.neuron_lineage),
                place.layer(),
                place.topology_index(),
                trajectory.association_influence.map(transfer),
                trajectory.body_influence.map(transfer),
                trajectory.localized_gradient_settlement.map(|gradient| {
                    (
                        gradient.cognitive_ordinal,
                        gradient.predecessor_separated_elementary_charges,
                        gradient.post_gradient_separated_elementary_charges,
                        gradient.interval_successor_separated_elementary_charges,
                        gradient.returned_elementary_charges,
                        gradient.pumped_elementary_charges,
                        gradient.unreturned_elementary_charges,
                        rational(gradient.membrane_gradient_work_zeptojoules),
                        rational(gradient.environment_energy_delivered_zeptojoules),
                        rational(gradient.environment_heat_exported_zeptojoules),
                    )
                }),
                trajectory
                    .localized_plasticity_settlement
                    .map(|plasticity| {
                        (
                            plasticity.cognitive_ordinal,
                            plasticity.incident_catalyst_quanta.to_string(),
                            plasticity.reaction_extent.to_string(),
                            rational(plasticity.delivered_energy_zeptojoules),
                            rational(plasticity.predecessor_gate_work_residue_zeptojoules),
                            rational(plasticity.successor_gate_work_residue_zeptojoules),
                            rational(plasticity.predecessor_plastic_rest_length_nanometres),
                            rational(plasticity.successor_plastic_rest_length_nanometres),
                            (
                                rational(plasticity.predecessor_reservoir.0),
                                rational(plasticity.predecessor_reservoir.1),
                                rational(plasticity.predecessor_reservoir.2),
                            ),
                            (
                                rational(plasticity.successor_reservoir.0),
                                rational(plasticity.successor_reservoir.1),
                                rational(plasticity.successor_reservoir.2),
                            ),
                        )
                    }),
            )
        })
        .collect()
}

fn project_localized_fluid_chemistry(
    settlements: &[LocalizedFluidChemistryObservation],
) -> Vec<LocalizedFluidChemistryProjection> {
    let rational = |value: crate::exact_rational::ExactRational| {
        let (numerator, denominator) = value.parts();
        (numerator.to_string(), denominator.to_string())
    };
    let reservoir = |parts: (
        crate::exact_rational::ExactRational,
        crate::exact_rational::ExactRational,
        crate::exact_rational::ExactRational,
    )| (rational(parts.0), rational(parts.1), rational(parts.2));
    settlements
        .iter()
        .map(|settlement| {
            let place = settlement.neuron_place;
            (
                hex_bytes(&settlement.neuron_lineage),
                place.layer(),
                place.topology_index(),
                settlement.cognitive_ordinal,
                (
                    settlement.interval_microseconds,
                    rational(settlement.pump_contact_power_zeptojoules_per_microsecond),
                    settlement.reached_neuron_count,
                    settlement.changed_reached_neuron_count,
                    settlement.unchanged_unreached_neuron_count,
                    settlement.unchanged_developmental_resting_neuron_count,
                    settlement.changed_unreached_neuron_count,
                ),
                (
                    settlement.predecessor_separated_elementary_charges,
                    settlement.successor_separated_elementary_charges,
                    settlement.predecessor_intracellular_carriers.to_string(),
                    settlement.predecessor_extracellular_carriers.to_string(),
                    settlement.successor_intracellular_carriers.to_string(),
                    settlement.successor_extracellular_carriers.to_string(),
                    settlement.returned_elementary_charges,
                    settlement.pumped_elementary_charges,
                ),
                (
                    reservoir(settlement.predecessor_reservoir),
                    reservoir(settlement.successor_reservoir),
                    rational(settlement.membrane_gradient_work_zeptojoules),
                ),
            )
        })
        .collect()
}

fn project_localized_metabolic_strain(
    observations: &[LocalizedMetabolicStrainObservation],
) -> Vec<LocalizedMetabolicStrainProjection> {
    observations
        .iter()
        .map(|observation| {
            let place = observation.neuron_place;
            (
                hex_bytes(&observation.neuron_lineage),
                place.layer(),
                place.topology_index(),
                observation.cognitive_ordinal,
                observation
                    .psi_dissipation_quanta
                    .iter()
                    .map(u128::to_string)
                    .collect(),
                observation.gate_dissipation_quanta.to_string(),
                observation.plastic_dissipation_quanta.to_string(),
            )
        })
        .collect()
}

fn project_ordered_physical_paths(
    paths: &[OrderedPhysicalPathObservation],
) -> Vec<OrderedPhysicalPathProjection> {
    paths
        .iter()
        .map(|path| {
            let [first, second] = path.directed_transfers();
            let project = |(sender, receiver, bond, carriers): (
                [u8; 16],
                [u8; 16],
                StablePhysicalBondReference,
                u128,
            )| {
                (
                    hex_bytes(&sender),
                    hex_bytes(&receiver),
                    bond.parallel_ordinal(),
                    carriers.to_string(),
                )
            };
            (project(first), project(second))
        })
        .collect()
}

fn project_physical_frontier_routes(
    routes: &[PhysicalFrontierRouteObservation],
) -> Vec<PhysicalFrontierRouteProjection> {
    routes
        .iter()
        .map(|route| {
            let seed_place = route.seed_place();
            let adjacent_place = route.adjacent_place();
            (
                hex_bytes(&route.seed_lineage()),
                seed_place.layer(),
                seed_place.topology_index(),
                hex_bytes(&route.adjacent_lineage()),
                adjacent_place.layer(),
                adjacent_place.topology_index(),
                route.bond().parallel_ordinal(),
                route.outward_whole_carriers_from_seed(),
            )
        })
        .collect()
}

fn hex_bytes(value: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(value.len() * 2);
    for byte in value {
        output.push(HEX[(byte >> 4) as usize] as char);
        output.push(HEX[(byte & 0x0f) as usize] as char);
    }
    output
}

fn parse_lineage_hex(value: &str) -> PyResult<[u8; 16]> {
    let bytes = value.as_bytes();
    if bytes.len() != 32 {
        return Err(PyValueError::new_err("neuron lineage is not canonical hex"));
    }
    let nibble = |byte: u8| match byte {
        b'0'..=b'9' => Some(byte - b'0'),
        b'a'..=b'f' => Some(byte - b'a' + 10),
        _ => None,
    };
    let mut lineage = [0_u8; 16];
    for (index, output) in lineage.iter_mut().enumerate() {
        let high = nibble(bytes[index * 2])
            .ok_or_else(|| PyValueError::new_err("neuron lineage is not canonical hex"))?;
        let low = nibble(bytes[index * 2 + 1])
            .ok_or_else(|| PyValueError::new_err("neuron lineage is not canonical hex"))?;
        *output = (high << 4) | low;
    }
    Ok(lineage)
}

fn take_u16(bytes: &[u8], offset: &mut usize) -> Result<u16, RuntimeError> {
    let end = offset
        .checked_add(std::mem::size_of::<u16>())
        .ok_or(RuntimeError::EnvelopeEndedEarly)?;
    let value = bytes
        .get(*offset..end)
        .ok_or(RuntimeError::EnvelopeEndedEarly)?;
    *offset = end;
    Ok(u16::from_le_bytes(value.try_into().expect("fixed u16")))
}

fn take_u32(bytes: &[u8], offset: &mut usize) -> Result<u32, RuntimeError> {
    let end = offset
        .checked_add(std::mem::size_of::<u32>())
        .ok_or(RuntimeError::EnvelopeEndedEarly)?;
    let value = bytes
        .get(*offset..end)
        .ok_or(RuntimeError::EnvelopeEndedEarly)?;
    *offset = end;
    Ok(u32::from_le_bytes(value.try_into().expect("fixed u32")))
}

fn take_u64(bytes: &[u8], offset: &mut usize) -> Result<u64, RuntimeError> {
    let end = offset
        .checked_add(std::mem::size_of::<u64>())
        .ok_or(RuntimeError::EnvelopeEndedEarly)?;
    let value = bytes
        .get(*offset..end)
        .ok_or(RuntimeError::EnvelopeEndedEarly)?;
    *offset = end;
    Ok(u64::from_le_bytes(value.try_into().expect("fixed u64")))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::path::PathBuf;

    #[test]
    fn motor_body_transition_uses_retained_effector_mount_not_afferent_ancestry() {
        use crate::articulated_body_joint_source_builder::admit_articulated_body_proprioceptive_source;
        use crate::neuron_source_anchor::{NeuronSourceSite, PhysicalSourceSense};
        use crate::resident_cognitive_formation::MotorBodyAfferentPath;
        use crate::virtual_articulated_body::{BodyAxis, BodyEffectorDirection};

        let terminal = BodyEffectorTerminal::new(
            BodyAxis::LeftElbowFlexion,
            BodyEffectorDirection::TowardMaximum,
        );
        let seed = settle_body_effector_drives(
            &ArticulatedBodyState::at_neutral(),
            &AdmittedBodyEffectorDrives::admit(vec![BodyEffectorDrive {
                terminal,
                outward_elementary_carriers: 1,
            }])
            .unwrap(),
        )
        .unwrap();
        let source =
            admit_articulated_body_proprioceptive_source(0, &seed.proprioceptive_consequences)
                .unwrap();
        let typed_site =
            NeuronSourceSite::from_source_port(&source.joint_source_ports()[1]).unwrap();
        assert_eq!(
            typed_site
                .body_proprioceptor_terminal()
                .map(|afferent| afferent.paired_effector()),
            Some(terminal)
        );
        let path = |site| MotorBodyAfferentPath {
            body_regulation_lineage: [2; 16],
            integration_lineage: [3; 16],
            receptor_lineage: [4; 16],
            receptor_site: site,
        };
        let recruitment = |paths| MotorUnitRecruitment {
            neuron_lineage: [1; 16],
            topology_index: 99,
            outward_elementary_carriers: 12,
            body_effector_terminal: terminal,
            body_afferent_paths: paths,
            preparation_transfers: Vec::new(),
        };

        let predecessor = ArticulatedBodyState::at_neutral();
        let settled = settle_motor_recruitments_into_articulated_body(
            &predecessor,
            &[recruitment(vec![path(typed_site.clone())])],
        )
        .unwrap();
        assert_eq!(settled.successor.axis(BodyAxis::LeftElbowFlexion), 12);
        assert_eq!(settled.proprioceptive_consequences.len(), 1);

        let untyped = NeuronSourceSite::fixture_in_sense(PhysicalSourceSense::Body, 99);
        let settled_from_untyped_afferent = settle_motor_recruitments_into_articulated_body(
            &predecessor,
            &[recruitment(vec![path(untyped)])],
        )
        .unwrap();
        assert_eq!(settled_from_untyped_afferent.successor, settled.successor);

        let other_site =
            NeuronSourceSite::from_source_port(&source.joint_source_ports()[0]).unwrap();
        let settled_from_opposed_afferents = settle_motor_recruitments_into_articulated_body(
            &predecessor,
            &[recruitment(vec![path(typed_site), path(other_site)])],
        )
        .unwrap();
        assert_eq!(settled_from_opposed_afferents.successor, settled.successor);
    }

    #[test]
    fn complete_body_observation_enters_the_ordinary_cognitive_boundary_once() {
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let before = runtime.active.articulated_body.clone();
        let prepared = runtime.prepare_articulated_body_observation().unwrap();
        assert_eq!(
            prepared.receptor_ingress.sense_counts(),
            [0, 0, 0, 0, 0, 74]
        );
        assert_eq!(prepared.observation.organism_tick, 1);
        assert_eq!(prepared.articulated_body_consequences.len(), 0);
        assert!(prepared.body_proprioceptive_sources.is_empty());
        assert_eq!(runtime.active.articulated_body, before);
        runtime.commit(prepared.token).unwrap();
        assert_eq!(runtime.active.articulated_body.axes(), before.axes());
        assert!(!before.proprioception_initialized());
        assert!(runtime.active.articulated_body.proprioception_initialized());
        assert_eq!(runtime.observation().organism_tick, 1);
    }

    #[test]
    fn every_unsealed_intake_observes_the_current_complete_body_once() {
        let episode = source("first-trajectory-with-body");
        let interval_count = episode.joint_source_occurrences().len();
        let episodes = vec![(episode, vec![(5, 1); interval_count])];
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();

        let first_phase = runtime
            .begin_unsealed_intake_direct(None, &episodes)
            .unwrap();
        let first = runtime
            .finalize_unsealed_intake_direct(first_phase.token)
            .unwrap();
        assert_eq!(first.observation.organism_tick, 2);
        assert_eq!(first.causal_interval_evidence.len(), 2);
        assert_eq!(first.receptor_ingress.sense_counts()[5], 74);
        assert!(runtime.active.articulated_body.proprioception_initialized());
        runtime.acknowledge_direct_commit(first.token).unwrap();
        assert!(runtime.active.articulated_body.proprioception_initialized());

        let second_phase = runtime
            .begin_unsealed_intake_direct(None, &episodes)
            .unwrap();
        let second = runtime
            .finalize_unsealed_intake_direct(second_phase.token)
            .unwrap();
        assert_eq!(second.observation.organism_tick, 4);
        assert_eq!(second.causal_interval_evidence.len(), 2);
        assert_eq!(second.receptor_ingress.sense_counts()[5], 74);
    }

    #[test]
    fn authenticated_production_envelope_migrates_exact_energy_once() {
        let Some(path) = std::env::var_os("GUALA_REAL_BODY") else {
            return;
        };
        let budget = RuntimeBudget::new(67_108_864, 67_108_000, 536_870_912).unwrap();
        let predecessor = fs::read(PathBuf::from(path)).expect("production envelope is readable");
        let before = parse_current_envelope(&predecessor, budget).unwrap();
        let identity = before.identity;
        let organism_tick = before.organism_tick;
        let fabric_generation = before.fabric_generation;
        let joint = before.joint_bytes.to_vec();

        // A pre-V18 body can remain structurally decodable while still
        // lacking the membrane-territory carrier material. Decodability is
        // therefore not migration authority; the explicit one-way boundary
        // below must execute and prove its current-format successor.
        let migrated =
            migrate_resident_organism_exact_energy_envelope(predecessor, budget).unwrap();
        let after = parse_current_envelope(&migrated, budget).unwrap();
        assert_eq!(after.identity, identity);
        assert_eq!(after.organism_tick, organism_tick);
        assert_eq!(after.fabric_generation, fabric_generation);
        assert_eq!(after.joint_bytes, joint);
        let mut runtime =
            ResidentOrganismRuntime::restore_envelope(migrated.clone(), budget).unwrap();
        runtime.prepare_articulated_body_observation().unwrap();
        assert_eq!(
            migrate_resident_organism_exact_energy_envelope(migrated.clone(), budget).unwrap(),
            migrated,
        );
    }

    /// Quiet (dark, silent) episodes appended after a presentation so the
    /// cohort can descend all the way to electrical rest.  Since the
    /// 2026-08-05 geometric differentiation the members' capacitances differ,
    /// so a settled cohort equalizes POTENTIAL rather than charge and needs a
    /// longer quiet tail to go silent than the tie-frozen anatomy did; the
    /// tail is transport, the quiescence is physics.
    const DARK_TAIL_EPISODES: usize = 64;
    use crate::joint_source_episode::decode_native_joint_source_episode;
    use crate::neuron_source_anchor::tests::{exact_dark_optical_episode, exact_optical_episode};

    const IDENTITY: &str = "12345678-9abc-4def-8123-456789abcdef";

    fn budget() -> RuntimeBudget {
        // The complete articulated body occupies layer-6 topology 629..702,
        // immediately after the unchanged served sensory geography. An empty
        // genesis therefore uses the production envelope so its compact
        // resting declaration reaches every standard body place without
        // consuming the one unit reserved for genuinely later growth. The
        // declaration itself remains compact and carries no cell history.
        RuntimeBudget::new(67_108_864, 67_108_000, 536_870_912).unwrap()
    }

    fn text(output: &mut Vec<u8>, value: &str) {
        output.extend_from_slice(&u16::try_from(value.len()).unwrap().to_le_bytes());
        output.extend_from_slice(value.as_bytes());
    }

    fn rational(output: &mut Vec<u8>, numerator: i64, denominator: i64) {
        text(output, &numerator.to_string());
        text(output, &denominator.to_string());
    }

    fn source_port(output: &mut Vec<u8>, topology: u32, values: [(i64, f64); 2]) {
        output.push(0);
        output.extend_from_slice(&topology.to_le_bytes());
        text(output, &format!("retina-{topology}"));
        text(output, "luminance");
        output.extend_from_slice(&1_u16.to_le_bytes());
        text(output, "receptor");
        text(output, &topology.to_string());
        text(output, "light");
        text(output, "normalized");
        text(output, "direct");
        text(output, "");
        text(output, "affine");
        rational(output, -1, 1);
        rational(output, 1, 1);
        rational(output, 1, 1);
        rational(output, 1, 1);
        output.extend_from_slice(&1_u32.to_le_bytes());
        output.push(topology as u8);
        output.extend_from_slice(&2_u32.to_le_bytes());
        for (time, signal) in values {
            rational(output, time, 1);
            output.extend_from_slice(&signal.to_bits().to_le_bytes());
            rational(output, 0, 1);
            rational(output, 1, 1);
            rational(output, (1.0 + signal) as i64, 1);
        }
    }

    fn source(episode: &str) -> NativeJointSourceEpisode {
        let mut body = b"GLJSRC02".to_vec();
        body.extend_from_slice(&2_u16.to_le_bytes());
        text(&mut body, episode);
        body.extend_from_slice(&[0, 1, 1, 1, 1, 1]);
        body.extend_from_slice(&2_u32.to_le_bytes());
        source_port(&mut body, 0, [(1, 0.0), (2, 1.0)]);
        source_port(&mut body, 1, [(1, 1.0), (2, 0.0)]);
        body.extend_from_slice(&2_u32.to_le_bytes());
        source_occurrence(&mut body, 0, [1, 2]);
        source_occurrence(&mut body, 1, [1, 2]);
        decode_native_joint_source_episode(&body, 2, 4, 2, 4).unwrap()
    }

    fn source_with_port_count(episode: &str, port_count: u32) -> NativeJointSourceEpisode {
        let mut body = b"GLJSRC02".to_vec();
        body.extend_from_slice(&2_u16.to_le_bytes());
        text(&mut body, episode);
        body.extend_from_slice(&[0, 1, 1, 1, 1, 1]);
        body.extend_from_slice(&port_count.to_le_bytes());
        for topology in 0..port_count {
            let values = if topology % 2 == 0 {
                [(1, 0.0), (2, 1.0)]
            } else {
                [(1, 1.0), (2, 0.0)]
            };
            source_port(&mut body, topology, values);
        }
        body.extend_from_slice(&port_count.to_le_bytes());
        for port_index in 0..port_count {
            source_occurrence(&mut body, port_index, [1, 2]);
        }
        decode_native_joint_source_episode(
            &body,
            port_count as usize,
            port_count as usize * 2,
            port_count as usize,
            port_count as usize * 2,
        )
        .unwrap()
    }

    fn source_occurrence(output: &mut Vec<u8>, port_index: u32, times: [i64; 2]) {
        output.extend_from_slice(&1_u32.to_le_bytes());
        output.extend_from_slice(&port_index.to_le_bytes());
        output.extend_from_slice(&2_u32.to_le_bytes());
        for time in times {
            rational(output, time, 1);
        }
        let profile =
            crate::joint_uf_source_adapter::SAMPLED_VOLUME_AND_RELEVANCE_PIECEWISE_LINEAR_PROFILE;
        output.extend_from_slice(&u32::try_from(profile.len()).unwrap().to_le_bytes());
        output.extend_from_slice(profile);
        output.extend_from_slice(&1_u32.to_le_bytes());
        output.extend_from_slice(&1_u32.to_le_bytes());
        output.extend_from_slice(&0_u32.to_le_bytes());
        output.extend_from_slice(&1_u32.to_le_bytes());
        output.push(1);
        output.extend_from_slice(&2_u32.to_le_bytes());
        rational(output, 1, 1);
        rational(output, 1, 1);
    }

    fn genesis_joint() -> Vec<u8> {
        let mut bytes = Vec::new();
        bytes.extend_from_slice(b"GLJDSF03");
        bytes.extend_from_slice(&3_u16.to_le_bytes());
        bytes.extend_from_slice(&0_u64.to_le_bytes());
        bytes.extend_from_slice(&1_u64.to_le_bytes());
        bytes.extend_from_slice(&[0; 32]);
        bytes.push(0);
        bytes.extend_from_slice(&0_u32.to_le_bytes());
        bytes.extend_from_slice(&0_u32.to_le_bytes());
        bytes.push(0);
        bytes
    }

    fn genesis_cognitive() -> Vec<u8> {
        ResidentCognitiveFormationState::default()
            .encode(1_000_000)
            .unwrap()
    }

    fn genesis_vestibular() -> ResidentVestibularBody {
        ResidentVestibularBody::phase_one_genesis().unwrap()
    }

    fn pre_articulated_fabric(
        generation: u64,
        joint: &[u8],
        cognitive: &[u8],
        vestibular: &ResidentVestibularBody,
    ) -> Vec<u8> {
        let mut output = Vec::new();
        output.extend_from_slice(PRE_ARTICULATED_FABRIC_MAGIC);
        output.extend_from_slice(&PRE_ARTICULATED_FABRIC_VERSION.to_le_bytes());
        output.extend_from_slice(&generation.to_le_bytes());
        output.extend_from_slice(&u32::try_from(joint.len()).unwrap().to_le_bytes());
        output.extend_from_slice(&u32::try_from(cognitive.len()).unwrap().to_le_bytes());
        output.extend_from_slice(&encode_functional_vestibular_anatomy(&vestibular.anatomy));
        output.extend_from_slice(&encode_canal_state(vestibular.canal));
        output.extend_from_slice(&vestibular.source_tick.to_le_bytes());
        output.extend_from_slice(joint);
        output.extend_from_slice(cognitive);
        output
    }

    #[test]
    fn pre_articulated_live_format_migrates_once_without_changing_existing_state() {
        let joint = genesis_joint();
        let cognitive = ResidentCognitiveFormationState::migrate_to_current_format(
            &genesis_cognitive(),
            cognitive_budget_after_joint(joint.len(), budget()).unwrap(),
        )
        .unwrap();
        let vestibular = genesis_vestibular();
        let old_fabric = pre_articulated_fabric(17, &joint, &cognitive, &vestibular);
        let old_envelope = encode_envelope(
            canonical_identity(IDENTITY).unwrap(),
            91,
            &old_fabric,
            budget(),
        )
        .unwrap();
        let old_parsed = parse_current_envelope(&old_envelope, budget()).unwrap();
        assert_eq!(old_parsed.joint_bytes, joint);
        assert_eq!(old_parsed.cognitive_bytes, Some(cognitive.as_slice()));
        assert_eq!(old_parsed.vestibular, Some(vestibular.clone()));
        assert_eq!(old_parsed.articulated_body, None);
        assert_eq!(
            ResidentOrganismRuntime::restore_envelope(old_envelope.clone(), budget()).unwrap_err(),
            RuntimeError::UnsupportedFabricVersion(PRE_ARTICULATED_FABRIC_VERSION),
        );

        let migrated = migrate_resident_organism_exact_energy_envelope(old_envelope, budget())
            .expect("one deployment migration adds the body");
        let parsed = parse_current_envelope(&migrated, budget()).unwrap();
        assert_eq!(parsed.identity, canonical_identity(IDENTITY).unwrap());
        assert_eq!(parsed.organism_tick, 91);
        assert_eq!(parsed.fabric_generation, 17);
        assert_eq!(parsed.joint_bytes, joint);
        assert_eq!(parsed.cognitive_bytes, Some(cognitive.as_slice()));
        assert_eq!(parsed.vestibular, Some(vestibular));
        assert_eq!(
            parsed.articulated_body,
            Some(ArticulatedBodyState::at_neutral())
        );
        assert_eq!(
            migrated.len(),
            old_fabric.len() + FIXED_BYTES + ARTICULATED_BODY_STATE_BYTES
        );
        assert_eq!(
            migrate_resident_organism_exact_energy_envelope(migrated.clone(), budget()).unwrap(),
            migrated,
        );
    }

    #[test]
    fn articulated_body_observation_is_exact_read_only_and_cold_persistent() {
        let runtime = resident(91, 17);
        let before_envelope = runtime.active_envelope().to_vec();
        let observed = native_resident_observation(&runtime);
        assert_eq!(observed.articulated_body_axes().len(), BODY_AXES.len());
        assert_eq!(
            observed.articulated_body_state_bytes(),
            ARTICULATED_BODY_STATE_BYTES,
        );
        assert_eq!(
            observed.articulated_body_lung_air_microlitres(),
            crate::virtual_articulated_body::NEUTRAL_LUNG_AIR_MICROLITRES,
        );
        assert_eq!(runtime.active_envelope(), before_envelope);

        let restored =
            ResidentOrganismRuntime::restore_envelope(before_envelope, budget()).unwrap();
        let after = native_resident_observation(&restored);
        assert_eq!(
            after.articulated_body_axes(),
            observed.articulated_body_axes()
        );
        assert_eq!(
            after.articulated_body_state_sha256(),
            observed.articulated_body_state_sha256(),
        );
        assert_eq!(
            restored.active.articulated_body,
            runtime.active.articulated_body
        );
    }

    fn legacy_joint() -> Vec<u8> {
        let mut bytes = Vec::new();
        bytes.extend_from_slice(b"GLJNFT02");
        bytes.extend_from_slice(&2_u16.to_le_bytes());
        bytes.extend_from_slice(&13_u64.to_le_bytes());
        bytes.extend_from_slice(&1_u64.to_le_bytes());
        bytes.extend_from_slice(&[0; 32]);
        bytes.push(0);
        bytes.extend_from_slice(&0_u32.to_le_bytes());
        bytes.extend_from_slice(&0_u32.to_le_bytes());
        bytes.push(0);
        bytes
    }

    fn legacy_fabric() -> Vec<u8> {
        let joint = legacy_joint();
        let mut bytes = Vec::new();
        bytes.extend_from_slice(b"GLMFAB03");
        bytes.extend_from_slice(&3_u16.to_le_bytes());
        bytes.extend_from_slice(&17_u64.to_le_bytes());
        bytes.extend_from_slice(&0_u32.to_le_bytes());
        bytes.extend_from_slice(&0_u32.to_le_bytes());
        bytes.extend_from_slice(&u32::try_from(joint.len()).unwrap().to_le_bytes());
        bytes.extend_from_slice(&joint);
        bytes
    }

    fn test_migration_authority(fabric: &[u8]) -> LegacyMigrationAuthority {
        LegacyMigrationAuthority {
            identity: IDENTITY,
            organism_tick: 91,
            fabric_receipt: sha256(fabric),
            fabric_generation: 17,
            mounted_generation: 13,
        }
    }

    fn restored(tick: u64, fabric_generation: u64) -> OrganismRuntime {
        let fabric = encode_fabric(
            fabric_generation,
            &genesis_joint(),
            &genesis_cognitive(),
            &genesis_vestibular(),
            &ArticulatedBodyState::at_neutral(),
            budget(),
        )
        .unwrap();
        OrganismRuntime::restore_current(IDENTITY, tick, fabric, budget()).unwrap()
    }

    fn resident(tick: u64, fabric_generation: u64) -> ResidentOrganismRuntime {
        let envelope = restored(tick, fabric_generation)
            .seal(budget().max_envelope_bytes)
            .unwrap()
            .bytes;
        ResidentOrganismRuntime::restore_envelope(envelope, budget()).unwrap()
    }

    #[test]
    fn body_balance_tick_claims_receptor_and_integration_cells_and_cold_restores() {
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let before = runtime.observation();
        let prepared = runtime.prepare_vestibular_tick(0, 64).unwrap();
        assert_eq!(
            prepared.observation.complete_neuron_count,
            before.complete_neuron_count + 3
        );
        // The receptor, its collision-free layer-6 partner, and its
        // topology-local layer-8 regulator each claim one declared resting
        // cell. No external growth unit is consumed.
        assert_eq!(
            prepared.observation.developmental_resting_neuron_count + 3,
            before.developmental_resting_neuron_count
        );
        assert_eq!(prepared.observation.dsf_delivery_count, 2);
        assert_eq!(prepared.observation.python_callback_count, 0);
        runtime.commit(prepared.token).unwrap();
        assert_eq!(runtime.active.vestibular.source_tick, 1);
        assert_ne!(runtime.active.vestibular.canal, CanalState::at_rest());
        let body = runtime.active_envelope().to_vec();
        let restored = ResidentOrganismRuntime::restore_envelope(body.clone(), budget()).unwrap();
        assert_eq!(restored.active_envelope(), body);
        assert_eq!(restored.active.vestibular, runtime.active.vestibular);
        assert_eq!(
            restored.observation().complete_neuron_count
                + restored.observation().developmental_resting_neuron_count,
            before.complete_neuron_count + before.developmental_resting_neuron_count
        );
    }

    #[test]
    fn exact_quarter_turn_reuses_the_specialized_pair_across_every_millisecond() {
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let before = runtime.observation();
        let before_total = before.complete_neuron_count + before.developmental_resting_neuron_count;
        let turn = settle_signed_yaw_actuation(
            YawBodyState::new(0).unwrap(),
            SignedYawActuation::new(90_000, 250_000).unwrap(),
        )
        .unwrap();
        let mut heading = 0_u32;
        for signed_step in turn.trajectory.as_slice() {
            let prepared = runtime
                .prepare_vestibular_tick(heading, *signed_step)
                .unwrap();
            heading =
                u32::try_from((i64::from(heading) + i64::from(*signed_step)).rem_euclid(360_000))
                    .unwrap();
            runtime.commit(prepared.token).unwrap();
        }
        let after = runtime.observation();
        assert_eq!(heading, 90_000);
        assert_eq!(after.organism_tick - before.organism_tick, 250);
        assert_eq!(
            after.complete_neuron_count,
            before.complete_neuron_count + 3
        );
        assert_eq!(
            after.developmental_resting_neuron_count + 3,
            before.developmental_resting_neuron_count
        );
        assert_eq!(
            after.complete_neuron_count + after.developmental_resting_neuron_count,
            before_total
        );
        assert_eq!(
            runtime
                .cognitive_state()
                .observe_reached_source_site_count("mounted-yaw-canal", "local-hair-bundle-0",),
            1
        );
        let body = runtime.active_envelope().to_vec();
        let restored = ResidentOrganismRuntime::restore_envelope(body.clone(), budget()).unwrap();
        assert_eq!(restored.active_envelope(), body);
        assert_eq!(restored.active.vestibular, runtime.active.vestibular);
        assert_eq!(
            restored
                .cognitive_state()
                .observe_reached_source_site_count("mounted-yaw-canal", "local-hair-bundle-0",),
            1
        );
    }

    #[test]
    fn one_seal_trajectory_is_byte_exact_with_per_interval_sealing() {
        let turn = settle_signed_yaw_actuation(
            YawBodyState::new(0).unwrap(),
            SignedYawActuation::new(90_000, 250_000).unwrap(),
        )
        .unwrap();
        let steps = turn.trajectory.as_slice();

        let mut reference = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let mut heading = 0_u32;
        for signed_step in steps {
            let prepared = reference
                .prepare_vestibular_tick(heading, *signed_step)
                .unwrap();
            reference.commit(prepared.token).unwrap();
            heading = (i64::from(heading) + i64::from(*signed_step)).rem_euclid(360_000) as u32;
        }

        let mut candidate = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let prepared = candidate.prepare_vestibular_trajectory(0, steps).unwrap();
        assert_eq!(prepared.phase_counts.successor_seal_count, 1);
        assert_eq!(prepared.phase_counts.current_cohort_evaluation_count, 250);
        assert_eq!(prepared.observation.dsf_delivery_count, 500);
        assert_eq!(prepared.observation.localized_fluid_chemistry.len(), 1);
        assert_eq!(
            prepared.observation.localized_fluid_chemistry[0].changed_unreached_neuron_count,
            0
        );
        assert!(
            prepared.observation.localized_fluid_chemistry[0].unchanged_unreached_neuron_count
                + prepared.observation.localized_fluid_chemistry[0]
                    .unchanged_developmental_resting_neuron_count
                > 0
        );
        let replay = create_resident_genesis(IDENTITY, 0, budget())
            .unwrap()
            .prepare_vestibular_trajectory(0, steps)
            .unwrap();
        assert_eq!(
            replay.observation.localized_fluid_chemistry,
            prepared.observation.localized_fluid_chemistry
        );
        candidate.commit(prepared.token).unwrap();

        assert_eq!(heading, 90_000);
        assert_eq!(candidate.active_envelope(), reference.active_envelope());
        assert_eq!(candidate.active.cognitive, reference.active.cognitive);
        assert_eq!(candidate.active.vestibular, reference.active.vestibular);
    }

    #[test]
    fn unsealed_admitted_trajectory_is_byte_exact_and_seals_once() {
        let sources = vec![
            source("admitted-trajectory-1"),
            source("admitted-trajectory-2"),
        ];

        let mut reference = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        reference
            .active
            .articulated_body
            .initialize_proprioception();
        let body = reference.prepare_articulated_body_observation().unwrap();
        reference.commit(body.token).unwrap();
        for source in &sources {
            let prepared = reference.prepare_with_store(source).unwrap();
            reference.commit(prepared.token).unwrap();
        }

        let mut candidate = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        candidate
            .active
            .articulated_body
            .initialize_proprioception();
        let episodes = sources
            .iter()
            .cloned()
            .map(|source| {
                let interval_count = source.joint_source_occurrences().len();
                (source, vec![(5, 1); interval_count])
            })
            .collect::<Vec<_>>();
        let phase = candidate
            .begin_unsealed_intake_direct(None, &episodes)
            .unwrap();
        let prepared = candidate
            .finalize_unsealed_intake_direct(phase.token)
            .unwrap();
        assert_eq!(prepared.phase_counts.successor_seal_count, 1);
        assert_eq!(prepared.phase_counts.current_cohort_evaluation_count, 41);
        assert_eq!(prepared.receptor_ingress.field_count(), 41);
        assert_eq!(prepared.receptor_ingress.witness_count(), 78);
        assert_eq!(prepared.observation.organism_tick, 3);
        assert_eq!(prepared.causal_interval_evidence.len(), 3);
        candidate.acknowledge_direct_commit(prepared.token).unwrap();

        assert_eq!(candidate.active_envelope(), reference.active_envelope());
        assert_eq!(candidate.active.cognitive, reference.active.cognitive);
        assert_eq!(candidate.active.vestibular, reference.active.vestibular);

        let body = reference.prepare_articulated_body_observation().unwrap();
        reference.commit(body.token).unwrap();
        for source in &sources {
            let prepared = reference.prepare_with_store(source).unwrap();
            reference.commit(prepared.token).unwrap();
        }
        let phase = candidate
            .begin_unsealed_intake_direct(None, &episodes)
            .unwrap();
        let prepared = candidate
            .finalize_unsealed_intake_direct(phase.token)
            .unwrap();
        let emitted_lineages = prepared
            .observation
            .emitted_neuron_fractals
            .iter()
            .map(|fractal| fractal.neuron_lineage)
            .collect::<std::collections::BTreeSet<_>>();
        assert_eq!(
            emitted_lineages.len(),
            prepared.observation.emitted_neuron_fractals.len()
        );
        candidate.acknowledge_direct_commit(prepared.token).unwrap();
        assert_eq!(candidate.active_envelope(), reference.active_envelope());
    }

    #[test]
    fn unsealed_intake_combines_vestibular_admitted_and_appended_sources_in_one_seal() {
        let initial_source = source("unsealed-initial");
        let appended_source = source("unsealed-self-hearing");
        let initial_intervals = vec![(5, 1); initial_source.joint_source_occurrences().len()];
        let appended_intervals = vec![(5, 1); appended_source.joint_source_occurrences().len()];
        let initial = vec![(initial_source, initial_intervals)];
        let appended = vec![(appended_source, appended_intervals)];
        let signed_steps = [1_i32];
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        runtime.active.articulated_body.initialize_proprioception();
        let predecessor = runtime.observation();

        let phase = runtime
            .begin_unsealed_intake_direct(Some((0, &signed_steps)), &initial)
            .unwrap();

        assert_eq!(runtime.observation(), predecessor);
        assert!(runtime.active_envelope().is_empty());
        assert!(runtime.unsealed_intake.is_some());
        let appended_phase = runtime
            .append_unsealed_intake_direct(phase.token, &appended)
            .unwrap();
        let prepared = runtime
            .finalize_unsealed_intake_direct(appended_phase.token)
            .unwrap();

        assert_eq!(prepared.phase_counts.successor_seal_count, 1);
        assert_eq!(prepared.causal_interval_evidence.len(), 4);
        assert_eq!(
            prepared.observation.organism_tick,
            predecessor.organism_tick + 4
        );
        assert_eq!(runtime.active.vestibular.source_tick, 1);
        assert!(runtime.unsealed_intake.is_none());
        assert!(runtime.direct_predecessor.is_some());
        runtime.acknowledge_direct_commit(prepared.token).unwrap();
    }

    #[test]
    fn aborting_unsealed_intake_restores_the_exact_predecessor() {
        let source = source("unsealed-abort");
        let intervals = vec![(5, 1); source.joint_source_occurrences().len()];
        let episodes = vec![(source, intervals)];
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        runtime.active.articulated_body.initialize_proprioception();
        let predecessor_envelope = runtime.active_envelope().to_vec();
        let predecessor_observation = runtime.observation();
        let predecessor_ordinal = runtime.next_prepare_ordinal;

        let phase = runtime
            .begin_unsealed_intake_direct(None, &episodes)
            .unwrap();
        runtime.abort_unsealed_intake(phase.token).unwrap();

        assert_eq!(runtime.active_envelope(), predecessor_envelope);
        assert_eq!(runtime.observation(), predecessor_observation);
        assert_eq!(runtime.next_prepare_ordinal, predecessor_ordinal);
        assert!(runtime.unsealed_intake.is_none());
        assert!(runtime.direct_predecessor.is_none());
    }

    #[test]
    fn one_episode_advances_only_the_truthful_mounted_step() {
        let episode = source("first-mounted-step");
        let predecessor = restored(91, 17);
        let predecessor_receipt = predecessor.observe().state_receipt;
        let result = predecessor.advance_mounted(&episode, budget()).unwrap();
        let observed = result.observation;
        assert_eq!(observed.schema, OBSERVATION_SCHEMA);
        assert_eq!(observed.scope, MOUNTED_STEP_SCOPE);
        assert_eq!(&observed.identity, IDENTITY.as_bytes());
        assert_eq!(
            (observed.predecessor_organism_tick, observed.organism_tick),
            (Some(91), 92)
        );
        assert_eq!(
            (
                observed.predecessor_fabric_generation,
                observed.fabric_generation
            ),
            (Some(17), 18)
        );
        assert_eq!(
            (
                observed.predecessor_mounted_generation,
                observed.mounted_generation
            ),
            (Some(0), 1)
        );
        assert_eq!(observed.joint_field_count, 1);
        assert_eq!(observed.joint_neuron_count, 2);
        assert_eq!(observed.dsf_delivery_count, 2);
        // The current cognitive boundary retains complete neurons only for
        // exact receptor-typed (optical or vestibular) occurrences; this
        // generic test source truthfully claims none.
        assert_eq!(observed.complete_neuron_count, 0);
        assert_eq!(observed.complete_neuron_fractal_count, 0);
        assert_eq!(observed.recurrent_complete_neuron_fractal_count, 0);
        assert_eq!(observed.source_cohort_l0_l4_evaluation_count, 1);
        assert_eq!(observed.successor_l0_l4_replay_count, 0);
        assert_eq!(
            observed.source_authority,
            Some(episode.joint_source_authority_receipt())
        );
        assert_eq!(
            observed.predecessor_state_receipt,
            Some(predecessor_receipt)
        );
        assert!(observed.joint_transition_receipt.is_some());
        assert!(observed.mounted_step_completed);
        assert!(!observed.physical_transition_claimed);
        assert!(!observed.cognitive_formation_claimed);
        assert_eq!(observed.python_callback_count, 0);
        assert_eq!(observed.state_receipt, result.successor.receipt);
        assert_eq!(sha256(&result.successor.bytes), result.successor.receipt);
        let expected_successor = result.successor.bytes.clone();
        let cold = OrganismRuntime::restore_envelope(result.successor.bytes, budget()).unwrap();
        assert_eq!(
            cold.seal(budget().max_envelope_bytes).unwrap().bytes,
            expected_successor
        );
    }

    #[test]
    fn recurrent_step_preserves_identity_and_local_continuity() {
        let first = restored(91, 17)
            .advance_mounted(&source("first"), budget())
            .unwrap();
        let runtime = OrganismRuntime::restore_envelope(first.successor.bytes, budget()).unwrap();
        let second = runtime
            .advance_mounted(&source("second"), budget())
            .unwrap();
        assert_eq!(&second.observation.identity, IDENTITY.as_bytes());
        assert_eq!(
            (
                second.observation.organism_tick,
                second.observation.fabric_generation,
                second.observation.mounted_generation
            ),
            (93, 19, 2)
        );
        assert_eq!(second.observation.dsf_delivery_count, 2);
        assert_eq!(second.observation.complete_neuron_fractal_count, 0);
        assert_eq!(
            second.observation.recurrent_complete_neuron_fractal_count,
            0
        );
        assert_eq!(second.observation.source_cohort_l0_l4_evaluation_count, 1);
        assert_eq!(second.observation.successor_l0_l4_replay_count, 0);
    }

    #[test]
    fn independent_clocks_are_not_required_to_share_a_number() {
        let result = restored(8_003, 401)
            .advance_mounted(&source("independent-clocks"), budget())
            .unwrap();
        assert_eq!(
            (
                result.observation.organism_tick,
                result.observation.fabric_generation,
                result.observation.mounted_generation
            ),
            (8_004, 402, 1)
        );
    }

    #[test]
    fn organism_tick_overflow_refuses_before_mounted_transition() {
        let predecessor = restored(u64::MAX, 17);
        let before = predecessor.observe().clone();
        assert_eq!(
            predecessor
                .advance_mounted(&source("tick-overflow"), budget())
                .unwrap_err(),
            RuntimeError::OrganismTickOverflow
        );
        assert_eq!(predecessor.observe(), &before);
    }

    #[test]
    fn fabric_generation_overflow_refuses_before_mounted_transition() {
        assert_eq!(
            restored(91, u64::MAX)
                .advance_mounted(&source("fabric-overflow"), budget())
                .unwrap_err(),
            RuntimeError::FabricGenerationOverflow
        );
    }

    #[test]
    fn derived_budget_reserves_both_envelopes_before_joint_work() {
        let admitted_envelope = 1_024;
        let admitted_fabric = 900;
        let exact = RuntimeBudget::new(admitted_envelope, admitted_fabric, 2_049).unwrap();
        assert_eq!(exact.derive().unwrap().max_joint_working_bytes, 1);
        assert_eq!(
            RuntimeBudget::new(admitted_envelope, admitted_fabric, 2_048).unwrap_err(),
            RuntimeError::InvalidBudget
        );
    }

    #[test]
    fn restored_observation_does_not_claim_a_step() {
        let runtime = restored(91, 17);
        assert_eq!(runtime.observe().scope, RESTORED_SCOPE);
        assert!(!runtime.observe().mounted_step_completed);
        assert_eq!(runtime.observe().predecessor_organism_tick, None);
        assert_eq!(runtime.observe().python_callback_count, 0);
    }

    #[test]
    fn current_only_restore_returns_exact_unchanged_glorun() {
        let original = restored(91, 17).seal(budget().max_envelope_bytes).unwrap();
        let expected_bytes = original.bytes.clone();
        let runtime = OrganismRuntime::restore_envelope(original.bytes, budget()).unwrap();
        let observation = runtime.observe().clone();
        let restored = runtime.seal(budget().max_envelope_bytes).unwrap();
        assert_eq!(restored.bytes, expected_bytes);
        assert_eq!(restored.receipt, observation.state_receipt);
        assert_eq!(observation.scope, RESTORED_SCOPE);
        assert_eq!(observation.predecessor_state_receipt, None);
        assert_eq!(observation.predecessor_organism_tick, None);
        assert_eq!(observation.predecessor_fabric_generation, None);
        assert_eq!(observation.predecessor_mounted_generation, None);
        assert!(!observation.mounted_step_completed);
        assert_eq!(observation.source_cohort_l0_l4_evaluation_count, 0);
        assert_eq!(observation.successor_l0_l4_replay_count, 0);
    }

    #[test]
    fn native_genesis_has_resting_anatomy_and_no_synthetic_experience() {
        let runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let observation = runtime.observation();
        assert_eq!(observation.identity.as_slice(), IDENTITY.as_bytes());
        assert_eq!(observation.organism_tick, 0);
        assert_eq!(observation.fabric_generation, 0);
        assert_eq!(observation.mounted_generation, 0);
        assert_eq!(observation.joint_field_count, 0);
        assert_eq!(observation.joint_neuron_count, 0);
        assert_eq!(observation.complete_neuron_count, 0);
        assert!(observation.developmental_resting_neuron_count > 0);
        assert_eq!(observation.cognitive_ordinal, 0);
        assert_eq!(observation.cognitive_trace_count, 0);
        assert_eq!(observation.cognitive_mosaic_count, 0);
        assert!(!observation.mounted_step_completed);
        assert!(!observation.cognitive_formation_claimed);
        assert_eq!(runtime.cold_restore_work().decode_count, 1);
        assert!(runtime.active_envelope().starts_with(MAGIC));
    }

    #[test]
    fn resident_growth_dna_genesis_is_structurally_empty_and_carries_only_authored_seeds() {
        let anatomy = exact_optical_episode();
        let seed_groups = vec![(vec![0_usize], Vec::<(usize, usize, i64)>::new())];
        let runtime =
            create_resident_genesis_with_growth_dna(IDENTITY, 0, &anatomy, &seed_groups, budget())
                .unwrap();
        let observation = runtime.observation();
        assert_eq!(observation.identity.as_slice(), IDENTITY.as_bytes());
        assert_eq!(observation.organism_tick, 0);
        assert_eq!(observation.complete_neuron_count, 0);
        assert!(observation.developmental_resting_neuron_count > 0);
        assert_eq!(observation.cognitive_ordinal, 0);
        assert_eq!(observation.cognitive_trace_count, 0);
        assert_eq!(observation.cognitive_mosaic_count, 0);
        assert!(!observation.mounted_step_completed);
        assert!(!observation.cognitive_formation_claimed);
        assert_eq!(
            runtime.active.cognitive.unexpressed_electrical_seed_count(),
            1
        );
        assert!(runtime
            .active
            .cognitive
            .retained_electrical_contact_counts()
            .is_empty());

        let out_of_range = create_resident_genesis_with_growth_dna(
            IDENTITY,
            0,
            &anatomy,
            &[(vec![1], vec![])],
            budget(),
        )
        .unwrap_err();
        assert!(out_of_range.to_string().contains("joint source ports"));
        let empty_groups =
            create_resident_genesis_with_growth_dna(IDENTITY, 0, &anatomy, &[], budget())
                .unwrap_err();
        assert!(empty_groups
            .to_string()
            .contains("at least one authored seed group"));
    }

    #[test]
    #[ignore = "retired: fixture requires Boolean/member-set mosaic admission"]
    fn resident_growth_dna_genesis_expresses_contacts_and_admits_a_real_mosaic() {
        use crate::neuron_source_anchor::tests::{
            exact_four_dark_optical_episode, exact_four_partial_optical_episode,
            exact_four_single_optical_episode,
        };
        let budget = RuntimeBudget::new(33_554_432, 33_000_000, 100_663_296).unwrap();
        let anatomy = exact_four_single_optical_episode(0);
        let seed_groups = vec![(
            (0..4).collect::<Vec<_>>(),
            (1..4)
                .map(|right| (right - 1, right, 500_i64))
                .collect::<Vec<_>>(),
        )];
        let mut runtime =
            create_resident_genesis_with_growth_dna(IDENTITY, 0, &anatomy, &seed_groups, budget)
                .unwrap();
        assert_eq!(runtime.observation().complete_neuron_count, 0);
        assert_eq!(
            runtime.active.cognitive.unexpressed_electrical_seed_count(),
            1
        );

        let dark = exact_four_dark_optical_episode();
        for receptor in 0..4 {
            let source = exact_four_single_optical_episode(receptor);
            let prepared = runtime.prepare_with_store(&source).unwrap();
            if receptor == 0 {
                assert_eq!(prepared.observation.complete_neuron_count, 4);
                assert!(prepared.observation.physical_transition_claimed);
            }
            runtime.commit(prepared.token).unwrap();
        }
        // The reached cohort expressed exactly the three authored contacts and
        // consumed the seed; nothing was inferred at growth time.
        assert_eq!(
            runtime
                .active
                .cognitive
                .retained_electrical_contact_counts(),
            [3]
        );
        assert_eq!(
            runtime.active.cognitive.unexpressed_electrical_seed_count(),
            0
        );

        for _ in 0..DARK_TAIL_EPISODES {
            let prepared = runtime.prepare_with_store(&dark).unwrap();
            runtime.commit(prepared.token).unwrap();
        }
        assert_eq!(runtime.observation().cognitive_mosaic_count, 0);

        let partial = exact_four_partial_optical_episode();
        let mut admitted_mosaic = false;
        for source in
            std::iter::once(&partial).chain(std::iter::repeat(&dark).take(DARK_TAIL_EPISODES))
        {
            let prepared = runtime.prepare_with_store(source).unwrap();
            runtime.commit(prepared.token).unwrap();
            if runtime.observation().cognitive_mosaic_count == 1 {
                admitted_mosaic = true;
                break;
            }
        }
        assert!(
            admitted_mosaic,
            "the authored growth DNA did not lead to an admitted mosaic"
        );

        // The admitted mosaic survives in the sealed envelope as decoded
        // state, not as a transition counter.
        let restored =
            ResidentOrganismRuntime::restore_envelope(runtime.active_envelope().to_vec(), budget)
                .unwrap();
        assert_eq!(restored.observation().cognitive_mosaic_count, 1);
        assert_eq!(restored.observation().complete_neuron_count, 4);
        assert_eq!(
            restored
                .active
                .cognitive
                .retained_electrical_contact_counts(),
            [3]
        );
    }

    #[test]
    fn resident_optical_step_reports_only_the_physical_cells_that_changed() {
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let resting_before = runtime.observation().developmental_resting_neuron_count;
        let prepared = runtime.prepare(&exact_optical_episode()).unwrap();
        assert_eq!(prepared.observation.complete_neuron_count, 2);
        assert_eq!(
            prepared.observation.developmental_resting_neuron_count,
            resting_before - 2
        );
        assert_eq!(prepared.observation.physically_transitioned_neuron_count, 2);
        assert!(prepared.observation.physical_transition_claimed);
        assert_eq!(prepared.observation.complete_neuron_fractal_count, 0);
        assert!(!prepared.observation.cognitive_formation_claimed);
    }

    #[test]
    fn resident_runtime_reports_fractal_after_retained_state_settlement() {
        // The occurrence creates physical change but does not certify its own
        // post-experience retained-state settlement.
        let mut runtime = create_resident_genesis(IDENTITY, 0, budget()).unwrap();
        let light = runtime.prepare(&exact_optical_episode()).unwrap();
        assert_eq!(light.observation.complete_neuron_fractal_count, 0);
        runtime.commit(light.token).unwrap();

        let mut runtime =
            ResidentOrganismRuntime::restore_envelope(runtime.active_envelope().to_vec(), budget())
                .unwrap();
        let mut emitted = 0usize;
        for _ in 0..DARK_TAIL_EPISODES {
            let settled = runtime.prepare(&exact_dark_optical_episode()).unwrap();
            emitted += settled.observation.complete_neuron_fractal_count;
            assert!(!settled.observation.cognitive_formation_claimed);
            runtime.commit(settled.token).unwrap();
        }
        assert_eq!(emitted, 2);

        let mut runtime =
            ResidentOrganismRuntime::restore_envelope(runtime.active_envelope().to_vec(), budget())
                .unwrap();
        let second_dark = runtime.prepare(&exact_dark_optical_episode()).unwrap();
        assert_eq!(second_dark.observation.complete_neuron_fractal_count, 0);
        assert!(!second_dark.observation.cognitive_formation_claimed);
    }

    #[test]
    fn resident_cold_restore_authenticates_once_and_save_is_exact() {
        let stateless = restored(91, 17).seal(budget().max_envelope_bytes).unwrap();
        let expected = stateless.bytes.clone();
        let runtime = ResidentOrganismRuntime::restore_envelope(stateless.bytes, budget()).unwrap();
        assert_eq!(runtime.active_envelope(), expected);
        assert_eq!(runtime.observation().state_receipt, sha256(&expected));
        assert_eq!(
            runtime.cold_restore_work(),
            ResidentMountedRestoreWork {
                authentication_count: 1,
                decode_count: 1,
                rebuilt_predecessor_field_count: 0,
            }
        );
        assert!(runtime.pending.is_none());
    }

    #[test]
    fn resident_prepare_and_discard_leave_active_state_exact() {
        let mut runtime = resident(91, 17);
        let active_bytes = runtime.active_envelope().to_vec();
        let active_observation = runtime.observation();
        let prepared = runtime.prepare(&source("discarded-resident-step")).unwrap();
        assert_eq!(runtime.active_envelope(), active_bytes);
        assert_eq!(runtime.observation(), active_observation);
        assert_eq!(
            prepared.phase_counts,
            MountedTransitionPhaseCounts {
                predecessor_authentication_count: 0,
                predecessor_decode_count: 0,
                predecessor_rebuilt_field_count: 0,
                retained_neuron_index_entry_count: 0,
                reached_neuron_lookup_count: 2,
                current_cohort_evaluation_count: 2,
                successor_seal_count: 1,
            }
        );
        assert_eq!(prepared.receptor_ingress.field_count(), 2);
        assert_eq!(prepared.receptor_ingress.witness_count(), 2);
        assert_eq!(prepared.receptor_ingress.sense_counts(), [2, 0, 0, 0, 0, 0]);
        assert_eq!(prepared.receptor_ingress.reached_neuron_visit_count(), 2);
        assert_eq!(prepared.receptor_ingress.witness_construction_count(), 0);
        assert!(!prepared.observation.physical_transition_claimed);
        assert!(!prepared.observation.cognitive_formation_claimed);
        assert_eq!(
            runtime.prepare(&source("second-pending-step")).unwrap_err(),
            RuntimeError::PendingCandidateExists
        );
        let mut wrong = prepared.token;
        wrong[0] ^= 1;
        assert_eq!(
            runtime.discard(wrong).unwrap_err(),
            RuntimeError::PendingTokenMismatch
        );
        assert_eq!(runtime.active_envelope(), active_bytes);
        assert_eq!(runtime.observation(), active_observation);
        runtime.discard(prepared.token).unwrap();
        assert_eq!(runtime.active_envelope(), active_bytes);
        assert_eq!(runtime.observation(), active_observation);
        assert_eq!(
            runtime.discard(prepared.token).unwrap_err(),
            RuntimeError::PendingCandidateMissing
        );

        let replacement = runtime.prepare(&source("discarded-resident-step")).unwrap();
        assert_ne!(replacement.token, prepared.token);
        assert_eq!(runtime.active_envelope(), active_bytes);
    }

    #[test]
    fn resident_commit_moves_prepared_state_without_redecode_and_consumes_token() {
        let mut runtime = resident(91, 17);
        let active_receipt = runtime.observation().state_receipt;
        let prepared = runtime.prepare(&source("committed-resident-step")).unwrap();
        assert_eq!(
            prepared.observation.predecessor_state_receipt,
            Some(active_receipt)
        );
        assert_eq!(prepared.phase_counts.predecessor_authentication_count, 0);
        assert_eq!(prepared.phase_counts.predecessor_decode_count, 0);
        assert_eq!(prepared.phase_counts.predecessor_rebuilt_field_count, 0);
        runtime.commit(prepared.token).unwrap();
        let committed = runtime.observation();
        assert_eq!(runtime.observation(), prepared.observation);
        assert_eq!(sha256(runtime.active_envelope()), committed.state_receipt);
        assert_eq!(
            (
                committed.organism_tick,
                committed.fabric_generation,
                committed.mounted_generation,
            ),
            (92, 18, 1)
        );
        assert_eq!(
            runtime.commit(prepared.token).unwrap_err(),
            RuntimeError::PendingCandidateMissing
        );
        assert_eq!(
            runtime.cold_restore_work(),
            ResidentMountedRestoreWork {
                authentication_count: 1,
                decode_count: 1,
                rebuilt_predecessor_field_count: 0,
            }
        );
    }

    #[test]
    fn resident_ingress_preserves_independent_clocks_and_exact_successor_bytes() {
        let episode = source("resident-ingress-independent-clocks");
        let mut duplicate = resident(8_003, 401);
        let duplicate_prepared = duplicate.prepare(&episode).unwrap();
        let expected = duplicate
            .pending
            .as_ref()
            .expect("one independently prepared resident successor")
            .envelope
            .clone();
        let mut runtime = resident(8_003, 401);
        let prepared = runtime.prepare(&episode).unwrap();
        assert_eq!(
            (
                prepared.observation.organism_tick,
                prepared.observation.fabric_generation,
                prepared.observation.mounted_generation,
            ),
            (8_004, 402, 1)
        );
        assert_eq!(prepared.observation, duplicate_prepared.observation);
        assert_eq!(prepared.receptor_ingress.witness_count(), 2);
        assert_eq!(
            runtime
                .pending
                .as_ref()
                .expect("one prepared resident successor")
                .envelope,
            expected
        );
    }

    #[test]
    fn dsf_delivery_repetition_cannot_claim_cognition_or_survive_as_a_false_mosaic() {
        let mut runtime = resident(91, 17);
        let first = runtime
            .prepare(&source_with_port_count("formation-origin", 4))
            .unwrap();
        assert!(!first.observation.cognitive_formation_claimed);
        // The cognitive ordinal counts admitted source generations, never
        // claimed cognition: it advances even though nothing formed.
        assert_eq!(first.observation.cognitive_ordinal, 1);
        assert_eq!(first.observation.cognitive_trace_count, 0);
        assert_eq!(first.observation.cognitive_mosaic_count, 0);
        runtime.commit(first.token).unwrap();

        let second = runtime
            .prepare(&source_with_port_count("formation-recurrence", 4))
            .unwrap();
        assert!(!second.observation.cognitive_formation_claimed);
        assert_eq!(second.observation.cognitive_ordinal, 2);
        assert_eq!(second.observation.cognitive_trace_count, 0);
        assert_eq!(second.observation.cognitive_mosaic_count, 0);
        assert_eq!(second.observation.formation_activation_count, 0);
        assert_eq!(second.observation.partial_cue_reassembly_count, 0);
        runtime.commit(second.token).unwrap();

        let saved = runtime.active_envelope().to_vec();
        let mut restored =
            ResidentOrganismRuntime::restore_envelope(saved.clone(), budget()).unwrap();
        assert_eq!(restored.active_envelope(), saved);
        assert_eq!(restored.observation().cognitive_ordinal, 2);
        assert_eq!(restored.observation().cognitive_trace_count, 0);
        assert_eq!(restored.observation().cognitive_mosaic_count, 0);

        let partial = restored
            .prepare(&source_with_port_count("formation-partial-cue", 3))
            .unwrap();
        assert!(!partial.observation.cognitive_formation_claimed);
        assert_eq!(partial.observation.formation_activation_count, 0);
        assert_eq!(partial.observation.partial_cue_reassembly_count, 0);
        assert_eq!(partial.observation.cognitive_mosaic_count, 0);
        restored.commit(partial.token).unwrap();

        let restarted = ResidentOrganismRuntime::restore_envelope(
            restored.active_envelope().to_vec(),
            budget(),
        )
        .unwrap();
        assert_eq!(restarted.observation().cognitive_ordinal, 3);
        assert_eq!(restarted.observation().cognitive_mosaic_count, 0);
    }

    #[test]
    fn resident_readiness_and_save_observe_active_not_pending() {
        let mut runtime = resident(91, 17);
        let active = runtime.observation();
        let active_bytes = runtime.active_envelope().to_vec();
        let prepared = runtime.prepare(&source("hidden-pending-step")).unwrap();
        assert_ne!(prepared.observation.state_receipt, active.state_receipt);
        assert_eq!(runtime.observation(), active);
        assert_eq!(runtime.active_envelope(), active_bytes);
        runtime.commit(prepared.token).unwrap();
        assert_eq!(runtime.observation(), prepared.observation);
        assert_eq!(
            sha256(runtime.active_envelope()),
            prepared.observation.state_receipt
        );
    }

    #[test]
    fn resident_restore_is_current_envelope_only() {
        let raw_fabric = encode_fabric(
            17,
            &genesis_joint(),
            &genesis_cognitive(),
            &genesis_vestibular(),
            &ArticulatedBodyState::at_neutral(),
            budget(),
        )
        .unwrap();
        assert_eq!(
            ResidentOrganismRuntime::restore_envelope(raw_fabric, budget()).unwrap_err(),
            RuntimeError::BadEnvelopeMagic
        );
        let sealed = restored(91, 17).seal(budget().max_envelope_bytes).unwrap();
        let mut old_fabric = sealed.bytes;
        old_fabric[FIXED_BYTES..FIXED_BYTES + 8].copy_from_slice(b"GLMFAB03");
        assert_eq!(
            ResidentOrganismRuntime::restore_envelope(old_fabric, budget()).unwrap_err(),
            RuntimeError::BadFabricMagic
        );
    }

    #[test]
    fn resident_organism_ten_thousand_commits_never_redecode_predecessor() {
        const COMMIT_COUNT: usize = 10_000;
        let mut runtime = resident(91, 17);
        let recurrent_source = source("resident-organism-recurrence");
        let mut evaluations = 0usize;
        for _ in 0..COMMIT_COUNT {
            let prepared = runtime.prepare(&recurrent_source).unwrap();
            assert_eq!(prepared.phase_counts.predecessor_authentication_count, 0);
            assert_eq!(prepared.phase_counts.predecessor_decode_count, 0);
            assert_eq!(prepared.phase_counts.predecessor_rebuilt_field_count, 0);
            assert_eq!(prepared.phase_counts.current_cohort_evaluation_count, 2);
            assert_eq!(prepared.receptor_ingress.witness_count(), 2);
            assert_eq!(prepared.receptor_ingress.reached_neuron_visit_count(), 2);
            assert_eq!(prepared.receptor_ingress.witness_construction_count(), 0);
            evaluations += prepared.phase_counts.current_cohort_evaluation_count;
            runtime.commit(prepared.token).unwrap();
        }
        assert_eq!(evaluations, COMMIT_COUNT * 2);
        assert_eq!(runtime.observation().organism_tick, 10_091);
        assert_eq!(runtime.observation().fabric_generation, 10_017);
        assert_eq!(runtime.observation().mounted_generation, 10_000);
        assert_eq!(
            runtime.cold_restore_work(),
            ResidentMountedRestoreWork {
                authentication_count: 1,
                decode_count: 1,
                rebuilt_predecessor_field_count: 0,
            }
        );
    }

    #[test]
    fn envelope_identity_and_current_schema_are_fail_closed() {
        let raw_fabric = encode_fabric(
            17,
            &genesis_joint(),
            &genesis_cognitive(),
            &genesis_vestibular(),
            &ArticulatedBodyState::at_neutral(),
            budget(),
        )
        .unwrap();
        assert_eq!(
            OrganismRuntime::restore_envelope(raw_fabric, budget()).unwrap_err(),
            RuntimeError::BadEnvelopeMagic
        );
        let sealed = restored(91, 17).seal(budget().max_envelope_bytes).unwrap();
        let mut changed_identity = sealed.bytes.clone();
        changed_identity[MAGIC.len() + 2] = b'G';
        assert_eq!(
            OrganismRuntime::restore_envelope(changed_identity, budget()).unwrap_err(),
            RuntimeError::InvalidIdentity
        );
        let mut old_fabric = sealed.bytes;
        old_fabric[FIXED_BYTES..FIXED_BYTES + 8].copy_from_slice(b"GLMFAB03");
        assert_eq!(
            OrganismRuntime::restore_envelope(old_fabric, budget()).unwrap_err(),
            RuntimeError::BadFabricMagic
        );
    }

    #[test]
    fn authenticated_legacy_migration_emits_only_one_current_runtime_envelope() {
        let legacy = legacy_fabric();
        let authority = test_migration_authority(&legacy);
        let result = migrate_authenticated_legacy_predecessor(
            legacy.clone(),
            sha256(&legacy),
            IDENTITY,
            91,
            budget(),
            authority,
        )
        .unwrap();
        assert_eq!(&result.sealed.bytes[..8], MAGIC);
        assert_eq!(result.legacy_fabric_receipt, sha256(&legacy));
        assert_eq!(&result.observation.identity, IDENTITY.as_bytes());
        assert_eq!(result.observation.organism_tick, 91);
        assert_eq!(result.observation.fabric_generation, 17);
        // The legacy mounted generation is authenticated import provenance,
        // not the causal coordinate of the new resident cognitive path.
        assert_eq!(result.observation.mounted_generation, 0);
        assert!(!result.observation.mounted_step_completed);
        assert!(!result.observation.physical_transition_claimed);
        assert!(!result.observation.cognitive_formation_claimed);
        assert_eq!(result.observation.python_callback_count, 0);
        assert_eq!(result.observation.dsf_delivery_count, 0);
        assert_eq!(result.observation.complete_neuron_fractal_count, 0);
        assert_eq!(
            result.observation.recurrent_complete_neuron_fractal_count,
            0
        );
        assert_eq!(result.observation.source_cohort_l0_l4_evaluation_count, 0);
        assert_eq!(result.observation.successor_l0_l4_replay_count, 0);
        let restored = OrganismRuntime::restore_envelope(result.sealed.bytes, budget()).unwrap();
        assert_eq!(restored.observe().organism_tick, 91);
    }

    #[test]
    fn authenticated_legacy_migration_refuses_wrong_hash_schema_identity_and_tick() {
        let legacy = legacy_fabric();
        let authority = test_migration_authority(&legacy);
        let mut wrong_hash = sha256(&legacy);
        wrong_hash[0] ^= 1;
        assert_eq!(
            migrate_authenticated_legacy_predecessor(
                legacy.clone(),
                wrong_hash,
                IDENTITY,
                91,
                budget(),
                authority,
            )
            .unwrap_err(),
            RuntimeError::LegacyMigration(
                "GLMFAB03 content SHA-256 does not bind the exact body".into()
            )
        );

        let current = encode_fabric(
            17,
            &legacy_joint(),
            &genesis_cognitive(),
            &genesis_vestibular(),
            &ArticulatedBodyState::at_neutral(),
            budget(),
        )
        .unwrap();
        let current_authority = LegacyMigrationAuthority {
            fabric_receipt: sha256(&current),
            ..authority
        };
        assert_eq!(
            migrate_authenticated_legacy_predecessor(
                current.clone(),
                sha256(&current),
                IDENTITY,
                91,
                budget(),
                current_authority,
            )
            .unwrap_err(),
            RuntimeError::LegacyMigration("materialized source evidence is not GLMFAB03".into())
        );

        assert_eq!(
            migrate_authenticated_legacy_predecessor(
                legacy.clone(),
                sha256(&legacy),
                "12345678-9abc-4def-8123-456789abcdeG",
                91,
                budget(),
                authority,
            )
            .unwrap_err(),
            RuntimeError::InvalidIdentity
        );
        assert_eq!(
            migrate_authenticated_legacy_predecessor(
                legacy.clone(),
                sha256(&legacy),
                "22345678-9abc-4def-8123-456789abcdef",
                91,
                budget(),
                authority,
            )
            .unwrap_err(),
            RuntimeError::Task853IdentityMismatch
        );
        assert_eq!(
            migrate_authenticated_legacy_predecessor(
                legacy.clone(),
                sha256(&legacy),
                IDENTITY,
                92,
                budget(),
                authority,
            )
            .unwrap_err(),
            RuntimeError::Task853TickMismatch
        );
    }

    #[test]
    fn migration_output_cannot_reenter_the_one_shot_boundary() {
        let legacy = legacy_fabric();
        let authority = test_migration_authority(&legacy);
        let first = migrate_authenticated_legacy_predecessor(
            legacy.clone(),
            sha256(&legacy),
            IDENTITY,
            91,
            budget(),
            authority,
        )
        .unwrap();
        let output = first.sealed.bytes;
        let output_authority = LegacyMigrationAuthority {
            fabric_receipt: sha256(&output),
            ..authority
        };
        assert_eq!(
            migrate_authenticated_legacy_predecessor(
                output.clone(),
                sha256(&output),
                IDENTITY,
                91,
                budget(),
                output_authority,
            )
            .unwrap_err(),
            RuntimeError::LegacyMigration("materialized source evidence is not GLMFAB03".into())
        );
    }

    #[test]
    #[ignore = "requires GUALA_TASK853_GLMFAB03 to name the authenticated predecessor"]
    fn exact_task853_predecessor_migrates_to_one_current_glorun() {
        let path = std::env::var("GUALA_TASK853_GLMFAB03")
            .expect("GUALA_TASK853_GLMFAB03 must name the authenticated predecessor");
        let legacy = std::fs::read(path).expect("read authenticated task-853 predecessor");
        let migrated = migrate_authenticated_task853_predecessor(
            legacy,
            TASK853_GLMFAB03_SHA256,
            TASK853_IDENTITY,
            TASK853_ORGANISM_TICK,
            RuntimeBudget::new(67_108_864, 67_108_000, 536_870_912).unwrap(),
        )
        .unwrap();
        assert_eq!(&migrated.sealed.bytes[..8], MAGIC);
        assert_eq!(migrated.legacy_fabric_receipt, TASK853_GLMFAB03_SHA256);
        let parsed = parse_current_envelope(
            &migrated.sealed.bytes,
            RuntimeBudget::new(67_108_864, 67_108_000, 536_870_912).unwrap(),
        )
        .unwrap();
        assert_eq!(&parsed.joint_bytes[..8], b"GLJDSF03");
        assert_eq!(migrated.observation.organism_tick, TASK853_ORGANISM_TICK);
        assert_eq!(migrated.observation.fabric_generation, 13);
        assert_eq!(migrated.observation.mounted_generation, 0);
        assert_eq!(migrated.observation.joint_field_count, 2);
        assert_eq!(migrated.observation.joint_neuron_count, 96);
        assert!(!migrated.observation.mounted_step_completed);
        assert!(!migrated.observation.physical_transition_claimed);
        assert!(!migrated.observation.cognitive_formation_claimed);
        assert_eq!(migrated.observation.complete_neuron_fractal_count, 0);
        assert_eq!(
            migrated.observation.recurrent_complete_neuron_fractal_count,
            0
        );
        assert_eq!(migrated.observation.python_callback_count, 0);
    }

    #[test]
    fn pyo3_registration_exports_each_runtime_callable_once() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::new(py, "guala_core_runtime_registration").unwrap();
            register(&module).unwrap();
            let keys = module
                .dict()
                .keys()
                .iter()
                .map(|key| key.extract::<String>().unwrap())
                .collect::<Vec<_>>();
            for name in [
                "transition_native_organism_runtime",
                "restore_native_organism_runtime",
                "restore_native_resident_organism_runtime",
                "create_native_resident_organism_runtime",
                "create_native_resident_organism_runtime_with_growth_dna",
                "migrate_authenticated_task853_predecessor_to_native_organism_runtime",
            ] {
                assert_eq!(
                    keys.iter()
                        .filter(|candidate| candidate.as_str() == name)
                        .count(),
                    1
                );
                assert!(module.getattr(name).unwrap().is_callable());
            }
            for name in [
                "NativeResidentOrganismRuntime",
                "NativeResidentOrganismObservation",
                "NativeResidentOrganismPrepare",
            ] {
                assert_eq!(
                    keys.iter()
                        .filter(|candidate| candidate.as_str() == name)
                        .count(),
                    1
                );
            }
        });
    }

    fn task853_bytes(output: &mut Vec<u8>, value: &[u8]) {
        output.extend_from_slice(&u32::try_from(value.len()).unwrap().to_le_bytes());
        output.extend_from_slice(value);
    }

    #[allow(clippy::too_many_arguments)]
    fn task853_current_source_port(
        output: &mut Vec<u8>,
        sense: u8,
        topology_index: u32,
        sensor_id: &str,
        substream_id: &str,
        coordinates: &[(&str, String)],
        physical_quantity: &str,
        physical_unit: &str,
        source_times: [i64; 3],
        dimensionless_fields: [i64; 3],
    ) {
        output.push(sense);
        output.extend_from_slice(&topology_index.to_le_bytes());
        text(output, sensor_id);
        text(output, substream_id);
        output.extend_from_slice(&u16::try_from(coordinates.len()).unwrap().to_le_bytes());
        for (axis_id, coordinate_id) in coordinates {
            text(output, axis_id);
            text(output, coordinate_id);
        }
        text(output, physical_quantity);
        text(output, physical_unit);
        text(output, "direct-physical-source");
        text(output, "");
        text(output, "identity-binary64");
        rational(output, -1, 1);
        rational(output, 1, 1);
        rational(output, 0, 1);
        rational(output, 1, 1);
        task853_bytes(output, b"identity-binary64-v1");
        output.extend_from_slice(&3_u32.to_le_bytes());
        for (source_time, field) in source_times.into_iter().zip(dimensionless_fields) {
            rational(output, source_time, 1);
            output.extend_from_slice(&(field as f64).to_bits().to_le_bytes());
            rational(output, 0, 1);
            rational(output, 1, 1);
            rational(output, field, 1);
        }
    }

    fn task853_current_occurrence(
        output: &mut Vec<u8>,
        first_port: u32,
        port_count: u32,
        source_times: [i64; 3],
        group_width: u32,
    ) {
        output.extend_from_slice(&port_count.to_le_bytes());
        for port_index in first_port..first_port + port_count {
            output.extend_from_slice(&port_index.to_le_bytes());
        }
        output.extend_from_slice(&3_u32.to_le_bytes());
        for source_time in source_times {
            rational(output, source_time, 1);
        }
        task853_bytes(
            output,
            crate::joint_uf_source_adapter::SAMPLED_VOLUME_AND_RELEVANCE_PIECEWISE_LINEAR_PROFILE,
        );
        assert_eq!(port_count % group_width, 0);
        let group_count = port_count / group_width;
        output.extend_from_slice(&group_count.to_le_bytes());
        for group_index in 0..group_count {
            output.extend_from_slice(&group_width.to_le_bytes());
            for member_offset in 0..group_width {
                output
                    .extend_from_slice(&(group_index * group_width + member_offset).to_le_bytes());
            }
        }
        task853_bytes(output, b"explicit-joint-relevance-v1");
        output.extend_from_slice(&3_u32.to_le_bytes());
        for _ in 0..3 {
            rational(output, 1, 1);
        }
    }

    fn task853_current_two_clock_source() -> NativeJointSourceEpisode {
        let mut output = b"GLJSRC02".to_vec();
        output.extend_from_slice(&2_u16.to_le_bytes());
        text(&mut output, "task853-current-two-clock-sight-sound");
        output.extend_from_slice(&[0, 0, 1, 1, 1, 1]);
        output.extend_from_slice(&96_u32.to_le_bytes());

        for topology_index in 0_u32..64 {
            let row = topology_index / 8;
            let column = topology_index % 8;
            let fields = if topology_index % 2 == 0 {
                [0, 1, 0]
            } else {
                [0, -1, 0]
            };
            task853_current_source_port(
                &mut output,
                0,
                topology_index,
                "browser-camera-retina-8x8",
                &format!("receptor-r{row}-c{column}"),
                &[
                    ("retina-row", row.to_string()),
                    ("retina-column", column.to_string()),
                ],
                "reset-referenced-area-mean-light-intensity",
                "normalized-sensor-code",
                [1, 2, 3],
                fields,
            );
        }

        for topology_index in 0_u32..32 {
            let band = topology_index / 2;
            let is_pressure = topology_index % 2 == 0;
            let component = if is_pressure {
                "pressure-envelope"
            } else {
                "carrier-phase-advance"
            };
            let substream = if is_pressure {
                format!("erb_{band:02}_pressure")
            } else {
                format!("erb_{band:02}_phase_advance")
            };
            let (quantity, unit) = if is_pressure {
                ("cochlear-pressure-envelope", "full-scale-pressure")
            } else {
                (
                    "cochlear-carrier-phase-advance",
                    "nyquist-fraction-per-observation-hop",
                )
            };
            let fields = if topology_index % 4 < 2 {
                [0, 1, 0]
            } else {
                [0, -1, 0]
            };
            task853_current_source_port(
                &mut output,
                1,
                topology_index,
                "microphone-gammatone-cochlear-field",
                &substream,
                &[
                    ("erb-band", format!("{band:02}")),
                    ("cochlear-component", component.to_owned()),
                ],
                quantity,
                unit,
                [10, 12, 14],
                fields,
            );
        }

        output.extend_from_slice(&2_u32.to_le_bytes());
        task853_current_occurrence(&mut output, 0, 64, [1, 2, 3], 8);
        task853_current_occurrence(&mut output, 64, 32, [10, 12, 14], 2);
        decode_native_joint_source_episode(&output, 96, 288, 2, 6).unwrap()
    }

    fn task853_lineage(ordinal: u64) -> [u8; 16] {
        let mut lineage = [0_u8; 16];
        lineage[..8].copy_from_slice(b"GLNLINE1");
        lineage[8..].copy_from_slice(&ordinal.to_be_bytes());
        lineage
    }

    fn task853_prepared_lineages(
        prepared: &crate::mounted_joint_fractal::PreparedMountedGeneration,
    ) -> std::collections::BTreeSet<[u8; 16]> {
        prepared
            .fields()
            .iter()
            .flat_map(|field| field.neurons())
            .map(|neuron| neuron.successor().neuron_lineage)
            .collect()
    }

    fn task853_reconstruct_balanced_ternary(
        trits: &[crate::joint_uf_neuron_boundary::BalancedTrit],
    ) -> num_bigint::BigInt {
        use crate::joint_uf_neuron_boundary::BalancedTrit;
        let mut value = num_bigint::BigInt::from(0);
        let mut place = num_bigint::BigInt::from(1);
        for trit in trits {
            let digit = match trit {
                BalancedTrit::Negative => -1,
                BalancedTrit::Quiescent => 0,
                BalancedTrit::Positive => 1,
            };
            value += num_bigint::BigInt::from(digit) * &place;
            place *= 3_u8;
        }
        value
    }

    #[test]
    #[ignore = "requires the authenticated /tmp/guala-task853-glmfab03.bin predecessor"]
    fn exact_task853_lineages_survive_enriched_two_clock_delivery_and_cold_restore() {
        use num_rational::BigRational;
        use num_traits::ToPrimitive;

        use crate::joint_uf_neuron_boundary::{settle_shared_dsf_mathloom, MathLoomAnatomy};
        use crate::ordered_gate_delivery_candidate::prepare_authenticated_ordered_gate_delivery;

        const STATE_LIMIT: usize = 67_108_000;
        const WORKING_LIMIT: usize = 536_870_912;

        let runtime_budget = RuntimeBudget::new(67_108_864, STATE_LIMIT, WORKING_LIMIT).unwrap();
        let legacy = std::fs::read("/tmp/guala-task853-glmfab03.bin")
            .expect("read authenticated task853 GLMFAB03 predecessor");
        let migrated = migrate_authenticated_task853_predecessor(
            legacy,
            TASK853_GLMFAB03_SHA256,
            TASK853_IDENTITY,
            TASK853_ORGANISM_TICK,
            runtime_budget,
        )
        .unwrap();
        let parsed = parse_current_envelope(&migrated.sealed.bytes, runtime_budget).unwrap();
        assert_eq!(&parsed.joint_bytes[..8], b"GLJDSF03");
        assert_eq!(parsed.fabric_generation, 13);

        let (restored_predecessor, predecessor_summary) =
            restore_resident_mounted_state(parsed.joint_bytes, STATE_LIMIT, WORKING_LIMIT).unwrap();
        assert_eq!(predecessor_summary.generation, 2);
        assert_eq!(predecessor_summary.joint_neuron_count, 96);

        let source = task853_current_two_clock_source();
        assert_eq!(source.joint_source_ports().len(), 96);
        assert_eq!(source.joint_source_occurrences().len(), 2);
        assert_eq!(
            source.joint_source_occurrences()[0].source_times,
            [
                BigRational::from_integer(1.into()),
                BigRational::from_integer(2.into()),
                BigRational::from_integer(3.into()),
            ]
        );
        assert_eq!(
            source.joint_source_occurrences()[1].source_times,
            [
                BigRational::from_integer(10.into()),
                BigRational::from_integer(12.into()),
                BigRational::from_integer(14.into()),
            ]
        );

        let prepared = prepare_resident_mounted_generation(
            &restored_predecessor,
            &source,
            STATE_LIMIT,
            WORKING_LIMIT,
        )
        .unwrap();
        assert_eq!(prepared.predecessor_generation(), 2);
        assert_eq!(prepared.successor_generation(), 3);
        assert_eq!(prepared.transition().joint_neuron_count, 96);
        assert_eq!(
            prepared.phase_counts().retained_neuron_index_entry_count,
            96
        );
        assert_eq!(prepared.phase_counts().reached_neuron_lookup_count, 96);

        let expected_lineages = (1_u64..=96)
            .map(task853_lineage)
            .collect::<std::collections::BTreeSet<_>>();
        assert_eq!(task853_prepared_lineages(&prepared), expected_lineages);
        for field in prepared.fields() {
            assert_eq!(field.source_ports().len(), field.neurons().len());
            for (source_port, neuron) in field.source_ports().iter().zip(field.neurons()) {
                let expected_ordinal = match source_port.sense {
                    0 => u64::from(source_port.topology_index) + 1,
                    1 => u64::from(source_port.topology_index) + 65,
                    other => panic!("unexpected task853 sense {other}"),
                };
                assert_eq!(
                    neuron.successor().neuron_lineage,
                    task853_lineage(expected_ordinal)
                );
                assert_eq!(source_port.coordinates.len(), 2);
            }
        }

        let delivery_plan =
            prepare_authenticated_ordered_gate_delivery(&prepared, &source).unwrap();
        assert_eq!(delivery_plan.occurrence_count(), 2);
        assert_eq!(delivery_plan.lineage_count(), 96);
        assert_eq!(delivery_plan.ordered_occurrences()[0].lineage_count(), 64);
        assert_eq!(delivery_plan.ordered_occurrences()[1].lineage_count(), 32);
        assert_eq!(
            delivery_plan
                .ordered_occurrences()
                .iter()
                .flat_map(|occurrence| occurrence.bindings())
                .map(|binding| binding.lineage())
                .collect::<std::collections::BTreeSet<_>>(),
            expected_lineages
        );

        let anatomy = MathLoomAnatomy::new(delivery_plan.required_mathloom_positions()).unwrap();
        for occurrence in delivery_plan.ordered_occurrences() {
            assert_eq!(
                occurrence.occurrence_index(),
                if occurrence.lineage_count() == 64 {
                    0
                } else {
                    1
                }
            );
            let observed_gate_order = occurrence
                .ordered_gates()
                .map(|gate| {
                    assert_eq!(gate.occurrence_index(), occurrence.occurrence_index());
                    for binding in gate.bindings().iter().copied() {
                        assert_eq!(binding.occurrence_index(), occurrence.occurrence_index());
                        let source_port = &source.joint_source_ports()[binding.source_port_index()];
                        let perspective = gate.perspective(binding).unwrap();
                        assert_eq!(perspective.coordinate_index(), binding.coordinate_index());
                        for local_index in 0..perspective.local_sev_len() {
                            let local = perspective.local_sev(local_index).unwrap();
                            let source_index = local.source_index();
                            let expected_field = source_port.dimensionless_fields[source_index]
                                .to_f64()
                                .unwrap();
                            let expected_delta = if source_index == 0 {
                                0.0
                            } else {
                                expected_field
                                    - source_port.dimensionless_fields[source_index - 1]
                                        .to_f64()
                                        .unwrap()
                            };
                            assert_eq!(local.field().to_bits(), expected_field.to_bits());
                            assert_eq!(local.delta_field().to_bits(), expected_delta.to_bits());
                        }

                        let delivery = settle_shared_dsf_mathloom(perspective, anatomy).unwrap();
                        assert_eq!(delivery.constraints().len(), 7);
                        for (constraint, dsf_value) in delivery
                            .constraints()
                            .iter()
                            .zip(perspective.dsf().ordered())
                        {
                            assert_eq!(constraint.binary64_bits(), dsf_value.to_bits());
                            assert_eq!(
                                constraint.exact_value().to_f64().unwrap().to_bits(),
                                dsf_value.to_bits()
                            );
                            let numerator =
                                task853_reconstruct_balanced_ternary(constraint.word().numerator());
                            let denominator = task853_reconstruct_balanced_ternary(
                                constraint.word().denominator(),
                            );
                            assert_eq!(
                                BigRational::new(numerator, denominator),
                                *constraint.exact_value()
                            );
                        }
                    }
                    gate.gate_index()
                })
                .collect::<Vec<_>>();
            assert_eq!(
                observed_gate_order,
                (0..occurrence.gate_count()).collect::<Vec<_>>()
            );
        }

        let prepared_bytes = prepared.state_bytes().to_vec();
        let (cold_resident, cold_summary) =
            restore_resident_mounted_state(&prepared_bytes, STATE_LIMIT, WORKING_LIMIT).unwrap();
        assert_eq!(cold_summary.generation, 3);
        assert_eq!(cold_summary.joint_neuron_count, 96);

        let recurrent = prepare_resident_mounted_generation(
            &cold_resident,
            &source,
            STATE_LIMIT,
            WORKING_LIMIT,
        )
        .unwrap();
        assert_eq!(recurrent.predecessor_generation(), 3);
        assert_eq!(recurrent.successor_generation(), 4);
        assert_eq!(recurrent.transition().joint_neuron_count, 96);
        assert_eq!(task853_prepared_lineages(&recurrent), expected_lineages);
        assert_eq!(
            recurrent.phase_counts().retained_neuron_index_entry_count,
            96
        );
        assert_eq!(recurrent.phase_counts().reached_neuron_lookup_count, 96);

        let (_, second_cold_summary) =
            restore_resident_mounted_state(recurrent.state_bytes(), STATE_LIMIT, WORKING_LIMIT)
                .unwrap();
        assert_eq!(second_cold_summary.generation, 4);
        assert_eq!(second_cold_summary.joint_neuron_count, 96);
    }
}
