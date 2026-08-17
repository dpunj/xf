#!/usr/bin/env python3
"""Sync Apple Health exports into the xf fitness repo.

Supports Apple's native export.xml/export.zip plus a small normalized JSON
shape suitable for Apple Shortcuts or Health Auto Export transforms.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


METRIC_TYPES = {
    "HKQuantityTypeIdentifierRestingHeartRate": "resting_hr",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv_sdnn",
    "HKQuantityTypeIdentifierVO2Max": "vo2_max",
    "HKQuantityTypeIdentifierBodyMass": "body_mass",
    "HKQuantityTypeIdentifierHeartRate": "heart_rate",
}

METRIC_UNITS = {
    "resting_hr": "bpm",
    "hrv_sdnn": "ms",
    "vo2_max": "mL/kg/min",
    "body_mass": "lb",
    "heart_rate": "bpm",
}

ZONE_PCTS = {
    "z1": (0.50, 0.60),
    "z2": (0.60, 0.70),
    "z3": (0.70, 0.80),
    "z4": (0.80, 0.90),
    "z5": (0.90, 1.00),
}


@dataclass
class MetricSample:
    metric: str
    value: float
    unit: str
    start: datetime
    source: str = "Apple Health"

    @property
    def date(self) -> str:
        return self.start.date().isoformat()


@dataclass
class Workout:
    workout_type: str
    start: datetime
    end: datetime | None
    duration_min: float | None
    calories_kcal: float | None
    distance_mi: float | None
    avg_hr: float | None
    max_hr: float | None
    source: str = "Apple Health"

    @property
    def slug(self) -> str:
        stamp = self.start.strftime("%Y-%m-%d-%H%M")
        return f"{stamp}-{slugify(self.workout_type)}.yaml"


@dataclass
class HealthData:
    samples: list[MetricSample] = field(default_factory=list)
    workouts: list[Workout] = field(default_factory=list)


class AppleHealthSyncError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Apple Health data into xf")
    parser.add_argument("input", type=Path, help="Apple export.xml/export.zip or normalized JSON")
    parser.add_argument("--out", type=Path, default=Path("."), help="xf repo root")
    parser.add_argument("--profile", type=Path, default=Path("profile.yaml"))
    parser.add_argument("--since", help="Only include samples/workouts on or after YYYY-MM-DD")
    parser.add_argument("--days", type=int, help="Only include the last N days in the export")
    parser.add_argument("--write-profile", action="store_true", help="Update profile.yaml vitals")
    parser.add_argument("--dry-run", action="store_true", help="Print summary only; write nothing")
    return parser.parse_args()


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    cleaned = value.replace("\u202f", " ").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError as exc:
        raise AppleHealthSyncError(f"Could not parse date: {value}") from exc


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def slugify(value: str) -> str:
    stripped = re.sub(r"^HKWorkoutActivityType", "", value)
    snake = re.sub(r"(?<!^)([A-Z])", r"_\1", stripped).lower()
    return re.sub(r"[^a-z0-9]+", "_", snake).strip("_") or "workout"


def normalize_metric_type(raw_type: str | None) -> str | None:
    if not raw_type:
        return None
    aliases = {
        "restingHeartRate": "resting_hr",
        "resting_hr": "resting_hr",
        "hrv": "hrv_sdnn",
        "hrv_sdnn": "hrv_sdnn",
        "vo2Max": "vo2_max",
        "vo2_max": "vo2_max",
        "bodyMass": "body_mass",
        "body_mass": "body_mass",
        "heartRate": "heart_rate",
        "heart_rate": "heart_rate",
    }
    return METRIC_TYPES.get(raw_type) or aliases.get(raw_type)


def normalize_value(metric: str, value: float, unit: str | None) -> float:
    if metric == "body_mass" and unit and unit.lower() in {"kg", "kilogram", "kilograms"}:
        return value * 2.2046226218
    if metric == "body_mass" and unit and unit.lower() in {"st", "stone"}:
        return value * 14
    return value


def normalize_unit(metric: str, unit: str | None) -> str:
    return METRIC_UNITS.get(metric, unit or "")


def parse_health_input(path: Path, since: datetime | None) -> HealthData:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return parse_json_export(path, since)
    if suffix == ".zip":
        return parse_zip_export(path, since)
    return parse_xml_export(path, since)


def parse_zip_export(path: Path, since: datetime | None) -> HealthData:
    with zipfile.ZipFile(path) as archive:
        export_name = next((n for n in archive.namelist() if n.endswith("export.xml")), None)
        if not export_name:
            raise AppleHealthSyncError("Zip did not contain export.xml")
        with archive.open(export_name) as file_obj:
            return parse_xml_stream(file_obj, since)


def parse_xml_export(path: Path, since: datetime | None) -> HealthData:
    with path.open("rb") as file_obj:
        return parse_xml_stream(file_obj, since)


def parse_xml_stream(file_obj: Any, since: datetime | None) -> HealthData:
    data = HealthData()
    root = None
    for event, elem in ET.iterparse(file_obj, events=("start", "end")):
        if root is None and event == "start":
            root = elem
        if event != "end":
            continue
        if elem.tag == "Record":
            add_record(data, elem.attrib, since)
            elem.clear()
            if root is not None:
                root.clear()
        elif elem.tag == "Workout":
            add_workout(data, elem, since)
            elem.clear()
            if root is not None:
                root.clear()
    return data


def add_record(data: HealthData, attrs: dict[str, str], since: datetime | None) -> None:
    metric = normalize_metric_type(attrs.get("type"))
    if not metric:
        return
    start = parse_date(attrs.get("startDate") or attrs.get("creationDate"))
    value = parse_float(attrs.get("value"))
    if not start or value is None or (since and start < since):
        return
    unit = attrs.get("unit")
    normalized = normalize_value(metric, value, unit)
    data.samples.append(MetricSample(metric, normalized, normalize_unit(metric, unit), start, attrs.get("sourceName", "Apple Health")))


def add_workout(data: HealthData, elem: ET.Element, since: datetime | None) -> None:
    start = parse_date(elem.attrib.get("startDate"))
    if not start or (since and start < since):
        return
    duration = parse_float(elem.attrib.get("duration"))
    workout = Workout(
        workout_type=slugify(elem.attrib.get("workoutActivityType", "workout")),
        start=start,
        end=parse_date(elem.attrib.get("endDate")),
        duration_min=duration_to_minutes(duration, elem.attrib.get("durationUnit")),
        calories_kcal=parse_energy(elem),
        distance_mi=parse_distance(elem),
        avg_hr=parse_workout_stat(elem, "HKQuantityTypeIdentifierHeartRate", "average"),
        max_hr=parse_workout_stat(elem, "HKQuantityTypeIdentifierHeartRate", "maximum"),
        source=elem.attrib.get("sourceName", "Apple Health"),
    )
    data.workouts.append(workout)


def duration_to_minutes(value: float | None, unit: str | None) -> float | None:
    if value is None:
        return None
    lowered = (unit or "min").lower()
    if lowered.startswith("sec"):
        return value / 60
    if lowered.startswith("hour") or lowered in {"hr", "h"}:
        return value * 60
    return value


def parse_energy(elem: ET.Element) -> float | None:
    direct = parse_float(elem.attrib.get("totalEnergyBurned"))
    if direct is not None:
        return direct
    return parse_workout_stat(elem, "HKQuantityTypeIdentifierActiveEnergyBurned", "sum")


def parse_distance(elem: ET.Element) -> float | None:
    direct = parse_float(elem.attrib.get("totalDistance"))
    unit = elem.attrib.get("totalDistanceUnit")
    if direct is not None:
        return distance_to_miles(direct, unit)
    for stat in elem.findall("WorkoutStatistics"):
        if stat.attrib.get("type") in {"HKQuantityTypeIdentifierDistanceWalkingRunning", "HKQuantityTypeIdentifierDistanceCycling"}:
            return distance_to_miles(parse_float(stat.attrib.get("sum")), stat.attrib.get("unit"))
    return None


def distance_to_miles(value: float | None, unit: str | None) -> float | None:
    if value is None:
        return None
    lowered = (unit or "mi").lower()
    if lowered in {"km", "kilometer", "kilometers"}:
        return value * 0.62137119
    if lowered in {"m", "meter", "meters"}:
        return value * 0.00062137119
    return value


def parse_workout_stat(elem: ET.Element, stat_type: str, attr: str) -> float | None:
    for stat in elem.findall("WorkoutStatistics"):
        if stat.attrib.get("type") == stat_type:
            return parse_float(stat.attrib.get(attr))
    return None


def parse_json_export(path: Path, since: datetime | None) -> HealthData:
    payload = json.loads(path.read_text())
    records = payload.get("records") or payload.get("metrics") or []
    workouts = payload.get("workouts") or []
    data = HealthData()
    for record in records:
        add_json_record(data, record, since)
    for workout in workouts:
        add_json_workout(data, workout, since)
    return data


def add_json_record(data: HealthData, record: dict[str, Any], since: datetime | None) -> None:
    metric = normalize_metric_type(record.get("type") or record.get("metric"))
    start = parse_date(record.get("startDate") or record.get("date"))
    value = parse_float(record.get("value"))
    if not metric or not start or value is None or (since and start < since):
        return
    unit = record.get("unit")
    data.samples.append(MetricSample(metric, normalize_value(metric, value, unit), normalize_unit(metric, unit), start, record.get("source", "Apple Health")))


def add_json_workout(data: HealthData, workout: dict[str, Any], since: datetime | None) -> None:
    start = parse_date(workout.get("startDate") or workout.get("date"))
    if not start or (since and start < since):
        return
    data.workouts.append(Workout(
        workout_type=slugify(str(workout.get("type") or workout.get("workoutActivityType") or "workout")),
        start=start,
        end=parse_date(workout.get("endDate")),
        duration_min=duration_to_minutes(parse_float(workout.get("duration") or workout.get("duration_min")), workout.get("durationUnit")),
        calories_kcal=parse_float(workout.get("activeEnergy") or workout.get("calories") or workout.get("calories_kcal")),
        distance_mi=distance_to_miles(parse_float(workout.get("distance") or workout.get("distance_mi")), workout.get("distanceUnit")),
        avg_hr=parse_float(workout.get("avgHeartRate") or workout.get("avg_hr")),
        max_hr=parse_float(workout.get("maxHeartRate") or workout.get("max_hr")),
        source=workout.get("source", "Apple Health"),
    ))


def resolve_since(data: HealthData, args: argparse.Namespace) -> datetime | None:
    explicit = parse_date(args.since) if args.since else None
    if explicit or not args.days:
        return explicit
    starts = [s.start for s in data.samples] + [w.start for w in data.workouts]
    if not starts:
        return None
    latest = max(starts)
    return latest.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta_days(args.days - 1)


def timedelta_days(days: int):
    from datetime import timedelta

    return timedelta(days=max(days, 0))


def filter_data(data: HealthData, since: datetime | None) -> HealthData:
    if not since:
        return data
    return HealthData(
        samples=[sample for sample in data.samples if sample.start >= since],
        workouts=[workout for workout in data.workouts if workout.start >= since],
    )


def latest_by_metric(samples: list[MetricSample]) -> dict[str, MetricSample]:
    latest: dict[str, MetricSample] = {}
    for sample in samples:
        if sample.metric == "heart_rate":
            continue
        if sample.metric not in latest or sample.start > latest[sample.metric].start:
            latest[sample.metric] = sample
    return latest


def observed_max_hr(samples: list[MetricSample], workouts: list[Workout]) -> MetricSample | None:
    candidates = [s for s in samples if s.metric == "heart_rate"]
    for workout in workouts:
        if workout.max_hr is not None:
            candidates.append(MetricSample("heart_rate", workout.max_hr, "bpm", workout.start, workout.source))
    if not candidates:
        return None
    return max(candidates, key=lambda sample: sample.value)


def daily_rollups(samples: list[MetricSample]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, dict[str, list[MetricSample]]] = defaultdict(lambda: defaultdict(list))
    for sample in samples:
        buckets[sample.date][sample.metric].append(sample)
    return {day: {metric: rollup_metric(values) for metric, values in metrics.items()} for day, metrics in sorted(buckets.items())}


def rollup_metric(values: list[MetricSample]) -> dict[str, Any]:
    nums = [sample.value for sample in values]
    latest = max(values, key=lambda sample: sample.start)
    return compact({
        "avg": round(sum(nums) / len(nums), 1),
        "min": round(min(nums), 1),
        "max": round(max(nums), 1),
        "latest": round(latest.value, 1),
        "unit": latest.unit,
        "samples": len(values),
        "source": latest.source,
    })


def build_summary(data: HealthData, profile_path: Path, since: datetime | None) -> dict[str, Any]:
    latest = latest_by_metric(data.samples)
    max_hr_sample = observed_max_hr(data.samples, data.workouts)
    resting = latest.get("resting_hr")
    profile_max = extract_profile_number(profile_path, "max_hr")
    max_for_zones = profile_max or (max_hr_sample.value if max_hr_sample else None)
    return compact({
        "synced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window_start": since.date().isoformat() if since else None,
        "latest": {metric: sample_to_dict(sample) for metric, sample in sorted(latest.items())},
        "max_hr_observed": sample_to_dict(max_hr_sample) if max_hr_sample else None,
        "karvonen_zones": karvonen_zones(resting.value if resting else None, max_for_zones),
        "workouts": workout_summary(data.workouts),
    })


def sample_to_dict(sample: MetricSample) -> dict[str, Any]:
    return {
        "value": round(sample.value, 1),
        "unit": sample.unit,
        "date": sample.date,
        "source": sample.source,
    }


def workout_summary(workouts: list[Workout]) -> dict[str, Any]:
    latest = sorted(workouts, key=lambda item: item.start, reverse=True)[:10]
    return {
        "count": len(workouts),
        "by_type": dict(sorted(Counter(w.workout_type for w in workouts).items())),
        "latest": [workout_to_dict(workout) for workout in latest],
    }


def workout_to_dict(workout: Workout) -> dict[str, Any]:
    return compact({
        "date": workout.start.date().isoformat(),
        "start": workout.start.isoformat(),
        "type": workout.workout_type,
        "duration_min": rounded(workout.duration_min),
        "calories_kcal": rounded(workout.calories_kcal),
        "distance_mi": rounded(workout.distance_mi, 2),
        "avg_hr": rounded(workout.avg_hr),
        "max_hr": rounded(workout.max_hr),
        "source": workout.source,
    })


def rounded(value: float | None, digits: int = 1) -> float | None:
    return None if value is None else round(value, digits)


def karvonen_zones(resting_hr: float | None, max_hr: float | None) -> dict[str, Any] | None:
    if resting_hr is None or max_hr is None or max_hr <= resting_hr:
        return None
    reserve = max_hr - resting_hr
    return {
        zone: {
            "low": round(reserve * low + resting_hr),
            "high": round(reserve * high + resting_hr),
            "intensity": f"{int(low * 100)}-{int(high * 100)}% HRR",
        }
        for zone, (low, high) in ZONE_PCTS.items()
    }


def write_outputs(out_dir: Path, data: HealthData, summary: dict[str, Any]) -> None:
    write_yaml(out_dir / "health/apple/summary.yaml", summary)
    for day, metrics in daily_rollups(data.samples).items():
        write_yaml(out_dir / f"health/apple/daily/{day}.yaml", {"date": day, "metrics": metrics})
    for workout in data.workouts:
        write_yaml(out_dir / f"logs/apple-health/{workout.slug}", workout_to_dict(workout))


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_yaml(data) + "\n")


def to_yaml(value: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        return yaml_dict(value, indent)
    if isinstance(value, list):
        return yaml_list(value, indent)
    return pad + yaml_scalar(value)


def yaml_dict(value: dict[str, Any], indent: int) -> str:
    lines = []
    pad = " " * indent
    for key, item in value.items():
        if isinstance(item, (dict, list)) and item:
            lines.append(f"{pad}{key}:")
            lines.append(to_yaml(item, indent + 2))
        else:
            lines.append(f"{pad}{key}: {yaml_scalar(item)}")
    return "\n".join(lines)


def yaml_list(value: list[Any], indent: int) -> str:
    lines = []
    pad = " " * indent
    for item in value:
        if isinstance(item, dict):
            lines.append(f"{pad}-")
            lines.append(to_yaml(item, indent + 2))
        else:
            lines.append(f"{pad}- {yaml_scalar(item)}")
    return "\n".join(lines) if lines else f"{pad}[]"


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def compact(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None and item != {}}


def extract_profile_number(profile_path: Path, key: str) -> float | None:
    if not profile_path.exists():
        return None
    match = re.search(rf"^\s*{re.escape(key)}:\s*\{{[^}}]*value:\s*([0-9.]+)", profile_path.read_text(), re.M)
    return parse_float(match.group(1)) if match else None


def update_profile(profile_path: Path, summary: dict[str, Any]) -> None:
    text = profile_path.read_text() if profile_path.exists() else "name: Divesh\n"
    latest = summary.get("latest", {})
    text = update_profile_weight(text, latest.get("body_mass"))
    text = ensure_vitals_block(text)
    for key in ("resting_hr", "hrv_sdnn", "vo2_max"):
        if key in latest:
            text = upsert_vital_line(text, key, inline_vital(latest[key]))
    text = update_max_hr_and_hrr(text, summary)
    profile_path.write_text(text.rstrip() + "\n")


def update_profile_weight(text: str, body_mass: dict[str, Any] | None) -> str:
    if not body_mass:
        return text
    line = f"weight: {{ value: {body_mass['value']}, unit: lb, source: \"Apple Health\", date: \"{body_mass['date']}\" }}"
    return re.sub(r"^weight:.*$", line, text, flags=re.M) if re.search(r"^weight:", text, re.M) else text + "\n" + line + "\n"


def ensure_vitals_block(text: str) -> str:
    if re.search(r"^vitals:\s*$", text, re.M):
        return text
    insert_at = text.find("\ndomains:")
    block = "\nvitals:\n"
    return text[:insert_at] + block + text[insert_at:] if insert_at != -1 else text + block


def upsert_vital_line(text: str, key: str, inline: str) -> str:
    line = f"  {key}: {inline}"
    if re.search(rf"^\s*{re.escape(key)}:\s*", text, re.M):
        return re.sub(rf"^\s*{re.escape(key)}:.*$", line, text, flags=re.M)
    return re.sub(r"^vitals:\s*$", "vitals:\n" + line, text, flags=re.M)


def inline_vital(metric: dict[str, Any]) -> str:
    return f"{{ value: {metric['value']}, unit: {metric['unit']}, source: \"Apple Health\", date: \"{metric['date']}\" }}"


def update_max_hr_and_hrr(text: str, summary: dict[str, Any]) -> str:
    observed = summary.get("max_hr_observed")
    observed_value = observed.get("value") if observed else None
    existing_max = extract_number_from_text(text, "max_hr")
    max_value = max([v for v in [existing_max, observed_value] if v is not None], default=None)
    resting = extract_number_from_text(text, "resting_hr")
    if max_value is None:
        return text
    if observed_value is not None and (existing_max is None or observed_value > existing_max):
        inline = f"{{ value: {round(observed_value, 1)}, unit: bpm, source: \"Apple Health\", date: \"{observed['date']}\" }}"
        text = upsert_vital_line(text, "max_hr", inline)
    if resting is not None:
        hrr = round(max_value - resting, 1)
        text = upsert_vital_line(text, "hrr", f"{{ value: {hrr}, unit: bpm, note: \"max_hr - resting_hr\" }}")
    return text


def extract_number_from_text(text: str, key: str) -> float | None:
    match = re.search(rf"^\s*{re.escape(key)}:\s*\{{[^}}]*value:\s*([0-9.]+)", text, re.M)
    return parse_float(match.group(1)) if match else None


def main() -> int:
    args = parse_args()
    profile_path = args.profile if args.profile.is_absolute() else args.out / args.profile
    first_pass = parse_health_input(args.input, parse_date(args.since) if args.since else None)
    since = resolve_since(first_pass, args)
    data = filter_data(first_pass, since)
    summary = build_summary(data, profile_path, since)
    if args.dry_run:
        print(to_yaml(summary))
        return 0
    write_outputs(args.out, data, summary)
    if args.write_profile:
        update_profile(profile_path, summary)
    print(f"Synced {len(data.samples)} samples and {len(data.workouts)} workouts")
    print(f"Summary: {args.out / 'health/apple/summary.yaml'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AppleHealthSyncError as exc:
        print(f"apple_health_sync: {exc}", file=sys.stderr)
        raise SystemExit(1)
