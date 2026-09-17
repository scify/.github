# SciFY Security Policy

This policy applies to every repository in the SciFY GitHub organisation that
does not have its own `SECURITY.md`.

## Reporting a vulnerability

Do not report security vulnerabilities through public GitHub issues, pull
requests, or discussions.

Use one of these private channels:

1. The **Report a vulnerability** button on the repository's **Security** tab.
   This opens a private advisory that only the maintainers can read.
2. Email to <info@scify.org> with "Security" in the subject line.

Include in the report:

- the repository and the version, tag, or commit affected,
- steps to reproduce the problem,
- the impact you expect.

We confirm that we received the report and keep you informed while we work on
a fix. We ask you to give us reasonable time to fix the problem before you
disclose it publicly.

## What to expect

SciFY is a non-profit organisation. Our software is released under the
Apache 2.0 licence and is maintained by a small team.

- **No formal SLA.** We fix confirmed vulnerabilities as fast as our capacity
  allows, and we prioritise by severity.
- **Latest version only.** Security fixes go into the default branch and the
  next release. We do not backport fixes to older releases.
- **Services we operate** run the latest version of the software, so a fix
  reaches them when it is released.

## Dependency updates

SciFY repositories use Dependabot security updates. See the `templates/`
folder in [scify/.github](https://github.com/scify/.github) for the shared configuration.
