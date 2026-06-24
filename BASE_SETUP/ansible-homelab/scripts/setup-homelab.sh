#!/bin/bash
# =====================================================
# Homelab Server Setup Script
# =====================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
PLAYBOOK_DIR="$ANSIBLE_DIR/playbooks"
export ANSIBLE_CONFIG="$ANSIBLE_DIR/ansible.cfg"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prereqs() {
    log_info "Checking prerequisites..."

    if ! command -v ansible &>/dev/null; then
        log_error "Ansible is not installed. Install with: pip install ansible"
        exit 1
    fi

    if ! command -v ansible-playbook &>/dev/null; then
        log_error "ansible-playbook not found"
        exit 1
    fi

    ANSIBLE_VERSION=$(ansible --version | head -1 | grep -oP '\d+\.\d+\.\d+' | head -1)
    log_info "Ansible version: $ANSIBLE_VERSION"

    if ! ansible-galaxy collection list ansible.posix &>/dev/null; then
        log_info "Installing ansible.posix collection..."
        ansible-galaxy collection install ansible.posix
    fi

    if ! ansible-galaxy collection list community.general &>/dev/null; then
        log_info "Installing community.general collection..."
        ansible-galaxy collection install community.general
    fi
}

test_connectivity() {
    log_info "Testing connectivity to all hosts..."
    ansible homelab -i "$ANSIBLE_DIR/inventory/production/hosts.yml" \
        -m ping \
        --one-line
    log_info "Connectivity test passed!"
}

run_full() {
    log_info "==========================================="
    log_info "Full Homelab Server Setup"
    log_info "==========================================="

    ansible-playbook "$PLAYBOOK_DIR/site.yml" \
        -i "$ANSIBLE_DIR/inventory/production/hosts.yml" \
        --become \
        --ask-become-pass \
        --vault-password-file "$ANSIBLE_DIR/.vault_pass" \
        -v

    log_info "==========================================="
    log_info "Setup complete!"
    log_info "==========================================="
}

run_tag() {
    local tag="$1"
    log_info "Running tag: $tag"
    ansible-playbook "$PLAYBOOK_DIR/site.yml" \
        -i "$ANSIBLE_DIR/inventory/production/hosts.yml" \
        --become \
        --ask-become-pass \
        --vault-password-file "$ANSIBLE_DIR/.vault_pass" \
        --tags "$tag" \
        -v
}

generate_vault() {
    local vault_file="$ANSIBLE_DIR/.vault_pass"
    local group_vars="$ANSIBLE_DIR/inventory/production/group_vars/all.yml"

    if [[ -f "$vault_file" ]]; then
        read -rp "Vault password file already exists. Overwrite? [y/N] " confirm
        [[ "$confirm" =~ ^[yY] ]] || { log_info "Aborted."; exit 0; }
    fi

    log_info "Creating vault password file..."
    read -rsp "Enter vault password: " vault_pass
    echo
    read -rsp "Confirm vault password: " vault_pass_confirm
    echo
    if [[ "$vault_pass" != "$vault_pass_confirm" ]]; then
        log_error "Passwords do not match."
        exit 1
    fi
    echo -n "$vault_pass" > "$vault_file"
    chmod 600 "$vault_file"
    log_info "Created $vault_file"

    log_info "Encrypting Cloudflare tunnel token..."
    read -rsp "Enter Cloudflare tunnel token: " cf_token
    echo

    local encrypted
    encrypted=$(ansible-vault encrypt_string "$cf_token" --name cloudflare_tunnel_token --vault-password-file "$vault_file" 2>/dev/null)

    if [[ -z "$encrypted" ]]; then
        log_error "Failed to encrypt token."
        exit 1
    fi

    log_info "Replace the cloudflare_tunnel_token in $group_vars with:"
    echo
    echo "$encrypted"
    echo
    log_warn "Make sure the vault password above matches the one in .vault_pass"
}

print_usage() {
    cat <<EOF
Usage: $0 [OPTION]

Options:
  full            Full server setup (common + swapfile + kernel + docker + cockpit)
  common          Base system configuration
  swapfile        Setup swapfile
  kernel          Install kernel 7.0
  docker          Install Docker CE + Compose
  cockpit         Install Cockpit web console
  cloudflare      Install and configure Cloudflare Tunnel
  smart           Install and configure SMART drive monitoring
  mail            Install local mail server (Postfix)
  test            Test connectivity to all hosts
  check           Check prerequisites only
  vault           Generate .vault_pass file and encrypt Cloudflare token

Examples:
  $0 check            # Check prerequisites
  $0 test             # Test connectivity
  $0 swapfile         # Only setup swapfile
  $0 vault            # Generate vault password file and encrypt token
  $0 full             # Complete setup
EOF
}

main() {
    if [[ $# -eq 0 ]]; then
        print_usage
        exit 0
    fi

    if [[ "${1:-}" != "vault" ]]; then
        check_prereqs
    fi

    case "${1:-}" in
        full)
            run_full
            ;;
        common|swapfile|kernel|docker|cockpit|cloudflare|smart|mail)
            run_tag "$1"
            ;;
        test)
            test_connectivity
            ;;
        check)
            log_info "Prerequisites check complete."
            ;;
        vault)
            generate_vault
            ;;
        -h|--help|help)
            print_usage
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
