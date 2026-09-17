# scan-dev-configs

Composite GitHub Action that scans dev tool configuration directories for signs of compromise. Catches malicious payloads and suspicious commands before they reach production.

## What it checks

**Directories scanned:** `.vscode/`, `.claude/`, `.cursor/`, `.idea/`

If none of these directories exist in the repository, the action passes silently.

| Check | What triggers a failure |
|-------|----------------------|
| Executable scripts | Any `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.mts`, or `.cts` file exists in a dev tool directory |
| Suspicious commands | Any config file contains execution or network patterns (see list below). Warns by default, fails with `strict: true` |

**Suspicious command patterns:**

`curl`, `wget`, `Invoke-WebRequest`, `iwr`, `bash -c`, `sh -c`, `powershell`, `pwsh`, `certutil`, `base64`, `chmod +x`, `nc`, `ncat`, `socat`, `python -c`, `node -e`, `eval(`, `npx`

Every pattern is matched on word boundaries, so `async` does not trigger `nc`.

Editor task files (`.vscode/tasks.json`) and agent permission lists (`.claude/settings.json`) legitimately contain `npx` or `curl`. That is why this check warns by default. Review the warnings, and enable `strict` once the repository's config files are clean.

## Inputs

| Name     | Default | Description                                            |
|----------|---------|--------------------------------------------------------|
| `strict` | `false` | Fail on suspicious commands instead of warning.        |

```yaml
- uses: scify/.github/.github/actions/scan-dev-configs@v0.1
  with:
    strict: true
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

The action is published from the public `scify/.github` repository. Reference it by the `v1` tag:

```yaml
steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  - uses: scify/.github/.github/actions/scan-dev-configs@v0.1
```

The reusable `security.yml` workflow in the same repository already runs this action. Call that workflow instead when you want the full set of checks.

### 2. Placement

Place after `actions/checkout` and before any build or deploy steps. It runs independently of `verify-npm-hardening` and does not require Node.js or npm.

## When the check fails

The error output names the exact file and line that triggered the failure:

- **Executable script found:** remove it from the repository. Dev tool directories should not contain executable code (`.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.mts`, `.cts`).
- **Suspicious command found:** inspect the config file. Remove entries containing execution or network commands.

If the file is legitimate and expected, reconsider whether it belongs in a dev tool config directory or whether it should live elsewhere in the project.
