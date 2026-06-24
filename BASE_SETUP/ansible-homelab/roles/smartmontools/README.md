# smartmontools

Enables SMART monitoring on all storage drives and schedules periodic tests.

## Requirements

- Debian-based system
- SATA (`/dev/sd*`) or NVMe (`/dev/nvme*`) drives with SMART support
- `smartmontools` package (installed by the role)

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `smartmontools_email` | `root@localhost` | Email address for SMART alerts |
| `smartmontools_schedule` | `S/../.././02` | smartd test schedule (short test daily at 2 AM) |

### Overrides in group_vars

```yaml
smartmontools_email: guionardo@gmail.com
smartmontools_schedule: S/../.././02
```

## Features

- Finds all available SCSI/SATA (`sd[a-z]`) and NVMe drives with the `find` module
- Enables SMART, offline auto, and save auto on each drive
- Configures `smartd` via template (`/etc/smartd.conf`) with:
  - Health monitoring (`-H`)
  - Error log tracking (`-l error`)
  - Selftest result tracking (`-l selftest`)
  - Pending sector check (`-f`)
  - Scheduled short tests (configurable via `smartmontools_schedule`)
  - Email alerts (configurable via `smartmontools_email`)
  - Daily reminder of past failures (`-M daily`)
- Enables and starts `smartd` service
- Enables `fstrim.timer` for SSD TRIM support

## Tags

- `smartmontools`
- `smart`
- `disk`

## Dependencies

None.

## Example

```yaml
- role: smartmontools
  vars:
    smartmontools_email: admin@example.com
    smartmontools_schedule: S/../.././03
```
