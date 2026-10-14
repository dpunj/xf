# xf

Personal fitness data — PRs, training logs, curated reference material.
Structured for AI-assisted coaching and analysis.

## Structure

```
prs.yaml        # current bests by domain/movement (rollup)
logs/crossfit/  # one YAML per session (history)
profile.yaml    # athlete context, current program
references/     # distilled training knowledge from elite sources
```

## Usage

Open this repo in an AI agent (Amp, etc.) — AGENTS.md teaches it how to be your fitness companion.

## CrossFit log

Jot sessions in the Apple Note **XF**, then ask the agent to "sync xf". It reads the note with
`scripts/read_xf_note.sh` and writes `logs/crossfit/YYYY-MM-DD.yaml`. See AGENTS.md.

## Apple Health sync

Import Apple Health export data into normalized YAML:

```bash
python3 scripts/apple_health_sync.py ~/Downloads/export.zip --days 90
```

Also update `profile.yaml` vitals:

```bash
python3 scripts/apple_health_sync.py ~/Downloads/export.zip --days 90 --write-profile
```

See `docs/apple-health-sync.md` for the full workflow and JSON schema.
