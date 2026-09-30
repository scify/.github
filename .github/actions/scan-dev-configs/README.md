# scan-dev-configs

Composite GitHub Action that scans dev tool configuration directories for signs of compromise. Catches malicious payloads and suspicious commands before they reach production.

## What it checks

**Directories scanned:** `.vscode/`, `.claude/`, `.cursor/`, `.idea/`

If none of these directories exist in the repository, the action passes silently.

| Check | What triggers a failure |
|-------|----------------------|
| Script files | A file in a dev tool directory is a script and `allowed-scripts` does not list it. A script is a file with a script or binary extension (`.js`, `.ts`, `.sh`, `.py`, `.ps1`, `.bat`, `.exe`, `.jar` and others), the executable bit, or a `#!` first line |
| Suspicious commands | Any config file contains execution or network patterns (see list below). Warns by default, fails with `strict: true` |

**Suspicious command patterns:**

`curl`, `wget`, `Invoke-WebRequest`, `iwr`, `bash -c`, `sh -c`, `powershell`, `pwsh`, `certutil`, `base64`, `chmod +x`, `nc`, `ncat`, `socat`, `python -c`, `node -e`, `eval(`, `npx`

Every pattern is matched on word boundaries, so `async` does not trigger `nc`.

Allowed scripts are scanned for suspicious commands too. The allowlist permits the file, not every command in it.

Editor task files (`.vscode/tasks.json`) and agent permission lists (`.claude/settings.json`) legitimately contain `npx` or `curl`. That is why this check warns by default. Review the warnings, and enable `strict` once the repository's config files are clean.

## Inputs

| Name | Default | Description |
| --- | --- | --- |
| `allowed-scripts` | `''` | Newline-separated glob patterns, relative to the repository root, of reviewed script files. `*` also matches `/`. Example: `.claude/hooks/*.sh` |
| `strict` | `'false'` | Fail on suspicious commands instead of warning. One of: `'true'`, `'false'` |

```yaml
- uses: scify/.github/.github/actions/scan-dev-configs@<commit-sha> # v0.1
  with:
    allowed-scripts: |
      .claude/hooks/*.sh
      .vscode/extensions/check.js
    strict: 'true'
```

## Why this exists

Supply chain attacks increasingly target dev tool configs as a persistence and execution vector. Malicious payloads are dropped as `.js` files in `.vscode/` or `.claude/` directories, and triggers are injected into `settings.json`, `tasks.json`, or similar config files to execute them. This action catches both the payload and the trigger.

## Setup

### 1. Wire the action into your workflow

**Same-repo usage** (action lives in the consuming repository):

Copy the `.github/actions/scan-dev-configs/` directory into your repo, then reference it as a local action:

```yaml
steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  - uses: ./.github/actions/scan-dev-configs
```

**Organisation-wide usage** (recommended):

In a SciFY repository, call the reusable `security.yml` workflow. It runs this
action with the other security checks. See the
[workflow guide](../../workflows/README.md#security).

To use the action on its own, pin it to a full commit SHA. The organisation
requires this for every action, including actions from `scify/.github`. A tag
such as `@v0.1` fails. Get the SHA of a release with
`git ls-remote https://github.com/scify/.github refs/tags/v0.1`:

```yaml
steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  - uses: scify/.github/.github/actions/scan-dev-configs@<commit-sha> # v0.1
```

### 2. Placement

Place after `actions/checkout` and before any build or deploy steps. It runs independently of `verify-npm-hardening` and does not require Node.js or npm.

## When the check fails

The error output names the exact file and line that triggered the failure:

- **Script file found:** remove it from the repository. If the script is legitimate, for example a Claude Code hook, review it and add its path to `allowed-scripts`. A reviewer then sees each new allowed path in the pull request.
- **Suspicious command found:** inspect the config file. Remove entries containing execution or network commands.

If the file is legitimate and expected, reconsider whether it belongs in a dev tool config directory or whether it should live elsewhere in the project.
