//! Definitive local physical transition for one reached Guala neuron.
//!
//! One ingress is a borrowed perspective over one shared UF v1.4 result. All
//! seven DSF facts pass through exact MathLoom balanced ternary into the mounted
//! Psi/Krimelack energy fabric. The same local interval also receives exact gate
//! work, recovery and DNA contacts, elapsed physical duration, and any sparse
//! inter-neuron charge transfer. Physical gate, conductance, membrane, finite
//! material, recovery, DNA, and plasticity consequences follow. A
//! neuronal fractal exists only as the retained sparse difference between
//! pre-experience and post-experience quiescent physical states.
//!
//! This pure transition contains no owner, lock, database, receipt, hash,
//! serializer, semantic label, score, ML approximation, or legacy VTVR field.

use crate::elementary_charge_membrane::{
    settle_membrane_elementary_charges, ElementaryChargeMembraneState, MembraneCapacitance,
};
use crate::elementary_charge_transfer::{
    current_limited_by_available_carriers, settle_elementary_charge_transfer, ChargeCarrierPhase,
};
use crate::exact_rational::{ExactRational, ExactRationalError};
use crate::joint_uf_neuron_boundary::{
    settle_shared_dsf_mathloom, BalancedTrit, BorrowedMathLoomDelivery, JointNeuronBoundaryError,
    JointNeuronPerspective, MathLoomAnatomy,
};
use crate::local_membrane_conductance_balance::{
    settle_local_membrane_conductances_with_inter_neuron_contact, LocalConductancePath,
    LocalMembraneConductanceState, LocalMembraneConductanceTransition, MembraneConductanceError,
};
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};
use std::collections::HashMap;
use std::fmt;
use std::ops::{Deref, DerefMut};
use std::sync::Arc;

type Exact = BigRational;

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PsiRingAnatomy {
    node_amplitude_quanta: [u128; 3],
    rest_energy_zeptojoules: [Exact; 3],
    dsf_coupling_zeptojoules: Exact,
    dissipation_quantum_zeptojoules: Exact,
    dissipation_capacity_quanta: u128,
    reachable: [[bool; 3]; 3],
    genesis_winding: BalancedTrit,
}

impl PsiRingAnatomy {
    pub(crate) fn new(
        node_amplitude_quanta: [u128; 3],
        rest_energy_zeptojoules: [Exact; 3],
        dsf_coupling_zeptojoules: Exact,
        dissipation_quantum_zeptojoules: Exact,
        dissipation_capacity_quanta: u128,
        reachable: [[bool; 3]; 3],
        genesis_winding: BalancedTrit,
    ) -> Result<Self, PsiSettlementError> {
        if node_amplitude_quanta.contains(&0)
            || dsf_coupling_zeptojoules <= Exact::zero()
            || dissipation_quantum_zeptojoules <= Exact::zero()
        {
            return Err(PsiSettlementError::NonPositiveEnergyAnatomy);
        }
        for state in 0..3 {
            if !reachable[state][state] || reachable[state] != transpose_row(&reachable, state) {
                return Err(PsiSettlementError::AsymmetricReachability);
            }
        }
        Ok(Self {
            node_amplitude_quanta,
            rest_energy_zeptojoules,
            dsf_coupling_zeptojoules,
            dissipation_quantum_zeptojoules,
            dissipation_capacity_quanta,
            reachable,
            genesis_winding,
        })
    }
}

fn transpose_row(matrix: &[[bool; 3]; 3], row: usize) -> [bool; 3] {
    [matrix[0][row], matrix[1][row], matrix[2][row]]
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PsiKrimelackAnatomy {
    positions: usize,
    constraint_count: usize,
    rings: Box<[PsiRingAnatomy]>,
}

impl PsiKrimelackAnatomy {
    pub(crate) fn new(
        positions: usize,
        constraint_count: usize,
        rings: Vec<PsiRingAnatomy>,
    ) -> Result<Self, PsiSettlementError> {
        let required = constraint_count
            .checked_mul(2)
            .and_then(|count| count.checked_mul(positions))
            .ok_or(PsiSettlementError::AnatomyWidth)?;
        if positions == 0 || rings.len() != required {
            return Err(PsiSettlementError::AnatomyWidth);
        }
        Ok(Self {
            positions,
            constraint_count,
            rings: rings.into_boxed_slice(),
        })
    }

    pub(crate) fn ring_count(&self) -> usize {
        self.rings.len()
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub(crate) struct PsiRingState {
    amplitude_quanta: [u128; 3],
    phase_thirds: [i8; 3],
    winding: BalancedTrit,
    dissipated_quanta: u128,
}

impl PsiRingState {
    pub(crate) fn amplitude_quanta(self) -> [u128; 3] {
        self.amplitude_quanta
    }

    pub(crate) fn phase_thirds(self) -> [i8; 3] {
        self.phase_thirds
    }

    pub(crate) fn winding(self) -> BalancedTrit {
        self.winding
    }

    pub(crate) fn dissipated_quanta(self) -> u128 {
        self.dissipated_quanta
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PsiKrimelackState {
    rings: Box<[PsiRingState]>,
}

impl PsiKrimelackState {
    pub(crate) fn genesis(anatomy: &PsiKrimelackAnatomy) -> Self {
        let rings = anatomy
            .rings
            .iter()
            .map(|ring| PsiRingState {
                amplitude_quanta: ring.node_amplitude_quanta,
                phase_thirds: canonical_phase_thirds(ring.genesis_winding),
                winding: ring.genesis_winding,
                dissipated_quanta: 0,
            })
            .collect::<Vec<_>>()
            .into_boxed_slice();
        Self { rings }
    }

    pub(crate) fn rings(&self) -> &[PsiRingState] {
        &self.rings
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum PsiSettlementError {
    NonPositiveEnergyAnatomy,
    AsymmetricReachability,
    AnatomyWidth,
    DeliveryShapeChanged,
    DegenerateLowerEnergySuccessor,
    DissipationNotQuantized,
    ArithmeticWidth,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PsiSettlement {
    pub(crate) successor: PsiKrimelackState,
    pub(crate) changed_rings: usize,
    pub(crate) dissipated_quanta: u128,
}

/// Settle every typed MathLoom position through its mounted finite energy
/// landscape. DSF supplies only the canonical coupling-energy term. The
/// successor is selected by reachable exact energy descent, never assignment
/// from the incoming trit. Exact ties retain the predecessor when possible and
/// otherwise refuse an unresolved symmetric successor.
pub(crate) fn settle_psi_krimelack(
    anatomy: &PsiKrimelackAnatomy,
    predecessor: &PsiKrimelackState,
    delivery: &BorrowedMathLoomDelivery<'_>,
) -> Result<PsiSettlement, PsiSettlementError> {
    if delivery.constraints().len() != anatomy.constraint_count
        || predecessor.rings.len() != anatomy.rings.len()
        || delivery.constraints().iter().any(|constraint| {
            constraint.word().numerator().len() != anatomy.positions
                || constraint.word().denominator().len() != anatomy.positions
        })
    {
        return Err(PsiSettlementError::DeliveryShapeChanged);
    }
    let mut successor = predecessor.clone();
    let mut changed_rings = 0_usize;
    let mut dissipated_quanta = 0_u128;
    let uniform_ring_anatomy = anatomy
        .rings
        .first()
        .filter(|first| anatomy.rings.iter().all(|ring| ring == *first));
    let mut uniform_settlements = HashMap::<(PsiRingState, BalancedTrit), PsiRingState>::new();
    for constraint_index in 0..anatomy.constraint_count {
        let word = delivery.constraints()[constraint_index].word();
        for (part_index, part) in [word.numerator(), word.denominator()].iter().enumerate() {
            for (position, target) in part.iter().enumerate() {
                let ring_index = (constraint_index * 2 + part_index) * anatomy.positions + position;
                let ring_anatomy = &anatomy.rings[ring_index];
                let prior = predecessor.rings[ring_index];
                let settled = if let Some(uniform) = uniform_ring_anatomy {
                    if let Some(settled) = uniform_settlements.get(&(prior, *target)) {
                        *settled
                    } else {
                        let settled = settle_one_ring(uniform, prior, *target)?;
                        uniform_settlements.insert((prior, *target), settled);
                        settled
                    }
                } else {
                    settle_one_ring(ring_anatomy, prior, *target)?
                };
                if settled.winding != prior.winding {
                    changed_rings += 1;
                    let used = settled
                        .dissipated_quanta
                        .checked_sub(prior.dissipated_quanta)
                        .ok_or(PsiSettlementError::ArithmeticWidth)?;
                    dissipated_quanta = dissipated_quanta
                        .checked_add(used)
                        .ok_or(PsiSettlementError::ArithmeticWidth)?;
                }
                successor.rings[ring_index] = settled;
            }
        }
    }
    Ok(PsiSettlement {
        successor,
        changed_rings,
        dissipated_quanta,
    })
}

fn settle_one_ring(
    anatomy: &PsiRingAnatomy,
    predecessor: PsiRingState,
    target: BalancedTrit,
) -> Result<PsiRingState, PsiSettlementError> {
    let current_index = trit_index(predecessor.winding);
    let mut energies = [Exact::zero(), Exact::zero(), Exact::zero()];
    for candidate in all_trits() {
        let index = trit_index(candidate);
        energies[index] = ring_energy(anatomy, candidate, target);
    }
    let mut minimum: Option<(usize, &Exact)> = None;
    let mut tied = false;
    for candidate in 0..3 {
        if !anatomy.reachable[current_index][candidate] {
            continue;
        }
        match minimum {
            None => minimum = Some((candidate, &energies[candidate])),
            Some((_, energy)) if energies[candidate] < *energy => {
                minimum = Some((candidate, &energies[candidate]));
                tied = false;
            }
            Some((_, energy)) if energies[candidate] == *energy => tied = true,
            _ => {}
        }
    }
    let (minimum_index, minimum_energy) = minimum.expect("self reachability is admitted");
    if energies[current_index] == *minimum_energy {
        return Ok(predecessor);
    }
    if tied {
        return Err(PsiSettlementError::DegenerateLowerEnergySuccessor);
    }
    let drop = &energies[current_index] - minimum_energy;
    let quanta = exact_unsigned_quanta(&drop, &anatomy.dissipation_quantum_zeptojoules)
        .ok_or(PsiSettlementError::DissipationNotQuantized)?;
    let next_dissipated = predecessor
        .dissipated_quanta
        .checked_add(quanta)
        .ok_or(PsiSettlementError::ArithmeticWidth)?;
    if next_dissipated > anatomy.dissipation_capacity_quanta {
        return Ok(predecessor);
    }
    Ok(PsiRingState {
        amplitude_quanta: anatomy.node_amplitude_quanta,
        phase_thirds: canonical_phase_thirds(all_trits()[minimum_index]),
        winding: all_trits()[minimum_index],
        dissipated_quanta: next_dissipated,
    })
}

fn ring_energy(anatomy: &PsiRingAnatomy, candidate: BalancedTrit, target: BalancedTrit) -> Exact {
    let constraint = if candidate == target {
        -Exact::from_integer(BigInt::from(3_u8)) * &anatomy.dsf_coupling_zeptojoules
    } else {
        Exact::new(BigInt::from(3_u8), BigInt::from(2_u8)) * &anatomy.dsf_coupling_zeptojoules
    };
    &anatomy.rest_energy_zeptojoules[trit_index(candidate)] + constraint
}

fn all_trits() -> [BalancedTrit; 3] {
    [
        BalancedTrit::Negative,
        BalancedTrit::Quiescent,
        BalancedTrit::Positive,
    ]
}

fn trit_index(value: BalancedTrit) -> usize {
    match value {
        BalancedTrit::Negative => 0,
        BalancedTrit::Quiescent => 1,
        BalancedTrit::Positive => 2,
    }
}

fn canonical_phase_thirds(winding: BalancedTrit) -> [i8; 3] {
    match winding {
        BalancedTrit::Negative => [0, -1, 1],
        BalancedTrit::Quiescent => [0, 0, 0],
        BalancedTrit::Positive => [0, 1, -1],
    }
}

fn exact_unsigned_quanta(energy: &Exact, quantum: &Exact) -> Option<u128> {
    if energy <= &Exact::zero() || quantum <= &Exact::zero() {
        return None;
    }
    let ratio = energy / quantum;
    if !ratio.is_integer() || ratio.is_negative() {
        return None;
    }
    ratio.to_integer().to_u128()
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct GatePsiContact {
    ring_index: usize,
    node_index: usize,
    preferred_phase_third: i8,
    open_minus_closed_coupling_zeptojoules: Exact,
}

impl GatePsiContact {
    pub(crate) fn new(
        ring_index: usize,
        node_index: usize,
        preferred_phase_third: i8,
        open_minus_closed_coupling_zeptojoules: Exact,
    ) -> Result<Self, GateSettlementError> {
        if node_index >= 3
            || !(-1..=1).contains(&preferred_phase_third)
            || open_minus_closed_coupling_zeptojoules < Exact::zero()
        {
            return Err(GateSettlementError::InvalidPsiContact);
        }
        Ok(Self {
            ring_index,
            node_index,
            preferred_phase_third,
            open_minus_closed_coupling_zeptojoules,
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct TwoStateGateAnatomy {
    population: u128,
    independent_channel_supports: bool,
    occurrence_bounded_population_work: bool,
    gating_charge_elementary: i128,
    chemical_open_minus_closed_zeptojoules: Exact,
    dissipation_quantum_zeptojoules: Exact,
    dissipation_capacity_quanta: u128,
    single_channel_conductance_picosiemens: ExactRational,
    reversal_potential_millivolts: ExactRational,
    psi_contacts: Box<[GatePsiContact]>,
}

impl TwoStateGateAnatomy {
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn new(
        population: u128,
        gating_charge_elementary: i128,
        chemical_open_minus_closed_zeptojoules: Exact,
        dissipation_quantum_zeptojoules: Exact,
        dissipation_capacity_quanta: u128,
        single_channel_conductance_picosiemens: ExactRational,
        reversal_potential_millivolts: ExactRational,
        psi_contacts: Vec<GatePsiContact>,
        psi_ring_count: usize,
    ) -> Result<Self, GateSettlementError> {
        Self::new_with_support_mode(
            population,
            false,
            false,
            gating_charge_elementary,
            chemical_open_minus_closed_zeptojoules,
            dissipation_quantum_zeptojoules,
            dissipation_capacity_quanta,
            single_channel_conductance_picosiemens,
            reversal_potential_millivolts,
            psi_contacts,
            psi_ring_count,
        )
    }

    #[allow(clippy::too_many_arguments)]
    pub(crate) fn new_independent_channels(
        population: u128,
        gating_charge_elementary: i128,
        chemical_open_minus_closed_zeptojoules: Exact,
        dissipation_quantum_zeptojoules: Exact,
        dissipation_capacity_quanta: u128,
        single_channel_conductance_picosiemens: ExactRational,
        reversal_potential_millivolts: ExactRational,
        psi_contacts: Vec<GatePsiContact>,
        psi_ring_count: usize,
    ) -> Result<Self, GateSettlementError> {
        Self::new_with_support_mode(
            population,
            true,
            true,
            gating_charge_elementary,
            chemical_open_minus_closed_zeptojoules,
            dissipation_quantum_zeptojoules,
            dissipation_capacity_quanta,
            single_channel_conductance_picosiemens,
            reversal_potential_millivolts,
            psi_contacts,
            psi_ring_count,
        )
    }

    #[allow(clippy::too_many_arguments)]
    fn new_with_support_mode(
        population: u128,
        independent_channel_supports: bool,
        occurrence_bounded_population_work: bool,
        gating_charge_elementary: i128,
        chemical_open_minus_closed_zeptojoules: Exact,
        dissipation_quantum_zeptojoules: Exact,
        dissipation_capacity_quanta: u128,
        single_channel_conductance_picosiemens: ExactRational,
        reversal_potential_millivolts: ExactRational,
        psi_contacts: Vec<GatePsiContact>,
        psi_ring_count: usize,
    ) -> Result<Self, GateSettlementError> {
        if population == 0
            || dissipation_quantum_zeptojoules <= Exact::zero()
            || single_channel_conductance_picosiemens.parts().0 < 0
        {
            return Err(GateSettlementError::InvalidAnatomy);
        }
        if psi_contacts
            .iter()
            .any(|contact| contact.ring_index >= psi_ring_count)
        {
            return Err(GateSettlementError::ContactOutsidePsiAnatomy);
        }
        Ok(Self {
            population,
            independent_channel_supports,
            occurrence_bounded_population_work,
            gating_charge_elementary,
            chemical_open_minus_closed_zeptojoules,
            dissipation_quantum_zeptojoules,
            dissipation_capacity_quanta,
            single_channel_conductance_picosiemens,
            reversal_potential_millivolts,
            psi_contacts: psi_contacts.into_boxed_slice(),
        })
    }

    pub(crate) fn dissipation_capacity_quanta(&self) -> u128 {
        self.dissipation_capacity_quanta
    }

    pub(crate) fn population(&self) -> u128 {
        self.population
    }

    fn has_independent_channel_supports(&self) -> bool {
        self.independent_channel_supports
    }

    fn has_occurrence_bounded_population_work(&self) -> bool {
        self.occurrence_bounded_population_work
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct PhysicalEnergyResidue {
    energy_zeptojoules: Exact,
}

impl PhysicalEnergyResidue {
    fn zero() -> Self {
        Self {
            energy_zeptojoules: Exact::zero(),
        }
    }

    fn from_exact_rational(value: ExactRational) -> Self {
        Self {
            energy_zeptojoules: rational_to_exact(value),
        }
    }

    fn energy(&self) -> &Exact {
        &self.energy_zeptojoules
    }

    fn is_zero(&self) -> bool {
        self.energy_zeptojoules.is_zero()
    }

    fn fixed_width(&self) -> Option<ExactRational> {
        ExactRational::new(
            self.energy_zeptojoules.numer().to_i128()?,
            self.energy_zeptojoules.denom().to_u128()?,
        )
        .ok()
    }

    fn heap_bytes(&self) -> Option<usize> {
        self.energy_zeptojoules
            .numer()
            .to_signed_bytes_le()
            .len()
            .checked_add(self.energy_zeptojoules.denom().to_signed_bytes_le().len())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct TwoStateGateState {
    open_population: u128,
    dissipated_quanta: u128,
    dissipation_residue_zeptojoules: PhysicalEnergyResidue,
}

impl TwoStateGateState {
    pub(crate) fn genesis(open_population: u128) -> Self {
        Self {
            open_population,
            dissipated_quanta: 0,
            dissipation_residue_zeptojoules: PhysicalEnergyResidue::zero(),
        }
    }

    pub(crate) fn open_population(&self) -> u128 {
        self.open_population
    }

    pub(crate) fn dissipated_quanta(&self) -> u128 {
        self.dissipated_quanta
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct CarrierReservoirs {
    intracellular: u128,
    extracellular: u128,
}

impl CarrierReservoirs {
    pub(crate) fn new(intracellular: u128, extracellular: u128) -> Self {
        Self {
            intracellular,
            extracellular,
        }
    }

    pub(crate) fn total(self) -> Option<u128> {
        self.intracellular.checked_add(self.extracellular)
    }

    pub(crate) fn intracellular(self) -> u128 {
        self.intracellular
    }

    pub(crate) fn extracellular(self) -> u128 {
        self.extracellular
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct RecoveryLaneAnatomy {
    catalyst_per_extent: u128,
    fuel_per_extent: u128,
    spent_per_extent: u128,
    exported_heat_per_extent: u128,
    fuel_capacity: u128,
    spent_capacity: u128,
    exported_heat_capacity: u128,
}

impl RecoveryLaneAnatomy {
    pub(crate) fn new(
        catalyst_per_extent: u128,
        fuel_per_extent: u128,
        spent_per_extent: u128,
        exported_heat_per_extent: u128,
        fuel_capacity: u128,
        spent_capacity: u128,
        exported_heat_capacity: u128,
    ) -> Result<Self, RecoveryError> {
        if catalyst_per_extent == 0
            || fuel_per_extent == 0
            || spent_per_extent == 0
            || exported_heat_per_extent == 0
            || fuel_per_extent != spent_per_extent
        {
            return Err(RecoveryError::InvalidAnatomy);
        }
        Ok(Self {
            catalyst_per_extent,
            fuel_per_extent,
            spent_per_extent,
            exported_heat_per_extent,
            fuel_capacity,
            spent_capacity,
            exported_heat_capacity,
        })
    }

    pub(crate) fn capacities(self) -> (u128, u128, u128) {
        (
            self.fuel_capacity,
            self.spent_capacity,
            self.exported_heat_capacity,
        )
    }

    pub(crate) fn stoichiometry(self) -> (u128, u128, u128, u128) {
        (
            self.catalyst_per_extent,
            self.fuel_per_extent,
            self.spent_per_extent,
            self.exported_heat_per_extent,
        )
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct RecoveryLaneState {
    fuel_quanta: u128,
    spent_quanta: u128,
    exported_heat_quanta: u128,
}

impl RecoveryLaneState {
    pub(crate) fn new(fuel_quanta: u128) -> Self {
        Self {
            fuel_quanta,
            spent_quanta: 0,
            exported_heat_quanta: 0,
        }
    }

    pub(crate) fn physical_parts(self) -> (u128, u128, u128) {
        (
            self.fuel_quanta,
            self.spent_quanta,
            self.exported_heat_quanta,
        )
    }

    pub(crate) fn from_physical_parts(
        anatomy: RecoveryLaneAnatomy,
        fuel_quanta: u128,
        spent_quanta: u128,
        exported_heat_quanta: u128,
    ) -> Result<Self, RecoveryError> {
        let (fuel_capacity, spent_capacity, heat_capacity) = anatomy.capacities();
        if fuel_quanta > fuel_capacity
            || spent_quanta > spent_capacity
            || exported_heat_quanta > heat_capacity
        {
            return Err(RecoveryError::InvalidAnatomy);
        }
        Ok(Self {
            fuel_quanta,
            spent_quanta,
            exported_heat_quanta,
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct RecoveryAnatomy {
    psi_lanes: Box<[RecoveryLaneAnatomy]>,
    gate_lane: RecoveryLaneAnatomy,
    plastic_lane: RecoveryLaneAnatomy,
}

impl RecoveryAnatomy {
    pub(crate) fn new(
        psi_lanes: Vec<RecoveryLaneAnatomy>,
        gate_lane: RecoveryLaneAnatomy,
        plastic_lane: RecoveryLaneAnatomy,
        psi_ring_count: usize,
    ) -> Result<Self, RecoveryError> {
        if psi_lanes.len() != psi_ring_count {
            return Err(RecoveryError::AnatomyWidth);
        }
        Ok(Self {
            psi_lanes: psi_lanes.into_boxed_slice(),
            gate_lane,
            plastic_lane,
        })
    }

    pub(crate) fn lane(&self, address: RecoveryLaneAddress) -> Option<RecoveryLaneAnatomy> {
        match address {
            RecoveryLaneAddress::Psi(index) => self.psi_lanes.get(index).copied(),
            RecoveryLaneAddress::Gate => Some(self.gate_lane),
            RecoveryLaneAddress::Plastic => Some(self.plastic_lane),
        }
    }

    pub(crate) fn psi_lane_count(&self) -> usize {
        self.psi_lanes.len()
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct RecoveryState {
    psi_lanes: Box<[RecoveryLaneState]>,
    gate_lane: RecoveryLaneState,
    plastic_lane: RecoveryLaneState,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum RecoveryLaneAddress {
    Psi(usize),
    Gate,
    Plastic,
}

impl RecoveryState {
    pub(crate) fn new(
        psi_lanes: Vec<RecoveryLaneState>,
        gate_lane: RecoveryLaneState,
        plastic_lane: RecoveryLaneState,
    ) -> Self {
        Self {
            psi_lanes: psi_lanes.into_boxed_slice(),
            gate_lane,
            plastic_lane,
        }
    }

    pub(crate) fn lane(&self, address: RecoveryLaneAddress) -> Option<RecoveryLaneState> {
        match address {
            RecoveryLaneAddress::Psi(index) => self.psi_lanes.get(index).copied(),
            RecoveryLaneAddress::Gate => Some(self.gate_lane),
            RecoveryLaneAddress::Plastic => Some(self.plastic_lane),
        }
    }

    pub(crate) fn replace_lane(
        &mut self,
        address: RecoveryLaneAddress,
        successor: RecoveryLaneState,
    ) -> Result<(), RecoveryError> {
        match address {
            RecoveryLaneAddress::Psi(index) => {
                *self
                    .psi_lanes
                    .get_mut(index)
                    .ok_or(RecoveryError::AnatomyWidth)? = successor;
            }
            RecoveryLaneAddress::Gate => self.gate_lane = successor,
            RecoveryLaneAddress::Plastic => self.plastic_lane = successor,
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum RecoveryError {
    InvalidAnatomy,
    AnatomyWidth,
    ArithmeticWidth,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct DnaExpressionAnatomy {
    catalyst_per_extent: u128,
    substrate_per_extent: u128,
    fuel_per_extent: u128,
    product_per_extent: u128,
    waste_per_extent: u128,
    product_capacity: u128,
    waste_capacity: u128,
}

impl DnaExpressionAnatomy {
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn new(
        catalyst_per_extent: u128,
        substrate_per_extent: u128,
        fuel_per_extent: u128,
        product_per_extent: u128,
        waste_per_extent: u128,
        product_capacity: u128,
        waste_capacity: u128,
    ) -> Result<Self, DnaExpressionError> {
        if catalyst_per_extent == 0
            || substrate_per_extent == 0
            || fuel_per_extent == 0
            || product_per_extent == 0
            || waste_per_extent == 0
            || substrate_per_extent != product_per_extent
            || fuel_per_extent != waste_per_extent
        {
            return Err(DnaExpressionError::InvalidAnatomy);
        }
        Ok(Self {
            catalyst_per_extent,
            substrate_per_extent,
            fuel_per_extent,
            product_per_extent,
            waste_per_extent,
            product_capacity,
            waste_capacity,
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct DnaExpressionState {
    substrate_quanta: u128,
    fuel_quanta: u128,
    expressed_product_quanta: u128,
    waste_quanta: u128,
}

impl DnaExpressionState {
    pub(crate) fn new(substrate_quanta: u128, fuel_quanta: u128) -> Self {
        Self {
            substrate_quanta,
            fuel_quanta,
            expressed_product_quanta: 0,
            waste_quanta: 0,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum DnaExpressionError {
    InvalidAnatomy,
    ArithmeticWidth,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct PlasticSupportAnatomy {
    elastic_energy_scale_zeptojoules: ExactRational,
    yield_stress_zeptojoules: ExactRational,
    closed_coordinate_nanometres: ExactRational,
    open_coordinate_nanometres: ExactRational,
    dissipation_quantum_zeptojoules: ExactRational,
    dissipation_capacity_quanta: u128,
}

impl PlasticSupportAnatomy {
    pub(crate) fn new(
        elastic_energy_scale_zeptojoules: ExactRational,
        yield_stress_zeptojoules: ExactRational,
        closed_coordinate_nanometres: ExactRational,
        open_coordinate_nanometres: ExactRational,
        dissipation_quantum_zeptojoules: ExactRational,
        dissipation_capacity_quanta: u128,
    ) -> Result<Self, PlasticityError> {
        let zero = ExactRational::integer(0);
        if elastic_energy_scale_zeptojoules.checked_cmp(yield_stress_zeptojoules)?
            != core::cmp::Ordering::Greater
            || yield_stress_zeptojoules.checked_cmp(zero)? != core::cmp::Ordering::Greater
            || closed_coordinate_nanometres.checked_cmp(zero)? != core::cmp::Ordering::Greater
            || open_coordinate_nanometres.checked_cmp(zero)? != core::cmp::Ordering::Greater
            || dissipation_quantum_zeptojoules.checked_cmp(zero)? != core::cmp::Ordering::Greater
        {
            return Err(PlasticityError::InvalidAnatomy);
        }
        Ok(Self {
            elastic_energy_scale_zeptojoules,
            yield_stress_zeptojoules,
            closed_coordinate_nanometres,
            open_coordinate_nanometres,
            dissipation_quantum_zeptojoules,
            dissipation_capacity_quanta,
        })
    }

    pub(crate) fn definitive_virtual_material() -> Result<Self, PlasticityError> {
        Self::new(
            ExactRational::integer(2),
            ExactRational::integer(1),
            ExactRational::integer(1),
            ExactRational::integer(2),
            ExactRational::new(3, 4)?,
            1,
        )
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PlasticSupportState {
    rest_length_nanometres: ExactRational,
    dissipated_quanta: u128,
    dissipation_residue_zeptojoules: PhysicalEnergyResidue,
}

impl PlasticSupportState {
    pub(crate) fn new(rest_length_nanometres: ExactRational) -> Result<Self, PlasticityError> {
        if rest_length_nanometres.checked_cmp(ExactRational::integer(0))?
            != core::cmp::Ordering::Greater
        {
            return Err(PlasticityError::InvalidState);
        }
        Ok(Self {
            rest_length_nanometres,
            dissipated_quanta: 0,
            dissipation_residue_zeptojoules: PhysicalEnergyResidue::zero(),
        })
    }
    pub(crate) fn definitive_virtual_genesis() -> Self {
        Self {
            rest_length_nanometres: ExactRational::integer(1),
            dissipated_quanta: 0,
            dissipation_residue_zeptojoules: PhysicalEnergyResidue::zero(),
        }
    }

    pub(crate) fn rest_length_nanometres(&self) -> ExactRational {
        self.rest_length_nanometres
    }

    pub(crate) fn physical_parts(&self) -> (ExactRational, u128, ExactRational) {
        (
            self.rest_length_nanometres,
            self.dissipated_quanta,
            self.dissipation_residue_zeptojoules
                .fixed_width()
                .expect("contact plasticity retains the fixed-width codec"),
        )
    }

    pub(crate) fn from_physical_parts(
        rest_length_nanometres: ExactRational,
        dissipated_quanta: u128,
        dissipation_residue_zeptojoules: ExactRational,
    ) -> Result<Self, PlasticityError> {
        if rest_length_nanometres.checked_cmp(ExactRational::integer(0))?
            != core::cmp::Ordering::Greater
            || dissipation_residue_zeptojoules.parts().0 < 0
        {
            return Err(PlasticityError::InvalidState);
        }
        Ok(Self {
            rest_length_nanometres,
            dissipated_quanta,
            dissipation_residue_zeptojoules: PhysicalEnergyResidue::from_exact_rational(
                dissipation_residue_zeptojoules,
            ),
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum PlasticityError {
    InvalidAnatomy,
    InvalidState,
    DissipationCapacityUnavailable,
    ArithmeticWidth,
}

impl From<ExactRationalError> for PlasticityError {
    fn from(value: ExactRationalError) -> Self {
        match value {
            ExactRationalError::ArithmeticWidth => Self::ArithmeticWidth,
            ExactRationalError::ZeroDenominator | ExactRationalError::NonCanonicalRatio => {
                Self::InvalidState
            }
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum PlasticityAvailability {
    ExecutedExactReturnMapping,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PlasticSettlement {
    pub(crate) successor: PlasticSupportState,
    pub(crate) changed: bool,
}

/// Settle a one-dimensional elastic support against an exact material yield
/// surface. Below yield, the rest geometry is unchanged. Beyond yield, the
/// successor rest length is the exact return-map solution whose stress is
/// exactly `+Y` or `-Y`; the released elastic work enters the mounted finite
/// dissipation reservoir.
fn settle_plastic_support(
    anatomy: &PlasticSupportAnatomy,
    predecessor: &PlasticSupportState,
    gate_population: u128,
    open_population: u128,
) -> Result<PlasticSettlement, PlasticityError> {
    settle_collective_plastic_support(anatomy, predecessor, gate_population, open_population)
}

fn settle_collective_plastic_support(
    anatomy: &PlasticSupportAnatomy,
    predecessor: &PlasticSupportState,
    gate_population: u128,
    open_population: u128,
) -> Result<PlasticSettlement, PlasticityError> {
    if gate_population == 0 || open_population > gate_population {
        return Err(PlasticityError::InvalidState);
    }
    let closed_population = gate_population - open_population;
    let observed_coordinate = anatomy
        .closed_coordinate_nanometres
        .checked_mul_unsigned(closed_population)?
        .checked_add(
            anatomy
                .open_coordinate_nanometres
                .checked_mul_unsigned(open_population)?,
        )?
        .checked_div_unsigned(gate_population)?;
    settle_plastic_support_at_coordinate(anatomy, predecessor, observed_coordinate)
}

pub(crate) fn settle_plastic_support_at_coordinate(
    anatomy: &PlasticSupportAnatomy,
    predecessor: &PlasticSupportState,
    observed_coordinate: ExactRational,
) -> Result<PlasticSettlement, PlasticityError> {
    let big = |value: ExactRational| {
        let (numerator, denominator) = value.parts();
        BigRational::new(BigInt::from(numerator), BigInt::from(denominator))
    };
    settle_plastic_support_at_big_coordinate(anatomy, predecessor, big(observed_coordinate))
}

pub(crate) fn settle_plastic_support_at_big_coordinate(
    anatomy: &PlasticSupportAnatomy,
    predecessor: &PlasticSupportState,
    observed_coordinate: BigRational,
) -> Result<PlasticSettlement, PlasticityError> {
    let big = |value: ExactRational| {
        let (numerator, denominator) = value.parts();
        BigRational::new(BigInt::from(numerator), BigInt::from(denominator))
    };
    let exact = |value: BigRational| -> Result<ExactRational, PlasticityError> {
        ExactRational::new(
            value
                .numer()
                .to_i128()
                .ok_or(PlasticityError::ArithmeticWidth)?,
            value
                .denom()
                .to_u128()
                .ok_or(PlasticityError::ArithmeticWidth)?,
        )
        .map_err(PlasticityError::from)
    };
    let predecessor_rest = big(predecessor.rest_length_nanometres);
    let elastic_scale = big(anatomy.elastic_energy_scale_zeptojoules);
    let yield_stress = big(anatomy.yield_stress_zeptojoules);
    let trial_strain = (&observed_coordinate - &predecessor_rest) / &predecessor_rest;
    let trial_stress = &elastic_scale * &trial_strain;
    if trial_stress.abs() <= yield_stress {
        return Ok(PlasticSettlement {
            successor: predecessor.clone(),
            changed: false,
        });
    }
    let return_denominator = if trial_stress > BigRational::zero() {
        &elastic_scale + &yield_stress
    } else {
        &elastic_scale - &yield_stress
    };
    let next_rest_length = &observed_coordinate * &elastic_scale / return_denominator;
    if next_rest_length <= BigRational::zero() {
        return Err(PlasticityError::InvalidState);
    }
    let returned_strain = (&observed_coordinate - &next_rest_length) / &next_rest_length;
    let returned_stress = &elastic_scale * &returned_strain;
    let expected_stress = if trial_stress > BigRational::zero() {
        yield_stress.clone()
    } else {
        -yield_stress.clone()
    };
    if returned_stress != expected_stress {
        return Err(PlasticityError::ArithmeticWidth);
    }
    let two = BigRational::from_integer(BigInt::from(2));
    let trial_energy = &elastic_scale * &trial_strain * &trial_strain / &two;
    let returned_energy = &elastic_scale * &returned_strain * &returned_strain / two;
    let released_energy = trial_energy - returned_energy;
    let accumulated_release =
        predecessor.dissipation_residue_zeptojoules.energy() + released_energy;
    let released_ratio = &accumulated_release / big(anatomy.dissipation_quantum_zeptojoules);
    if released_ratio < BigRational::zero() {
        return Err(PlasticityError::InvalidState);
    }
    let released_quanta = (released_ratio.numer() / released_ratio.denom())
        .to_u128()
        .ok_or(PlasticityError::ArithmeticWidth)?;
    let successor_residue = accumulated_release
        - big(anatomy.dissipation_quantum_zeptojoules)
            * BigRational::from_integer(BigInt::from(released_quanta));
    let next_dissipated = predecessor
        .dissipated_quanta
        .checked_add(released_quanta)
        .ok_or(PlasticityError::ArithmeticWidth)?;
    if next_dissipated > anatomy.dissipation_capacity_quanta {
        return Err(PlasticityError::DissipationCapacityUnavailable);
    }
    if next_dissipated == anatomy.dissipation_capacity_quanta
        && successor_residue != BigRational::zero()
    {
        return Err(PlasticityError::DissipationCapacityUnavailable);
    }
    Ok(PlasticSettlement {
        successor: PlasticSupportState {
            rest_length_nanometres: exact(next_rest_length)?,
            dissipated_quanta: next_dissipated,
            dissipation_residue_zeptojoules: PhysicalEnergyResidue {
                energy_zeptojoules: successor_residue,
            },
        },
        changed: true,
    })
}

fn support_energy_at(
    anatomy: &PlasticSupportAnatomy,
    coordinate: ExactRational,
    rest_length: ExactRational,
) -> Result<ExactRational, PlasticityError> {
    let strain = coordinate
        .checked_sub(rest_length)?
        .checked_div(rest_length)?;
    anatomy
        .elastic_energy_scale_zeptojoules
        .checked_mul(strain)?
        .checked_mul(strain)?
        .checked_div_unsigned(2)
        .map_err(PlasticityError::from)
}

fn single_channel_yielded_rest_length(
    anatomy: &PlasticSupportAnatomy,
) -> Result<ExactRational, PlasticityError> {
    let trial_strain = anatomy
        .open_coordinate_nanometres
        .checked_sub(anatomy.closed_coordinate_nanometres)?
        .checked_div(anatomy.closed_coordinate_nanometres)?;
    let trial_stress = anatomy
        .elastic_energy_scale_zeptojoules
        .checked_mul(trial_strain)?;
    if trial_stress.checked_cmp(anatomy.yield_stress_zeptojoules)? != core::cmp::Ordering::Greater {
        return Err(PlasticityError::InvalidAnatomy);
    }
    anatomy
        .open_coordinate_nanometres
        .checked_mul(anatomy.elastic_energy_scale_zeptojoules)?
        .checked_div(
            anatomy
                .elastic_energy_scale_zeptojoules
                .checked_add(anatomy.yield_stress_zeptojoules)?,
        )
        .map_err(PlasticityError::from)
}

// Diagnostic decoder for bodies written by the rejected irreversible-prefix
// model.  It is test-only and does not participate in live settlement.
#[cfg(test)]
fn legacy_independent_yielded_population(
    anatomy: &PlasticSupportAnatomy,
    state: &PlasticSupportState,
    gate_population: u128,
) -> Result<u128, PlasticityError> {
    if gate_population == 0 {
        return Err(PlasticityError::InvalidState);
    }
    let yielded_rest = single_channel_yielded_rest_length(anatomy)?;
    let yielded_delta = yielded_rest.checked_sub(anatomy.closed_coordinate_nanometres)?;
    let retained_delta = state
        .rest_length_nanometres
        .checked_sub(anatomy.closed_coordinate_nanometres)?;
    if yielded_delta.parts().0 <= 0 || retained_delta.parts().0 < 0 {
        return Err(PlasticityError::InvalidState);
    }
    let population = retained_delta
        .checked_mul_unsigned(gate_population)?
        .checked_div(yielded_delta)?;
    let (numerator, denominator) = population.parts();
    if denominator != 1 || numerator < 0 {
        return Err(PlasticityError::InvalidState);
    }
    let population = u128::try_from(numerator).map_err(|_| PlasticityError::ArithmeticWidth)?;
    if population > gate_population {
        return Err(PlasticityError::InvalidState);
    }
    Ok(population)
}

#[derive(Clone, Eq, PartialEq)]
pub(crate) struct NeuronPhysicalState(Arc<NeuronPhysicalStateBody>);

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct NeuronPhysicalStateBody {
    pub(crate) psi: PsiKrimelackState,
    pub(crate) gate: TwoStateGateState,
    pub(crate) membrane: LocalMembraneConductanceState<1>,
    pub(crate) carriers: CarrierReservoirs,
    pub(crate) recovery: RecoveryState,
    pub(crate) dna_expression: DnaExpressionState,
    pub(crate) plastic: PlasticSupportState,
    /// Retained local gate-work residue. For a receptor cell this is the
    /// exact-rational remainder of its continuous transduced-energy integral
    /// — `2·L·T` for light, `K·∫s²dt` for sound — not yet delivered on the
    /// receiving gate's own dissipation lattice. For an intrinsic cell it may
    /// also retain exact local fluid work whose reaction was catalysed by real
    /// incident contact carriers. Both sources use this ONE physical energy
    /// accumulator and the same gate-energy lattice; no second eligibility,
    /// reward, or semantic state exists. Same retained-residue discipline as
    /// the charge-carrier phases.
    ///
    /// BOUND (re-measured 2026-08-06; the previous comment here claimed
    /// `[0, gate dissipation quantum)` and was STALE — it described the law
    /// before threshold-integrated delivery was ratified): the residue is
    /// non-negative, and under threshold-integrated delivery it lawfully
    /// holds up to `opening_threshold_quanta − 1` whole quanta plus a
    /// sub-quantum remainder, because nothing is delivered at all until the
    /// accumulation reaches the receiving gate's own opening threshold.  For
    /// a genesis receptor site (quantum 1/16 zJ, threshold 17 quanta) that
    /// bound is strictly under 17/16 zJ.  Non-negativity is enforced at the
    /// codec boundary; the upper bound is a consequence of the delivery law,
    /// not a clamp.
    pub(crate) receptor_quantum_residue: ExactRational,
    /// Inert legacy membrane-return residue retained only so GLNPS01-04 bodies
    /// cold-restore byte-exactly.  The fabricated zero-voltage return and its
    /// quantized billing law are deleted; current pump settlement neither
    /// reads nor writes this value.  New states keep it at zero.  A later
    /// authenticated state-format migration may remove the bytes, but runtime
    /// physics must never resurrect them as energy or gradient authority.
    pub(crate) membrane_return_work_residue: ExactRational,
}

impl NeuronPhysicalState {
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn new(
        psi: PsiKrimelackState,
        gate: TwoStateGateState,
        membrane: LocalMembraneConductanceState<1>,
        carriers: CarrierReservoirs,
        recovery: RecoveryState,
        dna_expression: DnaExpressionState,
        plastic: PlasticSupportState,
        receptor_quantum_residue: ExactRational,
        membrane_return_work_residue: ExactRational,
    ) -> Self {
        Self(Arc::new(NeuronPhysicalStateBody {
            psi,
            gate,
            membrane,
            carriers,
            recovery,
            dna_expression,
            plastic,
            receptor_quantum_residue,
            membrane_return_work_residue,
        }))
    }

    pub(crate) fn shares_physical_body_with(&self, other: &Self) -> bool {
        Arc::ptr_eq(&self.0, &other.0)
    }
}

impl Deref for NeuronPhysicalState {
    type Target = NeuronPhysicalStateBody;

    fn deref(&self) -> &Self::Target {
        self.0.as_ref()
    }
}

impl DerefMut for NeuronPhysicalState {
    fn deref_mut(&mut self) -> &mut Self::Target {
        Arc::make_mut(&mut self.0)
    }
}

impl fmt::Debug for NeuronPhysicalState {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("NeuronPhysicalState")
            .field("psi", &self.psi)
            .field("gate", &self.gate)
            .field("membrane", &self.membrane)
            .field("carriers", &self.carriers)
            .field("recovery", &self.recovery)
            .field("dna_expression", &self.dna_expression)
            .field("plastic", &self.plastic)
            .field("receptor_quantum_residue", &self.receptor_quantum_residue)
            .field(
                "membrane_return_work_residue",
                &self.membrane_return_work_residue,
            )
            .finish()
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct NeuronPhysicalAnatomy {
    mathloom: MathLoomAnatomy,
    psi: PsiKrimelackAnatomy,
    gate: TwoStateGateAnatomy,
    capacitance: MembraneCapacitance,
    recovery: RecoveryAnatomy,
    dna_expression: DnaExpressionAnatomy,
    plastic: PlasticSupportAnatomy,
}

impl NeuronPhysicalAnatomy {
    pub(crate) fn new(
        mathloom: MathLoomAnatomy,
        psi: PsiKrimelackAnatomy,
        gate: TwoStateGateAnatomy,
        capacitance: MembraneCapacitance,
        recovery: RecoveryAnatomy,
        dna_expression: DnaExpressionAnatomy,
        plastic: PlasticSupportAnatomy,
    ) -> Result<Self, NeuronPhysicalError> {
        if psi.positions != mathloom.positions() {
            return Err(NeuronPhysicalError::AnatomyMismatch);
        }
        if recovery.psi_lanes.len() != psi.ring_count() {
            return Err(NeuronPhysicalError::AnatomyMismatch);
        }
        Ok(Self {
            mathloom,
            psi,
            gate,
            capacitance,
            recovery,
            dna_expression,
            plastic,
        })
    }

    pub(crate) fn capacitance(&self) -> MembraneCapacitance {
        self.capacitance
    }

    pub(crate) fn prepare_psi_settlement(
        &self,
        predecessor: &NeuronPhysicalState,
        perspective: JointNeuronPerspective<'_>,
    ) -> Result<PsiSettlement, NeuronPhysicalError> {
        let mathloom = settle_shared_dsf_mathloom(perspective, self.mathloom)?;
        settle_psi_krimelack(&self.psi, &predecessor.psi, &mathloom).map_err(Into::into)
    }

    pub(crate) fn mathloom_positions(&self) -> usize {
        self.mathloom.positions()
    }

    pub(crate) fn prepare_mathloom_delivery<'a>(
        &self,
        perspective: JointNeuronPerspective<'a>,
    ) -> Result<BorrowedMathLoomDelivery<'a>, NeuronPhysicalError> {
        settle_shared_dsf_mathloom(perspective, self.mathloom).map_err(Into::into)
    }

    pub(crate) fn prepare_psi_settlement_from_delivery(
        &self,
        predecessor: &NeuronPhysicalState,
        delivery: &BorrowedMathLoomDelivery<'_>,
    ) -> Result<PsiSettlement, NeuronPhysicalError> {
        settle_psi_krimelack(&self.psi, &predecessor.psi, delivery).map_err(Into::into)
    }

    /// The same anatomy carrying a different membrane capacitance.
    ///
    /// Since the 2026-08-05 geometric-differentiation ratification the
    /// capacitance is the ONLY part of a cohort sibling's authored anatomy
    /// that its own declared place changes; everything else (the whole Psi
    /// lattice, gate, recovery, DNA and plastic anatomy) is shared.  Retention
    /// layers use this to content-address the shared portion once and carry
    /// each member's own derived capacitance beside its reference, so
    /// differentiation costs 32 bytes a member instead of a whole duplicated
    /// anatomy blob.
    pub(crate) fn with_capacitance(&self, capacitance: MembraneCapacitance) -> Self {
        Self {
            capacitance,
            ..self.clone()
        }
    }

    pub(crate) fn recovery_anatomy(&self) -> &RecoveryAnatomy {
        &self.recovery
    }

    pub(crate) fn gate_dissipation_capacity_quanta(&self) -> u128 {
        self.gate.dissipation_capacity_quanta()
    }

    pub(crate) fn gate_population(&self) -> u128 {
        self.gate.population()
    }

    pub(crate) fn gate_support_coordinate_nanometres(
        &self,
        state: &NeuronPhysicalState,
    ) -> Result<ExactRational, NeuronPhysicalError> {
        if self.gate.population == 0 || state.gate.open_population > self.gate.population {
            return Err(NeuronPhysicalError::AnatomyMismatch);
        }
        self.plastic
            .closed_coordinate_nanometres
            .checked_mul_unsigned(self.gate.population - state.gate.open_population)?
            .checked_add(
                self.plastic
                    .open_coordinate_nanometres
                    .checked_mul_unsigned(state.gate.open_population)?,
            )?
            .checked_div_unsigned(self.gate.population)
            .map_err(Into::into)
    }

    /// The receiving gate's exact dissipation-lattice step. Quantized optical
    /// delivery derives its whole-quantum count from THIS anatomy value; no
    /// new constant is introduced anywhere.
    pub(crate) fn gate_dissipation_quantum_zeptojoules(&self) -> &Exact {
        &self.gate.dissipation_quantum_zeptojoules
    }

    pub(crate) fn gate_dissipation_quantum_exact_zeptojoules(
        &self,
    ) -> Result<ExactRational, NeuronPhysicalError> {
        exact_to_rational(&self.gate.dissipation_quantum_zeptojoules)
    }

    pub(crate) fn gate_single_channel_conductance_picosiemens(&self) -> ExactRational {
        self.gate.single_channel_conductance_picosiemens
    }

    pub(crate) fn gate_reversal_potential_millivolts(&self) -> ExactRational {
        self.gate.reversal_potential_millivolts
    }

    /// Maximum phase-one powered-contact rate for this mounted pump, in exact
    /// zeptojoules per microsecond.  It is the existing one-channel electrical
    /// power g*E_rev^2 with the exact pS/mV/us unit conversion; no demand,
    /// scheduler cadence, host power, or refill target enters the value.
    pub(crate) fn pump_contact_power_zeptojoules_per_microsecond(
        &self,
    ) -> Result<ExactRational, NeuronPhysicalError> {
        self.gate
            .single_channel_conductance_picosiemens
            .checked_mul(self.gate.reversal_potential_millivolts)?
            .checked_mul(self.gate.reversal_potential_millivolts)?
            .checked_div_unsigned(1_000)
            .map_err(Into::into)
    }

    pub(crate) fn recovery_full_saturation_requirement(
        &self,
        address: RecoveryLaneAddress,
    ) -> Result<RecoverySaturationRequirement, NeuronPhysicalError> {
        let lane = self
            .recovery
            .lane(address)
            .ok_or(RecoveryError::AnatomyWidth)?;
        let dissipation_capacity = match address {
            RecoveryLaneAddress::Psi(index) => {
                self.psi
                    .rings
                    .get(index)
                    .ok_or(RecoveryError::AnatomyWidth)?
                    .dissipation_capacity_quanta
            }
            RecoveryLaneAddress::Gate => self.gate.dissipation_capacity_quanta,
            RecoveryLaneAddress::Plastic => self.plastic.dissipation_capacity_quanta,
        };
        let (catalyst_per_extent, fuel_per_extent, spent_per_extent, heat_per_extent) =
            lane.stoichiometry();
        if dissipation_capacity % heat_per_extent != 0 {
            return Err(RecoveryError::InvalidAnatomy.into());
        }
        let extents = dissipation_capacity / heat_per_extent;
        Ok(RecoverySaturationRequirement {
            catalyst_quanta: extents
                .checked_mul(catalyst_per_extent)
                .ok_or(RecoveryError::ArithmeticWidth)?,
            fuel_quanta: extents
                .checked_mul(fuel_per_extent)
                .ok_or(RecoveryError::ArithmeticWidth)?,
            spent_quanta: extents
                .checked_mul(spent_per_extent)
                .ok_or(RecoveryError::ArithmeticWidth)?,
            heat_quanta: extents
                .checked_mul(heat_per_extent)
                .ok_or(RecoveryError::ArithmeticWidth)?,
        })
    }

    /// Exact body-energy carried by one complete recovery-reaction extent at
    /// this neuron's named local lane. Local lane state remains integer
    /// material counts; only a mounted body reservoir translates those counts
    /// into their common zeptojoule dimension.
    pub(crate) fn recovery_energy_per_extent_zeptojoules(
        &self,
        address: RecoveryLaneAddress,
    ) -> Result<ExactRational, NeuronPhysicalError> {
        let lane = self
            .recovery
            .lane(address)
            .ok_or(RecoveryError::AnatomyWidth)?;
        let heat_per_extent = lane.stoichiometry().3;
        self.lane_dissipation_quantum_zeptojoules(address)?
            .checked_mul_unsigned(heat_per_extent)
            .map_err(Into::into)
    }

    pub(crate) fn lane_dissipation_quantum_zeptojoules(
        &self,
        address: RecoveryLaneAddress,
    ) -> Result<ExactRational, NeuronPhysicalError> {
        Ok(match address {
            RecoveryLaneAddress::Psi(index) => exact_to_rational(
                &self
                    .psi
                    .rings
                    .get(index)
                    .ok_or(RecoveryError::AnatomyWidth)?
                    .dissipation_quantum_zeptojoules,
            )?,
            RecoveryLaneAddress::Gate => {
                exact_to_rational(&self.gate.dissipation_quantum_zeptojoules)?
            }
            RecoveryLaneAddress::Plastic => self.plastic.dissipation_quantum_zeptojoules,
        })
    }

    pub(crate) fn psi_ring_count(&self) -> usize {
        self.psi.ring_count()
    }

    pub(crate) fn sparse_delta_coordinate_count(&self) -> Option<usize> {
        self.psi.ring_count().checked_mul(5)?.checked_add(20)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct RecoverySaturationRequirement {
    pub(crate) catalyst_quanta: u128,
    pub(crate) fuel_quanta: u128,
    pub(crate) spent_quanta: u128,
    pub(crate) heat_quanta: u128,
}

impl NeuronPhysicalState {
    pub(crate) fn psi_state(&self) -> &PsiKrimelackState {
        &self.psi
    }

    #[cfg(test)]
    pub(crate) fn probe_gate_open_population(&self) -> u128 {
        self.gate.open_population
    }

    pub(crate) fn membrane_state(
        &self,
    ) -> crate::elementary_charge_membrane::ElementaryChargeMembraneState {
        self.membrane.membrane()
    }

    pub(crate) fn carrier_reservoirs(&self) -> CarrierReservoirs {
        self.carriers
    }

    pub(crate) fn resident_bytes(&self) -> Option<usize> {
        core::mem::size_of::<NeuronPhysicalStateBody>()
            .checked_add(
                self.psi
                    .rings
                    .len()
                    .checked_mul(core::mem::size_of::<PsiRingState>())?,
            )?
            .checked_add(
                self.recovery
                    .psi_lanes
                    .len()
                    .checked_mul(core::mem::size_of::<RecoveryLaneState>())?,
            )?
            .checked_add(self.gate.dissipation_residue_zeptojoules.heap_bytes()?)?
            .checked_add(self.plastic.dissipation_residue_zeptojoules.heap_bytes()?)
    }
}

#[cfg(test)]
impl NeuronPhysicalState {
    pub(crate) fn probe_retention_material(
        &self,
    ) -> ((u128, u128, u128), (u128, u128, u128, u128)) {
        (
            self.recovery.plastic_lane.physical_parts(),
            self.dna_expression.probe_parts(),
        )
    }
}

/// Extend only the positional MathLoom/Psi fabric reached by a field whose
/// exact balanced-ternary word is wider than this neuron's present anatomy.
/// Existing rings keep their exact block-relative positions. New high
/// positions repeat the same local ring and recovery anatomy and begin in that
/// anatomy's rest state; every other neuronal coordinate is unchanged.
pub(crate) fn extend_neuron_positional_fabric(
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
    required_positions: usize,
) -> Result<(NeuronPhysicalAnatomy, NeuronPhysicalState), NeuronPhysicalError> {
    let mounted_positions = anatomy.mathloom.positions();
    if required_positions <= mounted_positions {
        return Ok((anatomy.clone(), state.clone()));
    }
    if state.psi.rings.len() != anatomy.psi.rings.len()
        || state.recovery.psi_lanes.len() != anatomy.recovery.psi_lanes.len()
    {
        return Err(NeuronPhysicalError::AnatomyMismatch);
    }
    let block_count = anatomy
        .psi
        .constraint_count
        .checked_mul(2)
        .ok_or(PsiSettlementError::AnatomyWidth)?;
    let added_positions = required_positions
        .checked_sub(mounted_positions)
        .ok_or(PsiSettlementError::AnatomyWidth)?;
    let successor_ring_count = block_count
        .checked_mul(required_positions)
        .ok_or(PsiSettlementError::AnatomyWidth)?;
    let mut rings = Vec::with_capacity(successor_ring_count);
    let mut ring_states = Vec::with_capacity(successor_ring_count);
    let mut recovery_lanes = Vec::with_capacity(successor_ring_count);
    let mut recovery_states = Vec::with_capacity(successor_ring_count);
    for block in 0..block_count {
        let start = block
            .checked_mul(mounted_positions)
            .ok_or(PsiSettlementError::AnatomyWidth)?;
        let end = start
            .checked_add(mounted_positions)
            .ok_or(PsiSettlementError::AnatomyWidth)?;
        rings.extend_from_slice(&anatomy.psi.rings[start..end]);
        ring_states.extend_from_slice(&state.psi.rings[start..end]);
        recovery_lanes.extend_from_slice(&anatomy.recovery.psi_lanes[start..end]);
        recovery_states.extend_from_slice(&state.recovery.psi_lanes[start..end]);
        let ring_template = anatomy.psi.rings[end - 1].clone();
        let recovery_template = anatomy.recovery.psi_lanes[end - 1];
        for _ in 0..added_positions {
            rings.push(ring_template.clone());
            ring_states.push(PsiRingState {
                amplitude_quanta: ring_template.node_amplitude_quanta,
                phase_thirds: canonical_phase_thirds(ring_template.genesis_winding),
                winding: ring_template.genesis_winding,
                dissipated_quanta: 0,
            });
            recovery_lanes.push(recovery_template);
            recovery_states.push(RecoveryLaneState::new(recovery_template.fuel_capacity));
        }
    }
    let psi = PsiKrimelackAnatomy::new(required_positions, anatomy.psi.constraint_count, rings)?;
    let recovery = RecoveryAnatomy::new(
        recovery_lanes,
        anatomy.recovery.gate_lane,
        anatomy.recovery.plastic_lane,
        successor_ring_count,
    )?;
    let successor_anatomy = NeuronPhysicalAnatomy::new(
        MathLoomAnatomy::new(required_positions)?,
        psi,
        anatomy.gate.clone(),
        anatomy.capacitance,
        recovery,
        anatomy.dna_expression,
        anatomy.plastic.clone(),
    )?;
    let mut successor_state = state.clone();
    successor_state.psi = PsiKrimelackState {
        rings: ring_states.into_boxed_slice(),
    };
    successor_state.recovery = RecoveryState {
        psi_lanes: recovery_states.into_boxed_slice(),
        gate_lane: state.recovery.gate_lane,
        plastic_lane: state.recovery.plastic_lane,
    };
    Ok((successor_anatomy, successor_state))
}

/// One-way correction for retinal population anatomy. A one-channel legacy
/// cell keeps its exact lived state while omitted territory is added as virgin
/// material. An already-expanded cell authored by the retired unbounded-work
/// law instead passes through the narrower false-physiology retirement below.
pub(crate) fn expand_legacy_receptor_channel_population(
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
    target_population: u128,
    virgin_carriers_per_compartment: u128,
) -> Result<(NeuronPhysicalAnatomy, NeuronPhysicalState), NeuronPhysicalError> {
    if target_population == anatomy.gate.population {
        if target_population == 1
            || (anatomy.gate.has_independent_channel_supports()
                && anatomy.gate.has_occurrence_bounded_population_work())
        {
            return Ok((anatomy.clone(), state.clone()));
        }
        if anatomy.gate.has_independent_channel_supports() {
            return retire_unbounded_receptor_population_state(
                anatomy,
                state,
                virgin_carriers_per_compartment,
            );
        }
        return Err(NeuronPhysicalError::AnatomyMismatch);
    }
    if anatomy.gate.population != 1
        || anatomy.gate.has_independent_channel_supports()
        || target_population <= 1
        || state.gate.open_population > 1
    {
        return Err(NeuronPhysicalError::AnatomyMismatch);
    }

    let scale = target_population;
    let scaled = |value: u128| {
        value.checked_mul(scale).ok_or(NeuronPhysicalError::Gate(
            GateSettlementError::ArithmeticWidth,
        ))
    };
    let gate = TwoStateGateAnatomy::new_independent_channels(
        target_population,
        anatomy.gate.gating_charge_elementary,
        anatomy.gate.chemical_open_minus_closed_zeptojoules.clone(),
        anatomy.gate.dissipation_quantum_zeptojoules.clone(),
        scaled(anatomy.gate.dissipation_capacity_quanta)?,
        anatomy.gate.single_channel_conductance_picosiemens,
        anatomy.gate.reversal_potential_millivolts,
        anatomy.gate.psi_contacts.to_vec(),
        anatomy.psi.ring_count(),
    )?;

    let scale_lane =
        |lane: RecoveryLaneAnatomy| -> Result<RecoveryLaneAnatomy, NeuronPhysicalError> {
            let (catalyst, fuel, spent, heat) = lane.stoichiometry();
            let (fuel_capacity, spent_capacity, heat_capacity) = lane.capacities();
            RecoveryLaneAnatomy::new(
                catalyst,
                fuel,
                spent,
                heat,
                scaled(fuel_capacity)?,
                scaled(spent_capacity)?,
                scaled(heat_capacity)?,
            )
            .map_err(Into::into)
        };
    let gate_lane = scale_lane(anatomy.recovery.gate_lane)?;
    let plastic_lane = scale_lane(anatomy.recovery.plastic_lane)?;
    let recovery = RecoveryAnatomy::new(
        anatomy.recovery.psi_lanes.to_vec(),
        gate_lane,
        plastic_lane,
        anatomy.psi.ring_count(),
    )?;
    let plastic = PlasticSupportAnatomy::new(
        anatomy.plastic.elastic_energy_scale_zeptojoules,
        anatomy.plastic.yield_stress_zeptojoules,
        anatomy.plastic.closed_coordinate_nanometres,
        anatomy.plastic.open_coordinate_nanometres,
        anatomy.plastic.dissipation_quantum_zeptojoules,
        scaled(anatomy.plastic.dissipation_capacity_quanta)?,
    )?;

    let successor_anatomy = NeuronPhysicalAnatomy::new(
        anatomy.mathloom,
        anatomy.psi.clone(),
        gate,
        anatomy.capacitance,
        recovery,
        anatomy.dna_expression,
        plastic,
    )?;

    let yielded_rest = single_channel_yielded_rest_length(&anatomy.plastic)?;
    let yielded_population =
        if state.plastic.rest_length_nanometres == anatomy.plastic.closed_coordinate_nanometres {
            0
        } else if state.plastic.rest_length_nanometres == yielded_rest {
            1
        } else {
            return Err(NeuronPhysicalError::Plasticity(
                PlasticityError::InvalidState,
            ));
        };
    let retained_delta = yielded_rest.checked_sub(anatomy.plastic.closed_coordinate_nanometres)?;
    let successor_rest = anatomy.plastic.closed_coordinate_nanometres.checked_add(
        retained_delta
            .checked_mul_unsigned(yielded_population)?
            .checked_div_unsigned(target_population)?,
    )?;

    let added_channels = target_population - 1;
    let added_carriers = virgin_carriers_per_compartment
        .checked_mul(added_channels)
        .ok_or(NeuronPhysicalError::Gate(
            GateSettlementError::ArithmeticWidth,
        ))?;

    let expand_lane_state = |predecessor: RecoveryLaneState,
                             predecessor_anatomy: RecoveryLaneAnatomy,
                             successor_anatomy: RecoveryLaneAnatomy|
     -> Result<RecoveryLaneState, NeuronPhysicalError> {
        let (fuel, spent, heat) = predecessor.physical_parts();
        let (old_fuel_capacity, _, _) = predecessor_anatomy.capacities();
        let (new_fuel_capacity, _, _) = successor_anatomy.capacities();
        RecoveryLaneState::from_physical_parts(
            successor_anatomy,
            fuel.checked_add(new_fuel_capacity - old_fuel_capacity)
                .ok_or(RecoveryError::ArithmeticWidth)?,
            spent,
            heat,
        )
        .map_err(Into::into)
    };
    let mut successor_state = state.clone();
    successor_state.carriers = CarrierReservoirs::new(
        state
            .carriers
            .intracellular
            .checked_add(added_carriers)
            .ok_or(NeuronPhysicalError::Gate(
                GateSettlementError::ArithmeticWidth,
            ))?,
        state
            .carriers
            .extracellular
            .checked_add(added_carriers)
            .ok_or(NeuronPhysicalError::Gate(
                GateSettlementError::ArithmeticWidth,
            ))?,
    );
    successor_state.recovery.gate_lane = expand_lane_state(
        state.recovery.gate_lane,
        anatomy.recovery.gate_lane,
        successor_anatomy.recovery.gate_lane,
    )?;
    successor_state.recovery.plastic_lane = expand_lane_state(
        state.recovery.plastic_lane,
        anatomy.recovery.plastic_lane,
        successor_anatomy.recovery.plastic_lane,
    )?;
    successor_state.plastic = PlasticSupportState {
        rest_length_nanometres: successor_rest,
        dissipated_quanta: state.plastic.dissipated_quanta,
        dissipation_residue_zeptojoules: state.plastic.dissipation_residue_zeptojoules.clone(),
    };
    encode_neuron_physical_state(&successor_anatomy, &successor_state)
        .map_err(|_| NeuronPhysicalError::AnatomyMismatch)?;
    Ok((successor_anatomy, successor_state))
}

/// Add an exact quantity of virgin carrier material omitted by an older birth
/// law to both local compartments. This is neither a pump nor inference: the
/// caller must prove the omitted amount and whole-organism idempotence before
/// invoking it.
pub(crate) fn add_omitted_virgin_carrier_material(
    state: &NeuronPhysicalState,
    per_compartment: u128,
) -> Result<NeuronPhysicalState, NeuronPhysicalError> {
    if per_compartment == 0 {
        return Ok(state.clone());
    }
    let mut successor = state.clone();
    successor.carriers = CarrierReservoirs::new(
        state
            .carriers
            .intracellular
            .checked_add(per_compartment)
            .ok_or(GateSettlementError::ArithmeticWidth)?,
        state
            .carriers
            .extracellular
            .checked_add(per_compartment)
            .ok_or(GateSettlementError::ArithmeticWidth)?,
    );
    Ok(successor)
}

/// Retire retinal physiology produced by the former cross-occurrence energy
/// accumulator.  That law could progressively yield every support even when
/// no single occurrence paid for that state, so its gate, membrane, carrier,
/// plastic, recovery and optical-residue coordinates are not lived evidence.
/// Stable Psi/Krimelack state, its recovery lanes, DNA state, topology and
/// lineage remain exact.  The anatomy marker makes this correction one-way.
fn retire_unbounded_receptor_population_state(
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
    virgin_carriers_per_compartment: u128,
) -> Result<(NeuronPhysicalAnatomy, NeuronPhysicalState), NeuronPhysicalError> {
    if !anatomy.gate.has_independent_channel_supports()
        || anatomy.gate.has_occurrence_bounded_population_work()
        || anatomy.gate.population <= 1
        || virgin_carriers_per_compartment == 0
    {
        return Err(NeuronPhysicalError::AnatomyMismatch);
    }
    let mut successor_anatomy = anatomy.clone();
    successor_anatomy.gate.occurrence_bounded_population_work = true;
    let carriers_per_compartment = virgin_carriers_per_compartment
        .checked_mul(anatomy.gate.population)
        .ok_or(NeuronPhysicalError::Gate(
            GateSettlementError::ArithmeticWidth,
        ))?;
    let (gate_fuel_capacity, _, _) = anatomy.recovery.gate_lane.capacities();
    let (plastic_fuel_capacity, _, _) = anatomy.recovery.plastic_lane.capacities();
    let mut successor_state = state.clone();
    successor_state.gate = TwoStateGateState::genesis(0);
    successor_state.membrane = LocalMembraneConductanceState::genesis(0);
    successor_state.carriers =
        CarrierReservoirs::new(carriers_per_compartment, carriers_per_compartment);
    successor_state.recovery.gate_lane = RecoveryLaneState::new(gate_fuel_capacity);
    successor_state.recovery.plastic_lane = RecoveryLaneState::new(plastic_fuel_capacity);
    successor_state.plastic =
        PlasticSupportState::new(anatomy.plastic.closed_coordinate_nanometres)?;
    successor_state.receptor_quantum_residue = ExactRational::integer(0);
    successor_state.membrane_return_work_residue = ExactRational::integer(0);
    encode_neuron_physical_state(&successor_anatomy, &successor_state)
        .map_err(|_| NeuronPhysicalError::AnatomyMismatch)?;
    Ok((successor_anatomy, successor_state))
}

const NEURON_ANATOMY_CODEC_MAGIC: &[u8; 8] = b"GLNPA02\0";
const NEURON_INDEPENDENT_CHANNEL_ANATOMY_CODEC_MAGIC: &[u8; 8] = b"GLNPA03\0";
const NEURON_OCCURRENCE_BOUNDED_CHANNEL_ANATOMY_CODEC_MAGIC: &[u8; 8] = b"GLNPA04\0";
const NEURON_CELL_CODEC_MAGIC: &[u8; 8] = b"GLNPC02\0";
const MIN_PSI_RING_ANATOMY_BYTES: usize = 164;
const MIN_GATE_PSI_CONTACT_BYTES: usize = 35;
const RECOVERY_LANE_ANATOMY_BYTES: usize = 112;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum NeuronAnatomyCodecError {
    InvalidEncoding,
    InvalidAnatomy,
    ArithmeticWidth,
    State(NeuronStateCodecError),
}

impl From<NeuronStateCodecError> for NeuronAnatomyCodecError {
    fn from(value: NeuronStateCodecError) -> Self {
        Self::State(value)
    }
}

/// Encode immutable physical anatomy exactly. This carrier chooses no anatomy
/// and derives no coefficients; it only makes already-admitted anatomy
/// restartable with the neuron that uses it.
pub(crate) fn encode_neuron_physical_anatomy(
    anatomy: &NeuronPhysicalAnatomy,
) -> Result<Vec<u8>, NeuronAnatomyCodecError> {
    let mut encoded = Vec::new();
    encoded.extend_from_slice(if anatomy.gate.has_occurrence_bounded_population_work() {
        NEURON_OCCURRENCE_BOUNDED_CHANNEL_ANATOMY_CODEC_MAGIC
    } else if anatomy.gate.has_independent_channel_supports() {
        NEURON_INDEPENDENT_CHANNEL_ANATOMY_CODEC_MAGIC
    } else {
        NEURON_ANATOMY_CODEC_MAGIC
    });
    push_anatomy_usize(&mut encoded, anatomy.mathloom.positions())?;
    push_anatomy_usize(&mut encoded, anatomy.psi.constraint_count)?;
    push_anatomy_usize(&mut encoded, anatomy.psi.rings.len())?;
    for ring in &anatomy.psi.rings {
        for value in ring.node_amplitude_quanta {
            encoded.extend_from_slice(&value.to_le_bytes());
        }
        for value in &ring.rest_energy_zeptojoules {
            push_big_rational(&mut encoded, value)?;
        }
        push_big_rational(&mut encoded, &ring.dsf_coupling_zeptojoules)?;
        push_big_rational(&mut encoded, &ring.dissipation_quantum_zeptojoules)?;
        encoded.extend_from_slice(&ring.dissipation_capacity_quanta.to_le_bytes());
        for row in ring.reachable {
            for value in row {
                encoded.push(u8::from(value));
            }
        }
        encoded.push(ring.genesis_winding as i8 as u8);
    }

    encoded.extend_from_slice(&anatomy.gate.population.to_le_bytes());
    encoded.extend_from_slice(&anatomy.gate.gating_charge_elementary.to_le_bytes());
    push_big_rational(
        &mut encoded,
        &anatomy.gate.chemical_open_minus_closed_zeptojoules,
    )?;
    push_big_rational(&mut encoded, &anatomy.gate.dissipation_quantum_zeptojoules)?;
    encoded.extend_from_slice(&anatomy.gate.dissipation_capacity_quanta.to_le_bytes());
    push_exact_rational(
        &mut encoded,
        anatomy.gate.single_channel_conductance_picosiemens,
    );
    push_exact_rational(&mut encoded, anatomy.gate.reversal_potential_millivolts);
    push_anatomy_usize(&mut encoded, anatomy.gate.psi_contacts.len())?;
    for contact in &anatomy.gate.psi_contacts {
        push_anatomy_usize(&mut encoded, contact.ring_index)?;
        push_anatomy_usize(&mut encoded, contact.node_index)?;
        encoded.push(contact.preferred_phase_third as u8);
        push_big_rational(
            &mut encoded,
            &contact.open_minus_closed_coupling_zeptojoules,
        )?;
    }
    push_exact_rational(&mut encoded, anatomy.capacitance.picofarads());

    push_anatomy_usize(&mut encoded, anatomy.recovery.psi_lanes.len())?;
    for lane in &anatomy.recovery.psi_lanes {
        push_recovery_lane_anatomy(&mut encoded, *lane);
    }
    push_recovery_lane_anatomy(&mut encoded, anatomy.recovery.gate_lane);
    push_recovery_lane_anatomy(&mut encoded, anatomy.recovery.plastic_lane);

    for value in [
        anatomy.dna_expression.catalyst_per_extent,
        anatomy.dna_expression.substrate_per_extent,
        anatomy.dna_expression.fuel_per_extent,
        anatomy.dna_expression.product_per_extent,
        anatomy.dna_expression.waste_per_extent,
        anatomy.dna_expression.product_capacity,
        anatomy.dna_expression.waste_capacity,
    ] {
        encoded.extend_from_slice(&value.to_le_bytes());
    }
    for value in [
        anatomy.plastic.elastic_energy_scale_zeptojoules,
        anatomy.plastic.yield_stress_zeptojoules,
        anatomy.plastic.closed_coordinate_nanometres,
        anatomy.plastic.open_coordinate_nanometres,
        anatomy.plastic.dissipation_quantum_zeptojoules,
    ] {
        push_exact_rational(&mut encoded, value);
    }
    encoded.extend_from_slice(&anatomy.plastic.dissipation_capacity_quanta.to_le_bytes());
    Ok(encoded)
}

pub(crate) fn decode_neuron_physical_anatomy(
    encoded: &[u8],
) -> Result<NeuronPhysicalAnatomy, NeuronAnatomyCodecError> {
    let mut reader = NeuronAnatomyReader::new(encoded);
    let (independent_channel_supports, occurrence_bounded_population_work) =
        match reader.take(NEURON_ANATOMY_CODEC_MAGIC.len())? {
            magic if magic == NEURON_ANATOMY_CODEC_MAGIC => (false, false),
            magic if magic == NEURON_INDEPENDENT_CHANNEL_ANATOMY_CODEC_MAGIC => (true, false),
            magic if magic == NEURON_OCCURRENCE_BOUNDED_CHANNEL_ANATOMY_CODEC_MAGIC => (true, true),
            _ => return Err(NeuronAnatomyCodecError::InvalidEncoding),
        };
    let positions = reader.usize()?;
    let constraint_count = reader.usize()?;
    let ring_count = reader.usize()?;
    let required_rings = constraint_count
        .checked_mul(2)
        .and_then(|value| value.checked_mul(positions))
        .ok_or(NeuronAnatomyCodecError::ArithmeticWidth)?;
    if positions == 0 || ring_count != required_rings {
        return Err(NeuronAnatomyCodecError::InvalidAnatomy);
    }
    reader.require_records(ring_count, MIN_PSI_RING_ANATOMY_BYTES)?;
    let mut rings = Vec::new();
    rings
        .try_reserve_exact(ring_count)
        .map_err(|_| NeuronAnatomyCodecError::ArithmeticWidth)?;
    for _ in 0..ring_count {
        let node_amplitude_quanta = [reader.u128()?, reader.u128()?, reader.u128()?];
        let rest_energy_zeptojoules = [
            reader.big_rational()?,
            reader.big_rational()?,
            reader.big_rational()?,
        ];
        let dsf_coupling_zeptojoules = reader.big_rational()?;
        let dissipation_quantum_zeptojoules = reader.big_rational()?;
        let dissipation_capacity_quanta = reader.u128()?;
        let mut reachable = [[false; 3]; 3];
        for row in &mut reachable {
            for value in row {
                *value = reader.boolean()?;
            }
        }
        let genesis_winding =
            decode_winding(reader.i8()?).map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;
        rings.push(
            PsiRingAnatomy::new(
                node_amplitude_quanta,
                rest_energy_zeptojoules,
                dsf_coupling_zeptojoules,
                dissipation_quantum_zeptojoules,
                dissipation_capacity_quanta,
                reachable,
                genesis_winding,
            )
            .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?,
        );
    }
    let psi = PsiKrimelackAnatomy::new(positions, constraint_count, rings)
        .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;
    let mathloom =
        MathLoomAnatomy::new(positions).map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;

    let population = reader.u128()?;
    let gating_charge_elementary = reader.i128()?;
    let chemical_open_minus_closed_zeptojoules = reader.big_rational()?;
    let gate_dissipation_quantum = reader.big_rational()?;
    let gate_dissipation_capacity = reader.u128()?;
    let single_channel_conductance = reader.exact_rational()?;
    let reversal_potential = reader.exact_rational()?;
    let contact_count = reader.usize()?;
    reader.require_records(contact_count, MIN_GATE_PSI_CONTACT_BYTES)?;
    let mut contacts = Vec::new();
    contacts
        .try_reserve_exact(contact_count)
        .map_err(|_| NeuronAnatomyCodecError::ArithmeticWidth)?;
    for _ in 0..contact_count {
        contacts.push(
            GatePsiContact::new(
                reader.usize()?,
                reader.usize()?,
                reader.i8()?,
                reader.big_rational()?,
            )
            .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?,
        );
    }
    let gate = TwoStateGateAnatomy::new_with_support_mode(
        population,
        independent_channel_supports,
        occurrence_bounded_population_work,
        gating_charge_elementary,
        chemical_open_minus_closed_zeptojoules,
        gate_dissipation_quantum,
        gate_dissipation_capacity,
        single_channel_conductance,
        reversal_potential,
        contacts,
        psi.ring_count(),
    )
    .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;
    let capacitance = MembraneCapacitance::new(reader.exact_rational()?)
        .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;

    let recovery_lane_count = reader.usize()?;
    if recovery_lane_count != psi.ring_count() {
        return Err(NeuronAnatomyCodecError::InvalidAnatomy);
    }
    reader.require_records(recovery_lane_count, RECOVERY_LANE_ANATOMY_BYTES)?;
    let mut recovery_lanes = Vec::new();
    recovery_lanes
        .try_reserve_exact(recovery_lane_count)
        .map_err(|_| NeuronAnatomyCodecError::ArithmeticWidth)?;
    for _ in 0..recovery_lane_count {
        recovery_lanes.push(reader.recovery_lane()?);
    }
    let recovery = RecoveryAnatomy::new(
        recovery_lanes,
        reader.recovery_lane()?,
        reader.recovery_lane()?,
        psi.ring_count(),
    )
    .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;
    let dna_expression = DnaExpressionAnatomy::new(
        reader.u128()?,
        reader.u128()?,
        reader.u128()?,
        reader.u128()?,
        reader.u128()?,
        reader.u128()?,
        reader.u128()?,
    )
    .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;
    let plastic = PlasticSupportAnatomy::new(
        reader.exact_rational()?,
        reader.exact_rational()?,
        reader.exact_rational()?,
        reader.exact_rational()?,
        reader.exact_rational()?,
        reader.u128()?,
    )
    .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)?;
    if !reader.finished() {
        return Err(NeuronAnatomyCodecError::InvalidEncoding);
    }
    NeuronPhysicalAnatomy::new(
        mathloom,
        psi,
        gate,
        capacitance,
        recovery,
        dna_expression,
        plastic,
    )
    .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)
}

pub(crate) fn encode_neuron_physical_cell(
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
) -> Result<Vec<u8>, NeuronAnatomyCodecError> {
    let anatomy_bytes = encode_neuron_physical_anatomy(anatomy)?;
    let state_bytes = encode_neuron_physical_state(anatomy, state)?;
    let mut encoded = Vec::new();
    encoded.extend_from_slice(NEURON_CELL_CODEC_MAGIC);
    push_anatomy_usize(&mut encoded, anatomy_bytes.len())?;
    push_anatomy_usize(&mut encoded, state_bytes.len())?;
    encoded.extend_from_slice(&anatomy_bytes);
    encoded.extend_from_slice(&state_bytes);
    Ok(encoded)
}

pub(crate) fn decode_neuron_physical_cell(
    encoded: &[u8],
) -> Result<(NeuronPhysicalAnatomy, NeuronPhysicalState), NeuronAnatomyCodecError> {
    let mut reader = NeuronAnatomyReader::new(encoded);
    if reader.take(NEURON_CELL_CODEC_MAGIC.len())? != NEURON_CELL_CODEC_MAGIC {
        return Err(NeuronAnatomyCodecError::InvalidEncoding);
    }
    let anatomy_len = reader.usize()?;
    let state_len = reader.usize()?;
    let anatomy = decode_neuron_physical_anatomy(reader.take(anatomy_len)?)?;
    let state = decode_neuron_physical_state(&anatomy, reader.take(state_len)?)?;
    if !reader.finished() {
        return Err(NeuronAnatomyCodecError::InvalidEncoding);
    }
    Ok((anatomy, state))
}

fn push_anatomy_usize(encoded: &mut Vec<u8>, value: usize) -> Result<(), NeuronAnatomyCodecError> {
    encoded.extend_from_slice(
        &u64::try_from(value)
            .map_err(|_| NeuronAnatomyCodecError::ArithmeticWidth)?
            .to_le_bytes(),
    );
    Ok(())
}

fn push_exact_rational(encoded: &mut Vec<u8>, value: ExactRational) {
    let (numerator, denominator) = value.parts();
    encoded.extend_from_slice(&numerator.to_le_bytes());
    encoded.extend_from_slice(&denominator.to_le_bytes());
}

fn push_big_rational(
    encoded: &mut Vec<u8>,
    value: &BigRational,
) -> Result<(), NeuronAnatomyCodecError> {
    for integer in [value.numer(), value.denom()] {
        let text = integer.to_string();
        push_anatomy_usize(encoded, text.len())?;
        encoded.extend_from_slice(text.as_bytes());
    }
    Ok(())
}

fn push_recovery_lane_anatomy(encoded: &mut Vec<u8>, lane: RecoveryLaneAnatomy) {
    for value in [
        lane.catalyst_per_extent,
        lane.fuel_per_extent,
        lane.spent_per_extent,
        lane.exported_heat_per_extent,
        lane.fuel_capacity,
        lane.spent_capacity,
        lane.exported_heat_capacity,
    ] {
        encoded.extend_from_slice(&value.to_le_bytes());
    }
}

struct NeuronAnatomyReader<'a> {
    encoded: &'a [u8],
    cursor: usize,
}

impl<'a> NeuronAnatomyReader<'a> {
    fn new(encoded: &'a [u8]) -> Self {
        Self { encoded, cursor: 0 }
    }

    fn take(&mut self, count: usize) -> Result<&'a [u8], NeuronAnatomyCodecError> {
        let end = self
            .cursor
            .checked_add(count)
            .ok_or(NeuronAnatomyCodecError::ArithmeticWidth)?;
        let value = self
            .encoded
            .get(self.cursor..end)
            .ok_or(NeuronAnatomyCodecError::InvalidEncoding)?;
        self.cursor = end;
        Ok(value)
    }

    fn require_records(
        &self,
        count: usize,
        minimum_record_bytes: usize,
    ) -> Result<(), NeuronAnatomyCodecError> {
        let minimum_bytes = count
            .checked_mul(minimum_record_bytes)
            .ok_or(NeuronAnatomyCodecError::ArithmeticWidth)?;
        let remaining = self
            .encoded
            .len()
            .checked_sub(self.cursor)
            .ok_or(NeuronAnatomyCodecError::InvalidEncoding)?;
        if minimum_bytes > remaining {
            return Err(NeuronAnatomyCodecError::InvalidEncoding);
        }
        Ok(())
    }

    fn usize(&mut self) -> Result<usize, NeuronAnatomyCodecError> {
        usize::try_from(u64::from_le_bytes(
            self.take(8)?
                .try_into()
                .map_err(|_| NeuronAnatomyCodecError::InvalidEncoding)?,
        ))
        .map_err(|_| NeuronAnatomyCodecError::ArithmeticWidth)
    }

    fn u128(&mut self) -> Result<u128, NeuronAnatomyCodecError> {
        Ok(u128::from_le_bytes(
            self.take(16)?
                .try_into()
                .map_err(|_| NeuronAnatomyCodecError::InvalidEncoding)?,
        ))
    }

    fn i128(&mut self) -> Result<i128, NeuronAnatomyCodecError> {
        Ok(i128::from_le_bytes(
            self.take(16)?
                .try_into()
                .map_err(|_| NeuronAnatomyCodecError::InvalidEncoding)?,
        ))
    }

    fn i8(&mut self) -> Result<i8, NeuronAnatomyCodecError> {
        Ok(self.take(1)?[0] as i8)
    }

    fn boolean(&mut self) -> Result<bool, NeuronAnatomyCodecError> {
        match self.take(1)?[0] {
            0 => Ok(false),
            1 => Ok(true),
            _ => Err(NeuronAnatomyCodecError::InvalidEncoding),
        }
    }

    fn exact_rational(&mut self) -> Result<ExactRational, NeuronAnatomyCodecError> {
        ExactRational::new(self.i128()?, self.u128()?)
            .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)
    }

    fn big_rational(&mut self) -> Result<BigRational, NeuronAnatomyCodecError> {
        let numerator = self.big_integer()?;
        let denominator = self.big_integer()?;
        if denominator <= BigInt::zero() {
            return Err(NeuronAnatomyCodecError::InvalidAnatomy);
        }
        let value = BigRational::new(numerator.clone(), denominator.clone());
        if value.numer() != &numerator || value.denom() != &denominator {
            return Err(NeuronAnatomyCodecError::InvalidEncoding);
        }
        Ok(value)
    }

    fn big_integer(&mut self) -> Result<BigInt, NeuronAnatomyCodecError> {
        let length = self.usize()?;
        let text = std::str::from_utf8(self.take(length)?)
            .map_err(|_| NeuronAnatomyCodecError::InvalidEncoding)?;
        let value = text
            .parse::<BigInt>()
            .map_err(|_| NeuronAnatomyCodecError::InvalidEncoding)?;
        if value.to_string() != text {
            return Err(NeuronAnatomyCodecError::InvalidEncoding);
        }
        Ok(value)
    }

    fn recovery_lane(&mut self) -> Result<RecoveryLaneAnatomy, NeuronAnatomyCodecError> {
        RecoveryLaneAnatomy::new(
            self.u128()?,
            self.u128()?,
            self.u128()?,
            self.u128()?,
            self.u128()?,
            self.u128()?,
            self.u128()?,
        )
        .map_err(|_| NeuronAnatomyCodecError::InvalidAnatomy)
    }

    fn finished(&self) -> bool {
        self.cursor == self.encoded.len()
    }
}

const NEURON_STATE_CODEC_MAGIC: &[u8; 8] = b"GLNPS01\0";
/// Neuron-state layout carrying a nonzero retained membrane-return work
/// residue (the exact rest-cost law, 2026-08-06).  Codec precedent
/// GLEXP02→GLEXP03 and GLMRC01: the new magic appears ONLY when the new field
/// differs from the historical default (a zero residue), so every body whose
/// residue is zero — every body written before this law, including the live
/// organism's — encodes byte-identically to before and its receipts do not
/// drift.  The residue's two words follow the magic; the rest of the layout is
/// unchanged, byte for byte, from `GLNPS01`.
const NEURON_STATE_RETURN_RESIDUE_MAGIC: &[u8; 8] = b"GLNPS02\0";
/// Neuron-state layout carrying a nonzero exact gate- or
/// plastic-dissipation residue. It carries the membrane-return residue first,
/// then the gate residue and plastic residue, followed by the unchanged
/// `GLNPS01` body. `GLNPS01` and `GLNPS02` remain byte-identical for every
/// historical body; this magic is canonical only when either new residue is
/// nonzero.
const NEURON_STATE_PLASTIC_RESIDUE_MAGIC: &[u8; 8] = b"GLNPS03\0";
const NEURON_STATE_WIDE_DISSIPATION_RESIDUE_MAGIC: &[u8; 8] = b"GLNPS04\0";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum NeuronStateCodecError {
    AnatomyMismatch,
    InvalidEncoding,
    ArithmeticWidth,
}

pub(crate) fn encode_neuron_physical_state(
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
) -> Result<Vec<u8>, NeuronStateCodecError> {
    if state.psi.rings.len() != anatomy.psi.rings.len()
        || state.recovery.psi_lanes.len() != anatomy.recovery.psi_lanes.len()
        || state.gate.open_population > anatomy.gate.population
        || state.gate.dissipated_quanta > anatomy.gate.dissipation_capacity_quanta
        || state.plastic.dissipated_quanta > anatomy.plastic.dissipation_capacity_quanta
        || state.dna_expression.expressed_product_quanta > anatomy.dna_expression.product_capacity
        || state.dna_expression.waste_quanta > anatomy.dna_expression.waste_capacity
        // Law 1 (threshold-integrated delivery, ratified 2026-08-05): the
        // receptor accumulator RETAINS energy across intervals until the
        // receiving gate's own opening threshold is reached, so a lawful
        // residue is routinely several whole quanta.  Its only canonical
        // bound is non-negativity; no anatomy number bounds it from above,
        // and inventing one would silently destroy retained energy.
        || rational_to_exact(state.receptor_quantum_residue) < Exact::zero()
        // The retained membrane-return work residue is what the body still
        // owes for return work already done.  Its canonical bound is
        // `[0, gate dissipation quantum)`: the billing law takes every whole
        // quantum the accumulation covers, so anything at or beyond one
        // quantum is a state the law cannot produce.
        || rational_to_exact(state.membrane_return_work_residue) < Exact::zero()
        || rational_to_exact(state.membrane_return_work_residue)
            >= anatomy.gate.dissipation_quantum_zeptojoules
        // Plastic return work is billed in the plastic support's own exact
        // dissipation quantum. Any remaining sub-quantum work is conserved
        // here rather than rejected or rounded away.
        || state.plastic.dissipation_residue_zeptojoules.energy() < &Exact::zero()
        || state.plastic.dissipation_residue_zeptojoules.energy()
            >= &rational_to_exact(anatomy.plastic.dissipation_quantum_zeptojoules)
        || (state.plastic.dissipated_quanta
            == anatomy.plastic.dissipation_capacity_quanta
            && !state.plastic.dissipation_residue_zeptojoules.is_zero())
        || state.gate.dissipation_residue_zeptojoules.energy() < &Exact::zero()
        || state.gate.dissipation_residue_zeptojoules.energy()
            >= &anatomy.gate.dissipation_quantum_zeptojoules
        || (state.gate.dissipated_quanta == anatomy.gate.dissipation_capacity_quanta
            && !state.gate.dissipation_residue_zeptojoules.is_zero())
    {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    let mut encoded = Vec::new();
    // Versioned head magic: a zero residue keeps the pre-law `GLNPS01`
    // layout byte for byte (see the magic's doc); a nonzero residue names
    // itself with `GLNPS02` and carries its two exact-rational words next.
    let (return_residue_numerator, return_residue_denominator) =
        state.membrane_return_work_residue.parts();
    let fixed_gate_residue = state.gate.dissipation_residue_zeptojoules.fixed_width();
    let fixed_plastic_residue = state.plastic.dissipation_residue_zeptojoules.fixed_width();
    if (!state.gate.dissipation_residue_zeptojoules.is_zero() && fixed_gate_residue.is_none())
        || (!state.plastic.dissipation_residue_zeptojoules.is_zero()
            && fixed_plastic_residue.is_none())
    {
        encoded.extend_from_slice(NEURON_STATE_WIDE_DISSIPATION_RESIDUE_MAGIC);
        push_i128(&mut encoded, return_residue_numerator);
        push_u128(&mut encoded, return_residue_denominator);
        push_state_big_rational(
            &mut encoded,
            state.gate.dissipation_residue_zeptojoules.energy(),
        )?;
        push_state_big_rational(
            &mut encoded,
            state.plastic.dissipation_residue_zeptojoules.energy(),
        )?;
    } else if !state.plastic.dissipation_residue_zeptojoules.is_zero()
        || !state.gate.dissipation_residue_zeptojoules.is_zero()
    {
        let (gate_residue_numerator, gate_residue_denominator) = fixed_gate_residue
            .expect("zero or fixed-width gate residue must fit GLNPS03")
            .parts();
        let (plastic_residue_numerator, plastic_residue_denominator) = fixed_plastic_residue
            .expect("zero or fixed-width plastic residue must fit GLNPS03")
            .parts();
        encoded.extend_from_slice(NEURON_STATE_PLASTIC_RESIDUE_MAGIC);
        push_i128(&mut encoded, return_residue_numerator);
        push_u128(&mut encoded, return_residue_denominator);
        push_i128(&mut encoded, gate_residue_numerator);
        push_u128(&mut encoded, gate_residue_denominator);
        push_i128(&mut encoded, plastic_residue_numerator);
        push_u128(&mut encoded, plastic_residue_denominator);
    } else if return_residue_numerator == 0 {
        encoded.extend_from_slice(NEURON_STATE_CODEC_MAGIC);
    } else {
        encoded.extend_from_slice(NEURON_STATE_RETURN_RESIDUE_MAGIC);
        push_i128(&mut encoded, return_residue_numerator);
        push_u128(&mut encoded, return_residue_denominator);
    }
    push_usize(&mut encoded, state.psi.rings.len())?;
    for (ring, ring_anatomy) in state.psi.rings.iter().zip(anatomy.psi.rings.iter()) {
        if ring.amplitude_quanta != ring_anatomy.node_amplitude_quanta
            || ring.phase_thirds != canonical_phase_thirds(ring.winding)
            || ring.dissipated_quanta > ring_anatomy.dissipation_capacity_quanta
        {
            return Err(NeuronStateCodecError::AnatomyMismatch);
        }
        encoded.push(ring.winding as i8 as u8);
        push_u128(&mut encoded, ring.dissipated_quanta);
    }
    push_u128(&mut encoded, state.gate.open_population);
    push_u128(&mut encoded, state.gate.dissipated_quanta);
    push_i128(
        &mut encoded,
        state.membrane.membrane().separated_elementary_charges(),
    );
    push_phase(&mut encoded, state.membrane.membrane().carrier_phase());
    push_phase(&mut encoded, state.membrane.path_carrier_phases()[0]);
    push_u128(&mut encoded, state.carriers.intracellular);
    push_u128(&mut encoded, state.carriers.extracellular);
    push_usize(&mut encoded, state.recovery.psi_lanes.len())?;
    for (lane, lane_anatomy) in state
        .recovery
        .psi_lanes
        .iter()
        .zip(anatomy.recovery.psi_lanes.iter())
    {
        encode_recovery_lane(&mut encoded, *lane, *lane_anatomy)?;
    }
    encode_recovery_lane(
        &mut encoded,
        state.recovery.gate_lane,
        anatomy.recovery.gate_lane,
    )?;
    encode_recovery_lane(
        &mut encoded,
        state.recovery.plastic_lane,
        anatomy.recovery.plastic_lane,
    )?;
    push_u128(&mut encoded, state.dna_expression.substrate_quanta);
    push_u128(&mut encoded, state.dna_expression.fuel_quanta);
    push_u128(&mut encoded, state.dna_expression.expressed_product_quanta);
    push_u128(&mut encoded, state.dna_expression.waste_quanta);
    let (rest_numerator, rest_denominator) = state.plastic.rest_length_nanometres.parts();
    push_i128(&mut encoded, rest_numerator);
    push_u128(&mut encoded, rest_denominator);
    push_u128(&mut encoded, state.plastic.dissipated_quanta);
    // Retained quantized-optical sub-quantum residue (ratified 2026-08-05):
    // encoded with the same exact-rational fixed-width discipline as the
    // retained charge-carrier phases above.
    let (residue_numerator, residue_denominator) = state.receptor_quantum_residue.parts();
    push_i128(&mut encoded, residue_numerator);
    push_u128(&mut encoded, residue_denominator);
    Ok(encoded)
}

pub(crate) fn decode_neuron_physical_state(
    anatomy: &NeuronPhysicalAnatomy,
    encoded: &[u8],
) -> Result<NeuronPhysicalState, NeuronStateCodecError> {
    let mut reader = NeuronStateReader::new(encoded);
    // Whichever layout the leading bytes name: the pre-law body (residue
    // zero) or the `GLNPS02` body that carries a nonzero retained
    // membrane-return work residue.  A `GLNPS02` body carrying zero is
    // refused — its canonical form is the bare `GLNPS01` body, and accepting
    // both would let one physical state admit two encodings.
    let (membrane_return_work_residue, gate_dissipation_residue, plastic_dissipation_residue) =
        match reader.take(NEURON_STATE_CODEC_MAGIC.len())? {
            magic if magic == NEURON_STATE_CODEC_MAGIC => (
                ExactRational::integer(0),
                PhysicalEnergyResidue::zero(),
                PhysicalEnergyResidue::zero(),
            ),
            magic if magic == NEURON_STATE_RETURN_RESIDUE_MAGIC => {
                let residue = ExactRational::new(reader.i128()?, reader.u128()?)
                    .map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
                if residue.parts().0 == 0 {
                    return Err(NeuronStateCodecError::InvalidEncoding);
                }
                (
                    residue,
                    PhysicalEnergyResidue::zero(),
                    PhysicalEnergyResidue::zero(),
                )
            }
            magic if magic == NEURON_STATE_PLASTIC_RESIDUE_MAGIC => {
                let membrane_residue = ExactRational::new(reader.i128()?, reader.u128()?)
                    .map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
                let gate_residue = ExactRational::new(reader.i128()?, reader.u128()?)
                    .map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
                let plastic_residue = ExactRational::new(reader.i128()?, reader.u128()?)
                    .map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
                if gate_residue.parts().0 == 0 && plastic_residue.parts().0 == 0 {
                    return Err(NeuronStateCodecError::InvalidEncoding);
                }
                (
                    membrane_residue,
                    PhysicalEnergyResidue::from_exact_rational(gate_residue),
                    PhysicalEnergyResidue::from_exact_rational(plastic_residue),
                )
            }
            magic if magic == NEURON_STATE_WIDE_DISSIPATION_RESIDUE_MAGIC => {
                let membrane_residue = ExactRational::new(reader.i128()?, reader.u128()?)
                    .map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
                let gate_residue = PhysicalEnergyResidue {
                    energy_zeptojoules: reader.big_rational()?,
                };
                let plastic_residue = PhysicalEnergyResidue {
                    energy_zeptojoules: reader.big_rational()?,
                };
                if (gate_residue.is_zero() && plastic_residue.is_zero())
                    || (gate_residue.fixed_width().is_some()
                        && plastic_residue.fixed_width().is_some())
                {
                    return Err(NeuronStateCodecError::InvalidEncoding);
                }
                (membrane_residue, gate_residue, plastic_residue)
            }
            _ => return Err(NeuronStateCodecError::InvalidEncoding),
        };
    let psi_count = reader.usize()?;
    if psi_count != anatomy.psi.rings.len() {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    let mut rings = Vec::with_capacity(psi_count);
    for ring_anatomy in &anatomy.psi.rings {
        let winding = decode_winding(reader.i8()?)?;
        let dissipated_quanta = reader.u128()?;
        if dissipated_quanta > ring_anatomy.dissipation_capacity_quanta {
            return Err(NeuronStateCodecError::AnatomyMismatch);
        }
        rings.push(PsiRingState {
            amplitude_quanta: ring_anatomy.node_amplitude_quanta,
            phase_thirds: canonical_phase_thirds(winding),
            winding,
            dissipated_quanta,
        });
    }
    let gate = TwoStateGateState {
        open_population: reader.u128()?,
        dissipated_quanta: reader.u128()?,
        dissipation_residue_zeptojoules: gate_dissipation_residue,
    };
    if gate.open_population > anatomy.gate.population
        || gate.dissipated_quanta > anatomy.gate.dissipation_capacity_quanta
        || gate.dissipation_residue_zeptojoules.energy() < &Exact::zero()
        || gate.dissipation_residue_zeptojoules.energy()
            >= &anatomy.gate.dissipation_quantum_zeptojoules
        || (gate.dissipated_quanta == anatomy.gate.dissipation_capacity_quanta
            && !gate.dissipation_residue_zeptojoules.is_zero())
    {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    let separated_elementary_charges = reader.i128()?;
    let membrane_phase = reader.phase()?;
    let path_phase = reader.phase()?;
    let membrane = LocalMembraneConductanceState::from_physical_parts(
        ElementaryChargeMembraneState::from_physical_parts(
            separated_elementary_charges,
            membrane_phase,
        ),
        [path_phase],
    );
    let carriers = CarrierReservoirs {
        intracellular: reader.u128()?,
        extracellular: reader.u128()?,
    };
    let recovery_count = reader.usize()?;
    if recovery_count != anatomy.recovery.psi_lanes.len() {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    let mut psi_lanes = Vec::with_capacity(recovery_count);
    for lane_anatomy in &anatomy.recovery.psi_lanes {
        psi_lanes.push(decode_recovery_lane(&mut reader, *lane_anatomy)?);
    }
    let recovery = RecoveryState {
        psi_lanes: psi_lanes.into_boxed_slice(),
        gate_lane: decode_recovery_lane(&mut reader, anatomy.recovery.gate_lane)?,
        plastic_lane: decode_recovery_lane(&mut reader, anatomy.recovery.plastic_lane)?,
    };
    let dna_expression = DnaExpressionState {
        substrate_quanta: reader.u128()?,
        fuel_quanta: reader.u128()?,
        expressed_product_quanta: reader.u128()?,
        waste_quanta: reader.u128()?,
    };
    if dna_expression.expressed_product_quanta > anatomy.dna_expression.product_capacity
        || dna_expression.waste_quanta > anatomy.dna_expression.waste_capacity
    {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    let plastic = PlasticSupportState {
        rest_length_nanometres: ExactRational::new(reader.i128()?, reader.u128()?)
            .map_err(|_| NeuronStateCodecError::InvalidEncoding)?,
        dissipated_quanta: reader.u128()?,
        dissipation_residue_zeptojoules: plastic_dissipation_residue,
    };
    let receptor_quantum_residue = ExactRational::new(reader.i128()?, reader.u128()?)
        .map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
    if plastic.rest_length_nanometres.parts().0 <= 0
        || plastic.dissipated_quanta > anatomy.plastic.dissipation_capacity_quanta
        // Law 1: a retained receptor accumulator is bounded only by
        // non-negativity (see the encoder).
        || rational_to_exact(receptor_quantum_residue) < Exact::zero()
        // The retained membrane-return work residue is bounded by
        // `[0, gate dissipation quantum)` (see the encoder).
        || rational_to_exact(membrane_return_work_residue) < Exact::zero()
        || rational_to_exact(membrane_return_work_residue)
            >= anatomy.gate.dissipation_quantum_zeptojoules
        || plastic.dissipation_residue_zeptojoules.energy() < &Exact::zero()
        || plastic.dissipation_residue_zeptojoules.energy()
            >= &rational_to_exact(anatomy.plastic.dissipation_quantum_zeptojoules)
        || (plastic.dissipated_quanta == anatomy.plastic.dissipation_capacity_quanta
            && !plastic.dissipation_residue_zeptojoules.is_zero())
        || gate.dissipation_residue_zeptojoules.energy() < &Exact::zero()
        || gate.dissipation_residue_zeptojoules.energy()
            >= &anatomy.gate.dissipation_quantum_zeptojoules
        || (gate.dissipated_quanta == anatomy.gate.dissipation_capacity_quanta
            && !gate.dissipation_residue_zeptojoules.is_zero())
        || !reader.finished()
    {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    Ok(NeuronPhysicalState::new(
        PsiKrimelackState {
            rings: rings.into_boxed_slice(),
        },
        gate,
        membrane,
        carriers,
        recovery,
        dna_expression,
        plastic,
        receptor_quantum_residue,
        membrane_return_work_residue,
    ))
}

fn encode_recovery_lane(
    encoded: &mut Vec<u8>,
    lane: RecoveryLaneState,
    anatomy: RecoveryLaneAnatomy,
) -> Result<(), NeuronStateCodecError> {
    if lane.fuel_quanta > anatomy.fuel_capacity
        || lane.spent_quanta > anatomy.spent_capacity
        || lane.exported_heat_quanta > anatomy.exported_heat_capacity
    {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    push_u128(encoded, lane.fuel_quanta);
    push_u128(encoded, lane.spent_quanta);
    push_u128(encoded, lane.exported_heat_quanta);
    Ok(())
}

fn decode_recovery_lane(
    reader: &mut NeuronStateReader<'_>,
    anatomy: RecoveryLaneAnatomy,
) -> Result<RecoveryLaneState, NeuronStateCodecError> {
    let lane = RecoveryLaneState {
        fuel_quanta: reader.u128()?,
        spent_quanta: reader.u128()?,
        exported_heat_quanta: reader.u128()?,
    };
    if lane.fuel_quanta > anatomy.fuel_capacity
        || lane.spent_quanta > anatomy.spent_capacity
        || lane.exported_heat_quanta > anatomy.exported_heat_capacity
    {
        return Err(NeuronStateCodecError::AnatomyMismatch);
    }
    Ok(lane)
}

fn push_phase(encoded: &mut Vec<u8>, phase: ChargeCarrierPhase) {
    let (numerator, denominator) = phase.parts();
    push_i128(encoded, numerator);
    push_u128(encoded, denominator);
}

fn push_usize(encoded: &mut Vec<u8>, value: usize) -> Result<(), NeuronStateCodecError> {
    encoded.extend_from_slice(
        &u64::try_from(value)
            .map_err(|_| NeuronStateCodecError::ArithmeticWidth)?
            .to_le_bytes(),
    );
    Ok(())
}

fn push_u128(encoded: &mut Vec<u8>, value: u128) {
    encoded.extend_from_slice(&value.to_le_bytes());
}

fn push_i128(encoded: &mut Vec<u8>, value: i128) {
    encoded.extend_from_slice(&value.to_le_bytes());
}

fn push_state_big_rational(
    encoded: &mut Vec<u8>,
    value: &Exact,
) -> Result<(), NeuronStateCodecError> {
    for integer in [value.numer(), value.denom()] {
        let bytes = integer.to_signed_bytes_le();
        push_usize(encoded, bytes.len())?;
        encoded.extend_from_slice(&bytes);
    }
    Ok(())
}

fn decode_winding(value: i8) -> Result<BalancedTrit, NeuronStateCodecError> {
    match value {
        -1 => Ok(BalancedTrit::Negative),
        0 => Ok(BalancedTrit::Quiescent),
        1 => Ok(BalancedTrit::Positive),
        _ => Err(NeuronStateCodecError::InvalidEncoding),
    }
}

struct NeuronStateReader<'a> {
    encoded: &'a [u8],
    cursor: usize,
}

impl<'a> NeuronStateReader<'a> {
    fn new(encoded: &'a [u8]) -> Self {
        Self { encoded, cursor: 0 }
    }

    fn take(&mut self, count: usize) -> Result<&'a [u8], NeuronStateCodecError> {
        let end = self
            .cursor
            .checked_add(count)
            .ok_or(NeuronStateCodecError::ArithmeticWidth)?;
        let value = self
            .encoded
            .get(self.cursor..end)
            .ok_or(NeuronStateCodecError::InvalidEncoding)?;
        self.cursor = end;
        Ok(value)
    }

    fn i8(&mut self) -> Result<i8, NeuronStateCodecError> {
        Ok(self.take(1)?[0] as i8)
    }

    fn u128(&mut self) -> Result<u128, NeuronStateCodecError> {
        Ok(u128::from_le_bytes(
            self.take(16)?
                .try_into()
                .map_err(|_| NeuronStateCodecError::InvalidEncoding)?,
        ))
    }

    fn i128(&mut self) -> Result<i128, NeuronStateCodecError> {
        Ok(i128::from_le_bytes(
            self.take(16)?
                .try_into()
                .map_err(|_| NeuronStateCodecError::InvalidEncoding)?,
        ))
    }

    fn usize(&mut self) -> Result<usize, NeuronStateCodecError> {
        usize::try_from(u64::from_le_bytes(
            self.take(8)?
                .try_into()
                .map_err(|_| NeuronStateCodecError::InvalidEncoding)?,
        ))
        .map_err(|_| NeuronStateCodecError::ArithmeticWidth)
    }

    fn big_integer(&mut self) -> Result<BigInt, NeuronStateCodecError> {
        let length = self.usize()?;
        if length == 0 {
            return Err(NeuronStateCodecError::InvalidEncoding);
        }
        let bytes = self.take(length)?;
        let value = BigInt::from_signed_bytes_le(bytes);
        if value.to_signed_bytes_le() != bytes {
            return Err(NeuronStateCodecError::InvalidEncoding);
        }
        Ok(value)
    }

    fn big_rational(&mut self) -> Result<Exact, NeuronStateCodecError> {
        let numerator = self.big_integer()?;
        let denominator = self.big_integer()?;
        if denominator <= BigInt::zero() {
            return Err(NeuronStateCodecError::InvalidEncoding);
        }
        let value = Exact::new(numerator.clone(), denominator.clone());
        if value.numer() != &numerator || value.denom() != &denominator {
            return Err(NeuronStateCodecError::InvalidEncoding);
        }
        Ok(value)
    }

    fn phase(&mut self) -> Result<ChargeCarrierPhase, NeuronStateCodecError> {
        ChargeCarrierPhase::new(self.i128()?, self.u128()?)
            .map_err(|_| NeuronStateCodecError::InvalidEncoding)
    }

    fn finished(&self) -> bool {
        self.cursor == self.encoded.len()
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) enum NeuronPhysicalError {
    AnatomyMismatch,
    Boundary(JointNeuronBoundaryError),
    Psi(PsiSettlementError),
    Gate(GateSettlementError),
    Recovery(RecoveryError),
    DnaExpression(DnaExpressionError),
    Plasticity(PlasticityError),
    ExactDelta(ExactRationalError),
    SequenceEndedBeforeQuiescence,
}

impl From<JointNeuronBoundaryError> for NeuronPhysicalError {
    fn from(value: JointNeuronBoundaryError) -> Self {
        Self::Boundary(value)
    }
}

impl From<PsiSettlementError> for NeuronPhysicalError {
    fn from(value: PsiSettlementError) -> Self {
        Self::Psi(value)
    }
}

impl From<GateSettlementError> for NeuronPhysicalError {
    fn from(value: GateSettlementError) -> Self {
        Self::Gate(value)
    }
}

impl From<RecoveryError> for NeuronPhysicalError {
    fn from(value: RecoveryError) -> Self {
        Self::Recovery(value)
    }
}

impl From<DnaExpressionError> for NeuronPhysicalError {
    fn from(value: DnaExpressionError) -> Self {
        Self::DnaExpression(value)
    }
}

impl From<PlasticityError> for NeuronPhysicalError {
    fn from(value: PlasticityError) -> Self {
        Self::Plasticity(value)
    }
}

impl From<ExactRationalError> for NeuronPhysicalError {
    fn from(value: ExactRationalError) -> Self {
        Self::ExactDelta(value)
    }
}

#[derive(Clone, Debug)]
pub(crate) struct NeuronPhysicalInterval {
    pub(crate) psi: PsiSettlement,
    pub(crate) gate_membrane: GateMembraneSettlement,
    pub(crate) successor: NeuronPhysicalState,
}

/// Execute one exact reached physical interval. This produces current physical
/// successor state only. It does not emit a neuronal fractal because a single
/// membrane interval is not, by itself, proof of post-experience quiescence.
pub(crate) fn settle_neuron_physical_interval(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    perspective: JointNeuronPerspective<'_>,
    gate_work: GateWorkOccurrence,
    interval_microseconds: u32,
) -> Result<NeuronPhysicalInterval, NeuronPhysicalError> {
    settle_neuron_physical_interval_with_contact(
        anatomy,
        predecessor,
        perspective,
        gate_work,
        interval_microseconds,
        0,
        None,
    )
}

pub(crate) fn settle_neuron_physical_interval_with_contact(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    perspective: JointNeuronPerspective<'_>,
    gate_work: GateWorkOccurrence,
    interval_microseconds: u32,
    inter_neuron_outward_elementary_charges: i128,
    prepared_psi: Option<PsiSettlement>,
) -> Result<NeuronPhysicalInterval, NeuronPhysicalError> {
    let psi = match prepared_psi {
        Some(psi) => psi,
        None => {
            let mathloom = settle_shared_dsf_mathloom(perspective, anatomy.mathloom)?;
            settle_psi_krimelack(&anatomy.psi, &predecessor.psi, &mathloom)?
        }
    };
    let gate_membrane = settle_gate_membrane_with_contact(
        &anatomy.gate,
        &anatomy.plastic,
        &predecessor.plastic,
        predecessor.gate.clone(),
        &psi.successor,
        gate_work,
        anatomy.capacitance,
        predecessor.membrane,
        predecessor.carriers,
        interval_microseconds,
        inter_neuron_outward_elementary_charges,
    )?;
    let successor = NeuronPhysicalState::new(
        psi.successor.clone(),
        gate_membrane.successor_gate.clone(),
        gate_membrane.membrane.successor,
        gate_membrane.successor_carriers,
        predecessor.recovery.clone(),
        predecessor.dna_expression,
        predecessor.plastic.clone(),
        predecessor.receptor_quantum_residue,
        // A stimulus interval does no membrane-RETURN work — the return path
        // is the rest metabolism's — so it neither adds to nor erases the
        // retained sub-quantum remainder, exactly as a dark interval leaves
        // the receptor accumulator alone.
        predecessor.membrane_return_work_residue,
    );
    Ok(NeuronPhysicalInterval {
        psi,
        gate_membrane,
        successor,
    })
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum GateSettlementError {
    InvalidAnatomy,
    InvalidPsiContact,
    ContactOutsidePsiAnatomy,
    GatePopulationExceeded,
    ArithmeticWidth,
    InsufficientCarrierMaterial,
    Membrane(MembraneConductanceError),
    Plasticity(PlasticityError),
}

impl From<MembraneConductanceError> for GateSettlementError {
    fn from(value: MembraneConductanceError) -> Self {
        Self::Membrane(value)
    }
}

impl From<PlasticityError> for GateSettlementError {
    fn from(value: PlasticityError) -> Self {
        Self::Plasticity(value)
    }
}

impl From<ExactRationalError> for GateSettlementError {
    fn from(value: ExactRationalError) -> Self {
        match value {
            ExactRationalError::ArithmeticWidth => Self::ArithmeticWidth,
            ExactRationalError::ZeroDenominator | ExactRationalError::NonCanonicalRatio => {
                Self::InvalidAnatomy
            }
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct GateMembraneSettlement {
    pub(crate) successor_gate: TwoStateGateState,
    pub(crate) successor_carriers: CarrierReservoirs,
    pub(crate) membrane: LocalMembraneConductanceTransition<1>,
    pub(crate) open_minus_closed_energy_zeptojoules: Exact,
    /// Exact downhill work that could not remain in this gate's finite local
    /// dissipation reservoir and therefore crossed the neuron's local control
    /// volume as heat. It is transient flow, not retained neuronal state.
    pub(crate) exported_heat_zeptojoules: Exact,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct GatePopulationSettlement {
    open_population: u128,
    released_quanta: u128,
    dissipation_residue_zeptojoules: PhysicalEnergyResidue,
    exported_heat_zeptojoules: Exact,
}

fn quantize_gate_release(
    predecessor_residue: &PhysicalEnergyResidue,
    released_energy: &Exact,
    quantum: &Exact,
    maximum_released_quanta: Option<u128>,
) -> Result<Option<(u128, PhysicalEnergyResidue, Exact)>, GateSettlementError> {
    if released_energy <= &Exact::zero() || quantum <= &Exact::zero() {
        return Ok(None);
    }
    let accumulated = predecessor_residue.energy() + released_energy;
    let whole = (&accumulated / quantum).floor().to_integer();
    let released_quanta = whole
        .to_u128()
        .ok_or(GateSettlementError::ArithmeticWidth)?;
    let residue = &accumulated - quantum * Exact::from_integer(whole);
    let (released_quanta, residue, exported_heat) = match maximum_released_quanta {
        Some(maximum)
            if released_quanta > maximum || (released_quanta == maximum && !residue.is_zero()) =>
        {
            let local_capacity = quantum * Exact::from_integer(BigInt::from(maximum));
            let exported = &accumulated - &local_capacity;
            if exported <= Exact::zero() {
                return Err(GateSettlementError::ArithmeticWidth);
            }
            (maximum, Exact::zero(), exported)
        }
        _ => (released_quanta, residue, Exact::zero()),
    };
    Ok(Some((
        released_quanta,
        PhysicalEnergyResidue {
            energy_zeptojoules: residue,
        },
        exported_heat,
    )))
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct GateWorkOccurrence {
    open_minus_closed_zeptojoules: Exact,
    receptor_target_open_population: Option<u128>,
}

impl GateWorkOccurrence {
    pub(crate) fn new(open_minus_closed_zeptojoules: Exact) -> Self {
        Self {
            open_minus_closed_zeptojoules,
            receptor_target_open_population: None,
        }
    }

    pub(crate) fn receptor_activation(
        delivered_work_zeptojoules: Exact,
        target_open_population: u128,
    ) -> Result<Self, GateSettlementError> {
        if delivered_work_zeptojoules.is_positive() || target_open_population == 0 {
            return Err(GateSettlementError::InvalidAnatomy);
        }
        Ok(Self {
            open_minus_closed_zeptojoules: delivered_work_zeptojoules,
            receptor_target_open_population: Some(target_open_population),
        })
    }

    pub(crate) fn is_zero(&self) -> bool {
        self.open_minus_closed_zeptojoules.is_zero()
    }
}

/// Deterministic two-state free-energy descent approved for virtual material.
/// `delta_g < 0` can open finite closed conformations; `delta_g > 0` can close
/// finite open conformations; equality retains the predecessor. Every changed
/// conformation deposits its exact released energy in the finite dissipation
/// reservoir. Conductance follows only from the resulting open population.
pub(crate) fn settle_gate_membrane(
    anatomy: &TwoStateGateAnatomy,
    plastic_anatomy: &PlasticSupportAnatomy,
    plastic_state: &PlasticSupportState,
    predecessor_gate: TwoStateGateState,
    psi: &PsiKrimelackState,
    gate_work: GateWorkOccurrence,
    capacitance: MembraneCapacitance,
    predecessor_membrane: LocalMembraneConductanceState<1>,
    predecessor_carriers: CarrierReservoirs,
    interval_microseconds: u32,
) -> Result<GateMembraneSettlement, GateSettlementError> {
    settle_gate_membrane_with_contact(
        anatomy,
        plastic_anatomy,
        plastic_state,
        predecessor_gate,
        psi,
        gate_work,
        capacitance,
        predecessor_membrane,
        predecessor_carriers,
        interval_microseconds,
        0,
    )
}

#[allow(clippy::too_many_arguments)]
pub(crate) fn settle_gate_membrane_with_contact(
    anatomy: &TwoStateGateAnatomy,
    plastic_anatomy: &PlasticSupportAnatomy,
    plastic_state: &PlasticSupportState,
    predecessor_gate: TwoStateGateState,
    psi: &PsiKrimelackState,
    gate_work: GateWorkOccurrence,
    capacitance: MembraneCapacitance,
    predecessor_membrane: LocalMembraneConductanceState<1>,
    predecessor_carriers: CarrierReservoirs,
    interval_microseconds: u32,
    inter_neuron_outward_elementary_charges: i128,
) -> Result<GateMembraneSettlement, GateSettlementError> {
    if predecessor_gate.open_population > anatomy.population {
        return Err(GateSettlementError::GatePopulationExceeded);
    }
    let open_minus_closed = gate_open_minus_closed_free_energy(
        anatomy,
        plastic_anatomy,
        plastic_state,
        predecessor_membrane,
        capacitance,
        psi,
        &gate_work,
    )?;
    let free_quanta = anatomy
        .dissipation_capacity_quanta
        .checked_sub(predecessor_gate.dissipated_quanta)
        .ok_or(GateSettlementError::GatePopulationExceeded)?;
    let population_settlement = select_gate_population_settlement(
        anatomy,
        plastic_anatomy,
        plastic_state,
        &predecessor_gate,
        predecessor_membrane,
        capacitance,
        psi,
        &gate_work,
        Some(free_quanta),
    )?;
    let mut successor_gate = predecessor_gate.clone();
    let mut exported_heat_zeptojoules = Exact::zero();
    if let Some(settlement) = population_settlement {
        successor_gate.dissipated_quanta = predecessor_gate
            .dissipated_quanta
            .checked_add(settlement.released_quanta)
            .ok_or(GateSettlementError::ArithmeticWidth)?;
        successor_gate.dissipation_residue_zeptojoules = settlement.dissipation_residue_zeptojoules;
        successor_gate.open_population = settlement.open_population;
        exported_heat_zeptojoules = settlement.exported_heat_zeptojoules;
    }

    let open_i128 = i128::try_from(successor_gate.open_population)
        .map_err(|_| GateSettlementError::ArithmeticWidth)?;
    let conductance = anatomy
        .single_channel_conductance_picosiemens
        .checked_mul(ExactRational::integer(open_i128))
        .map_err(|_| GateSettlementError::ArithmeticWidth)?;
    let path = LocalConductancePath::new(conductance, anatomy.reversal_potential_millivolts)?;
    let mut membrane = settle_local_membrane_conductances_with_inter_neuron_contact(
        capacitance,
        predecessor_membrane,
        &[path],
        interval_microseconds,
        inter_neuron_outward_elementary_charges,
    )?;
    // CONDUCTANCE IS CARRIERS TIMES MOBILITY, so a site with no carriers
    // conducts nothing (2026-08-08).  This is a definition, not a tuning.
    //
    // MEASURED ON THE LIVE ORGANISM: neuron 8 pushed its intracellular
    // carriers to zero and every transport afterwards refused with
    // InsufficientCarrierMaterial — every lesson, every offered material and
    // even a plain dark interval.  Carriers only come back by moving through
    // this same transport, so nothing could ever return them: she was frozen
    // permanently and could not have any experience at all.  Treating an
    // empty reservoir as an ERROR is what turned depletion into a deadlock.
    //
    // The path is re-settled with its conductance scaled by exactly the
    // fraction of the demanded charge the reservoir can actually supply, so
    // the membrane and the carriers move the SAME bounded charge and
    // conservation is untouched.  The scale is an exact rational read from
    // her own state — no constant, no threshold, no tuned coefficient.
    // TWO FLOWS DRAW ON ONE RESERVE IN THE SAME INTERVAL (2026-08-08).
    //
    // The inter-neuron transfer is decided FIRST, atomically for the whole
    // cohort, and it is already bounded by what the sender holds. The local
    // flow then draws on what is LEFT. Checking both against the same
    // pre-interval reserve let the second one overdraw — which is why neuron
    // 8 was fixed and neuron 7 immediately refused in its place.
    let demanded = membrane.outward_elementary_charges_by_path[0];
    let committed_outward: u128 = if inter_neuron_outward_elementary_charges > 0 {
        inter_neuron_outward_elementary_charges.unsigned_abs()
    } else {
        0
    };
    let available: u128 = if demanded >= 0 {
        predecessor_carriers
            .intracellular
            .saturating_sub(committed_outward)
    } else {
        predecessor_carriers.extracellular
    };
    if demanded.unsigned_abs() > available {
        let requested_current = membrane.path_currents_picoamperes[0];
        let bounded_current = current_limited_by_available_carriers(
            predecessor_membrane.path_carrier_phases()[0],
            requested_current,
            interval_microseconds,
            available,
        )
        .map_err(MembraneConductanceError::from)
        .map_err(GateSettlementError::from)?;
        let limited = bounded_current
            .checked_div(requested_current)
            .map_err(|_| GateSettlementError::ArithmeticWidth)?;
        let scaled = conductance
            .checked_mul(limited)
            .map_err(|_| GateSettlementError::ArithmeticWidth)?;
        let bounded_path =
            LocalConductancePath::new(scaled, anatomy.reversal_potential_millivolts)?;
        membrane = settle_local_membrane_conductances_with_inter_neuron_contact(
            capacitance,
            predecessor_membrane,
            &[bounded_path],
            interval_microseconds,
            inter_neuron_outward_elementary_charges,
        )?;
    }
    let locally_settled_carriers = move_carriers(
        predecessor_carriers,
        membrane.outward_elementary_charges_by_path[0],
    )?;
    let successor_carriers = move_inter_neuron_carriers(
        locally_settled_carriers,
        inter_neuron_outward_elementary_charges,
    )?;
    Ok(GateMembraneSettlement {
        successor_gate,
        successor_carriers,
        membrane,
        open_minus_closed_energy_zeptojoules: open_minus_closed,
        exported_heat_zeptojoules,
    })
}

#[allow(clippy::too_many_arguments)]
fn select_gate_population_settlement(
    anatomy: &TwoStateGateAnatomy,
    plastic_anatomy: &PlasticSupportAnatomy,
    plastic_state: &PlasticSupportState,
    predecessor_gate: &TwoStateGateState,
    predecessor_membrane: LocalMembraneConductanceState<1>,
    capacitance: MembraneCapacitance,
    psi: &PsiKrimelackState,
    gate_work: &GateWorkOccurrence,
    maximum_released_quanta: Option<u128>,
) -> Result<Option<GatePopulationSettlement>, GateSettlementError> {
    let internal_only_work = GateWorkOccurrence::new(Exact::zero());
    let predecessor_work = if gate_work.receptor_target_open_population.is_some() {
        &internal_only_work
    } else {
        gate_work
    };
    let predecessor_energy = gate_population_free_energy(
        anatomy,
        plastic_anatomy,
        plastic_state,
        predecessor_membrane,
        capacitance,
        psi,
        predecessor_work,
        predecessor_gate.open_population,
    )?;
    if let Some(target_population) = gate_work.receptor_target_open_population {
        if !anatomy.has_independent_channel_supports()
            || target_population < predecessor_gate.open_population
            || target_population > anatomy.population
        {
            return Err(GateSettlementError::GatePopulationExceeded);
        }
        let successor_energy = gate_population_free_energy(
            anatomy,
            plastic_anatomy,
            plastic_state,
            predecessor_membrane,
            capacitance,
            psi,
            &internal_only_work,
            target_population,
        )?;
        let internal_required = &successor_energy - &predecessor_energy;
        let delivered = -gate_work.open_minus_closed_zeptojoules.clone();
        let released_energy = delivered - internal_required;
        let Some((released_quanta, dissipation_residue_zeptojoules, exported_heat_zeptojoules)) =
            quantize_gate_release(
                &predecessor_gate.dissipation_residue_zeptojoules,
                &released_energy,
                &anatomy.dissipation_quantum_zeptojoules,
                maximum_released_quanta,
            )?
        else {
            return Ok(None);
        };
        return Ok(Some(GatePopulationSettlement {
            open_population: target_population,
            released_quanta,
            dissipation_residue_zeptojoules,
            exported_heat_zeptojoules,
        }));
    }
    if anatomy.population == 1 {
        let successor_population = 1 - predecessor_gate.open_population;
        let successor_energy = gate_population_free_energy(
            anatomy,
            plastic_anatomy,
            plastic_state,
            predecessor_membrane,
            capacitance,
            psi,
            gate_work,
            successor_population,
        )?;
        if successor_energy >= predecessor_energy {
            return Ok(None);
        }
        let released_energy = &predecessor_energy - &successor_energy;
        let Some((released_quanta, dissipation_residue_zeptojoules, exported_heat_zeptojoules)) =
            quantize_gate_release(
                &predecessor_gate.dissipation_residue_zeptojoules,
                &released_energy,
                &anatomy.dissipation_quantum_zeptojoules,
                maximum_released_quanta,
            )?
        else {
            return Ok(None);
        };
        return Ok(Some(GatePopulationSettlement {
            open_population: successor_population,
            released_quanta,
            dissipation_residue_zeptojoules,
            exported_heat_zeptojoules,
        }));
    }
    // The collective support coordinate is affine in open population and its
    // elastic energy is quadratic; every other gate term is linear. The whole
    // gate free-energy law is therefore convex over integer population. Find
    // its exact discrete minimum by comparing adjacent energies instead of
    // reevaluating every possible population. At most two adjacent integers
    // can share the minimum, so the predecessor and tie behavior below is
    // identical to the former exhaustive scan.
    let energy_at = |open_population| {
        gate_population_free_energy(
            anatomy,
            plastic_anatomy,
            plastic_state,
            predecessor_membrane,
            capacitance,
            psi,
            gate_work,
            open_population,
        )
    };
    let mut low = 0_u128;
    let mut high = anatomy.population;
    while low < high {
        let middle = low + (high - low) / 2;
        let middle_energy = energy_at(middle)?;
        let next_energy = energy_at(
            middle
                .checked_add(1)
                .ok_or(GateSettlementError::ArithmeticWidth)?,
        )?;
        if next_energy < middle_energy {
            low = middle
                .checked_add(1)
                .ok_or(GateSettlementError::ArithmeticWidth)?;
        } else {
            high = middle;
        }
    }
    let first_minimum = low;
    let first_minimum_energy = energy_at(first_minimum)?;
    let second_minimum = if first_minimum < anatomy.population {
        let candidate = first_minimum
            .checked_add(1)
            .ok_or(GateSettlementError::ArithmeticWidth)?;
        (energy_at(candidate)? == first_minimum_energy).then_some(candidate)
    } else {
        None
    };
    let mut selected: Option<GatePopulationSettlement> = None;
    let mut tied = false;
    for open_population in [Some(first_minimum), second_minimum].into_iter().flatten() {
        if open_population == predecessor_gate.open_population {
            continue;
        }
        let candidate_energy = energy_at(open_population)?;
        if candidate_energy >= predecessor_energy {
            continue;
        }
        let released_energy = &predecessor_energy - &candidate_energy;
        let Some((released_quanta, dissipation_residue_zeptojoules, exported_heat_zeptojoules)) =
            quantize_gate_release(
                &predecessor_gate.dissipation_residue_zeptojoules,
                &released_energy,
                &anatomy.dissipation_quantum_zeptojoules,
                maximum_released_quanta,
            )?
        else {
            continue;
        };
        if selected.is_none() {
            selected = Some(GatePopulationSettlement {
                open_population,
                released_quanta,
                dissipation_residue_zeptojoules,
                exported_heat_zeptojoules,
            });
        } else {
            tied = true;
        }
    }
    if tied {
        return Ok(None);
    }
    Ok(selected)
}

#[allow(clippy::too_many_arguments)]
fn gate_population_free_energy(
    anatomy: &TwoStateGateAnatomy,
    plastic_anatomy: &PlasticSupportAnatomy,
    plastic_state: &PlasticSupportState,
    predecessor_membrane: LocalMembraneConductanceState<1>,
    capacitance: MembraneCapacitance,
    psi: &PsiKrimelackState,
    gate_work: &GateWorkOccurrence,
    open_population: u128,
) -> Result<Exact, GateSettlementError> {
    if anatomy.population == 0 || open_population > anatomy.population {
        return Err(GateSettlementError::GatePopulationExceeded);
    }
    // A finite receptor ensemble has one exact mechanical coordinate
    // x(n)=((N-n)x_closed+n x_open)/N.  Gate energy and plastic return mapping
    // must read that same coordinate.  Treating already-yielded channels as
    // an irreversible prefix made occupancy a one-way maximum and erased
    // later lower/differently distributed sensory patterns.
    let closed_population = anatomy.population - open_population;
    let coordinate = plastic_anatomy
        .closed_coordinate_nanometres
        .checked_mul_unsigned(closed_population)?
        .checked_add(
            plastic_anatomy
                .open_coordinate_nanometres
                .checked_mul_unsigned(open_population)?,
        )?
        .checked_div_unsigned(anatomy.population)?;
    let support_energy = rational_to_exact(support_energy_at(
        plastic_anatomy,
        coordinate,
        plastic_state.rest_length_nanometres,
    )?);

    let potential = predecessor_membrane
        .membrane()
        .potential_millivolts(capacitance)
        .map_err(MembraneConductanceError::from)?;
    let electrical = rational_to_exact(potential)
        * Exact::from_integer(BigInt::from(anatomy.gating_charge_elementary))
        * Exact::new(
            BigInt::from(801_088_317_u64),
            BigInt::from(5_000_000_000_u64),
        );
    let mut per_open_channel = anatomy.chemical_open_minus_closed_zeptojoules.clone();
    per_open_channel -= electrical;
    for contact in &anatomy.psi_contacts {
        let phase = psi.rings[contact.ring_index].phase_thirds[contact.node_index];
        let cosine = if phase == contact.preferred_phase_third {
            Exact::one()
        } else {
            Exact::new(BigInt::from(-1_i8), BigInt::from(2_u8))
        };
        per_open_channel -= &contact.open_minus_closed_coupling_zeptojoules * cosine;
    }
    let open = Exact::from_integer(BigInt::from(open_population));
    let population = Exact::from_integer(BigInt::from(anatomy.population));
    Ok(support_energy
        + &open * per_open_channel
        + (&open / population) * &gate_work.open_minus_closed_zeptojoules)
}

fn gate_open_minus_closed_free_energy(
    anatomy: &TwoStateGateAnatomy,
    plastic_anatomy: &PlasticSupportAnatomy,
    plastic_state: &PlasticSupportState,
    predecessor_membrane: LocalMembraneConductanceState<1>,
    capacitance: MembraneCapacitance,
    psi: &PsiKrimelackState,
    gate_work: &GateWorkOccurrence,
) -> Result<Exact, GateSettlementError> {
    let closed = gate_population_free_energy(
        anatomy,
        plastic_anatomy,
        plastic_state,
        predecessor_membrane,
        capacitance,
        psi,
        gate_work,
        0,
    )?;
    let open = gate_population_free_energy(
        anatomy,
        plastic_anatomy,
        plastic_state,
        predecessor_membrane,
        capacitance,
        psi,
        gate_work,
        anatomy.population,
    )?;
    Ok(open - closed)
}

/// The receiving gate's own opening window, in whole dissipation-lattice
/// quanta, for the pending local interval.
///
/// Ratified 2026-08-05 (Law 1, threshold-integrated delivery). Nothing here
/// is a new constant: the barrier is this gate's existing exact
/// open-minus-closed free energy with ZERO receptor work (its chemical,
/// plastic-support, electrical, and psi-contact terms), read on the same
/// lattice the gate already dissipates on; the cap is that barrier plus the
/// gate's declared dissipation capacity, which is the most work one
/// conformational settlement can lawfully dissipate once the recovery
/// reaction has freed the gate's full capacity.
///
/// * `opening_threshold_quanta` — the least whole quantum count whose work
///   drives the gate's free energy strictly downhill (`floor(barrier) + 1`).
/// * `window_cap_quanta` — the greatest whole quantum count whose settlement
///   still fits the gate's declared dissipation capacity.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct GateOpeningQuantumWindow {
    pub(crate) opening_threshold_quanta: u128,
    pub(crate) window_cap_quanta: u128,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct GatePopulationOpeningSchedule {
    predecessor_open_population: u128,
    channel_count: u128,
    first_barrier_quanta: Exact,
    barrier_step_quanta: Exact,
}

impl GatePopulationOpeningSchedule {
    pub(crate) fn from_progression(
        predecessor_open_population: u128,
        total_population: u128,
        channel_count: u128,
        first_barrier_quanta: Exact,
        barrier_step_quanta: Exact,
    ) -> Result<Self, GateSettlementError> {
        if predecessor_open_population > total_population
            || channel_count > total_population - predecessor_open_population
            || barrier_step_quanta.is_negative()
        {
            return Err(GateSettlementError::InvalidAnatomy);
        }
        Ok(Self {
            predecessor_open_population,
            channel_count,
            first_barrier_quanta,
            barrier_step_quanta,
        })
    }

    pub(crate) fn predecessor_open_population(&self) -> u128 {
        self.predecessor_open_population
    }

    pub(crate) fn channel_count(&self) -> u128 {
        self.channel_count
    }

    pub(crate) fn first_barrier_quanta(&self) -> &Exact {
        &self.first_barrier_quanta
    }

    pub(crate) fn barrier_step_quanta(&self) -> &Exact {
        &self.barrier_step_quanta
    }

    #[cfg(test)]
    pub(crate) fn expanded_activation_quanta(&self) -> Result<Vec<u128>, GateSettlementError> {
        let mut expanded = Vec::new();
        expanded
            .try_reserve_exact(
                usize::try_from(self.channel_count)
                    .map_err(|_| GateSettlementError::ArithmeticWidth)?,
            )
            .map_err(|_| GateSettlementError::ArithmeticWidth)?;
        for offset in 0..self.channel_count {
            let barrier = &self.first_barrier_quanta
                + &self.barrier_step_quanta * Exact::from_integer(BigInt::from(offset));
            expanded.push(if barrier.is_positive() {
                barrier
                    .floor()
                    .to_integer()
                    .to_u128()
                    .ok_or(GateSettlementError::ArithmeticWidth)?
                    .checked_add(1)
                    .ok_or(GateSettlementError::ArithmeticWidth)?
            } else {
                0
            });
        }
        Ok(expanded)
    }
}

/// Derive the exact sequential activation law for every still-closed channel
/// from this neuron's current material state. Gate free energy is quadratic in
/// collective open population, so successive single-channel barriers form an
/// exact arithmetic progression. Retaining that progression instead of one
/// rational object per channel preserves every barrier without population-
/// proportional allocation or evaluation.
pub(crate) fn gate_population_opening_schedule_with_psi(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    psi: &PsiSettlement,
) -> Result<GatePopulationOpeningSchedule, NeuronPhysicalError> {
    if !anatomy.gate.has_independent_channel_supports()
        || predecessor.gate.open_population > anatomy.gate.population
    {
        return Err(GateSettlementError::GatePopulationExceeded.into());
    }
    let free_dissipation = anatomy
        .gate
        .dissipation_capacity_quanta
        .checked_sub(predecessor.gate.dissipated_quanta)
        .ok_or(GateSettlementError::GatePopulationExceeded)?;
    let closed_population = anatomy.gate.population - predecessor.gate.open_population;
    let schedule_len = closed_population.min(free_dissipation);
    if schedule_len == 0 {
        return GatePopulationOpeningSchedule::from_progression(
            predecessor.gate.open_population,
            anatomy.gate.population,
            0,
            Exact::zero(),
            Exact::zero(),
        )
        .map_err(NeuronPhysicalError::from);
    }
    let zero_work = GateWorkOccurrence::new(Exact::zero());
    let predecessor_energy = gate_population_free_energy(
        &anatomy.gate,
        &anatomy.plastic,
        &predecessor.plastic,
        predecessor.membrane,
        anatomy.capacitance,
        &psi.successor,
        &zero_work,
        predecessor.gate.open_population,
    )?;
    let first_population = predecessor
        .gate
        .open_population
        .checked_add(1)
        .ok_or(GateSettlementError::ArithmeticWidth)?;
    let first_energy = gate_population_free_energy(
        &anatomy.gate,
        &anatomy.plastic,
        &predecessor.plastic,
        predecessor.membrane,
        anatomy.capacitance,
        &psi.successor,
        &zero_work,
        first_population,
    )?;
    let first_barrier_quanta =
        (&first_energy - &predecessor_energy) / &anatomy.gate.dissipation_quantum_zeptojoules;
    let barrier_step_quanta = if schedule_len > 1 {
        let second_population = first_population
            .checked_add(1)
            .ok_or(GateSettlementError::ArithmeticWidth)?;
        let second_energy = gate_population_free_energy(
            &anatomy.gate,
            &anatomy.plastic,
            &predecessor.plastic,
            predecessor.membrane,
            anatomy.capacitance,
            &psi.successor,
            &zero_work,
            second_population,
        )?;
        let second_barrier_quanta =
            (&second_energy - &first_energy) / &anatomy.gate.dissipation_quantum_zeptojoules;
        second_barrier_quanta - &first_barrier_quanta
    } else {
        Exact::zero()
    };
    GatePopulationOpeningSchedule::from_progression(
        predecessor.gate.open_population,
        anatomy.gate.population,
        schedule_len,
        first_barrier_quanta,
        barrier_step_quanta,
    )
    .map_err(NeuronPhysicalError::from)
}

pub(crate) fn gate_opening_quantum_window(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    perspective: JointNeuronPerspective<'_>,
) -> Result<GateOpeningQuantumWindow, NeuronPhysicalError> {
    let mathloom = settle_shared_dsf_mathloom(perspective, anatomy.mathloom)?;
    let psi = settle_psi_krimelack(&anatomy.psi, &predecessor.psi, &mathloom)?;
    gate_opening_quantum_window_with_psi(anatomy, predecessor, &psi)
}

pub(crate) fn gate_opening_quantum_window_with_psi(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    psi: &PsiSettlement,
) -> Result<GateOpeningQuantumWindow, NeuronPhysicalError> {
    let barrier = gate_open_minus_closed_free_energy(
        &anatomy.gate,
        &anatomy.plastic,
        &predecessor.plastic,
        predecessor.membrane,
        anatomy.capacitance,
        &psi.successor,
        &GateWorkOccurrence::new(Exact::zero()),
    )?;
    let barrier_quanta = if barrier.is_positive() {
        (&barrier / &anatomy.gate.dissipation_quantum_zeptojoules)
            .floor()
            .to_integer()
            .to_u128()
            .ok_or(GateSettlementError::ArithmeticWidth)?
    } else {
        0
    };
    let opening_threshold_quanta = barrier_quanta
        .checked_add(1)
        .ok_or(GateSettlementError::ArithmeticWidth)?;
    let window_cap_quanta = barrier_quanta
        .checked_add(anatomy.gate.dissipation_capacity_quanta)
        .ok_or(GateSettlementError::ArithmeticWidth)?;
    Ok(GateOpeningQuantumWindow {
        opening_threshold_quanta,
        window_cap_quanta,
    })
}

/// Exact recovery reaction extents needed for every currently downhill gate
/// conformation to settle under the pending local interval. This is derived
/// from the same free-energy expression and dissipation quantum used by gate
/// settlement. It introduces no firing threshold or elapsed-time rule.
pub(crate) fn required_gate_recovery_extent_for_interval(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    perspective: JointNeuronPerspective<'_>,
    gate_work: &GateWorkOccurrence,
) -> Result<u128, NeuronPhysicalError> {
    if predecessor.gate.open_population > anatomy.gate.population {
        return Err(GateSettlementError::GatePopulationExceeded.into());
    }
    let mathloom = settle_shared_dsf_mathloom(perspective, anatomy.mathloom)?;
    let psi = settle_psi_krimelack(&anatomy.psi, &predecessor.psi, &mathloom)?;
    required_gate_recovery_extent_for_interval_with_psi(anatomy, predecessor, gate_work, &psi)
}

pub(crate) fn required_gate_recovery_extent_for_interval_with_psi(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    gate_work: &GateWorkOccurrence,
    psi: &PsiSettlement,
) -> Result<u128, NeuronPhysicalError> {
    let settlement = select_gate_population_settlement(
        &anatomy.gate,
        &anatomy.plastic,
        &predecessor.plastic,
        &predecessor.gate,
        predecessor.membrane,
        anatomy.capacitance,
        &psi.successor,
        gate_work,
        None,
    )?;
    let Some(settlement) = settlement else {
        return Ok(0);
    };
    let required_quanta = settlement.released_quanta;
    let free_quanta = anatomy
        .gate
        .dissipation_capacity_quanta
        .checked_sub(predecessor.gate.dissipated_quanta)
        .ok_or(GateSettlementError::GatePopulationExceeded)?;
    let missing_quanta = required_quanta.saturating_sub(free_quanta);
    if missing_quanta == 0 {
        return Ok(0);
    }
    let gate_lane = anatomy
        .recovery
        .lane(RecoveryLaneAddress::Gate)
        .ok_or(RecoveryError::AnatomyWidth)?;
    let exported_heat_per_extent = gate_lane.stoichiometry().3;
    let rounded = missing_quanta
        .checked_add(exported_heat_per_extent - 1)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    Ok(rounded / exported_heat_per_extent)
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct RecoveryOnlySettlement {
    pub(crate) successor: NeuronPhysicalState,
    pub(crate) extent: u128,
}

/// Execute only the already-defined local recovery reaction. Fluid exchange is
/// a distinct control-volume settlement and must debit/credit its own material.
pub(crate) fn settle_recovery_only(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    contact: RecoveryContact<'_>,
) -> Result<RecoveryOnlySettlement, NeuronPhysicalError> {
    let mut successor = predecessor.clone();
    let recovery = settle_recovery(&anatomy.recovery, &mut successor, contact)?;
    Ok(RecoveryOnlySettlement {
        successor,
        extent: recovery.extent,
    })
}

fn move_inter_neuron_carriers(
    predecessor: CarrierReservoirs,
    outward: i128,
) -> Result<CarrierReservoirs, GateSettlementError> {
    // NOT BOUNDED HERE, AND THAT IS DELIBERATE (2026-08-08).
    //
    // An inter-neuron flow is EQUAL AND OPPOSITE between two neurons. Bounding
    // it at this end alone was tried and her own runtime caught it
    // immediately: MaterialConservation. A depleted sender must be bounded
    // where the contact charge is computed FOR BOTH SIDES, so the receiver
    // takes exactly what the sender could give. Until that is done, this path
    // still refuses when a neuron is empty — which is honest, and far better
    // than silently unbalancing her.
    let amount = outward.unsigned_abs();
    let intracellular = if outward >= 0 {
        predecessor
            .intracellular
            .checked_sub(amount)
            .ok_or(GateSettlementError::InsufficientCarrierMaterial)?
    } else {
        predecessor
            .intracellular
            .checked_add(amount)
            .ok_or(GateSettlementError::ArithmeticWidth)?
    };
    Ok(CarrierReservoirs {
        intracellular,
        extracellular: predecessor.extracellular,
    })
}

fn open_minus_closed_support_energy(
    anatomy: &PlasticSupportAnatomy,
    state: &PlasticSupportState,
) -> Result<ExactRational, PlasticityError> {
    let closed_strain = anatomy
        .closed_coordinate_nanometres
        .checked_sub(state.rest_length_nanometres)?
        .checked_div(state.rest_length_nanometres)?;
    let open_strain = anatomy
        .open_coordinate_nanometres
        .checked_sub(state.rest_length_nanometres)?
        .checked_div(state.rest_length_nanometres)?;
    let closed_energy = anatomy
        .elastic_energy_scale_zeptojoules
        .checked_mul(closed_strain)?
        .checked_mul(closed_strain)?
        .checked_div_unsigned(2)?;
    let open_energy = anatomy
        .elastic_energy_scale_zeptojoules
        .checked_mul(open_strain)?
        .checked_mul(open_strain)?
        .checked_div_unsigned(2)?;
    Ok(open_energy.checked_sub(closed_energy)?)
}

fn rational_to_exact(value: ExactRational) -> Exact {
    let (numerator, denominator) = value.parts();
    Exact::new(BigInt::from(numerator), BigInt::from(denominator))
}

/// Narrow an exact residue back to the resident fixed-width rational the
/// neuron persists.  A value that will not fit is REFUSED, never rounded —
/// same discipline as `receptor_quantum_delivery::big_to_exact_rational`,
/// which refuses `ResidueWidth` rather than approximate a retained residue.
fn exact_to_rational(value: &Exact) -> Result<ExactRational, NeuronPhysicalError> {
    let numerator = value.numer().to_i128().ok_or(NeuronPhysicalError::Gate(
        GateSettlementError::ArithmeticWidth,
    ))?;
    let denominator = value.denom().to_u128().ok_or(NeuronPhysicalError::Gate(
        GateSettlementError::ArithmeticWidth,
    ))?;
    ExactRational::new(numerator, denominator)
        .map_err(|_| NeuronPhysicalError::Gate(GateSettlementError::ArithmeticWidth))
}

fn move_carriers(
    predecessor: CarrierReservoirs,
    outward: i128,
) -> Result<CarrierReservoirs, GateSettlementError> {
    let amount = outward.unsigned_abs();
    if outward >= 0 {
        if amount > predecessor.intracellular {
            return Err(GateSettlementError::InsufficientCarrierMaterial);
        }
        Ok(CarrierReservoirs {
            intracellular: predecessor.intracellular - amount,
            extracellular: predecessor
                .extracellular
                .checked_add(amount)
                .ok_or(GateSettlementError::ArithmeticWidth)?,
        })
    } else {
        if amount > predecessor.extracellular {
            return Err(GateSettlementError::InsufficientCarrierMaterial);
        }
        Ok(CarrierReservoirs {
            intracellular: predecessor
                .intracellular
                .checked_add(amount)
                .ok_or(GateSettlementError::ArithmeticWidth)?,
            extracellular: predecessor.extracellular - amount,
        })
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct RecoveryContact<'a> {
    psi_catalyst_quanta: &'a [u128],
    gate_catalyst_quanta: u128,
    plastic_catalyst_quanta: u128,
}

impl<'a> RecoveryContact<'a> {
    pub(crate) fn new(
        psi_catalyst_quanta: &'a [u128],
        gate_catalyst_quanta: u128,
        plastic_catalyst_quanta: u128,
    ) -> Self {
        Self {
            psi_catalyst_quanta,
            gate_catalyst_quanta,
            plastic_catalyst_quanta,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct DnaExpressionContact {
    catalyst_quanta: u128,
}

impl DnaExpressionContact {
    pub(crate) fn new(catalyst_quanta: u128) -> Self {
        Self { catalyst_quanta }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct RecoverySettlement {
    extent: u128,
}

fn settle_recovery(
    anatomy: &RecoveryAnatomy,
    state: &mut NeuronPhysicalState,
    contact: RecoveryContact<'_>,
) -> Result<RecoverySettlement, RecoveryError> {
    if contact.psi_catalyst_quanta.len() != anatomy.psi_lanes.len()
        || state.recovery.psi_lanes.len() != anatomy.psi_lanes.len()
        || state.psi.rings.len() != anatomy.psi_lanes.len()
    {
        return Err(RecoveryError::AnatomyWidth);
    }
    let state = Arc::make_mut(&mut state.0);
    let mut total_extent = 0_u128;
    for lane_index in 0..anatomy.psi_lanes.len() {
        let extent = settle_recovery_lane(
            anatomy.psi_lanes[lane_index],
            &mut state.psi.rings[lane_index].dissipated_quanta,
            &mut state.recovery.psi_lanes[lane_index],
            contact.psi_catalyst_quanta[lane_index],
        )?;
        total_extent = total_extent
            .checked_add(extent)
            .ok_or(RecoveryError::ArithmeticWidth)?;
    }
    let gate_extent = settle_recovery_lane(
        anatomy.gate_lane,
        &mut state.gate.dissipated_quanta,
        &mut state.recovery.gate_lane,
        contact.gate_catalyst_quanta,
    )?;
    total_extent = total_extent
        .checked_add(gate_extent)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    let plastic_extent = settle_recovery_lane(
        anatomy.plastic_lane,
        &mut state.plastic.dissipated_quanta,
        &mut state.recovery.plastic_lane,
        contact.plastic_catalyst_quanta,
    )?;
    total_extent = total_extent
        .checked_add(plastic_extent)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    Ok(RecoverySettlement {
        extent: total_extent,
    })
}

fn settle_recovery_lane(
    anatomy: RecoveryLaneAnatomy,
    dissipated_quanta: &mut u128,
    state: &mut RecoveryLaneState,
    catalyst_quanta: u128,
) -> Result<u128, RecoveryError> {
    let spent_free = anatomy
        .spent_capacity
        .checked_sub(state.spent_quanta)
        .ok_or(RecoveryError::InvalidAnatomy)?;
    let heat_free = anatomy
        .exported_heat_capacity
        .checked_sub(state.exported_heat_quanta)
        .ok_or(RecoveryError::InvalidAnatomy)?;
    let extent = (catalyst_quanta / anatomy.catalyst_per_extent)
        .min(state.fuel_quanta / anatomy.fuel_per_extent)
        .min(spent_free / anatomy.spent_per_extent)
        .min(*dissipated_quanta / anatomy.exported_heat_per_extent)
        .min(heat_free / anatomy.exported_heat_per_extent);
    if extent == 0 {
        return Ok(0);
    }
    let fuel = extent
        .checked_mul(anatomy.fuel_per_extent)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    let spent = extent
        .checked_mul(anatomy.spent_per_extent)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    let heat = extent
        .checked_mul(anatomy.exported_heat_per_extent)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    state.fuel_quanta -= fuel;
    state.spent_quanta = state
        .spent_quanta
        .checked_add(spent)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    *dissipated_quanta -= heat;
    state.exported_heat_quanta = state
        .exported_heat_quanta
        .checked_add(heat)
        .ok_or(RecoveryError::ArithmeticWidth)?;
    Ok(extent)
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct DnaExpressionSettlement {
    extent: u128,
}

fn settle_dna_expression(
    anatomy: DnaExpressionAnatomy,
    state: &mut DnaExpressionState,
    contact: DnaExpressionContact,
) -> Result<DnaExpressionSettlement, DnaExpressionError> {
    let product_free = anatomy
        .product_capacity
        .checked_sub(state.expressed_product_quanta)
        .ok_or(DnaExpressionError::InvalidAnatomy)?;
    let waste_free = anatomy
        .waste_capacity
        .checked_sub(state.waste_quanta)
        .ok_or(DnaExpressionError::InvalidAnatomy)?;
    let extent = (contact.catalyst_quanta / anatomy.catalyst_per_extent)
        .min(state.substrate_quanta / anatomy.substrate_per_extent)
        .min(state.fuel_quanta / anatomy.fuel_per_extent)
        .min(product_free / anatomy.product_per_extent)
        .min(waste_free / anatomy.waste_per_extent);
    if extent == 0 {
        return Ok(DnaExpressionSettlement { extent: 0 });
    }
    let substrate = extent
        .checked_mul(anatomy.substrate_per_extent)
        .ok_or(DnaExpressionError::ArithmeticWidth)?;
    let fuel = extent
        .checked_mul(anatomy.fuel_per_extent)
        .ok_or(DnaExpressionError::ArithmeticWidth)?;
    let product = extent
        .checked_mul(anatomy.product_per_extent)
        .ok_or(DnaExpressionError::ArithmeticWidth)?;
    let waste = extent
        .checked_mul(anatomy.waste_per_extent)
        .ok_or(DnaExpressionError::ArithmeticWidth)?;
    state.substrate_quanta -= substrate;
    state.fuel_quanta -= fuel;
    state.expressed_product_quanta = state
        .expressed_product_quanta
        .checked_add(product)
        .ok_or(DnaExpressionError::ArithmeticWidth)?;
    state.waste_quanta = state
        .waste_quanta
        .checked_add(waste)
        .ok_or(DnaExpressionError::ArithmeticWidth)?;
    Ok(DnaExpressionSettlement { extent })
}

#[derive(Clone, Debug)]
pub(crate) struct NeuronIntervalInput<'a> {
    pub(crate) perspective: JointNeuronPerspective<'a>,
    pub(crate) gate_work: GateWorkOccurrence,
    pub(crate) interval_microseconds: u32,
    pub(crate) recovery: RecoveryContact<'a>,
    pub(crate) dna_expression: DnaExpressionContact,
    /// `Some(residue)` when this interval's gate work is a quantized optical
    /// delivery (ratified 2026-08-05): the exact sub-quantum remainder to
    /// retain in the successor state after the whole-quantum delivery carried
    /// by `gate_work`. `None` for every non-optical delivery: the predecessor
    /// residue is carried through unchanged.
    pub(crate) receptor_successor_residue: Option<ExactRational>,
    /// The one local Psi/Krimelack settlement already derived from this
    /// interval's complete field and predecessor. Gate-window, recovery and
    /// membrane consequences consume the same physical result rather than
    /// re-settling it three times.
    pub(crate) prepared_psi: Option<PsiSettlement>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct QuiescentNeuronState {
    state: NeuronPhysicalState,
}

impl QuiescentNeuronState {
    pub(crate) fn state(&self) -> &NeuronPhysicalState {
        &self.state
    }

    pub(crate) fn from_state(state: NeuronPhysicalState) -> Self {
        Self { state }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub(crate) enum PhysicalStateCoordinate {
    PsiWinding(usize),
    PsiDissipatedEnergy(usize),
    GateOpenPopulation,
    GateDissipatedEnergy,
    MembraneSeparatedCharge,
    MembraneCarrierPhase,
    ConductancePathCarrierPhase(usize),
    IntracellularCarrier,
    ExtracellularCarrier,
    RecoveryPsiFuel(usize),
    RecoveryPsiSpent(usize),
    RecoveryPsiExportedHeat(usize),
    RecoveryGateFuel,
    RecoveryGateSpent,
    RecoveryGateExportedHeat,
    PlasticRestLength,
    PlasticDissipatedEnergy,
    RecoveryPlasticFuel,
    RecoveryPlasticSpent,
    RecoveryPlasticExportedHeat,
    DnaSubstrate,
    DnaFuel,
    DnaExpressedProduct,
    DnaWaste,
    /// Exact sub-quantum receptor material retained between causal
    /// intervals. The same accumulator is used by sight, sound, touch, smell,
    /// and taste; the coordinate therefore names the physical mechanism, not
    /// one sense. Its existing wire tag remains 24.
    ReceptorQuantumResidue,
    /// The retained sub-quantum membrane-return work residue (exact rest-cost
    /// law, 2026-08-06).  It is part of the neuron's persisted physical state,
    /// so a fractal — the sparse difference between the pre-experience and
    /// post-experience quiescent states — must be able to carry it, or a
    /// restored state would silently differ from the settled one.  Appended
    /// LAST so every pre-existing coordinate keeps its wire tag and its sort
    /// position; a body whose residue never moved encodes exactly as before.
    MembraneReturnWorkResidue,
    /// Exact sub-quantum plastic return work retained across intervals.
    /// Appended last so every existing sparse-coordinate wire tag remains
    /// unchanged.
    PlasticDissipationResidue,
    /// Exact sub-quantum gate dissipation retained across intervals.
    /// Appended last so all prior sparse-coordinate wire tags remain stable.
    GateDissipationResidue,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct ExactSignedDelta {
    negative: bool,
    magnitude: u128,
}

impl ExactSignedDelta {
    pub(crate) fn from_parts(negative: bool, magnitude: u128) -> Option<Self> {
        (magnitude != 0).then_some(Self {
            negative,
            magnitude,
        })
    }

    pub(crate) fn parts(self) -> (bool, u128) {
        (self.negative, self.magnitude)
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) enum ExactPhysicalStateDelta {
    Integral(ExactSignedDelta),
    Rational(ExactRational),
    Energy(Exact),
}

impl ExactPhysicalStateDelta {
    fn is_zero(&self) -> bool {
        match self {
            Self::Integral(delta) => delta.magnitude == 0,
            Self::Rational(delta) => delta.parts().0 == 0,
            Self::Energy(delta) => delta.is_zero(),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PhysicalStateDeltaEntry {
    coordinate: PhysicalStateCoordinate,
    delta: ExactPhysicalStateDelta,
}

impl PhysicalStateDeltaEntry {
    pub(crate) fn new(
        coordinate: PhysicalStateCoordinate,
        delta: ExactPhysicalStateDelta,
    ) -> Option<Self> {
        (!delta.is_zero() && coordinate_accepts_delta(coordinate, &delta))
            .then_some(Self { coordinate, delta })
    }

    pub(crate) fn coordinate(&self) -> PhysicalStateCoordinate {
        self.coordinate
    }

    pub(crate) fn delta(&self) -> ExactPhysicalStateDelta {
        self.delta.clone()
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct SparsePhysicalStateDelta {
    entries: Box<[PhysicalStateDeltaEntry]>,
}

impl SparsePhysicalStateDelta {
    pub(crate) fn from_canonical_entries(entries: Vec<PhysicalStateDeltaEntry>) -> Option<Self> {
        if entries.is_empty()
            || entries.iter().any(|entry| {
                entry.delta.is_zero() || !coordinate_accepts_delta(entry.coordinate, &entry.delta)
            })
            || entries
                .windows(2)
                .any(|pair| pair[0].coordinate >= pair[1].coordinate)
        {
            return None;
        }
        Some(Self {
            entries: entries.into_boxed_slice(),
        })
    }

    pub(crate) fn entries(&self) -> &[PhysicalStateDeltaEntry] {
        &self.entries
    }

    pub(crate) fn exact_delta(
        &self,
        coordinate: PhysicalStateCoordinate,
    ) -> Option<ExactPhysicalStateDelta> {
        self.entries
            .binary_search_by_key(&coordinate, |entry| entry.coordinate)
            .ok()
            .map(|index| self.entries[index].delta.clone())
    }

    pub(crate) fn resident_bytes(&self) -> Option<usize> {
        let fixed = core::mem::size_of::<Self>().checked_add(
            self.entries
                .len()
                .checked_mul(core::mem::size_of::<PhysicalStateDeltaEntry>())?,
        )?;
        self.entries.iter().try_fold(fixed, |total, entry| {
            let extra = match &entry.delta {
                ExactPhysicalStateDelta::Energy(value) => value
                    .numer()
                    .to_signed_bytes_le()
                    .len()
                    .checked_add(value.denom().to_signed_bytes_le().len())?,
                ExactPhysicalStateDelta::Integral(_) | ExactPhysicalStateDelta::Rational(_) => 0,
            };
            total.checked_add(extra)
        })
    }
}

fn coordinate_accepts_delta(
    coordinate: PhysicalStateCoordinate,
    delta: &ExactPhysicalStateDelta,
) -> bool {
    matches!(
        (coordinate, delta),
        (
            PhysicalStateCoordinate::MembraneCarrierPhase
                | PhysicalStateCoordinate::ConductancePathCarrierPhase(_)
                | PhysicalStateCoordinate::PlasticRestLength
                | PhysicalStateCoordinate::ReceptorQuantumResidue
                | PhysicalStateCoordinate::MembraneReturnWorkResidue
                | PhysicalStateCoordinate::PlasticDissipationResidue
                | PhysicalStateCoordinate::GateDissipationResidue,
            &ExactPhysicalStateDelta::Rational(_)
        ) | (
            PhysicalStateCoordinate::GateDissipationResidue
                | PhysicalStateCoordinate::PlasticDissipationResidue,
            &ExactPhysicalStateDelta::Energy(_)
        ) | (
            PhysicalStateCoordinate::PsiWinding(_)
                | PhysicalStateCoordinate::PsiDissipatedEnergy(_)
                | PhysicalStateCoordinate::GateOpenPopulation
                | PhysicalStateCoordinate::GateDissipatedEnergy
                | PhysicalStateCoordinate::MembraneSeparatedCharge
                | PhysicalStateCoordinate::IntracellularCarrier
                | PhysicalStateCoordinate::ExtracellularCarrier
                | PhysicalStateCoordinate::RecoveryPsiFuel(_)
                | PhysicalStateCoordinate::RecoveryPsiSpent(_)
                | PhysicalStateCoordinate::RecoveryPsiExportedHeat(_)
                | PhysicalStateCoordinate::RecoveryGateFuel
                | PhysicalStateCoordinate::RecoveryGateSpent
                | PhysicalStateCoordinate::RecoveryGateExportedHeat
                | PhysicalStateCoordinate::PlasticDissipatedEnergy
                | PhysicalStateCoordinate::RecoveryPlasticFuel
                | PhysicalStateCoordinate::RecoveryPlasticSpent
                | PhysicalStateCoordinate::RecoveryPlasticExportedHeat
                | PhysicalStateCoordinate::DnaSubstrate
                | PhysicalStateCoordinate::DnaFuel
                | PhysicalStateCoordinate::DnaExpressedProduct
                | PhysicalStateCoordinate::DnaWaste,
            &ExactPhysicalStateDelta::Integral(_)
        )
    )
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct PostExperienceSettlement {
    pub(crate) quiescent: QuiescentNeuronState,
    pub(crate) fractal: Option<SparsePhysicalStateDelta>,
    pub(crate) plasticity: PlasticityAvailability,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub(crate) struct ExtendedIntervalSettlement {
    pub(crate) successor: NeuronPhysicalState,
    pub(crate) exported_heat_zeptojoules: Exact,
    /// Exact transient electrical emission from this interval: the number of
    /// physical gate channels that changed from closed to open. The gate
    /// population remains the sole authority; this value is never persisted
    /// and is never a neuronal fractal.
    pub(crate) newly_opened_gate_channels: u128,
    pub(crate) quiescent: bool,
}

fn settle_extended_interval(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    input: NeuronIntervalInput<'_>,
) -> Result<ExtendedIntervalSettlement, NeuronPhysicalError> {
    settle_extended_interval_with_contact(anatomy, predecessor, input, 0)
}

pub(crate) fn settle_extended_interval_with_contact(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    input: NeuronIntervalInput<'_>,
    inter_neuron_outward_elementary_charges: i128,
) -> Result<ExtendedIntervalSettlement, NeuronPhysicalError> {
    let physical = settle_neuron_physical_interval_with_contact(
        anatomy,
        predecessor,
        input.perspective,
        input.gate_work,
        input.interval_microseconds,
        inter_neuron_outward_elementary_charges,
        input.prepared_psi,
    )?;
    let predecessor_open_population = predecessor.gate.open_population();
    let successor_open_population = physical.successor.gate.open_population();
    let newly_opened_gate_channels = if successor_open_population > predecessor_open_population {
        successor_open_population
            .checked_sub(predecessor_open_population)
            .ok_or(GateSettlementError::ArithmeticWidth)?
    } else {
        0
    };
    let psi_changed = physical.psi.changed_rings != 0;
    let gate_changed = physical.successor.gate != predecessor.gate;
    let membrane_active = physical
        .gate_membrane
        .membrane
        .path_currents_picoamperes
        .iter()
        .any(|current| current.parts().0 != 0)
        || physical.successor.membrane != predecessor.membrane;
    let exported_heat_zeptojoules = physical.gate_membrane.exported_heat_zeptojoules.clone();
    let mut successor = physical.successor;
    // The retained sub-quantum residue is a receptor accumulator, not a
    // settled physical coordinate: it does not enter the quiescence
    // predicate.  The ratified law changes WHAT energy arrives, nothing else.
    if let Some(residue) = input.receptor_successor_residue {
        successor.receptor_quantum_residue = residue;
    }
    let plastic = settle_plastic_support(
        &anatomy.plastic,
        &predecessor.plastic,
        anatomy.gate.population,
        successor.gate.open_population,
    )?;
    successor.plastic = plastic.successor;
    let recovery = settle_recovery(&anatomy.recovery, &mut successor, input.recovery)?;
    let dna = settle_dna_expression(
        anatomy.dna_expression,
        &mut successor.dna_expression,
        input.dna_expression,
    )?;
    Ok(ExtendedIntervalSettlement {
        successor,
        exported_heat_zeptojoules,
        newly_opened_gate_channels,
        quiescent: !psi_changed
            && !gate_changed
            && !membrane_active
            && !plastic.changed
            && recovery.extent == 0
            && dna.extent == 0,
    })
}

/// Settle only along the supplied exact physical interval sequence. The
/// sequence is the causal occurrence, not a timeout. If it ends before an
/// unchanged zero-current interval, no quiescence or fractal is claimed.
pub(crate) fn settle_to_quiescence(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    intervals: &[NeuronIntervalInput<'_>],
) -> Result<QuiescentNeuronState, NeuronPhysicalError> {
    let mut state = predecessor.clone();
    for input in intervals {
        let settled = settle_extended_interval(anatomy, &state, input.clone())?;
        state = settled.successor;
        if settled.quiescent {
            return Ok(QuiescentNeuronState { state });
        }
    }
    Err(NeuronPhysicalError::SequenceEndedBeforeQuiescence)
}

pub(crate) fn settle_experience_to_quiescence(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &QuiescentNeuronState,
    perturbation: NeuronIntervalInput<'_>,
    post_experience_intervals: &[NeuronIntervalInput<'_>],
) -> Result<PostExperienceSettlement, NeuronPhysicalError> {
    let first = settle_extended_interval(anatomy, &predecessor.state, perturbation)?;
    let quiescent = if first.quiescent {
        QuiescentNeuronState {
            state: first.successor,
        }
    } else {
        settle_to_quiescence(anatomy, &first.successor, post_experience_intervals)?
    };
    let fractal = sparse_physical_state_delta(&predecessor.state, &quiescent.state)?;
    Ok(PostExperienceSettlement {
        quiescent,
        fractal,
        plasticity: PlasticityAvailability::ExecutedExactReturnMapping,
    })
}

pub(crate) fn sparse_physical_state_delta(
    predecessor: &NeuronPhysicalState,
    successor: &NeuronPhysicalState,
) -> Result<Option<SparsePhysicalStateDelta>, NeuronPhysicalError> {
    if predecessor.shares_physical_body_with(successor) {
        return Ok(None);
    }
    if predecessor.psi.rings.len() != successor.psi.rings.len()
        || predecessor.recovery.psi_lanes.len() != successor.recovery.psi_lanes.len()
    {
        return Err(NeuronPhysicalError::AnatomyMismatch);
    }
    let capacity = predecessor
        .psi
        .rings
        .len()
        .checked_mul(5)
        .and_then(|count| count.checked_add(23))
        .ok_or(NeuronPhysicalError::AnatomyMismatch)?;
    let mut entries = Vec::new();
    entries
        .try_reserve_exact(capacity)
        .map_err(|_| NeuronPhysicalError::AnatomyMismatch)?;
    for index in 0..predecessor.psi.rings.len() {
        push_i128_delta(
            &mut entries,
            PhysicalStateCoordinate::PsiWinding(index),
            predecessor.psi.rings[index].winding as i8 as i128,
            successor.psi.rings[index].winding as i8 as i128,
        );
        push_u128_delta(
            &mut entries,
            PhysicalStateCoordinate::PsiDissipatedEnergy(index),
            predecessor.psi.rings[index].dissipated_quanta,
            successor.psi.rings[index].dissipated_quanta,
        );
        let prior_recovery = predecessor.recovery.psi_lanes[index];
        let next_recovery = successor.recovery.psi_lanes[index];
        push_u128_delta(
            &mut entries,
            PhysicalStateCoordinate::RecoveryPsiFuel(index),
            prior_recovery.fuel_quanta,
            next_recovery.fuel_quanta,
        );
        push_u128_delta(
            &mut entries,
            PhysicalStateCoordinate::RecoveryPsiSpent(index),
            prior_recovery.spent_quanta,
            next_recovery.spent_quanta,
        );
        push_u128_delta(
            &mut entries,
            PhysicalStateCoordinate::RecoveryPsiExportedHeat(index),
            prior_recovery.exported_heat_quanta,
            next_recovery.exported_heat_quanta,
        );
    }
    push_u128_delta(
        &mut entries,
        PhysicalStateCoordinate::GateOpenPopulation,
        predecessor.gate.open_population,
        successor.gate.open_population,
    );
    push_u128_delta(
        &mut entries,
        PhysicalStateCoordinate::GateDissipatedEnergy,
        predecessor.gate.dissipated_quanta,
        successor.gate.dissipated_quanta,
    );
    push_energy_delta(
        &mut entries,
        PhysicalStateCoordinate::GateDissipationResidue,
        predecessor.gate.dissipation_residue_zeptojoules.energy(),
        successor.gate.dissipation_residue_zeptojoules.energy(),
    );
    push_i128_delta(
        &mut entries,
        PhysicalStateCoordinate::MembraneSeparatedCharge,
        predecessor
            .membrane
            .membrane()
            .separated_elementary_charges(),
        successor.membrane.membrane().separated_elementary_charges(),
    );
    let prior_membrane_phase = predecessor.membrane.membrane().carrier_phase().parts();
    let next_membrane_phase = successor.membrane.membrane().carrier_phase().parts();
    push_rational_delta(
        &mut entries,
        PhysicalStateCoordinate::MembraneCarrierPhase,
        ExactRational::new(prior_membrane_phase.0, prior_membrane_phase.1)?,
        ExactRational::new(next_membrane_phase.0, next_membrane_phase.1)?,
    )?;
    for (index, (prior_phase, next_phase)) in predecessor
        .membrane
        .path_carrier_phases()
        .iter()
        .zip(successor.membrane.path_carrier_phases().iter())
        .enumerate()
    {
        let prior = prior_phase.parts();
        let next = next_phase.parts();
        push_rational_delta(
            &mut entries,
            PhysicalStateCoordinate::ConductancePathCarrierPhase(index),
            ExactRational::new(prior.0, prior.1)?,
            ExactRational::new(next.0, next.1)?,
        )?;
    }
    push_u128_delta(
        &mut entries,
        PhysicalStateCoordinate::IntracellularCarrier,
        predecessor.carriers.intracellular,
        successor.carriers.intracellular,
    );
    push_u128_delta(
        &mut entries,
        PhysicalStateCoordinate::ExtracellularCarrier,
        predecessor.carriers.extracellular,
        successor.carriers.extracellular,
    );
    push_recovery_gate_delta(&mut entries, predecessor, successor);
    push_dna_delta(
        &mut entries,
        predecessor.dna_expression,
        successor.dna_expression,
    );
    push_rational_delta(
        &mut entries,
        PhysicalStateCoordinate::PlasticRestLength,
        predecessor.plastic.rest_length_nanometres,
        successor.plastic.rest_length_nanometres,
    )?;
    push_rational_delta(
        &mut entries,
        PhysicalStateCoordinate::ReceptorQuantumResidue,
        predecessor.receptor_quantum_residue,
        successor.receptor_quantum_residue,
    )?;
    push_rational_delta(
        &mut entries,
        PhysicalStateCoordinate::MembraneReturnWorkResidue,
        predecessor.membrane_return_work_residue,
        successor.membrane_return_work_residue,
    )?;
    push_energy_delta(
        &mut entries,
        PhysicalStateCoordinate::PlasticDissipationResidue,
        predecessor.plastic.dissipation_residue_zeptojoules.energy(),
        successor.plastic.dissipation_residue_zeptojoules.energy(),
    );
    push_u128_delta(
        &mut entries,
        PhysicalStateCoordinate::PlasticDissipatedEnergy,
        predecessor.plastic.dissipated_quanta,
        successor.plastic.dissipated_quanta,
    );
    push_recovery_plastic_delta(&mut entries, predecessor, successor);
    entries.sort_unstable_by_key(|entry| entry.coordinate);
    Ok(SparsePhysicalStateDelta::from_canonical_entries(entries))
}

/// Project one exact whole-neuron change onto the retained structure that can
/// lawfully become a neuronal fractal.
///
/// The complete state also contains transient working physics and metabolic
/// ledgers. Those values persist for exact continuation after restart, but
/// persistence does not make membrane charge, carrier phase, receptor
/// residue, dissipation, or fuel/spent/heat into memory. A receptor's exact
/// finite post-quiescence channel population is retained physical anatomy
/// state: discarding it would collapse the graded collective-coordinate
/// settlement back to Boolean experience before formation. The structural
/// coordinates currently present in the definitive neuron are its
/// Psi/Krimelack winding, settled channel population, plastic rest geometry,
/// and expressed DNA product.
/// Future synaptic/coupling structure belongs here when such a coordinate
/// actually exists; contact carrier phase does not.
pub(crate) fn sparse_retained_physical_state_delta(
    predecessor: &NeuronPhysicalState,
    successor: &NeuronPhysicalState,
) -> Result<Option<SparsePhysicalStateDelta>, NeuronPhysicalError> {
    let Some(delta) = sparse_physical_state_delta(predecessor, successor)? else {
        return Ok(None);
    };
    let retained = delta
        .entries()
        .iter()
        .cloned()
        .filter(|entry| retained_physical_state_coordinate(entry.coordinate()))
        .collect::<Vec<_>>();
    Ok(SparsePhysicalStateDelta::from_canonical_entries(retained))
}

pub(crate) fn retained_physical_state_coordinate(coordinate: PhysicalStateCoordinate) -> bool {
    matches!(
        coordinate,
        PhysicalStateCoordinate::PsiWinding(_)
            | PhysicalStateCoordinate::GateOpenPopulation
            | PhysicalStateCoordinate::PlasticRestLength
            | PhysicalStateCoordinate::DnaExpressedProduct
            | PhysicalStateCoordinate::ReceptorQuantumResidue
    )
}

fn push_recovery_gate_delta(
    entries: &mut Vec<PhysicalStateDeltaEntry>,
    predecessor: &NeuronPhysicalState,
    successor: &NeuronPhysicalState,
) {
    let prior = predecessor.recovery.gate_lane;
    let next = successor.recovery.gate_lane;
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::RecoveryGateFuel,
        prior.fuel_quanta,
        next.fuel_quanta,
    );
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::RecoveryGateSpent,
        prior.spent_quanta,
        next.spent_quanta,
    );
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::RecoveryGateExportedHeat,
        prior.exported_heat_quanta,
        next.exported_heat_quanta,
    );
}

fn push_recovery_plastic_delta(
    entries: &mut Vec<PhysicalStateDeltaEntry>,
    predecessor: &NeuronPhysicalState,
    successor: &NeuronPhysicalState,
) {
    let prior = predecessor.recovery.plastic_lane;
    let next = successor.recovery.plastic_lane;
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::RecoveryPlasticFuel,
        prior.fuel_quanta,
        next.fuel_quanta,
    );
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::RecoveryPlasticSpent,
        prior.spent_quanta,
        next.spent_quanta,
    );
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::RecoveryPlasticExportedHeat,
        prior.exported_heat_quanta,
        next.exported_heat_quanta,
    );
}

fn push_dna_delta(
    entries: &mut Vec<PhysicalStateDeltaEntry>,
    predecessor: DnaExpressionState,
    successor: DnaExpressionState,
) {
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::DnaSubstrate,
        predecessor.substrate_quanta,
        successor.substrate_quanta,
    );
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::DnaFuel,
        predecessor.fuel_quanta,
        successor.fuel_quanta,
    );
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::DnaExpressedProduct,
        predecessor.expressed_product_quanta,
        successor.expressed_product_quanta,
    );
    push_u128_delta(
        entries,
        PhysicalStateCoordinate::DnaWaste,
        predecessor.waste_quanta,
        successor.waste_quanta,
    );
}

fn push_u128_delta(
    entries: &mut Vec<PhysicalStateDeltaEntry>,
    coordinate: PhysicalStateCoordinate,
    predecessor: u128,
    successor: u128,
) {
    if predecessor == successor {
        return;
    }
    entries.push(PhysicalStateDeltaEntry {
        coordinate,
        delta: ExactPhysicalStateDelta::Integral(ExactSignedDelta {
            negative: successor < predecessor,
            magnitude: predecessor.abs_diff(successor),
        }),
    });
}

fn push_rational_delta(
    entries: &mut Vec<PhysicalStateDeltaEntry>,
    coordinate: PhysicalStateCoordinate,
    predecessor: ExactRational,
    successor: ExactRational,
) -> Result<(), NeuronPhysicalError> {
    let delta = successor.checked_sub(predecessor)?;
    if delta.parts().0 != 0 {
        entries.push(PhysicalStateDeltaEntry {
            coordinate,
            delta: ExactPhysicalStateDelta::Rational(delta),
        });
    }
    Ok(())
}

fn push_energy_delta(
    entries: &mut Vec<PhysicalStateDeltaEntry>,
    coordinate: PhysicalStateCoordinate,
    predecessor: &Exact,
    successor: &Exact,
) {
    let delta = successor - predecessor;
    if !delta.is_zero() {
        let fixed = delta
            .numer()
            .to_i128()
            .zip(delta.denom().to_u128())
            .and_then(|(numerator, denominator)| ExactRational::new(numerator, denominator).ok());
        entries.push(PhysicalStateDeltaEntry {
            coordinate,
            delta: fixed
                .map(ExactPhysicalStateDelta::Rational)
                .unwrap_or(ExactPhysicalStateDelta::Energy(delta)),
        });
    }
}

fn push_i128_delta(
    entries: &mut Vec<PhysicalStateDeltaEntry>,
    coordinate: PhysicalStateCoordinate,
    predecessor: i128,
    successor: i128,
) {
    if predecessor == successor {
        return;
    }
    let (negative, magnitude) = if successor < predecessor {
        (true, predecessor.abs_diff(successor))
    } else {
        (false, successor.abs_diff(predecessor))
    };
    entries.push(PhysicalStateDeltaEntry {
        coordinate,
        delta: ExactPhysicalStateDelta::Integral(ExactSignedDelta {
            negative,
            magnitude,
        }),
    });
}

const SPARSE_DELTA_MINIMUM_ENTRY_BYTES: usize = 1 + 8 + 1 + 2 * (8 + 1);

fn sparse_delta_coordinate_parts(coordinate: PhysicalStateCoordinate) -> (u8, usize) {
    match coordinate {
        PhysicalStateCoordinate::PsiWinding(index) => (0, index),
        PhysicalStateCoordinate::PsiDissipatedEnergy(index) => (1, index),
        PhysicalStateCoordinate::GateOpenPopulation => (2, 0),
        PhysicalStateCoordinate::GateDissipatedEnergy => (3, 0),
        PhysicalStateCoordinate::MembraneSeparatedCharge => (4, 0),
        PhysicalStateCoordinate::MembraneCarrierPhase => (5, 0),
        PhysicalStateCoordinate::ConductancePathCarrierPhase(index) => (6, index),
        PhysicalStateCoordinate::IntracellularCarrier => (7, 0),
        PhysicalStateCoordinate::ExtracellularCarrier => (8, 0),
        PhysicalStateCoordinate::RecoveryPsiFuel(index) => (9, index),
        PhysicalStateCoordinate::RecoveryPsiSpent(index) => (10, index),
        PhysicalStateCoordinate::RecoveryPsiExportedHeat(index) => (11, index),
        PhysicalStateCoordinate::RecoveryGateFuel => (12, 0),
        PhysicalStateCoordinate::RecoveryGateSpent => (13, 0),
        PhysicalStateCoordinate::RecoveryGateExportedHeat => (14, 0),
        PhysicalStateCoordinate::PlasticRestLength => (15, 0),
        PhysicalStateCoordinate::PlasticDissipatedEnergy => (16, 0),
        PhysicalStateCoordinate::RecoveryPlasticFuel => (17, 0),
        PhysicalStateCoordinate::RecoveryPlasticSpent => (18, 0),
        PhysicalStateCoordinate::RecoveryPlasticExportedHeat => (19, 0),
        PhysicalStateCoordinate::DnaSubstrate => (20, 0),
        PhysicalStateCoordinate::DnaFuel => (21, 0),
        PhysicalStateCoordinate::DnaExpressedProduct => (22, 0),
        PhysicalStateCoordinate::DnaWaste => (23, 0),
        PhysicalStateCoordinate::ReceptorQuantumResidue => (24, 0),
        PhysicalStateCoordinate::MembraneReturnWorkResidue => (25, 0),
        PhysicalStateCoordinate::PlasticDissipationResidue => (26, 0),
        PhysicalStateCoordinate::GateDissipationResidue => (27, 0),
    }
}

fn sparse_delta_coordinate_from_parts(
    tag: u8,
    index: usize,
) -> Result<PhysicalStateCoordinate, NeuronStateCodecError> {
    let coordinate = match tag {
        0 => PhysicalStateCoordinate::PsiWinding(index),
        1 => PhysicalStateCoordinate::PsiDissipatedEnergy(index),
        2 if index == 0 => PhysicalStateCoordinate::GateOpenPopulation,
        3 if index == 0 => PhysicalStateCoordinate::GateDissipatedEnergy,
        4 if index == 0 => PhysicalStateCoordinate::MembraneSeparatedCharge,
        5 if index == 0 => PhysicalStateCoordinate::MembraneCarrierPhase,
        6 => PhysicalStateCoordinate::ConductancePathCarrierPhase(index),
        7 if index == 0 => PhysicalStateCoordinate::IntracellularCarrier,
        8 if index == 0 => PhysicalStateCoordinate::ExtracellularCarrier,
        9 => PhysicalStateCoordinate::RecoveryPsiFuel(index),
        10 => PhysicalStateCoordinate::RecoveryPsiSpent(index),
        11 => PhysicalStateCoordinate::RecoveryPsiExportedHeat(index),
        12 if index == 0 => PhysicalStateCoordinate::RecoveryGateFuel,
        13 if index == 0 => PhysicalStateCoordinate::RecoveryGateSpent,
        14 if index == 0 => PhysicalStateCoordinate::RecoveryGateExportedHeat,
        15 if index == 0 => PhysicalStateCoordinate::PlasticRestLength,
        16 if index == 0 => PhysicalStateCoordinate::PlasticDissipatedEnergy,
        17 if index == 0 => PhysicalStateCoordinate::RecoveryPlasticFuel,
        18 if index == 0 => PhysicalStateCoordinate::RecoveryPlasticSpent,
        19 if index == 0 => PhysicalStateCoordinate::RecoveryPlasticExportedHeat,
        20 if index == 0 => PhysicalStateCoordinate::DnaSubstrate,
        21 if index == 0 => PhysicalStateCoordinate::DnaFuel,
        22 if index == 0 => PhysicalStateCoordinate::DnaExpressedProduct,
        23 if index == 0 => PhysicalStateCoordinate::DnaWaste,
        24 if index == 0 => PhysicalStateCoordinate::ReceptorQuantumResidue,
        25 if index == 0 => PhysicalStateCoordinate::MembraneReturnWorkResidue,
        26 if index == 0 => PhysicalStateCoordinate::PlasticDissipationResidue,
        27 if index == 0 => PhysicalStateCoordinate::GateDissipationResidue,
        _ => return Err(NeuronStateCodecError::InvalidEncoding),
    };
    Ok(coordinate)
}

/// Exact wire form for one already-computed sparse physical-state delta. The
/// codec transports the existing coordinate machinery only; it computes no new
/// physics and admits no coordinate the settled delta law cannot produce.
pub(crate) fn encode_sparse_physical_state_delta(
    delta: &SparsePhysicalStateDelta,
) -> Result<Vec<u8>, NeuronStateCodecError> {
    let mut encoded = Vec::new();
    push_usize(&mut encoded, delta.entries.len())?;
    for entry in delta.entries.iter() {
        let (tag, index) = sparse_delta_coordinate_parts(entry.coordinate);
        encoded.push(tag);
        push_usize(&mut encoded, index)?;
        match &entry.delta {
            ExactPhysicalStateDelta::Integral(signed) => {
                let (negative, magnitude) = signed.parts();
                encoded.push(0);
                push_u128(&mut encoded, magnitude);
                push_u128(&mut encoded, u128::from(negative));
            }
            ExactPhysicalStateDelta::Rational(rational) => {
                let (numerator, denominator) = rational.parts();
                encoded.push(1);
                push_i128(&mut encoded, numerator);
                push_u128(&mut encoded, denominator);
            }
            ExactPhysicalStateDelta::Energy(rational) => {
                encoded.push(2);
                push_state_big_rational(&mut encoded, rational)?;
            }
        }
    }
    Ok(encoded)
}

pub(crate) fn decode_sparse_physical_state_delta(
    encoded: &[u8],
) -> Result<SparsePhysicalStateDelta, NeuronStateCodecError> {
    let mut reader = NeuronStateReader::new(encoded);
    let entry_count = reader.usize()?;
    let maximum_entries_in_body = encoded
        .len()
        .checked_sub(8)
        .ok_or(NeuronStateCodecError::InvalidEncoding)?
        / SPARSE_DELTA_MINIMUM_ENTRY_BYTES;
    if entry_count > maximum_entries_in_body {
        return Err(NeuronStateCodecError::InvalidEncoding);
    }
    let mut entries = Vec::new();
    entries
        .try_reserve_exact(entry_count)
        .map_err(|_| NeuronStateCodecError::ArithmeticWidth)?;
    for _ in 0..entry_count {
        let tag = reader.take(1)?[0];
        let index = reader.usize()?;
        let coordinate = sparse_delta_coordinate_from_parts(tag, index)?;
        let kind = reader.take(1)?[0];
        let delta = match kind {
            0 => {
                let magnitude = reader.u128()?;
                let negative = match reader.u128()? {
                    0 => false,
                    1 => true,
                    _ => return Err(NeuronStateCodecError::InvalidEncoding),
                };
                ExactPhysicalStateDelta::Integral(
                    ExactSignedDelta::from_parts(negative, magnitude)
                        .ok_or(NeuronStateCodecError::InvalidEncoding)?,
                )
            }
            1 => {
                let numerator = reader.i128()?;
                let denominator = reader.u128()?;
                ExactPhysicalStateDelta::Rational(
                    ExactRational::new(numerator, denominator)
                        .map_err(|_| NeuronStateCodecError::InvalidEncoding)?,
                )
            }
            2 => ExactPhysicalStateDelta::Energy(reader.big_rational()?),
            _ => return Err(NeuronStateCodecError::InvalidEncoding),
        };
        entries.push(
            PhysicalStateDeltaEntry::new(coordinate, delta)
                .ok_or(NeuronStateCodecError::InvalidEncoding)?,
        );
    }
    if !reader.finished() {
        return Err(NeuronStateCodecError::InvalidEncoding);
    }
    SparsePhysicalStateDelta::from_canonical_entries(entries)
        .ok_or(NeuronStateCodecError::InvalidEncoding)
}

fn apply_unsigned_member_delta(
    value: u128,
    delta: ExactSignedDelta,
) -> Result<u128, NeuronStateCodecError> {
    let (negative, magnitude) = delta.parts();
    if negative {
        value.checked_sub(magnitude)
    } else {
        value.checked_add(magnitude)
    }
    .ok_or(NeuronStateCodecError::InvalidEncoding)
}

fn apply_signed_member_delta(
    value: i128,
    delta: ExactSignedDelta,
) -> Result<i128, NeuronStateCodecError> {
    let (negative, magnitude) = delta.parts();
    let magnitude =
        i128::try_from(magnitude).map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
    if negative {
        value.checked_sub(magnitude)
    } else {
        value.checked_add(magnitude)
    }
    .ok_or(NeuronStateCodecError::InvalidEncoding)
}

fn apply_rational_member_delta(
    base: ExactRational,
    delta: ExactRational,
) -> Result<ExactRational, NeuronStateCodecError> {
    base.checked_add(delta)
        .map_err(|_| NeuronStateCodecError::InvalidEncoding)
}

fn apply_phase_member_delta(
    base: ChargeCarrierPhase,
    delta: ExactRational,
) -> Result<ChargeCarrierPhase, NeuronStateCodecError> {
    let (numerator, denominator) = base.parts();
    let base = ExactRational::new(numerator, denominator)
        .map_err(|_| NeuronStateCodecError::InvalidEncoding)?;
    let (numerator, denominator) = apply_rational_member_delta(base, delta)?.parts();
    ChargeCarrierPhase::new(numerator, denominator)
        .map_err(|_| NeuronStateCodecError::InvalidEncoding)
}

fn integral_member_delta(
    delta: ExactPhysicalStateDelta,
) -> Result<ExactSignedDelta, NeuronStateCodecError> {
    match delta {
        ExactPhysicalStateDelta::Integral(signed) => Ok(signed),
        ExactPhysicalStateDelta::Rational(_) | ExactPhysicalStateDelta::Energy(_) => {
            Err(NeuronStateCodecError::InvalidEncoding)
        }
    }
}

fn rational_member_delta(
    delta: ExactPhysicalStateDelta,
) -> Result<ExactRational, NeuronStateCodecError> {
    match delta {
        ExactPhysicalStateDelta::Rational(rational) => Ok(rational),
        ExactPhysicalStateDelta::Integral(_) | ExactPhysicalStateDelta::Energy(_) => {
            Err(NeuronStateCodecError::InvalidEncoding)
        }
    }
}

fn energy_member_delta(delta: ExactPhysicalStateDelta) -> Result<Exact, NeuronStateCodecError> {
    match delta {
        ExactPhysicalStateDelta::Energy(rational) => Ok(rational),
        ExactPhysicalStateDelta::Rational(rational) => Ok(rational_to_exact(rational)),
        ExactPhysicalStateDelta::Integral(_) => Err(NeuronStateCodecError::InvalidEncoding),
    }
}

/// Reconstruct the exact successor of `base` under one already-settled sparse
/// physical-state delta. This applies the existing coordinate machinery in the
/// forward direction; `sparse_physical_state_delta(base, applied)` returns the
/// same delta. It settles no physics and clamps nothing: any coordinate the
/// anatomy cannot carry, any capacity violation, and any arithmetic escape
/// refuses instead of adjusting.
pub(crate) fn apply_sparse_physical_state_delta(
    anatomy: &NeuronPhysicalAnatomy,
    base: &NeuronPhysicalState,
    delta: &SparsePhysicalStateDelta,
) -> Result<NeuronPhysicalState, NeuronStateCodecError> {
    let mut applied = base.clone();
    let mut separated_elementary_charges =
        applied.membrane.membrane().separated_elementary_charges();
    let mut membrane_phase = applied.membrane.membrane().carrier_phase();
    let mut path_phases = applied.membrane.path_carrier_phases();
    for entry in delta.entries() {
        match entry.coordinate() {
            PhysicalStateCoordinate::PsiWinding(index) => {
                let ring = applied
                    .psi
                    .rings
                    .get_mut(index)
                    .ok_or(NeuronStateCodecError::InvalidEncoding)?;
                let winding = apply_signed_member_delta(
                    ring.winding as i8 as i128,
                    integral_member_delta(entry.delta())?,
                )?;
                let winding = decode_winding(
                    i8::try_from(winding).map_err(|_| NeuronStateCodecError::InvalidEncoding)?,
                )?;
                ring.winding = winding;
                ring.phase_thirds = canonical_phase_thirds(winding);
            }
            PhysicalStateCoordinate::PsiDissipatedEnergy(index) => {
                let ring = applied
                    .psi
                    .rings
                    .get_mut(index)
                    .ok_or(NeuronStateCodecError::InvalidEncoding)?;
                ring.dissipated_quanta = apply_unsigned_member_delta(
                    ring.dissipated_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::GateOpenPopulation => {
                applied.gate.open_population = apply_unsigned_member_delta(
                    applied.gate.open_population,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::GateDissipatedEnergy => {
                applied.gate.dissipated_quanta = apply_unsigned_member_delta(
                    applied.gate.dissipated_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::GateDissipationResidue => {
                let energy = applied.gate.dissipation_residue_zeptojoules.energy()
                    + energy_member_delta(entry.delta())?;
                applied.gate.dissipation_residue_zeptojoules = PhysicalEnergyResidue {
                    energy_zeptojoules: energy,
                };
            }
            PhysicalStateCoordinate::MembraneSeparatedCharge => {
                separated_elementary_charges = apply_signed_member_delta(
                    separated_elementary_charges,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::MembraneCarrierPhase => {
                membrane_phase = apply_phase_member_delta(
                    membrane_phase,
                    rational_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::ConductancePathCarrierPhase(index) => {
                let phase = path_phases
                    .get_mut(index)
                    .ok_or(NeuronStateCodecError::InvalidEncoding)?;
                *phase = apply_phase_member_delta(*phase, rational_member_delta(entry.delta())?)?;
            }
            PhysicalStateCoordinate::IntracellularCarrier => {
                applied.carriers.intracellular = apply_unsigned_member_delta(
                    applied.carriers.intracellular,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::ExtracellularCarrier => {
                applied.carriers.extracellular = apply_unsigned_member_delta(
                    applied.carriers.extracellular,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryPsiFuel(index) => {
                let lane = applied
                    .recovery
                    .psi_lanes
                    .get_mut(index)
                    .ok_or(NeuronStateCodecError::InvalidEncoding)?;
                lane.fuel_quanta = apply_unsigned_member_delta(
                    lane.fuel_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryPsiSpent(index) => {
                let lane = applied
                    .recovery
                    .psi_lanes
                    .get_mut(index)
                    .ok_or(NeuronStateCodecError::InvalidEncoding)?;
                lane.spent_quanta = apply_unsigned_member_delta(
                    lane.spent_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryPsiExportedHeat(index) => {
                let lane = applied
                    .recovery
                    .psi_lanes
                    .get_mut(index)
                    .ok_or(NeuronStateCodecError::InvalidEncoding)?;
                lane.exported_heat_quanta = apply_unsigned_member_delta(
                    lane.exported_heat_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryGateFuel => {
                applied.recovery.gate_lane.fuel_quanta = apply_unsigned_member_delta(
                    applied.recovery.gate_lane.fuel_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryGateSpent => {
                applied.recovery.gate_lane.spent_quanta = apply_unsigned_member_delta(
                    applied.recovery.gate_lane.spent_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryGateExportedHeat => {
                applied.recovery.gate_lane.exported_heat_quanta = apply_unsigned_member_delta(
                    applied.recovery.gate_lane.exported_heat_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::PlasticRestLength => {
                applied.plastic.rest_length_nanometres = apply_rational_member_delta(
                    applied.plastic.rest_length_nanometres,
                    rational_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::PlasticDissipatedEnergy => {
                applied.plastic.dissipated_quanta = apply_unsigned_member_delta(
                    applied.plastic.dissipated_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryPlasticFuel => {
                applied.recovery.plastic_lane.fuel_quanta = apply_unsigned_member_delta(
                    applied.recovery.plastic_lane.fuel_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryPlasticSpent => {
                applied.recovery.plastic_lane.spent_quanta = apply_unsigned_member_delta(
                    applied.recovery.plastic_lane.spent_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::RecoveryPlasticExportedHeat => {
                applied.recovery.plastic_lane.exported_heat_quanta = apply_unsigned_member_delta(
                    applied.recovery.plastic_lane.exported_heat_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::DnaSubstrate => {
                applied.dna_expression.substrate_quanta = apply_unsigned_member_delta(
                    applied.dna_expression.substrate_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::DnaFuel => {
                applied.dna_expression.fuel_quanta = apply_unsigned_member_delta(
                    applied.dna_expression.fuel_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::DnaExpressedProduct => {
                applied.dna_expression.expressed_product_quanta = apply_unsigned_member_delta(
                    applied.dna_expression.expressed_product_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::DnaWaste => {
                applied.dna_expression.waste_quanta = apply_unsigned_member_delta(
                    applied.dna_expression.waste_quanta,
                    integral_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::ReceptorQuantumResidue => {
                applied.receptor_quantum_residue = apply_rational_member_delta(
                    applied.receptor_quantum_residue,
                    rational_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::MembraneReturnWorkResidue => {
                applied.membrane_return_work_residue = apply_rational_member_delta(
                    applied.membrane_return_work_residue,
                    rational_member_delta(entry.delta())?,
                )?;
            }
            PhysicalStateCoordinate::PlasticDissipationResidue => {
                let energy = applied.plastic.dissipation_residue_zeptojoules.energy()
                    + energy_member_delta(entry.delta())?;
                applied.plastic.dissipation_residue_zeptojoules = PhysicalEnergyResidue {
                    energy_zeptojoules: energy,
                };
            }
        }
    }
    applied.membrane = LocalMembraneConductanceState::from_physical_parts(
        ElementaryChargeMembraneState::from_physical_parts(
            separated_elementary_charges,
            membrane_phase,
        ),
        path_phases,
    );
    encode_neuron_physical_state(anatomy, &applied)?;
    Ok(applied)
}

// ---------------------------------------------------------------------------
// Metabolic loop (minimal feeding metabolism, authorized by Joe 2026-08-05).
//
// Nothing below introduces a physical constant.  Every quantity read here is
// already authored in this neuron's anatomy (the gate's single-channel
// conductance, its dissipation-lattice quantum, the membrane capacitance, the
// recovery lanes' stoichiometry and the declared dissipation capacities) or is
// the neuron's own retained state.  The reactions are the ones this module
// already defines; these entry points only address a lane by name and expose
// the exact bounds the reservoir-side settlement needs to stay conservative.
// ---------------------------------------------------------------------------

impl NeuronPhysicalAnatomy {
    /// The declared dissipation capacity of one recovery lane's ledger.
    pub(crate) fn lane_dissipation_capacity_quanta(
        &self,
        address: RecoveryLaneAddress,
    ) -> Option<u128> {
        match address {
            RecoveryLaneAddress::Psi(index) => self
                .psi
                .rings
                .get(index)
                .map(|ring| ring.dissipation_capacity_quanta),
            RecoveryLaneAddress::Gate => Some(self.gate.dissipation_capacity_quanta),
            RecoveryLaneAddress::Plastic => Some(self.plastic.dissipation_capacity_quanta),
        }
    }
}

impl NeuronPhysicalState {
    /// The quanta currently standing in one recovery lane's dissipation ledger
    /// — the dissipation the lane's recovery reaction can still undo.
    pub(crate) fn lane_dissipated_quanta(&self, address: RecoveryLaneAddress) -> Option<u128> {
        match address {
            RecoveryLaneAddress::Psi(index) => {
                self.psi.rings.get(index).map(|ring| ring.dissipated_quanta)
            }
            RecoveryLaneAddress::Gate => Some(self.gate.dissipated_quanta),
            RecoveryLaneAddress::Plastic => Some(self.plastic.dissipated_quanta),
        }
    }

    /// This neuron's signed separated membrane charge, in elementary charges.
    /// Rest is exactly zero: the state every neuron is authored at
    /// (`LocalMembraneConductanceState::genesis(0)` in virtual material
    /// genesis), so the displacement from rest IS this value.
    pub(crate) fn separated_elementary_charges(&self) -> i128 {
        self.membrane.membrane().separated_elementary_charges()
    }
}

/// One interval of the membrane return path.
///
/// `charges` is the signed outward elementary-charge count to transport;
/// `successor_phase` is the retained sub-charge phase to keep for the next
/// interval, present only when the whole computed transport is deliverable
/// (an interval the body cannot pay for keeps the predecessor phase, so no
/// fraction of a charge is ever lost or invented).
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct MembranePumpBound {
    pub(crate) charges: i128,
    pub(crate) successor_phase: Option<ChargeCarrierPhase>,
}

/// One exact interval of the phase-one AE carrier pump.  The pump has no
/// desired voltage.  Its direction is the direction that increases the
/// existing finite carrier-gradient work declared by the sign of E_rev; its
/// throughput is the already-authored one-channel conductance integrated over
/// exact elapsed time.  The caller still has to prove that local recovery
/// energy can pay the resulting increase in stored physical work.
pub(crate) fn membrane_gradient_pump_charge_bound(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    interval_microseconds: u32,
) -> Result<MembranePumpBound, NeuronPhysicalError> {
    let reversal = anatomy.gate.reversal_potential_millivolts;
    let reversal_sign = reversal.parts().0.signum();
    if reversal_sign == 0 {
        return Ok(MembranePumpBound {
            charges: 0,
            successor_phase: None,
        });
    }
    let potential = predecessor
        .membrane
        .membrane()
        .potential_millivolts(anatomy.capacitance)
        .map_err(MembraneConductanceError::from)
        .map_err(GateSettlementError::from)?;
    let electrochemical_drive = potential.checked_sub(reversal)?;
    let magnitude_current = anatomy
        .gate
        .single_channel_conductance_picosiemens
        .checked_mul(electrochemical_drive.checked_abs()?)?
        .checked_div_unsigned(1_000)?;
    let pump_current = if reversal_sign < 0 {
        magnitude_current.checked_neg()?
    } else {
        magnitude_current
    };
    let transfer = settle_elementary_charge_transfer(
        predecessor.membrane.membrane().carrier_phase(),
        pump_current,
        interval_microseconds,
    )
    .map_err(MembraneConductanceError::from)
    .map_err(GateSettlementError::from)?;
    let available = if transfer.outward_elementary_charges >= 0 {
        predecessor.carriers.intracellular
    } else {
        predecessor.carriers.extracellular
    };
    let magnitude = transfer
        .outward_elementary_charges
        .unsigned_abs()
        .min(available);
    let charges = if transfer.outward_elementary_charges < 0 {
        -i128::try_from(magnitude).map_err(|_| GateSettlementError::ArithmeticWidth)?
    } else {
        i128::try_from(magnitude).map_err(|_| GateSettlementError::ArithmeticWidth)?
    };
    Ok(MembranePumpBound {
        charges,
        successor_phase: (charges == transfer.outward_elementary_charges)
            .then_some(transfer.successor_phase),
    })
}

/// Exact retained electrical plus generic carrier-gradient work.
///
/// The electrical term is 1/2 C V^2, with the exact unit conversion
/// 1 pF*mV^2 = 1000 zJ.  The gradient term uses the already-authored fixed
/// chemical potential E_rev and the finite carrier compartment on its uphill
/// side.  This is a derived observation of existing state, not another stored
/// gradient authority.
pub(crate) fn membrane_and_gradient_work_zeptojoules(
    anatomy: &NeuronPhysicalAnatomy,
    state: &NeuronPhysicalState,
) -> Result<ExactRational, NeuronPhysicalError> {
    let potential = state
        .membrane
        .membrane()
        .potential_millivolts(anatomy.capacitance)
        .map_err(MembraneConductanceError::from)
        .map_err(GateSettlementError::from)?;
    let capacitor = anatomy
        .capacitance
        .picofarads()
        .checked_mul(potential)?
        .checked_mul(potential)?
        .checked_mul_unsigned(500)?;
    let reversal = anatomy.gate.reversal_potential_millivolts;
    let uphill_carriers = if reversal.parts().0 < 0 {
        state.carriers.intracellular
    } else if reversal.parts().0 > 0 {
        state.carriers.extracellular
    } else {
        0
    };
    let gradient = ExactRational::new(801_088_317, 5_000_000_000)?
        .checked_mul(reversal.checked_abs()?)?
        .checked_mul_unsigned(uphill_carriers)?;
    capacitor.checked_add(gradient).map_err(Into::into)
}

/// Move an exact whole-carrier pump extent across this neuron's membrane.
///
/// Charge is conserved, never destroyed: the membrane's separated charge and
/// the intracellular/extracellular carrier partition move equal and opposite,
/// exactly as every other transport in this module does.  The retained carrier
/// phases are untouched — this is a whole-charge transport, not an ensemble
/// current, so it leaves no sub-charge residue behind.
pub(crate) fn settle_membrane_pump_transport(
    anatomy: &NeuronPhysicalAnatomy,
    predecessor: &NeuronPhysicalState,
    outward_elementary_charges: i128,
    successor_phase: Option<ChargeCarrierPhase>,
    interval_microseconds: u32,
) -> Result<NeuronPhysicalState, NeuronPhysicalError> {
    // A DEPLETED RESERVOIR LIMITS THE CURRENT; IT DOES NOT HALT THE BODY
    // (2026-08-08).
    //
    // MEASURED ON THE LIVE ORGANISM: neuron 8 pushed its intracellular
    // carriers to zero, and from then on EVERY transport refused with
    // InsufficientCarrierMaterial — every lesson, every offered material,
    // and even a plain dark interval. Since carriers only return by moving
    // through this same transport, nothing could ever bring them back: she
    // was frozen, permanently, and could not have any experience at all.
    //
    // Treating an empty reservoir as an ERROR is what made that a deadlock.
    // The physical fact is that you cannot move more charge carriers than
    // you have, so the flow SATURATES at what is available — a real neuron
    // low on ions passes less current, it does not stop the universe. The
    // demand that could not be met is not silently dropped either: it stays
    // as the unmet flow it always was, exactly as the dissipation ledger
    // already records demand it could not meet.
    //
    // Charge conservation is preserved because the membrane is settled with
    // the SAME bounded charge that the carriers move — they cannot disagree.
    let available: i128 = if outward_elementary_charges >= 0 {
        i128::try_from(predecessor.carriers.intracellular).unwrap_or(i128::MAX)
    } else {
        i128::try_from(predecessor.carriers.extracellular).unwrap_or(i128::MAX)
    };
    let magnitude = outward_elementary_charges
        .unsigned_abs()
        .min(u128::try_from(available).unwrap_or(0));
    let outward_elementary_charges = if outward_elementary_charges >= 0 {
        i128::try_from(magnitude).unwrap_or(0)
    } else {
        -i128::try_from(magnitude).unwrap_or(0)
    };
    let phase = successor_phase.unwrap_or_else(|| predecessor.membrane.membrane().carrier_phase());
    if outward_elementary_charges == 0 && phase == predecessor.membrane.membrane().carrier_phase() {
        return Ok(predecessor.clone());
    }
    let membrane = settle_membrane_elementary_charges(
        anatomy.capacitance,
        predecessor.membrane.membrane(),
        outward_elementary_charges,
        interval_microseconds,
    )
    .map_err(MembraneConductanceError::from)
    .map_err(GateSettlementError::from)?;
    let carriers = move_carriers(predecessor.carriers, outward_elementary_charges)?;
    let mut successor = predecessor.clone();
    successor.membrane = LocalMembraneConductanceState::from_physical_parts(
        ElementaryChargeMembraneState::from_physical_parts(
            membrane.successor.separated_elementary_charges(),
            phase,
        ),
        predecessor.membrane.path_carrier_phases(),
    );
    successor.carriers = carriers;
    Ok(successor)
}

// Measurement-only test accessors (no production logic): expose otherwise
// private conserved quantities so probe tests can report them exactly.
#[cfg(test)]
impl DnaExpressionState {
    pub(crate) fn probe_parts(self) -> (u128, u128, u128, u128) {
        (
            self.substrate_quanta,
            self.fuel_quanta,
            self.expressed_product_quanta,
            self.waste_quanta,
        )
    }
}

#[cfg(test)]
impl PlasticSupportState {
    pub(crate) fn probe_dissipated_quanta(&self) -> u128 {
        self.dissipated_quanta
    }

    pub(crate) fn probe_rest_length_nanometres(&self) -> ExactRational {
        self.rest_length_nanometres
    }
}

#[cfg(test)]
impl NeuronPhysicalAnatomy {
    pub(crate) fn probe_plastic_dissipation_capacity_quanta(&self) -> u128 {
        self.plastic.dissipation_capacity_quanta
    }

    pub(crate) fn probe_psi_ring_dissipation_capacity_quanta(&self, index: usize) -> Option<u128> {
        self.psi
            .rings
            .get(index)
            .map(|ring| ring.dissipation_capacity_quanta)
    }

    pub(crate) fn probe_plastic_closed_coordinate_nanometres(&self) -> ExactRational {
        self.plastic.closed_coordinate_nanometres
    }

    pub(crate) fn probe_legacy_independent_yielded_population(
        &self,
        state: &PlasticSupportState,
    ) -> Result<u128, PlasticityError> {
        legacy_independent_yielded_population(&self.plastic, state, self.gate.population)
    }
}

#[cfg(test)]
mod tests {
    use std::sync::Arc;

    use super::*;
    use crate::declared_geometric_anatomy::membrane_capacitance_from_declared_geometry;
    use crate::joint_uf_neuron_boundary::{
        bind_isolated_neuron_perspective, bind_neuron_perspective,
        prepare_complete_joint_field_admitted_fixture, prepare_complete_joint_field_fixture,
        prepare_isolated_single_neuron_field_fixture, DsfFactFamily, SharedCompleteJointField,
    };
    use crate::joint_uf_source_adapter::EvaluatedJointSourceOccurrence;
    use crate::joint_uf_v1_4::{
        evaluate_with_physical_bounds, JointIntersampleLaw, JointUfCoordinateBounds, JointUfInput,
        JointUfPhysicalBounds, JointUfResult,
    };
    use crate::neuron_source_anchor::tests::exact_episode;
    use crate::neuron_source_anchor::{
        bind_neuron_source_anchor, NeuronSourceSite, PhysicalSourceSense,
    };
    use crate::physical_mosaic::admit_physical_mosaic;
    use crate::reached_neuron_cohort::{
        decode_reached_cohort_cell, decode_reached_cohort_state, decode_reached_cohort_state_delta,
        encode_reached_cohort_cell, encode_reached_cohort_cell_v5, encode_reached_cohort_state,
        encode_reached_cohort_state_delta, encode_reached_cohort_state_v4,
        settle_reached_cohort_dark_rest, settle_reached_cohort_experience_to_quiescence,
        settle_reached_cohort_interval, settle_reached_cohort_membrane_pumps,
        settle_reached_cohort_recurrence, settle_reached_cohort_to_quiescence,
        ReachedCohortAnatomy, ReachedCohortIntervalInput, ReachedCohortState,
    };
    use crate::recovery_fluid_contact::RecoveryFluidReservoirState;
    use crate::sparse_electrical_contact::{
        ElectricalContactAnatomy, SparseElectricalAnatomy, SparseElectricalState,
    };

    fn q(numerator: i64, denominator: i64) -> Exact {
        Exact::new(BigInt::from(numerator), BigInt::from(denominator))
    }

    fn r(numerator: i128, denominator: u128) -> ExactRational {
        ExactRational::new(numerator, denominator).unwrap()
    }

    #[test]
    fn sparse_fractal_rejects_coordinate_delta_kind_mismatch() {
        let integral =
            ExactPhysicalStateDelta::Integral(ExactSignedDelta::from_parts(false, 1).unwrap());
        let rational = ExactPhysicalStateDelta::Rational(r(1, 3));

        assert!(PhysicalStateDeltaEntry::new(
            PhysicalStateCoordinate::GateOpenPopulation,
            integral.clone(),
        )
        .is_some());
        assert!(PhysicalStateDeltaEntry::new(
            PhysicalStateCoordinate::PlasticRestLength,
            rational.clone(),
        )
        .is_some());
        assert!(PhysicalStateDeltaEntry::new(
            PhysicalStateCoordinate::GateOpenPopulation,
            rational.clone(),
        )
        .is_none());
        assert!(PhysicalStateDeltaEntry::new(
            PhysicalStateCoordinate::PlasticRestLength,
            integral.clone(),
        )
        .is_none());
        assert!(
            SparsePhysicalStateDelta::from_canonical_entries(vec![PhysicalStateDeltaEntry {
                coordinate: PhysicalStateCoordinate::MembraneCarrierPhase,
                delta: integral,
            },])
            .is_none()
        );
    }

    fn fixture_source_sites(count: usize) -> Vec<NeuronSourceSite> {
        (0..count)
            .map(|index| NeuronSourceSite::fixture(index as u32))
            .collect()
    }

    fn fixture_lineages(count: usize) -> Vec<[u8; 16]> {
        (0..count)
            .map(|index| {
                let mut lineage = [0u8; 16];
                lineage[8..].copy_from_slice(&(index as u64 + 1).to_be_bytes());
                lineage
            })
            .collect()
    }

    fn evaluate_fixture(input: JointUfInput, bounds: &[(f64, f64)]) -> JointUfResult {
        evaluate_with_physical_bounds(
            input,
            JointUfPhysicalBounds::new(
                bounds
                    .iter()
                    .map(|(minimum, maximum)| {
                        JointUfCoordinateBounds::new(*minimum, *maximum).unwrap()
                    })
                    .collect(),
                BigRational::from_integer(BigInt::from(2)),
            )
            .unwrap(),
        )
        .unwrap()
    }

    fn shared_field() -> SharedCompleteJointField {
        let field = evaluate_fixture(
            JointUfInput {
                times: vec![q(0, 1), q(1, 2), q(1, 1), q(2, 1)],
                fields: vec![vec![0.0], vec![0.3], vec![0.3], vec![0.0]],
                relevance: vec![0.1, 0.2, 0.3, 0.4],
                intersample_law: JointIntersampleLaw::SampledVolumeAndRelevancePiecewiseLinear,
            },
            &[(0.0, 0.3)],
        );
        prepare_isolated_single_neuron_field_fixture(
            Arc::from([1_u8, 2, 3]),
            [4; 32],
            0,
            EvaluatedJointSourceOccurrence {
                port_indices: vec![0],
                groups: vec![vec![0]],
                field,
            },
        )
        .unwrap()
    }

    fn shared_three_neuron_field() -> SharedCompleteJointField {
        let field = evaluate_fixture(
            JointUfInput {
                times: vec![q(0, 1), q(1, 2), q(1, 1), q(2, 1)],
                fields: vec![
                    vec![0.0, 2.0, -2.0],
                    vec![0.3, 2.4, -1.7],
                    vec![0.3, 2.8, -1.4],
                    vec![0.0, 3.2, -1.1],
                ],
                relevance: vec![0.1, 0.2, 0.3, 0.4],
                intersample_law: JointIntersampleLaw::SampledVolumeAndRelevancePiecewiseLinear,
            },
            &[(0.0, 0.3), (2.0, 3.2), (-2.0, -1.1)],
        );
        prepare_complete_joint_field_fixture(
            Arc::from([8_u8, 9, 10]),
            [11; 32],
            0,
            EvaluatedJointSourceOccurrence {
                port_indices: vec![0, 1, 2],
                groups: vec![vec![0, 1, 2]],
                field,
            },
        )
        .unwrap()
    }

    fn shared_four_neuron_field() -> SharedCompleteJointField {
        let field = evaluate_fixture(
            JointUfInput {
                times: vec![q(0, 1), q(1, 2), q(1, 1), q(2, 1)],
                fields: vec![
                    vec![0.0, 2.0, -2.0, 4.0],
                    vec![0.3, 2.4, -1.7, 4.2],
                    vec![0.3, 2.8, -1.4, 4.4],
                    vec![0.0, 3.2, -1.1, 4.6],
                ],
                relevance: vec![0.1, 0.2, 0.3, 0.4],
                intersample_law: JointIntersampleLaw::SampledVolumeAndRelevancePiecewiseLinear,
            },
            &[(-10.0, 10.0), (-10.0, 10.0), (-10.0, 10.0), (-10.0, 10.0)],
        );
        prepare_complete_joint_field_fixture(
            Arc::from([12_u8, 13, 14]),
            [15; 32],
            0,
            EvaluatedJointSourceOccurrence {
                port_indices: vec![0, 1, 2, 3],
                groups: vec![vec![0, 1, 2, 3]],
                field,
            },
        )
        .unwrap()
    }

    fn ring_anatomy() -> PsiRingAnatomy {
        PsiRingAnatomy::new(
            [1, 1, 1],
            [q(0, 1), q(0, 1), q(0, 1)],
            q(1, 1),
            q(9, 2),
            10_000,
            [[true; 3]; 3],
            BalancedTrit::Quiescent,
        )
        .unwrap()
    }

    struct Fixture {
        anatomy: NeuronPhysicalAnatomy,
        state: NeuronPhysicalState,
        zero_catalysts: Vec<u128>,
        ring_count: usize,
    }

    fn physical_fixture() -> Fixture {
        physical_fixture_at(0)
    }

    /// One fixture neuron authored AT a declared place.  Its membrane
    /// capacitance is derived from that place exactly as production genesis
    /// derives it (see `declared_geometric_anatomy`), so a cohort of fixtures
    /// at distinct places carries distinct anatomy — the differentiated
    /// fixtures the 2026-08-05 ratification requires.
    fn physical_fixture_at(topology_index: u32) -> Fixture {
        scaled_physical_fixture_at(64, 7, topology_index)
    }

    fn physical_fixtures<const N: usize>() -> [Fixture; N] {
        std::array::from_fn(|index| physical_fixture_at(index as u32))
    }

    #[test]
    fn retained_plastic_geometry_changes_later_gate_free_energy() {
        let shared = shared_field();
        let fixture = physical_fixture();
        let perspective = bind_isolated_neuron_perspective(&shared, 1).unwrap();
        let delivered =
            settle_shared_dsf_mathloom(perspective, fixture.anatomy.mathloom).unwrap();
        let psi = settle_psi_krimelack(
            &fixture.anatomy.psi,
            &fixture.state.psi,
            &delivered,
        )
        .unwrap();
        let zero_work = GateWorkOccurrence::new(Exact::zero());
        let genesis_barrier = gate_open_minus_closed_free_energy(
            &fixture.anatomy.gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &psi.successor,
            &zero_work,
        )
        .unwrap();
        let mut retained = fixture.state.clone();
        retained.plastic =
            PlasticSupportState::from_physical_parts(r(4, 3), 0, r(0, 1)).unwrap();
        let retained_barrier = gate_open_minus_closed_free_energy(
            &fixture.anatomy.gate,
            &fixture.anatomy.plastic,
            &retained.plastic,
            retained.membrane,
            fixture.anatomy.capacitance,
            &psi.successor,
            &zero_work,
        )
        .unwrap();

        assert_ne!(genesis_barrier, retained_barrier);
        let genesis_window = gate_opening_quantum_window(
            &fixture.anatomy,
            &fixture.state,
            bind_isolated_neuron_perspective(&shared, 1).unwrap(),
        )
        .unwrap();
        let retained_window = gate_opening_quantum_window(
            &fixture.anatomy,
            &retained,
            bind_isolated_neuron_perspective(&shared, 1).unwrap(),
        )
        .unwrap();

        assert_eq!(
            genesis_window.opening_threshold_quanta,
            retained_window.opening_threshold_quanta
        );
    }

    #[test]
    fn powered_dark_interval_pumps_existing_gradient_without_a_voltage_target() {
        let fixture = physical_fixture();
        let electrical = SparseElectricalAnatomy::new(1, Vec::new()).unwrap();
        let mut neuron = fixture.state.clone();
        neuron.membrane = LocalMembraneConductanceState::genesis(-1_000);
        neuron.carriers = CarrierReservoirs::new(6_241, 6_243);
        let anatomy = ReachedCohortAnatomy::new(
            vec![fixture.anatomy],
            fixture_lineages(1),
            fixture_source_sites(1),
            electrical.clone(),
        )
        .unwrap();
        let predecessor = ReachedCohortState::new(
            &anatomy,
            vec![neuron],
            SparseElectricalState::genesis(&electrical),
        )
        .unwrap();
        let predecessor_neuron = &predecessor.neurons()[0];
        let predecessor_work = membrane_and_gradient_work_zeptojoules(
            &anatomy.neuron_anatomies()[0],
            predecessor_neuron,
        )
        .unwrap();
        let predecessor_carriers = predecessor_neuron.carrier_reservoirs();
        let predecessor_charge = predecessor_neuron.separated_elementary_charges();
        let predecessor_energy = predecessor.recovery_fluid().physical_parts();

        let (successor, observation) =
            settle_reached_cohort_dark_rest(&anatomy, &predecessor, 250_000).unwrap();

        assert_eq!(observation.returned_elementary_charges, 0);
        assert_eq!(observation.fuel_quanta, 0);
        assert!(observation.pumped_elementary_charges < 0);
        let successor_neuron = &successor.neurons()[0];
        let successor_carriers = successor_neuron.carrier_reservoirs();
        assert_eq!(successor_carriers.total(), predecessor_carriers.total());
        assert_eq!(
            successor_carriers.intracellular() - predecessor_carriers.intracellular(),
            observation.pumped_elementary_charges.unsigned_abs()
        );
        assert_eq!(
            successor_neuron.separated_elementary_charges(),
            predecessor_charge - observation.pumped_elementary_charges
        );
        let successor_work = membrane_and_gradient_work_zeptojoules(
            &anatomy.neuron_anatomies()[0],
            successor_neuron,
        )
        .unwrap();
        let local_pump_work = successor_work.checked_sub(predecessor_work).unwrap();
        assert_eq!(
            local_pump_work
                .checked_cmp(ExactRational::integer(0))
                .unwrap(),
            core::cmp::Ordering::Greater
        );
        let successor_energy = successor.recovery_fluid().physical_parts();
        assert_eq!(
            predecessor_energy
                .0
                .checked_sub(successor_energy.0)
                .unwrap(),
            local_pump_work
        );
        assert_eq!(
            successor_energy
                .1
                .checked_sub(predecessor_energy.1)
                .unwrap(),
            local_pump_work
        );
        assert_eq!(successor_energy.2, predecessor_energy.2);
        let encoded_successor = encode_reached_cohort_state(&anatomy, &successor).unwrap();
        assert_eq!(
            decode_reached_cohort_state(&anatomy, &encoded_successor).unwrap(),
            successor
        );
    }

    #[test]
    fn powered_environment_recharges_exhausted_body_before_local_pump() {
        let fixture = physical_fixture();
        let electrical = SparseElectricalAnatomy::new(1, Vec::new()).unwrap();
        let mut neuron = fixture.state.clone();
        neuron.membrane = LocalMembraneConductanceState::genesis(-1_000);
        neuron.carriers = CarrierReservoirs::new(6_241, 6_243);
        let anatomy = ReachedCohortAnatomy::new(
            vec![fixture.anatomy],
            fixture_lineages(1),
            fixture_source_sites(1),
            electrical.clone(),
        )
        .unwrap();
        let powered = ReachedCohortState::new(
            &anatomy,
            vec![neuron],
            SparseElectricalState::genesis(&electrical),
        )
        .unwrap();
        let reservoir_anatomy = ReachedCohortState::recovery_fluid_anatomy_for_test(&anatomy);
        let (_, spent_capacity, thermal_capacity) = reservoir_anatomy.capacities();
        let exhausted_reservoir = RecoveryFluidReservoirState::new(
            reservoir_anatomy,
            ExactRational::integer(0),
            spent_capacity,
            thermal_capacity,
        )
        .unwrap();
        let predecessor = powered
            .with_recovery_fluid_for_test(&anatomy, exhausted_reservoir)
            .unwrap();

        let (successor, observation) =
            settle_reached_cohort_dark_rest(&anatomy, &predecessor, 250_000).unwrap();

        assert_ne!(successor, predecessor);
        assert!(observation.pumped_elementary_charges < 0);
        assert_eq!(
            observation
                .environment_energy_delivered_zeptojoules
                .checked_cmp(ExactRational::integer(0))
                .unwrap(),
            core::cmp::Ordering::Greater
        );
        assert_eq!(
            observation
                .environment_heat_exported_zeptojoules
                .checked_cmp(ExactRational::integer(0))
                .unwrap(),
            core::cmp::Ordering::Greater
        );
        assert_eq!(observation.returned_elementary_charges, 0);
        assert_eq!(observation.fuel_quanta, 0);
    }

    #[test]
    fn active_frontier_pumps_only_the_reached_neuron() {
        let [first, second] = physical_fixtures::<2>();
        let electrical = SparseElectricalAnatomy::new(2, Vec::new()).unwrap();
        let mut first_state = first.state.clone();
        first_state.membrane = LocalMembraneConductanceState::genesis(-1_000);
        first_state.carriers = CarrierReservoirs::new(0, 12_484);
        let mut second_state = second.state.clone();
        second_state.membrane = LocalMembraneConductanceState::genesis(-1_000);
        second_state.carriers = CarrierReservoirs::new(0, 12_484);
        let anatomy = ReachedCohortAnatomy::new(
            vec![first.anatomy, second.anatomy],
            fixture_lineages(2),
            fixture_source_sites(2),
            electrical.clone(),
        )
        .unwrap();
        let predecessor = ReachedCohortState::new(
            &anatomy,
            vec![first_state, second_state],
            SparseElectricalState::genesis(&electrical),
        )
        .unwrap();
        let predecessor_first = predecessor.neurons()[0].clone();
        let predecessor_second = predecessor.neurons()[1].clone();
        let predecessor_material = predecessor
            .neurons()
            .iter()
            .map(|neuron| neuron.carrier_reservoirs().total().unwrap())
            .sum::<u128>();

        let (successor, observation) =
            settle_reached_cohort_membrane_pumps(&anatomy, &predecessor, &[1], 250_000).unwrap();

        assert_eq!(successor.neurons()[0], predecessor_first);
        assert_ne!(successor.neurons()[1], predecessor_second);
        assert!(successor.neurons()[1].carrier_reservoirs().intracellular() > 0);
        assert!(observation.pumped_elementary_charges < 0);
        assert_eq!(observation.recovered_neuron_count, 1);
        assert_eq!(observation.reached_neuron_count, 1);
        assert_eq!(observation.changed_reached_neuron_count, 1);
        assert_eq!(observation.unchanged_unreached_neuron_count, 1);
        assert_eq!(observation.changed_unreached_neuron_count, 0);
        assert_eq!(observation.localized_fluid_chemistry.len(), 1);
        let local = observation.localized_fluid_chemistry[0];
        assert_eq!(local.neuron_index, 1);
        assert_eq!(local.predecessor_intracellular_carriers, 0);
        assert_eq!(
            local.predecessor_intracellular_carriers + local.predecessor_extracellular_carriers,
            local.successor_intracellular_carriers + local.successor_extracellular_carriers
        );
        assert_eq!(
            local.successor_intracellular_carriers as i128,
            local.predecessor_intracellular_carriers as i128 - local.pumped_elementary_charges
        );
        assert_eq!(
            local.successor_extracellular_carriers as i128,
            local.predecessor_extracellular_carriers as i128 + local.pumped_elementary_charges
        );
        assert_eq!(
            local.successor_reservoir.0,
            local
                .predecessor_reservoir
                .0
                .checked_sub(local.membrane_gradient_work_zeptojoules)
                .unwrap()
        );
        assert_eq!(
            local.successor_reservoir.1,
            local
                .predecessor_reservoir
                .1
                .checked_add(local.membrane_gradient_work_zeptojoules)
                .unwrap()
        );
        assert_eq!(local.successor_reservoir.2, local.predecessor_reservoir.2);
        assert_eq!(successor.electrical(), predecessor.electrical());
        assert_eq!(
            successor
                .neurons()
                .iter()
                .map(|neuron| neuron.carrier_reservoirs().total().unwrap())
                .sum::<u128>(),
            predecessor_material
        );
    }

    fn population_gate(
        fixture: &Fixture,
        population: u128,
        dissipation_quantum_zeptojoules: Exact,
    ) -> TwoStateGateAnatomy {
        TwoStateGateAnatomy::new(
            population,
            0,
            q(0, 1),
            dissipation_quantum_zeptojoules,
            100_000,
            r(1, 1),
            r(-1, 1),
            Vec::new(),
            fixture.ring_count,
        )
        .unwrap()
    }

    #[test]
    fn one_channel_population_is_the_original_two_state_energy_law() {
        let fixture = physical_fixture();
        let gate = population_gate(&fixture, 1, q(1, 1));
        let work = GateWorkOccurrence::new(q(-9, 1));
        let original_delta = rational_to_exact(
            open_minus_closed_support_energy(&fixture.anatomy.plastic, &fixture.state.plastic)
                .unwrap(),
        ) + q(-9, 1);
        let graded_delta = gate_open_minus_closed_free_energy(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &work,
        )
        .unwrap();
        assert_eq!(graded_delta, original_delta);
        assert_eq!(graded_delta, q(-1, 1));

        let settlement = select_gate_population_settlement(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            &fixture.state.gate,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &work,
            None,
        )
        .unwrap()
        .unwrap();
        assert_eq!(settlement.open_population, 1);
        assert_eq!(settlement.released_quanta, 1);

        let fractional = select_gate_population_settlement(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            &fixture.state.gate,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &GateWorkOccurrence::new(q(-17, 2)),
            None,
        )
        .unwrap()
        .unwrap();
        assert_eq!(fractional.open_population, 1);
        assert_eq!(fractional.released_quanta, 0);
        assert_eq!(
            fractional.dissipation_residue_zeptojoules.energy(),
            &rational_to_exact(r(1, 2))
        );
    }

    #[test]
    fn downhill_gate_exports_exact_heat_beyond_its_finite_local_capacity() {
        let predecessor_residue = PhysicalEnergyResidue {
            energy_zeptojoules: q(1, 4),
        };
        let released = q(10, 1);
        let quantum = q(1, 1);
        let (retained_quanta, retained_residue, exported_heat) =
            quantize_gate_release(&predecessor_residue, &released, &quantum, Some(2))
                .unwrap()
                .unwrap();
        assert_eq!(retained_quanta, 2);
        assert_eq!(retained_residue.energy(), &q(0, 1));
        assert_eq!(exported_heat, q(33, 4));
        assert_eq!(
            quantum * Exact::from_integer(BigInt::from(retained_quanta)) + exported_heat,
            predecessor_residue.energy() + &released,
        );
    }

    #[test]
    fn channel_population_retains_distinct_exact_magnitudes_without_duplicating_work() {
        let fixture = physical_fixture();
        let gate = population_gate(&fixture, 4, q(1, 2));
        let settle = |work| {
            select_gate_population_settlement(
                &gate,
                &fixture.anatomy.plastic,
                &fixture.state.plastic,
                &fixture.state.gate,
                fixture.state.membrane,
                fixture.anatomy.capacitance,
                &fixture.state.psi,
                &GateWorkOccurrence::new(q(work, 1)),
                None,
            )
            .unwrap()
            .unwrap()
        };
        let lower = settle(-4);
        let higher = settle(-8);
        assert_eq!(lower.open_population, 1);
        assert_eq!(higher.open_population, 2);

        let zero_work = gate_population_free_energy(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &GateWorkOccurrence::new(q(0, 1)),
            4,
        )
        .unwrap();
        let full_work = gate_population_free_energy(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &GateWorkOccurrence::new(q(-8, 1)),
            4,
        )
        .unwrap();
        assert_eq!(full_work - zero_work, q(-8, 1));
    }

    #[test]
    fn open_receptor_population_settles_exact_work_without_opening_more_channels() {
        let fixture = physical_fixture();
        let gate = TwoStateGateAnatomy::new_independent_channels(
            4,
            0,
            q(0, 1),
            q(1, 2),
            100_000,
            r(1, 1),
            r(-1, 1),
            Vec::new(),
            fixture.ring_count,
        )
        .unwrap();
        let mut predecessor_gate = fixture.state.gate.clone();
        predecessor_gate.open_population = 2;
        let delivered = q(3, 1);
        let settlement = select_gate_population_settlement(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            &predecessor_gate,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &GateWorkOccurrence::receptor_activation(-delivered.clone(), 2).unwrap(),
            None,
        )
        .unwrap()
        .unwrap();

        assert_eq!(settlement.open_population, 2);
        assert_eq!(settlement.released_quanta, 6);
        assert_eq!(
            gate.dissipation_quantum_zeptojoules
                * Exact::from_integer(BigInt::from(settlement.released_quanta))
                + settlement.dissipation_residue_zeptojoules.energy()
                + settlement.exported_heat_zeptojoules,
            predecessor_gate.dissipation_residue_zeptojoules.energy() + delivered,
        );
    }

    #[test]
    fn tied_lowest_population_retains_the_predecessor() {
        let fixture = physical_fixture();
        let gate = population_gate(&fixture, 3, q(1, 9));
        let settlement = select_gate_population_settlement(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            &fixture.state.gate,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &GateWorkOccurrence::new(q(-8, 1)),
            None,
        )
        .unwrap();
        assert_eq!(settlement, None);
    }

    #[test]
    fn logarithmic_population_minimum_matches_exhaustive_convex_law() {
        let fixture = physical_fixture();
        for population in 2..=16_u128 {
            let gate = population_gate(&fixture, population, q(1, 16));
            for predecessor_open in 0..=population {
                let mut predecessor_gate = fixture.state.gate.clone();
                predecessor_gate.open_population = predecessor_open;
                for signed_work in -32..=32_i64 {
                    let work = GateWorkOccurrence::new(q(signed_work, 1));
                    let predecessor_energy = gate_population_free_energy(
                        &gate,
                        &fixture.anatomy.plastic,
                        &fixture.state.plastic,
                        fixture.state.membrane,
                        fixture.anatomy.capacitance,
                        &fixture.state.psi,
                        &work,
                        predecessor_open,
                    )
                    .unwrap();
                    let mut exhaustive: Option<(u128, Exact)> = None;
                    let mut tied = false;
                    for candidate in 0..=population {
                        if candidate == predecessor_open {
                            continue;
                        }
                        let energy = gate_population_free_energy(
                            &gate,
                            &fixture.anatomy.plastic,
                            &fixture.state.plastic,
                            fixture.state.membrane,
                            fixture.anatomy.capacitance,
                            &fixture.state.psi,
                            &work,
                            candidate,
                        )
                        .unwrap();
                        if energy >= predecessor_energy {
                            continue;
                        }
                        match exhaustive.as_ref() {
                            None => {
                                exhaustive = Some((candidate, energy));
                                tied = false;
                            }
                            Some((_, lowest)) if energy < *lowest => {
                                exhaustive = Some((candidate, energy));
                                tied = false;
                            }
                            Some((_, lowest)) if energy == *lowest => tied = true,
                            Some(_) => {}
                        }
                    }
                    let expected = if tied {
                        None
                    } else {
                        exhaustive.map(|(candidate, _)| candidate)
                    };
                    let observed = select_gate_population_settlement(
                        &gate,
                        &fixture.anatomy.plastic,
                        &fixture.state.plastic,
                        &predecessor_gate,
                        fixture.state.membrane,
                        fixture.anatomy.capacitance,
                        &fixture.state.psi,
                        &work,
                        None,
                    )
                    .unwrap()
                    .map(|settlement| settlement.open_population);
                    assert_eq!(
                        observed, expected,
                        "population={population} predecessor={predecessor_open} work={signed_work}"
                    );
                }
            }
        }
    }

    #[test]
    fn multi_million_channel_population_settles_without_population_scan() {
        let fixture = physical_fixture();
        let population = 4_563_410_u128;
        let gate = population_gate(&fixture, population, q(1, 16));
        let settled = select_gate_population_settlement(
            &gate,
            &fixture.anatomy.plastic,
            &fixture.state.plastic,
            &fixture.state.gate,
            fixture.state.membrane,
            fixture.anatomy.capacitance,
            &fixture.state.psi,
            &GateWorkOccurrence::new(q(-9, 1)),
            None,
        )
        .unwrap();
        assert!(settled
            .as_ref()
            .is_none_or(|value| value.open_population <= population));
    }

    fn scaled_physical_fixture(positions: usize, constraint_count: usize) -> Fixture {
        scaled_physical_fixture_at(positions, constraint_count, 0)
    }

    fn scaled_physical_fixture_at(
        positions: usize,
        constraint_count: usize,
        topology_index: u32,
    ) -> Fixture {
        let ring_count = positions * constraint_count * 2;
        let psi = PsiKrimelackAnatomy::new(
            positions,
            constraint_count,
            vec![ring_anatomy(); ring_count],
        )
        .unwrap();
        let gate = TwoStateGateAnatomy::new(
            2,
            0,
            q(0, 1),
            q(1, 9),
            10_000,
            r(1, 1),
            r(-1, 1),
            vec![GatePsiContact::new(0, 1, 1, q(12, 1)).unwrap()],
            ring_count,
        )
        .unwrap();
        let recovery_lane =
            RecoveryLaneAnatomy::new(1, 1, 1, 1, 100_000, 100_000, 100_000).unwrap();
        let recovery = RecoveryAnatomy::new(
            vec![recovery_lane; ring_count],
            recovery_lane,
            recovery_lane,
            ring_count,
        )
        .unwrap();
        let dna_expression = DnaExpressionAnatomy::new(1, 1, 1, 1, 1, 100_000, 100_000).unwrap();
        let plastic =
            PlasticSupportAnatomy::new(r(4, 1), r(1, 1), r(1, 1), r(3, 1), r(1, 72), 100_000)
                .unwrap();
        let anatomy = NeuronPhysicalAnatomy::new(
            MathLoomAnatomy::new(positions).unwrap(),
            psi.clone(),
            gate,
            membrane_capacitance_from_declared_geometry(
                r(1, 1),
                &NeuronSourceSite::fixture(topology_index),
            )
            .unwrap(),
            recovery,
            dna_expression,
            plastic,
        )
        .unwrap();
        let state = NeuronPhysicalState::new(
            PsiKrimelackState::genesis(&psi),
            TwoStateGateState::genesis(0),
            LocalMembraneConductanceState::genesis(0),
            CarrierReservoirs::new(1_000_000, 1_000_000),
            RecoveryState::new(
                vec![RecoveryLaneState::new(100_000); ring_count],
                RecoveryLaneState::new(100_000),
                RecoveryLaneState::new(100_000),
            ),
            DnaExpressionState::new(100_000, 100_000),
            PlasticSupportState::new(r(1, 1)).unwrap(),
            r(0, 1),
            r(0, 1),
        );
        Fixture {
            anatomy,
            state,
            zero_catalysts: vec![0; ring_count],
            ring_count,
        }
    }

    /// PERSISTED-STATE QUARANTINE: a body whose retired membrane-return residue
    /// is zero must encode byte-identically, while a historical nonzero value
    /// remains readable without becoming runtime energy or pump authority.
    #[test]
    fn a_zero_return_residue_encodes_byte_identically_to_the_pre_law_body() {
        let fixture = physical_fixture();
        let zero = encode_neuron_physical_state(&fixture.anatomy, &fixture.state).unwrap();
        assert_eq!(&zero[..8], NEURON_STATE_CODEC_MAGIC);
        assert_eq!(
            decode_neuron_physical_state(&fixture.anatomy, &zero).unwrap(),
            fixture.state
        );

        let mut owing = fixture.state.clone();
        owing.membrane_return_work_residue = ExactRational::new(3, 88).unwrap();
        let nonzero = encode_neuron_physical_state(&fixture.anatomy, &owing).unwrap();
        assert_eq!(&nonzero[..8], NEURON_STATE_RETURN_RESIDUE_MAGIC);
        // Same layout, one magic and two exact-rational words wider; every
        // pre-existing byte is where it was.
        assert_eq!(nonzero.len(), zero.len() + 32);
        assert_eq!(&nonzero[40..], &zero[8..]);
        assert_eq!(&nonzero[8..24], &3_i128.to_le_bytes());
        assert_eq!(&nonzero[24..40], &88_u128.to_le_bytes());
        let restored = decode_neuron_physical_state(&fixture.anatomy, &nonzero).unwrap();
        assert_eq!(restored, owing);
        assert_eq!(
            encode_neuron_physical_state(&fixture.anatomy, &restored).unwrap(),
            nonzero
        );

        // One physical state, one encoding: the residue-carrying layout may
        // not restate a zero residue.  The retired layout remains restricted
        // to the historical sub-quantum range it originally authenticated.
        let mut zero_in_the_wide_layout = Vec::new();
        zero_in_the_wide_layout.extend_from_slice(NEURON_STATE_RETURN_RESIDUE_MAGIC);
        push_i128(&mut zero_in_the_wide_layout, 0);
        push_u128(&mut zero_in_the_wide_layout, 1);
        zero_in_the_wide_layout.extend_from_slice(&zero[8..]);
        assert_eq!(
            decode_neuron_physical_state(&fixture.anatomy, &zero_in_the_wide_layout),
            Err(NeuronStateCodecError::InvalidEncoding)
        );

        let mut whole_quantum_owed = fixture.state.clone();
        whole_quantum_owed.membrane_return_work_residue = ExactRational::new(1, 9).unwrap();
        assert_eq!(
            rational_to_exact(whole_quantum_owed.membrane_return_work_residue),
            fixture.anatomy.gate.dissipation_quantum_zeptojoules
        );
        assert_eq!(
            encode_neuron_physical_state(&fixture.anatomy, &whole_quantum_owed),
            Err(NeuronStateCodecError::AnatomyMismatch)
        );

        let mut negative_debt = fixture.state.clone();
        negative_debt.membrane_return_work_residue = ExactRational::new(-1, 2).unwrap();
        assert_eq!(
            encode_neuron_physical_state(&fixture.anatomy, &negative_debt),
            Err(NeuronStateCodecError::AnatomyMismatch)
        );
    }

    #[test]
    fn physical_state_clone_shares_until_exact_mutation_and_preserves_codec_bytes() {
        let fixture = scaled_physical_fixture(2_048, 7);
        let original_bytes =
            encode_neuron_physical_state(&fixture.anatomy, &fixture.state).unwrap();
        let mut successor = fixture.state.clone();

        assert!(fixture.state.shares_physical_body_with(&successor));
        assert_eq!(
            sparse_physical_state_delta(&fixture.state, &successor).unwrap(),
            None
        );
        assert_eq!(
            encode_neuron_physical_state(&fixture.anatomy, &successor).unwrap(),
            original_bytes
        );

        successor.receptor_quantum_residue = r(1, 2);

        assert!(!fixture.state.shares_physical_body_with(&successor));
        assert!(
            sparse_physical_state_delta(&fixture.state, &successor)
                .unwrap()
                .is_some()
        );
        assert_eq!(fixture.state.receptor_quantum_residue, r(0, 1));
        assert_eq!(successor.receptor_quantum_residue, r(1, 2));
        assert_eq!(
            encode_neuron_physical_state(&fixture.anatomy, &fixture.state).unwrap(),
            original_bytes
        );
        assert_eq!(
            decode_neuron_physical_state(&fixture.anatomy, &original_bytes).unwrap(),
            fixture.state
        );
    }

    #[test]
    fn definitive_neuron_anatomy_and_state_cold_restore_exactly() {
        let fixture = physical_fixture();
        let anatomy_bytes = encode_neuron_physical_anatomy(&fixture.anatomy).unwrap();
        let restored_anatomy = decode_neuron_physical_anatomy(&anatomy_bytes).unwrap();
        assert_eq!(restored_anatomy, fixture.anatomy);
        assert_eq!(
            encode_neuron_physical_anatomy(&restored_anatomy).unwrap(),
            anatomy_bytes
        );

        let cell = encode_neuron_physical_cell(&fixture.anatomy, &fixture.state).unwrap();
        let (restored_anatomy, restored_state) = decode_neuron_physical_cell(&cell).unwrap();
        assert_eq!(restored_anatomy, fixture.anatomy);
        assert_eq!(restored_state, fixture.state);
        assert_eq!(
            encode_neuron_physical_cell(&restored_anatomy, &restored_state).unwrap(),
            cell
        );
        assert_eq!(
            decode_neuron_physical_cell(&cell[..cell.len() - 1]),
            Err(NeuronAnatomyCodecError::InvalidEncoding)
        );

        let mut incompatible_anatomy = fixture.anatomy.clone();
        incompatible_anatomy.gate.population = 1;
        let mut incompatible_state = fixture.state.clone();
        incompatible_state.gate.open_population = 2;
        let state_bytes =
            encode_neuron_physical_state(&fixture.anatomy, &incompatible_state).unwrap();
        assert_eq!(
            decode_neuron_physical_state(&incompatible_anatomy, &state_bytes),
            Err(NeuronStateCodecError::AnatomyMismatch)
        );

        let mut overfilled_recovery = fixture.state.clone();
        overfilled_recovery.recovery.psi_lanes[0].fuel_quanta = 100_001;
        assert_eq!(
            encode_neuron_physical_state(&fixture.anatomy, &overfilled_recovery),
            Err(NeuronStateCodecError::AnatomyMismatch)
        );

        let mut impossible_ring_allocation = Vec::new();
        impossible_ring_allocation.extend_from_slice(NEURON_ANATOMY_CODEC_MAGIC);
        impossible_ring_allocation.extend_from_slice(&1_u64.to_le_bytes());
        impossible_ring_allocation.extend_from_slice(&1_000_u64.to_le_bytes());
        impossible_ring_allocation.extend_from_slice(&2_000_u64.to_le_bytes());
        assert_eq!(
            decode_neuron_physical_anatomy(&impossible_ring_allocation),
            Err(NeuronAnatomyCodecError::InvalidEncoding)
        );
    }

    fn interval<'a>(
        perspective: JointNeuronPerspective<'a>,
        catalysts: &'a [u128],
    ) -> NeuronIntervalInput<'a> {
        NeuronIntervalInput {
            perspective,
            gate_work: GateWorkOccurrence::new(q(0, 1)),
            interval_microseconds: 1_000,
            recovery: RecoveryContact::new(catalysts, 0, 0),
            dna_expression: DnaExpressionContact::new(0),
            receptor_successor_residue: None,
            prepared_psi: None,
        }
    }

    fn cohort_interval_with_work<'a>(
        shared: &'a SharedCompleteJointField,
        fixtures: &'a [Fixture; 3],
        gate_index: usize,
        gate_work: [i64; 3],
    ) -> ReachedCohortIntervalInput<'a> {
        ReachedCohortIntervalInput::fixture(
            fixtures
                .iter()
                .enumerate()
                .map(|(index, fixture)| NeuronIntervalInput {
                    perspective: bind_neuron_perspective(shared, index, gate_index).unwrap(),
                    gate_work: GateWorkOccurrence::new(q(gate_work[index], 1)),
                    interval_microseconds: 1_000,
                    recovery: RecoveryContact::new(&fixture.zero_catalysts, 0, 0),
                    dna_expression: DnaExpressionContact::new(0),
                    receptor_successor_residue: None,
                    prepared_psi: None,
                })
                .collect(),
            fixture_source_sites(fixtures.len()),
        )
        .unwrap()
    }

    fn four_neuron_control_interval<'a>(
        shared: &'a SharedCompleteJointField,
        fixtures: &'a [Fixture; 4],
    ) -> ReachedCohortIntervalInput<'a> {
        ReachedCohortIntervalInput::fixture(
            fixtures
                .iter()
                .enumerate()
                .map(|(index, fixture)| NeuronIntervalInput {
                    perspective: bind_neuron_perspective(shared, index, 0).unwrap(),
                    gate_work: GateWorkOccurrence::new(q(100, 1)),
                    interval_microseconds: 1_000,
                    recovery: RecoveryContact::new(&fixture.zero_catalysts, 0, 0),
                    dna_expression: DnaExpressionContact::new(0),
                    receptor_successor_residue: None,
                    prepared_psi: None,
                })
                .collect(),
            fixture_source_sites(fixtures.len()),
        )
        .unwrap()
    }

    fn four_neuron_interval_with_work<'a>(
        shared: &'a SharedCompleteJointField,
        fixtures: &'a [Fixture; 4],
        gate_index: usize,
        gate_work: [i64; 4],
    ) -> ReachedCohortIntervalInput<'a> {
        ReachedCohortIntervalInput::fixture(
            fixtures
                .iter()
                .enumerate()
                .map(|(index, fixture)| NeuronIntervalInput {
                    perspective: bind_neuron_perspective(shared, index, gate_index).unwrap(),
                    gate_work: GateWorkOccurrence::new(q(gate_work[index], 1)),
                    interval_microseconds: 1_000,
                    recovery: RecoveryContact::new(&fixture.zero_catalysts, 0, 0),
                    dna_expression: DnaExpressionContact::new(0),
                    receptor_successor_residue: None,
                    prepared_psi: None,
                })
                .collect(),
            fixture_source_sites(fixtures.len()),
        )
        .unwrap()
    }

    #[test]
    fn shared_dsf_causally_reaches_post_quiescence_fractal_and_control_is_zero() {
        let shared = shared_field();
        let control = bind_isolated_neuron_perspective(&shared, 0).unwrap();
        let perturbation = bind_isolated_neuron_perspective(&shared, 1).unwrap();
        assert_eq!(control.dsf().d_k, 0.0);
        assert_eq!(perturbation.dsf().d_k, 1.0);

        let fixture = physical_fixture();
        let predecessor = settle_to_quiescence(
            &fixture.anatomy,
            &fixture.state,
            &[
                interval(control, &fixture.zero_catalysts),
                interval(control, &fixture.zero_catalysts),
            ],
        )
        .unwrap();

        let delivered = settle_shared_dsf_mathloom(perturbation, fixture.anatomy.mathloom).unwrap();
        let displacement = &delivered.constraints()[0];
        let causal_interval = settle_neuron_physical_interval(
            &fixture.anatomy,
            predecessor.state(),
            perturbation,
            GateWorkOccurrence::new(q(0, 1)),
            1_000,
        )
        .unwrap();
        assert_eq!(displacement.family(), DsfFactFamily::Displacement);
        assert_eq!(displacement.binary64_bits(), 1.0_f64.to_bits());
        assert_eq!(
            causal_interval.psi.successor.rings()[0].winding(),
            BalancedTrit::Positive
        );
        assert_eq!(
            causal_interval
                .gate_membrane
                .successor_gate
                .open_population(),
            2
        );
        assert_ne!(
            causal_interval.gate_membrane.membrane.successor,
            causal_interval.gate_membrane.membrane.predecessor
        );
        assert_eq!(
            causal_interval.gate_membrane.successor_carriers.total(),
            predecessor.state().carriers.total()
        );

        let post = [
            interval(control, &fixture.zero_catalysts),
            interval(control, &fixture.zero_catalysts),
        ];
        let settled = settle_experience_to_quiescence(
            &fixture.anatomy,
            &predecessor,
            interval(perturbation, &fixture.zero_catalysts),
            &post,
        )
        .unwrap();
        assert_eq!(settled.quiescent.state().gate.open_population(), 0);
        assert!(settled
            .quiescent
            .state()
            .psi
            .rings()
            .iter()
            .zip(predecessor.state().psi.rings())
            .all(|(successor, prior)| successor.winding() == prior.winding()));
        assert!(settled
            .quiescent
            .state()
            .psi
            .rings()
            .iter()
            .zip(predecessor.state().psi.rings())
            .any(|(successor, prior)| {
                successor.dissipated_quanta() > prior.dissipated_quanta()
            }));
        assert_eq!(
            settled
                .fractal
                .as_ref()
                .unwrap()
                .exact_delta(PhysicalStateCoordinate::PlasticRestLength),
            Some(ExactPhysicalStateDelta::Rational(r(1, 3)))
        );
        assert!(settled.fractal.as_ref().unwrap().entries().len() > 1);

        let control_only = settle_experience_to_quiescence(
            &fixture.anatomy,
            &predecessor,
            interval(control, &fixture.zero_catalysts),
            &[],
        )
        .unwrap();
        assert!(control_only.fractal.is_none());
    }

    #[test]
    fn newly_opened_channels_are_one_transient_emission_not_retained_state() {
        let shared = shared_field();
        let control = bind_isolated_neuron_perspective(&shared, 0).unwrap();
        let perturbation = bind_isolated_neuron_perspective(&shared, 1).unwrap();
        let fixture = physical_fixture();
        let predecessor = settle_to_quiescence(
            &fixture.anatomy,
            &fixture.state,
            &[
                interval(control, &fixture.zero_catalysts),
                interval(control, &fixture.zero_catalysts),
            ],
        )
        .unwrap();

        let opened = settle_extended_interval(
            &fixture.anatomy,
            predecessor.state(),
            interval(perturbation, &fixture.zero_catalysts),
        )
        .unwrap();
        assert_eq!(opened.newly_opened_gate_channels, 2);
        assert_eq!(opened.successor.gate.open_population(), 2);

        let recovery = settle_extended_interval(
            &fixture.anatomy,
            &opened.successor,
            interval(control, &fixture.zero_catalysts),
        )
        .unwrap();
        assert_eq!(recovery.newly_opened_gate_channels, 0);
        assert!(recovery.successor.gate.open_population() <= 2);
    }

    #[test]
    fn fixed_anatomy_and_recurrence_do_not_grow_resident_state() {
        let shared = shared_field();
        let control = bind_isolated_neuron_perspective(&shared, 0).unwrap();
        let fixture = physical_fixture();
        let mut quiescent = settle_to_quiescence(
            &fixture.anatomy,
            &fixture.state,
            &[
                interval(control, &fixture.zero_catalysts),
                interval(control, &fixture.zero_catalysts),
            ],
        )
        .unwrap();
        let state_width = core::mem::size_of_val(quiescent.state());
        let psi_width = quiescent.state().psi.rings().len();
        assert_eq!(psi_width, fixture.ring_count);
        for _ in 0..100 {
            let settled = settle_experience_to_quiescence(
                &fixture.anatomy,
                &quiescent,
                interval(control, &fixture.zero_catalysts),
                &[],
            )
            .unwrap();
            assert!(settled.fractal.is_none());
            quiescent = settled.quiescent;
            assert_eq!(core::mem::size_of_val(quiescent.state()), state_width);
            assert_eq!(quiescent.state().psi.rings().len(), psi_width);
        }
    }

    #[test]
    fn three_complete_neurons_and_one_contact_commit_one_synchronous_generation() {
        let shared = shared_three_neuron_field();
        let fixtures = physical_fixtures::<3>();
        let mut predecessor_neurons = fixtures
            .iter()
            .map(|fixture| fixture.state.clone())
            .collect::<Vec<_>>();
        predecessor_neurons[0].membrane = LocalMembraneConductanceState::genesis(1_000_000);

        let electrical_anatomy = SparseElectricalAnatomy::new(
            3,
            vec![ElectricalContactAnatomy::new(0, 1, r(1, 1), 3).unwrap()],
        )
        .unwrap();
        let electrical_state = SparseElectricalState::genesis(&electrical_anatomy);
        let cohort_anatomy = ReachedCohortAnatomy::new(
            fixtures
                .iter()
                .map(|fixture| fixture.anatomy.clone())
                .collect(),
            fixture_lineages(fixtures.len()),
            fixture_source_sites(fixtures.len()),
            electrical_anatomy,
        )
        .unwrap();
        let predecessor = ReachedCohortState::new(
            &cohort_anatomy,
            predecessor_neurons.clone(),
            electrical_state,
        )
        .unwrap();
        let inputs = fixtures
            .iter()
            .enumerate()
            .map(|(index, fixture)| {
                interval(
                    bind_neuron_perspective(&shared, index, 1).unwrap(),
                    &fixture.zero_catalysts,
                )
            })
            .collect::<Vec<_>>();
        let baselines = fixtures
            .iter()
            .zip(predecessor_neurons.iter())
            .zip(inputs.iter().cloned())
            .map(|((fixture, state), input)| {
                settle_extended_interval_with_contact(&fixture.anatomy, state, input, 0)
                    .unwrap()
                    .successor
            })
            .collect::<Vec<_>>();
        let predecessor_material = predecessor
            .neurons()
            .iter()
            .map(|state| state.carrier_reservoirs().total().unwrap())
            .sum::<u128>();
        let settled = settle_reached_cohort_interval(
            &cohort_anatomy,
            &predecessor,
            ReachedCohortIntervalInput::fixture(inputs, fixture_source_sites(fixtures.len()))
                .unwrap(),
        )
        .unwrap();

        assert_eq!(cohort_anatomy.neuron_count(), 3);
        assert_eq!(cohort_anatomy.contact_count(), 1);
        assert_eq!(settled.contact_transitions.len(), 1);
        let transferred = settled.contact_transitions[0].outward_elementary_charges_from_left;
        assert!(transferred > 0);
        assert_eq!(
            settled
                .contact_outward_elementary_charges_by_neuron
                .as_ref(),
            [transferred, -transferred, 0]
        );
        assert_eq!(
            settled
                .contact_outward_elementary_charges_by_neuron
                .iter()
                .sum::<i128>(),
            0
        );
        for index in 0..3 {
            let expected_contact = settled.contact_outward_elementary_charges_by_neuron[index];
            assert_eq!(
                settled.successor.neurons()[index]
                    .membrane_state()
                    .separated_elementary_charges(),
                baselines[index]
                    .membrane_state()
                    .separated_elementary_charges()
                    - expected_contact
            );
            let expected_intracellular = if expected_contact >= 0 {
                baselines[index].carrier_reservoirs().intracellular()
                    - expected_contact.unsigned_abs()
            } else {
                baselines[index].carrier_reservoirs().intracellular()
                    + expected_contact.unsigned_abs()
            };
            assert_eq!(
                settled.successor.neurons()[index]
                    .carrier_reservoirs()
                    .intracellular(),
                expected_intracellular
            );
            assert_eq!(
                settled.successor.neurons()[index]
                    .carrier_reservoirs()
                    .extracellular(),
                baselines[index].carrier_reservoirs().extracellular()
            );
        }
        assert_eq!(
            settled
                .successor
                .neurons()
                .iter()
                .map(|state| state.carrier_reservoirs().total().unwrap())
                .sum::<u128>(),
            predecessor_material
        );
        assert!(settled.electrically_active);
        assert!(!settled.quiescent);

        let reordered_inputs = fixtures
            .iter()
            .enumerate()
            .map(|(index, fixture)| {
                interval(
                    bind_neuron_perspective(&shared, index, 1).unwrap(),
                    &fixture.zero_catalysts,
                )
            })
            .collect::<Vec<_>>();
        let mut reordered_sites = fixture_source_sites(fixtures.len());
        reordered_sites.swap(0, 1);
        let reordered = settle_reached_cohort_interval(
            &cohort_anatomy,
            &predecessor,
            ReachedCohortIntervalInput::fixture(reordered_inputs, reordered_sites).unwrap(),
        )
        .unwrap();
        assert_eq!(reordered.successor.neurons().len(), fixtures.len());
    }

    #[test]
    fn differentiated_pair_breaks_the_blockade_and_descends() {
        // The ratified energy-descent charge-transfer law measured through the
        // cohort's own quiescence predicate, on the anatomy that now exists:
        // geometrically differentiated neurons (this cohort's first two carry
        // 1 pF and 3 pF from their own declared places), one authored 500 pS
        // contact, 1 ms intervals.
        //
        // MEASURED BEFORE the descent law: charges (-12,-11) on IDENTICAL 1 pF
        // neurons crossed one elementary charge every second interval forever
        // (+1/-1 limit cycle) and the cohort never quiesced.
        // MEASURED AFTER the descent law, on identical anatomy: the exact tie
        // blockaded every one-charge move — quiescent, but frozen.
        // MEASURED NOW, on differentiated anatomy: the odd residual is NOT
        // frozen.  Unequal capacitors equalize POTENTIAL, not charge, so the
        // pair descends — strictly, one whole charge at a time, never
        // reversing — to the charge split its own geometry demands and only
        // then goes electrically silent.  That is the blockade broken by
        // anatomy, which is exactly what the differentiation ratification
        // claimed it would do.
        let shared = shared_three_neuron_field();
        let fixtures = physical_fixtures::<3>();
        let electrical_anatomy = SparseElectricalAnatomy::new(
            3,
            vec![ElectricalContactAnatomy::new(0, 1, r(500, 1), 3).unwrap()],
        )
        .unwrap();
        let cohort_anatomy = ReachedCohortAnatomy::new(
            fixtures
                .iter()
                .map(|fixture| fixture.anatomy.clone())
                .collect(),
            fixture_lineages(fixtures.len()),
            fixture_source_sites(fixtures.len()),
            electrical_anatomy.clone(),
        )
        .unwrap();
        assert_eq!(
            cohort_anatomy
                .neuron_anatomies()
                .iter()
                .map(|anatomy| anatomy.capacitance().picofarads().parts())
                .collect::<Vec<_>>(),
            [(1, 1), (3, 1), (6, 1)]
        );
        let cohort_state = |left: i128, right: i128| {
            let mut neurons = fixtures
                .iter()
                .map(|fixture| fixture.state.clone())
                .collect::<Vec<_>>();
            neurons[0].membrane = LocalMembraneConductanceState::genesis(left);
            neurons[1].membrane = LocalMembraneConductanceState::genesis(right);
            ReachedCohortState::new(
                &cohort_anatomy,
                neurons,
                SparseElectricalState::genesis(&electrical_anatomy),
            )
            .unwrap()
        };
        let inputs = || {
            ReachedCohortIntervalInput::fixture(
                fixtures
                    .iter()
                    .enumerate()
                    .map(|(index, fixture)| {
                        interval(
                            bind_neuron_perspective(&shared, index, 1).unwrap(),
                            &fixture.zero_catalysts,
                        )
                    })
                    .collect(),
                fixture_source_sites(fixtures.len()),
            )
            .unwrap()
        };
        let separated = |state: &ReachedCohortState| {
            state
                .neurons()
                .iter()
                .map(|neuron| neuron.membrane_state().separated_elementary_charges())
                .collect::<Vec<_>>()
        };

        // The odd residual that used to oscillate, then freeze.  On
        // differentiated geometry one whole charge crosses immediately, and it
        // crosses toward the LARGER membrane, which is the descending
        // direction: stored energy q^2 e^2 / 2C falls when charge moves to the
        // bigger capacitor.
        let odd = cohort_state(-12, -11);
        let opening = separated(&odd);
        assert_eq!(opening[0] - opening[1], -1);
        let settled = settle_reached_cohort_interval(&cohort_anatomy, &odd, inputs()).unwrap();
        assert!(settled.electrically_active);
        let crossed = settled.contact_transitions[0].outward_elementary_charges_from_left;
        let after = separated(&settled.successor);
        eprintln!(
            "MEASURE differentiated 1 pF / 3 pF pair, 500 pS, odd residual (-12,-11): \
             crossed {crossed} charges in the first millisecond, charges {opening:?} -> {after:?}"
        );
        // The blockade is gone: whole charges cross on the very first
        // millisecond, in one direction, and the pair's exact stored energy
        // q^2 e^2 / 2C strictly falls.  (Equal-capacitance neighbours could
        // not move at all: every one-charge move tied exactly.)
        assert_ne!(crossed, 0);
        assert_eq!(
            settled
                .contact_outward_elementary_charges_by_neuron
                .as_ref(),
            [crossed, -crossed, 0]
        );
        // The contact's own ledger is equal and opposite: charge is conserved
        // across it exactly.  (The members' raw charges also move on their own
        // local channel accounts, which is why the ledger, not the raw charge,
        // is what the contact law is read through.)
        //
        // Exact descent, in the law's own formula, for the move that was made:
        // dE * 2 / e^2 = (n^2 - 2 n q_left)/C_left + (n^2 + 2 n q_right)/C_right.
        let bracket = r(crossed * crossed - 2 * crossed * opening[0], 1)
            .checked_add(r(crossed * crossed + 2 * crossed * opening[1], 3))
            .unwrap();
        assert_eq!(
            bracket.checked_cmp(r(0, 1)).unwrap(),
            core::cmp::Ordering::Less
        );
        // It moved toward equal potential: the 3 pF membrane takes the charge,
        // heading for the split where it holds three times the 1 pF membrane's.
        assert!(crossed < 0);

        // Equal charge on unequal geometry is NOT rest: the larger membrane
        // still holds the lower potential, so the pair moves.
        let unequal_geometry = cohort_state(-12, -12);
        let settled =
            settle_reached_cohort_interval(&cohort_anatomy, &unequal_geometry, inputs()).unwrap();
        assert!(settled.electrically_active);
    }

    #[test]
    fn reached_cohort_requires_exact_sight_sound_and_body_source_anatomy() {
        let episode = exact_episode();
        let shared = prepare_complete_joint_field_admitted_fixture(&episode, 0).unwrap();
        let fixtures = physical_fixtures::<4>();
        let source_sites = (0..fixtures.len())
            .map(|index| {
                NeuronSourceSite::from_anchor(
                    bind_neuron_source_anchor(
                        &episode,
                        bind_neuron_perspective(&shared, index, 0).unwrap(),
                    )
                    .unwrap(),
                )
            })
            .collect::<Vec<_>>();
        assert_eq!(
            source_sites
                .iter()
                .map(NeuronSourceSite::sense)
                .collect::<Vec<_>>(),
            [
                PhysicalSourceSense::Sight,
                PhysicalSourceSense::Sound,
                PhysicalSourceSense::Sound,
                PhysicalSourceSense::Body,
            ]
        );
        assert_eq!(source_sites[1].topology_index(), 0);
        assert_eq!(source_sites[2].topology_index(), 1);

        let electrical_anatomy = SparseElectricalAnatomy::new(
            4,
            vec![
                ElectricalContactAnatomy::new(0, 1, r(250, 1), 4).unwrap(),
                ElectricalContactAnatomy::new(1, 2, r(250, 1), 4).unwrap(),
                ElectricalContactAnatomy::new(2, 3, r(250, 1), 4).unwrap(),
            ],
        )
        .unwrap();
        let anatomy = ReachedCohortAnatomy::new(
            fixtures
                .iter()
                .map(|fixture| fixture.anatomy.clone())
                .collect(),
            fixture_lineages(fixtures.len()),
            source_sites,
            electrical_anatomy.clone(),
        )
        .unwrap();
        let predecessor = ReachedCohortState::new(
            &anatomy,
            fixtures
                .iter()
                .map(|fixture| fixture.state.clone())
                .collect(),
            SparseElectricalState::genesis(&electrical_anatomy),
        )
        .unwrap();
        let inputs = fixtures
            .iter()
            .enumerate()
            .map(|(index, fixture)| {
                interval(
                    bind_neuron_perspective(&shared, index, 0).unwrap(),
                    &fixture.zero_catalysts,
                )
            })
            .collect::<Vec<_>>();
        let cohort_cell = encode_reached_cohort_cell(&anatomy, &predecessor).unwrap();
        let (restored_anatomy, restored_predecessor) =
            decode_reached_cohort_cell(&cohort_cell).unwrap();
        assert_eq!(restored_anatomy, anatomy);
        assert_eq!(restored_predecessor, predecessor);
        assert_eq!(
            encode_reached_cohort_cell(&restored_anatomy, &restored_predecessor).unwrap(),
            cohort_cell
        );
        assert!(decode_reached_cohort_cell(&cohort_cell[..cohort_cell.len() - 1]).is_err());
        let input = ReachedCohortIntervalInput::from_episode(&episode, inputs).unwrap();
        let settled = settle_reached_cohort_interval(&anatomy, &predecessor, input).unwrap();
        assert_eq!(settled.successor.neurons().len(), 4);
        assert_eq!(anatomy.source_sites().count(), 4);
    }

    #[test]
    fn three_neuron_causal_sequence_emits_three_true_post_quiescence_fractals() {
        let shared = shared_three_neuron_field();
        let mut fixtures = physical_fixtures::<3>();
        for fixture in &mut fixtures {
            fixture.anatomy.gate.single_channel_conductance_picosiemens = r(2, 1);
        }
        let electrical_anatomy = SparseElectricalAnatomy::new(
            3,
            vec![ElectricalContactAnatomy::new(0, 1, r(500, 1), 3).unwrap()],
        )
        .unwrap();
        let electrical_state = SparseElectricalState::genesis(&electrical_anatomy);
        let cohort_anatomy = ReachedCohortAnatomy::new(
            fixtures
                .iter()
                .map(|fixture| fixture.anatomy.clone())
                .collect(),
            fixture_lineages(fixtures.len()),
            fixture_source_sites(fixtures.len()),
            electrical_anatomy,
        )
        .unwrap();
        let genesis = ReachedCohortState::new(
            &cohort_anatomy,
            fixtures
                .iter()
                .map(|fixture| fixture.state.clone())
                .collect(),
            electrical_state,
        )
        .unwrap();
        let initial_controls = [
            cohort_interval_with_work(&shared, &fixtures, 0, [0, 0, 0]),
            cohort_interval_with_work(&shared, &fixtures, 0, [0, 0, 0]),
        ];
        let predecessor =
            settle_reached_cohort_to_quiescence(&cohort_anatomy, &genesis, &initial_controls)
                .unwrap();
        let predecessor_material = predecessor
            .state()
            .neurons()
            .iter()
            .map(|state| state.carrier_reservoirs().total().unwrap())
            .sum::<u128>();

        let causal_sequence = [
            cohort_interval_with_work(&shared, &fixtures, 1, [-100, 100, 100]),
            cohort_interval_with_work(&shared, &fixtures, 0, [100, 100, 100]),
            cohort_interval_with_work(&shared, &fixtures, 1, [100, -100, 100]),
            cohort_interval_with_work(&shared, &fixtures, 0, [100, 100, 100]),
            cohort_interval_with_work(&shared, &fixtures, 1, [100, 100, -100]),
            cohort_interval_with_work(&shared, &fixtures, 0, [100, 100, 100]),
            cohort_interval_with_work(&shared, &fixtures, 0, [0, 0, 0]),
            cohort_interval_with_work(&shared, &fixtures, 0, [0, 0, 0]),
        ];
        let settled = settle_reached_cohort_experience_to_quiescence(
            &cohort_anatomy,
            &predecessor,
            &causal_sequence,
        )
        .unwrap();
        assert!(settled.electrical_contact_was_active);
        assert_eq!(settled.neuron_fractals.len(), 3);
        for fractal in &settled.neuron_fractals {
            assert_eq!(
                fractal
                    .as_ref()
                    .unwrap()
                    .exact_delta(PhysicalStateCoordinate::PlasticRestLength),
                Some(ExactPhysicalStateDelta::Rational(r(1, 3)))
            );
            assert_eq!(
                fractal
                    .as_ref()
                    .unwrap()
                    .entries()
                    .iter()
                    .map(|entry| entry.coordinate())
                    .collect::<Vec<_>>(),
                vec![PhysicalStateCoordinate::PlasticRestLength]
            );
        }
        assert_eq!(
            settled
                .rest
                .as_ref()
                .unwrap()
                .state()
                .neurons()
                .iter()
                .map(|state| state.carrier_reservoirs().total().unwrap())
                .sum::<u128>(),
            predecessor_material
        );
    }

    #[test]
    fn four_neuron_partial_cue_recurs_through_sparse_chain_without_state_growth() {
        let shared = shared_four_neuron_field();
        let fixtures = physical_fixtures::<4>();
        let electrical_anatomy = SparseElectricalAnatomy::new(
            4,
            vec![
                ElectricalContactAnatomy::new(0, 1, r(250, 1), 4).unwrap(),
                ElectricalContactAnatomy::new(1, 2, r(250, 1), 4).unwrap(),
                ElectricalContactAnatomy::new(2, 3, r(250, 1), 4).unwrap(),
            ],
        )
        .unwrap();
        let electrical_state = SparseElectricalState::genesis(&electrical_anatomy);
        let cohort_anatomy = ReachedCohortAnatomy::new(
            fixtures
                .iter()
                .map(|fixture| fixture.anatomy.clone())
                .collect(),
            fixture_lineages(fixtures.len()),
            fixture_source_sites(fixtures.len()),
            electrical_anatomy,
        )
        .unwrap();
        let mut neurons = fixtures
            .iter()
            .map(|fixture| fixture.state.clone())
            .collect::<Vec<_>>();
        neurons[0].membrane = LocalMembraneConductanceState::genesis(800_000);
        let mut state =
            ReachedCohortState::new(&cohort_anatomy, neurons, electrical_state).unwrap();
        let resident_bytes = state.resident_bytes().unwrap();
        let initial_charge = state
            .neurons()
            .iter()
            .map(|neuron| neuron.membrane_state().separated_elementary_charges())
            .sum::<i128>();
        let initial_material = state
            .neurons()
            .iter()
            .map(|neuron| neuron.carrier_reservoirs().total().unwrap())
            .sum::<u128>();
        let mut fourth_neuron_reached = false;
        for recurrence in 0..100 {
            let settled = settle_reached_cohort_interval(
                &cohort_anatomy,
                &state,
                four_neuron_control_interval(&shared, &fixtures),
            )
            .unwrap();
            assert_eq!(settled.contact_transitions.len(), 3);
            assert_eq!(settled.successor.resident_bytes(), Some(resident_bytes));
            assert_eq!(
                settled
                    .successor
                    .neurons()
                    .iter()
                    .map(|neuron| neuron.membrane_state().separated_elementary_charges())
                    .sum::<i128>(),
                initial_charge
            );
            assert_eq!(
                settled
                    .successor
                    .neurons()
                    .iter()
                    .map(|neuron| neuron.carrier_reservoirs().total().unwrap())
                    .sum::<u128>(),
                initial_material
            );
            if recurrence >= 2
                && settled.successor.neurons()[3]
                    .membrane_state()
                    .separated_elementary_charges()
                    != 0
            {
                fourth_neuron_reached = true;
            }
            state = settled.successor;
        }
        assert!(fourth_neuron_reached);
        assert_eq!(state.neurons().len(), 4);
        assert_eq!(state.electrical().contact_count(), 3);
        let encoded = encode_reached_cohort_state(&cohort_anatomy, &state).unwrap();
        let restored = decode_reached_cohort_state(&cohort_anatomy, &encoded).unwrap();
        assert_eq!(restored, state);
        assert_eq!(restored.resident_bytes(), Some(resident_bytes));
        let uninterrupted = settle_reached_cohort_interval(
            &cohort_anatomy,
            &state,
            four_neuron_control_interval(&shared, &fixtures),
        )
        .unwrap();
        let after_restart = settle_reached_cohort_interval(
            &cohort_anatomy,
            &restored,
            four_neuron_control_interval(&shared, &fixtures),
        )
        .unwrap();
        assert_eq!(after_restart, uninterrupted);
        assert!(
            decode_reached_cohort_state(&cohort_anatomy, &encoded[..encoded.len() - 1]).is_err()
        );
    }

    #[test]
    #[ignore = "retired: fixture requires Boolean/member-set mosaic admission"]
    fn four_neuron_learned_assembly_admits_only_after_partial_cue_and_exact_restart() {
        let shared = shared_four_neuron_field();
        let mut fixtures = physical_fixtures::<4>();
        for fixture in &mut fixtures {
            fixture.anatomy.gate.single_channel_conductance_picosiemens = r(2, 1);
        }
        let electrical_anatomy = SparseElectricalAnatomy::new(
            4,
            vec![
                ElectricalContactAnatomy::new(0, 1, r(500, 1), 4).unwrap(),
                ElectricalContactAnatomy::new(1, 2, r(500, 1), 4).unwrap(),
                ElectricalContactAnatomy::new(2, 3, r(500, 1), 4).unwrap(),
            ],
        )
        .unwrap();
        let cohort_anatomy = ReachedCohortAnatomy::new(
            fixtures
                .iter()
                .map(|fixture| fixture.anatomy.clone())
                .collect(),
            fixture_lineages(fixtures.len()),
            fixture_source_sites(fixtures.len()),
            electrical_anatomy.clone(),
        )
        .unwrap();
        let genesis = ReachedCohortState::new(
            &cohort_anatomy,
            fixtures
                .iter()
                .map(|fixture| fixture.state.clone())
                .collect(),
            SparseElectricalState::genesis(&electrical_anatomy),
        )
        .unwrap();
        let controls = [
            four_neuron_interval_with_work(&shared, &fixtures, 0, [0, 0, 0, 0]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [0, 0, 0, 0]),
        ];
        let pre_learning =
            settle_reached_cohort_to_quiescence(&cohort_anatomy, &genesis, &controls).unwrap();

        let mut learning = vec![
            four_neuron_interval_with_work(&shared, &fixtures, 1, [-100, 100, 100, 100]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [100, 100, 100, 100]),
            four_neuron_interval_with_work(&shared, &fixtures, 1, [100, -100, 100, 100]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [100, 100, 100, 100]),
            four_neuron_interval_with_work(&shared, &fixtures, 1, [100, 100, -100, 100]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [100, 100, 100, 100]),
            four_neuron_interval_with_work(&shared, &fixtures, 1, [100, 100, 100, -100]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [100, 100, 100, 100]),
        ];
        for _ in 0..64 {
            learning.push(four_neuron_interval_with_work(
                &shared,
                &fixtures,
                0,
                [0, 0, 0, 0],
            ));
        }
        let original = settle_reached_cohort_experience_to_quiescence(
            &cohort_anatomy,
            &pre_learning,
            &learning,
        )
        .unwrap();
        assert!(original.neuron_fractals.iter().all(Option::is_some));
        assert!(original
            .active_electrical_contacts
            .iter()
            .all(|active| *active));

        let recurrence_inputs = [
            four_neuron_interval_with_work(&shared, &fixtures, 1, [-100, 0, 0, 0]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [100, 0, 0, 0]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [0, 0, 0, 0]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [0, 0, 0, 0]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [0, 0, 0, 0]),
            four_neuron_interval_with_work(&shared, &fixtures, 0, [0, 0, 0, 0]),
        ];
        let learned_predecessor = original.rest.clone().unwrap();
        let recurrence = settle_reached_cohort_recurrence(
            &cohort_anatomy,
            learned_predecessor.state(),
            &recurrence_inputs,
        )
        .unwrap();
        let control = settle_reached_cohort_recurrence(
            &cohort_anatomy,
            pre_learning.state(),
            &recurrence_inputs,
        )
        .unwrap();

        let encoded =
            encode_reached_cohort_state(&cohort_anatomy, learned_predecessor.state()).unwrap();
        let restored = decode_reached_cohort_state(&cohort_anatomy, &encoded).unwrap();
        let restored_recurrence =
            settle_reached_cohort_recurrence(&cohort_anatomy, &restored, &recurrence_inputs)
                .unwrap();
        assert_ne!(recurrence.successor, control.successor);
        assert_eq!(recurrence, restored_recurrence);
        let mosaic = admit_physical_mosaic(&cohort_anatomy, &original, &recurrence).unwrap();
        let mut expected_lineages = cohort_anatomy.neuron_lineages().to_vec();
        expected_lineages.sort_unstable();
        assert_eq!(mosaic.member_lineages(), expected_lineages);
        assert_eq!(mosaic.retained_fractals().len(), 4);
        assert!(mosaic.retained_fractals().iter().all(|fractal| {
            fractal.exact_delta(PhysicalStateCoordinate::PlasticRestLength)
                == Some(ExactPhysicalStateDelta::Rational(r(1, 3)))
        }));
        assert_eq!(mosaic.partial_cue_lineages(), &expected_lineages[..1]);
        assert_eq!(mosaic.original_bonds().len(), 3);
        assert_eq!(mosaic.recurrence_bonds().len(), 3);
        assert!(
            mosaic.resident_bytes().unwrap()
                < learned_predecessor.state().resident_bytes().unwrap()
        );
    }

    fn wide_cohort(
        neuron_count: usize,
    ) -> (Vec<Fixture>, ReachedCohortAnatomy, ReachedCohortState) {
        let fixtures = (0..neuron_count)
            .map(|index| physical_fixture_at(index as u32))
            .collect::<Vec<_>>();
        let electrical_anatomy = SparseElectricalAnatomy::new(neuron_count, Vec::new()).unwrap();
        let electrical_state = SparseElectricalState::genesis(&electrical_anatomy);
        let anatomy = ReachedCohortAnatomy::new(
            fixtures
                .iter()
                .map(|fixture| fixture.anatomy.clone())
                .collect(),
            fixture_lineages(neuron_count),
            fixture_source_sites(neuron_count),
            electrical_anatomy,
        )
        .unwrap();
        let state = ReachedCohortState::new(
            &anatomy,
            fixtures
                .iter()
                .map(|fixture| fixture.state.clone())
                .collect(),
            electrical_state,
        )
        .unwrap();
        (fixtures, anatomy, state)
    }

    fn read_test_u64(encoded: &[u8], cursor: &mut usize) -> usize {
        let value = u64::from_le_bytes(encoded[*cursor..*cursor + 8].try_into().unwrap());
        *cursor += 8;
        usize::try_from(value).unwrap()
    }

    /// Structural walk of one `GLRCC05` cell: distinct anatomy-blob count,
    /// distinct state-blob count, and the byte offset of the derived
    /// recovery-fluid anatomy digest.
    fn v5_cell_shape(encoded: &[u8]) -> (usize, usize, usize) {
        assert_eq!(&encoded[..8], b"GLRCC05\0");
        let mut cursor = 8;
        let neuron_count = read_test_u64(encoded, &mut cursor);
        let anatomy_table_count = read_test_u64(encoded, &mut cursor);
        for _ in 0..anatomy_table_count {
            let length = read_test_u64(encoded, &mut cursor);
            cursor += length;
        }
        let state_table_count = read_test_u64(encoded, &mut cursor);
        for _ in 0..state_table_count {
            let length = read_test_u64(encoded, &mut cursor);
            cursor += length;
        }
        for _ in 0..neuron_count {
            cursor += 16;
            let source_length = read_test_u64(encoded, &mut cursor);
            // source + anatomy reference + state reference + this member's own
            // geometry-derived capacitance (exact rational, 16 + 16 bytes).
            cursor += source_length + 32 + 32 + 32;
        }
        (anatomy_table_count, state_table_count, cursor)
    }

    #[test]
    fn content_addressed_cell_dedupes_and_a_single_mutation_adds_exactly_one_blob() {
        let (_, anatomy, state) = wide_cohort(29);
        let inline_cell = encode_reached_cohort_cell(&anatomy, &state).unwrap();
        let deduplicated_cell = encode_reached_cohort_cell_v5(&anatomy, &state).unwrap();
        let (anatomy_blobs, state_blobs, _) = v5_cell_shape(&deduplicated_cell);
        assert_eq!(anatomy_blobs, 1);
        assert_eq!(state_blobs, 1);
        assert!(deduplicated_cell.len() * 10 < inline_cell.len());
        let (restored_anatomy, restored_state) =
            decode_reached_cohort_cell(&deduplicated_cell).unwrap();
        assert_eq!(restored_anatomy, anatomy);
        assert_eq!(restored_state, state);
        assert_eq!(
            encode_reached_cohort_cell_v5(&restored_anatomy, &restored_state).unwrap(),
            deduplicated_cell
        );

        let mut mutated_neurons = state.neurons().to_vec();
        mutated_neurons[5].carriers = CarrierReservoirs::new(999_999, 1_000_001);
        let mutated_state =
            ReachedCohortState::new(&anatomy, mutated_neurons, state.electrical().clone()).unwrap();
        let mutated_cell = encode_reached_cohort_cell_v5(&anatomy, &mutated_state).unwrap();
        let (anatomy_blobs, state_blobs, _) = v5_cell_shape(&mutated_cell);
        assert_eq!(anatomy_blobs, 1);
        assert_eq!(state_blobs, 2);
        let (_, remutated) = decode_reached_cohort_cell(&mutated_cell).unwrap();
        assert_eq!(remutated, mutated_state);

        eprintln!(
            "MEASURE cohort-cell 29 neurons: inline GLRCC03 = {} B, content-addressed GLRCC05 = {} B",
            inline_cell.len(),
            deduplicated_cell.len()
        );
        let inline_state = encode_reached_cohort_state(&anatomy, &state).unwrap();
        let deduplicated_state = encode_reached_cohort_state_v4(&anatomy, &state).unwrap();
        eprintln!(
            "MEASURE cohort-state 29 neurons: inline GLRCS03 = {} B, content-addressed GLRCS04 = {} B",
            inline_state.len(),
            deduplicated_state.len()
        );
    }

    /// The standard 29-neuron post-lesson body at live blob scale: 27
    /// 458-ring card neurons plus two small neurons, with retained experience
    /// evidence whose POST snapshot equals the current state and whose PRE
    /// snapshot differs in four members.
    ///
    /// Since the 2026-08-05 geometric-differentiation ratification the 27 card
    /// neurons are no longer byte-identical: each carries the capacitance its
    /// own declared place derives, so the content-addressed cell codec now
    /// sees 29 distinct anatomy blobs where it used to see 3.  Everything else
    /// about a card neuron — its whole 458-ring Psi lattice, gate, recovery,
    /// DNA and plastic anatomy — is still shared, and the codec's shared
    /// anatomy section stores that once (`encode_reached_cohort_cell_v5`),
    /// carrying only the per-site derived parameters per member.
    #[test]
    fn standard_twenty_nine_neuron_post_lesson_body_measurement() {
        let card_neurons = (0..27_u32)
            .map(|topology_index| scaled_physical_fixture_at(229, 1, topology_index))
            .collect::<Vec<_>>();
        let small_a = scaled_physical_fixture_at(8, 1, 27);
        let small_b = scaled_physical_fixture_at(8, 1, 28);
        let mut small_b_state = small_b.state.clone();
        small_b_state.carriers = CarrierReservoirs::new(999_999, 1_000_001);
        let mut anatomies = card_neurons
            .iter()
            .map(|card| card.anatomy.clone())
            .collect::<Vec<_>>();
        anatomies.push(small_a.anatomy.clone());
        anatomies.push(small_b.anatomy.clone());
        let mut states = card_neurons
            .iter()
            .map(|card| card.state.clone())
            .collect::<Vec<_>>();
        states.push(small_a.state.clone());
        states.push(small_b_state);
        let electrical_anatomy = SparseElectricalAnatomy::new(29, Vec::new()).unwrap();
        let electrical_state = SparseElectricalState::genesis(&electrical_anatomy);
        let anatomy = ReachedCohortAnatomy::new(
            anatomies,
            fixture_lineages(29),
            fixture_source_sites(29),
            electrical_anatomy,
        )
        .unwrap();
        let post = ReachedCohortState::new(&anatomy, states, electrical_state).unwrap();
        let mut pre_neurons = post.neurons().to_vec();
        for neuron in pre_neurons.iter_mut().take(4) {
            neuron.carriers = CarrierReservoirs::new(1_000_500, 999_500);
            neuron.gate.open_population = 1;
        }
        let pre =
            ReachedCohortState::new(&anatomy, pre_neurons, post.electrical().clone()).unwrap();

        let inline_cell = encode_reached_cohort_cell(&anatomy, &post).unwrap();
        let deduplicated_cell = encode_reached_cohort_cell_v5(&anatomy, &post).unwrap();
        let inline_snapshot = encode_reached_cohort_state(&anatomy, &pre).unwrap();
        let pre_delta = encode_reached_cohort_state_delta(&anatomy, &post, &pre).unwrap();
        assert_eq!(
            decode_reached_cohort_state_delta(&anatomy, &post, &pre_delta).unwrap(),
            pre
        );
        let (restored_anatomy, restored_post) =
            decode_reached_cohort_cell(&deduplicated_cell).unwrap();
        assert_eq!(restored_anatomy, anatomy);
        assert_eq!(restored_post, post);
        // The 29 members are now anatomically distinct — no two capacitances
        // are equal — and the cell still interns exactly TWO anatomy blobs:
        // the shared 458-ring card anatomy and the shared small anatomy.  The
        // differentiation costs 29 x 32 bytes of carried capacitance, not 29
        // duplicated anatomy blobs (which measured 3,485,943 B for this body
        // before the shared-portion split).
        let (anatomy_blobs, _, _) = v5_cell_shape(&deduplicated_cell);
        assert_eq!(anatomy_blobs, 2);
        let capacitances = anatomy
            .neuron_anatomies()
            .iter()
            .map(|neuron| neuron.capacitance().picofarads().parts())
            .collect::<Vec<_>>();
        for (index, capacitance) in capacitances.iter().enumerate() {
            assert!(!capacitances[..index].contains(capacitance));
        }

        // Evidence framing: magic + mode bytes + length prefixes + the two
        // bool sections (29 neurons, 0 contacts).
        let bool_sections = 8 + 29 + 8;
        let retired_evidence =
            8 + 8 + inline_snapshot.len() + 1 + 8 + inline_snapshot.len() + bool_sections;
        let current_evidence = 8 + 1 + 8 + pre_delta.len() + 1 + 32 + bool_sections;
        let header_and_checkpoint = 90 + 74;
        let retired_body = header_and_checkpoint + 8 + inline_cell.len() + 3 + 8 + retired_evidence;
        let current_body =
            header_and_checkpoint + 8 + deduplicated_cell.len() + 3 + 8 + current_evidence;
        eprintln!(
            "MEASURE standard 29-neuron post-lesson body: retired layout = {} B, \
             content-addressed layout = {} B (cell {} -> {} B, evidence {} -> {} B)",
            retired_body,
            current_body,
            inline_cell.len(),
            deduplicated_cell.len(),
            retired_evidence,
            current_evidence
        );
        assert!(current_body < 450_000);
        assert!(current_body * 10 < retired_body);
    }

    #[test]
    fn derived_recovery_fluid_digest_mismatch_is_refused() {
        let (_, anatomy, state) = wide_cohort(3);
        let mut cell = encode_reached_cohort_cell_v5(&anatomy, &state).unwrap();
        assert!(decode_reached_cohort_cell(&cell).is_ok());
        let (_, _, digest_offset) = v5_cell_shape(&cell);
        cell[digest_offset] ^= 1;
        assert!(decode_reached_cohort_cell(&cell).is_err());
    }

    #[test]
    fn sparse_delta_wire_and_apply_reconstruct_the_exact_target_state() {
        let fixture = physical_fixture();
        let base = fixture.state.clone();
        let mut target = base.clone();
        target.gate.open_population = 1;
        target.carriers = CarrierReservoirs::new(999_000, 1_001_000);
        target.plastic.rest_length_nanometres = r(3, 2);
        target.dna_expression.expressed_product_quanta = 7;
        target.dna_expression.waste_quanta = 7;
        target.recovery.psi_lanes[3] = RecoveryLaneState {
            fuel_quanta: 99_998,
            spent_quanta: 1,
            exported_heat_quanta: 1,
        };
        target.psi.rings[0].winding = BalancedTrit::Positive;
        target.psi.rings[0].phase_thirds = canonical_phase_thirds(BalancedTrit::Positive);
        target.membrane = LocalMembraneConductanceState::from_physical_parts(
            ElementaryChargeMembraneState::from_physical_parts(
                5,
                ChargeCarrierPhase::new(1, 3).unwrap(),
            ),
            [ChargeCarrierPhase::new(-1, 4).unwrap()],
        );
        let delta = sparse_physical_state_delta(&base, &target)
            .unwrap()
            .unwrap();
        let wire = encode_sparse_physical_state_delta(&delta).unwrap();
        let decoded = decode_sparse_physical_state_delta(&wire).unwrap();
        assert_eq!(decoded, delta);
        let applied = apply_sparse_physical_state_delta(&fixture.anatomy, &base, &decoded).unwrap();
        assert_eq!(applied, target);
        assert_eq!(
            sparse_physical_state_delta(&base, &applied)
                .unwrap()
                .unwrap(),
            delta
        );
        let retained = sparse_retained_physical_state_delta(&base, &target)
            .unwrap()
            .unwrap();
        assert_eq!(
            retained
                .entries()
                .iter()
                .map(|entry| entry.coordinate())
                .collect::<Vec<_>>(),
            vec![
                PhysicalStateCoordinate::PsiWinding(0),
                PhysicalStateCoordinate::GateOpenPopulation,
                PhysicalStateCoordinate::PlasticRestLength,
                PhysicalStateCoordinate::DnaExpressedProduct,
            ]
        );
        let mut transient_only = base.clone();
        transient_only.carriers = CarrierReservoirs::new(999_999, 1_000_001);
        transient_only.dna_expression.waste_quanta = 1;
        transient_only.membrane_return_work_residue = r(1, 144);
        assert!(sparse_physical_state_delta(&base, &transient_only)
            .unwrap()
            .is_some());
        assert!(sparse_retained_physical_state_delta(&base, &transient_only)
            .unwrap()
            .is_none());
        assert!(decode_sparse_physical_state_delta(&wire[..wire.len() - 1]).is_err());
        let mut unordered = wire.clone();
        unordered[0] = 2;
        assert!(decode_sparse_physical_state_delta(&unordered).is_err());
        assert!(decode_sparse_physical_state_delta(&u64::MAX.to_le_bytes()).is_err());
    }

    #[test]
    fn cohort_state_delta_reconstructs_exactly_and_refuses_digest_divergence() {
        let (_, anatomy, base) = wide_cohort(4);
        let mut target_neurons = base.neurons().to_vec();
        target_neurons[2].carriers = CarrierReservoirs::new(999_999, 1_000_001);
        target_neurons[2].dna_expression.waste_quanta = 3;
        let target =
            ReachedCohortState::new(&anatomy, target_neurons, base.electrical().clone()).unwrap();
        let encoded = encode_reached_cohort_state_delta(&anatomy, &base, &target).unwrap();
        let reconstructed = decode_reached_cohort_state_delta(&anatomy, &base, &encoded).unwrap();
        assert_eq!(reconstructed, target);
        assert!(
            encoded.len() * 20
                < encode_reached_cohort_state_v4(&anatomy, &target)
                    .unwrap()
                    .len()
        );
        eprintln!(
            "MEASURE cohort-state delta 4 neurons/1 changed: {} B (full GLRCS04 = {} B)",
            encoded.len(),
            encode_reached_cohort_state_v4(&anatomy, &target)
                .unwrap()
                .len()
        );

        let mut lying_digest = encoded.clone();
        let last = lying_digest.len() - 1;
        lying_digest[last] ^= 1;
        assert!(decode_reached_cohort_state_delta(&anatomy, &base, &lying_digest).is_err());
        assert!(decode_reached_cohort_state_delta(&anatomy, &target, &encoded).is_err());
    }
}
