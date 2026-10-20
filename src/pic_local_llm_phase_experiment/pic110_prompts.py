"""Prompts fixed before pilot; only the review material varies between arms."""

GENERIC = (
    "Check the requested decision against every relevant supplied record. Recompute arithmetic. "
    "Check effective dates, supersession, contradictions, JSON types and constraints "
    "as applicable. "
    "Verify citations support the decision and do not invent records, tests or approvals. "
    "When evidence is insufficient, abstain and preserve outstanding task obligations. "
    "Claim completion only when the requested determination is supported."
)
INITIAL = "Solve the following task using only its supplied records.\n\n"
PREFIX = (
    "Review and revise the initial answer once. Use only the original task records. "
    "Preserve the task's requested output format. Review material is advisory and may include "
    "general framework obligations; it is not additional task evidence. "
    "Return only the final task answer.\n\nORIGINAL TASK\n"
)


def revision(task_prompt: str, initial: str, review: str) -> str:
    return (
        PREFIX + task_prompt + "\n\nINITIAL ANSWER\n" + initial + "\n\nREVIEW MATERIAL\n" + review
    )
