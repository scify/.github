# Contributing

This file is the SciFY organisation default. A repository can override it with
its own `CONTRIBUTING.md`.

When you want to contribute a change, first discuss it with the owners of the
repository. Open an issue, or contact us at <info@scify.org>. This avoids work
on changes that the project cannot accept.

## Code of conduct

We have a [code of conduct](CODE_OF_CONDUCT.md). Follow it in all your
interactions with the project.

## Pull request process

1. Keep each pull request focused on one change. Open separate pull requests
   for unrelated changes.
2. Run the project's checks before you push. Most SciFY repositories provide
   `composer check` and `npm run check`, or a `composer test` script. The
   repository `README.md` documents the exact commands.
3. Update the `README.md` when your change affects how the project is set up
   or used. This includes new environment variables, configuration options,
   and useful file locations.
4. When the repository publishes versioned releases, increase the version
   number in the example files and the `README.md` to the version this pull
   request represents. We use [SemVer](https://semver.org/).
5. You may merge the pull request once you have the sign-off of two other
   developers. If you do not have permission to merge, ask the second reviewer
   to merge it for you.

## Reporting security issues

Do not open a public issue for a security problem. Follow [SECURITY.md](SECURITY.md).
