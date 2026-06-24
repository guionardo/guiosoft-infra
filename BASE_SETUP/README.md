# guiosoft.info server setup

## Setup Checklist

- [x] Setup swapfile
- [x] Zabbly mainline kernel
- [x] Docker + Compose v2
- [x] Cockpit + all plugins (sensors, dockermanager, navigator, benchmark, compose, cloudflared, file-sharing)
- [x] Cloudflare Tunnel
- [x] SMART monitoring + fstrim
- [x] Local mail server (Postfix)
- [x] Unattended upgrades (auto security updates)
- [x] Mail notification prompt (`.mail_prompt` sourced in `.bashrc`)
- [x] lm-sensors

**Ansible playbook:** `ansible-homelab/playbooks/site.yml`

**Usage:** `./ansible-homelab/scripts/setup-homelab.sh full`
*(prompts for sudo password)*

## First-time setup

### Create `.vault_pass` and encrypt Cloudflare token

Run the built-in helper:

```bash
./ansible-homelab/scripts/setup-homelab.sh vault
```

It will:
1. Ask for a vault password (creates `ansible-homelab/.vault_pass`)
2. Ask for the Cloudflare tunnel token
3. Output the encrypted token — paste it into `inventory/production/group_vars/all.yml` under `cloudflare_tunnel_token:`

> `.vault_pass` is already in `.gitignore` — it will never be committed.
