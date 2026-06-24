# guiosoft.info server setup

## Setup Checklist

- [x] Setup swapfile
- [x] Zabbly mainline kernel
- [x] Docker + Compose v2
- [x] Cockpit + all plugins (sensors, dockermanager, navigator, benchmark, compose, cloudflared, file-sharing)
- [x] Cloudflare Tunnel
- [x] SMART monitoring + fstrim
- [x] Local mail server (Postfix)
- [x] lm-sensors

**Ansible playbook:** `ansible-homelab/playbooks/site.yml`

**Usage:** `./ansible-homelab/scripts/setup-homelab.sh full`
*(prompts for sudo password)*
