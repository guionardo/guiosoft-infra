#!/bin/bash
# =====================================================
# Homelab Server Setup Script
# =====================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
PLAYBOOK_DIR="$ANSIBLE_DIR/playbooks"

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

print_usage() {
    cat <<EOF
Usage: $0 [OPTION]

Options:
  full        Full server setup (common + swapfile + kernel + docker + cockpit)
  common      Base system configuration
  swapfile    Setup swapfile
  kernel      Install kernel 7.0
  docker      Install Docker CE + Compose
  cockpit     Install Cockpit web console
  cloudflare  Install and configure Cloudflare Tunnel
  smart       Install and configure SMART drive monitoring
  mail        Install local mail server (Postfix)
  test        Test connectivity to all hosts
  check       Check prerequisites only

Examples:
  $0 check            # Check prerequisites
  $0 test             # Test connectivity
  $0 swapfile         # Only setup swapfile
  $0 full             # Complete setup
EOF
}

main() {
    if [[ $# -eq 0 ]]; then
        print_usage
        exit 0
    fi

    check_prereqs

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
