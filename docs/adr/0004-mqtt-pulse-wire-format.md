# 0004. MQTT topics and pulse list wire format

- Status: Accepted
- Date: 2026-10-25

## Context

The ESP gateway and the orchestrator communicate only through MQTT
(see [ADR-0003](0003-raw-pulse-gateway.md)). MQTT was chosen because it is easy to debug: any MQTT
client can watch the raw pulses and inject test pulse lists. The project started as a proof of
concept and has kept this transport since; [ADR-0007](0007-gateway-transport.md) considers
alternatives.

This contract is implicit in the code on both sides and must be changed in step.

## Decision

This ADR documents the contract as implemented today.

### Gateway ⇄ orchestrator

| Topic | Direction | Payload |
| --- | --- | --- |
| `rfproxys3/sensor/pulse_list` | ESP → orchestrator | Space-separated pulse durations in µs, published every 100 ms when non-empty (max 2048 per message). |
| `rfproxys3/send/pulse_list` | orchestrator → ESP | `<inverted> <d1> <d2> ... `: a first value of `0` means inverted output and any other value means normal, followed by alternating high/low durations in µs. Must end with a trailing space. |

### Orchestrator ⇄ Home Assistant

| Topic | Direction | Payload |
| --- | --- | --- |
| `homeassistant/sensor/<id>/config`, `homeassistant/switch/<id>/config` | orchestrator → HA | MQTT discovery configs. |
| `orchestrator/sensor/th_sensor/<channel>-<device_id>` | orchestrator → HA | JSON: `id`, `battery`, `tx_mode`, `channel`, `temperature`, `humidity`, `timestamp`. |
| `orchestrator/switch/<id>` | orchestrator → HA | `ON` / `OFF` when a matching code is received. |
| `orchestrator/switch/command` | HA → orchestrator | JSON: `{ "state": "ON"\|"OFF", "id": "<home_assistant_id>" }`. |
| `orchestrator/switch/last` | orchestrator → (debug) | JSON: last decoded RCSwitch `code`, `protocol`, `pulselength`. |

## Consequences

- Any change to these tables is a breaking change: it must update both the firmware and the
  orchestrator, and this ADR must be superseded.
- The `rfproxys3` prefix is hardcoded, so only one gateway can share a broker. One gateway is enough
  for now. Several gateways for wider coverage were considered early on and would need a
  per-gateway prefix, plus de-duplication of signals received by more than one gateway.
- The trailing space is required by the firmware parser.
