"""
Spatial Evidence-Sufficiency Reference Engine
Motor de referencia para suficiencia de evidencia espacial

Autor
Carlos Busón Buesa

Afiliación
Universidade Federal de Mato Grosso do Sul (UFMS), Brasil

ORCID
0000-0002-1446-2252

Correo
carlos.buson@ufms.br

Versión
1.0

Artículo asociado
"From incomplete spatial evidence to bounded inference:
an integrative evidence-sufficiency methodology developed across
four scientific applications"

QUÉ HACE ESTE PROGRAMA

Este módulo implementa el motor lógico genérico descrito en el artículo.
Su objetivo es evaluar si la evidencia disponible para una unidad espacial
permite o no sostener una inferencia científica previamente definida.

El motor NO:
- predice depósitos minerales;
- calcula potencial acuífero;
- interpola valores;
- asigna evidencias a geometrías;
- sustituye la interpretación experta;
- convierte ausencia de datos en cero.

El motor SÍ:
1. recibe evidencias ya asignadas a una unidad espacial;
2. conserva estados epistémicos explícitos:
   SUPPORTED, VERIFIED_NEGATIVE, UNKNOWN, CONFLICT,
   NOT_APPLICABLE e INVALID;
3. evalúa requisitos mediante operadores ANY, ALL y COUNT_AT_LEAST;
4. distingue requisitos críticos de requisitos no críticos;
5. impide que evidencia favorable no relacionada compense el fallo
   de un requisito crítico;
6. devuelve un estado de inferencia limitado:
   SUPPORTABLE, REJECTED_BY_EVIDENCE, NON_EVALUABLE
   o NOT_APPLICABLE;
7. conserva los bottlenecks, es decir, los requisitos exactos que
   bloquean o impiden la inferencia;
8. devuelve también el claim boundary, que explicita qué NO significa
   el resultado obtenido.

PRINCIPIO CENTRAL

    evidencia + contrato científico
        -> evaluación de requisitos
        -> estado de inferencia acotado
        -> bottlenecks
        -> límite explícito de la afirmación

El contrato científico debe declararse antes de ejecutar la evaluación.
El programa hace reproducibles esas reglas, pero no decide por sí solo
qué requisitos son científicamente adecuados.

Licencia
Pendiente de definir para la publicación pública definitiva.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence


class EvidenceState(str, Enum):
    SUPPORTED = "SUPPORTED"
    VERIFIED_NEGATIVE = "VERIFIED_NEGATIVE"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INVALID = "INVALID"


class RequirementState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INVALID = "INVALID"


class TargetState(str, Enum):
    SUPPORTABLE = "SUPPORTABLE"
    REJECTED_BY_EVIDENCE = "REJECTED_BY_EVIDENCE"
    NON_EVALUABLE = "NON_EVALUABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Operator(str, Enum):
    ANY = "ANY"
    ALL = "ALL"
    COUNT_AT_LEAST = "COUNT_AT_LEAST"


@dataclass(frozen=True)
class EvidenceRecord:
    unit_id: str
    evidence_type: str
    state: EvidenceState
    source_id: str
    value: object | None = None


@dataclass(frozen=True)
class RequirementSpec:
    requirement_id: str
    evidence_keys: tuple[str, ...]
    operator: Operator
    accepted_states: frozenset[EvidenceState]
    critical: bool = True
    count_at_least: int | None = None
    action_if_unresolved: str | None = None


@dataclass(frozen=True)
class TargetSpec:
    target_id: str
    requirements: tuple[RequirementSpec, ...]
    claim_boundary: str


@dataclass(frozen=True)
class EvaluationResult:
    unit_id: str
    target_id: str
    target_state: TargetState
    requirement_states: Mapping[str, RequirementState]
    bottlenecks: tuple[str, ...]
    claim_boundary: str


_UNRESOLVED_PRECEDENCE = (
    EvidenceState.CONFLICT,
    EvidenceState.INVALID,
    EvidenceState.UNKNOWN,
)


def _collapse_unresolved(states: Sequence[EvidenceState]) -> RequirementState:
    """Return a deterministic reporting state for unresolved evidence.

    This is a reporting precedence, not a truth ordering:
    CONFLICT > INVALID > UNKNOWN.
    """
    if EvidenceState.CONFLICT in states:
        return RequirementState.CONFLICT
    if EvidenceState.INVALID in states:
        return RequirementState.INVALID
    return RequirementState.UNKNOWN


def evaluate_requirement(
    evidence_by_type: Mapping[str, Sequence[EvidenceRecord]],
    spec: RequirementSpec,
) -> RequirementState:
    """Evaluate one requirement using explicit multi-state semantics.

    Missing evidence keys are represented as UNKNOWN rather than as zero/false.
    NOT_APPLICABLE records are excluded from applicable evidence; if all required
    evidence is NOT_APPLICABLE, the requirement is NOT_APPLICABLE.
    """
    states: list[EvidenceState] = []
    for key in spec.evidence_keys:
        records = list(evidence_by_type.get(key, ()))
        if not records:
            states.append(EvidenceState.UNKNOWN)
        else:
            states.extend(r.state for r in records)

    if not states:
        return RequirementState.UNKNOWN

    accepted = [s for s in states if s in spec.accepted_states]
    negative = [s for s in states if s == EvidenceState.VERIFIED_NEGATIVE]
    unresolved = [s for s in states if s in _UNRESOLVED_PRECEDENCE]
    applicable = [s for s in states if s != EvidenceState.NOT_APPLICABLE]

    if not applicable:
        return RequirementState.NOT_APPLICABLE

    if spec.operator == Operator.ANY:
        if accepted:
            return RequirementState.PASS
        # If unresolved evidence could still satisfy the ANY requirement,
        # the requirement remains unresolved rather than being rejected.
        if unresolved:
            return _collapse_unresolved(unresolved)
        if negative:
            return RequirementState.FAIL
        return RequirementState.UNKNOWN

    if spec.operator == Operator.ALL:
        # A verified negative is sufficient to fail an ALL requirement.
        if negative:
            return RequirementState.FAIL
        if unresolved:
            return _collapse_unresolved(unresolved)
        # NOT_APPLICABLE items are ignored when at least one applicable item exists.
        if all(s in spec.accepted_states for s in applicable):
            return RequirementState.PASS
        return RequirementState.UNKNOWN

    if spec.operator == Operator.COUNT_AT_LEAST:
        k = spec.count_at_least
        if k is None or k < 1:
            raise ValueError("COUNT_AT_LEAST requires count_at_least >= 1")
        pass_count = len(accepted)
        if pass_count >= k:
            return RequirementState.PASS

        unresolved_count = len(unresolved)
        # If even every unresolved item became accepted, the threshold cannot be met.
        if pass_count + unresolved_count < k:
            return RequirementState.FAIL

        if unresolved:
            return _collapse_unresolved(unresolved)
        return RequirementState.FAIL

    raise ValueError(f"Unsupported operator: {spec.operator}")


def evaluate_target(
    unit_id: str,
    evidence: Iterable[EvidenceRecord],
    target: TargetSpec,
) -> EvaluationResult:
    evidence_by_type: dict[str, list[EvidenceRecord]] = {}
    for record in evidence:
        if record.unit_id != unit_id:
            continue
        evidence_by_type.setdefault(record.evidence_type, []).append(record)

    req_states: dict[str, RequirementState] = {}
    for req in target.requirements:
        req_states[req.requirement_id] = evaluate_requirement(evidence_by_type, req)

    critical_specs = [r for r in target.requirements if r.critical]
    critical_states = [req_states[r.requirement_id] for r in critical_specs]

    if not critical_specs:
        state = TargetState.SUPPORTABLE
        bottlenecks: tuple[str, ...] = ()
    elif RequirementState.FAIL in critical_states:
        state = TargetState.REJECTED_BY_EVIDENCE
        bottlenecks = tuple(
            r.requirement_id
            for r in critical_specs
            if req_states[r.requirement_id] == RequirementState.FAIL
        )
    elif any(
        s in {RequirementState.UNKNOWN, RequirementState.CONFLICT, RequirementState.INVALID}
        for s in critical_states
    ):
        state = TargetState.NON_EVALUABLE
        bottlenecks = tuple(
            r.requirement_id
            for r in critical_specs
            if req_states[r.requirement_id]
            in {RequirementState.UNKNOWN, RequirementState.CONFLICT, RequirementState.INVALID}
        )
    elif critical_states and all(s == RequirementState.NOT_APPLICABLE for s in critical_states):
        state = TargetState.NOT_APPLICABLE
        bottlenecks = tuple(r.requirement_id for r in critical_specs)
    else:
        # At least one critical requirement is applicable and every applicable
        # critical requirement passed.
        applicable_states = [s for s in critical_states if s != RequirementState.NOT_APPLICABLE]
        if applicable_states and all(s == RequirementState.PASS for s in applicable_states):
            state = TargetState.SUPPORTABLE
            bottlenecks = ()
        else:
            state = TargetState.NON_EVALUABLE
            bottlenecks = tuple(
                r.requirement_id
                for r in critical_specs
                if req_states[r.requirement_id] != RequirementState.PASS
            )

    return EvaluationResult(
        unit_id=unit_id,
        target_id=target.target_id,
        target_state=state,
        requirement_states=req_states,
        bottlenecks=bottlenecks,
        claim_boundary=target.claim_boundary,
    )
