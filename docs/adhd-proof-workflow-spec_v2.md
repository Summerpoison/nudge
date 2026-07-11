# ADHD-Proof Workflow System — Design Spec

**Author:** Summer + Claude (brainstorming session, June 2026)
**Reviewed by:** ChatGPT (two independent passes) with Summer's corrections
**Status:** Design concept — not yet implemented
**Purpose:** A personal productivity system designed around ADHD-specific failure modes, usable across freelance, employment, and study contexts without requiring access to company-sensitive data.

---

## Core Design Principles

- **Proof over self-report.** The system never asks "did you do it?" — it asks "show me the thing." Any accountability mechanism that relies on honest yes/no answers will be defeated by avoidance.
- **The system does the emotional labor.** Drafting uncomfortable messages (extensions, help requests, follow-ups) is the highest-leverage intervention. The human only has to hit send.
- **Reduce decision latency.** The real danger isn't that work isn't happening — it's that uncertainty remains unresolved too long. The system's mission: *reduce the time between detecting friction and taking the next socially relevant action.* Need help? Ask. Need an extension? Ask. Need clarification? Ask. The system shortens every one of those gaps.
- **Relational anchoring.** Checkpoints are tied to real people and real events (meetings, presentations, handoffs) rather than abstract percentages. Work done for a specific person has higher activation energy than work done into the void.
- **Messy input, clean output.** Every input surface tolerates imperfect, rushed, or incomplete data. Cleanup happens at export time, not entry time.
- **Infer metadata, don't ask for it.** The user provides proof, priorities, and decisions. Everything else (task type, confidence levels, risk indicators) should be inferred from behavioral signals or timestamps. Every manual field that could be inferred is friction that accumulates until you stop using the system.
- **Buffer by default.** Time estimates and deadlines are automatically padded. The human can override, but the safe option is the default.
- **No company data in the AI layer.** Task descriptions can be vague ("Client A deliverable") and the system still works. Sensitive details stay in company tools; this system manages the *structure* around the work.
- **Build for the spiral, not the good days.** Everything is fine when things are on track. The system earns its value in the first 48 hours after a deadline slips.
- **Respect the ADHD energy inversion.** Activation cost is inversely proportional to task complexity, not proportional. Renaming a file is a high-energy task; designing a complex system is a low-energy task. Any feature that assumes "simple = easy" will be wrong and eventually ignored.

---

## Module 1: Checkpoint & Escalation System

### Problem it solves
The docassemble pattern: scope creeps invisibly, the gap between expectations and reality grows, trust erodes, micromanagement begins, and by the time the crisis is visible it's too late to recover gracefully.

### How it works

**At project kickoff**, each deliverable gets:

| Field | Description |
|---|---|
| Task name | Can be vague for security ("Client A onboarding doc") |
| External deadline | The real one communicated to stakeholders |
| Buffer deadline | Auto-calculated at 70% of available time (overridable) |
| Checkpoint 1 (default 50%) | Date for first proof-of-progress artifact |
| Checkpoint 2 (default 75%) | Date for second artifact / fake deadline |
| Stakeholder contact | Who to email if timeline needs adjusting |
| Team scope question | "Is this scoped for one person?" — forced yes/no at kickoff |

**Checkpoints snap to real events.** If there's a meeting on Wednesday where the work would naturally come up, move the checkpoint there instead of an arbitrary calendar percentage. The meeting is the accountability moment.

**At each checkpoint**, the system requires an artifact. Not a checkbox.

### Acceptable artifacts (in order of strength)

| Level | Examples |
|---|---|
| **Strong** | File, draft, commit, screenshot, document link |
| **Medium** | Meeting notes, decision note, annotated outline |
| **Minimal** | Voice note explaining progress, text description of current state |

The system should prefer stronger artifacts but never block on them. The worst outcome is the user spending 20 minutes wondering "does this count?" and avoiding the checkpoint entirely. Anything beats nothing.

Two types of artifact serve different purposes:
- **Proof artifact** — demonstrates progress was made (a draft, a file, a screenshot)
- **Context artifact** — preserves state for future-you or for handoff ("here's where I am and what's next")

Both count. A context artifact at a checkpoint is still evidence of engagement.

### Blocker Triage (decision menu, not open-ended)

If no artifact is submitted by end-of-day at a checkpoint:

> *What's the next physical action on this? Pick one:*
>
> **A. I know what to do, I just haven't started** → Avoidance. System suggests a 25-minute focused sprint right now. Breaks the task into the smallest possible next step.
>
> **B. I'm stuck on a specific question** → System drafts a help-request message to the relevant person. You edit and send.
>
> **C. I'm waiting on someone else** → System drafts a follow-up nudge to that person. Task stays visible — "waiting" is still active because it may need a reminder. Tasks never hide.
>
> **D. The scope changed and the deadline doesn't fit** → System drafts an extension/renegotiation email to the stakeholder. Includes what IS done and a revised estimate.

The point: you pick from a menu (low executive function cost), and the system produces the *draft of the uncomfortable message* so you only have to hit send.

### Assumption Review (at every checkpoint)

Generalized from scope-change detection. At each checkpoint, the system prompts a quick review — not of the work, but of the assumptions the plan was built on:

- Is the deadline still realistic?
- Is the scope still realistic?
- Is the ownership still realistic? (Still one person? Still the right person?)
- Is the estimate still realistic?

The core issue isn't any single assumption going wrong — it's assumptions becoming outdated without anyone noticing. The checkpoint forces a moment of "is this still true?"

### Escalation Levels

Not every missed checkpoint is the same severity. The system should behave differently depending on how deep the problem is:

| Level | Signal | System behavior |
|---|---|---|
| **1 — Not started** | Checkpoint approaching, no activity | Blocker triage. "What's the next physical action?" |
| **2 — Blocked** | Triage answer is B or C | Draft help/follow-up message. Track resolution. |
| **3 — Deadline risk** | 75% checkpoint missed, or buffer deadline passed | Draft extension email. Force assumption review. |
| **4 — Recovery mode** | Triggers Panic Mode (see Module 5) | System switches from productivity to damage control. |

---

## Module 2: Task Prep for Trivial Tasks

### Problem it solves
Activation cost is inversely proportional to task complexity. Renaming a field in a file is 5 minutes of work wrapped in 70 minutes of executive function overhead: finding the file, remembering what to change, context-switching, mental preparation.

### How it works

When a trivial task arrives (and you still have the context loaded), you capture a **future-you instruction manual**:

```
TASK: Fix typo in client proposal
FILE: [path or location description]
EXACT CHANGE: Page 3, second paragraph, "Antragstellung" → "Antragsstellung"
SEND TO: [person], via email
```

This can be done by:
- Writing it yourself in the tracker
- Pasting the request to Claude with context → Claude writes the micro-instructions
- Voice note that gets transcribed into steps

The key: capture happens at the moment of *receiving* the task, not at the moment of *doing* it. Present-you writes instructions for future-you who has lost all context.

### Batching
Trivial tasks accumulate and get a dedicated time block (e.g., Friday afternoon "admin sweep"). The block has a checklist of pre-written micro-instructions. Each one is a 5-minute follow-the-steps exercise, not a 75-minute reconstruction project.

---

## Module 3: Personal Time Tracker

### Problem it solves
Timesheets are fine when maintained in real time, catastrophic when reconstructed from memory days later. Company time-tracking tools are often rigid and create anxiety when entries need editing.

### How it works

**A personal timer, separate from the company system.** The company timesheet is the clean export; this is the messy working copy.

Core interactions:
- **Quick note + start**: Type "presentation XYZ" and hit start
- **Switch**: Stop current task, start a new one in one action
- **Pause/resume**: For breaks
- **Manual entry**: Add a block with start/end time after the fact
- **"Forgot to switch" recovery**: If a timer has been running suspiciously long (e.g., 3+ hours), prompt on next interaction: "Was that really 3.5 hours, or did you switch earlier?" Allow splitting the block retroactively

**Auto-rules for common patterns:**
- Calendar meetings auto-generate time blocks (imported or manually noted)
- Configurable prep/debrief buffer per meeting type (e.g., +15min before client calls)
- Lunch break auto-detected or defaulted if no activity for 45+ minutes

**Weekly export:** End of week, the system generates a clean timesheet in whatever format the company uses (15-minute blocks with project + description). You review and transfer to the official system. Adjustments happen here, invisibly, so the official record is clean on first entry.

### Data model per time block

| Field | Description |
|---|---|
| Start time | Timestamp |
| End time | Timestamp |
| Task/project label | Short description, can be vague |
| Source | Timer / manual / calendar / auto-rule |
| Edited | Boolean — for your own awareness, not visible in export |
| Confidence | Auto-inferred: "high" if tracked live, "medium" if entered same day, "low" if reconstructed later. Derived from timestamp comparison — never a manual field. Used to weight calibration data (reconstructed entries are less reliable for estimate accuracy). |

---

## Module 4: Weekly Review Loop

### Problem it solves
Without a regular aggregation point, commitments live in scattered emails, chat messages, calendar events, and memory. The weekly review makes the invisible visible and forces a prioritization decision.

### How it works

**Monday morning email** (or notification — whatever channel you actually check):
- Lists all open tasks with their checkpoint dates and status
- Highlights anything overdue or approaching a checkpoint
- Shows the week's calendar commitments
- Flags any tasks that have been sitting with no artifact for more than one cycle

**You reply with your top 3 priorities for the week.** This is the executive function moment — not reading, but *choosing*. The system doesn't let you say "all of them."

**Those 3 get time-blocked in your calendar** (manually or auto-scheduled if calendar integration is available). Each block includes the micro-instructions or current status so you don't have to reconstruct context when the block arrives.

**Wednesday check-in email:**
- Shows the 3 committed tasks
- For each: "Show artifact" / "I'm blocked (→ triage)" / "Pushed to later this week"
- Escalation triggers only when no interaction **and** a checkpoint or deadline is approaching. No interaction on a task that's comfortably ahead of schedule doesn't generate noise.

**Friday summary:**
- What got done (with artifacts as evidence)
- What rolled over (auto-added to next Monday's list)
- Time tracker summary for the week (ready to export to company timesheet)
- Estimate accuracy: predicted vs. actual hours per task (builds calibration data over time)

---

## Module 5: Panic Mode

### Problem it solves
When a situation has already passed the point of recovery through normal productivity, the system should stop optimizing for output and start optimizing for damage control. Most productivity systems keep pretending deep work is realistic when the actual need is triage.

### Triggers (any of these)
- Deadline within 48 hours and no artifact exists
- Progress significantly below expected threshold at 75% checkpoint
- Estimate exceeded by a large margin with deadline still approaching
- **User manually activates** — sometimes you know it's a crisis before the system does

### What changes

The system stops showing the normal task management interface and switches to four questions:

1. **What is the minimum viable outcome?** Not "how do I finish everything" — "what can I actually ship?"
2. **Who needs to know?** List the stakeholders who are expecting something.
3. **What gets cut?** Explicitly name what's being dropped or deferred.
4. **What message needs sending today?** System drafts the emergency communication — not an extension request (that was Level 3), but a "here's the situation, here's what I can deliver, here's what I need" message. An SOS, not a negotiation.

### Design notes
- Panic mode is not a failure state. It's an acknowledgment that the situation has changed and the appropriate response is damage control, not productivity.
- The emergency draft should include what IS done (proof artifacts from earlier checkpoints) so the message isn't just "I'm behind" — it's "here's where things stand and here's my plan."
- Exiting panic mode requires either: the deadline passes, the task is completed, or the user explicitly deactivates it.

---

## Cross-Cutting: Estimate Calibration

Every task gets a "how long do I think this will take" entry at creation. When marked complete, actual duration is logged. Over time this produces a personal calibration ratio (e.g., "you consistently underestimate by 40%").

This data serves two purposes:
1. **Self-awareness**: Concrete evidence for pushing back on overpromising ("my data shows tasks like this take me 1.4x what I estimate")
2. **Automatic buffer adjustment**: The system can adjust the 70% buffer based on your actual calibration ratio rather than a fixed default

Note: calibration data is weighted by time-tracker confidence (see Module 3). Entries reconstructed days later are less reliable than live-tracked entries and should have less influence on the ratio.

---

## Implementation Notes (for when the time comes)

### What to build first
1. **Time tracker** — most universally useful, works in any context (study, employment, freelance), and produces immediate value via timesheet export. Good candidate for a StudyTracker-style standalone tool.
2. **Task prep micro-instructions** — zero infrastructure needed, can start as a habit with Claude in chat before any tool exists.
3. **Weekly review loop** — needs the task list to exist first, but the email/notification layer is a standard cron job.
4. **Checkpoint system** — most complex, most valuable for project work specifically. Build when freelancing or project-based employment begins.
5. **Panic mode** — implement alongside or shortly after the checkpoint system. It's the checkpoint system's emergency exit.

### Tech considerations
- **No company data through third-party AI.** Task labels stay vague. The intelligence layer handles structure and scheduling, not content.
- **Local-first where possible.** Markdown files, local scripts, personal calendar. Reduces dependency on external services.
- **Google Apps Script** as a potential host for the email/calendar integration (free, lives in personal Google account, native Gmail + Calendar access).
- **Claude API** for the intelligence layer (blocker triage drafting, timesheet cleanup, weekly summary generation) if/when budget allows.
- **StudyTracker as a proven pattern.** The UI principles that work there (clean overview, side-by-side context) should carry over.

### The "building is more fun than using" safeguard
- Build one module at a time. Don't start Module 2 until Module 1 has been in daily use for 2+ weeks.
- Each module must be usable within one build session. If it needs a second session to become functional, the scope is too big.
- The spec exists so future-you doesn't re-derive the design from scratch (which would be the fun part and therefore the trap).

---

## Parked Ideas (not in scope, revisit later)

### Task classification / motivation tagging
The idea: tag tasks with type (routine / semi-regular / exception-positive / exception-negative) or a "how do I feel about this task" marker. Could produce interesting data about which tasks stall and why.

**Why it's parked:** At the current integration level (no deep system access), the system can't observe behavioral patterns between checkpoints. Classification would be a manual field with no current consumer — the system doesn't do anything different based on it. Interesting analytically but premature. Revisit only if the system ever accumulates enough historical data to infer patterns, or if deeper integration makes behavioral signals visible.

### Staleness detection
The idea: track "last interaction" per task and alert if untouched for N days.

**Why it's parked:** The 50% checkpoint already serves this function. Adding a separate staleness threshold creates redundant noise. The checkpoint IS the staleness detection — "if you haven't done anything by now, do it."

### Energy management
The idea: tag tasks by cognitive load so the system can recommend appropriate tasks based on current energy.

**Why it's parked:** Energy in ADHD doesn't map to cognitive complexity. "Boring simple task" is high-energy; "interesting complex task" is low-energy. Any energy model built on neurotypical assumptions will give wrong recommendations. Would need to be inferred from personal historical patterns rather than self-reported, and that requires integration depth we don't have.

---

## Open Questions

- Should the Wednesday check-in have a social/relational component (e.g., accountability buddy gets notified) or is that too high-stakes for a default?
- How does this integrate with whatever project management tool a future employer uses (Jira, Asana, etc.)? Probably as a personal layer on top rather than a replacement.
- Voice input as a primary interface? Lower friction than typing, especially for task capture and status updates.
- What's the right threshold for panic mode auto-triggering? 48 hours is a starting point but may need per-task calibration.
- Should panic mode notify anyone automatically, or only draft messages for the user to send? (Probably the latter — forced sends would create trust issues with the system itself.)
