"""Candidate source adapters.

MVP ships ``UploadAdapter``. Workday and LinkedIn are left as clean seams
(``workday_adapter.py``, ``linkedin_adapter.py``) — adding either is a new
``CandidateSourceAdapter`` implementation with no change to the scoring core.
"""
from app.adapters.upload_adapter import UploadAdapter

__all__ = ["UploadAdapter"]
