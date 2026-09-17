# scify/.github

WIP: Organisation-wide defaults and reusable GitHub Actions for [SciFY](https://github.com/scify) repositories.

This repository is public. GitHub requires that for the default files, the profile
README and the workflow templates to take effect. Do not commit secrets, hostnames
or internal URLs here.

## What is in here

| Path | Purpose | How it reaches other repositories |
| --- | --- | --- |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/` | Default community health files | Automatic. Applies to every scify repository that has no file of its own. |
| `profile/README.md` | Organisation profile page | Automatic. Shown on https://github.com/scify. |
| `workflow-templates/` | Starter workflows | Actions tab → New workflow → "By SciFY". The developer gets a copy. Only the Laravel CI template exists so far. Node and deploy templates come later. |
| `.github/workflows/*.yml` | Reusable workflows (`workflow_call`) | Called with `uses: scify/.github/.github/workflows/<name>.yml@v0.1`. One implementation, shared by all callers. |
| `.github/actions/*/` | Composite actions | Called as a step with `uses: scify/.github/.github/actions/<name>@v0.1`. Each folder has its own README. |
| `templates/dependabot-*.yml` | Dependabot configuration | Manual copy to `.github/dependabot.yml`. GitHub has no default mechanism for Dependabot. |

## Reusable workflows

| Workflow | For | Inputs of note |
| --- | --- | --- |
| `laravel-ci.yml` | Laravel repositories | `php-version`, `frontend`, `build-frontend-for-tests` |
| `node-ci.yml` | npm-only repositories | `node-version`, `working-directory`, `build-command` |
| `laravel-deploy.yml` | Laravel app to a SciFY server over SSH | `environment`, `php-binary`, `build-command`, `extra-exclude`, `extra-checkout-*` |
| `node-deploy.yml` | Static frontend build to a server over SSH | `environment`, `build-directory`, `delete-remote-files` |
| `security.yml` | Any repository. Committed `.env` files, Gitleaks, dev tool configs, npm hardening, `composer audit`, `npm audit` | `php-version`, `npm-audit-level`, `strict-dev-configs` |
| `license-check.yml` | Opt-in. Allow-list check of Composer and npm production licences. Not for WordPress repositories | `allowed-licenses` |
| `owasp-dependency-check.yml` | Opt-in. OWASP Dependency-Check HTML report | `fail-on-cvss`, secret `NVD_API_KEY` |

Each file starts with a comment block that lists every input, secret and server requirement.

### Add CI to a repository

Laravel repositories:

1. Open the repository's **Actions** tab and click **New workflow**.
2. Pick **SciFY Laravel CI** under "By SciFY".
3. Adjust the inputs in the generated file and commit it.

Or copy `workflow-templates/laravel-ci.yml` by hand into `.github/workflows/ci.yml`
and replace `$default-branch` with `main`.

npm-only repositories have no template yet. Create `.github/workflows/ci.yml` with:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read
jobs:
  ci:
    uses: scify/.github/.github/workflows/node-ci.yml@v0.1
```

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

3. Create `.github/workflows/deploy-production.yml`. There is no template yet. For Laravel:

   ```yaml
   name: Deploy production
   on:
     workflow_dispatch:
   permissions:
     contents: read
   jobs:
     deploy:
       uses: scify/.github/.github/workflows/laravel-deploy.yml@v0.1
       with:
         environment: production
       secrets:
         SSH_HOST: ${{ secrets.SSH_HOST }}
         SSH_PORT: ${{ secrets.SSH_PORT }}
         SSH_USER: ${{ secrets.SSH_USER }}
         SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
         PROJECT_PATH: ${{ secrets.PROJECT_PATH }}
         ENV_FILE: ${{ secrets.ENV_FILE }}
   ```

   For a static frontend, call `node-deploy.yml` instead with the same secrets.
4. Run it from the Actions tab with **Run workflow**.

Laravel-specific server requirements are listed at the top of `.github/workflows/laravel-deploy.yml`.

### Add security scanning to a repository

Create `.github/workflows/security.yml`:

```yaml
name: Security
on:
  pull_request:
  schedule:
    - cron: '0 11 * * 1'
permissions:
  contents: read
jobs:
  security:
    uses: scify/.github/.github/workflows/security.yml@v0.1
```

Every check skips itself when the repository lacks the matching files, so the
same call works for Laravel, npm-only and PHP-only repositories. The npm
hardening check expects the `.npmrc` described in
`.github/actions/verify-npm-hardening/README.md`.

Licence and OWASP scans are separate workflows. Add a job that calls
`license-check.yml` or `owasp-dependency-check.yml` when a project needs them.

### Versioning

This repository is work in progress. Releases are tagged `v0.x` and callers
pin to the current one, `v0.1`. Any `v0.x` release may change inputs or
defaults. When the workflows have run in real repositories for a while, `v1`
becomes the first stable tag and moves forward only for backwards-compatible
fixes.

To publish a new release:

1. Update every `@v0.x` reference in this repository to the new tag. The
   `security.yml` workflow calls the composite actions by tag, so a missing
   update breaks it.
2. Tag and push:

   ```bash
   git tag v0.2 && git push origin v0.2
   ```

### Composite actions and the release tag

A reusable workflow cannot reference a sibling action by relative path, so
`security.yml` calls the actions in this repository as
`scify/.github/.github/actions/<name>@v0.1`. When you test a workflow change on a
branch, the actions still come from `v1`. Move the tag after both are merged.

## Dependabot

Copy the matching template to `.github/dependabot.yml` in the repository:

- `templates/dependabot-laravel.yml` for Composer + npm + GitHub Actions
- `templates/dependabot-node.yml` for npm + GitHub Actions
- `templates/dependabot-wordpress.yml` for WordPress themes and plugins. Read its header: WordPress core and wp-admin plugins are not tracked.

Both files configure **security updates only**. Enable "Dependabot security
updates" in the repository's Security settings as well.

## Contributing to this repository

- Pin every third-party action to a full commit SHA with the version in a trailing comment.
- Keep reusable workflows tolerant: run a tool only when the repository is configured for it.
- Test a change by pointing a caller at your branch: `uses: scify/.github/.github/workflows/laravel-ci.yml@my-branch`.
- Run `actionlint` before you push.
