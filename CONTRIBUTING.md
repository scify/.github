# Contributing to SciFY projects

Thank you for your interest in a SciFY project. This file is the organisation
default. A repository can override it with its own `CONTRIBUTING.md`.

## Before you start

- Read the repository `README.md` for setup instructions.
- Search the open issues before you open a new one.
- For a large change, open an issue first and describe the change.

## Development workflow

1. Fork the repository, or create a branch if you are a SciFY member.
2. Name the branch after the change, for example `feature/export-csv` or `fix/login-redirect`.
3. Keep each pull request focused on one change.
4. Run the project checks before you push. Most repositories provide `composer check` and `npm run check`, or a `composer test` script.
5. Open a pull request against the default branch and fill in the template.

## Commit messages

- Use the imperative mood: "Add CSV export", not "Added CSV export".
- Keep the subject line under 72 characters.
- Explain why in the body when the reason is not obvious.

## Code standards

SciFY members: follow the [SciFY Engineering Guidelines](https://github.com/scify/scify-engineering-guidelines).
That repository holds the shared linter and formatter configuration for PHP, JavaScript and TypeScript.

External contributors: match the style of the surrounding code. The CI checks
will tell you if something does not pass.

## Continuous integration

Reusable GitHub Actions workflows live in [scify/.github](https://github.com/scify/.github).
See its `README.md` to add CI or deployment to a repository.

## Reporting security issues

Do not open a public issue for a security problem. Follow [SECURITY.md](SECURITY.md).
