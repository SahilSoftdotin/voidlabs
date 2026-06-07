"""Deterministic, explainable, offline scorer.

This is the default when no LLM key is configured. It produces real,
defensible per-criterion scores from simple heuristics so the entire pipeline
(ingest -> knockout -> score -> tier -> interview questions) runs and is
testable without any network call. Every score carries a justification string,
satisfying the explainability requirement (§2 principle 5).

It reads ONLY the bias-safe ``CandidateScoringView``.
"""
from __future__ import annotations

import re

from app.domain.schemas import (
    CandidateScoringView,
    CriterionScore,
    InterviewQuestion,
    KnockoutResult,
    KnockoutType,
    Rubric,
)

_TOKEN_RE = re.compile(r"[a-z0-9+#.]+")
_METRIC_RE = re.compile(r"(\d+(\.\d+)?\s*%|\$\s?\d|\b\d{2,}\b|\bmillion\b|\bbillion\b|\bx\b)")
_STOPWORDS = {
    "and", "the", "for", "with", "you", "our", "are", "will", "have", "this",
    "that", "from", "your", "who", "all", "job", "role", "team", "work", "years",
    "experience", "ability", "strong", "must", "should", "plus", "etc",
}


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 2 and t not in _STOPWORDS}


def _searchable_text(view: CandidateScoringView) -> str:
    parts: list[str] = list(view.skills) + list(view.certifications)
    for w in view.work_history:
        parts += [w.title or "", w.organization or "", w.description or ""]
        parts += w.highlights
    for e in view.education:
        parts += [e.degree or "", e.field_of_study or ""]
    return " ".join(parts)


def _clamp5(x: float) -> float:
    return round(max(0.0, min(5.0, x)), 2)


class MockScorer:
    engine_name = "mock-heuristic-1.0"

    # -- Stage 1: knockouts -------------------------------------------------
    def evaluate_knockouts(
        self, view: CandidateScoringView, rubric: Rubric
    ) -> list[KnockoutResult]:
        text = _searchable_text(view).lower()
        results: list[KnockoutResult] = []
        for ko in rubric.knockouts:
            required = [t.lower() for t in ko.config.get("required_terms", [])]
            found = [t for t in required if t in text]
            if ko.type in (KnockoutType.WORK_AUTHORIZATION, KnockoutType.LOCATION_CONSTRAINT):
                # Rarely determinable from a resume. Default to PASS so triage
                # never auto-rejects on unknowable info; flag for the human.
                if found:
                    just = f"Evidence found in resume: {', '.join(found)}."
                else:
                    just = ("Not determinable from resume — assumed pass; "
                            "verify with candidate before relying on it.")
                results.append(KnockoutResult(
                    knockout_id=ko.id, knockout_name=ko.name, passed=True,
                    justification=just,
                ))
            else:
                passed = bool(found) if required else ko.config.get("default_pass", True)
                if required:
                    just = (f"Required term(s) present: {', '.join(found)}."
                            if found else
                            f"None of the required term(s) found: {', '.join(required)}.")
                else:
                    just = "No required terms configured; default pass."
                results.append(KnockoutResult(
                    knockout_id=ko.id, knockout_name=ko.name, passed=passed,
                    justification=just,
                ))
        return results

    # -- Stage 2: weighted scoring -----------------------------------------
    def score_criteria(
        self, view: CandidateScoringView, rubric: Rubric, job_context: str
    ) -> list[CriterionScore]:
        job_tokens = _tokens(job_context)
        cand_skill_tokens = _tokens(" ".join(view.skills + view.certifications))
        all_cand_tokens = _tokens(_searchable_text(view))

        scores: list[CriterionScore] = []
        for crit in rubric.weighted_criteria:
            raw, just = self._score_one(
                crit.id, view, job_tokens, cand_skill_tokens, all_cand_tokens
            )
            scores.append(CriterionScore(
                criterion_id=crit.id,
                criterion_name=crit.name,
                raw_score=raw,
                weight=crit.weight,
                weighted_score=round(raw / 5.0 * crit.weight, 2),
                justification=just,
            ))
        return scores

    def _score_one(self, cid, view, job_tokens, skill_tokens, all_tokens):
        if cid == "skills_match":
            overlap = job_tokens & all_tokens
            ratio = (len(overlap) / len(job_tokens)) if job_tokens else 0.3
            raw = _clamp5(0.5 + ratio * 5.5)
            sample = ", ".join(sorted(overlap)[:8]) or "no direct overlap"
            return raw, f"Semantic/keyword overlap with role: {len(overlap)} concepts ({sample})."
        if cid == "experience_depth":
            n = len(view.work_history)
            described = sum(1 for w in view.work_history if (w.description or w.highlights))
            raw = _clamp5(1.0 + n * 0.8 + described * 0.4)
            return raw, f"{n} role(s) in history, {described} with substantive detail. Gaps not penalized."
        if cid == "impact":
            metrics = 0
            for w in view.work_history:
                blob = " ".join([w.description or ""] + w.highlights)
                metrics += len(_METRIC_RE.findall(blob))
            raw = _clamp5(0.5 + metrics * 1.0)
            return raw, f"{metrics} quantified achievement signal(s) detected (metrics/scale)."
        if cid == "trajectory":
            titles = [w.title or "" for w in view.work_history if w.title]
            seniority = sum(1 for t in titles if re.search(r"senior|lead|principal|head|manager|director", t.lower()))
            raw = _clamp5(1.5 + len(set(titles)) * 0.5 + seniority * 0.8)
            return raw, f"{len(set(titles))} distinct title(s); {seniority} senior-level marker(s)."
        if cid == "education":
            edu_tokens = _tokens(" ".join((e.degree or "") + " " + (e.field_of_study or "") for e in view.education))
            overlap = job_tokens & edu_tokens
            certs = len(view.certifications)
            raw = _clamp5(1.0 + len(overlap) * 1.2 + certs * 0.8)
            return raw, (f"Field relevance: {len(overlap)} matching concept(s); {certs} certification(s). "
                         "Institution prestige intentionally ignored.")
        if cid == "clarity":
            structured = sum([
                bool(view.work_history), bool(view.skills),
                bool(view.education),
                any(w.highlights for w in view.work_history),
            ])
            raw = _clamp5(1.0 + structured * 1.0)
            return raw, f"Structure completeness across {structured}/4 expected sections/signals."
        # Unknown custom criterion: neutral, explained.
        return 2.5, "No heuristic for this custom criterion; neutral score pending human review."

    # -- Manager interview questions (§3.6) --------------------------------
    def generate_interview_questions(
        self, view: CandidateScoringView, job_context: str, n: int = 5
    ) -> list[InterviewQuestion]:
        questions: list[InterviewQuestion] = []

        # 1. Quantified achievement (technical depth / authenticity)
        quant = None
        for w in view.work_history:
            for h in w.highlights + ([w.description] if w.description else []):
                if h and _METRIC_RE.search(h):
                    quant = (h, w.title or "a previous role")
                    break
            if quant:
                break
        if quant:
            item, title = quant
            questions.append(InterviewQuestion(
                question=f"You list this result as {title}: \"{item.strip()[:160]}\". Walk me through how it was measured and what you personally owned versus the team.",
                resume_item=item.strip()[:200],
                type="technical",
                signal="Strong: concrete baseline, method, and clear individual contribution. Weak: vague, cannot reproduce the number, or only 'we' with no personal role.",
            ))

        # 2. A top skill — probe depth vs surface
        if view.skills:
            skill = view.skills[0]
            questions.append(InterviewQuestion(
                question=f"Describe the most technically demanding problem you solved using {skill}, including a tradeoff you got wrong and corrected.",
                resume_item=f"Listed skill: {skill}",
                type="technical",
                signal=f"Strong: specific, hands-on detail and learned tradeoffs in {skill}. Weak: textbook definitions or no real project.",
            ))

        # 3. Ownership / project they led (behavioral, STAR)
        led = next((w for w in view.work_history if w.title and re.search(r"lead|senior|principal|manager|head", w.title.lower())), None)
        if led is None and view.work_history:
            led = view.work_history[0]
        if led:
            questions.append(InterviewQuestion(
                question=f"Tell me about a project at {led.title or 'your most recent role'} where you drove the outcome. What was the situation, what did you decide, and what happened?",
                resume_item=f"Role: {led.title or 'most recent'} at {led.organization or 'previous employer'}",
                type="behavioral",
                signal="Strong (STAR): clear situation, decisions they personally made, measurable result. Weak: diffuse team credit, no decision ownership.",
            ))

        # 4. Career pivot / scale change (behavioral)
        if len(view.work_history) >= 2:
            a, b = view.work_history[0], view.work_history[1]
            questions.append(InterviewQuestion(
                question=f"You moved from {b.title or 'an earlier role'} to {a.title or 'your current role'}. What drove that change and what did you have to learn fastest?",
                resume_item=f"Transition: {b.title or '—'} → {a.title or '—'}",
                type="behavioral",
                signal="Strong: deliberate reasoning, self-awareness about the gap closed. Weak: no narrative or purely circumstantial.",
            ))

        # 5. Collaboration / conflict (behavioral)
        questions.append(InterviewQuestion(
            question="Tell me about a time you disagreed with a colleague or stakeholder on a technical decision. How did you handle it and what was the result?",
            resume_item="General professional conduct (collaboration & conflict)",
            type="behavioral",
            signal="Strong: respectful, data-driven resolution and a real outcome. Weak: avoidance, blame, or no concrete example.",
        ))

        return questions[:n]
