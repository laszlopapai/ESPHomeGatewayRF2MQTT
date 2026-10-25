# 0003. ESP acts as a raw pulse gateway, decoding happens on the HA side

- Status: Accepted
- Date: 2026-10-25

## Context

433 MHz devices (RCSwitch style sockets and remotes, Alecto WS1700 style temperature/humidity
sensors, other sensors, blinds/covers, ...) each use their own OOK pulse encoding, and they usually
do not advertise which protocol they use. Supporting a new device often means sniffing its signals
(pressing a remote button, or waiting for a sensor to transmit), reverse engineering the protocol
from the pulse timings, and checking that replayed or generated pulses actually operate the device.

ESPHome already offers `remote_receiver` / `remote_transmitter` with built-in RCSwitch support, but
it only covers known protocols, and adding a new one means writing C++ and reflashing the gateway.

The gateway hardware is an ESP32-S3 with a CC1101 module.

## Decision

The ESP firmware does no protocol decoding. It only:

- timestamps signal edges from the CC1101 (GDO2) and publishes the pulse durations, and
- replays pulse durations it receives on the CC1101 (GDO0).

All protocol knowledge (decoding received pulses, encoding commands into pulses, device
configuration, Home Assistant discovery) lives in the orchestrator.

## Consequences

- The gateway doubles as a sniffing and replay tool for reverse engineering unknown devices.
- New protocols and devices are added without reflashing the firmware.
- Protocol code is easy to test with recorded pulse lists.
- The link carries a lot of raw data: the CC1101 outputs noise in OOK RX mode, so the ESP publishes
  pulses continuously. Bandwidth and the ESPHome MQTT buffer size need watching; filtering obvious
  noise on the ESP may be needed.
- RX/TX switching and transmit timing remain the firmware's responsibility.
- Raw replay only works for fixed-code devices. Rolling-code devices, which some blinds and covers
  use, need a protocol implementation in the orchestrator that generates fresh codes.
- Nothing is decoded while the orchestrator is down.
