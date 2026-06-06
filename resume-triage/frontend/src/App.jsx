import React, { useEffect, useRef, useState } from "react";
import { api } from "./api.js";
import { Button, Card, TierBadge } from "./ui.jsx";
import RubricEditor from "./components/RubricEditor.jsx";
import CandidateDetail from "./components/CandidateDetail.jsx";

export default function App() {
  const [view, setView] = useState({ name: "jobs" });
  const [health, setHealth] = useState(null);

  useEffect(() => { api.health().then(setHealth).catch(() => {}); }, []);

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <button className="text-left" onClick={() => setView({ name: "jobs" })}>
            <h1 className="text-lg font-bold tracking-tight">Resume Triage</h1>
            <p className="text-xs text-slate-400">Scores & tiers candidates against a job-specific rubric — triage, not auto-reject.</p>
          </button>
          {health && (
            <div className="text-right text-xs text-slate-400">
              <div>scoring: <b className="text-slate-600">{health.scoring_backend}</b> · parser: <b className="text-slate-600">{health.normalizer}</b></div>
              <div>engine v{health.engine_version}</div>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-6">
        {view.name === "jobs" && <JobsView onOpen={(id) => setView({ name: "job", id })} />}
        {view.name === "job" && (
          <JobView
            jobId={view.id}
            onOpenCandidate={(cid) => setView({ name: "candidate", id: cid, jobId: view.id })}
          />
        )}
        {view.name === "candidate" && (
          <CandidateDetail
            candidateId={view.id}
            onBack={() => setView({ name: "job", id: view.jobId })}
          />
        )}
      </main>
    </div>
  );
}

function JobsView({ onOpen }) {
  const [jobs, setJobs] = useState([]);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");

  const load = () => api.listJobs().then(setJobs);
  useEffect(() => { load(); }, []);

  async function create() {
    if (!title.trim()) return;
    const job = await api.createJob({ title, description: desc });
    setCreating(false); setTitle(""); setDesc("");
    onOpen(job.id);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Open requisitions</h2>
        <Button onClick={() => setCreating(!creating)}>{creating ? "Cancel" : "+ New job"}</Button>
      </div>

      {creating && (
        <Card title="Create job">
          <div className="space-y-2">
            <input className="w-full rounded border-slate-300 px-3 py-2 text-sm" placeholder="Job title"
              value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea className="w-full rounded border-slate-300 px-3 py-2 text-sm" rows={4}
              placeholder="Job description / required skills (used for semantic matching)"
              value={desc} onChange={(e) => setDesc(e.target.value)} />
            <Button onClick={create}>Create & set rubric</Button>
          </div>
        </Card>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        {jobs.map((j) => (
          <button key={j.id} onClick={() => onOpen(j.id)}
            className="rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm hover:border-slate-300">
            <h3 className="font-semibold">{j.title}</h3>
            <p className="line-clamp-2 text-xs text-slate-400">{j.description || "No description"}</p>
            <p className="mt-2 text-xs text-slate-500">{j.candidate_count} candidate(s)</p>
          </button>
        ))}
        {jobs.length === 0 && <p className="text-sm text-slate-400">No jobs yet — create one to begin.</p>}
      </div>
    </div>
  );
}

function JobView({ jobId, onOpenCandidate }) {
  const [job, setJob] = useState(null);
  const [showRubric, setShowRubric] = useState(false);
  const [candidates, setCandidates] = useState([]);
  const [filters, setFilters] = useState({ tier: "", status: "", min_score: "", search: "", sort: "total_desc" });
  const [batch, setBatch] = useState(null);
  const fileRef = useRef();
  const pollRef = useRef();

  const loadJob = () => api.getJob(jobId).then(setJob);
  const loadCandidates = () => api.listCandidates(jobId, filters).then((d) => setCandidates(d.candidates));

  useEffect(() => { loadJob(); }, [jobId]);
  useEffect(() => { loadCandidates(); }, [jobId, JSON.stringify(filters)]);

  async function upload(e) {
    const files = [...e.target.files];
    if (!files.length) return;
    const b = await api.uploadResumes(jobId, files);
    setBatch(b);
    fileRef.current.value = "";
    poll(b.id);
  }

  function poll(batchId) {
    clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      const b = await api.batchStatus(jobId, batchId);
      setBatch(b);
      if (b.status === "DONE") {
        clearInterval(pollRef.current);
        loadCandidates(); loadJob();
      }
    }, 1000);
  }
  useEffect(() => () => clearInterval(pollRef.current), []);

  if (!job) return <div className="text-slate-500">Loading…</div>;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold">{job.title}</h2>
          <p className="text-xs text-slate-400">{job.candidate_count} candidate(s)</p>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => setShowRubric(!showRubric)}>{showRubric ? "Hide rubric" : "Edit rubric"}</Button>
          <a href={api.exportUrl(jobId, "csv")}><Button variant="ghost">Export CSV</Button></a>
          <a href={api.exportUrl(jobId, "json")}><Button variant="ghost">Export JSON</Button></a>
          <Button onClick={() => fileRef.current.click()}>Upload resumes</Button>
          <input ref={fileRef} type="file" multiple accept=".pdf,.docx,.txt,.md" className="hidden" onChange={upload} />
        </div>
      </div>

      {batch && batch.status !== "DONE" && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm text-blue-700">
          Processing batch… {batch.processed}/{batch.total} done{batch.failed ? `, ${batch.failed} failed` : ""}
        </div>
      )}

      {showRubric && (
        <RubricEditor
          rubric={job.rubric}
          thresholds={job.tier_thresholds}
          onSave={async (body) => { await api.updateRubric(jobId, body); await loadJob(); setShowRubric(false); }}
        />
      )}

      <Card title="Ranked candidates" right={
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <select className="rounded border-slate-300 px-2 py-1" value={filters.tier}
            onChange={(e) => setFilters({ ...filters, tier: e.target.value })}>
            <option value="">All tiers</option><option>A</option><option>B</option><option>C</option>
          </select>
          <select className="rounded border-slate-300 px-2 py-1" value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
            <option value="">All statuses</option><option value="SCORED">Scored</option><option value="KNOCKED_OUT">Knocked out</option>
          </select>
          <input type="number" placeholder="min score" className="w-24 rounded border-slate-300 px-2 py-1"
            value={filters.min_score} onChange={(e) => setFilters({ ...filters, min_score: e.target.value })} />
          <input placeholder="search" className="w-32 rounded border-slate-300 px-2 py-1"
            value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
          <select className="rounded border-slate-300 px-2 py-1" value={filters.sort}
            onChange={(e) => setFilters({ ...filters, sort: e.target.value })}>
            <option value="total_desc">Score ↓</option><option value="total_asc">Score ↑</option><option value="name">Name</option>
          </select>
        </div>
      }>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 text-left text-xs uppercase text-slate-400">
              <th className="py-2">#</th><th>Candidate</th><th>Tier</th><th>Score</th><th>Status</th><th></th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c, i) => (
              <tr key={c.id} className="border-b border-slate-50 hover:bg-slate-50">
                <td className="py-2 text-slate-400">{i + 1}</td>
                <td className="font-medium">{c.name || c.source_ref_id || c.id.slice(0, 8)}</td>
                <td><TierBadge tier={c.tier} status={c.status} /></td>
                <td className="font-semibold">{c.total?.toFixed?.(1) ?? "—"}</td>
                <td className="text-xs text-slate-500">{c.status}</td>
                <td><button className="text-xs text-blue-600" onClick={() => onOpenCandidate(c.id)}>View →</button></td>
              </tr>
            ))}
            {candidates.length === 0 && (
              <tr><td colSpan={6} className="py-6 text-center text-slate-400">No candidates match. Upload resumes to begin.</td></tr>
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
