# 0005. Python as the orchestrator language

- Status: Accepted
- Date: 2026-10-25

## Context

The orchestrator is written in Python because its protocol code was ported from Python sources
(rpi-rf, pilight protocol descriptions). The choice was inherited rather than made, so it was
reviewed against Java, .NET and C++, and against Go/Rust as lighter compiled options.

- The workload is small: the worst case is about 20 000 pulse durations per second, each needing a
  few comparisons and bit operations.
- Typical hosts are Raspberry Pi class machines.
- Home Assistant and most of its tooling are written in Python, and the reference material is easy
  to port to it.

## Decision

Keep Python. Robustness comes from engineering practice rather than from the language:

- type hints checked with `mypy`,
- a validated configuration model,
- unit tests feeding recorded pulse lists to the protocol decoders,
- correct MQTT reconnect and discovery handling,
- pinned dependencies.

## Consequences

- Low memory footprint and small images compared to JVM/.NET runtimes on aarch64/armv7.
- Protocol decoders can be developed quickly, which suits the reverse engineering workflow in
  [ADR-0003](0003-raw-pulse-gateway.md).
- Keeps the option of a Home Assistant custom integration open, which can only be written in Python
  (see [ADR-0006](0006-addon-vs-custom-integration.md)).
- There is no compile-time type safety by default; correctness relies on `mypy` and tests.
- Revisit (Go or Rust) only if the orchestrator grows into a large, performance-sensitive
  multi-protocol service.
