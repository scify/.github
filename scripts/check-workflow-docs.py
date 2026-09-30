#!/usr/bin/env python3
"""Check that the workflow guide documents every reusable workflow input.

For each workflow with `on: workflow_call`, every input and secret must appear
in .github/workflows/README.md as `name`, and every single-line default must
appear there word for word.

Usage: python3 scripts/check-workflow-docs.py
"""
import glob
import sys

import yaml

GUIDE = ".github/workflows/README.md"

guide = open(GUIDE).read()
failed = False
for path in sorted(glob.glob(".github/workflows/*.yml")):
    workflow = yaml.safe_load(open(path))
    # PyYAML reads the key `on` as the boolean True.
    triggers = workflow.get(True) or workflow.get("on") or {}
    if not isinstance(triggers, dict) or "workflow_call" not in triggers:
        continue
    call = triggers["workflow_call"] or {}
    inputs = call.get("inputs") or {}
    secrets = call.get("secrets") or {}
    problems = [f"input or secret `{name}` is not documented" for name in [*inputs, *secrets] if f"`{name}`" not in guide]
    for name, spec in inputs.items():
        default = spec.get("default")
        if isinstance(default, str) and default and "\n" not in default and default not in guide:
            problems.append(f"default of `{name}` ({default!r}) is not documented")
    for problem in problems:
        print(f"::error file={path}::{problem} in {GUIDE}")
    failed = failed or bool(problems)
    print(f"{'FAIL' if problems else 'ok  '} {path}: {len(inputs)} inputs, {len(secrets)} secrets")

sys.exit(1 if failed else 0)
