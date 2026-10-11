"""Every GitHub Actions step pins its action to a commit SHA.

A tag such as ``@v4`` can be moved to new code at any time (the 2025
tj-actions/changed-files compromise rewrote tags), so each ``uses:`` names a
full 40-hex commit and carries the release it corresponds to as a comment,
which is what Dependabot reads and updates. Pinning also keeps Node 20 actions
from lingering unnoticed: GitHub removed Node 20 from its runners on 2026-09-23.

The jobs that are handed the PyPI token pin their packages the same way: each
installs one hash-locked requirements file and nothing by name, and builds
with the backend that file locks instead of one downloaded during the build.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

_ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github" / "workflows").is_dir())
_WORKFLOWS = sorted((_ROOT / ".github" / "workflows").glob("*.yml"))
_USES = re.compile(r"^\s*(?:-\s*)?uses:\s*(\S+)(.*)$")
_PINNED = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
_LOCAL = re.compile(r"^\./")
_VERSION_COMMENT = re.compile(r"^\s+#\s*v\d+(\.\d+)*\s*$")
_PYPI_TOKEN = "secrets.PYPI_API_TOKEN"
_LOCKED_DIRECTORY = ".github/requirements"
_LOCKED_TOOLING = f"{_LOCKED_DIRECTORY}/publish.txt"
_LOCKED_INSTALL = f"python -m pip install --require-hashes --only-binary :all: -r {_LOCKED_TOOLING}"
_INSTALL = re.compile(r"\b(?:pip3?|pipx|uv)\b.*\binstall\b")
_BUILD = re.compile(r"\bpython3? -m build\b|\bpyproject-build\b")
_LOCKED_BACKEND_FLAG = "--no-isolation"
_RUN_KEY = re.compile(r"^(?:-\s*)?run:\s*")
_PINNED_PACKAGE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)", re.MULTILINE)
_BUILD_REQUIRES = re.compile(r"^requires\s*=\s*\[([^\]]*)\]", re.MULTILINE)
_BUILT_METADATA = ("pyproject.toml", "dev.toml")


def _uses(path: Path) -> list[tuple[int, str, str]]:
    """Return ``(line number, action reference, rest of line)`` for each remote ``uses:``."""
    found = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = _USES.match(line)
        if match and not _LOCAL.match(match.group(1)):
            found.append((number, match.group(1), match.group(2)))
    return found


def test_workflows_exist():
    assert _WORKFLOWS


@pytest.mark.parametrize("workflow", _WORKFLOWS, ids=lambda p: p.name)
def test_every_action_is_pinned_to_a_commit_with_its_version(workflow):
    bad = [f"{workflow.name}:{number} {ref}{rest}"
           for number, ref, rest in _uses(workflow)
           if not (_PINNED.match(ref) and _VERSION_COMMENT.match(rest))]
    assert bad == []


def test_one_version_per_action():
    # The same action at two different commits means a partial upgrade.
    seen: dict[str, set[str]] = {}
    for workflow in _WORKFLOWS:
        for _number, ref, _rest in _uses(workflow):
            action, _, sha = ref.partition("@")
            seen.setdefault(action, set()).add(sha)
    assert {action: shas for action, shas in seen.items() if len(shas) > 1} == {}


def _dependabot_blocks() -> list[tuple[str, str]]:
    """Return ``(ecosystem, block text)`` for each update block of ``dependabot.yml``.

    Parsed as text: PyYAML is not a test dependency.
    """
    text = (_ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    blocks = re.split(r"^\s*-\s*package-ecosystem:", text, flags=re.MULTILINE)[1:]
    return [(block.split()[0].strip("\"'"), block) for block in blocks]


def test_dependabot_keeps_pins_current_on_dev():
    # Pinned SHAs only stay current if something bumps them; every update
    # goes to dev because main is the release branch.
    blocks = _dependabot_blocks()
    assert {"pip", "github-actions"} <= {ecosystem for ecosystem, _block in blocks}
    assert all(re.search(r"^\s*target-branch:\s*\"dev\"", block, re.MULTILINE)
               for _ecosystem, block in blocks)


def test_dependabot_waits_a_week_before_proposing_a_release():
    # A compromised release is usually found and yanked within days. Dependabot's
    # own default wait is 3 days, and zizmor's dependabot-cooldown audit asks
    # for 7. The wait never delays security updates.
    blocks = _dependabot_blocks()
    days = [re.search(r"^\s*default-days:\s*(\d+)", block, re.MULTILINE) for _ecosystem, block in blocks]
    assert blocks and all(match and int(match.group(1)) >= 7 for match in days)


def test_dependabot_reaches_the_hash_locked_requirements():
    # Dependabot reads only the directories it is given, and "/" does not include
    # .github/requirements, so the pins in ci.txt and publish.txt would never move.
    listed = {path for ecosystem, block in _dependabot_blocks() if ecosystem == "pip"
              for path in re.findall(r"^\s*(?:-|directory:)\s*\"(/[^\"]*)\"", block, re.MULTILINE)}
    assert {"/", f"/{_LOCKED_DIRECTORY}"} <= listed


def _checkout_steps(path: Path) -> list[tuple[int, str]]:
    """Return ``(line number, step text)`` for each ``actions/checkout`` step."""
    lines = path.read_text(encoding="utf-8").splitlines()
    steps = []
    for index, line in enumerate(lines):
        if not re.search(r"uses:\s*actions/checkout@", line):
            continue
        column = line.index("uses:")
        body = [line]
        for following in lines[index + 1:]:
            indent = len(following) - len(following.lstrip())
            if following.strip() and (indent < column or following.lstrip().startswith("- ")):
                break
            body.append(following)
        steps.append((index + 1, "\n".join(body)))
    return steps


@pytest.mark.parametrize("workflow", _WORKFLOWS, ids=lambda p: p.name)
def test_every_checkout_decides_on_persisted_credentials(workflow):
    # actions/checkout leaves the job token in .git/config unless told not
    # to, where every later step (and any uploaded workspace) can read it.
    # Only jobs that push keep it, and they say so.
    bad = [f"{workflow.name}:{number}" for number, step in _checkout_steps(workflow)
           if not re.search(r"^\s*persist-credentials:\s*(true|false)\b", step, re.MULTILINE)]
    assert bad == []


_JOB_HEAD = re.compile(r"^  [A-Za-z0-9_-]+:\s*(#.*)?$")


def _jobs(path: Path) -> list[tuple[str, str]]:
    """Return ``(job id, job text)`` for each job under ``jobs:`` in a workflow."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if re.match(r"^jobs:\s*(#.*)?$", line))
    heads = [i for i in range(start + 1, len(lines)) if _JOB_HEAD.match(lines[i])]
    ends = [*heads[1:], len(lines)]
    return [(lines[i].strip().rstrip(":"), "\n".join(lines[i:end])) for i, end in zip(heads, ends)]


@pytest.mark.parametrize("workflow", _WORKFLOWS, ids=lambda p: p.name)
def test_every_job_has_a_timeout(workflow):
    # Without timeout-minutes a hung job runs for GitHub's default six hours.
    # Each job sets about three times its slowest recent run, at least 15 minutes.
    bad = [name for name, body in _jobs(workflow)
           if "runs-on:" in body and not re.search(r"^\s*timeout-minutes:", body, re.MULTILINE)]
    assert bad == []


def _publish_jobs() -> dict[str, str]:
    """Map ``workflow file:job id`` to the text of each job that is handed the PyPI token."""
    return {f"{workflow.name}:{name}": body
            for workflow in _WORKFLOWS for name, body in _jobs(workflow) if _PYPI_TOKEN in body}


def _commands(job: str, pattern: re.Pattern[str]) -> list[str]:
    """Return the lines of a job that match ``pattern``; comment lines are not commands."""
    lines = (_RUN_KEY.sub("", line.strip()) for line in job.splitlines())
    return [line for line in lines if not line.startswith("#") and pattern.search(line)]


def _installs(job: str) -> list[str]:
    """Return the commands of a job that install packages."""
    return _commands(job, _INSTALL)


def _builds(job: str) -> list[str]:
    """Return the commands of a job that build the distribution."""
    return _commands(job, _BUILD)


def _locked() -> dict[str, str]:
    """Map each package the locked tooling pins to its version."""
    return dict(_PINNED_PACKAGE.findall((_ROOT / _LOCKED_TOOLING).read_text(encoding="utf-8")))


def _build_requires(metadata: str) -> list[Requirement]:
    """Return ``build-system.requires`` of a metadata file.

    Parsed as text: ``tomllib`` is missing on Python 3.10, which CI still tests.
    """
    items = _BUILD_REQUIRES.search((_ROOT / metadata).read_text(encoding="utf-8")).group(1)
    return [Requirement(item) for item in re.findall(r"[\"']([^\"']+)[\"']", items)]


def _unmet(requirements: list[Requirement], locked: dict[str, str]) -> list[str]:
    """Return the requirements ``locked`` does not satisfy; a package it does not pin is unmet."""
    names = [(requirement, canonicalize_name(requirement.name)) for requirement in requirements]
    return [str(requirement) for requirement, name in names
            if name not in locked or not requirement.specifier.contains(locked[name])]


def test_the_publish_jobs_are_the_two_that_upload():
    # The dev channel (ci.yml) and the stable release (publish.yml). A third job that gets the
    # token joins the check below by itself; this list only shows that the check found the two.
    assert sorted(_publish_jobs()) == ["ci.yml:publish-dev", "publish.yml:publish"]


@pytest.mark.parametrize("job", sorted(_publish_jobs()))
def test_a_publish_job_installs_only_the_hash_locked_tooling(job):
    # A job that holds the PyPI token runs whatever its tools resolve to on that day, so it
    # installs the locked file and nothing else: no pip upgrade, no second install by name.
    assert _installs(_publish_jobs()[job]) == [_LOCKED_INSTALL]


def test_the_install_check_sees_an_unpinned_install():
    unpinned = "- name: Install build tools\n  run: |\n    python -m pip install --upgrade pip\n" \
               "    pip install build twine\n# pip install nothing\n- run: pipx install twine\n"
    assert _installs(unpinned) == [
        "python -m pip install --upgrade pip", "pip install build twine", "pipx install twine"]
    assert _installs(f"- run: {_LOCKED_INSTALL}\n") == [_LOCKED_INSTALL]


def test_the_locked_tooling_pins_what_the_publish_jobs_run():
    # build and twine are the commands; setuptools is the backend a build without isolation imports.
    assert {"build", "twine", "setuptools"} <= set(_locked())


@pytest.mark.parametrize("job", sorted(_publish_jobs()))
def test_a_publish_job_builds_with_the_locked_backend(job):
    # An isolated build downloads the newest backend each time, outside the lock, into the job
    # that is about to upload with the token.
    builds = _builds(_publish_jobs()[job])
    assert builds and all(_LOCKED_BACKEND_FLAG in command.split() for command in builds)


def test_the_build_check_sees_an_isolated_build():
    isolated = "- name: Build\n  run: python -m build\n# python -m build --no-isolation\n- run: pyproject-build\n"
    assert _builds(isolated) == ["python -m build", "pyproject-build"]
    assert _builds("- run: python -m twine check dist/*\n") == []


@pytest.mark.parametrize("metadata", _BUILT_METADATA)
def test_the_locked_tooling_satisfies_build_system_requires(metadata):
    # --no-isolation checks build-system.requires instead of installing it. A floor raised without
    # regenerating publish.txt (Dependabot edits these files) fails here, not in the publish job.
    requirements = _build_requires(metadata)
    assert requirements
    assert _unmet(requirements, _locked()) == []


def test_the_requirement_check_sees_a_raised_floor_and_an_unpinned_package():
    locked = {"setuptools": "84.0.0"}
    assert _unmet([Requirement("setuptools>=82.0.1")], locked) == []
    assert _unmet([Requirement("setuptools>=85"), Requirement("wheel")], locked) == ["setuptools>=85", "wheel"]
