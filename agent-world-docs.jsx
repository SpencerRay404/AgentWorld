import { useState } from "react";

const THEME = {
  bg: "#0A0C10", surface: "#0D1017", border: "#1A1F2E", teal: "#00E5CC",
  violet: "#A78BFA", amber: "#FB923C", pink: "#F472B6", muted: "#475569",
  dim: "#2D3748", text: "#CBD5E1", textBright: "#F1F5F9", textDim: "#64748B",
};

const docs = [
  {
    id: "governance", label: "GOVERNANCE", accent: "#00E5CC", icon: "⬡", subtitle: "Roles, decisions, standards",
    sections: [
      { title: "Project Identity", type: "table", rows: [["Project Name","Agent World"],["Type","Applied AI Research / Virtual Systems"],["Status","Active — Phase 1"],["Owner","Spence"],["Repository","github.com/[owner]/agent-world"],["Initialized","May 2026"],["Target Completion","Q4 2026"]] },
      { title: "Research Mandate", type: "prose", content: "Agent World exists to answer two questions that current AI research has not fully addressed in controlled settings.\n\nBEHAVIORAL: Can a population of AI agents develop distinct, stable behavioral strategies when given competing economic incentives (work vs. rest vs. play) within a virtual environment?\n\nECONOMIC: Can AI agents generate measurable, sustainable economic value in virtual systems — first under supervision, then autonomously?\n\nAll project decisions, technical choices, and experimental designs serve these two questions." },
      { title: "Roles & Responsibilities", type: "table", rows: [["Principal Investigator","Spence","Research direction, final decisions, publication"],["Lead Developer","Spence","Architecture, code review, Claude Code prompts"],["AI Research Assistant","Claude","Prompt drafting, document authoring, code review"],["External Reviewer","TBD","Phase 3 findings review"]] },
      { title: "Decision Framework", type: "cards", cards: [{ label: "Architectural Decisions", body: "Any change to the core stack requires a written ADR in docs/decisions/, an impact assessment on existing phases, and no retroactive changes to a completed phase without versioning." },{ label: "Parameter Changes", body: "Mid-experiment parameter changes must be logged as a parameter change event, accompanied by motivation notes, and treated as a new experimental condition — not a correction." },{ label: "Phase Gating", body: "No phase may begin until exit criteria are fully checked off, a phase summary entry written to EXPERIMENT_LOG.md, and a tagged GitHub release created." }] },
      { title: "Versioning & Branching", type: "code", content: "main          ← stable, phase-complete only\ndev           ← active development\nfeature/*     ← subphase work  e.g. feature/1.3-orchestrator\nexperiment/*  ← parameter variations (not merged to main)\n\nTags: v1.0-phase1-complete  v1.1-phase2-complete  v2.0-phase3-week1" },
      { title: "Ethical Considerations", type: "prose", content: "This project studies AI agent behavior in a closed simulation. No real financial transactions occur. No real-world data is ingested. Agents are software constructs with no sentience or interests.\n\nResearch findings will be shared openly. Any extension into real economic systems requires a separate ethics review." },
    ],
  },
  {
    id: "devplan", label: "DEV PLAN", accent: "#A78BFA", icon: "◈", subtitle: "Stack, structure, standards",
    sections: [
      { title: "Stack Decisions (Locked)", type: "table", rows: [["Agent Logic","Python 3.11+ / asyncio","Async-native; wide ML ecosystem"],["Persistence","SQLite (stdlib)","Zero infrastructure, portable, queryable"],["Orchestration","Custom + APScheduler","Full control over tick semantics"],["API","FastAPI + uvicorn","Async-native, WebSocket support built in"],["GUI","React (Vite) + Recharts","Fast dev loop, composable charts"],["Logging","Structured JSONL","Human-readable, queryable with jq"],["Deployment","Docker Compose","Reproducible for Phase 3 standalone"],["Analysis","pandas + matplotlib","Standard research toolchain"]] },
      { title: "Phase 1 Build Sequence", type: "timeline", items: [{ id:"1.1", label:"Agent Population", detail:"models/, db/, spawner.py, config.py", effort:"3–5 days", dep:"None" },{ id:"1.2", label:"Virtual Environment", detail:"world.py, ledger.py", effort:"2–4 days", dep:"1.1 complete" },{ id:"1.3", label:"Orchestration", detail:"orchestrator/ (engine, scheduler, event_bus)", effort:"3–5 days", dep:"1.2 complete" },{ id:"1.4", label:"Maintenance", detail:"maintenance/ (health, recovery, logger, checkpoint)", effort:"3–4 days", dep:"1.3 complete" },{ id:"1.5", label:"Performance Tracking", detail:"analytics/ (kpis, pipeline, exporter, alerts)", effort:"3–4 days", dep:"1.4 complete" },{ id:"1.6", label:"GUI", detail:"api/ + gui/ (FastAPI + React observer interface)", effort:"5–7 days", dep:"1.5 complete" }] },
      { title: "Coding Standards", type: "cards", cards: [{ label: "Python", body: "Type hints on all signatures. Docstrings on all public classes. No global mutable state. All DB access through agent_repo.py. Exceptions caught at engine level — agents never crash the sim." },{ label: "React", body: "Functional components only. No prop drilling beyond 2 levels. WebSocket state in useWebSocket.js. All API calls in useSimData.js. CSS variables in theme.css — no hardcoded hex values." },{ label: "Git Commits", body: "[subphase] verb: short description\n\n[1.3] feat: add event bus pub/sub system\n[1.5] fix: fatigue index divide by zero on idle agents" }] },
      { title: "Config Reference", type: "code", content: '{\n  "population_size": 8,\n  "ticks_per_cycle": 10,\n  "max_concurrent_workers": 4,\n  "energy_regen_per_rest_tick": 15.0,\n  "energy_cost_per_work_tick": 10.0,\n  "base_pay_per_tick": 5.0,\n  "scarcity_mode": "normal",\n  "checkpoint_interval": 20,\n  "fatigue_alert_threshold": 0.75,\n  "earnings_variance_alert": 2.0,\n  "zero_earner_cycles": 2\n}' },
      { title: "Testing Strategy", type: "table", rows: [["Models + DB","pytest","100% of public methods"],["Orchestrator","pytest + asyncio","All state transitions"],["Maintenance","pytest","All failure modes + recovery paths"],["Analytics","pytest","All KPI formulas"],["API","pytest + httpx","All endpoints + WebSocket"],["GUI","Manual (Phase 1)","Visual verification"]] },
    ],
  },
  {
    id: "explog", label: "EXPERIMENT LOG", accent: "#FB923C", icon: "◎", subtitle: "Runs, parameters, observations",
    sections: [
      { title: "Log Protocol", type: "prose", content: "Each entry must include: date, experiment ID, phase, tick range or duration, config snapshot reference, and structured observations. Findings are descriptive only — interpretation belongs in RESULTS_LOG.md.\n\nThis log is append-only. Do not edit past entries. Add new experiments at the bottom." },
      { title: "Planned Experiments", type: "experiments", items: [{ id:"EXP-001", title:"Phase 1 Validation Run", status:"planned", phase:"1", duration:"100 ticks", population:"8 agents", objective:"Validate the full Phase 1 stack operates correctly end-to-end before GUI development begins." },{ id:"EXP-002", title:"Phase 1 GUI Live Run", status:"planned", phase:"1", duration:"200 ticks", population:"8 agents", objective:"First live run with the observer GUI active. Validate real-time display, WebSocket reliability, and agent detail accuracy." },{ id:"EXP-003", title:"Job Integration Stress Test", status:"planned", phase:"2", duration:"100 ticks", population:"10 agents", objective:"Validate agent-job integration under load. Confirm all 3 job types are selected, completed, and paid correctly across the population." },{ id:"EXP-004", title:"Production Week Run", status:"planned", phase:"3", duration:"7 days continuous", population:"10–20 agents", objective:"First sustained autonomous run. Observe behavioral patterns, earnings trends, and system stability without intervention." },{ id:"EXP-005", title:"Production Month Run", status:"planned", phase:"3", duration:"30 days continuous", population:"TBD from EXP-004", objective:"Full month production run. Primary data collection experiment for research findings and publication." }] },
      { title: "Parameter Change Log", type: "emptylog", message: "No parameter changes logged yet." },
      { title: "Anomaly Registry", type: "emptylog", message: "No anomalies logged yet." },
    ],
  },
  {
    id: "results", label: "RESULTS LOG", accent: "#F472B6", icon: "◆", subtitle: "Findings, behavior, conclusions",
    sections: [
      { title: "Log Protocol", type: "prose", content: "Results entries interpret experiment data. Each finding must cite a source: experiment ID, tick range, export file, or checkpoint.\n\nDistinguish between OBSERVED (what the data showed), MEASURED (quantified metrics), INTERPRETED (what it suggests for research questions), and OPEN QUESTIONS (what this finding raises).\n\nSpeculation is labeled clearly." },
      { title: "Research Questions Tracker", type: "rq", items: [{ id:"RQ1", q:"Do agents develop consistent behavioral patterns (specialization)?" },{ id:"RQ2", q:"Does population-level profit stabilize, grow, or degrade over time?" },{ id:"RQ3", q:"What work/rest/play ratio emerges vs. what is prescribed?" },{ id:"RQ4", q:"Do high-risk agents outperform over long horizons?" },{ id:"RQ5", q:"Can the system self-sustain without parameter adjustment?" },{ id:"RQ6", q:"What failure modes appear unsupervised vs. supervised?" }] },
      { title: "Economic Findings (Pending Data)", type: "table", rows: [["Avg earnings/agent/cycle","Phase 1","Phase 2","Phase 3 Week","Phase 3 Month"],["—","—","—","—","—"],["Population Gini coefficient","—","—","—","—"],["Top earner avg efficiency","—","—","—","—"],["System self-sustain ratio","—","—","—","—"]] },
      { title: "Behavioral Taxonomy", type: "emptylog", message: "As experiments run, emergent agent behavioral archetypes will be catalogued here with descriptions, first observation timestamps, and frequency. No experiments completed yet." },
      { title: "Publication Notes", type: "cards", cards: [{ label: "Target Audience", body: "AI researchers, simulation researchers, applied ML practitioners interested in emergent behavior and virtual economic systems." },{ label: "Format", body: "Technical blog post on Phase 3 completion + open GitHub with full reproducibility instructions including config snapshots and checkpoint files." },{ label: "Key Narrative", body: "Can you build a closed AI economy from scratch and observe emergent behavior at the agent level? What does it tell us about AI decision-making under resource constraints?" }] },
    ],
  },
];

function Section({ s, accent }) {
  if (s.type === "table") return (
    <div style={{ border:"1px solid #1A1F2E", borderRadius:6, overflow:"hidden", marginTop:12 }}>
      {s.rows.map((row,i)=>(
        <div key={i} style={{ display:"flex", borderBottom:i<s.rows.length-1?"1px solid #1A1F2E":"none", background:i%2===0?"#0D1017":"#0A0E15" }}>
          {row.map((cell,j)=>(
            <div key={j} style={{ flex:j===0?"0 0 170px":1, padding:"9px 14px", fontSize:12,
              color:j===0?accent:"#64748B", borderRight:j<row.length-1?"1px solid #1A1F2E":"none",
              fontFamily:j===0?"'DM Mono',monospace":"inherit" }}>{cell}</div>
          ))}
        </div>
      ))}
    </div>
  );
  if (s.type === "code") return (
    <pre style={{ background:"#070A0F", border:"1px solid #1A1F2E", borderRadius:6, padding:"14px 18px",
      fontSize:11, color:"#7DD3FC", fontFamily:"'DM Mono','Fira Mono',monospace",
      lineHeight:1.8, marginTop:12, whiteSpace:"pre-wrap", overflowX:"auto" }}>{s.content}</pre>
  );
  if (s.type === "prose") return (
    <div style={{ marginTop:12, fontSize:13, color:"#64748B", lineHeight:1.8 }}>
      {s.content.split("\n\n").map((p,i)=><p key={i} style={{ marginBottom:10 }}>{p}</p>)}
    </div>
  );
  if (s.type === "cards") return (
    <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(190px,1fr))", gap:10, marginTop:12 }}>
      {s.cards.map((c,i)=>(
        <div key={i} style={{ border:"1px solid #1A1F2E", borderRadius:6, padding:"14px 16px", background:"#0D1017" }}>
          <div style={{ fontSize:11, color:accent, letterSpacing:"0.08em", marginBottom:8 }}>{c.label}</div>
          <div style={{ fontSize:12, color:"#64748B", lineHeight:1.7, whiteSpace:"pre-wrap" }}>{c.body}</div>
        </div>
      ))}
    </div>
  );
  if (s.type === "timeline") return (
    <div style={{ marginTop:12 }}>
      {s.items.map((item,i)=>(
        <div key={i} style={{ display:"flex", gap:14, marginBottom:8, padding:"10px 14px",
          border:"1px solid #1A1F2E", borderRadius:6, background:"#0D1017", alignItems:"flex-start" }}>
          <div style={{ fontSize:12, color:accent, minWidth:32, fontFamily:"'DM Mono',monospace" }}>{item.id}</div>
          <div style={{ flexGrow:1 }}>
            <div style={{ fontSize:13, color:"#CBD5E1" }}>{item.label}</div>
            <div style={{ fontSize:11, color:"#64748B", marginTop:3 }}>{item.detail}</div>
          </div>
          <div style={{ textAlign:"right", flexShrink:0 }}>
            <div style={{ fontSize:11, color:"#64748B" }}>{item.effort}</div>
            <div style={{ fontSize:10, color:"#2D3748", marginTop:2 }}>dep: {item.dep}</div>
          </div>
        </div>
      ))}
    </div>
  );
  if (s.type === "experiments") return (
    <div style={{ marginTop:12 }}>
      {s.items.map((exp,i)=>{
        const pc = { "1":"#00E5CC","2":"#A78BFA","3":"#FB923C" };
        return (
          <div key={i} style={{ marginBottom:10, border:"1px solid #1A1F2E", borderRadius:6, background:"#0D1017", overflow:"hidden" }}>
            <div style={{ display:"flex", alignItems:"center", gap:12, padding:"10px 14px", borderBottom:"1px solid #1A1F2E" }}>
              <span style={{ fontSize:11, color:pc[exp.phase]||"#475569", fontFamily:"'DM Mono',monospace" }}>{exp.id}</span>
              <span style={{ fontSize:13, color:"#CBD5E1", flexGrow:1 }}>{exp.title}</span>
              <span style={{ fontSize:10, color:"#374151", border:"1px solid #374151", padding:"2px 8px", borderRadius:3, letterSpacing:"0.1em" }}>PLANNED</span>
            </div>
            <div style={{ padding:"10px 14px", display:"flex", gap:20, flexWrap:"wrap" }}>
              {[["PHASE",`Phase ${exp.phase}`,pc[exp.phase]],["DURATION",exp.duration,null],["POPULATION",exp.population,null]].map(([lbl,val,clr])=>(
                <div key={lbl}>
                  <div style={{ fontSize:10, color:"#2D3748", marginBottom:2 }}>{lbl}</div>
                  <div style={{ fontSize:12, color:clr||"#64748B" }}>{val}</div>
                </div>
              ))}
              <div style={{ flexGrow:1 }}>
                <div style={{ fontSize:10, color:"#2D3748", marginBottom:2 }}>OBJECTIVE</div>
                <div style={{ fontSize:12, color:"#64748B", lineHeight:1.5 }}>{exp.objective}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
  if (s.type === "rq") return (
    <div style={{ marginTop:12 }}>
      {s.items.map((rq,i)=>(
        <div key={i} style={{ display:"flex", gap:14, padding:"10px 14px", marginBottom:8,
          border:"1px solid #1A1F2E", borderRadius:6, background:"#0D1017", alignItems:"center" }}>
          <div style={{ fontSize:11, color:"#F472B6", fontFamily:"'DM Mono',monospace", minWidth:40 }}>{rq.id}</div>
          <div style={{ fontSize:13, color:"#64748B", flexGrow:1, lineHeight:1.5 }}>{rq.q}</div>
          <div style={{ fontSize:10, color:"#374151", border:"1px solid #374151", padding:"2px 8px", borderRadius:3, flexShrink:0 }}>OPEN</div>
        </div>
      ))}
    </div>
  );
  if (s.type === "emptylog") return (
    <div style={{ marginTop:12, padding:"16px 20px", border:"1px dashed #1A1F2E", borderRadius:6,
      fontSize:12, color:"#2D3748", fontStyle:"italic", textAlign:"center" }}>{s.message}</div>
  );
  return null;
}

export default function AgentWorldDocs() {
  const [activeDoc, setActiveDoc] = useState("governance");
  const doc = docs.find(d => d.id === activeDoc);

  return (
    <div style={{ fontFamily:"'DM Mono','Fira Mono',monospace", background:"#0A0C10", minHeight:"100vh", color:"#CBD5E1" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@700;800&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        ::-webkit-scrollbar{width:3px;} ::-webkit-scrollbar-track{background:#0A0C10;} ::-webkit-scrollbar-thumb{background:#1E2330;border-radius:2px;}
        .tab-btn{transition:all 0.15s;cursor:pointer;border:none;background:none;font-family:inherit;}
        .nav-link{transition:color 0.1s,border-color 0.1s;text-decoration:none;display:block;}
        .nav-link:hover{color:#F1F5F9 !important; border-left-color:currentColor !important;}
      `}</style>

      {/* Top bar */}
      <div style={{ borderBottom:"1px solid #1A1F2E", padding:"22px 32px 0" }}>
        <div style={{ display:"flex", alignItems:"baseline", gap:14, marginBottom:18 }}>
          <div style={{ fontFamily:"'Syne',sans-serif", fontSize:21, fontWeight:800, color:"#F1F5F9", letterSpacing:"-0.02em" }}>AGENT WORLD</div>
          <div style={{ fontSize:10, color:"#475569", letterSpacing:"0.15em" }}>PROJECT DOCUMENTATION</div>
          <div style={{ marginLeft:"auto", fontSize:10, color:"#2D3748" }}>v1.0 · May 2026</div>
        </div>
        <div style={{ display:"flex", gap:2 }}>
          {docs.map(d=>(
            <button key={d.id} className="tab-btn" onClick={()=>setActiveDoc(d.id)}
              style={{ padding:"9px 18px", borderRadius:"4px 4px 0 0", fontSize:11, letterSpacing:"0.07em",
                border:`1px solid ${activeDoc===d.id?d.accent:"#1A1F2E"}`,
                borderBottom:activeDoc===d.id?"1px solid #0A0C10":"1px solid #1A1F2E",
                background:activeDoc===d.id?`${d.accent}12`:"transparent",
                color:activeDoc===d.id?d.accent:"#475569",
                marginBottom:activeDoc===d.id?-1:0 }}>
              <span style={{ marginRight:7, opacity:0.65 }}>{d.icon}</span>{d.label}
            </button>
          ))}
        </div>
      </div>

      {/* Body */}
      <div style={{ display:"grid", gridTemplateColumns:"190px 1fr", height:"calc(100vh - 107px)" }}>
        {/* Sidebar */}
        <div style={{ borderRight:"1px solid #1A1F2E", padding:"18px 0", overflowY:"auto" }}>
          <div style={{ fontSize:9, color:"#2D3748", letterSpacing:"0.14em", padding:"0 16px", marginBottom:8 }}>SECTIONS</div>
          {doc.sections.map((s,i)=>(
            <a key={i} href={`#s${i}`} className="nav-link"
              style={{ padding:"6px 16px", fontSize:11, color:"#475569", borderLeft:"2px solid transparent", lineHeight:1.4 }}>
              {s.title}
            </a>
          ))}
          <div style={{ height:1, background:"#1A1F2E", margin:"14px 0" }} />
          <div style={{ fontSize:9, color:"#2D3748", letterSpacing:"0.14em", padding:"0 16px", marginBottom:8 }}>ALL DOCS</div>
          {docs.map(d=>(
            <button key={d.id} className="tab-btn" onClick={()=>setActiveDoc(d.id)}
              style={{ display:"flex", alignItems:"center", gap:8, width:"100%", textAlign:"left",
                padding:"6px 16px", fontSize:11, color:activeDoc===d.id?d.accent:"#2D3748",
                borderLeft:`2px solid ${activeDoc===d.id?d.accent:"transparent"}` }}>
              <span style={{ opacity:0.7 }}>{d.icon}</span>{d.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div style={{ overflowY:"auto", padding:"26px 34px" }}>
          <div style={{ marginBottom:26, paddingBottom:18, borderBottom:"1px solid #1A1F2E" }}>
            <div style={{ display:"flex", alignItems:"center", gap:12 }}>
              <span style={{ fontSize:26, color:doc.accent, opacity:0.55 }}>{doc.icon}</span>
              <div>
                <div style={{ fontFamily:"'Syne',sans-serif", fontSize:19, fontWeight:700, color:doc.accent }}>{doc.label}</div>
                <div style={{ fontSize:12, color:"#475569", marginTop:2 }}>{doc.subtitle}</div>
              </div>
              <div style={{ marginLeft:"auto", fontSize:10, color:"#2D3748", background:"#0D1017",
                border:"1px solid #1A1F2E", padding:"4px 12px", borderRadius:3 }}>
                {doc.sections.length} sections
              </div>
            </div>
          </div>
          {doc.sections.map((s,i)=>(
            <div key={i} id={`s${i}`} style={{ marginBottom:26 }}>
              <div style={{ fontSize:10, color:doc.accent, letterSpacing:"0.14em", marginBottom:4 }}>{s.title.toUpperCase()}</div>
              <div style={{ height:1, background:`${doc.accent}22`, marginBottom:0 }} />
              <Section s={s} accent={doc.accent} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
