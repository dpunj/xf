import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apple_health_sync.py"


class AppleHealthSyncTests(unittest.TestCase):
    def test_xml_export_writes_summary_logs_and_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            export = tmp_path / "export.xml"
            profile = tmp_path / "profile.yaml"
            export.write_text(sample_export_xml())
            profile.write_text(sample_profile())

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    str(export),
                    "--out",
                    str(tmp_path),
                    "--profile",
                    "profile.yaml",
                    "--since",
                    "2026-05-01",
                    "--write-profile",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Synced 5 samples and 1 workouts", result.stdout)
            summary = (tmp_path / "health/apple/summary.yaml").read_text()
            self.assertIn("resting_hr:", summary)
            self.assertIn("value: 70.0", summary)
            self.assertIn("karvonen_zones:", summary)
            self.assertIn("functional_strength_training: 1", summary)

            daily = (tmp_path / "health/apple/daily/2026-05-02.yaml").read_text()
            self.assertIn("hrv_sdnn:", daily)
            self.assertIn("avg: 42.0", daily)

            workout_logs = list((tmp_path / "logs/apple-health").glob("*.yaml"))
            self.assertEqual(len(workout_logs), 1)
            self.assertIn("avg_hr: 145.0", workout_logs[0].read_text())

            updated = profile.read_text()
            self.assertIn("resting_hr: { value: 70.0", updated)
            self.assertIn("hrv_sdnn: { value: 42.0", updated)
            self.assertIn("weight: { value: 154.3", updated)

    def test_normalized_json_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            payload = tmp_path / "health.json"
            payload.write_text(
                '{"records":[{"type":"resting_hr","date":"2026-05-03","value":68}],'
                '"workouts":[{"type":"running","date":"2026-05-03","duration_min":30,"distance_mi":3.1}]}'
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(payload), "--out", str(tmp_path), "--dry-run"],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("resting_hr:", result.stdout)
            self.assertIn("running: 1", result.stdout)
            self.assertFalse((tmp_path / "health").exists())


def sample_export_xml() -> str:
    return textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
          <Record type="HKQuantityTypeIdentifierRestingHeartRate" sourceName="Apple Watch" unit="count/min" creationDate="2026-05-02 08:00:00 -0500" startDate="2026-05-02 08:00:00 -0500" endDate="2026-05-02 08:00:00 -0500" value="70"/>
          <Record type="HKQuantityTypeIdentifierHeartRateVariabilitySDNN" sourceName="Apple Watch" unit="ms" creationDate="2026-05-02 08:00:00 -0500" startDate="2026-05-02 08:00:00 -0500" endDate="2026-05-02 08:00:00 -0500" value="42"/>
          <Record type="HKQuantityTypeIdentifierVO2Max" sourceName="Apple Watch" unit="mL/min·kg" creationDate="2026-05-02 09:00:00 -0500" startDate="2026-05-02 09:00:00 -0500" endDate="2026-05-02 09:00:00 -0500" value="31.2"/>
          <Record type="HKQuantityTypeIdentifierBodyMass" sourceName="Health" unit="kg" creationDate="2026-05-02 09:00:00 -0500" startDate="2026-05-02 09:00:00 -0500" endDate="2026-05-02 09:00:00 -0500" value="70"/>
          <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" unit="count/min" creationDate="2026-05-02 10:00:00 -0500" startDate="2026-05-02 10:00:00 -0500" endDate="2026-05-02 10:00:00 -0500" value="188"/>
          <Workout workoutActivityType="HKWorkoutActivityTypeFunctionalStrengthTraining" sourceName="Apple Watch" duration="55" durationUnit="min" totalEnergyBurned="420" totalEnergyBurnedUnit="kcal" startDate="2026-05-02 17:00:00 -0500" endDate="2026-05-02 17:55:00 -0500">
            <WorkoutStatistics type="HKQuantityTypeIdentifierHeartRate" average="145" maximum="178" unit="count/min"/>
          </Workout>
        </HealthData>
        """
    )


def sample_profile() -> str:
    return textwrap.dedent(
        """\
        name: Divesh
        weight: { value: 150, unit: lb, note: "approximate" }

        vitals:
          resting_hr: { value: 82, unit: bpm, date: "2026-03-23" }
          max_hr: { value: 201, unit: bpm, source: "Apple Watch" }
          hrr: { value: 119, unit: bpm, note: "max_hr - resting_hr" }
          vo2_max: { value: 30, unit: "mL/kg/min", date: "2026-03-23" }

        domains:
          - crossfit
        """
    )


if __name__ == "__main__":
    unittest.main()
