"""Check a requirements.txt against PyPI for Python 3.11 compatibility.

Usage: python check_requirements.py [requirements.txt]
"""

import sys

import requests
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

TARGET_PYTHON = Version("3.11")
PYPI_URL = "https://pypi.org/pypi/{}/json"


def fetch_json(path):
    """Return parsed JSON for a PyPI path, or None on 404."""
    resp = requests.get(PYPI_URL.format(path), timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def parse_line(line):
    """Split 'name==version' into (name, version)."""
    name, _, version = line.partition("==")
    return name.strip(), version.strip()


def minimum_python(spec_set):
    """Lowest Python version allowed by the specifier's lower bounds."""
    bounds = [Version(s.version.replace("*", "0")) for s in spec_set
              if s.operator in (">=", ">", "~=", "==")]
    return max(bounds) if bounds else None


def main(path):
    with open(path) as f:
        lines = [l.split("#", 1)[0].strip() for l in f]
    lines = [l for l in lines if l]

    not_found = 0
    incompatible = 0
    highest = None  # (min_version, name, version, requires_python)

    for line in lines:
        name, version = parse_line(line)

        if fetch_json(name) is None:
            not_found += 1
            continue
        release = fetch_json(f"{name}/{version}")
        if release is None:
            not_found += 1
            continue

        requires_python = (release["info"].get("requires_python") or "").strip()
        if not requires_python:
            continue  # no constraint counts as compatible

        try:
            spec = SpecifierSet(requires_python)
        except InvalidSpecifier:
            continue

        if not spec.contains(TARGET_PYTHON, prereleases=True):
            incompatible += 1

        min_py = minimum_python(spec)
        if min_py is not None and (highest is None or min_py > highest[0]):
            highest = (min_py, name, version, requires_python)

    print(f"Dependencies checked: {len(lines)}")
    print(f"Not found on PyPI: {not_found}")
    print(f"Incompatible with Python 3.11: {incompatible}")
    if highest:
        _, name, version, requires_python = highest
        print(f"Highest requirement: {name}=={version} ({requires_python})")
    else:
        print("Highest requirement: none")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "requirements.txt")
