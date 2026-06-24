# AGENTS.md — GuioSoft Infra

This file documents conventions and rules for AI agents working on this repository.

## Ansible (BASE_SETUP)

- All Ansible playbooks/roles are under `BASE_SETUP/ansible-homelab/`
- **Run command:** `./scripts/setup-homelab.sh full` (from `BASE_SETUP/ansible-homelab/`)
- The script exports `ANSIBLE_CONFIG` automatically
- **8 roles:** common, swapfile, kernel, docker, cockpit, cloudflare-tunnel, smartmontools, mail-server
- **Single inventory:** `inventory/production/hosts.yml`
- **Single group_vars:** `inventory/production/group_vars/all.yml` (one source of truth for all variables)
- **Secrets:** Ansible Vault with `.vault_pass` (gitignored). Use `./scripts/setup-homelab.sh vault` to generate
- **Inventory hosts:**
  - Production: `guiosoft-info` @ `192.168.88.9`, user `guionardo`
  - Staging: `staging-1` @ same IP
- **All roles must have** `meta/main.yml` with author, license, min_ansible_version, platforms
- **No `vars/` directories** — all variable overrides come from group_vars
- **DEB822 `.sources` format** for all APT repositories
- **Prefer modules over shell** — avoid `shell`/`command` unless necessary
- **Keyrings directories** (`/etc/apt/keyrings`, `/usr/share/keyrings`) are managed by the `common` role
- **Always use `no_log: yes`** on tasks handling secrets
- **Idempotency first** — tasks should be safe to run multiple times
- **After adding a task**, run `ansible-playbook playbooks/site.yml --syntax-check` to validate

### Tags available per role

`common`, `swapfile`, `kernel`, `docker`, `cockpit`, `cloudflare`, `smart`, `mail`

## Python

- **Package manager:** `uv` (not Poetry, not pip)
- **Python version:** 3.11+
- **Linting/formatting:** Ruff (configured in `.pre-commit-config.yaml`)
- **Tests:** pytest
- **Setup a new project:**
  ```bash
  uv init
  uv add <dependency>
  uv add --dev pytest ruff
  ```
- **Run tests:** `uv run pytest`
- **Run linter:** `uv run ruff check`
- **Run formatter:** `uv run ruff format`
- **Pre-commit:** hooks configured at root and per-project level
- **Existing projects** (like `SCRIPTS/furlanserver-backup/`) still use Poetry — do not migrate unless instructed

## Go

- **Minimum Go version:** 1.26+
- **Use `go mod init`** for new projects
- **Entry point:** `cmd/` directory convention
- **Run:** `go run .` or `go build -o <name> ./cmd/`

## Shell Scripts

- **Strict mode:** `set -euo pipefail`
- **Colored logging:** use `RED/GREEN/YELLOW/NC` with `log_info`/`log_warn`/`log_error` functions
- **Use `command -v`** instead of `which` for checking command availability
- **Use `read -rsp`** for sensitive input (silent mode)
- **Avoid `cd`** before commands; use absolute paths or `workdir` parameter

## General Conventions

- **pre-commit hooks:** Always run `.pre-commit-config.yaml` hooks before committing. Run `pre-commit run --all-files` to check
- **Documentation:** Articles exist in both PT-BR (`ARTICLE.md`) and English (`ARTICLE_EN.md`)
- **New features** should be documented in `MEMORY.md` (Key Decisions section)
- **No Makefile** — use shell scripts or ansible directly
- **Git commits:** follow existing commit message style in git history
