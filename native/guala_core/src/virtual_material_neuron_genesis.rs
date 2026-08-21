//! Production construction of one finite virtual-material neuron.
//!
//! The constructor derives lattice width from the complete seven-field UF
//! perspective and instantiates the exact virtual units accepted for the
//! definitive neuron: zeptojoule coupling, nanometre plastic geometry,
//! picofarad membrane capacitance, picosiemens conductance, and the finite
//! elementary-charge inventory required by one femtocoulomb.  It creates no
//! meaning, score, owner, lock, database row, history, or compatibility state.

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{ToPrimitive, Zero};

use crate::complete_neuron::{
    expand_legacy_receptor_channel_population, extend_neuron_positional_fabric, CarrierReservoirs,
    DnaExpressionAnatomy, DnaExpressionError, DnaExpressionState, GateSettlementError,
    NeuronPhysicalAnatomy, NeuronPhysicalError, NeuronPhysicalState, PlasticSupportAnatomy,
    PlasticSupportState, PlasticityError, PsiKrimelackAnatomy, PsiKrimelackState, PsiRingAnatomy,
    PsiSettlementError, RecoveryAnatomy, RecoveryError, RecoveryLaneAnatomy, RecoveryLaneState,
    RecoveryState, TwoStateGateAnatomy, TwoStateGateState,
};
use crate::declared_geometric_anatomy::{
    declared_geometric_territory, declared_neuron_territory,
    membrane_capacitance_from_declared_place, DeclaredGeometryError, DeclaredNeuronPlace,
};
use crate::elementary_charge_membrane::MembraneChargeError;
use crate::exact_rational::{ExactRational, ExactRationalError};
use crate::joint_source_episode::NativeJointSourceEpisode;
use crate::joint_uf_neuron_boundary::{
    bind_neuron_perspective, declared_field_arithmetic_positions, prepare_complete_joint_field,
    required_mathloom_positions_for_birth_field, BalancedTrit, JointNeuronBoundaryError,
    JointNeuronPerspective, MathLoomAnatomy, SharedCompleteJointField,
};
use crate::local_membrane_conductance_balance::LocalMembraneConductanceState;
use crate::neuron_source_anchor::{
    bind_neuron_source_anchor, NeuronSourceAnchorError, NeuronSourceSite,
};
use crate::reached_neuron_cohort::{
    extend_reached_cohort_cells, ReachedCohortAnatomy, ReachedCohortError, ReachedCohortState,
    ReachedNeuronGenesisCell,
};
use crate::sparse_electrical_contact::{
    SparseElectricalAnatomy, SparseElectricalError, SparseElectricalState,
};

const DSF_CONSTRAINTS: usize = 7;
const ORDINARY_GATE_DISSIPATION_QUANTUM_NUMERATOR: i64 = 1;
const ORDINARY_GATE_DISSIPATION_QUANTUM_DENOMINATOR: i64 = 16;
const ORDINARY_GATE_DISSIPATION_CAPACITY_QUANTA: u128 = 36;
const PLASTIC_ELASTIC_ENERGY_SCALE_NUMERATOR: i64 = 2;
const PLASTIC_ELASTIC_ENERGY_SCALE_DENOMINATOR: i64 = 1;
const PLASTIC_YIELD_STRESS_NUMERATOR: i64 = 1;
const PLASTIC_YIELD_STRESS_DENOMINATOR: i64 = 1;
const PLASTIC_CLOSED_COORDINATE_NUMERATOR: i64 = 1;
const PLASTIC_CLOSED_COORDINATE_DENOMINATOR: i64 = 1;
const PLASTIC_OPEN_COORDINATE_NUMERATOR: i64 = 2;
const PLASTIC_OPEN_COORDINATE_DENOMINATOR: i64 = 1;
const PLASTIC_DISSIPATION_QUANTUM_NUMERATOR: i64 = 3;
const PLASTIC_DISSIPATION_QUANTUM_DENOMINATOR: i64 = 4;
const PLASTIC_GENESIS_REST_LENGTH_NUMERATOR: i64 = 1;
const PLASTIC_GENESIS_REST_LENGTH_DENOMINATOR: i64 = 1;

/// `ceil(1 fC / e)`, where the SI elementary charge is exact.
const ONE_FEMTOCOULOMB_CARRIER_QUANTA: u128 = 6_242;

/// Virgin carrier material assigned to each explicitly represented receptor
/// channel at this virtual organism's genesis. A one-way anatomy correction
/// uses the same physical quantity for omitted channels; it must not derive
/// virgin material from a lived channel whose carriers have already moved.
pub(crate) fn definitive_virtual_carriers_per_compartment() -> u128 {
    ONE_FEMTOCOULOMB_CARRIER_QUANTA
}

/// Virgin mobile material for one declared membrane. The base quantity is one
/// femtocoulomb per one-picofarad unit patch, so an `A`-patch membrane owns
/// `A` such quantities in each local compartment. Gate population is not
/// membrane volume.
pub(crate) fn definitive_virtual_carriers_for_place(
    place: DeclaredNeuronPlace,
) -> Result<u128, DeclaredGeometryError> {
    ONE_FEMTOCOULOMB_CARRIER_QUANTA
        .checked_mul(declared_neuron_territory(place)?)
        .ok_or(DeclaredGeometryError::ArithmeticWidth)
}

/// The authored base membrane capacitance: the picofarad capacitance of ONE
/// unit patch of this virtual membrane.  It is unchanged from the original
/// authored anatomy; the geometric-differentiation ratification (2026-08-05)
/// keeps it as the scale and takes every neuron's spread from the neuron's own
/// declared territory (see `declared_geometric_anatomy`).
const BASE_MEMBRANE_CAPACITANCE_PICOFARADS_NUMERATOR: i128 = 1;
const BASE_MEMBRANE_CAPACITANCE_PICOFARADS_DENOMINATOR: u128 = 1;

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) enum VirtualMaterialGenesisError {
    JointField(JointNeuronBoundaryError),
    ExactRational(ExactRationalError),
    Psi(PsiSettlementError),
    Gate(GateSettlementError),
    Membrane(MembraneChargeError),
    Recovery(RecoveryError),
    Dna(DnaExpressionError),
    Plasticity(PlasticityError),
    Neuron(NeuronPhysicalError),
    Source(NeuronSourceAnchorError),
    DeclaredGeometry(DeclaredGeometryError),
    Cohort(ReachedCohortError),
    Electrical(SparseElectricalError),
    GateEnergyLatticeUnavailable,
    DeclaredPlaceMismatch,
    RestingSpecializationMismatch,
    ArithmeticWidth,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct VirtualMaterialNeuronGenesis {
    pub(crate) anatomy: NeuronPhysicalAnatomy,
    pub(crate) state: NeuronPhysicalState,
    pub(crate) zero_recovery_catalysts: Box<[u128]>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct VirtualMaterialReachedCohortGenesis {
    pub(crate) anatomy: ReachedCohortAnatomy,
    pub(crate) state: ReachedCohortState,
    pub(crate) zero_recovery_catalysts: Box<[Box<[u128]>]>,
}

/// Construct the complete source-specialized cells for one explicit joint
/// occurrence. Sparse contact anatomy must already exist; this function never
/// infers a synapse or gap junction from source order, coordinate proximity,
/// DSF values, or simultaneous observation.
pub(crate) fn create_virtual_material_reached_cohort(
    episode: &NativeJointSourceEpisode,
    occurrence_index: usize,
    neuron_lineages: Vec<[u8; 16]>,
    electrical: SparseElectricalAnatomy,
) -> Result<VirtualMaterialReachedCohortGenesis, VirtualMaterialGenesisError> {
    let shared = prepare_complete_joint_field(episode, occurrence_index)
        .map_err(VirtualMaterialGenesisError::JointField)?;
    create_virtual_material_reached_cohort_from_shared(
        episode,
        &shared,
        neuron_lineages,
        electrical,
    )
}

pub(crate) fn create_virtual_material_reached_cohort_from_shared(
    episode: &NativeJointSourceEpisode,
    shared: &SharedCompleteJointField,
    neuron_lineages: Vec<[u8; 16]>,
    electrical: SparseElectricalAnatomy,
) -> Result<VirtualMaterialReachedCohortGenesis, VirtualMaterialGenesisError> {
    create_virtual_material_reached_cohort_subset_from_shared(
        episode,
        shared,
        &(0..shared.vertex_count()).collect::<Vec<_>>(),
        neuron_lineages,
        electrical,
    )
}

/// Construct one receptor/anatomical cohort from a declared physical group
/// inside a larger simultaneous joint occurrence.  The complete joint field
/// is still evaluated once and every selected neuron retains its perspective
/// into that same field; this function only prevents unrelated receptor
/// structures from being fused into one resident fluid compartment.
pub(crate) fn create_virtual_material_reached_cohort_subset_from_shared(
    episode: &NativeJointSourceEpisode,
    shared: &SharedCompleteJointField,
    coordinate_indices: &[usize],
    neuron_lineages: Vec<[u8; 16]>,
    electrical: SparseElectricalAnatomy,
) -> Result<VirtualMaterialReachedCohortGenesis, VirtualMaterialGenesisError> {
    if coordinate_indices.is_empty()
        || coordinate_indices.len() != neuron_lineages.len()
        || coordinate_indices
            .iter()
            .enumerate()
            .any(|(index, coordinate)| {
                *coordinate >= shared.vertex_count()
                    || coordinate_indices[..index].contains(coordinate)
            })
    {
        return Err(VirtualMaterialGenesisError::ArithmeticWidth);
    }
    let mut neurons = Vec::new();
    let mut states = Vec::new();
    let mut source_sites = Vec::new();
    let mut catalysts = Vec::new();
    neurons
        .try_reserve_exact(coordinate_indices.len())
        .map_err(|_| VirtualMaterialGenesisError::ArithmeticWidth)?;
    states
        .try_reserve_exact(coordinate_indices.len())
        .map_err(|_| VirtualMaterialGenesisError::ArithmeticWidth)?;
    source_sites
        .try_reserve_exact(coordinate_indices.len())
        .map_err(|_| VirtualMaterialGenesisError::ArithmeticWidth)?;
    catalysts
        .try_reserve_exact(coordinate_indices.len())
        .map_err(|_| VirtualMaterialGenesisError::ArithmeticWidth)?;
    for coordinate_index in coordinate_indices {
        let perspective = bind_neuron_perspective(shared, *coordinate_index, 0)
            .map_err(VirtualMaterialGenesisError::JointField)?;
        let source = bind_neuron_source_anchor(episode, perspective)
            .map_err(VirtualMaterialGenesisError::Source)?;
        let site = NeuronSourceSite::from_anchor(source);
        let genesis = create_virtual_material_neuron(perspective, &site)?;
        source_sites.push(site);
        neurons.push(genesis.anatomy);
        states.push(genesis.state);
        catalysts.push(genesis.zero_recovery_catalysts);
    }
    let electrical_state = SparseElectricalState::genesis(&electrical);
    let anatomy = ReachedCohortAnatomy::new(neurons, neuron_lineages, source_sites, electrical)
        .map_err(VirtualMaterialGenesisError::Cohort)?;
    let state = ReachedCohortState::new(&anatomy, states, electrical_state)
        .map_err(VirtualMaterialGenesisError::Cohort)?;
    Ok(VirtualMaterialReachedCohortGenesis {
        anatomy,
        state,
        zero_recovery_catalysts: catalysts.into_boxed_slice(),
    })
}

pub(crate) fn extend_virtual_material_reached_cohort_from_shared(
    episode: &NativeJointSourceEpisode,
    shared: &SharedCompleteJointField,
    anatomy: &ReachedCohortAnatomy,
    state: &ReachedCohortState,
    additions: &[(usize, [u8; 16])],
) -> Result<(ReachedCohortAnatomy, ReachedCohortState), VirtualMaterialGenesisError> {
    let mut cells = Vec::new();
    cells
        .try_reserve_exact(additions.len())
        .map_err(|_| VirtualMaterialGenesisError::ArithmeticWidth)?;
    for (coordinate_index, lineage) in additions {
        let perspective = bind_neuron_perspective(shared, *coordinate_index, 0)
            .map_err(VirtualMaterialGenesisError::JointField)?;
        let source = bind_neuron_source_anchor(episode, perspective)
            .map_err(VirtualMaterialGenesisError::Source)?;
        let site = NeuronSourceSite::from_anchor(source);
        let genesis = create_virtual_material_neuron(perspective, &site)?;
        cells.push(ReachedNeuronGenesisCell {
            anatomy: genesis.anatomy,
            lineage: *lineage,
            mount: crate::reached_neuron_cohort::ReachedNeuronMount::Receptor(site),
            state: genesis.state,
        });
    }
    extend_reached_cohort_cells(anatomy, state, cells).map_err(VirtualMaterialGenesisError::Cohort)
}

impl VirtualMaterialNeuronGenesis {
    pub(crate) fn anatomy(&self) -> &NeuronPhysicalAnatomy {
        &self.anatomy
    }

    pub(crate) fn state(&self) -> &NeuronPhysicalState {
        &self.state
    }

    pub(crate) fn zero_recovery_catalysts(&self) -> &[u128] {
        &self.zero_recovery_catalysts
    }

    pub(crate) fn into_parts(self) -> (NeuronPhysicalAnatomy, NeuronPhysicalState, Box<[u128]>) {
        (self.anatomy, self.state, self.zero_recovery_catalysts)
    }
}

fn exact(numerator: i64, denominator: i64) -> BigRational {
    BigRational::new(BigInt::from(numerator), BigInt::from(denominator))
}

fn ratio(numerator: i128, denominator: u128) -> Result<ExactRational, VirtualMaterialGenesisError> {
    ExactRational::new(numerator, denominator).map_err(VirtualMaterialGenesisError::ExactRational)
}

pub(crate) fn definitive_virtual_gate_capacity_zeptojoules() -> BigRational {
    exact(
        ORDINARY_GATE_DISSIPATION_QUANTUM_NUMERATOR,
        ORDINARY_GATE_DISSIPATION_QUANTUM_DENOMINATOR,
    ) * BigRational::from_integer(ORDINARY_GATE_DISSIPATION_CAPACITY_QUANTA.into())
}

/// Exact open-minus-closed support energy at the already-mounted genesis rest
/// geometry. This derives the occurrence from the same declared plastic
/// anatomy used below; it does not add a receptor coefficient.
pub(crate) fn definitive_virtual_genesis_support_energy_zeptojoules() -> BigRational {
    definitive_virtual_reachable_support_energies_zeptojoules()[0].clone()
}

/// Exact support energies reachable by the definitive one-channel plastic
/// anatomy. Genesis begins closed at rest length one. Its only yielding move
/// is the first opening, whose existing return map gives
/// `r' = xE/(E+Y) = 2*2/(2+1) = 4/3`; later closed/open moves remain inside
/// that yield surface. A receptor-specialized gate lattice must represent both
/// support energies because either can participate in its next exact delta-G.
pub(crate) fn definitive_virtual_reachable_support_energies_zeptojoules() -> [BigRational; 2] {
    let elastic_scale = exact(
        PLASTIC_ELASTIC_ENERGY_SCALE_NUMERATOR,
        PLASTIC_ELASTIC_ENERGY_SCALE_DENOMINATOR,
    );
    let yield_stress = exact(
        PLASTIC_YIELD_STRESS_NUMERATOR,
        PLASTIC_YIELD_STRESS_DENOMINATOR,
    );
    let genesis_rest = exact(
        PLASTIC_GENESIS_REST_LENGTH_NUMERATOR,
        PLASTIC_GENESIS_REST_LENGTH_DENOMINATOR,
    );
    let closed_coordinate = exact(
        PLASTIC_CLOSED_COORDINATE_NUMERATOR,
        PLASTIC_CLOSED_COORDINATE_DENOMINATOR,
    );
    let open_coordinate = exact(
        PLASTIC_OPEN_COORDINATE_NUMERATOR,
        PLASTIC_OPEN_COORDINATE_DENOMINATOR,
    );
    let yielded_open_rest = &open_coordinate * &elastic_scale / (&elastic_scale + yield_stress);
    [
        support_energy_at_rest(
            &elastic_scale,
            &closed_coordinate,
            &open_coordinate,
            &genesis_rest,
        ),
        support_energy_at_rest(
            &elastic_scale,
            &closed_coordinate,
            &open_coordinate,
            &yielded_open_rest,
        ),
    ]
}

fn support_energy_at_rest(
    elastic_scale: &BigRational,
    closed_coordinate: &BigRational,
    open_coordinate: &BigRational,
    rest: &BigRational,
) -> BigRational {
    let closed_strain = (closed_coordinate - rest) / rest;
    let open_strain = (open_coordinate - rest) / rest;
    let two = BigRational::from_integer(2.into());
    let closed_energy = elastic_scale * &closed_strain * &closed_strain / &two;
    let open_energy = elastic_scale * &open_strain * &open_strain / two;
    open_energy - closed_energy
}

/// Construct one quiescent neuron from the exact width demanded by its full
/// DSF perspective.  The constructor does not consume an experience and cannot
/// itself create a neuronal fractal.
pub(crate) fn create_virtual_material_neuron(
    perspective: JointNeuronPerspective<'_>,
    site: &NeuronSourceSite,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    create_virtual_material_neuron_with_gate_energy_quantum(
        perspective,
        site,
        exact(
            ORDINARY_GATE_DISSIPATION_QUANTUM_NUMERATOR,
            ORDINARY_GATE_DISSIPATION_QUANTUM_DENOMINATOR,
        ),
    )
}

/// Construct one receptor neuron for one explicitly declared physical
/// terminal. The terminal owns one transduction gate; its membrane
/// capacitance and carrier material still derive from its unique declared
/// place. This avoids multiplying one anatomical ending into one gate per
/// geometric territory patch.
pub(crate) fn create_single_terminal_virtual_material_neuron(
    perspective: JointNeuronPerspective<'_>,
    site: &NeuronSourceSite,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    let positions = required_mathloom_positions_for_birth_field(perspective)
        .map_err(VirtualMaterialGenesisError::JointField)?
        .max(declared_field_arithmetic_positions());
    build_quiescent_virtual_material_neuron(
        positions,
        DeclaredNeuronPlace::from_source_site(site),
        1,
        false,
        exact(
            ORDINARY_GATE_DISSIPATION_QUANTUM_NUMERATOR,
            ORDINARY_GATE_DISSIPATION_QUANTUM_DENOMINATOR,
        ),
    )
}

/// Construct the same definitive virtual-material neuron with a receptor-
/// derived exact gate-energy lattice. The physical dissipation capacity is
/// preserved from the ordinary genesis as `(1/16 zJ) * 36 = 9/4 zJ`; only its
/// exact quantum count changes. No energy is rounded or selected by modality.
pub(crate) fn create_virtual_material_neuron_with_gate_energy_quantum(
    perspective: JointNeuronPerspective<'_>,
    site: &NeuronSourceSite,
    gate_dissipation_quantum_zeptojoules: BigRational,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    let receptor_population = declared_geometric_territory(site)
        .map_err(VirtualMaterialGenesisError::DeclaredGeometry)?;
    // Every gate in this already-arrived occurrence belongs to the neuron's
    // one current birth field.  Mount the smallest exact positional fabric
    // that can carry that whole field; this is not future capacity and does
    // not pre-grow for any later occurrence.
    let positions = required_mathloom_positions_for_birth_field(perspective)
        .map_err(VirtualMaterialGenesisError::JointField)?
        .max(declared_field_arithmetic_positions());
    build_quiescent_virtual_material_neuron(
        positions,
        DeclaredNeuronPlace::from_source_site(site),
        receptor_population,
        receptor_population > 1,
        gate_dissipation_quantum_zeptojoules,
    )
}

/// Construct one neuron at its organism-relative resting place before any
/// receptor, joint field, or sensory episode reaches it.  Birth mounts only
/// the minimum exact positional fabric required by the unchanged seven-field
/// arithmetic.  A later real occurrence may extend that fabric before it
/// settles; birth itself performs no field evaluation and emits no fractal.
pub(crate) fn create_quiescent_virtual_material_neuron(
    place: DeclaredNeuronPlace,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    build_quiescent_virtual_material_neuron(
        declared_field_arithmetic_positions(),
        place,
        1,
        false,
        exact(
            ORDINARY_GATE_DISSIPATION_QUANTUM_NUMERATOR,
            ORDINARY_GATE_DISSIPATION_QUANTUM_DENOMINATOR,
        ),
    )
}

/// Let one already-declared quiescent cell reach its first ordinary receptor.
/// The cell's place, capacitance, lived coordinates, and state remain its own.
/// Only virgin receptor-channel material omitted from its source-independent
/// resting anatomy and any newly required high MathLoom/Psi positions are
/// mounted before the first occurrence settles. No experience is evaluated
/// here and this transition cannot itself emit a neuronal fractal.
pub(crate) fn reach_quiescent_virtual_material_neuron(
    perspective: JointNeuronPerspective<'_>,
    site: &NeuronSourceSite,
    declared_place: DeclaredNeuronPlace,
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    if DeclaredNeuronPlace::from_source_site(site) != declared_place {
        return Err(VirtualMaterialGenesisError::DeclaredPlaceMismatch);
    }
    let positions = required_mathloom_positions_for_birth_field(perspective)
        .map_err(VirtualMaterialGenesisError::JointField)?
        .max(declared_field_arithmetic_positions());
    let (anatomy, state) = extend_neuron_positional_fabric(anatomy, state, positions)
        .map_err(VirtualMaterialGenesisError::Neuron)?;
    let receptor_population = declared_geometric_territory(site)
        .map_err(VirtualMaterialGenesisError::DeclaredGeometry)?;
    let (anatomy, state) =
        expand_legacy_receptor_channel_population(&anatomy, &state, receptor_population, 0)
    .map_err(VirtualMaterialGenesisError::Neuron)?;
    let zero_recovery_catalysts = vec![0; anatomy.psi_ring_count()].into_boxed_slice();
    Ok(VirtualMaterialNeuronGenesis {
        anatomy,
        state,
        zero_recovery_catalysts,
    })
}

/// Reach an already-declared quiescent cell with one explicit physical
/// terminal. The resting cell already owns its one gate, so first contact
/// extends only the exact positional fabric required by the arrived field.
pub(crate) fn reach_quiescent_single_terminal_virtual_material_neuron(
    perspective: JointNeuronPerspective<'_>,
    site: &NeuronSourceSite,
    declared_place: DeclaredNeuronPlace,
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    if DeclaredNeuronPlace::from_source_site(site) != declared_place
        || anatomy.gate_population() != 1
    {
        return Err(VirtualMaterialGenesisError::DeclaredPlaceMismatch);
    }
    let positions = required_mathloom_positions_for_birth_field(perspective)
        .map_err(VirtualMaterialGenesisError::JointField)?
        .max(declared_field_arithmetic_positions());
    let (anatomy, state) = extend_neuron_positional_fabric(anatomy, state, positions)
        .map_err(VirtualMaterialGenesisError::Neuron)?;
    let zero_recovery_catalysts = vec![0; anatomy.psi_ring_count()].into_boxed_slice();
    Ok(VirtualMaterialNeuronGenesis {
        anatomy,
        state,
        zero_recovery_catalysts,
    })
}

/// Express one receptor-specific gate-energy lattice in an already-declared
/// virgin cell.  This is the specialization-DNA boundary: it is legal only
/// while the cell is still byte-for-byte its source-independent quiescent
/// genesis.  Its lineage is owned by the caller; its place, capacitance and
/// total physical gate capacity remain unchanged.  A lived cell can never be
/// rebuilt or retyped through this function.
pub(crate) fn specialize_quiescent_virtual_material_neuron_with_gate_energy_quantum(
    perspective: JointNeuronPerspective<'_>,
    site: &NeuronSourceSite,
    declared_place: DeclaredNeuronPlace,
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
    gate_dissipation_quantum_zeptojoules: BigRational,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    if DeclaredNeuronPlace::from_source_site(site) != declared_place {
        return Err(VirtualMaterialGenesisError::DeclaredPlaceMismatch);
    }
    let virgin = create_quiescent_virtual_material_neuron(declared_place)?;
    if virgin.anatomy() != anatomy || virgin.state() != state {
        return Err(VirtualMaterialGenesisError::RestingSpecializationMismatch);
    }
    let positions = required_mathloom_positions_for_birth_field(perspective)
        .map_err(VirtualMaterialGenesisError::JointField)?
        .max(declared_field_arithmetic_positions());
    let specialized = build_quiescent_virtual_material_neuron(
        positions,
        declared_place,
        1,
        false,
        gate_dissipation_quantum_zeptojoules,
    )?;
    if specialized.anatomy().capacitance() != anatomy.capacitance()
        || specialized.state().carrier_reservoirs().total() != state.carrier_reservoirs().total()
    {
        return Err(VirtualMaterialGenesisError::RestingSpecializationMismatch);
    }
    Ok(specialized)
}

fn build_quiescent_virtual_material_neuron(
    positions: usize,
    place: DeclaredNeuronPlace,
    receptor_population: u128,
    independent_gate_channels: bool,
    gate_dissipation_quantum_zeptojoules: BigRational,
) -> Result<VirtualMaterialNeuronGenesis, VirtualMaterialGenesisError> {
    if gate_dissipation_quantum_zeptojoules <= BigRational::zero() || receptor_population == 0 {
        return Err(VirtualMaterialGenesisError::GateEnergyLatticeUnavailable);
    }
    let physical_gate_capacity_zeptojoules = definitive_virtual_gate_capacity_zeptojoules()
        * BigRational::from_integer(BigInt::from(receptor_population));
    let derived_capacity =
        physical_gate_capacity_zeptojoules / &gate_dissipation_quantum_zeptojoules;
    if !derived_capacity.is_integer() {
        return Err(VirtualMaterialGenesisError::GateEnergyLatticeUnavailable);
    }
    let gate_dissipation_capacity_quanta = derived_capacity
        .to_integer()
        .to_u128()
        .filter(|value| *value != 0)
        .ok_or(VirtualMaterialGenesisError::GateEnergyLatticeUnavailable)?;
    let ring_count = positions
        .checked_mul(DSF_CONSTRAINTS)
        .and_then(|value| value.checked_mul(2))
        .ok_or(VirtualMaterialGenesisError::ArithmeticWidth)?;

    let ring = PsiRingAnatomy::new(
        [1, 1, 1],
        [exact(0, 1), exact(0, 1), exact(0, 1)],
        exact(1, 1),
        exact(9, 2),
        1,
        [[true; 3]; 3],
        BalancedTrit::Quiescent,
    )
    .map_err(VirtualMaterialGenesisError::Psi)?;
    let psi = PsiKrimelackAnatomy::new(positions, DSF_CONSTRAINTS, vec![ring; ring_count])
        .map_err(VirtualMaterialGenesisError::Psi)?;

    let gate = if independent_gate_channels {
        TwoStateGateAnatomy::new_independent_channels(
            receptor_population,
            0,
            exact(0, 1),
            gate_dissipation_quantum_zeptojoules,
            gate_dissipation_capacity_quanta,
            ratio(1, 1)?,
            ratio(-1, 1)?,
            Vec::new(),
            ring_count,
        )
    } else {
        TwoStateGateAnatomy::new(
            receptor_population,
            0,
            exact(0, 1),
            gate_dissipation_quantum_zeptojoules,
            gate_dissipation_capacity_quanta,
            ratio(1, 1)?,
            ratio(-1, 1)?,
            Vec::new(),
            ring_count,
        )
    }
    .map_err(VirtualMaterialGenesisError::Gate)?;

    let recovery_lane = RecoveryLaneAnatomy::new(1, 1, 1, 1, 1, 1, 1)
        .map_err(VirtualMaterialGenesisError::Recovery)?;
    let gate_recovery_lane = RecoveryLaneAnatomy::new(
        1,
        1,
        1,
        1,
        gate_dissipation_capacity_quanta,
        gate_dissipation_capacity_quanta,
        gate_dissipation_capacity_quanta,
    )
    .map_err(VirtualMaterialGenesisError::Recovery)?;
    let recovery = RecoveryAnatomy::new(
        vec![recovery_lane; ring_count],
        gate_recovery_lane,
        RecoveryLaneAnatomy::new(
            1,
            1,
            1,
            1,
            receptor_population,
            receptor_population,
            receptor_population,
        )
        .map_err(VirtualMaterialGenesisError::Recovery)?,
        ring_count,
    )
    .map_err(VirtualMaterialGenesisError::Recovery)?;
    let dna =
        DnaExpressionAnatomy::new(1, 1, 1, 1, 1, 1, 1).map_err(VirtualMaterialGenesisError::Dna)?;
    let plastic = PlasticSupportAnatomy::new(
        ratio(
            PLASTIC_ELASTIC_ENERGY_SCALE_NUMERATOR.into(),
            PLASTIC_ELASTIC_ENERGY_SCALE_DENOMINATOR as u128,
        )?,
        ratio(
            PLASTIC_YIELD_STRESS_NUMERATOR.into(),
            PLASTIC_YIELD_STRESS_DENOMINATOR as u128,
        )?,
        ratio(
            PLASTIC_CLOSED_COORDINATE_NUMERATOR.into(),
            PLASTIC_CLOSED_COORDINATE_DENOMINATOR as u128,
        )?,
        ratio(
            PLASTIC_OPEN_COORDINATE_NUMERATOR.into(),
            PLASTIC_OPEN_COORDINATE_DENOMINATOR as u128,
        )?,
        ratio(
            PLASTIC_DISSIPATION_QUANTUM_NUMERATOR.into(),
            PLASTIC_DISSIPATION_QUANTUM_DENOMINATOR as u128,
        )?,
        receptor_population,
    )
    .map_err(VirtualMaterialGenesisError::Plasticity)?;
    // Ratified 2026-08-05: the membrane is as large as the territory this
    // receptor's own declared place closes off in the organism's sensory
    // lattice, so no two authored neurons can be physically identical.
    let capacitance = membrane_capacitance_from_declared_place(
        ratio(
            BASE_MEMBRANE_CAPACITANCE_PICOFARADS_NUMERATOR,
            BASE_MEMBRANE_CAPACITANCE_PICOFARADS_DENOMINATOR,
        )?,
        place,
    )
    .map_err(VirtualMaterialGenesisError::DeclaredGeometry)?;
    let mathloom =
        MathLoomAnatomy::new(positions).map_err(VirtualMaterialGenesisError::JointField)?;
    let anatomy = NeuronPhysicalAnatomy::new(
        mathloom,
        psi.clone(),
        gate,
        capacitance,
        recovery,
        dna,
        plastic,
    )
    .map_err(VirtualMaterialGenesisError::Neuron)?;
    let carriers_per_compartment = definitive_virtual_carriers_for_place(place)
        .map_err(VirtualMaterialGenesisError::DeclaredGeometry)?;
    let state = NeuronPhysicalState::new(
        PsiKrimelackState::genesis(&psi),
        TwoStateGateState::genesis(0),
        LocalMembraneConductanceState::genesis(0),
        CarrierReservoirs::new(carriers_per_compartment, carriers_per_compartment),
        RecoveryState::new(
            vec![RecoveryLaneState::new(1); ring_count],
            RecoveryLaneState::new(gate_dissipation_capacity_quanta),
            RecoveryLaneState::new(receptor_population),
        ),
        DnaExpressionState::new(1, 1),
        PlasticSupportState::new(ratio(
            PLASTIC_GENESIS_REST_LENGTH_NUMERATOR.into(),
            PLASTIC_GENESIS_REST_LENGTH_DENOMINATOR as u128,
        )?)
        .map_err(VirtualMaterialGenesisError::Plasticity)?,
        // Quantized-light law (ratified 2026-08-05): a newborn receptor has
        // integrated no light, so its retained sub-quantum residue is zero.
        ratio(0, 1)?,
        // Exact rest-cost law (2026-08-06): a newborn neuron has done no
        // membrane-return work, so it owes no sub-quantum remainder.
        ratio(0, 1)?,
    );
    Ok(VirtualMaterialNeuronGenesis {
        anatomy,
        state,
        zero_recovery_catalysts: vec![0; ring_count].into_boxed_slice(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::complete_neuron::{
        decode_neuron_physical_cell, encode_neuron_physical_cell,
        gate_population_opening_schedule_with_psi, settle_extended_interval_with_contact,
        sparse_physical_state_delta, DnaExpressionContact, GateWorkOccurrence, NeuronIntervalInput,
        PhysicalStateCoordinate, RecoveryContact,
    };
    use crate::joint_uf_neuron_boundary::{
        bind_neuron_perspective, prepare_complete_joint_field_admitted_fixture,
    };
    use crate::neuron_source_anchor::tests::{exact_episode, exact_four_optical_episode};
    use crate::optical_receptor_work::quantize_optical_population_delivery;
    use crate::reached_neuron_cohort::{decode_reached_cohort_cell, encode_reached_cohort_cell};
    use crate::sparse_electrical_contact::SparseElectricalAnatomy;

    #[test]
    fn production_genesis_is_exact_finite_and_cold_restorable() {
        let episode = exact_episode();
        let shared = prepare_complete_joint_field_admitted_fixture(&episode, 0).unwrap();
        let perspective = bind_neuron_perspective(&shared, 0, 0).unwrap();
        let site = NeuronSourceSite::from_anchor(
            bind_neuron_source_anchor(&episode, perspective).unwrap(),
        );
        let genesis = create_virtual_material_neuron(perspective, &site).unwrap();
        assert_eq!(
            genesis.zero_recovery_catalysts().len(),
            genesis.state().psi.rings().len()
        );
        assert_eq!(
            genesis.state().carrier_reservoirs().total(),
            Some(ONE_FEMTOCOULOMB_CARRIER_QUANTA * 2)
        );
        let encoded = encode_neuron_physical_cell(genesis.anatomy(), genesis.state()).unwrap();
        let (restored_anatomy, restored_state) = decode_neuron_physical_cell(&encoded).unwrap();
        assert_eq!(&restored_anatomy, genesis.anatomy());
        assert_eq!(&restored_state, genesis.state());
        assert_eq!(
            encode_neuron_physical_cell(&restored_anatomy, &restored_state).unwrap(),
            encoded
        );
        assert!(restored_state.resident_bytes().unwrap() < encoded.len());
    }

    #[test]
    fn one_three_and_four_neurons_are_born_quiescent_before_sensation() {
        let mut single_cell_bytes = None;
        for count in [1_usize, 3, 4] {
            let mut capacitances = std::collections::BTreeSet::new();
            let mut total_encoded_bytes = 0_usize;
            for topology_index in 0..count {
                let place = DeclaredNeuronPlace::new(
                    7,
                    u32::try_from(topology_index).expect("small fixture index"),
                );
                let genesis = create_quiescent_virtual_material_neuron(place).unwrap();
                assert_eq!(
                    genesis.anatomy().mathloom_positions(),
                    declared_field_arithmetic_positions()
                );
                assert!(
                    sparse_physical_state_delta(genesis.state(), genesis.state())
                        .unwrap()
                        .is_none(),
                    "birth cannot emit a neuronal fractal"
                );
                assert!(capacitances.insert(genesis.anatomy().capacitance().picofarads().parts()));
                let territory = declared_neuron_territory(place).unwrap();
                assert_eq!(
                    genesis.state().carrier_reservoirs().total(),
                    Some(ONE_FEMTOCOULOMB_CARRIER_QUANTA * territory * 2),
                    "virgin carrier material follows membrane territory"
                );

                let encoded =
                    encode_neuron_physical_cell(genesis.anatomy(), genesis.state()).unwrap();
                if count == 1 {
                    println!(
                        "MEASURE source-independent resting neuron: encoded={} B resident={} B",
                        encoded.len(),
                        genesis.state().resident_bytes().unwrap()
                    );
                }
                let (restored_anatomy, restored_state) =
                    decode_neuron_physical_cell(&encoded).unwrap();
                assert_eq!(&restored_anatomy, genesis.anatomy());
                assert_eq!(&restored_state, genesis.state());
                assert_eq!(
                    encode_neuron_physical_cell(&restored_anatomy, &restored_state).unwrap(),
                    encoded
                );
                total_encoded_bytes += encoded.len();
                match single_cell_bytes {
                    Some(bytes) => assert_eq!(encoded.len(), bytes),
                    None => single_cell_bytes = Some(encoded.len()),
                }
            }
            assert_eq!(capacitances.len(), count);
            assert_eq!(total_encoded_bytes, single_cell_bytes.unwrap() * count);
        }
    }

    #[test]
    fn reached_cohort_genesis_preserves_every_source_specialization_and_cell() {
        let episode = exact_episode();
        let shared = prepare_complete_joint_field_admitted_fixture(&episode, 0).unwrap();
        let electrical = SparseElectricalAnatomy::new(shared.vertex_count(), Vec::new()).unwrap();
        let lineages = (1..=shared.vertex_count())
            .map(|index| (index as u128).to_be_bytes())
            .collect();
        let genesis = create_virtual_material_reached_cohort_from_shared(
            &episode, &shared, lineages, electrical,
        )
        .unwrap();
        assert_eq!(genesis.anatomy.neuron_count(), shared.vertex_count());
        assert_eq!(genesis.state.neurons().len(), shared.vertex_count());
        assert_eq!(genesis.zero_recovery_catalysts.len(), shared.vertex_count());
        let encoded = encode_reached_cohort_cell(&genesis.anatomy, &genesis.state).unwrap();
        let (restored_anatomy, restored_state) = decode_reached_cohort_cell(&encoded).unwrap();
        assert_eq!(restored_anatomy, genesis.anatomy);
        assert_eq!(restored_state, genesis.state);
        assert_eq!(
            encode_reached_cohort_cell(&restored_anatomy, &restored_state).unwrap(),
            encoded
        );
    }

    #[test]
    fn resting_cells_keep_their_place_while_first_receptor_contact_specializes_them() {
        let episode = exact_four_optical_episode();
        let shared = prepare_complete_joint_field_admitted_fixture(&episode, 0).unwrap();
        let mut reached = Vec::new();
        let mut retained = Vec::new();
        for coordinate_index in [1_usize, 2] {
            let perspective = bind_neuron_perspective(&shared, coordinate_index, 0).unwrap();
            let site = NeuronSourceSite::from_anchor(
                bind_neuron_source_anchor(&episode, perspective).unwrap(),
            );
            let place = DeclaredNeuronPlace::from_source_site(&site);
            let resting = create_quiescent_virtual_material_neuron(place).unwrap();
            let resting_capacitance = resting.anatomy().capacitance();
            let specialized = reach_quiescent_virtual_material_neuron(
                perspective,
                &site,
                place,
                resting.anatomy(),
                resting.state(),
            )
            .unwrap();
            let direct = create_virtual_material_neuron(perspective, &site).unwrap();
            assert_eq!(specialized.anatomy().capacitance(), resting_capacitance);
            assert_eq!(specialized.anatomy(), direct.anatomy());
            assert_eq!(specialized.state(), direct.state());
            assert_eq!(
                specialized.state().carrier_reservoirs(),
                resting.state().carrier_reservoirs(),
                "first receptor specialization cannot create carrier material"
            );
            assert_eq!(
                specialized.anatomy().gate_population(),
                declared_geometric_territory(&site).unwrap()
            );
            let encoded =
                encode_neuron_physical_cell(specialized.anatomy(), specialized.state()).unwrap();
            let (cold_anatomy, cold_state) = decode_neuron_physical_cell(&encoded).unwrap();
            assert_eq!(&cold_anatomy, specialized.anatomy());
            assert_eq!(&cold_state, specialized.state());

            let prepared_psi = specialized
                .anatomy()
                .prepare_psi_settlement(specialized.state(), perspective)
                .unwrap();
            let schedule = gate_population_opening_schedule_with_psi(
                specialized.anatomy(),
                specialized.state(),
                &prepared_psi,
            )
            .unwrap();
            let quantum = BigRational::new(BigInt::from(1), BigInt::from(16));
            let energy = &quantum * BigRational::from_integer(BigInt::from(10));
            let delivery = quantize_optical_population_delivery(
                &energy,
                specialized.state().receptor_quantum_residue,
                &quantum,
                &schedule,
            )
            .unwrap();
            let lit = settle_extended_interval_with_contact(
                specialized.anatomy(),
                specialized.state(),
                NeuronIntervalInput {
                    perspective,
                    gate_work: delivery.gate_work,
                    interval_microseconds: 1_000,
                    recovery: RecoveryContact::new(specialized.zero_recovery_catalysts(), 0, 0),
                    dna_expression: DnaExpressionContact::new(0),
                    receptor_successor_residue: Some(delivery.successor_residue),
                    prepared_psi: Some(prepared_psi),
                },
                0,
            )
            .unwrap();
            let dark_psi = specialized
                .anatomy()
                .prepare_psi_settlement(&lit.successor, perspective)
                .unwrap();
            let dark = settle_extended_interval_with_contact(
                specialized.anatomy(),
                &lit.successor,
                NeuronIntervalInput {
                    perspective,
                    gate_work: GateWorkOccurrence::new(BigRational::zero()),
                    interval_microseconds: 1_000,
                    recovery: RecoveryContact::new(specialized.zero_recovery_catalysts(), 0, 0),
                    dna_expression: DnaExpressionContact::new(0),
                    receptor_successor_residue: None,
                    prepared_psi: Some(dark_psi),
                },
                0,
            )
            .unwrap();
            retained.push(
                sparse_physical_state_delta(specialized.state(), &dark.successor)
                    .unwrap()
                    .unwrap(),
            );
            reached.push(specialized);
        }
        assert_ne!(reached[0].anatomy(), reached[1].anatomy());
        assert_ne!(retained[0], retained[1]);
    }

    #[test]
    fn sight_territory_yields_graded_retained_states_and_cold_restores_exactly() {
        let episode = exact_four_optical_episode();
        let shared = prepare_complete_joint_field_admitted_fixture(&episode, 0).unwrap();
        let perspective = bind_neuron_perspective(&shared, 2, 0).unwrap();
        let site = NeuronSourceSite::from_anchor(
            bind_neuron_source_anchor(&episode, perspective).unwrap(),
        );
        let genesis = create_virtual_material_neuron(perspective, &site).unwrap();
        let population = declared_geometric_territory(&site).unwrap();
        assert_eq!(population, 6);
        assert_eq!(genesis.anatomy().gate_population(), population);
        assert_eq!(
            genesis.state().carrier_reservoirs().total(),
            Some(ONE_FEMTOCOULOMB_CARRIER_QUANTA * population * 2)
        );

        let settle_light_then_dark = |energy_quanta: u128| {
            let prepared_psi = genesis
                .anatomy()
                .prepare_psi_settlement(genesis.state(), perspective)
                .unwrap();
            let schedule = gate_population_opening_schedule_with_psi(
                genesis.anatomy(),
                genesis.state(),
                &prepared_psi,
            )
            .unwrap();
            // Collective receptor geometry x(n) makes each next channel's
            // exact barrier depend on the currently open population. The
            // former constant 17-quantum schedule belonged to the rejected
            // independent irreversible-prefix model.
            assert_eq!(
                schedule.expanded_activation_quanta().unwrap(),
                [1, 2, 3, 4, 5, 5]
            );
            let quantum = BigRational::new(BigInt::from(1), BigInt::from(16));
            let energy = &quantum * BigRational::from_integer(BigInt::from(energy_quanta));
            let delivery = quantize_optical_population_delivery(
                &energy,
                genesis.state().receptor_quantum_residue,
                &quantum,
                &schedule,
            )
            .unwrap();
            let lit = settle_extended_interval_with_contact(
                genesis.anatomy(),
                genesis.state(),
                NeuronIntervalInput {
                    perspective,
                    gate_work: delivery.gate_work,
                    interval_microseconds: 1_000,
                    recovery: RecoveryContact::new(genesis.zero_recovery_catalysts(), 0, 0),
                    dna_expression: DnaExpressionContact::new(0),
                    receptor_successor_residue: Some(delivery.successor_residue),
                    prepared_psi: Some(prepared_psi),
                },
                0,
            )
            .unwrap();
            let lit_delta = sparse_physical_state_delta(genesis.state(), &lit.successor)
                .unwrap()
                .unwrap();

            let dark_psi = genesis
                .anatomy()
                .prepare_psi_settlement(&lit.successor, perspective)
                .unwrap();
            let dark = settle_extended_interval_with_contact(
                genesis.anatomy(),
                &lit.successor,
                NeuronIntervalInput {
                    perspective,
                    gate_work: GateWorkOccurrence::new(BigRational::zero()),
                    interval_microseconds: 1_000,
                    recovery: RecoveryContact::new(genesis.zero_recovery_catalysts(), 0, 0),
                    dna_expression: DnaExpressionContact::new(0),
                    receptor_successor_residue: None,
                    prepared_psi: Some(dark_psi),
                },
                0,
            )
            .unwrap();
            let retained = sparse_physical_state_delta(genesis.state(), &dark.successor)
                .unwrap()
                .unwrap();
            (lit_delta, dark.successor, retained)
        };

        let (lower_lit, lower_state, lower_retained) = settle_light_then_dark(10);
        assert_eq!(
            lower_lit
                .exact_delta(PhysicalStateCoordinate::GateOpenPopulation)
                .unwrap(),
            crate::complete_neuron::ExactPhysicalStateDelta::Integral(
                crate::complete_neuron::ExactSignedDelta::from_parts(false, 4).unwrap()
            )
        );
        assert_eq!(
            lower_retained
                .exact_delta(PhysicalStateCoordinate::GateOpenPopulation)
                .unwrap(),
            crate::complete_neuron::ExactPhysicalStateDelta::Integral(
                crate::complete_neuron::ExactSignedDelta::from_parts(false, 1).unwrap()
            )
        );
        assert_eq!(
            lower_retained
                .exact_delta(PhysicalStateCoordinate::PlasticRestLength)
                .unwrap(),
            crate::complete_neuron::ExactPhysicalStateDelta::Rational(
                ExactRational::new(1, 9).unwrap()
            )
        );

        let (_, higher_state, higher_retained) = settle_light_then_dark(15);
        assert_eq!(
            higher_retained
                .exact_delta(PhysicalStateCoordinate::PlasticRestLength)
                .unwrap(),
            crate::complete_neuron::ExactPhysicalStateDelta::Rational(
                ExactRational::new(2, 9).unwrap()
            )
        );
        assert_ne!(lower_state, higher_state);

        for state in [lower_state, higher_state] {
            let encoded = encode_neuron_physical_cell(genesis.anatomy(), &state).unwrap();
            let (restored_anatomy, restored_state) = decode_neuron_physical_cell(&encoded).unwrap();
            assert_eq!(&restored_anatomy, genesis.anatomy());
            assert_eq!(restored_state, state);
            assert_eq!(
                encode_neuron_physical_cell(&restored_anatomy, &restored_state).unwrap(),
                encoded
            );
        }
    }
}
