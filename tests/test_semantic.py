import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from moose_benchmark.contracts import EvaluationContext, ModelIdentity, UsageRecord
from moose_benchmark.evaluators import get_evaluator
from moose_benchmark.llm import LLMClient, load_llm_config
from moose_benchmark.loader import (
    case_bundle_paths,
    load_case,
    load_evaluation,
    load_manifest,
)
from moose_benchmark.runner import build_submission_record

from .fakes import ScriptedLLMClient

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark/manifest.yaml"
FIXTURES = ROOT / "tests/fixtures/semantic_invariance"


def _evaluate_response(
    response_text,
    llm_client,
    *,
    memory_mib=0,
    case_id="F2-THERMAL-REFLECTOR-001",
):
    case_path, evaluation_path = case_bundle_paths(
        MANIFEST,
        case_id,
        include_disabled=case_id.startswith("V1-"),
    )
    case = load_case(case_path)
    evaluation = load_evaluation(evaluation_path)
    manifest = load_manifest(MANIFEST)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "response.md").write_text(response_text, encoding="utf-8")
        timestamp = datetime(2026, 9, 24, tzinfo=UTC)
        submission = build_submission_record(
            case,
            root,
            model=ModelIdentity(provider="fixture", model="invariance"),
            started_at=timestamp,
            finished_at=timestamp,
            usage=UsageRecord(
                wall_time_seconds=0,
                cpu_seconds=0,
                memory_mib=memory_mib,
                validation_attempts=0,
                execution_attempts=0,
            ),
        )
        context = EvaluationContext(
            benchmark_id=manifest.benchmark_id,
            benchmark_version=manifest.benchmark_version,
            submission_sha256=submission.submission_sha256,
            run_record_sha256="4" * 64,
            submission_root=root,
            public_case_root=case_path.parent,
            private_case_root=evaluation_path.parent,
        )
        return get_evaluator(evaluation.evaluator).evaluate(
            case,
            evaluation,
            submission,
            [],
            context,
            llm_client=llm_client,
        )


def _full_f2_ratings():
    return {
        "conduction_volume": "full",
        "prescribed_flux_boundary": "full",
        "convection_boundary": "full",
        "essential_and_insulated_boundaries": "full",
        "complete_residual": "full",
    }


def test_partial_credit_uses_discrete_half_score():
    ratings = _full_f2_ratings()
    ratings["convection_boundary"] = "partial"
    result = _evaluate_response(
        (FIXTURES / "standard.md").read_text(encoding="utf-8"),
        ScriptedLLMClient(ratings),
    )
    self_expected = 87.5
    assert result.raw_score == self_expected
    assert result.case_passed


def test_judge_must_return_exact_criterion_ids():
    ratings = _full_f2_ratings()
    ratings.pop("complete_residual")
    with pytest.raises(ValueError, match="criterion IDs"):
        _evaluate_response(
            (FIXTURES / "standard.md").read_text(encoding="utf-8"),
            ScriptedLLMClient(ratings),
        )

    ratings = _full_f2_ratings()
    ratings["unexpected"] = "full"
    with pytest.raises(ValueError, match="criterion IDs"):
        _evaluate_response(
            (FIXTURES / "standard.md").read_text(encoding="utf-8"),
            ScriptedLLMClient(ratings),
        )


def test_equivalent_response_formats_receive_the_same_scripted_score():
    scores = []
    for path in sorted(FIXTURES.glob("*.md")):
        result = _evaluate_response(
            path.read_text(encoding="utf-8"),
            ScriptedLLMClient(_full_f2_ratings()),
        )
        scores.append(result.raw_score)
    assert scores
    assert set(scores) == {100.0}


def test_measured_memory_budget_is_a_hard_gate():
    result = _evaluate_response(
        (FIXTURES / "standard.md").read_text(encoding="utf-8"),
        ScriptedLLMClient(_full_f2_ratings()),
        memory_mib=1025,
    )
    assert result.raw_score == 100.0
    assert result.official_score == 0.0
    assert not result.gates_passed


@pytest.mark.llm
def test_live_judge_is_invariant_across_equivalent_responses():
    config_path = os.environ.get("MOOSE_BENCHMARK_LLM_CONFIG")
    if not config_path:
        pytest.skip("set MOOSE_BENCHMARK_LLM_CONFIG to run live semantic calibration")
    client = LLMClient(load_llm_config(config_path))
    results = [
        _evaluate_response(path.read_text(encoding="utf-8"), client)
        for path in sorted(FIXTURES.glob("*.md"))
    ]
    scores = [result.raw_score for result in results]
    assert all(result.case_passed for result in results)
    assert max(scores) - min(scores) <= 1.0


@pytest.mark.llm
def test_live_mms_derivation_judge_accepts_gold_and_rejects_sign_mutant():
    config_path = os.environ.get("MOOSE_BENCHMARK_LLM_CONFIG")
    if not config_path:
        pytest.skip("set MOOSE_BENCHMARK_LLM_CONFIG to run live semantic calibration")
    client = LLMClient(load_llm_config(config_path))
    case_id = "V1-DIFFUSION-STEADY-DIRICHLET-MMS-001"
    fixture_root = ROOT / "benchmark/example-submissions"
    gold = _evaluate_response(
        (fixture_root / case_id / "response.md").read_text(encoding="utf-8"),
        client,
        case_id=case_id,
    )
    mutant = _evaluate_response(
        (fixture_root / f"{case_id}-mutant-001/response.md").read_text(encoding="utf-8"),
        client,
        case_id=case_id,
    )
    assert gold.case_passed
    assert not mutant.case_passed
