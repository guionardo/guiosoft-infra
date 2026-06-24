# docker

Installs Docker CE, Compose v2, Buildx, and the Python Docker SDK.

## Requirements

- Debian-based system
- x86_64 / amd64 architecture (arm64 also supported by Docker, but the role uses `{{ ansible_architecture }}`)

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `docker_users` | `[]` | Users to add to the `docker` group |

### Overrides in group_vars

```yaml
docker_users:
  - homelab
  - guionardo
```

## Features

- Removes old/conflicting Docker packages (docker, docker-engine, docker.io, containerd, runc)
- Adds official Docker APT repository (DEB822 `.sources` format)
- Installs: `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`
- Enables and starts the `docker` systemd service
- Adds users to the `docker` group (no need for sudo for docker commands)
- Installs `python3-docker` SDK for Ansible `docker_*` modules

## Tags

- `docker`

## Dependencies

- `common` (for `/etc/apt/keyrings` directory)

## Example

```yaml
- role: docker
  vars:
    docker_users:
      - alice
      - bob
```
