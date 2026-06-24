# Script para backup automatizado e periódico das estações

O script de backup pode ser adicionado a um cronjob.

Requisitos para execução:

* Script ssh_backup.sh
* Arquivo de chave privada para acesso ao host de backup via SSH
* Arquivo de configuração

```json
{
    "backup_host": "furlan-server",
    "private_key_file": "id_ed25519",
    "destiny_dynamic_folder_format": "%Y-%m-%d",
    "destiny_base_path": "/home/guionardo/sdb1",
    "local_host": "guionote-debian",
    "paths": [
        "/home/guionardo/dev"
    ]
}
```
