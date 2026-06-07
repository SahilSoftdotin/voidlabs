import React, { useState } from "react";
import { Button, Card } from "../ui.jsx";

// Editable rubric: knockouts + weighted criteria (must sum to 100) + tier bands.
export default function RubricEditor({ rubric, thresholds, onSave }) {
  const [crit, setCrit] = useState(rubric.weighted_criteria);
  const [knockouts, setKnockouts] = useState(rubric.knockouts);
  const [bands, setBands] = useState(thresholds);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  const total = crit.reduce((s, c) => s + Number(c.weight || 0), 0);

  const setC = (i, key, val) =>
    setCrit(crit.map((c, j) => (j === i ? { ...c, [key]: val } : c)));
  const addCrit = () =>
    setCrit([...crit, { id: `crit_${Date.now()}`, name: "New criterion", weight: 0, scoring_guidance: "" }]);
  const delCrit = (i) => setCrit(crit.filter((_, j) => j !== i));

  const setK = (i, key, val) =>
    setKnockouts(knockouts.map((k, j) => (j === i ? { ...k, [key]: val } : k)));
  const addK = () =>
    setKnockouts([
      ...knockouts,
      { id: `ko_${Date.now()}`, name: "New knockout", type: "CUSTOM", description: "", config: { required_terms: [] } },
    ]);
  const delK = (i) => setKnockouts(knockouts.filter((_, j) => j !== i));

  async function save() {
    setErr("");
    if (total !== 100) {
      setErr(`Weights must sum to 100 (currently ${total}).`);
      return;
    }
    setSaving(true);
    try {
      await onSave({
        rubric: { knockouts, weighted_criteria: crit.map((c) => ({ ...c, weight: Number(c.weight) })) },
        tier_thresholds: { a_min: Number(bands.a_min), b_min: Number(bands.b_min) },
      });
    } catch (e) {
      setErr(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card
      title="Rubric"
      right={
        <span className={`text-xs font-semibold ${total === 100 ? "text-emerald-600" : "text-red-600"}`}>
          Weights: {total}/100
        </span>
      }
    >
      <div className="space-y-6">
        <section>
          <div className="mb-2 flex items-center justify-between">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Stage 1 · Knockout filters (pass/fail)
            </h4>
            <Button variant="ghost" onClick={addK}>+ Knockout</Button>
          </div>
          <div className="space-y-2">
            {knockouts.map((k, i) => (
              <div key={k.id} className="grid grid-cols-12 gap-2 rounded-lg bg-slate-50 p-2">
                <input className="col-span-3 rounded border-slate-300 px-2 py-1 text-sm"
                  value={k.name} onChange={(e) => setK(i, "name", e.target.value)} />
                <select className="col-span-3 rounded border-slate-300 px-2 py-1 text-sm"
                  value={k.type} onChange={(e) => setK(i, "type", e.target.value)}>
                  {["WORK_AUTHORIZATION", "REQUIRED_CERTIFICATION", "LOCATION_CONSTRAINT", "REQUIRED_SKILL", "CUSTOM"].map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                <input className="col-span-5 rounded border-slate-300 px-2 py-1 text-sm"
                  placeholder="required terms (comma separated)"
                  value={(k.config?.required_terms || []).join(", ")}
                  onChange={(e) =>
                    setK(i, "config", { ...k.config, required_terms: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) })
                  } />
                <button className="col-span-1 text-sm text-red-500" onClick={() => delK(i)}>✕</button>
              </div>
            ))}
            {knockouts.length === 0 && <p className="text-xs text-slate-400">No knockouts — keep this list short and truly non-negotiable.</p>}
          </div>
        </section>

        <section>
          <div className="mb-2 flex items-center justify-between">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Stage 2 · Weighted criteria (0–5 each)
            </h4>
            <Button variant="ghost" onClick={addCrit}>+ Criterion</Button>
          </div>
          <div className="space-y-2">
            {crit.map((c, i) => (
              <div key={c.id} className="grid grid-cols-12 gap-2 rounded-lg bg-slate-50 p-2">
                <input className="col-span-3 rounded border-slate-300 px-2 py-1 text-sm"
                  value={c.name} onChange={(e) => setC(i, "name", e.target.value)} />
                <input type="number" min="0" max="100" className="col-span-2 rounded border-slate-300 px-2 py-1 text-sm"
                  value={c.weight} onChange={(e) => setC(i, "weight", e.target.value)} />
                <input className="col-span-6 rounded border-slate-300 px-2 py-1 text-sm"
                  placeholder="scoring guidance" value={c.scoring_guidance}
                  onChange={(e) => setC(i, "scoring_guidance", e.target.value)} />
                <button className="col-span-1 text-sm text-red-500" onClick={() => delCrit(i)}>✕</button>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Stage 3 · Tier bands
          </h4>
          <div className="flex items-center gap-3 text-sm">
            <label className="flex items-center gap-1">A ≥
              <input type="number" className="w-20 rounded border-slate-300 px-2 py-1"
                value={bands.a_min} onChange={(e) => setBands({ ...bands, a_min: e.target.value })} />
            </label>
            <label className="flex items-center gap-1">B ≥
              <input type="number" className="w-20 rounded border-slate-300 px-2 py-1"
                value={bands.b_min} onChange={(e) => setBands({ ...bands, b_min: e.target.value })} />
            </label>
            <span className="text-slate-400">C below B</span>
          </div>
        </section>

        {err && <p className="text-sm text-red-600">{err}</p>}
        <Button onClick={save} disabled={saving}>{saving ? "Saving…" : "Save rubric"}</Button>
      </div>
    </Card>
  );
}
