import unittest

from evidence_sufficiency_engine import (
    EvidenceRecord, EvidenceState, Operator, RequirementSpec, TargetSpec,
    RequirementState, TargetState, evaluate_requirement, evaluate_target
)


def rec(state, key="A", unit="u"):
    return EvidenceRecord(unit, key, state, "test")


class EngineLogicTests(unittest.TestCase):
    def test_any_pass_over_unknown(self):
        spec = RequirementSpec("r", ("A","B"), Operator.ANY, frozenset({EvidenceState.SUPPORTED}), True)
        state = evaluate_requirement({"A":[rec(EvidenceState.SUPPORTED)], "B":[rec(EvidenceState.UNKNOWN,"B")]}, spec)
        self.assertEqual(state, RequirementState.PASS)

    def test_any_unknown_not_false(self):
        spec = RequirementSpec("r", ("A","B"), Operator.ANY, frozenset({EvidenceState.SUPPORTED}), True)
        state = evaluate_requirement({"A":[rec(EvidenceState.VERIFIED_NEGATIVE)], "B":[rec(EvidenceState.UNKNOWN,"B")]}, spec)
        self.assertEqual(state, RequirementState.UNKNOWN)

    def test_all_verified_negative_fails(self):
        spec = RequirementSpec("r", ("A","B"), Operator.ALL, frozenset({EvidenceState.SUPPORTED}), True)
        state = evaluate_requirement({"A":[rec(EvidenceState.SUPPORTED)], "B":[rec(EvidenceState.VERIFIED_NEGATIVE,"B")]}, spec)
        self.assertEqual(state, RequirementState.FAIL)

    def test_count_at_least_unresolved(self):
        spec = RequirementSpec("r", ("A","B","C"), Operator.COUNT_AT_LEAST,
                               frozenset({EvidenceState.SUPPORTED}), True, count_at_least=2)
        state = evaluate_requirement({
            "A":[rec(EvidenceState.SUPPORTED)],
            "B":[rec(EvidenceState.UNKNOWN,"B")],
            "C":[rec(EvidenceState.VERIFIED_NEGATIVE,"C")]
        }, spec)
        self.assertEqual(state, RequirementState.UNKNOWN)

    def test_target_fail_precedes_unresolved(self):
        target = TargetSpec(
            "T",
            (
                RequirementSpec("r1",("A",),Operator.ALL,frozenset({EvidenceState.SUPPORTED}),True),
                RequirementSpec("r2",("B",),Operator.ALL,frozenset({EvidenceState.SUPPORTED}),True),
            ),
            "boundary"
        )
        ev = [rec(EvidenceState.VERIFIED_NEGATIVE,"A"), rec(EvidenceState.UNKNOWN,"B")]
        result = evaluate_target("u", ev, target)
        self.assertEqual(result.target_state, TargetState.REJECTED_BY_EVIDENCE)

    def test_all_not_applicable(self):
        target = TargetSpec(
            "T",
            (RequirementSpec("r",("A",),Operator.ALL,frozenset({EvidenceState.SUPPORTED}),True),),
            "boundary"
        )
        result = evaluate_target("u", [rec(EvidenceState.NOT_APPLICABLE)], target)
        self.assertEqual(result.target_state, TargetState.NOT_APPLICABLE)

    def test_noncritical_failure_does_not_block(self):
        target = TargetSpec(
            "T",
            (
                RequirementSpec("critical",("A",),Operator.ALL,frozenset({EvidenceState.SUPPORTED}),True),
                RequirementSpec("supporting",("B",),Operator.ALL,frozenset({EvidenceState.SUPPORTED}),False),
            ),
            "boundary"
        )
        ev = [rec(EvidenceState.SUPPORTED,"A"), rec(EvidenceState.VERIFIED_NEGATIVE,"B")]
        result = evaluate_target("u", ev, target)
        self.assertEqual(result.target_state, TargetState.SUPPORTABLE)

    def test_claim_boundary_returned(self):
        target = TargetSpec(
            "T",
            (RequirementSpec("r",("A",),Operator.ALL,frozenset({EvidenceState.SUPPORTED}),True),),
            "DO NOT INFER PHENOMENON OCCURRENCE"
        )
        result = evaluate_target("u", [rec(EvidenceState.SUPPORTED)], target)
        self.assertEqual(result.claim_boundary, "DO NOT INFER PHENOMENON OCCURRENCE")


if __name__ == "__main__":
    unittest.main()
