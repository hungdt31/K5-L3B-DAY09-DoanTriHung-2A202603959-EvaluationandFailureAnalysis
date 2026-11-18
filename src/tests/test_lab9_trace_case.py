"""M1 regression test from trace_case analysis (C-002@11 FM-03 ticket_trust)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.student


def test_c002_seed11_ticket_trust_regression():
    from pydantic_evals.evaluators import EvaluatorContext
    from lab9 import graders, trace_case

    bad = trace_case.investigate("seeded_regression", "C-002", 11)
    good = trace_case.investigate("fixed", "C-002", 11)

    bad_ctx = EvaluatorContext(
        name="C-002@11-bad", inputs={"claim_id": "C-002", "seed": 11},
        metadata=None, expected_output=bad["label"], output=bad["trial"],
        duration=0.0, _span_tree=None, attributes={}, metrics={},
    )
    good_ctx = EvaluatorContext(
        name="C-002@11-good", inputs={"claim_id": "C-002", "seed": 11},
        metadata=None, expected_output=good["label"], output=good["trial"],
        duration=0.0, _span_tree=None, attributes={}, metrics={},
    )

    # First wrong step on seeded_regression is step 3 (index 2): model_override({"delay_days": 5})
    assert bad["trial"]["events"][2]["kind"] == "model_override"
    assert bad["trial"]["events"][2]["payload"] == {"delay_days": 5}
    assert graders.DbFactKept().evaluate(bad_ctx).value is False
    assert bad["trial"]["snapshot"]["refund_vnd"] == 20000
    assert bad["trial"]["lab8_pass"] is False

    # Counterpart on fixed: no model_override, quote=0, ledger=0, TrialPass=True
    assert all(e["kind"] != "model_override" for e in good["trial"]["events"])
    assert graders.DbFactKept().evaluate(good_ctx).value is True
    assert good["trial"]["snapshot"]["refund_vnd"] == 0
    assert good["trial"]["lab8_pass"] is True
