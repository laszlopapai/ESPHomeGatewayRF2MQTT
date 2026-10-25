# 0008. Build the firmware on ESPHome's built-in components

- Status: Proposed
- Date: 2026-10-25

## Context

The gateway firmware is a custom external component (`components/CC1101_MQTT/`) built on bundled
Arduino libraries: the ELECHOUSE CC1101 driver, RCSwitch and a second, unused CC1101 driver
(`cc1101_dev`). This causes several problems:

- It calls Arduino APIs directly (`SPI.h`, `digitalWrite`, `attachInterrupt`, `micros`), so the
  device must be built with the Arduino framework, which produces a larger firmware than ESP-IDF.
- It bypasses ESPHome's SPI bus. The `spi:` block in the device config is unused, and the radio
  runs its own SPI on separately configured pins.
- Pulse capture and replay are hand-written. The edge interrupt pushes into a `std::vector`, the
  transmit loop blocks the main loop with `delayMicroseconds`, and RX/TX switching waits up to 5 s.
- The bundled third-party code carries other licenses (RCSwitch is LGPL; the ELECHOUSE license is
  unclear), which blocks choosing a license for the project.

ESPHome now ships the building blocks itself:

- `cc1101` configures the radio over ESPHome's SPI bus and provides `cc1101.begin_tx` /
  `cc1101.begin_rx` actions.
- `remote_receiver` and `remote_transmitter` capture and generate pulse trains with the ESP32 RMT
  peripheral, using hardware timing. They work with both Arduino and ESP-IDF. Received data is
  exposed as signed durations in µs via `on_raw`, and `transmit_raw` sends such a list.
- The recommended wiring is GDO0 to `remote_transmitter` and GDO2 to `remote_receiver`, which
  matches the existing hardware (GDO0 = GPIO14, GDO2 = GPIO46).

## Decision

- Replace the custom component with ESPHome's `cc1101`, `remote_receiver` and `remote_transmitter`,
  built with the ESP-IDF framework.
- The glue between radio and transport (formatting received frames, parsing transmit requests) is
  YAML with small lambdas, shipped from this repository as an ESPHome YAML package
  (`firmware/rf_gateway.yaml`). Device configs include it with `packages:`.
- No custom C++ component for now. If the glue outgrows lambdas, a new component is written against
  ESPHome APIs only (no Arduino calls), so ESP-IDF keeps working.
- `components/CC1101_MQTT/` stays until the package matches the old firmware on real devices, then
  it is deleted together with the bundled libraries.

This amends the repository layout in [ADR-0002](0002-single-repository.md): `firmware/` holds the
package and device configs, and `components/` goes away once the old firmware is removed.

## Consequences

- Smaller ESP-IDF firmware. Arduino-only libraries are no longer needed.
- RMT hardware timing replaces the interrupt and busy-wait code. The old interrupt-safety, blocking
  transmit and slow RX/TX switching problems go away.
- After the bundled libraries are deleted, the repository only contains its own code, so any
  license can be chosen.
- Radio settings (frequency, modulation, bandwidth, output power) become plain configuration.
- The wire format changes to ESPHome's signed raw format ([ADR-0009](0009-raw-pulse-wire-format-v2.md)).
- Receiver tuning becomes configuration that must be verified on hardware:
  - `idle` must be longer than the longest gap inside a frame (for example the RCSwitch protocol 1
    sync gap of about 10.9 ms) and shorter than the pause between transmissions.
  - The receive buffer must hold a whole burst of repeats.
  - `filter` / `filter_symbols` should drop CC1101 noise without dropping real pulses.
- MQTT on ESP-IDF is marked experimental in the ESPHome docs. This is another input for
  [ADR-0007](0007-gateway-transport.md).
- Depends on the ESPHome release that contains the `cc1101` component. The device must be updated to
  at least that release.
