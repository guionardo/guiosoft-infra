# cockpit

Installs Cockpit web console and a comprehensive set of plugins.

## Requirements

- Debian-based system (Bookworm / Trixie)
- amd64 architecture (45Drives plugins are amd64 only)
- Internet access for GitHub releases and external APT repos

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `cockpit_port` | `9090` | Cockpit web console port |
| `cockpit_plugins` | `[]` | Base cockpit plugins (apt packages) |

### Overrides in group_vars

```yaml
cockpit_port: 9090
cockpit_plugins:
  - cockpit-machines
  - cockpit-storaged
```

## Features

### Base Cockpit
- `cockpit` + plugins from `cockpit_plugins` (machines, storaged)
- Configures port in `/etc/cockpit/cockpit.conf`
- Opens port in UFW
- Enables `cockpit.socket`

### Plugins installed from external sources

| Plugin | Source | Installation method |
|---|---|---|
| **cockpit-dockermanager** | ChrisJBawden APT repo | APT (`trusted=yes`) |
| **cockpit-file-sharing** | 45Drives APT repo | APT |
| **cockpit-navigator** | 45Drives APT repo | APT |
| **cockpit-benchmark** | 45Drives APT repo | APT |
| **cockpit-compose** | GitHub releases (RXTX4816) | .deb package |

## Tags

- `cockpit`

## Dependencies

- `common` (for `/usr/share/keyrings` directory)

## Notes

- The 45Drives repository is hardcoded to `bookworm` suite (only supported version).
- The dockermanager repo is unsigned (`trusted=yes`) — this is a limitation of the upstream project.

## Example

```yaml
- role: cockpit
  vars:
    cockpit_port: 4443
```
