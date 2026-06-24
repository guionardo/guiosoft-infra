# mail-server

Configures a local-only Postfix mail server for system email delivery and notifications.

## Requirements

- Debian-based system
- `mail_server_admin_user` must exist as a system user

## Role Variables

| Variable | Default | Description |
|---|---|---|
| `mail_server_admin_user` | `root` | System user to receive root's mail |

### Overrides in group_vars

```yaml
mail_server_admin_user: guionardo
```

## Features

- Installs `postfix`, `mailutils`, `bsd-mailx`, and `mutt`
- Configures Postfix for local-only delivery (`inet_interfaces = loopback-only`)
- Sets `mydestination` to localhost only
- Forwards root's mail to `{{ mail_server_admin_user }}` via `/etc/aliases`
- Creates mail spool for the admin user
- Sends a test email on first run (one-time via `creates` guard)
- Creates `~/.mail_prompt` with a mail notification script and sources it in `.bashrc`
  - Checks for unread mail via `mailx -H` every `$MAILCHECK` seconds (default 60)
  - Appends to existing `PROMPT_COMMAND` — does not override custom prompts

## Tags

- `mail`
- `postfix`

## Dependencies

None.

## Example

```yaml
- role: mail-server
  vars:
    mail_server_admin_user: alice
```
