# Contribution Guide

This repository uses a simple portfolio-friendly Git flow.

## Branches

```text
main      -> production-ready branch
develop   -> integration branch
feature/* -> new features
fix/*     -> bug fixes
chore/*   -> documentation, tooling or maintenance
```

## Workflow

```text
feature/my-change -> develop -> main
```

1. Create an issue in Spanish when planning the task.
2. Create a branch with an English name.
3. Open a pull request with an English title and summary.
4. Wait for CI to pass.
5. Merge into `develop`.
6. Promote `develop` into `main` when ready for release.

## Commit style

Use short, descriptive commits:

```text
feat: add task statistics endpoint
fix: validate blank task titles
chore: add docker support
```
