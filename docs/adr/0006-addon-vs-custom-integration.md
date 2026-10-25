# 0006. Deliver the orchestrator as an add-on or as a custom integration

- Status: Proposed
- Date: 2026-10-25

## Context

The orchestrator is currently a Home Assistant add-on: a Docker container run by the Supervisor,
talking to Home Assistant through MQTT discovery.

- The current targets are Home Assistant OS and Supervised, which both support add-ons. Container
  and Core installations may become targets later, and they cannot run add-ons.
- The add-on needs its own MQTT credentials and configures devices through JSON strings in the
  add-on options.
- A custom integration (installed via HACS) runs inside Home Assistant on every installation type,
  can reuse Home Assistant's MQTT connection and can offer a config flow UI for devices. It is tied
  to Home Assistant's Python version and internal APIs.

## Options

1. Keep the add-on and improve it: use `services: mqtt:need` and a structured options schema.
2. Convert the orchestrator to a custom integration.
3. Keep the protocol code as a standalone library used by either packaging, so option 2 stays cheap
   to adopt when Container/Core support is wanted.

## Decision

Open. To be decided before larger investment in the orchestrator. Also depends on
[ADR-0007](0007-gateway-transport.md).

## Consequences

To be filled in when accepted.
