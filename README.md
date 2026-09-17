# scify/.github

Organisation-wide defaults and reusable GitHub Actions for [SciFY](https://github.com/scify) repositories.

This repository is public. GitHub requires that for the default files, the profile
README and the workflow templates to take effect. Do not commit secrets, hostnames
or internal URLs here.

## What is in here

| Path | Purpose | How it reaches other repositories |
| --- | --- | --- |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/` | Default community health files | Automatic. Applies to every scify repository that has no file of its own. |
| `profile/README.md` | Organisation profile page | Automatic. Shown on https://github.com/scify. |
| `workflow-templates/` | Starter workflows | Actions tab → New workflow → "By SciFY". The developer gets a copy. |
| `.github/workflows/*.yml` | Reusable workflows (`workflow_call`) | Called with `uses: scify/.github/.github/workflows/<name>.yml@v1`. One implementation, shared by all callers. |
| `templates/dependabot-*.yml` | Dependabot configuration | Manual copy to `.github/dependabot.yml`. GitHub has no default mechanism for Dependabot. |

## Reusable workflows

| Workflow | For | Inputs of note |
| --- | --- | --- |
| `laravel-ci.yml` | Laravel repositories | `php-version`, `frontend`, `build-frontend-for-tests` |
| `node-ci.yml` | npm-only repositories | `node-version`, `working-directory`, `build-command` |
| `laravel-deploy.yml` | Laravel app to a SciFY server over SSH | `environment`, `php-binary`, `build-command`, `extra-exclude`, `extra-checkout-*` |
| `node-deploy.yml` | Static frontend build to a server over SSH | `environment`, `build-directory`, `delete-remote-files` |

Each file starts with a comment block that lists every input, secret and server requirement.

### Add CI to a repository

1. Open the repository's **Actions** tab and click **New workflow**.
2. Pick **SciFY Laravel CI** or **SciFY Node CI** under "By SciFY".
3. Adjust the inputs in the generated file and commit it.

Or copy the file from `workflow-templates/` by hand into `.github/workflows/ci.yml`
and replace `$default-branch` with `main`.

### Add deployment to a repository

1. Create a GitHub **environment** named `production` in the repository settings.
2. Add these environment secrets:

   | Secret | Value |
   | --- | --- |
   | `SSH_HOST` | Server hostname or IP |
   | `SSH_PORT` | SSH port. Optional, defaults to 22 |
   | `SSH_USER` | Deploy user |
   | `SSH_PRIVATE_KEY` | Private key of the deploy user |
   | `PROJECT_PATH` | Absolute path of the application on the server |
   | `ENV_FILE` | Full content of the production `.env`. Optional for Laravel: when empty, the `.env` already on the server is kept |

3. Add the **SciFY Laravel deploy** or **SciFY Node deploy** template.
4. Run it from the Actions tab with **Run workflow**.

Laravel-specific server requirements are listed at the top of `.github/workflows/laravel-deploy.yml`.

### Versioning

Callers pin to the `v1` tag. Backwards-compatible fixes move the tag forward:

```bash
git tag -f v1 && git push -f origin v1
```

A breaking change (renamed input, removed secret, changed default) gets a new
major tag `v2`, and callers migrate on their own schedule. Never point `v1`
at a breaking change.

### Why no composite actions yet

A reusable workflow cannot reference a sibling action by relative path. It
would need `uses: scify/.github/actions/<name>@<ref>`, which brings its own
pinning problem. Steps stay inline until a second consumer needs the same steps.

## Dependabot

Copy the matching template to `.github/dependabot.yml` in the repository:

- `templates/dependabot-laravel.yml` for Composer + npm + GitHub Actions
- `templates/dependabot-node.yml` for npm + GitHub Actions

Both files configure **security updates only**. Enable "Dependabot security
updates" in the repository's Security settings as well.

## Contributing to this repository

- Pin every third-party action to a full commit SHA with the version in a trailing comment.
- Keep reusable workflows tolerant: run a tool only when the repository is configured for it.
- Test a change by pointing a caller at your branch: `uses: scify/.github/.github/workflows/laravel-ci.yml@my-branch`.
- Run `actionlint` before you push.
