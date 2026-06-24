# common

Base system configuration for Debian servers. Prepares the foundation for all other roles.

## Requirements

- Debian 12+ (Bookworm / Trixie)
- `ansible.posix` and `community.general` collections

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `timezone` | `UTC` | System timezone |
| `ntp_servers` | `[0.pool.ntp.org, 1.pool.ntp.org]` | NTP pool servers for chrony |
| `base_packages` | `[curl, wget, vim, git, ca-certificates, bash-completion]` | APT packages to install |

### Overrides in group_vars

See `inventory/production/group_vars/all.yml` for the expanded `base_packages` list (includes htop, btop, jq, gnupg2, lm-sensors, ufw, mc, duf, etc.).

## Features

- APT cache update and full dist-upgrade
- Unattended-upgrades installation and configuration (auto security updates)
- Package installation (`{{ base_packages }}`)
- Hostname and `/etc/hosts` configuration
- Timezone and NTP (chrony with configurable servers)
- APT keyrings directories (`/etc/apt/keyrings`, `/usr/share/keyrings`)
- Homelab directory structure (`/opt/homelab/`)
- Bash completion
- Helix editor (from GitHub releases)
- Starship prompt (from official install script)

## Tags

- `common` — main role
- `helix` — skip Helix editor installation
- `starship` — skip Starship prompt installation

## Dependencies

None.

## Example

```yaml
- name: Configure homelab server
  hosts: homelab
  become: yes
  roles:
    - role: common
```
