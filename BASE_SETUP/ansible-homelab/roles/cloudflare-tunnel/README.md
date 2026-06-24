# cloudflare-tunnel

Installs and configures a Cloudflare Tunnel using `cloudflared`.

## Requirements

- Debian-based system
- A Cloudflare Zero Trust account with a configured tunnel
- A Cloudflare connector token (stored in Ansible Vault)

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `cloudflare_tunnel_token` | `""` | Cloudflare tunnel connector token (vault-encrypted) |

## Features

- Adds Cloudflare APT repository (DEB822 format)
- Installs `cloudflared` package
- Registers the tunnel as a systemd service via `cloudflared service install`
- Token change detection: if the token hash changes, the old service is removed and reinstalled
- All token handling uses `no_log: yes` to prevent secrets in output

## Tags

- `cloudflare`
- `tunnel`

## Dependencies

- `common` (for `/usr/share/keyrings` directory)

## Notes

- The token is expected to be a **connector token** from Cloudflare Zero Trust, not an API token.
- Token is encrypted with `ansible-vault` in `group_vars/all.yml`.
- Use `./scripts/setup-homelab.sh vault` to generate the encrypted token interactively.

## Example

```yaml
- role: cloudflare-tunnel
  vars:
    cloudflare_tunnel_token: "{{ vault_encrypted_token }}"
```
