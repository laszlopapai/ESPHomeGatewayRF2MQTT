# 0009. Raw pulse wire format v2: signed durations, one frame per message

- Status: Proposed
- Date: 2026-10-25

## Context

The current gateway ⇄ orchestrator format ([ADR-0004](0004-mqtt-pulse-wire-format.md)) has several
weaknesses:

- Received pulses are unsigned edge-to-edge durations collected for 100 ms. Whether a pulse was
  high or low is lost, and frames are split arbitrarily across messages.
- Transmit requests start with an "inverted" flag and must end with a trailing space.
- Topics are hardcoded to `rfproxys3/...`.

With [ADR-0008](0008-firmware-on-esphome-components.md), the firmware uses `remote_receiver` and
`remote_transmitter`. Both work with signed durations in µs: positive values are high (mark),
negative values are low (space). The receiver delivers one list per frame, ending when the signal
has been idle for the configured `idle` time.

## Decision

| Topic | Direction | Payload |
| --- | --- | --- |
| `<prefix>/rx` | gateway → orchestrator | One received frame: space-separated signed durations in µs, starting with a positive value. The trailing idle gap is not included. |
| `<prefix>/tx` | orchestrator → gateway | One pulse train to send, in the same format. Repeats are included in the list by the orchestrator. |

- `<prefix>` is set per device with the `rf_topic_prefix` substitution (e.g. `rfproxys3/rf`). This
  allows more than one gateway per broker.
- Both directions use the same format. A frame captured on `rx` (or copied from the ESPHome log with
  `dump: raw`) can be published unchanged on `tx` to replay it, which supports the reverse
  engineering workflow from [ADR-0003](0003-raw-pulse-gateway.md).
- The orchestrator appends a synthetic gap after each received frame before feeding its decoders,
  since decoders use long gaps to detect frame boundaries.
- When accepted, this supersedes the gateway ⇄ orchestrator section of
  [ADR-0004](0004-mqtt-pulse-wire-format.md). The orchestrator ⇄ Home Assistant section stays valid.

## Consequences

- Breaking change: the firmware and the orchestrator must switch together. With a single gateway
  this is a hard switch (add-on 0.1.0 speaks only v2) rather than a period of supporting both formats.
- Decoders get mark/space information and whole frames instead of arbitrary 100 ms slices.
- Transmit payloads grow with the number of repeats (about 2–3 kB for 10 repeats of a 24-bit
  RCSwitch code).
- The format is transport-neutral: the same integer list could be carried by a native API event or
  action if [ADR-0007](0007-gateway-transport.md) moves away from MQTT.
