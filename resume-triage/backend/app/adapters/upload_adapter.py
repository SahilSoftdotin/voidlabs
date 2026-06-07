"""UploadAdapter — manual PDF/DOCX/TXT upload source (MVP).

Implements ``CandidateSourceAdapter``. ``normalize`` maps a raw uploaded file
into the normalized ``Candidate`` schema; ``fetch_candidates`` is the batch
entry point. Files are persisted so ``original_file_ref`` stays resolvable.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings
from app.domain.schemas import Candidate, CandidateSource
from app.services.parsing import build_normalizer, extract_text


@dataclass
class RawUpload:
    filename: str
    data: bytes


class UploadAdapter:
    source_name = CandidateSource.UPLOAD.value

    def __init__(self) -> None:
        self._normalizer = build_normalizer()
        self._storage = Path(get_settings().storage_dir)
        self._storage.mkdir(parents=True, exist_ok=True)

    def fetch_candidates(self, job_ref: str, *, uploads: list[RawUpload] | None = None,
                         **kwargs) -> list[Candidate]:
        uploads = uploads or []
        return [self.normalize(u) for u in uploads]

    def normalize(self, raw: RawUpload) -> Candidate:
        file_ref = self._persist(raw)
        text = extract_text(raw.filename, raw.data)
        candidate = self._normalizer.normalize_text(
            text,
            source=CandidateSource.UPLOAD,
            source_ref_id=raw.filename,
            original_file_ref=file_ref,
        )
        return candidate

    def _persist(self, raw: RawUpload) -> str:
        safe = Path(raw.filename).name
        unique = f"{uuid.uuid4().hex}_{safe}"
        path = self._storage / unique
        path.write_bytes(raw.data)
        return unique
