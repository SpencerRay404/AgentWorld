# AGENT WORLD — Results Log
**Interpreted findings, behavioral observations, and research conclusions**
*Maintained by: Spence | Started: May 2026*

---

> **Log Protocol**
> Results entries interpret experiment data. Each finding must cite a source: experiment ID, tick range, export file, or checkpoint. Distinguish between **observed** (what happened), **measured** (quantified), and **interpreted** (what it may mean). Speculation is labeled clearly.

---

## How to Read This Log

Each results entry is structured as:

```
## RES-NNN | [Title]
Source: EXP-NNN, ticks X–Y | Export: exports/filename.csv
---
OBSERVED: What the data showed, neutrally stated
MEASURED: Quantified metrics
INTERPRETED: What this suggests for the research questions
OPEN QUESTIONS: What this finding raises
```

---

## Research Questions Tracker

| RQ | Question | Status | Best Evidence So Far |
|---|---|---|---|
| RQ1 | Do agents develop consistent behavioral patterns? | Open | — |
| RQ2 | Does population profit stabilize, grow, or degrade? | Open | — |
| RQ3 | What work/rest/play ratio emerges vs. prescribed? | Open | — |
| RQ4 | Do high-risk agents outperform over long horizons? | Open | — |
| RQ5 | Can the system self-sustain without parameter adjustment? | Open | — |
| RQ6 | What failure modes appear unsupervised vs. supervised? | Open | — |

---

## Findings

---

## RES-001 | Phase 1 System Validated — Near-Equal Distribution, Healthy Economy
Source: EXP-001, ticks 1–100, 10 cycles | In-memory run, config defaults

---

**OBSERVED:** All 8 agents spawned, ran through work/rest/play cycles, and accumulated balance over 100 ticks. The maintenance layer detected and responded to 9 STUCK health events. One agent (Drift) was terminated by the recovery manager after exceeding max_recoveries. No FROZEN, OVERDRAINED, or NEGATIVE_BALANCE events occurred. CSV export produced valid output.

**MEASURED:**
- Population total profit: $1,295.00 across 10 pay cycles
- Mean earnings per agent: $161.88 (std $22.77, Gini 0.0787)
- Earnings range: $130–$205 (Drift, terminated, earned the most before failing)
- Work/rest/play ratios: ~35% / ~42% / ~23% (population average)
- Fatigue indexes: 0.003–0.036 (very low — agents are not over-exploited)
- Efficiency scores: 0.42–0.45 earn/energy-unit (consistent across roles)
- Health events: 9 total, all STUCK; 0 hard system failures

**INTERPRETED:**
- The Phase 1 stack functions correctly end-to-end. Agents earn, rest, play, and are maintained.
- The Gini of 0.0787 is very low — essentially equal earnings across agents at 100 ticks. This is expected given the homogeneous job structure; Phase 2 job differentiation should widen this.
- The highest earner (Drift, $205) was also the one terminated — suggests that aggressive work behavior can maximize short-term earnings at the cost of getting stuck, a real trade-off.
- The STUCK pattern (agents stuck in RESTING as well as WORKING) suggests the scheduler's rest/play logic may hold agents in rest longer than necessary, especially for agents with moderate energy. Worth investigating in Phase 2.
- Fatigue indexes are very low, suggesting the current energy parameters leave agents well below overexertion. This is intentional for Phase 1 stability, but Phase 2 should test tighter energy curves.

**OPEN QUESTIONS:**
- Why was Drift consistently stuck vs. other agents? Is this a role-specific trait or scheduler edge case?
- Will Gini widen meaningfully with a larger population (10–20 agents) or more cycles?
- Do STUCK events in RESTING indicate that rest → work transitions are too conservative?

---

## Phase Summaries

### Phase 1 Summary
**Status:** Infrastructure validated (EXP-001 complete); GUI (1.6) implementation in progress

Key infrastructure validated:
- [x] Agent lifecycle (spawn → active → terminated) operates without data loss — confirmed EXP-001
- [x] Ledger accuracy confirmed — $1295 population total matches expected range
- [x] Health monitor fires and recovery manager terminates agents that exceed max_recoveries
- [ ] GUI latency acceptable at 8 agents — EXP-002 (GUI live run) pending

Notable observations:
- Drift paradox: highest earner ($205) terminated due to STUCK pattern — see RES-001
- STUCK events occur in both WORKING and RESTING states — scheduler rest-exit logic worth tuning
- Near-equal earnings distribution (Gini 0.0787) expected to widen with Phase 2 job differentiation

### Phase 2 Summary
**Status:** Pending

### Phase 3 Summary
**Status:** Pending

---

## Behavioral Taxonomy

*As patterns emerge, we'll catalog agent behavioral archetypes here.*

| Archetype Name | Description | First Observed | Frequency |
|---|---|---|---|
| — | — | — | — |

---

## Economic Findings

*Quantitative results from ledger and KPI exports.*

| Metric | Phase 1 | Phase 2 | Phase 3 (Week) | Phase 3 (Month) |
|---|---|---|---|---|
| Avg earnings/agent/cycle | — | — | — | — |
| Population Gini coefficient | — | — | — | — |
| Top earner avg efficiency | — | — | — | — |
| System self-sustain ratio | — | — | — | — |

---

## Publication Notes

*Notes toward eventual write-up or sharing.*

- Target audience: AI researchers, simulation researchers, applied ML practitioners
- Format: Technical blog post (Phase 3 complete) + open GitHub with full reproducibility instructions
- Key narrative: Can you build a closed AI economy from scratch and observe emergent behavior at the agent level?

---

*This log is the interpretive layer above EXPERIMENT_LOG.md. Raw data lives in exports/. Findings here drive research conclusions.*
