# Homelab Server

Ansible-based automation to provision a homelab server running Debian 13 (Trixie).

## Architecture

```
┌──────────────────────────────────────┐
│         guiosoft-info                │
│  192.168.88.9                        │
│  ├── Swapfile (4GB)                  │
│  ├── Zabbly mainline kernel          │
│  ├── Docker CE + Compose v2          │
│  ├── Cockpit (port 9090)             │
│  │   ├── cockpit-sensors             │
│  │   ├── cockpit-dockermanager       │
│  │   ├── cockpit-navigator           │
│  │   ├── cockpit-benchmark           │
│  │   ├── cockpit-compose             │
│  │   ├── cockpit-cloudflared         │
│  │   └── cockpit-file-sharing        │
│  ├── Cloudflare Tunnel               │
│  ├── SMART monitoring (smartd)       │
│  ├── Postfix local-only MTA          │
│  └── lm-sensors                      │
└──────────────────────────────────────┘
```

## Prerequisites

- Debian 13+ server
- SSH key-based access
- User with sudo access
- Python 3 + `pip`

```bash
apt install ansible
```

## Quick Start

```bash
# 1. Edit inventory with your server
vim inventory/production/hosts.yml

# 2. Test connectivity
./scripts/setup-homelab.sh test

# 3. Full server setup (prompts for sudo password)
./scripts/setup-homelab.sh full
```

## Ansible Commands

```bash
# Full setup (prompts for sudo + vault)
ansible-playbook playbooks/site.yml \
  -i inventory/production/hosts.yml \
  --become --ask-become-pass \
  --vault-password-file .vault_pass

# Individual components
ansible-playbook playbooks/site.yml --tags common \
  -i inventory/production/hosts.yml \
  --become --ask-become-pass \
  --vault-password-file .vault_pass

# Available tags: common, swapfile, kernel, docker, cockpit,
#                 cloudflare, smartmontools, mail
```

## Project Structure

```
ansible-homelab/
├── .gitignore
├── .vault_pass                # Vault password (gitignored)
├── ansible.cfg
├── inventory/
│   ├── production/hosts.yml   # Production host definition
│   ├── production/group_vars/ # All variables (single source)
│   └── staging/hosts.yml
├── roles/
│   ├── common/                # System prep, packages, timezone, helix, starship
│   ├── swapfile/              # Swapfile creation & configuration
│   ├── kernel/                # Zabbly mainline kernel
│   ├── docker/                # Docker CE, Compose, docker group
│   ├── cockpit/               # Cockpit + all plugins
│   ├── cloudflare-tunnel/     # Cloudflare Tunnel service
│   ├── smartmontools/         # SMART monitoring + fstrim
│   └── mail-server/           # Postfix local-only MTA
├── playbooks/
│   └── site.yml               # Master playbook
├── scripts/
│   └── setup-homelab.sh       # Orchestration script
└── README.md
```

## Roles

### common
- System updates & base packages (btop, helix, starship, lm-sensors, ufw, etc.)
- Hostname & /etc/hosts configuration
- Timezone & NTP (chrony)
- Homelab directories
- Bash completion, Helix editor, Starship prompt

### swapfile
- Configurable swapfile size (default: 4GB)
- /etc/fstab persistence
- Swappiness tuning (default: 10)

### kernel
- Zabbly kernel repository (supports Debian 12+)
- Latest mainline kernel via `linux-zabbly` meta-package
- GPG key verification
- GRUB update (only when kernel changes)

### docker
- Docker CE, CLI, containerd
- Docker Compose plugin (v2), Buildx
- User docker group membership
- python3-docker SDK

### cockpit
- Cockpit web console (port 9090)
- Plugins: machines, podman, storaged, sensors
- cockpit-dockermanager
- 45Drives plugins: file-sharing, navigator, benchmark
- cockpit-compose (from GitHub releases)
- cockpit-cloudflared (from RPM extraction)
- UFW port configuration

### mail-server
- Postfix local-only MTA
- Mail utilities (mailutils, bsd-mailx, mutt)
- Root alias forwarding to admin user
- Test email sent on first setup only

### smartmontools
- SMART monitoring enabled on all drives
- Scheduled self-tests (nightly at 2am)
- Email alerts on errors
- fstrim.timer enabled for SSDs

### cloudflare-tunnel
- Cloudflare `cloudflared` from official APT repo
- Tunnel service install via `cloudflared service install <token>`
- Token stored in Ansible Vault

## Variables

Single source of truth at `inventory/production/group_vars/all.yml`:

```yaml
# Common
timezone: "America/Sao_Paulo"
base_packages:
  - curl, wget, vim, htop, btop, git, jq, lm-sensors, ufw, ...

# Swap
swapfile_size_mb: 4096
swap_swappiness: 10

# Docker
docker_users:
  - homelab

# Mail
mail_server_admin_user: "guionardo"

# SMART
smartmontools_email: "guionardo@gmail.com"
smartmontools_schedule: "S/../.././02"

# Cloudflare (encrypted with ansible-vault)
cloudflare_tunnel_token: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...

# Cockpit
cockpit_port: 9090
cockpit_plugins:
  - cockpit-machines
  - cockpit-podman
  - cockpit-storaged
```

## Vault

Sensitive values (cloudflare tunnel token) are encrypted with `ansible-vault`:

```bash
# Edit encrypted values
ansible-vault edit inventory/production/group_vars/all.yml --vault-password-file .vault_pass

# Rekey (change vault password)
ansible-vault rekey inventory/production/group_vars/all.yml --vault-password-file .vault_pass
```

## Task Tracking

See `../README.md` for the setup progress checklist.
