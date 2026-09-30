# Reusable workflows

This folder holds the reusable workflows that SciFY repositories call for CI and
security checks. This guide explains how to call each workflow from your
application, which inputs it accepts, and how to solve common problems.

| Workflow | Use it for |
| --- | --- |
| [`laravel-ci.yml`](#laravel-ci) | CI for Laravel applications |
| [`node-ci.yml`](#node-ci) | CI for npm-only applications (Vue, React, TypeScript SPAs) |
| [`security.yml`](#security) | Secret, dev tool config, npm hardening and dependency audit checks for any repository |

Each workflow file also starts with a comment block that shows a full example call.
`self-check.yml` is the CI of this repository. Do not call it.

## Contents

- [How a call works](#how-a-call-works)
- [Laravel CI](#laravel-ci)
- [Node CI](#node-ci)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## How a call works

Your repository keeps a short workflow file. That file calls a workflow from
this folder as a job:

```yaml
# .github/workflows/ci.yml in your repository
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ci:                                                     # caller job id
    uses: scify/.github/.github/workflows/laravel-ci.yml@v0.1
    with:                                                 # inputs
      php-version: '8.4'
    secrets:                                              # secrets, only when the workflow declares them
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

Rules that apply to every workflow here:

- **Pin to a tag.** Use `@v0.1`, not `@main`. A `v0.x` release can change
  inputs, so read the release notes before you move to a new tag.
- **Your file owns the triggers.** `on:`, `concurrency:` and `permissions:` go in
  your file. The shared workflow only defines the jobs.
- **Inputs have defaults.** Set only the inputs that you want to change. A
  misspelled input fails the run with "input is not defined". Run
  [`actionlint`](https://github.com/rhysd/actionlint) locally to catch it early.
- **Pass secrets explicitly.** A called workflow sees only the secrets that you
  pass under `secrets:`. You can also use `secrets: inherit`, but explicit
  mapping shows what the workflow receives.
- **Check names.** GitHub names each check `<caller job id> / <job name>`. With
  the job id `ci`, the CI workflows report `ci / Static checks`, `ci / CI` and
  so on.

### Start from a template

The workflows have starter templates: SciFY Laravel CI, SciFY Node CI and SciFY
Security. Each template lists every input with its default and example values.

1. Open your repository's **Actions** tab and click **New workflow**.
2. Under "By SciFY", pick **SciFY Laravel CI**, **SciFY Node CI** or **SciFY Security**.
3. Uncomment and change only the inputs that you need.
4. Commit the file.

You can also copy [`laravel-ci.yml`](../../workflow-templates/laravel-ci.yml),
[`node-ci.yml`](../../workflow-templates/node-ci.yml) or
[`security.yml`](../../workflow-templates/security.yml) from `workflow-templates/`
by hand. Replace `$default-branch` with `main`.

### The CI model

`laravel-ci.yml` and `node-ci.yml` work the same way:

- **Parallel jobs.** Static checks, tests and (for Node) the build run in
  parallel. Browser tests are an opt-in job.
- **Auto-detect or command.** Each `*-command` input has two modes. When it is
  empty, the workflow runs only the tools that your repository is configured
  for. When you set it, the workflow runs your command instead. The command runs
  in bash, so `&&` and quotes work.
- **Coverage.** Setting `coverage-file` turns on the Codecov upload. Your test
  command must write that file.
- **One required check.** The last job, `CI`, is green when no other job failed
  or was cancelled. A skipped job counts as green. In branch protection,
  require only `ci / CI`. When you add or remove jobs later, the rule stays the
  same.

## Laravel CI

`laravel-ci.yml` runs static checks, backend tests and optional browser tests
for a Laravel application.

### Jobs

| Job | What it does |
| --- | --- |
| `Static checks` | Code style, lint and static analysis. See [auto-detection](#laravel-auto-detection). |
| `Backend tests` | Builds the frontend assets (optional), runs `test-command`, then `npm run test` if `package.json` defines it. Uploads coverage when `coverage-file` is set. |
| `Browser tests` | Builds the assets, installs Playwright Chromium, runs `browser-test-command`. Runs only with `browser-tests: true`. |
| `CI` | Aggregate check. |

Every job starts with the same setup steps. They install PHP and Composer
dependencies, optionally Node.js and npm dependencies, and prepare `.env` and
`APP_KEY`. Every command runs inside `working-directory`.

### Inputs

| Input | Default | Example values |
| --- | --- | --- |
| `working-directory` | `.` | `backend`, `apps/api` (the folder with `composer.json`) |
| `php-version` | `'8.4'` | `'8.3'` |
| `php-extensions` | `mbstring, dom, fileinfo, intl, pdo_sqlite, sqlite3, gd, zip, bcmath` | `mbstring, intl, pdo_mysql, redis` |
| `env-file` | `''` (`.env.testing` if present, else `.env.example`) | `.env.testing`, `.env.ci` (relative to `working-directory`) |
| `frontend` | `true` | `false` for a repository without `package.json` |
| `build-frontend-for-tests` | `true` | `false` when tests do not need the Vite manifest |
| `node-version-file` | `.nvmrc` (relative to the repository root) | `backend/.nvmrc`, `package.json` |
| `lint-command` | `''` (auto-detect) | `composer check` |
| `types-command` | `''` (auto-detect) | `composer check:types` |
| `analysis-cache-paths` | `/tmp/phpstan` and `/tmp/rector_cached_files` | `.phpstan-cache` and `/tmp/rector` (one path per line; absolute, or relative to the repository root) |
| `test-command` | `php artisan test` | `php artisan test --parallel`, `vendor/bin/pest --exclude-testsuite=Browser` |
| `coverage-file` | `''` (no coverage) | `coverage/clover.xml` (relative to `working-directory`) |
| `browser-tests` | `false` | `true` |
| `browser-test-command` | `vendor/bin/pest --testsuite=Browser` | `php artisan dusk` |

| Secret | Required | Purpose |
| --- | --- | --- |
| `CODECOV_TOKEN` | Only with `coverage-file` | Codecov upload token |

### Laravel auto-detection

When `lint-command` is empty, the `Static checks` job runs:

- `vendor/bin/pint --test` when `pint.json` exists
- `vendor/bin/rector --dry-run` when `rector.php` exists
- `npm run check`, or else `npm run lint`, when `frontend` is true and the script exists

When `types-command` is empty, it runs:

- `vendor/bin/phpstan analyse` when `phpstan.neon` or `phpstan.neon.dist` exists
- `npm run types`, or else `npm run type-check`, when `frontend` is true and the script exists

The job caches the PHPStan and Rector results, so later runs analyse only the
changed files. If `phpstan.neon` sets `tmpDir` or `rector.php` sets
`cacheDirectory`, set `analysis-cache-paths` to the same paths.

### Environment and database

The `.env` file comes from `env-file`. An existing `.env` is kept. The action
then runs `php artisan key:generate`.

The database comes from your `phpunit.xml` and `.env` file. The Laravel default,
SQLite in memory, needs nothing else. The workflow has no MySQL or PostgreSQL
service container.

### Laravel recipes

Minimal call, for a standard Laravel application with Pint, PHPStan and Vite:

```yaml
jobs:
  ci:
    uses: scify/.github/.github/workflows/laravel-ci.yml@v0.1
```

API without a frontend:

```yaml
jobs:
  ci:
    uses: scify/.github/.github/workflows/laravel-ci.yml@v0.1
    with:
      frontend: false
```

Composer scripts for the checks, Pest with coverage, and browser tests:

```yaml
jobs:
  ci:
    uses: scify/.github/.github/workflows/laravel-ci.yml@v0.1
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
    with:
      lint-command: composer check
      types-command: composer check:types
      analysis-cache-paths: |
        .phpstan-cache
        /tmp/rector
      test-command: vendor/bin/pest --exclude-testsuite=Browser --parallel --coverage-clover=coverage/clover.xml
      coverage-file: coverage/clover.xml
      browser-tests: true
```

Exclude the browser suite from `test-command` when you turn on `browser-tests`.
Otherwise the browser tests also run in the `Backend tests` job, which has no
browser.

## Node CI

`node-ci.yml` runs static checks, unit tests, the build and optional Playwright
tests for an npm-only application.

### Jobs

| Job | What it does |
| --- | --- |
| `Static checks` | Runs `lint-command` and `types-command`, or the npm scripts. See [auto-detection](#node-auto-detection). |
| `Unit tests` | Runs `test-command`, or `npm run test` if it exists. Uploads coverage when `coverage-file` is set. |
| `Build` | Runs `build-command`. |
| `Browser tests` | Installs the Playwright browsers, runs `build-command`, then `browser-test-command`. Runs only with `browser-tests: true`. |
| `CI` | Aggregate check. |

Every job installs Node.js and runs `npm ci`. Every command runs inside
`working-directory`.

### Inputs

| Input | Default | Example values |
| --- | --- | --- |
| `node-version-file` | `.nvmrc` (relative to the repository root) | `frontend/.nvmrc`, `package.json` |
| `node-version` | `''` | `'22'`, `'lts/*'`. Takes precedence over `node-version-file` |
| `working-directory` | `.` | `frontend`, `apps/web` |
| `lint-command` | `''` (auto-detect) | `npm run lint -- --max-warnings=0` |
| `types-command` | `''` (auto-detect) | `npx tsc --noEmit`, `npx vue-tsc --noEmit` |
| `test-command` | `''` (auto-detect) | `npx vitest run --coverage --coverage.reporter=lcov` |
| `coverage-file` | `''` (no coverage) | `coverage/lcov.info`, relative to `working-directory` |
| `build-command` | `npm run build` | `npm run build -- --mode staging` |
| `browser-tests` | `false` | `true` |
| `browser-test-command` | `npx playwright test` | `npm run test:e2e` |
| `playwright-browsers` | `chromium` | `chromium firefox webkit` (space-separated) |

| Secret | Required | Purpose |
| --- | --- | --- |
| `CODECOV_TOKEN` | Only with `coverage-file` | Codecov upload token |

### Node auto-detection

When an input is empty, the job runs the first npm script that `package.json` defines:

| Input | Scripts, in order |
| --- | --- |
| `lint-command` | `check`, `lint` |
| `types-command` | `types`, `type-check` |
| `test-command` | `test` |

When no script matches, the step prints a message and passes.

### Node recipes

Minimal call, for an application with `lint`, `type-check`, `test` and `build` scripts:

```yaml
jobs:
  ci:
    uses: scify/.github/.github/workflows/node-ci.yml@v0.1
```

Application in a subfolder, with Vitest coverage and Playwright on two browsers:

```yaml
jobs:
  ci:
    uses: scify/.github/.github/workflows/node-ci.yml@v0.1
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
    with:
      working-directory: frontend
      node-version-file: frontend/.nvmrc
      test-command: npx vitest run --coverage --coverage.reporter=lcov
      coverage-file: coverage/lcov.info
      browser-tests: true
      playwright-browsers: chromium firefox
```

If your Playwright configuration starts a preview server, `build-command` has
already built the application when the browser tests start.

## Security

`security.yml` runs four independent checks. Each check runs only when the
repository has the matching files. So the same call works for Laravel,
npm-only and PHP-only repositories.

| Job | What it checks |
| --- | --- |
| `Secrets` | Committed `.env` files anywhere in the repository, and Gitleaks. On a pull request, Gitleaks scans only the pull request's commits. On push and schedule, it scans the full git history. Examples, `.env.testing`, `.env.ci` and templates (`.dist`, `.sample`, `.template`, `.tpl`, `.j2`, `.jinja`, `.jinja2`) are allowed |
| `Dev tool configs` | Script files and suspicious commands in `.vscode`, `.claude`, `.cursor` and `.idea`. See [`scan-dev-configs`](../actions/scan-dev-configs/README.md) |
| `npm supply chain hardening` | `.npmrc` settings and lockfile. See [`verify-npm-hardening`](../actions/verify-npm-hardening/README.md) |
| `Dependency audit` | `composer audit --locked` and `npm audit` against the lock files. No install is needed |

| Input | Default | Example values |
| --- | --- | --- |
| `working-directory` | `.` | `frontend`, `apps/web`. The npm hardening and audit checks run there |
| `php-version` | `'8.4'` | `'8.3'` |
| `composer-abandoned` | `report` (list, do not fail) | `ignore`, `fail` |
| `gitleaks-full-history` | `false` (pull requests scan their own commits) | `true` (every run scans the full history) |
| `npm-min-release-age` | `'7'` | `'14'` (days; 7 or more) |
| `npm-audit-level` | `high` | `low`, `moderate`, `critical` |
| `strict-dev-configs` | `false` (warn only) | `true` (fail on suspicious commands) |
| `allowed-dev-scripts` | `''` (no scripts allowed) | `.claude/hooks/*.sh` (one glob per line; `*` also matches `/`) |

Run it on pull requests and once a week. The weekly run finds new advisories
for dependencies that did not change.

The weekly run also scans the full git history with Gitleaks, so it finds a
secret that reached `main` without a pull request.

In a public repository, GitHub disables scheduled workflows after 60 days
without repository activity, and it sends only an email. After a quiet period,
check the **Actions** tab and enable the workflow again:

```yaml
# .github/workflows/security.yml in your repository
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

When your repository keeps hook scripts in `.claude/hooks/`, review them and allow them:

```yaml
jobs:
  security:
    uses: scify/.github/.github/workflows/security.yml@v0.1
    with:
      allowed-dev-scripts: |
        .claude/hooks/*.sh
```

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| `input "..." is not defined in ... reusable workflow` | The input name is misspelled, or your tag is older than the input. Check the inputs table and your `@v0.x` tag. |
| A required check shows "Expected — Waiting for status to be reported" | Branch protection requires a check name that no longer exists, for example `ci / Node checks`. Require `ci / CI` instead. |
| `Codecov` fails on your own pull requests | The `CODECOV_TOKEN` secret is missing or not passed under `secrets:`. Pull requests from forks get no secrets, so there the upload failure does not fail the job. |
| `Environment file '...' not found` (Laravel) | Your repository has no `.env.testing` and no `.env.example`, or `env-file` points to a missing file. |
| Browser tests also run in `Backend tests` (Laravel) | Exclude the browser suite in `test-command`, for example `vendor/bin/pest --exclude-testsuite=Browser`. |
| `Environment files are committed to the repository` | A real env file, such as `.env` or `.env.production`, is committed. Remove it and rotate its secrets. A template must end in `.example`, `.dist`, `.sample`, `.template`, `.tpl`, `.j2`, `.jinja` or `.jinja2`. |
| `Found 1 abandoned package` fails the `Dependency audit` job | The caller sets `composer-abandoned: fail`. Replace the package, or set `composer-abandoned: report`. |
| `leaks found` in the `Secrets` job | Gitleaks found a secret. Rotate it first: removing it from the code does not remove it from the git history. If the finding is a false positive, add its fingerprint (printed in the log, for example `abc123:config/app.php:generic-api-key:12`) as one line to `.gitleaksignore` in the repository root. |
| The weekly security run stopped | GitHub disables scheduled workflows in a public repository after 60 days without activity. Open the workflow in the **Actions** tab and click **Enable workflow**. |
| `Script files found in dev tool directories` | A script file is in `.vscode`, `.claude`, `.cursor` or `.idea`. Remove it, or review it and add it to `allowed-dev-scripts`. |
| PHPStan or Rector re-analyse every file on each run | `analysis-cache-paths` does not match `tmpDir` in `phpstan.neon` or `cacheDirectory` in `rector.php`. |

To test an unreleased change in this repository, point your caller at the
branch: `uses: scify/.github/.github/workflows/laravel-ci.yml@my-branch`.
