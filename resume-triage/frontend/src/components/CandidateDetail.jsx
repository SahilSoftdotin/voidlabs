import React, { useEffect, useState } from "react";
import { api } from "../api.js";
import { Badge, Button, Card, ScoreBar, TierBadge } from "../ui.jsx";

export default function CandidateDetail({ candidateId, onBack, onChanged }) {
  const [data, setData] = useState(null);
  const [audit, setAudit] = useState([]);
  const [busy, setBusy] = useState(false);

  async function load() {
    const d = await api.getCandidate(candidateId);
    setData(d);
    setAudit((await api.candidateAudit(candidateId)).entries);
  }
  useEffect(() => { load(); }, [candidateId]);

  if (!data) return <div className="p-6 text-slate-500">Loading…</div>;
  const { candidate, score } = data;

  async function doOverride(crit) {
    const reason = window.prompt(`Override "${crit.criterion_name}". Reason (required):`);
    if (!reason) return;
    const val = window.prompt("New score 0–5:", crit.raw_score);
    if (val == null) return;
    setBusy(true);
    try {
      await api.override(candidateId, {
        criterion_id: crit.criterion_id,
        new_raw_score: Number(val),
        reason,
      });
      await load();
      onChanged?.();
    } finally { setBusy(false); }
  }

  async function regen() {
    setBusy(true);
    try { await api.regenQuestions(candidateId); await load(); } finally { setBusy(false); }
  }

  async function rescore() {
    setBusy(true);
    try { await api.rescore(candidateId); await load(); onChanged?.(); } finally { setBusy(false); }
  }

  async function calibrate() {
    const outcome = window.prompt("Record real outcome (e.g. INTERVIEWED / HIRED / REJECTED):");
    if (!outcome) return;
    const notes = window.prompt("Notes (optional):") || null;
    await api.calibrate(candidateId, { outcome, notes });
    setAudit((await api.candidateAudit(candidateId)).entries);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button className="text-sm text-slate-500 hover:text-slate-800" onClick={onBack}>← Back to ranked list</button>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={rescore} disabled={busy}>Re-score</Button>
          <Button variant="ghost" onClick={calibrate}>Record outcome</Button>
        </div>
      </div>

      <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">{candidate.contact.full_name || candidate.source_ref_id || "Candidate"}</h2>
            <TierBadge tier={score?.tier} status={score?.status} />
          </div>
          <p className="text-xs text-slate-400">
            {candidate.contact.email} · {candidate.contact.location} · engine {score?.engine_version}
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-slate-900">{score ? score.total.toFixed(1) : "—"}</div>
          <div className="text-xs text-slate-400">/ 100</div>
          {data.has_file && (
            <a className="text-xs text-blue-600 hover:underline" href={api.fileUrl(candidateId)} target="_blank" rel="noreferrer">
              Original file ↗
            </a>
          )}
        </div>
      </div>

      {score?.status === "KNOCKED_OUT" && (
        <Card title="Knockout — excluded from scoring (not deleted)">
          <ul className="space-y-1 text-sm">
            {score.knockout_results.map((k) => (
              <li key={k.knockout_id} className="flex gap-2">
                <span className={k.passed ? "text-emerald-600" : "text-red-600"}>{k.passed ? "✓" : "✕"}</span>
                <span><b>{k.knockout_name}:</b> {k.justification}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {score?.per_criterion?.length > 0 && (
          <Card title="Score breakdown (per criterion)">
            <div className="space-y-3">
              {score.per_criterion.map((c) => (
                <div key={c.criterion_id}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">
                      {c.criterion_name} {c.overridden && <Badge className="bg-blue-100 text-blue-700 border-blue-200">override</Badge>}
                    </span>
                    <span className="text-slate-500">
                      {c.raw_score}/5 × {c.weight}% = <b>{c.weighted_score.toFixed(1)}</b>
                      <button className="ml-2 text-xs text-blue-600" onClick={() => doOverride(c)} disabled={busy}>edit</button>
                    </span>
                  </div>
                  <ScoreBar value={c.raw_score} />
                  <p className="mt-1 text-xs text-slate-500">{c.justification}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        <Card
          title="Manager interview questions"
          right={<Button variant="ghost" onClick={regen} disabled={busy}>Regenerate</Button>}
        >
          <InterviewQuestions
            candidateId={candidateId}
            questions={score?.interview_questions || []}
            onSaved={load}
          />
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Parsed resume">
          <ResumeView candidate={candidate} />
        </Card>
        <Card title="Audit trail">
          <ul className="space-y-2 text-xs">
            {audit.map((e) => (
              <li key={e.id} className="border-l-2 border-slate-200 pl-2">
                <div className="font-medium text-slate-700">{e.action} <span className="text-slate-400">· {e.actor}</span></div>
                <div className="text-slate-400">{new Date(e.timestamp).toLocaleString()}</div>
                {e.reason && <div className="text-slate-500">{e.reason}</div>}
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}

function InterviewQuestions({ candidateId, questions, onSaved }) {
  const [items, setItems] = useState(questions);
  const [dirty, setDirty] = useState(false);
  useEffect(() => { setItems(questions); setDirty(false); }, [questions]);

  const upd = (i, key, val) => { setItems(items.map((q, j) => (j === i ? { ...q, [key]: val } : q))); setDirty(true); };
  const del = (i) => { setItems(items.filter((_, j) => j !== i)); setDirty(true); };
  const add = () => { setItems([...items, { question: "", resume_item: "", type: "technical", signal: "" }]); setDirty(true); };

  async function save() {
    await api.saveQuestions(candidateId, items);
    setDirty(false);
    onSaved?.();
  }

  return (
    <div className="space-y-3">
      {items.map((q, i) => (
        <div key={i} className="rounded-lg border border-slate-100 bg-slate-50 p-2">
          <div className="mb-1 flex items-center justify-between">
            <select className="rounded border-slate-300 px-1 py-0.5 text-xs"
              value={q.type} onChange={(e) => upd(i, "type", e.target.value)}>
              <option value="technical">technical</option>
              <option value="behavioral">behavioral</option>
            </select>
            <button className="text-xs text-red-500" onClick={() => del(i)}>remove</button>
          </div>
          <textarea className="w-full rounded border-slate-300 px-2 py-1 text-sm" rows={2}
            value={q.question} onChange={(e) => upd(i, "question", e.target.value)} />
          <p className="mt-1 text-xs text-slate-500"><b>Probes:</b> {" "}
            <input className="w-3/4 rounded border-slate-200 px-1 text-xs" value={q.resume_item}
              onChange={(e) => upd(i, "resume_item", e.target.value)} />
          </p>
          <p className="mt-1 text-xs text-slate-400"><b>Signal:</b> {" "}
            <input className="w-3/4 rounded border-slate-200 px-1 text-xs" value={q.signal}
              onChange={(e) => upd(i, "signal", e.target.value)} />
          </p>
        </div>
      ))}
      <div className="flex gap-2">
        <Button variant="ghost" onClick={add}>+ Add</Button>
        {dirty && <Button onClick={save}>Save changes</Button>}
      </div>
    </div>
  );
}

function ResumeView({ candidate }) {
  return (
    <div className="space-y-3 text-sm">
      <div>
        <h5 className="text-xs font-semibold uppercase text-slate-400">Skills</h5>
        <div className="mt-1 flex flex-wrap gap-1">
          {candidate.skills.map((s, i) => <Badge key={i} className="bg-slate-100 text-slate-600 border-slate-200">{s}</Badge>)}
        </div>
      </div>
      <div>
        <h5 className="text-xs font-semibold uppercase text-slate-400">Experience</h5>
        {candidate.work_history.map((w, i) => (
          <div key={i} className="mt-1">
            <div className="font-medium">{w.title} {w.organization && <span className="text-slate-400">· {w.organization}</span>}</div>
            <ul className="ml-4 list-disc text-xs text-slate-500">
              {(w.highlights || []).map((h, j) => <li key={j}>{h}</li>)}
            </ul>
          </div>
        ))}
      </div>
      <div>
        <h5 className="text-xs font-semibold uppercase text-slate-400">Education</h5>
        {candidate.education.map((e, i) => (
          <div key={i} className="text-xs text-slate-500">{e.degree} {e.field_of_study && `in ${e.field_of_study}`} {e.institution && `· ${e.institution}`}</div>
        ))}
      </div>
    </div>
  );
}
