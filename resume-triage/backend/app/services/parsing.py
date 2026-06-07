"""Resume parsing: raw file -> normalized ``Candidate``.

Two normalizers behind one entry point (selected by config):

* ``HeuristicNormalizer`` — pure-Python, offline. Extracts contact + skills +
  rough work/education sections via regex/section heuristics.
* ``LLMNormalizer`` — uses Claude to produce a clean structured Candidate.

Both are bias-aware: protected attributes are never extracted. Contact details
are captured (for the reviewer) but live in ``Candidate.contact`` and are
dropped from the scoring view.
"""
from __future__ import annotations

import io
import re
import uuid

from app.config import get_settings
from app.domain.schemas import (
    Candidate,
    CandidateSource,
    Contact,
    Education,
    WorkExperience,
)

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(\+?\d[\d\-\s().]{7,}\d)")
_URL_RE = re.compile(r"(https?://[^\s]+|(?:www\.|linkedin\.com|github\.com)[^\s]+)")


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------
def extract_text(filename: str, data: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(data)
    if lower.endswith(".docx"):
        return _extract_docx(data)
    if lower.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {filename} (use PDF, DOCX, or TXT)")


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _extract_docx(data: bytes) -> str:
    import docx

    doc = docx.Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


# ---------------------------------------------------------------------------
# Normalizers
# ---------------------------------------------------------------------------
_SECTION_HEADERS = {
    "experience": re.compile(r"^\s*(work\s+)?(experience|employment|professional)\b", re.I),
    "education": re.compile(r"^\s*education\b", re.I),
    "skills": re.compile(r"^\s*(technical\s+)?skills\b|^\s*technologies\b", re.I),
    "certifications": re.compile(r"^\s*certif", re.I),
}


class HeuristicNormalizer:
    name = "heuristic"

    def normalize_text(self, raw_text: str, *, source: CandidateSource,
                       source_ref_id: str | None, original_file_ref: str | None) -> Candidate:
        lines = [ln.rstrip() for ln in raw_text.splitlines()]
        contact = self._contact(raw_text, lines)
        sections = self._split_sections(lines)

        skills = self._skills(sections.get("skills", []))
        certs = [ln.strip("•-* \t") for ln in sections.get("certifications", []) if ln.strip()]
        work = self._work(sections.get("experience", []))
        education = self._education(sections.get("education", []))

        return Candidate(
            internal_id=str(uuid.uuid4()),
            source=source,
            source_ref_id=source_ref_id,
            contact=contact,
            work_history=work,
            education=education,
            skills=skills,
            certifications=certs,
            raw_text=raw_text,
            original_file_ref=original_file_ref,
        )

    def _contact(self, raw_text: str, lines: list[str]) -> Contact:
        email_m = _EMAIL_RE.search(raw_text)
        email = email_m.group(0) if email_m else None
        phone_m = _PHONE_RE.search(raw_text)
        phone = phone_m.group(0).strip() if phone_m else None
        links = list(dict.fromkeys(_URL_RE.findall(raw_text)))[:5]
        # Name heuristic: first non-empty line that is not contact info.
        name = None
        for ln in lines[:5]:
            s = ln.strip()
            if s and not _EMAIL_RE.search(s) and not _PHONE_RE.search(s) and len(s.split()) <= 5:
                name = s
                break
        return Contact(full_name=name, email=email, phone=phone, links=links)

    def _split_sections(self, lines: list[str]) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {}
        current = None
        for ln in lines:
            matched = None
            for key, rx in _SECTION_HEADERS.items():
                if rx.search(ln) and len(ln.strip()) < 40:
                    matched = key
                    break
            if matched:
                current = matched
                sections.setdefault(current, [])
                continue
            if current:
                sections[current].append(ln)
        return sections

    def _skills(self, lines: list[str]) -> list[str]:
        blob = " ".join(lines)
        parts = re.split(r"[,•|•;/]|\s{2,}|\n", blob)
        skills = []
        for p in parts:
            s = p.strip("•-* \t")
            if 1 < len(s) <= 40 and not s.lower().startswith(("and ", "with ")):
                skills.append(s)
        # de-dup preserving order
        seen, out = set(), []
        for s in skills:
            k = s.lower()
            if k not in seen:
                seen.add(k)
                out.append(s)
        return out[:40]

    def _work(self, lines: list[str]) -> list[WorkExperience]:
        entries: list[WorkExperience] = []
        current: WorkExperience | None = None
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            bullet = s.startswith(("•", "-", "*", "•"))
            if not bullet and len(s) < 90 and (re.search(r"\b(19|20)\d{2}\b", s) or " at " in s.lower() or " - " in s):
                if current:
                    entries.append(current)
                title = s
                org = None
                if " at " in s.lower():
                    parts = re.split(r"\s+at\s+", s, flags=re.I)
                    title, org = parts[0].strip(), parts[1].strip()
                current = WorkExperience(
                    title=title, organization=org,
                    is_current=bool(re.search(r"present|current", s, re.I)),
                    highlights=[],
                )
            elif current is not None:
                current.highlights.append(s.lstrip("•-* \t"))
            else:
                current = WorkExperience(title=s, highlights=[])
        if current:
            entries.append(current)
        return entries[:15]

    def _education(self, lines: list[str]) -> list[Education]:
        out: list[Education] = []
        for ln in lines:
            s = ln.strip("•-* \t")
            if not s:
                continue
            degree = None
            field = None
            m = re.search(r"(bachelor|master|b\.?s\.?|m\.?s\.?|ph\.?d|mba|associate)[^,;]*", s, re.I)
            if m:
                degree = m.group(0).strip()
            fm = re.search(r"\bin\s+([A-Za-z &]+)", s)
            if fm:
                field = fm.group(1).strip()
            inst = s if not degree else None
            out.append(Education(institution=inst, degree=degree, field_of_study=field))
        return out[:8]


class LLMNormalizer:
    name = "llm"

    def __init__(self) -> None:
        from app.llm.client import LLMClient

        self.client = LLMClient()

    _SCHEMA = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "contact": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "full_name": {"type": ["string", "null"]},
                    "email": {"type": ["string", "null"]},
                    "phone": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "links": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["full_name", "email", "phone", "location", "links"],
            },
            "skills": {"type": "array", "items": {"type": "string"}},
            "certifications": {"type": "array", "items": {"type": "string"}},
            "work_history": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": ["string", "null"]},
                        "organization": {"type": ["string", "null"]},
                        "start_date": {"type": ["string", "null"]},
                        "end_date": {"type": ["string", "null"]},
                        "is_current": {"type": "boolean"},
                        "description": {"type": ["string", "null"]},
                        "highlights": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["title", "organization", "start_date", "end_date",
                                 "is_current", "description", "highlights"],
                },
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "institution": {"type": ["string", "null"]},
                        "degree": {"type": ["string", "null"]},
                        "field_of_study": {"type": ["string", "null"]},
                        "start_date": {"type": ["string", "null"]},
                        "end_date": {"type": ["string", "null"]},
                    },
                    "required": ["institution", "degree", "field_of_study",
                                 "start_date", "end_date"],
                },
            },
        },
        "required": ["contact", "skills", "certifications", "work_history", "education"],
    }

    def normalize_text(self, raw_text: str, *, source: CandidateSource,
                       source_ref_id: str | None, original_file_ref: str | None) -> Candidate:
        system = (
            "You extract structured resume data. Extract ONLY what is present. "
            "NEVER infer or output protected attributes (gender, age, date of "
            "birth, marital status, nationality, photo). Capture institution "
            "names under education.institution if present."
        )
        user = f"Extract this resume into the schema.\n\nRESUME:\n{raw_text[:20000]}"
        data = self.client.structured(system=system, user=user, schema=self._SCHEMA, max_tokens=4096)
        c = data["contact"]
        return Candidate(
            internal_id=str(uuid.uuid4()),
            source=source,
            source_ref_id=source_ref_id,
            contact=Contact(**c),
            skills=data["skills"],
            certifications=data["certifications"],
            work_history=[WorkExperience(**w) for w in data["work_history"]],
            education=[Education(**e) for e in data["education"]],
            raw_text=raw_text,
            original_file_ref=original_file_ref,
        )


def build_normalizer():
    settings = get_settings()
    if settings.use_llm_normalizer:
        try:
            return LLMNormalizer()
        except Exception:  # noqa: BLE001 - fall back, never break ingestion
            return HeuristicNormalizer()
    return HeuristicNormalizer()
