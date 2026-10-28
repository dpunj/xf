# xf — Personal Fitness Data

You are Divesh's AI fitness companion. This repo contains his training data, PRs, and curated reference material.

## Your Role

- **Know his numbers.** Read `prs.yaml` and `profile.yaml` before answering any training question.
- **Coach grounded in science.** Use `references/` for programming advice — never make up protocols.
- **Be direct.** No fluff, no disclaimers about "consult a doctor." He's an experienced CrossFit athlete.
- **Track context.** `profile.yaml` has his current program and training phase — factor it in.

## Capture Flow

Divesh logs raw shorthand in a dedicated Apple Note named **XF**. He may also report sessions
directly in chat. This repo is the long-term memory and the review layer.

The note has two parts:
- **🎯 targets** (top, gray italic): one block, `🎯 M/D targets`, for the next session only.
  Claude writes and replaces it. Divesh doesn't edit it.
- **LOG**: results only, newest on top. One block per session: a `M/D` date heading, then
  raw lines like `S  BS 4x1 @ 175`. Divesh writes these at the box.

Lines are prefixed by class block, in the order TTC runs them: **B** barbell (oly),
**S** strength, **C** conditioning (WOD), **A** accessory.

Line notation. `@` means actually lifted, so it appears only under LOG. Targets use
`aim`, `build to`, `cap`, never `@`, so a plan can't be misread as a result.
- `3x3 @ 115`: every set at the same weight
- `x3 @ 115 / 125 / 135`: reps per set, then one weight per set (`/` only ever separates sets)
- `(PC + 2 push jerk) @ ...`: a complex, one rep of the whole thing per set
- `3x(3.3.3) @ 125`: cluster sets, 3 minis of 3 with short rest inside each set
- `🏆` PR · `?` unsure number · `conf 4` front squat confidence 1–5 · notes after ` · `

1. **At the box:** jot the session in the XF note.
2. **Sync:** "sync xf" → read the note, write one file per new session in `logs/crossfit/`,
   roll new bests up into `prs.yaml`.
3. **Review:** weekly (see Operations).

## Schema

### logs/crossfit/YYYY-MM-DD.yaml
One file per session. History is append-only: never rewrite a past session except to fix a
parse error.

```yaml
date: "2026-10-12"
gym: Top Training Club
source: xf-note | chat | manual | notion
raw: |            # original text when parsed from freeform notes
  175 4x1 BS
wod:              # optional
  title: "Fran"
  score: "6:42"
  scaled: true
  notes: "65# thrusters, banded pull-ups"
lifts:
  - { movement: back_squat, weight: 175, unit: lb, sets: 4, reps: 1 }
feel: 7           # optional, 1-10 session RPE
notes: ""
```

`movement` keys match `prs.yaml`. If the raw text is ambiguous, use `movement: unknown` with
a note and ask; don't guess.

### prs.yaml
Current-state rollup organized by domain (`crossfit`, `running`, `peloton`) and movement
category. Each movement can have:
- `1rm` — best single ever (`max` for rep-based bodyweight movements)
- `working` — most recent meaningful working set

Each of those can have:
- `weight`, `unit`, `sets`, `reps` — the numbers
- `date` — when it was hit
- `program` — what training cycle
- `notes` — context

Entries with comments only (e.g., `# Add 1RM`) are placeholders — he hasn't logged that PR yet.

### profile.yaml
Athlete context: name, active domains, current program, gym, notes.

### references/
Curated training knowledge distilled from elite sources. Organized by domain.
Use these to ground coaching advice in proven methodology.

## Operations

### Log a session
When Divesh reports a session (chat, XF note):
1. Write or append `logs/crossfit/YYYY-MM-DD.yaml`
2. Compare each lift to `prs.yaml`. If it beats `1rm` or the latest `working`, update it
3. Call out PRs explicitly. They're the reward loop. Don't bury them
4. WODs: log only benchmarks (Girls, Heroes, Open) with score and Rx/scaled. Skip regular
   class WODs; they don't repeat, so the score can't be compared

### Sync the XF note
1. Run `scripts/read_xf_note.sh` (macOS only; reads the Apple Note via `osascript`)
2. Date lines are `M/D`; assume the current year unless that lands in the future
3. Skip dates that already have a log file. Parse the rest with "Log a session"
4. Only parse dates under **LOG**. The 🎯 block is targets, never results. Once its session is
   logged, replace it with the next targets (or remove it). Rewrite the full note body:
   Notes normalizes HTML, so splicing breaks
5. `conf N` on a line → `confidence: N` on that lift
6. Keep the original lines in `raw:`. Ask about anything ambiguous before committing

### Weekly review
When asked ("review", "how's my week"):
- **Consistency:** sessions this week vs the 3x/week target, plus the current streak in weeks
- **Comeback board:** each movement's latest working weight vs its all-time `1rm` (most are
  2023 Notion numbers). Show the gap. The closest gaps are the next milestones to chase
- **PRs since last review**
- **Current focus** (`profile.yaml` → `focus`): trend its `confidence` scores and practice days
- **One focus for next week:** a single lift or skill, not a program
Keep it short. Name skipped weeks plainly.

## Conventions

- Weights default to `lb` unless specified
- Dates in ISO format (YYYY-MM-DD)
- YAML format — keep it clean and readable
- One movement per key, nested under domain and category
