# Project Memory

## Server
- **Hostname:** guiosoft-info
- **IP:** 192.168.88.9
- **OS:** Debian 13 (Trixie)
- **User:** guionardo (sudo)
- **SSH key:** `~/.ssh/id_rsa`
- **Sudo password:** not stored — use `--ask-become-pass`

## Project Structure
```
/home/guionardo/dev/guiosoft-infra/
├── AGENTS.md             # AI agent conventions
├── MEMORY.md             # This file
├── README.md             # Project overview
├── BASE_SETUP/           # Ansible homelab automation + articles
│   ├── ansible-homelab/  # Playbooks, roles, inventory, scripts
│   ├── ARTICLE.md        # Homelab article (PT-BR)
│   └── ARTICLE_EN.md     # Homelab article (EN)
├── SCRIPTS/              # Automation scripts
│   ├── furlanserver-backup/  # Python/poetry backup app
│   └── ssh_backup/           # Bash SSH backup
├── SERVICES/             # (placeholder)
└── docs/                 # Documentation
```

## Ansible
- Single inventory: `inventory/production/hosts.yml`
- Single group_vars: `inventory/production/group_vars/all.yml`
- Cloudflare token encrypted with `ansible-vault` (password in `.vault_pass`, gitignored)
- Run: `./scripts/setup-homelab.sh full` (prompts for sudo password, uses `.vault_pass`)

## Roles (8)
1. **common** — apt update/upgrade, base packages, hostname, timezone, NTP, directories, helix, starship, unattended-upgrades
2. **swapfile** — 4 GB swapfile, swappiness=10
3. **kernel** — Zabbly mainline kernel repo
4. **docker** — Docker CE, Compose v2, Buildx, python3-docker
5. **cockpit** — port 9090, plugins: machines/storaged/dockermanager/navigator/benchmark/compose/file-sharing
6. **cloudflare-tunnel** — cloudflared from APT, `service install <vault token>`
7. **smartmontools** — SMART monitoring + fstrim timer
8. **mail-server** — Postfix local-only, root alias, test email, ~/.mail_prompt notification script sourced in .bashrc

## Key Decisions
- Debian 13 so no Ubuntu PPAs, no `apt-key`, PEP 668 enforced
- Stack: Ansible + APT + GitHub releases (no pip for system tools)
- DEB822 `.sources` format for all repos
- `ansible-vault` for secrets, `--ask-become-pass` for sudo
- 45Drives repo uses `bookworm` suite (only supported version)
- dockermanager repo is unsigned (`trusted=yes`)
- `AGENTS.md` documents all conventions for AI agents working on the repo
- Python: `uv` for new projects, Ruff lint/format, pytest (legacy Poetry in `SCRIPTS/furlanserver-backup/`)
- Go: minimum 1.26+, `go mod init`, `cmd/` entry point
- Shell scripts: `set -euo pipefail`, `command -v`, logging colors, `read -rsp` for secrets
- Swapfile created with `fallocate` instead of `dd`
- Cloudflare token change detected via SHA1 hash comparison
- Chrony NTP servers configurable via `ntp_servers` variable (previously unused)
- Keyrings dirs created once in common role (not duplicated per role)
- Mail notification via `mailx -H` grep, appended to PROMPT_COMMAND (no override to existing prompt)
- Kernel reboot notification added post-install
- `meta/main.yml` added to all 8 roles with platform metadata
- Setup script exports `ANSIBLE_CONFIG` for correct role resolution regardless of CWD
- Docker uses `{{ ansible_architecture }}` instead of hardcoded `amd64`
- SMART drive detection uses `find` module instead of shell loop with `|| true`

## Articles
- `BASE_SETUP/ARTICLE.md` (PT-BR) — Part 1 covers Debian install, SSH, first Ansible run
- `BASE_SETUP/ARTICLE_EN.md` — English translation
