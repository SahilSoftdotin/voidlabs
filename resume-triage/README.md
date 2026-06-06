# Resume Scoring & Candidate Triage

A web app that scores and ranks a batch of resumes against a **specific job's
rubric** and surfaces a top tier of candidates for human review. It **triages —
it does not auto-reject**. The only automatic exclusions are true Stage‑1
knockout filters; everything else is ranked for a person to decide.

> Built per the spec in the build prompt. MVP choices (confirmed up front):
> Python FastAPI backend + React frontend, hosted Claude LLM for semantic
> scoring (with a deterministic offline fallback), batch sizes in the hundreds,
> single‑user (no auth — auth left as a seam).

---

## Why it's built this way (design principles)

| Principle | How it's enforced |
|---|---|
| **Score relative to a job, never in the abstract** | The rubric (knockouts + weighted criteria + tier bands) is an input on each `Job`. The same resume scores differently per job. Nothing rubric‑related is hardcoded in the engine. |
| **Triage, don't auto‑reject** | Only Stage‑1 knockouts exclude a candidate, and even then the candidate is kept fully visible (status `KNOCKED_OUT`), never deleted. |
| **Bias & compliance built in** | The scorer is only ever handed a `CandidateScoringView` that structurally has **no** field for name, gender, age/DOB, photo, marital status, nationality, and drops institution names. A runtime guard (`assert_scoring_view_clean`) re‑proves nothing leaked. Employment gaps are never penalized (stated in rubric guidance + prompts). |
| **Human‑in‑the‑loop** | Any criterion score can be overridden with a **required reason** (logged); tiers/totals recompute. Interview questions are editable. |
| **Explainability** | Every criterion returns `raw_score`, `weighted_score`, and a `justification`. The total decomposes exactly into per‑criterion contributions. |
| **Future Workday/LinkedIn without rewriting the core** | Hexagonal ports/adapters. The core depends only on the normalized schema + `CandidateSourceAdapter`. `UploadAdapter` ships; `WorkdayAdapter`/`LinkedInAdapter` are clean seams with integration notes and TODOs. |

---

## Architecture

```
resume-triage/
├── backend/                      FastAPI + SQLAlchemy
│   └── app/
│       ├── domain/schemas.py     Normalized Candidate/Job/Rubric/Score + bias-safe scoring view
│       ├── core/
│       │   ├── ports.py          CandidateSourceAdapter / Scorer / ATSWriteAdapter interfaces
│       │   └── default_rubric.py Editable default mid-level rubric (weights sum to 100)
│       ├── adapters/             UploadAdapter (MVP) + Workday/LinkedIn seams + OAuth placeholder
│       ├── services/
│       │   ├── parsing.py        PDF/DOCX/TXT → normalized Candidate (heuristic + LLM normalizers)
│       │   ├── bias.py           Protected-attribute guard
│       │   ├── scorers/          mock_scorer (offline) + llm_scorer (Claude); build_scorer() selects
│       │   ├── scoring_engine.py Stages 1–3 orchestration + interview questions
│       │   ├── pipeline.py       Async batch ingest+score (designed for hundreds)
│       │   └── audit.py          Audit log
│       ├── llm/client.py         Anthropic SDK wrapper (structured JSON output)
│       ├── db/                   ORM models + engine
│       └── api/                  jobs / candidates / audit_export routers
└── frontend/                     React + Vite + Tailwind dashboard
```

### Scoring pipeline (§4)
1. **Stage 1 — Knockouts** → pass/fail. Any fail ⇒ excluded from scoring, kept visible.
2. **Stage 2 — Weighted scoring** → each criterion 0–5 × weight ⇒ 0–100 total, each with a justification.
3. **Stage 3 — Tiering** → A/B/C bands (thresholds configurable per job).
4. **Interview questions** → 5 tailored manager questions grounded in standout resume items (mix technical/behavioral, each with the resume item probed + good‑vs‑weak signal).

### Semantic scoring
The LLM scorer (Claude, default `claude-opus-4-8`) uses semantic skill matching
and returns a **structured per‑criterion JSON** with justifications, so output
stays explainable and auditable. When no `ANTHROPIC_API_KEY` is set, the app
transparently falls back to a deterministic, offline `MockScorer` so the whole
system runs and is fully testable with no network.

---

## Running it

### Backend
```bash
cd resume-triage/backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY for LLM scoring (optional)
uvicorn app.main:app --reload --port 8000
```
API docs at <http://localhost:8000/docs>. Health at `/api/health`.

Scoring backend selection (`.env`):
- `SCORING_BACKEND=auto` — LLM when a key is present, else the offline mock.
- `=llm` / `=mock` to force either. Same pattern for `RESUME_NORMALIZER`.

For production, point `DATABASE_URL` at PostgreSQL and uncomment the `psycopg`
dependency in `requirements.txt`.

### Frontend
```bash
cd resume-triage/frontend
npm install
npm run dev        # http://localhost:5173 (proxies /api → :8000)
```

### Tests
```bash
cd resume-triage/backend && . .venv/bin/activate && pytest
```
Covers the testable acceptance criteria: bias protection (scorer never reads
protected attributes), knockouts exclude‑not‑delete, weighting/total math,
rubric‑relative scoring, interview‑question generation, adapter conformance, and
a full create‑job → upload → rank → override → export → audit API flow.

---

## API surface (selected)
| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/default-rubric` | Editable starting rubric |
| `POST` | `/api/jobs` | Create job (validates weights = 100) |
| `PUT` | `/api/jobs/{id}/rubric` | Edit rubric / tier bands |
| `POST` | `/api/jobs/{id}/candidates` | Bulk resume upload → background parse+score |
| `GET` | `/api/jobs/{id}/batches/{bid}` | Batch progress |
| `GET` | `/api/jobs/{id}/candidates` | Ranked list (filter by tier/score/criterion, search, sort) |
| `GET` | `/api/candidates/{id}` | Full breakdown + parsed resume + interview questions |
| `GET` | `/api/candidates/{id}/file` | Download original file |
| `POST` | `/api/candidates/{id}/override` | Override a criterion (reason required, logged) |
| `POST` | `/api/candidates/{id}/interview-questions/regenerate` | Regenerate questions |
| `PUT` | `/api/candidates/{id}/interview-questions` | Manager edits questions |
| `POST` | `/api/candidates/{id}/calibration` | Record real hire/interview outcome (calibration hook) |
| `GET` | `/api/jobs/{id}/audit`, `/api/candidates/{id}/audit` | Audit log |
| `GET` | `/api/jobs/{id}/export?format=csv\|json` | Export ranked results |

---

## Future integrations (seams only — not built, per §6)
- **Workday** — Recruiting REST API + Reports‑as‑a‑Service (RaaS). Needs tenant
  config + OAuth client‑credentials. See `adapters/workday_adapter.py`.
- **LinkedIn** — Talent Solutions / Recruiter System Connect (RSC). Needs
  partner approval + 3‑legged OAuth. See `adapters/linkedin_adapter.py`.
- **ATS write‑back** — `ATSWriteAdapter` port for pushing dispositions back.
- **Auth** — single‑user today; `app/main.py` is where a recruiter/hiring‑manager
  auth dependency would attach.

Verify both vendors' current API docs at integration time — they change.
