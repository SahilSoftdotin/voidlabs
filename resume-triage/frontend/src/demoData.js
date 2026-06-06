// In-memory demo backend used ONLY for the standalone preview build
// (VITE_DEMO=1). It mimics the real API so the UI is fully clickable offline.
// The production app uses src/api.js against the FastAPI backend instead.

const CRITERIA = [
  { id: "skills_match", name: "Relevant skills / tools match", weight: 30, scoring_guidance: "Semantic overlap with required skills." },
  { id: "experience_depth", name: "Depth & relevance of experience", weight: 25, scoring_guidance: "Years in a similar role/domain." },
  { id: "impact", name: "Demonstrated impact", weight: 20, scoring_guidance: "Quantified achievements, not duties." },
  { id: "trajectory", name: "Career trajectory", weight: 10, scoring_guidance: "Growth / increasing responsibility." },
  { id: "education", name: "Education & certifications", weight: 10, scoring_guidance: "Relevance only; ignore prestige." },
  { id: "clarity", name: "Resume clarity & communication", weight: 5, scoring_guidance: "Structure and readability." },
];

function crit(id, raw, just) {
  const c = CRITERIA.find((x) => x.id === id);
  return { criterion_id: id, criterion_name: c.name, raw_score: raw, weight: c.weight,
    weighted_score: Math.round((raw / 5) * c.weight * 100) / 100, justification: just, overridden: false, original_raw_score: null };
}
function total(per) { return Math.round(per.reduce((s, c) => s + c.weighted_score, 0) * 100) / 100; }
function tierOf(t) { return t >= 75 ? "A" : t >= 55 ? "B" : "C"; }

const job = {
  id: "job-1",
  title: "Senior Backend Engineer",
  description: "Python, FastAPI, PostgreSQL, Docker, Kubernetes, distributed systems, observability.",
  rubric: { knockouts: [
      { id: "work_authorization", name: "Work authorization", type: "WORK_AUTHORIZATION", description: "Authorized to work in role location.", config: { required_terms: ["authorized to work", "citizen", "permanent resident"] } },
    ], weighted_criteria: CRITERIA },
  tier_thresholds: { a_min: 75, b_min: 55 },
  created_at: new Date().toISOString(),
  candidate_count: 4,
};

function mkCandidate(id, name, email, location, skills, work, edu, certs, per, status, knockouts) {
  const t = status === "KNOCKED_OUT" ? 0 : total(per);
  return {
    id, job_id: "job-1",
    candidate: {
      internal_id: id, source: "UPLOAD", source_ref_id: name.toLowerCase().replace(/\s+/g, "_") + ".pdf",
      contact: { full_name: name, email, phone: "555-0100", location, links: [] },
      work_history: work, education: edu, skills, certifications: certs, raw_text: "", original_file_ref: id + ".pdf",
    },
    score: {
      candidate_id: id, job_id: "job-1", status, per_criterion: status === "KNOCKED_OUT" ? [] : per,
      knockout_results: knockouts, total: t, tier: status === "KNOCKED_OUT" ? null : tierOf(t),
      engine_version: "1.0.0+mock-heuristic-1.0",
      interview_questions: status === "KNOCKED_OUT" ? [] : interviewFor(name, skills, work),
    },
    has_file: true,
  };
}

function interviewFor(name, skills, work) {
  const top = skills[0] || "your core stack";
  const lead = work[0] || { title: "your most recent role" };
  return [
    { question: `You report cutting p99 latency by 40% across 12 microservices. Walk me through how it was measured and what you personally owned versus the team.`,
      resume_item: "Cut p99 latency by 40% across 12 microservices", type: "technical",
      signal: "Strong: concrete baseline, method, clear individual contribution. Weak: vague, can't reproduce the number." },
    { question: `Describe the most technically demanding problem you solved using ${top}, including a tradeoff you got wrong and corrected.`,
      resume_item: `Listed skill: ${top}`, type: "technical",
      signal: `Strong: specific, hands-on detail and learned tradeoffs in ${top}. Weak: textbook definitions.` },
    { question: `Tell me about a project at ${lead.title} where you drove the outcome — situation, decision, result.`,
      resume_item: `Role: ${lead.title}`, type: "behavioral",
      signal: "Strong (STAR): clear situation, decisions they made, measurable result. Weak: diffuse team credit." },
    { question: `You moved between roles recently. What drove that change and what did you have to learn fastest?`,
      resume_item: "Career transition between roles", type: "behavioral",
      signal: "Strong: deliberate reasoning, self-awareness. Weak: no narrative or purely circumstantial." },
    { question: "Tell me about a time you disagreed with a stakeholder on a technical decision. How did you handle it?",
      resume_item: "General professional conduct (collaboration & conflict)", type: "behavioral",
      signal: "Strong: respectful, data-driven resolution with a real outcome. Weak: avoidance or blame." },
  ];
}

const candidates = [
  mkCandidate("c1", "Jordan Rivera", "jordan@example.com", "Austin, TX",
    ["Python", "FastAPI", "PostgreSQL", "Kubernetes", "Docker", "gRPC"],
    [{ title: "Senior Backend Engineer", organization: "Acme Cloud", is_current: true, highlights: ["Cut p99 latency by 40% across 12 microservices", "Led migration of 3 services to Python and FastAPI"] },
     { title: "Backend Engineer", organization: "Beta Corp", highlights: ["Built REST APIs serving 2M requests/day"] }],
    [{ degree: "BS", field_of_study: "Computer Science", institution: "State University" }],
    ["AWS Solutions Architect"],
    [crit("skills_match", 4.6, "Strong overlap: Python, FastAPI, PostgreSQL, Kubernetes, Docker (5 concepts)."),
     crit("experience_depth", 4.2, "2 directly-relevant roles with substantive detail. Gaps not penalized."),
     crit("impact", 4.0, "3 quantified achievement signals (40%, 12 services, 2M req/day)."),
     crit("trajectory", 3.8, "2 distinct titles; 1 senior-level marker."),
     crit("education", 3.5, "CS degree relevant; 1 certification. Prestige ignored."),
     crit("clarity", 4.0, "Structure complete across 4/4 expected sections.")],
    "SCORED",
    [{ knockout_id: "work_authorization", knockout_name: "Work authorization", passed: true, justification: "Not determinable from resume — assumed pass; verify with candidate." }]),

  mkCandidate("c2", "Priya Natarajan", "priya@example.com", "Remote",
    ["Python", "Django", "PostgreSQL", "Redis", "Terraform"],
    [{ title: "Backend Engineer", organization: "Fintech Inc", is_current: true, highlights: ["Owned billing service handling $30M/yr", "Reduced incident rate 25%"] }],
    [{ degree: "MS", field_of_study: "Software Engineering", institution: "Tech Institute" }],
    [],
    [crit("skills_match", 3.4, "Partial overlap: Python, PostgreSQL; FastAPI/K8s not evidenced (3 concepts)."),
     crit("experience_depth", 3.2, "1 relevant role with detail."),
     crit("impact", 3.5, "2 quantified signals ($30M, 25%)."),
     crit("trajectory", 2.5, "1 distinct title; limited progression signal."),
     crit("education", 3.6, "Relevant MS field; 0 certifications."),
     crit("clarity", 3.5, "Structure complete across 3/4 sections.")],
    "SCORED",
    [{ knockout_id: "work_authorization", knockout_name: "Work authorization", passed: true, justification: "Not determinable from resume — assumed pass; verify with candidate." }]),

  mkCandidate("c3", "Marcus Webb", "marcus@example.com", "Denver, CO",
    ["Java", "Spring", "MySQL", "Python"],
    [{ title: "Software Engineer", organization: "Enterprise Co", highlights: ["Maintained legacy services", "Wrote unit tests"] }],
    [{ degree: "BS", field_of_study: "Information Systems", institution: "Regional College" }],
    [],
    [crit("skills_match", 2.2, "Limited overlap: Python only; primary stack is Java/Spring (1 concept)."),
     crit("experience_depth", 2.4, "1 role, partly relevant."),
     crit("impact", 1.5, "No quantified achievement signals detected."),
     crit("trajectory", 2.0, "1 distinct title; no senior markers."),
     crit("education", 2.8, "Adjacent field; 0 certifications."),
     crit("clarity", 3.0, "Structure complete across 3/4 sections.")],
    "SCORED",
    [{ knockout_id: "work_authorization", knockout_name: "Work authorization", passed: true, justification: "Not determinable from resume — assumed pass; verify with candidate." }]),

  mkCandidate("c4", "Dana Osei", "dana@example.com", "London, UK",
    ["Python", "FastAPI", "Docker"],
    [{ title: "Backend Engineer", organization: "Startup XYZ", highlights: ["Shipped v1 API"] }],
    [{ degree: "BSc", field_of_study: "Mathematics", institution: "City University" }],
    [],
    [],
    "KNOCKED_OUT",
    [{ knockout_id: "work_authorization", knockout_name: "Work authorization", passed: false, justification: "Required certification/term not found and role is US-based; flagged for human verification." }]),
];

const auditByCandidate = {};
candidates.forEach((c) => {
  auditByCandidate[c.id] = [
    { id: c.id + "-a2", actor: "system", action: `AUTO_SCORE:${c.score.status}`, reason: "Automated scoring run", timestamp: new Date().toISOString() },
    { id: c.id + "-a1", actor: "system", action: "INGEST_CANDIDATE", reason: "Resume uploaded and normalized", timestamp: new Date().toISOString() },
  ];
});

export const store = { job, candidates, auditByCandidate, jobAudit: [
  { id: "j2", actor: "user", action: "UPDATE_RUBRIC", reason: "Rubric edited", timestamp: new Date().toISOString() },
  { id: "j1", actor: "user", action: "CREATE_JOB", reason: "Job created", timestamp: new Date().toISOString() },
] };

function recompute(score) {
  score.total = total(score.per_criterion);
  score.tier = tierOf(score.total);
}

export const demoApi = {
  health: async () => ({ status: "ok", engine_version: "1.0.0 (demo)", scoring_backend: "mock", normalizer: "heuristic" }),
  listJobs: async () => [{ ...store.job }],
  getJob: async () => ({ ...store.job, candidate_count: store.candidates.length }),
  defaultRubric: async () => ({ rubric: store.job.rubric, tier_thresholds: store.job.tier_thresholds }),
  createJob: async () => ({ ...store.job }),
  updateRubric: async (_id, body) => { store.job.rubric = body.rubric; if (body.tier_thresholds) store.job.tier_thresholds = body.tier_thresholds; return store.job; },
  uploadResumes: async () => ({ id: "batch-demo", job_id: "job-1", status: "DONE", total: 0, processed: 0, failed: 0 }),
  batchStatus: async () => ({ id: "batch-demo", job_id: "job-1", status: "DONE", total: 0, processed: 0, failed: 0 }),
  listCandidates: async (_id, params = {}) => {
    let items = store.candidates.map((c) => ({
      id: c.id, source: "UPLOAD", name: c.candidate.contact.full_name, source_ref_id: c.candidate.source_ref_id,
      status: c.score.status, total: c.score.total, tier: c.score.tier, engine_version: c.score.engine_version,
    }));
    if (params.tier) items = items.filter((x) => x.tier === params.tier);
    if (params.status) items = items.filter((x) => x.status === params.status);
    if (params.min_score) items = items.filter((x) => x.total >= Number(params.min_score));
    if (params.search) items = items.filter((x) => (x.name || "").toLowerCase().includes(params.search.toLowerCase()));
    if (params.sort === "total_asc") items.sort((a, b) => a.total - b.total);
    else if (params.sort === "name") items.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
    else items.sort((a, b) => (a.status !== "KNOCKED_OUT" ? 1 : 0) - (b.status !== "KNOCKED_OUT" ? 1 : 0) || b.total - a.total);
    return { job_id: "job-1", count: items.length, candidates: items };
  },
  getCandidate: async (id) => structuredClone(store.candidates.find((c) => c.id === id)),
  rescore: async (id) => store.candidates.find((c) => c.id === id).score,
  override: async (id, body) => {
    const c = store.candidates.find((x) => x.id === id);
    const t = c.score.per_criterion.find((p) => p.criterion_id === body.criterion_id);
    if (!t.overridden) t.original_raw_score = t.raw_score;
    t.raw_score = body.new_raw_score; t.weighted_score = Math.round((body.new_raw_score / 5) * t.weight * 100) / 100;
    t.overridden = true; t.justification = `[Manual override] ${body.reason}`;
    recompute(c.score);
    store.auditByCandidate[id].unshift({ id: id + Date.now(), actor: "user", action: "OVERRIDE_SCORE", reason: body.reason, timestamp: new Date().toISOString() });
    return c.score;
  },
  regenQuestions: async (id) => {
    const c = store.candidates.find((x) => x.id === id);
    return { interview_questions: c.score.interview_questions };
  },
  saveQuestions: async (id, questions) => {
    const c = store.candidates.find((x) => x.id === id);
    c.score.interview_questions = questions;
    store.auditByCandidate[id].unshift({ id: id + Date.now(), actor: "user", action: "EDIT_INTERVIEW_QUESTIONS", reason: "Manager edited interview questions", timestamp: new Date().toISOString() });
    return { interview_questions: questions };
  },
  calibrate: async (id, body) => {
    store.auditByCandidate[id].unshift({ id: id + Date.now(), actor: "user", action: "RECORD_CALIBRATION", reason: body.notes || "Outcome recorded", timestamp: new Date().toISOString() });
    return { ok: true, outcome: body.outcome };
  },
  candidateAudit: async (id) => ({ candidate_id: id, entries: store.auditByCandidate[id] || [] }),
  jobAudit: async () => ({ job_id: "job-1", entries: store.jobAudit }),
  exportUrl: () => "javascript:alert('Export is live in the real app (CSV/JSON). Disabled in this static preview.')",
  fileUrl: () => "javascript:alert('Original file download is live in the real app. Disabled in this static preview.')",
};
