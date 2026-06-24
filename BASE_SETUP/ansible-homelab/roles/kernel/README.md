# kernel

Installs the latest Zabbly mainline kernel on Debian.

## Requirements

- Debian-based system (uses `ansible_distribution_release` for repo suite)
- x86_64 / amd64 architecture (Zabbly supports amd64 and arm64)

## Role Variables

No configurable variables. The Zabbly repository URL and GPG fingerprint are hardcoded.

## Features

- Adds Zabbly APT repository (DEB822 `.sources` format)
- Downloads and verifies Zabbly GPG key (fingerprint: `82CC 8797 C838 DCFD`)
- Installs `linux-zabbly` meta-package (tracks latest mainline)
- Runs `update-grub` after kernel install
- Displays reboot notification when a new kernel is installed

## Tags

- `kernel`

## Dependencies

- `common` (for `/etc/apt/keyrings` directory)

## Notes

- A reboot is required after a new kernel is installed. The role does **not** reboot automatically — it displays a warning message.
- Zabbly kernels are mainline builds, not Debian stock kernels. See [pkgs.zabbly.com](https://pkgs.zabbly.com) for details.

## Example

```yaml
- role: kernel
```
