# Architecture Decision Records

This folder records the significant architectural decisions of the project, one decision per file,
using the format described in [ADR-0001](0001-record-architecture-decisions.md).

## Workflow

1. Copy [`template.md`](template.md) to `NNNN-short-title.md`, using the next free number.
2. Fill it in with status **Proposed** and open it for discussion.
3. When agreed, change the status to **Accepted**. ADRs are not edited after acceptance except for
   their status; to change a decision, write a new ADR and mark the old one
   **Superseded by ADR-NNNN**.

## Index

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-single-repository.md) | Keep the ESPHome component and the HA add-on in one repository | Accepted |
| [0003](0003-raw-pulse-gateway.md) | ESP acts as a raw pulse gateway, decoding happens on the HA side | Accepted |
| [0004](0004-mqtt-pulse-wire-format.md) | MQTT topics and pulse list wire format | Accepted |
| [0005](0005-python-for-orchestrator.md) | Python as the orchestrator language | Accepted |
| [0006](0006-addon-vs-custom-integration.md) | Deliver the orchestrator as an add-on or as a custom integration | Proposed |
| [0007](0007-gateway-transport.md) | Transport between the gateway and the orchestrator | Proposed |
| [0008](0008-firmware-on-esphome-components.md) | Build the firmware on ESPHome's built-in components | Proposed |
| [0009](0009-raw-pulse-wire-format-v2.md) | Raw pulse wire format v2: signed durations, one frame per message | Proposed |
