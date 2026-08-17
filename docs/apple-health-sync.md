# Apple Health Sync

`xf` can ingest Apple Health data from either:

1. Apple's native `export.xml` / `export.zip`
2. A normalized JSON file from an Apple Shortcut or export app

The sync writes normalized YAML into this repo:

```txt
health/apple/summary.yaml              # latest vitals, zones, workout counts
health/apple/daily/YYYY-MM-DD.yaml      # daily metric rollups
logs/apple-health/YYYY-MM-DD-HHMM-*.yaml # workout-level logs
```

## Native Apple Health export

On iPhone:

1. Health app → profile icon → Export All Health Data
2. AirDrop/download the zip to your Mac
3. Run:

```bash
python3 scripts/apple_health_sync.py ~/Downloads/export.zip --days 90
```

Update `profile.yaml` vitals too:

```bash
python3 scripts/apple_health_sync.py ~/Downloads/export.zip --days 90 --write-profile
```

Dry-run summary without writing files:

```bash
python3 scripts/apple_health_sync.py ~/Downloads/export.zip --days 30 --dry-run
```

## Normalized JSON input

For Apple Shortcuts or Health Auto Export transforms, use this shape:

```json
{
  "records": [
    { "type": "resting_hr", "date": "2026-05-03", "value": 68, "unit": "count/min" },
    { "type": "hrv_sdnn", "date": "2026-05-03", "value": 42, "unit": "ms" },
    { "type": "vo2_max", "date": "2026-05-03", "value": 31.2 },
    { "type": "body_mass", "date": "2026-05-03", "value": 70, "unit": "kg" }
  ],
  "workouts": [
    {
      "type": "functional_strength_training",
      "date": "2026-05-03 17:00:00 -0500",
      "duration_min": 55,
      "calories_kcal": 420,
      "avg_hr": 145,
      "max_hr": 178
    }
  ]
}
```

Supported record type aliases:

- `resting_hr`, `restingHeartRate`
- `hrv_sdnn`, `hrv`
- `vo2_max`, `vo2Max`
- `body_mass`, `bodyMass`
- `heart_rate`, `heartRate`

## CrossFit use

Apple Health gives biometrics and workout containers. It does **not** know SugarWOD movement details, Rx/scaled status, loads, rounds, or reps. Treat Apple Health as the biometric layer, then layer CrossFit scores separately under `logs/crossfit/`.

## Notes

- `body_mass` is normalized to pounds for `profile.yaml`.
- Karvonen HR zones use latest synced resting HR and existing `profile.yaml` max HR when available.
- Raw Apple exports are huge/sensitive; keep them out of git.
