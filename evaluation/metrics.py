"""Binary classification metrics and an offline worst-case helper.

``worst_case_label`` exists only for paper-style offline comparison. It is not
imported by the decision module and never influences the final label, which is
always taken from the Step 7 LLM response.
"""

from __future__ import annotations

from lvdetector.domain.enums import SinkVerdict


def _as_binary(value) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        text = str(value).strip().lower()
        return 1 if text in {"true", "yes", "vulnerable", "latent", "manifest"} else 0


def binary_metrics(y_true, y_pred) -> dict:
    """Return accuracy, precision, recall, and F1 for binary labels."""
    truth = [_as_binary(value) for value in y_true]
    predicted = [_as_binary(value) for value in y_pred]

    tp = sum(1 for t, p in zip(truth, predicted) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(truth, predicted) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(truth, predicted) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(truth, predicted) if t == 1 and p == 0)

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def worst_case_label(verdicts) -> str:
    """Aggregate per-sink verdicts using worst-case ordering.

    This is an analysis utility only; it is intentionally disconnected from
    the production decision path.
    """
    saw_latent = False
    saw_safe = False
    for verdict in verdicts:
        text = verdict.value if isinstance(verdict, SinkVerdict) else str(verdict).lower()
        if "manifest" in text:
            return "manifest"
        if "latent" in text:
            saw_latent = True
        elif "safe" in text:
            saw_safe = True

    if saw_latent:
        return "latent"
    if saw_safe:
        return "safe"
    return "unresolved"
