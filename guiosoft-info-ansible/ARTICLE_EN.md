# Homelab: Setting Up Your Own Server at Home

## Introduction

Having your own server at home is one of those experiences every tech professional should have. Not just for the technical knowledge you gain, but for the freedom that comes with it.

When I started studying infrastructure, I noticed a gap between what I knew in theory and what I could actually do in practice. Cloud services like AWS, DigitalOcean, or Vercel are amazing and solve real problems, but they hide most of the complexity under the rug. You pay not to worry about it — and there's nothing wrong with that. But when you want to *understand*, to *experiment*, to *break and fix*, having full control over hardware and operating system is irreplaceable.

### Why build a homelab?

**Hands-on learning.** Nothing beats the experience of setting up a server from scratch. Networking, firewalls, DNS, virtualization, storage, monitoring — every service you deploy teaches you something no theoretical tutorial can convey.

**Real savings.** Managed services are convenient, but costs scale fast. A basic VPS with 2 GB RAM runs between US$ 10 and US$ 20 per month. A dedicated server with 16 GB RAM and NVMe storage easily exceeds US$ 60 monthly. In a year, you've spent enough to buy a decent machine. With a homelab, the cost is basically electricity and internet — a fraction of that.

**Privacy and control.** Your data, your rules. No third party accesses your files, logs, or applications. You decide who gets in and what gets exposed.

**Availability.** Internet dependency for external access is a real limitation, but for local services (files, home automation, development), an on-premise server is as fast or faster than any cloud.

This article is the first in a series documenting the full build of my homelab. Here we'll cover the foundation: operating system installation, user setup, SSH configuration, and the first run of the Ansible playbook that automates everything else.

---

## Part 1: The Foundation

### The Hardware

The server is a regular desktop I had lying around:

- **CPU:** Intel Core i5 (12th gen)
- **RAM:** 16 GB DDR4
- **Storage:** 512 GB NVMe SSD + 2 TB HDD
- **Network:** Gigabit Ethernet

Nothing special, but more than enough to run dozens of containers, web services, databases, and automation. The rule is simple: if you have an old computer or a mini PC (like a Dell OptiPlex or Intel NUC), you have a server.

### Installing Debian

I chose Debian 13 "Trixie" as the operating system. Why Debian?

- **Legendary stability.** Debian doesn't break. You can run `apt upgrade` after months without updating and it keeps working.
- **Lightweight.** A server doesn't need a GUI, browser, or office suite. Debian Server idles under 1 GB of RAM.
- **Huge community.** Whatever problem you run into, someone else has had it before. Documentation is vast.
- **APT.** Debian's package manager is mature, secure, and simple.

The installation process is straightforward:

1. Downloaded the Debian 13 netinstall ISO from the official site
2. Created a bootable USB with `dd`
3. Booted the server from the USB drive
4. During installation, selected only "SSH server" and "Standard system utilities" — no desktop environment
5. Set the hostname to `guiosoft-info`
6. Partitioned the disk as a single ext4 partition + swap (later replaced with a swapfile managed by Ansible)

The full install took about 10 minutes.

### First User and SSH Access

During Debian installation, I created the user `guionardo` with a temporary password. The first step after the system was running was to set up SSH key access:

```bash
# On my laptop (control machine):
ssh-copy-id guionardo@192.168.88.9
```

This copies my public key to `~/.ssh/authorized_keys` on the server. From that point on, passwordless access.

Then I disabled password login over SSH for better security:

```bash
# On the server:
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

Also disabled root login:

```bash
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

At this point, the server is accessible and minimally secure.

### Final Verification

```bash
ssh guionardo@192.168.88.9

# Should connect without a password prompt
# Then test sudo:
sudo whoami
# Should return: root
```

### The Ansible Playbook

With the basic server up and running, the rest of the configuration is 100% automated with Ansible. The main playbook (`playbooks/site.yml`) orchestrates 8 roles:

| Role | What it does |
|------|-------------|
| **common** | System updates, base packages (helix, starship, lm-sensors, ufw, mc, git, etc.), hostname, timezone, NTP, directories |
| **swapfile** | Creates a 4 GB swapfile with low swappiness |
| **kernel** | Adds the Zabbly repository and installs the latest mainline kernel |
| **docker** | Installs Docker CE, Docker Compose v2, Buildx, and adds users to the docker group |
| **cockpit** | Installs Cockpit + plugins (sensors, dockermanager, navigator, benchmark, compose, cloudflared, file-sharing) |
| **cloudflare-tunnel** | Installs cloudflared and configures the Cloudflare Tunnel |
| **smartmontools** | Enables SMART monitoring on all drives and schedules tests |
| **mail-server** | Configures local Postfix for system email delivery |

### Running Ansible

Before the first run, I made sure the control laptop had Ansible installed:

```bash
pip install ansible
```

Then I configured the inventory in `inventory/production/hosts.yml`:

```yaml
all:
  children:
    homelab:
      hosts:
        guiosoft-info:
          ansible_host: 192.168.88.9
          ansible_user: guionardo
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
```

The Cloudflare Tunnel token was encrypted with Ansible Vault so it wouldn't be exposed in the repository:

```bash
ansible-vault encrypt_string "your-token-here" --name cloudflare_tunnel_token
```

The full setup runs with a single command:

```bash
cd ansible-homelab
./scripts/setup-homelab.sh full
```

The script first tests connectivity, checks prerequisites, and then runs all roles in sequence. During execution, it prompts for the sudo password (never stored anywhere) and uses the `.vault_pass` file to decrypt the Cloudflare token.

The end result is a production-ready server with:

- Modern kernel and up-to-date drivers
- Docker + Compose for container workloads
- Cockpit for web-based management
- Cloudflare Tunnel to expose services securely without opening router ports
- SMART monitoring to prevent disk failures
- Local mail server for system alerts
- Development environment with Helix editor and Starship prompt

And everything is versioned in Git, documented, and reproducible. If the disk dies tomorrow, the server is back up in 30 minutes.

---

In part two, I'll cover the services running on top of this foundation: Docker Compose automation, Grafana monitoring, automated backups, and more.
