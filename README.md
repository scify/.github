# scify/.github

WIP: Organisation-wide defaults and shared CI for [SciFY](https://github.com/scify) repositories.

This repository is public. GitHub requires that for the default files, the profile
README and the workflow templates to take effect. Do not commit secrets, hostnames
or internal URLs here.

## Scope

This repository holds only content that is safe to publish:

- Community health files and the organisation profile
- Reusable CI and security workflows, and the composite actions they use
- Workflow templates and Dependabot templates

Deployment workflows do not belong here. They need server details and
deployment secrets, so they will live in a separate private repository.

## What is in here

| Path | Purpose | How it reaches other repositories |
| --- | --- | --- |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/` | Default community health files | Automatic. Applies to every scify repository that has no file of its own. |
| `profile/README.md` | Organisation profile page | Automatic. Shown on https://github.com/scify. |
| `workflow-templates/` | Starter workflows | Actions tab → New workflow → "By SciFY". The developer gets a copy. Templates exist for Laravel CI and Node CI. |
| `.github/workflows/*.yml` | Reusable workflows (`workflow_call`) | Called with `uses: scify/.github/.github/workflows/<name>.yml@v0.1`. One implementation, shared by all callers. |
| `.github/actions/*/` | Composite actions | Called as a step with `uses: scify/.github/.github/actions/<name>@v0.1`. Each folder has its own README. |
| `templates/dependabot-*.yml` | Dependabot configuration | Manual copy to `.github/dependabot.yml`. GitHub has no default mechanism for Dependabot. |
| `tests/fixtures/`, `scripts/` | Fixture projects and checker scripts for this repository's own CI (`self-check.yml`) | Not used by other repositories. |

## Reusable workflows

| Workflow | For |
| --- | --- |
| `laravel-ci.yml` | CI for Laravel applications |
| `node-ci.yml` | CI for npm-only applications |
| `security.yml` | Secret, dev tool config, npm hardening and dependency audit checks |

To use them in your application, read the
[workflow guide](.github/workflows/README.md). It explains how a call works,
lists every input with example values, and gives recipes and troubleshooting.

The quickest start for CI: open your repository's **Actions** tab, click
**New workflow**, and pick **SciFY Laravel CI** or **SciFY Node CI**.

## Dependabot

Dependabot reads only the repository's own `.github/dependabot.yml`. There is
no include mechanism, so the templates are copied once and then owned by that
repository. Pick the matching template:

- `templates/dependabot-laravel.yml` for Composer + npm + GitHub Actions
- `templates/dependabot-node.yml` for npm + GitHub Actions
- `templates/dependabot-wordpress.yml` for WordPress themes and plugins. Read its header: WordPress core and wp-admin plugins are not tracked.

From the target repository's root:

```bash
mkdir -p .github
curl -sSfL https://raw.githubusercontent.com/scify/.github/v0.1/templates/dependabot-laravel.yml -o .github/dependabot.yml
```

Then enable "Dependabot security updates" in the repository's Security
settings and commit the file.

All three templates configure **security updates only**. A change to a
template does not reach existing copies. Re-run the command to pick it up.

## Maintaining this repository

### Versioning

This repository is work in progress. Releases are tagged `v0.x` and callers
pin to the current one, `v0.1`. Any `v0.x` release may change inputs or
defaults. When the workflows have run in real repositories for a while, `v1`
becomes the first stable tag and moves forward only for backwards-compatible
fixes.

To publish a new release:

1. Update every `@v0.x` reference in the documentation and comments to the new
   tag. The self-check fails when they differ.
2. Tag and push:

   ```bash
   git tag v0.2 && git push origin v0.2
   ```

### Composite actions and the release tag

The organisation requires every action to be pinned to a full commit SHA, and
this includes actions from `scify/.github`. Reusable workflows can still be
called by tag. So:

- `security.yml` does not call its actions by tag. It checks out `scify/.github`
  at `job.workflow_sha`, the commit of the workflow file itself, and runs the
  actions from that local path. The actions always match the workflow version.
- `laravel-ci.yml` and `node-ci.yml` use no composite actions. They share setup
  steps between jobs with YAML anchors (`&name` and `*name`).

A branch test therefore runs the branch code everywhere. The `@v0.1` references
that remain are in comments and documentation. The self-check fails when they
differ.

### Rules for changes

- Add only content that is safe to publish. Deployment workflows and anything that needs server details go to the private repository.
- Pin every third-party action to a full commit SHA with the version in a trailing comment.
- Keep reusable workflows tolerant: run a tool only when the repository is configured for it.
- Test a change by pointing a caller at your branch: `uses: scify/.github/.github/workflows/laravel-ci.yml@my-branch`.
- The `Self-check` workflow (`.github/workflows/self-check.yml`) runs on every push and pull request. It runs actionlint with shellcheck, runs shellcheck on the composite actions, and checks that the workflow guide lists every input. Run the same checks locally before you push:

  ```bash
  actionlint .github/workflows/*.yml
  python3 scripts/shellcheck-actions.py
  python3 scripts/check-workflow-docs.py
  ```
