#!/usr/bin/env python3
"""Fetch/copy, authenticate, extract and replay the frozen drag evidence.

Python >= 3.11. The numerical and proof-record checks are the original archived
programs. This wrapper does not implement a replacement certificate checker.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from urllib.parse import quote, urlsplit
from urllib.request import urlopen

REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "data/archive-lock.json"
CHUNK = 8 * 1024 * 1024
SCOPE = (
    "Integrity of both archives, exact certificate assembly, array identity, "
    "stored full-space enclosure aggregation, and (in portable mode) frozen "
    "scalar/time, geometric and physical-cover replays. Not an independent "
    "numerical recomputation of every production spatial enclosure."
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def check_file(path, expected):
    require(path.is_file() and not path.is_symlink(), f"Not a regular file: {path.name}")
    require(path.stat().st_size == expected["bytes"], f"Wrong size: {path.name}")
    observed = digest(path)
    require(observed == expected["sha256"], f"SHA-256 mismatch: {path.name}")
    return {"name": path.name, "bytes": expected["bytes"], "sha256": observed, "passed": True}


def validate_base_url(value):
    u = urlsplit(value)
    require(u.scheme == "https" or (u.scheme == "http" and u.hostname in {"localhost", "127.0.0.1", "::1"}),
            "Use HTTPS; HTTP is allowed only for a local transfer test")
    require(bool(u.hostname) and not u.username and not u.password and not u.query and not u.fragment,
            "Use a plain file-base URL without credentials, query or fragment")
    return value.rstrip("/")


def fetch(url, destination, expected):
    """Do not expose a partially downloaded file under its final name."""
    partial = destination.with_name(destination.name + ".part")
    require(not destination.exists() and not partial.exists(), "Download target already exists")
    total = 0
    try:
        with urlopen(url, timeout=60) as response, partial.open("xb") as out:
            validate_base_url(response.geturl())
            while block := response.read(CHUNK):
                total += len(block)
                require(total <= expected["bytes"], f"Download too large: {destination.name}")
                out.write(block)
        check_file(partial, expected)
        partial.rename(destination)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def extract_archive(archive, target, expected):
    """Only regular files/directories within the pinned root; never restore links."""
    root = expected["root"]
    require(not (target / root).exists(), f"Extraction root already exists: {root}")
    seen = set()
    files, total = 0, 0
    with tarfile.open(archive, "r|gz") as stream:
        for member in stream:
            p = PurePosixPath(member.name)
            require(bool(p.parts) and not p.is_absolute() and ".." not in p.parts and "\\" not in member.name,
                    f"Unsafe archive path: {member.name}")
            require(p.parts[0] == root and p.as_posix() not in seen, f"Wrong root or duplicate member: {member.name}")
            require(member.isfile() or member.isdir(), f"Unsupported archive member: {member.name}")
            seen.add(p.as_posix())
            dest = target.joinpath(*p.parts)
            require(dest.resolve().is_relative_to(target.resolve()), f"Escaping archive path: {member.name}")
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
                continue
            require(member.size >= 0, "Negative member size")
            files += 1
            total += member.size
            require(files <= expected["extracted_regular_files"] and total <= expected["extracted_bytes"],
                    "Archive exceeds its pinned extraction limits")
            dest.parent.mkdir(parents=True, exist_ok=True)
            payload = stream.extractfile(member)
            require(payload is not None, "Missing archive payload")
            with payload, dest.open("xb") as out:
                shutil.copyfileobj(payload, out, CHUNK)
            require(dest.stat().st_size == member.size, "Truncated archive member")
    require(files == expected["extracted_regular_files"] and total == expected["extracted_bytes"],
            "Wrong extracted file count or total size")
    return {"root": root, "files": files, "bytes": total, "passed": True}


def stage_plan(extracted, reports, portable):
    root = extracted / "T2_certificate_v1"
    earlier = extracted / "earlier_certificates_2026-11-17"
    stages = [
        ("integrity", ["verification/verify.py", "--report", str(reports / "integrity.json")], reports / "integrity.json"),
        ("arrays", ["verification/arrays.py", "--report", str(reports / "arrays.json")], reports / "arrays.json"),
        ("enclosures", ["verification/enclosures.py", "--out", str(reports / "enclosures")], reports / "enclosures/RESULTS.json"),
    ]
    if portable:
        for name in ("scalars", "geometry", "cover"):
            stages.append((name, ["verification/replay.py", name, "--out", str(reports / name)], reports / name / "RESULTS.json"))
    stages.append(("earlier", ["verification/verify_earlier.py", "--archive", str(earlier), "--report", str(reports / "earlier.json")], reports / "earlier.json"))
    return root, stages


def run_stage(name, args, output, root, reports, env):
    log = reports / (name + ".log")
    start = time.monotonic()
    print(f"Running {name}...", flush=True)
    with log.open("w") as stream:
        result = subprocess.run([sys.executable, "-B", *args], cwd=root, env=env,
                                stdout=stream, stderr=subprocess.STDOUT, check=False)
    require(result.returncode == 0, f"Stage {name} failed (exit {result.returncode}); see {log}")
    require(output.is_file(), f"Stage {name} did not produce {output.name}")
    record = json.loads(output.read_text())
    require(record.get("passed") is True, f"Stage {name} did not report passed=true")
    print(f"PASS {name}", flush=True)
    return {"stage": name, "passed": True, "seconds": time.monotonic() - start,
            "report": str(output.relative_to(reports)), "report_sha256": digest(output),
            "log": log.name}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-dir", type=Path, help="Local directory containing the nine pinned submission files")
    source.add_argument("--base-url", help="HTTPS directory containing those files, e.g. a published Zenodo record's /files")
    ap.add_argument("--work-dir", required=True, type=Path, help="New directory; existing directories are refused")
    ap.add_argument("--mode", choices=("portable", "records"), default="portable",
                    help="portable: all seven checks; records: four stdlib-only checks")
    args = ap.parse_args(argv)
    require(sys.version_info >= (3, 11), "Python 3.11 or later is required")
    require(__debug__, "Do not use Python -O; native assertions must remain enabled")
    require(not os.environ.get("PYTHONOPTIMIZE"), "Unset PYTHONOPTIMIZE; native assertions must remain enabled")
    packages = {}
    if args.mode == "portable":
        for name in ("numpy", "mpmath"):
            try:
                packages[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError as exc:
                raise ValueError(f"Install requirements-replay.txt first (missing {name})") from exc
    lock = json.loads(LOCK.read_text())
    expected = lock["files"]
    require(lock["format_version"] == 1 and len({r['name'] for r in expected}) == len(expected), "Invalid archive lock")
    for rec in expected:
        require(Path(rec["name"]).name == rec["name"] and rec["name"] not in {"", ".", ".."}, "Invalid lock filename")
    local = args.source_dir.resolve() if args.source_dir else None
    base_url = validate_base_url(args.base_url) if args.base_url else None
    if local:
        require(local.is_dir(), "Source directory is missing")
    require(not args.work_dir.exists() and not args.work_dir.is_symlink(), "Work directory exists; choose a fresh directory")
    work = args.work_dir.resolve()
    if local:
        require(not work.is_relative_to(local), "Keep work output outside the source directory")
    work.mkdir(parents=True)
    reports = work / "reports"
    reports.mkdir()
    status = {"passed": False, "status": "running", "mode": args.mode, "scope": SCOPE,
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "platform": platform.platform(), "packages": packages,
              "archive_lock_sha256": digest(LOCK), "files": [], "extractions": [], "stages": [],
              "source_kind": "local_files" if local else "http_transfer",
              "source_url": base_url}
    summary = reports / "verification-summary.json"
    write_json(summary, status)
    start = time.monotonic()
    try:
        inputs = work / "downloads"
        inputs.mkdir()
        for rec in expected:
            print(f"Checking {rec['name']}...", flush=True)
            dest = inputs / rec["name"]
            if local:
                require(not (local / rec["name"]).is_symlink(), "Source files must not be symlinks")
                shutil.copyfile(local / rec["name"], dest)
            else:
                fetch(base_url + "/" + quote(rec["name"]), dest, rec)
            status["files"].append(check_file(dest, rec))
            write_json(summary, status)
        extracted = work / "extracted"
        extracted.mkdir()
        for rec in expected:
            if "root" in rec:
                print(f"Extracting {rec['name']}...", flush=True)
                status["extractions"].append(extract_archive(inputs / rec["name"], extracted, rec))
                write_json(summary, status)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        root, stages = stage_plan(extracted, reports, args.mode == "portable")
        for name, command, output in stages:
            status["stages"].append(run_stage(name, command, output, root, reports, env))
            write_json(summary, status)
        integrity = json.loads((reports / "integrity.json").read_text())
        status["certificate_interval"] = integrity["release"]["readable_interval"]
        status["budget_approx"] = integrity["release"]["budget_approx"]
        status["passed"] = True
        status["status"] = "completed"
    except BaseException as exc:
        status["status"] = "failed"
        status["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        status["seconds"] = time.monotonic() - start
        write_json(summary, status)
    print(f"PASS: {len(status['stages'])} {args.mode} checks. Report: {summary}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Exception, KeyboardInterrupt) as exc:
        print(f"VERIFICATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
