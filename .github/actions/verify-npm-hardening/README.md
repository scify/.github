# verify-npm-hardening

Composite GitHub Action that verifies supply chain security settings before `npm ci` runs. Catches missing or misconfigured settings before they reach production.

## Policy

This table is the canonical SciFY npm supply chain policy. The action enforces
every rule marked "fails". The `npm-harden` skill in the `scify-devops` Claude
Code plugin applies the same rules to a repository.

| # | Rule | Value | CI result | Why |
| --- | --- | --- | --- | --- |
| 1 | `.npmrc` is committed | file exists | fails | Holds the settings below |
| 2 | `package-lock.json` is committed | file exists | fails | `npm ci` needs it for a deterministic install |
| 3 | `ignore-scripts` | `true` | fails | Blocks install scripts, the main vector of npm supply chain attacks |
| 4 | `engine-strict` | `true` | fails | Refuses to install on Node or npm versions outside `engines` |
| 5 | `min-release-age` | a plain integer, at least 7 (days); the `min-age` input can raise the minimum | fails | Quarantines new releases. Needs npm 11.10.0 or later. `7d` is invalid and disables the protection |
| 6 | No git, URL, GitHub or `file:` dependencies in `package.json` | none allowed; `npm:` aliases are allowed | fails | These sources bypass `min-release-age` |
| 7 | Every `resolved` URL in `package-lock.json` points to the public npm registry | starts with `https://registry.npmjs.org/` (no other host, no `http://`) | fails | Detects a tampered lockfile |
| 8 | `save-exact` | `true` | not checked (recommended) | New dependencies get exact versions instead of `^` ranges |

## Setup

### 1. Add `.npmrc` to your repository

```ini
engine-strict=true
ignore-scripts=true
min-release-age=7
```

Commit this file. Do not `.gitignore` it.

You may also want to add `save-exact=true` to pin new dependencies to exact versions instead of `^` ranges. The action does not enforce this, but it is recommended.

**Common mistake:** `min-release-age` takes a plain integer (days), not a suffixed value. `min-release-age=7` is correct. `min-release-age=7d` silently resolves to `null` and disables the protection entirely.

### 2. Commit your lockfile

`package-lock.json` must be committed to the repository. Without it, `npm ci` cannot perform a deterministic installation and the action will fail.

### 3. Wire the action into your workflow

**Same-repo usage** (action lives in the consuming repository):

Copy the `.github/actions/verify-npm-hardening/` directory into your repo, then reference it as a local action:

```yaml
steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  - uses: ./.github/actions/verify-npm-hardening
  - run: npm ci
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
  - uses: scify/.github/.github/actions/verify-npm-hardening@<commit-sha> # v0.1
  - run: npm ci
```

## Inputs

| Name      | Default | Description                                                       |
|-----------|---------|-------------------------------------------------------------------|
| `min-age` | `7`     | Minimum acceptable `min-release-age` value in days. Must be >= 7. |
| `working-directory` | `.` | Folder that holds `package.json` and `.npmrc`, relative to the repository root. Example: `frontend` |

```yaml
- uses: ./.github/actions/verify-npm-hardening
  with:
    min-age: 14  # stricter quarantine
```

## When the check fails

The error output names the exact file or setting that is missing or invalid:

- **`.npmrc` missing:** create it with the settings listed above and commit it.
- **`package-lock.json` missing:** run `npm install` locally, commit the lockfile, and push.
- **A setting is missing or invalid:** add or correct it in `.npmrc` and push.

Do not remove or weaken these settings to make the build pass.
