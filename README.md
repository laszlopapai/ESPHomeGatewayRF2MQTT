# ESPHomeGatewayRF2MQTT

Control and receive 433 MHz devices from Home Assistant using a CC1101 radio on an ESP32-S3 running
ESPHome. The gateway also works as a sniffing and replay tool for reverse engineering unknown devices.

Status: proof of concept.

```
433 MHz devices ⇄ CC1101 ⇄ ESP (ESPHome component) ⇄ MQTT ⇄ RF Orchestrator (HA add-on) ⇄ Home Assistant
```

The ESP forwards raw pulse timings; the orchestrator decodes and encodes protocols and exposes the
devices to Home Assistant via MQTT discovery. See [docs/adr](docs/adr/README.md) for the reasoning.

## Repository layout

```
repository.yaml                 Home Assistant add-on repository manifest
components/CC1101_MQTT/         ESPHome external component (CC1101 driver, pulse RX/TX over MQTT)
rf_orchestrator/                Home Assistant add-on
  config.yaml                   Add-on manifest and options schema
  Dockerfile, requirements.txt  Container build
  src/main.py                   Entry point
  src/processors/               Turn decoded data into MQTT/HA messages
  src/protocols/                RF protocol encoders/decoders (RCSwitch, Alecto WS1700)
docs/adr/                       Architecture decision records
tools/legacy/                   Superseded single-file prototypes, not shipped
```

## ESPHome

```yaml
external_components:
  - source: github://laszlopapai/ESPHomeGatewayRF2MQTT@development
    components: [CC1101_MQTT]
```

## Home Assistant add-on

Add `https://github.com/laszlopapai/ESPHomeGatewayRF2MQTT` as an add-on repository, install
**RF MQTT Orchestrator** and set the MQTT connection and device lists in its options.

For local runs outside Home Assistant, put the options in `rf_orchestrator/src/data/options.json`
(git-ignored) and run `python main.py` from `rf_orchestrator/src`.
