# 0002. Keep the ESPHome component and the HA add-on in one repository

- Status: Accepted
- Date: 2026-10-25

## Context

The system has two deliverables:

- an ESPHome external component (`components/CC1101_MQTT/`) that drives a CC1101 radio, and
- a Home Assistant add-on (`rf_orchestrator/`) that decodes and encodes RF protocols and exposes
  devices to Home Assistant.

Neither is useful without the other, and they share an implicit contract: MQTT topic names and the
pulse list format (see [ADR-0004](0004-mqtt-pulse-wire-format.md)). Both installers can consume a
single git repository:

- The Home Assistant Supervisor clones the repository, reads the repository name and maintainer
  from `repository.yaml` at the root, and finds add-ons by recursively searching for
  `**/config.{yaml,yml,json}`. Paths containing a folder that starts with `.` or is named `rootfs`
  are skipped. The folder holding a match is the add-on and its Docker build context.
- ESPHome's `external_components` git source loads components from `components/<name>/` by default.

## Decision

Keep both parts in one repository with this layout:

```
repository.yaml          HA add-on repository manifest (must stay at the root)
components/CC1101_MQTT/  ESPHome external component (path expected by ESPHome)
rf_orchestrator/         HA add-on (config.yaml, Dockerfile, src/)
docs/adr/                Architecture decision records
tools/                   Developer scripts not shipped with either deliverable
```

Only the add-on folder may contain a file named `config.yaml`, `config.yml` or `config.json`.
Example ESPHome configs and other YAML files must use different names (e.g. `gateway.yaml`).

## Consequences

- A change to the wire contract lands on both sides in one commit; a tag identifies a compatible pair.
- Both deliverables share git tags. Add-on updates are still driven by `version` in
  `rf_orchestrator/config.yaml`; ESPHome users pin a branch or tag.
- A stray `config.yaml` anywhere in the repository would be picked up as a broken add-on.
- Revisit if the ESPHome component becomes a general-purpose component used by other projects, or a
  second gateway type with its own release cadence is added.
