# 0001. Record architecture decisions

- Status: Accepted
- Date: 2026-10-25

## Context

The project spans two runtimes (ESP firmware and a Home Assistant side service) that communicate over
an implicit contract. Decisions about where logic lives and how the parts talk to each other are
easy to forget and hard to reconstruct from the code alone.

## Decision

Significant architectural decisions are recorded as Architecture Decision Records in `docs/adr/`,
following Michael Nygard's format (Context, Decision, Consequences) with a status and a date.
Files are numbered sequentially and never renumbered.

## Consequences

- New contributors (and future us) can see why things are the way they are.
- Changing a recorded decision requires writing a new ADR that supersedes the old one.
- Small overhead per decision; trivial or easily reversible choices do not need an ADR.
