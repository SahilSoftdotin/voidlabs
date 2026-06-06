// Thin API client for the triage backend.
const BASE = "/api";

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch (_) {}
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

export const api = {
  health: () => req("/health"),
  defaultRubric: () => req("/default-rubric"),
  listJobs: () => req("/jobs"),
  getJob: (id) => req(`/jobs/${id}`),
  createJob: (body) =>
    req("/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  updateRubric: (id, body) =>
    req(`/jobs/${id}/rubric`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  uploadResumes: (id, files) => {
    const fd = new FormData();
    for (const f of files) fd.append("files", f);
    return req(`/jobs/${id}/candidates`, { method: "POST", body: fd });
  },
  batchStatus: (jobId, batchId) => req(`/jobs/${jobId}/batches/${batchId}`),
  listCandidates: (id, params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null),
    );
    return req(`/jobs/${id}/candidates?${q.toString()}`);
  },
  getCandidate: (id) => req(`/candidates/${id}`),
  rescore: (id) => req(`/candidates/${id}/rescore`, { method: "POST" }),
  override: (id, body) =>
    req(`/candidates/${id}/override`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  regenQuestions: (id) =>
    req(`/candidates/${id}/interview-questions/regenerate`, { method: "POST" }),
  saveQuestions: (id, questions) =>
    req(`/candidates/${id}/interview-questions`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questions }),
    }),
  calibrate: (id, body) =>
    req(`/candidates/${id}/calibration`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  candidateAudit: (id) => req(`/candidates/${id}/audit`),
  jobAudit: (id) => req(`/jobs/${id}/audit`),
  exportUrl: (id, fmt) => `${BASE}/jobs/${id}/export?format=${fmt}`,
  fileUrl: (id) => `${BASE}/candidates/${id}/file`,
};
