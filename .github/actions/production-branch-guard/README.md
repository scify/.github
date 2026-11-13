# production-branch-guard

Composite GitHub Action that fails unless a pull request comes from an allowed branch of the same repository. The reusable workflow [`production-branch-guard.yml`](../../workflows/production-branch-guard.yml) runs it on pull requests into a deploy branch, for example `production`. Call the workflow, not this action. See the [workflow guide](../../workflows/README.md#production-branch-guard).

## What it checks

| Check | What triggers a failure |
|-------|----------------------|
| Source | `head-ref` or `head-repository` is empty, for example because the event is not a pull request |
| Fork | `head-repository` is not `repository`. A fork can have a branch named `main` |
| Branch | `head-ref` matches no line of `allowed-branches` |

Each line of `allowed-branches` is a shell glob. `*` also matches `/`, so `hotfix/*` matches `hotfix/a/b`. A line matches the whole branch name: `hotfix/*` does not match `hotfixes`. `|` is not an "or": put each glob on its own line.

The action checks out no code and runs no code from the pull request. It only compares names.

## Inputs

| Name | Default | Description |
| --- | --- | --- |
| `allowed-branches` | `main` | Newline-separated glob patterns of source branches that may merge. Example: `main`, `hotfix/*` |
| `head-ref` | required | The source branch of the pull request: `github.event.pull_request.head.ref` |
| `head-repository` | required | The repository of the source branch: `github.event.pull_request.head.repo.full_name` |
| `repository` | `github.repository` | This repository, as `owner/name`. A different `head-repository` is a fork |

```yaml
- uses: scify/.github/.github/actions/production-branch-guard@<commit-sha> # v0.1
  with:
    allowed-branches: |
      main
      hotfix/*
    head-ref: ${{ github.event.pull_request.head.ref }}
    head-repository: ${{ github.event.pull_request.head.repo.full_name }}
```
