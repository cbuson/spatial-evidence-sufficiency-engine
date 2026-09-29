from __future__ import annotations
import csv
import json
from pathlib import Path

from evidence_sufficiency_engine import (
    EvidenceRecord, EvidenceState, Operator, RequirementSpec, TargetSpec,
    TargetState, evaluate_target
)

ROOT = Path(__file__).resolve().parent
FIXTURE = json.loads((ROOT / "pag_tb_fixture.json").read_text(encoding="utf-8"))

CLAIM_BOUNDARY = (
    "SUPPORTABLE indicates model openness/evaluability under the frozen PAG-ETR "
    "M2/M4 pilot contract; it does not imply mineral prospectivity, a deposit, "
    "resource, reserve, or authorization for fieldwork."
)


def decode_bitset(hex_string: str, n: int) -> list[bool]:
    raw = bytes.fromhex(hex_string)
    bits = []
    for byte in raw:
        for shift in range(7, -1, -1):
            bits.append(bool((byte >> shift) & 1))
    return bits[:n]


def target_for(keys: tuple[str, ...], operator=Operator.ANY, count_at_least=None, target_id="PAG_OPEN"):
    return TargetSpec(
        target_id=target_id,
        requirements=(
            RequirementSpec(
                requirement_id="r_open",
                evidence_keys=keys,
                operator=operator,
                accepted_states=frozenset({EvidenceState.SUPPORTED}),
                critical=True,
                count_at_least=count_at_least,
                action_if_unresolved="Acquire or review diagnostic geological evidence.",
            ),
        ),
        claim_boundary=CLAIM_BOUNDARY,
    )


BASELINE = target_for(("M2", "M4"), Operator.ANY, target_id="PAG_ANY_M2_M4")
M2_ONLY = target_for(("M2",), Operator.ANY, target_id="PAG_M2_ONLY")
M4_ONLY = target_for(("M4",), Operator.ANY, target_id="PAG_M4_ONLY")
ALL_BOTH = target_for(("M2", "M4"), Operator.ALL, target_id="PAG_ALL_M2_M4")
COUNT2 = target_for(("M2", "M4"), Operator.COUNT_AT_LEAST, 2, "PAG_COUNT2_M2_M4")


def make_evidence(unit_id: str, m2_open: bool, m4_open: bool):
    return [
        EvidenceRecord(
            unit_id=unit_id,
            evidence_type="M2",
            state=EvidenceState.SUPPORTED if m2_open else EvidenceState.UNKNOWN,
            source_id="PAG-ETR frozen M2 state",
        ),
        EvidenceRecord(
            unit_id=unit_id,
            evidence_type="M4",
            state=EvidenceState.SUPPORTED if m4_open else EvidenceState.UNKNOWN,
            source_id="PAG-ETR frozen M4 state",
        ),
    ]


summary = []
sensitivity = []
all_baseline = []

for scale, spec in FIXTURE["scales"].items():
    n = spec["total"]
    m2 = decode_bitset(spec["m2_bitset_hex"], n)
    m4 = decode_bitset(spec["m4_bitset_hex"], n)

    counts = {
        "scale_km2": int(scale),
        "cells": n,
        "native_overall_open": sum(a or b for a, b in zip(m2, m4)),
        "native_m2_open": sum(m2),
        "native_m4_open": sum(m4),
        "engine_supportable_overall": 0,
        "engine_supportable_m2": 0,
        "engine_supportable_m4": 0,
        "engine_non_evaluable_overall": 0,
        "discrepancies_overall": 0,
        "discrepancies_m2": 0,
        "discrepancies_m4": 0,
    }

    alt_counts = {
        "baseline_ANY": 0,
        "M2_only": 0,
        "M4_only": 0,
        "ALL_M2_M4": 0,
        "COUNT_AT_LEAST_2": 0,
    }

    for i, (m2_open, m4_open) in enumerate(zip(m2, m4), start=1):
        unit_id = f"{scale}_ordinal_{i:04d}"
        ev = make_evidence(unit_id, m2_open, m4_open)

        overall = evaluate_target(unit_id, ev, BASELINE)
        t2 = evaluate_target(unit_id, ev, M2_ONLY)
        t4 = evaluate_target(unit_id, ev, M4_ONLY)
        tall = evaluate_target(unit_id, ev, ALL_BOTH)
        tcount2 = evaluate_target(unit_id, ev, COUNT2)

        native_overall = m2_open or m4_open
        eng_overall = overall.target_state == TargetState.SUPPORTABLE
        eng_m2 = t2.target_state == TargetState.SUPPORTABLE
        eng_m4 = t4.target_state == TargetState.SUPPORTABLE

        counts["engine_supportable_overall"] += int(eng_overall)
        counts["engine_supportable_m2"] += int(eng_m2)
        counts["engine_supportable_m4"] += int(eng_m4)
        counts["engine_non_evaluable_overall"] += int(overall.target_state == TargetState.NON_EVALUABLE)
        counts["discrepancies_overall"] += int(eng_overall != native_overall)
        counts["discrepancies_m2"] += int(eng_m2 != m2_open)
        counts["discrepancies_m4"] += int(eng_m4 != m4_open)

        alt_counts["baseline_ANY"] += int(eng_overall)
        alt_counts["M2_only"] += int(eng_m2)
        alt_counts["M4_only"] += int(eng_m4)
        alt_counts["ALL_M2_M4"] += int(tall.target_state == TargetState.SUPPORTABLE)
        alt_counts["COUNT_AT_LEAST_2"] += int(tcount2.target_state == TargetState.SUPPORTABLE)

        all_baseline.append((scale, unit_id, native_overall, overall.target_state.value))

    exp = spec["expected"]
    assert counts["native_overall_open"] == exp["overall_open"]
    assert counts["native_m2_open"] == exp["m2_open"]
    assert counts["native_m4_open"] == exp["m4_open"]
    assert counts["discrepancies_overall"] == 0
    assert counts["discrepancies_m2"] == 0
    assert counts["discrepancies_m4"] == 0
    summary.append(counts)

    baseline = alt_counts["baseline_ANY"]
    for contract_name, supportable in alt_counts.items():
        sensitivity.append({
            "scale_km2": int(scale),
            "contract": contract_name,
            "supportable": supportable,
            "change_vs_baseline": supportable - baseline,
            "pct_of_cells": supportable / n,
        })

with (ROOT / "pag_tb_exact_engine_summary.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)

with (ROOT / "pag_td_contract_sensitivity.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=sensitivity[0].keys())
    writer.writeheader()
    writer.writerows(sensitivity)

report = {
    "engine": "evidence_sufficiency_engine.py",
    "total_cells": sum(x["cells"] for x in summary),
    "total_cell_output_comparisons": sum(x["cells"] for x in summary) * 3,
    "total_supportable_baseline": sum(x["engine_supportable_overall"] for x in summary),
    "total_non_evaluable_baseline": sum(x["engine_non_evaluable_overall"] for x in summary),
    "total_discrepancies": sum(
        x["discrepancies_overall"] + x["discrepancies_m2"] + x["discrepancies_m4"]
        for x in summary
    ),
    "summary": summary,
    "contract_sensitivity": sensitivity,
}
(ROOT / "pag_tb_td_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps(report, indent=2))
