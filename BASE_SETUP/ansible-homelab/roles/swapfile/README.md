# swapfile

Creates and configures a swapfile with optimized swappiness.

## Requirements

- Debian-based system
- Sufficient disk space for the swapfile

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `swapfile_path` | `/swapfile` | Path to the swapfile |
| `swapfile_size_mb` | `2048` | Size in MB |
| `swap_swappiness` | `10` | vm.swappiness kernel parameter |

## Features

- Creates swapfile with `fallocate` (instant, no dd overhead)
- Sets secure permissions (0600)
- Formats with `mkswap` and enables with `swapon`
- Adds permanent entry to `/etc/fstab`
- Sets `vm.swappiness` via sysctl

## Tags

- `swapfile`
- `swap`

## Dependencies

- `common` (for keyrings directory)

## Example

```yaml
- role: swapfile
  vars:
    swapfile_size_mb: 8192
    swap_swappiness: 5
```
