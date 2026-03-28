# Contributing to SalesEdge

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

**Authors:** Aheli Poddar, Shuvam Banerji Seal, Alok Mishra  

Thank you for improving SalesEdge. This guide orients contributors to workflows, standards, and review expectations.

## Where to start

- Read the [documentation index](docs/README.md).  
- For connectors, follow [Adding a data source](docs/development/adding-data-source.md).  
- For scoring changes, read the [formula handbook](docs/formulas/handbook.md) and add backtests when behavior changes.

## Development workflow

1. Fork / branch from `main` (or your team’s default branch).  
2. Run `make bootstrap` once per machine.  
3. Implement changes with tests.  
4. Run `make lint`, `make typecheck`, and `make test` (or targeted subsets).  
5. Open a PR with a clear description and risk notes.

## Standards

- **Python:** Ruff + mypy strict — see [Coding standards](docs/development/coding-standards.md).  
- **TypeScript:** ESLint + Prettier + `tsc` strict.  
- **Commits:** Conventional Commits preferred.  
- **UX:** Use INR and IST helpers (`format_inr`, `formatIST`) for user-visible values.

## Security

- Never commit secrets; use `SE_*` variables per [Secret management](docs/operations/secret-management.md).  
- Report vulnerabilities through your organisation’s security channel.

## Code review

- Keep PRs focused; unrelated refactors belong in separate PRs.  
- Link issues or tickets when applicable.  
- Update docs when behavior, env vars, or APIs change.

## Changelog

User-facing or notable changes should include an entry in [CHANGELOG.md](CHANGELOG.md).

---

[Documentation index](docs/README.md)
