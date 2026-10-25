# 0007. Transport between the gateway and the orchestrator

- Status: Proposed
- Date: 2026-10-25

## Context

The gateway and the orchestrator talk over MQTT ([ADR-0004](0004-mqtt-pulse-wire-format.md)). MQTT
was picked during the proof of concept because raw pulses are easy to watch and inject for
debugging, not for architectural reasons. The cost is a required broker, separate credentials, and
hand-rolled topic conventions.

The ESPHome native API is the usual channel between ESPHome devices and Home Assistant. Python
clients other than Home Assistant can connect to it through `aioesphomeapi`.

## Options

1. **Keep MQTT** for everything.
2. **Native API for the gateway link**: expose pulse RX as events or a text sensor and TX as an API
   action. Use ESPHome's own logs (`esphome logs`) for debugging, or keep MQTT as an optional
   debug-only channel.
3. **Hybrid**: use the native API in normal operation and enable MQTT pulse mirroring only when
   reverse engineering a new device.

## Open questions

- Can the native API carry about 2048 pulses every 100 ms reliably?
- Does the choice in [ADR-0006](0006-addon-vs-custom-integration.md) favour one option? A custom
  integration would naturally use the native API.
- How do raw sniffing and replay ([ADR-0003](0003-raw-pulse-gateway.md)) work without MQTT tooling?

## Decision

Open.

## Consequences

To be filled in when accepted.
