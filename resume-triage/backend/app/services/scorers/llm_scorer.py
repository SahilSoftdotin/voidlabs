"""LLM-assisted scorer (Claude) — the production scoring path.

Uses semantic skill matching and per-criterion scoring with a REQUIRED
justification string per criterion, so output stays explainable and auditable
(§4). It is handed only the bias-safe ``CandidateScoringView``; the prompts
explicitly forbid use of protected attributes (§2 principle 3).

If any call fails, ``build_scorer`` falls back to the deterministic mock so
ingestion never hard-fails.
"""
from __future__ import annotations

from app.domain.schemas import (
    CandidateScoringView,
    CriterionScore,
    InterviewQuestion,
    KnockoutResult,
    Rubric,
)
from app.llm.client import LLMClient

_COMPLIANCE = (
    "You are assisting lawful, EEOC-defensible candidate triage. You MUST NOT "
    "use or infer any protected attribute: name, gender, age/date of birth, "
    "photo, marital status, nationality, or the prestige of any institution. "
    "Do NOT penalize employment gaps. Judge only professional, role-relevant "
    "content. Every score must include a short, factual justification."
)


def _view_json(view: CandidateScoringView) -> str:
    return view.model_dump_json(indent=2)


class LLMScorer:
    engine_name = "llm-claude-1.0"

    def __init__(self) -> None:
        self.client = LLMClient()
        self.engine_name = f"llm-{self.client.model}-1.0"

    # -- Stage 1: knockouts -------------------------------------------------
    def evaluate_knockouts(
        self, view: CandidateScoringView, rubric: Rubric
    ) -> list[KnockoutResult]:
        if not rubric.knockouts:
            return []
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "knockout_id": {"type": "string"},
                            "passed": {"type": "boolean"},
                            "justification": {"type": "string"},
                        },
                        "required": ["knockout_id", "passed", "justification"],
                    },
                }
            },
            "required": ["results"],
        }
        kos = [
            {"id": k.id, "name": k.name, "type": k.type.value,
             "description": k.description, "config": k.config}
            for k in rubric.knockouts
        ]
        user = (
            "Evaluate each pass/fail knockout filter against the candidate.\n"
            "A knockout that cannot be determined from the resume should PASS "
            "(assume eligible) with a justification noting it must be verified.\n\n"
            f"KNOCKOUTS:\n{kos}\n\nCANDIDATE (bias-safe view):\n{_view_json(view)}"
        )
        data = self.client.structured(system=_COMPLIANCE, user=user, schema=schema)
        by_id = {k.id: k for k in rubric.knockouts}
        out: list[KnockoutResult] = []
        for r in data.get("results", []):
            ko = by_id.get(r["knockout_id"])
            if ko:
                out.append(KnockoutResult(
                    knockout_id=ko.id, knockout_name=ko.name,
                    passed=bool(r["passed"]), justification=r["justification"],
                ))
        # Ensure every knockout has a result.
        seen = {r.knockout_id for r in out}
        for ko in rubric.knockouts:
            if ko.id not in seen:
                out.append(KnockoutResult(
                    knockout_id=ko.id, knockout_name=ko.name, passed=True,
                    justification="No determination returned; defaulted to pass for human review.",
                ))
        return out

    # -- Stage 2: weighted scoring -----------------------------------------
    def score_criteria(
        self, view: CandidateScoringView, rubric: Rubric, job_context: str
    ) -> list[CriterionScore]:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "criterion_id": {"type": "string"},
                            "raw_score": {"type": "number"},
                            "justification": {"type": "string"},
                        },
                        "required": ["criterion_id", "raw_score", "justification"],
                    },
                }
            },
            "required": ["scores"],
        }
        crits = [
            {"id": c.id, "name": c.name, "guidance": c.scoring_guidance}
            for c in rubric.weighted_criteria
        ]
        user = (
            "Score the candidate against this specific job — never in the "
            "abstract. Each criterion is scored 0-5 using semantic matching "
            "(map synonyms/related concepts, not just exact keywords). Return a "
            "short factual justification for each.\n\n"
            f"JOB:\n{job_context}\n\nCRITERIA:\n{crits}\n\n"
            f"CANDIDATE (bias-safe view):\n{_view_json(view)}"
        )
        data = self.client.structured(system=_COMPLIANCE, user=user, schema=schema)
        by_id = {c.id: c for c in rubric.weighted_criteria}
        results: dict[str, CriterionScore] = {}
        for s in data.get("scores", []):
            crit = by_id.get(s["criterion_id"])
            if not crit:
                continue
            raw = max(0.0, min(5.0, float(s["raw_score"])))
            results[crit.id] = CriterionScore(
                criterion_id=crit.id,
                criterion_name=crit.name,
                raw_score=round(raw, 2),
                weight=crit.weight,
                weighted_score=round(raw / 5.0 * crit.weight, 2),
                justification=s["justification"],
            )
        # Guarantee one score per criterion.
        out: list[CriterionScore] = []
        for crit in rubric.weighted_criteria:
            out.append(results.get(crit.id, CriterionScore(
                criterion_id=crit.id, criterion_name=crit.name, raw_score=0.0,
                weight=crit.weight, weighted_score=0.0,
                justification="No score returned by model; defaulted to 0 for human review.",
            )))
        return out

    # -- Manager interview questions (§3.6) --------------------------------
    def generate_interview_questions(
        self, view: CandidateScoringView, job_context: str, n: int = 5
    ) -> list[InterviewQuestion]:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "question": {"type": "string"},
                            "resume_item": {"type": "string"},
                            "type": {"type": "string", "enum": ["technical", "behavioral"]},
                            "signal": {"type": "string"},
                        },
                        "required": ["question", "resume_item", "type", "signal"],
                    },
                }
            },
            "required": ["questions"],
        }
        user = (
            f"Generate {n} tailored interview questions for the hiring manager's "
            "round, grounded in standout items on THIS candidate's resume "
            "(quantified achievements, projects they led, notable tech/scale, a "
            "career pivot, or a risk worth understanding). Mix technical "
            "(probe depth & authenticity of claimed skills) and behavioral "
            "(STAR: ownership, decision-making, collaboration, conflict). For "
            "each: the question, the exact resume_item it probes, the type, and "
            "one line on good-vs-weak answer signals. Use only professional, "
            "role-relevant content — never protected attributes.\n\n"
            f"JOB:\n{job_context}\n\nCANDIDATE (bias-safe view):\n{_view_json(view)}"
        )
        data = self.client.structured(
            system=_COMPLIANCE, user=user, schema=schema, max_tokens=4096
        )
        out: list[InterviewQuestion] = []
        for q in data.get("questions", [])[:n]:
            out.append(InterviewQuestion(
                question=q["question"], resume_item=q["resume_item"],
                type=q["type"], signal=q["signal"],
            ))
        return out
