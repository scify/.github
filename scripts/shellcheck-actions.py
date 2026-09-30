#!/usr/bin/env python3
"""Run shellcheck on every bash step of the composite actions.

actionlint checks the scripts in workflows, but not in action.yml files.
Each `run:` block is written to a temporary file and checked on its own.
`${{ ... }}` expressions are replaced with a placeholder word first.

Usage: python3 scripts/shellcheck-actions.py
"""
import glob
import re
import subprocess
import sys
import tempfile

import yaml

EXPRESSION = re.compile(r"\$\{\{.*?\}\}")

failed = False
for path in sorted(glob.glob(".github/actions/*/action.yml")):
    action = yaml.safe_load(open(path))
    for index, step in enumerate(action["runs"].get("steps", [])):
        if "run" not in step or step.get("shell") != "bash":
            continue
        name = step.get("name", f"step {index + 1}")
        script = "#!/usr/bin/env bash\n" + EXPRESSION.sub("GITHUB_EXPRESSION", step["run"])
        with tempfile.NamedTemporaryFile("w", suffix=".sh") as handle:
            handle.write(script)
            handle.flush()
            result = subprocess.run(["shellcheck", handle.name], capture_output=True, text=True)
        if result.returncode != 0:
            failed = True
            print(f"::error file={path}::shellcheck failed in step '{name}'")
            print(result.stdout.replace(handle.name, f"{path} ({name})"))
        else:
            print(f"ok  {path}: {name}")

sys.exit(1 if failed else 0)
