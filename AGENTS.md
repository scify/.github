# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Copilot, Cursor and
others). People read [README.md](README.md) first.

This repository holds the shared GitHub material of the SciFY organisation:
reusable workflows, composite actions, workflow templates, Dependabot templates
and the organisation's default community files. It is public. Agent skills live
in a different repository, `scify/scify-agent-tools`.

| Your task | Read |
| --- | --- |
| Add CI or security checks to **another** SciFY repository | [Part 1](#part-1-use-the-shared-workflows-in-another-repository) |
| Change **this** repository | [Part 2](#part-2-change-this-repository) |

## Part 1: Use the shared workflows in another repository

**Current release tag: `v0.1`.** Call every workflow with `@v0.1`. This short
tag moves to each fix release. Never pin an exact release such as `@v0.1.4`,
even when the release list shows it as "Latest".

| Repository type | Workflows to call | Template |
| --- | --- | --- |
| Laravel (has `artisan` and `composer.json`) | `laravel-ci.yml` and `security.yml` | `workflow-templates/laravel-ci.yml`, `workflow-templates/security.yml` |
| npm only (has `package.json`, no `composer.json`) | `node-ci.yml` and `security.yml` | `workflow-templates/node-ci.yml`, `workflow-templates/security.yml` |
| Other (PHP library, WordPress, static site) | `security.yml` only | `workflow-templates/security.yml` |

Follow the procedure in
[Adopt in an existing repository](.github/workflows/README.md#adopt-in-an-existing-repository).
The [workflow guide](.github/workflows/README.md) lists every input with its
default and example values. If you have the `scify-devops` Claude Code plugin,
the `/ci-setup` skill runs the same procedure.

Read these files from the release tag, not from `main`:

```bash
gh api 'repos/scify/.github/contents/workflow-templates/laravel-ci.yml?ref=v0.1' \
  -H 'Accept: application/vnd.github.raw'
gh api 'repos/scify/.github/contents/.github/workflows/README.md?ref=v0.1' \
  -H 'Accept: application/vnd.github.raw'
```

Rules that cause failures when you break them:

1. **Start from the template** and keep its triggers, `concurrency` and
   `permissions`. **Replace only CI and security workflows**; keep deployment,
   Dependabot auto-merge and other workflows. **Do not guess inputs**: read
   `phpunit.xml`, `composer.json` and `package.json` first.

2. **Workflows by tag, actions by SHA.** Call a reusable workflow with `@v0.1`.
   The organisation requires every action in a step to be pinned by full commit
   SHA, also actions from `scify/.github`. Do not call
   `scify/.github/.github/actions/<name>@v0.1`: it fails. Use `security.yml`
   instead, which runs both actions.
3. **Run the target repository's own checks before you push.** Its formatters
   and linters also check the new workflow files. Then run
   `actionlint .github/workflows/*.yml`.
4. **The required check becomes `ci / CI`.** Tell the user to update the branch
   ruleset or branch protection. Do not change repository settings without the
   user's approval.
5. **Read the job logs.** A green job can mean that a step was skipped, for
   example "No package.json, skipping".
6. **Delete replaced files**: old CI or security workflows, and local copies of
   `scan-dev-configs` or `verify-npm-hardening`.

The npm rules that `security.yml` enforces are in the
[npm policy](.github/actions/verify-npm-hardening/README.md#policy).

## Part 2: Change this repository

### Layout

| Path | Contents |
| --- | --- |
| `.github/workflows/laravel-ci.yml`, `node-ci.yml`, `security.yml` | Reusable workflows (`on: workflow_call`) |
| `.github/workflows/self-check.yml` | CI of this repository. Not reusable |
| `.github/workflows/README.md` | Workflow guide for callers |
| `.github/actions/scan-dev-configs/`, `verify-npm-hardening/` | Composite actions that `security.yml` runs |
| `workflow-templates/` | Starter workflows for the "New workflow" page, with `.properties.json` files |
| `templates/` | Dependabot templates that repositories copy |
| `scripts/` | Checker scripts that the self-check runs |
| `tests/fixtures/` | Sample projects for the smoke tests (see its README) |
| `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`, `profile/` | Organisation defaults. GitHub applies them to every SciFY repository without its own copy |
| `tasks/` | Local notes. Git ignores this folder |

### Design rules

Keep these rules. Each one fixes a failure that happened.

1. **Scope.** Only content that is safe to publish. No secrets, hostnames or
   deployment workflows: deployment lives in private repositories.
2. **Pin every third-party action by full commit SHA**, with the version in a
   trailing comment: `uses: actions/checkout@<sha> # v7.0.1`.
3. **No tag-pinned own actions.** `security.yml` checks out this repository at
   `job.workflow_sha` and runs the actions from `./.scify-github/...`. Do not
   change this to `scify/.github/.github/actions/<name>@v0.1`.
4. **No composite actions for setup in the CI workflows.** `laravel-ci.yml` and
   `node-ci.yml` share setup steps through YAML anchors (`&name` in the first
   job, `*name` in the others). A setup step changes in the first job only.
5. **Tolerant defaults.** An empty `*-command` input means auto-detect: a tool
   runs only when the repository has its config file.
6. **No `${{ }}` inside `run:`.** Pass inputs through `env:` and run custom
   commands with `bash -c "$VAR"`.
7. **`shell: bash` runs with `-e -o pipefail`.** `x=$(grep ...)` stops the step
   when grep finds nothing. Add `|| true` where no match is a valid result.
8. **Every input description ends with example values.** The guide documents
   every input and default. `scripts/check-workflow-docs.py` fails otherwise.
9. **Templates list every input**, commented out, with the extra indentation
   after the `#` (`#   input: value`), so Prettier in a caller repository does
   not move them.
10. **Every internal `@vX` reference uses the same tag.** The self-check fails
    otherwise.
11. **Every check needs a case that must fail.** The `security-actions` job runs
    each action on a broken fixture and expects a failure.
12. **Write documentation in ASD-STE100 Simplified Technical English**: active
    voice, short sentences, one instruction per sentence.

### Check your change locally

The `Self-check` workflow runs these on every pull request. Run them before you
push:

```bash
actionlint .github/workflows/*.yml   # needs shellcheck on PATH for the run: scripts
python3 scripts/shellcheck-actions.py
python3 scripts/check-workflow-docs.py
```

The smoke tests (the fixtures in `tests/fixtures/`) run only on GitHub. Open a
pull request and read the logs of the jobs that your change affects.

### Release

Releases follow [Versioning](README.md#versioning) in the README:

1. Merge to `main` and wait for a green `Self-check`.
2. Tag an immutable release, for example `v0.1.4`, and move the short tag
   `v0.1` to the same commit. The ruleset `protect-release-tags` allows this
   only for organisation owners.
3. Publish GitHub release notes for the new tag.

Changes to documentation, templates or fixtures only need no release. GitHub
reads templates from `main`.

### Commits and pull requests

- One logical change per commit. The subject is an imperative sentence of at
  most 72 characters.
- Do not add AI attribution lines (`Co-Authored-By`, "Generated with").
- Pull request descriptions explain what changed and why. Do not add a "Test
  plan" section.
