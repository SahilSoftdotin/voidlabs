"""Resume Scoring & Candidate Triage backend.

Hexagonal architecture: the scoring core depends only on the normalized
domain schema (``app.domain.schemas``) and the port interfaces
(``app.core.ports``). Vendor-specific candidate sources (upload today,
Workday/LinkedIn later) plug in as adapters without touching the core.
"""

ENGINE_VERSION = "1.0.0"
