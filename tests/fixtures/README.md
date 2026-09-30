# Fixtures

Sample projects for the CI of this repository. No other repository uses them.

`.github/workflows/self-check.yml` calls `laravel-ci.yml`, `node-ci.yml` and
`security.yml` by local path, with `working-directory` set to a folder here. It
also runs the composite actions against these folders. A pull request
therefore runs its own workflow changes against a real project before any
caller receives them. actionlint checks the syntax. These runs catch the
runtime errors that actionlint cannot see, such as wrong paths or a wrong step
order.

| Folder | Contents | Smoke-test jobs |
| --- | --- | --- |
| `laravel/` | The `laravel/laravel` skeleton, with `pint.json` and `.nvmrc` added | `laravel-defaults`, `laravel-commands` |
| `node/` | A project without dependencies, with `lint`, `type-check`, `test` and `build` scripts | `node-defaults`, `node-commands`, `security-actions` |
| `dev-configs/` | A `.claude` hook script and editor settings | `security-actions` |
| `security/` | `composer.lock` and `package-lock.json` without dependencies, a hardened `.npmrc`, and a Jinja `.env` template | `security-fixture` |

## Refresh the Laravel fixture

Refresh it when a new Laravel major version is out, or when its dependencies
show security alerts. From the repository root:

```bash
composer create-project laravel/laravel /tmp/laravel-fixture --no-scripts --no-interaction
cd /tmp/laravel-fixture
rm -f AGENTS.md CLAUDE.md README.md
npm install --ignore-scripts --no-audit --no-fund
cd -
cp tests/fixtures/laravel/pint.json tests/fixtures/laravel/.nvmrc /tmp/laravel-fixture/
rm -rf tests/fixtures/laravel
mkdir tests/fixtures/laravel
cd /tmp/laravel-fixture && git init -q && git add -A && git ls-files > /tmp/laravel-fixture-files.txt && cd -
rsync -a --files-from=/tmp/laravel-fixture-files.txt /tmp/laravel-fixture/ tests/fixtures/laravel/
```

- `--no-scripts` stops Composer from creating `.env` and a database file.
- Remove `CLAUDE.md` and `AGENTS.md`. Agent tools load them for the whole repository.
- The `git ls-files` step copies only the files that the skeleton's `.gitignore`
  allows, so `vendor/`, `node_modules/` and `.env` stay out.

Security alerts for the fixture dependencies appear in this repository's
Security tab. The fixtures never run in production. Refresh the fixture, or
dismiss the alert as "used in tests".
