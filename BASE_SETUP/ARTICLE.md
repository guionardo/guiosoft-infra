# Homelab: Montando Seu Próprio Servidor em Casa

## Introdução

Ter o próprio servidor em casa é uma daquelas experiências que todo profissional de tecnologia deveria viver. Não apenas pelo conhecimento técnico adquirido, mas pela liberdade que vem com ele.

Quando comecei a estudar infraestrutura, percebi que havia uma lacuna entre o que eu sabia teoricamente e o que conseguia fazer na prática. Serviços cloud como AWS, DigitalOcean ou Vercel são incríveis e resolvem problemas reais, mas escondem grande parte da complexidade embaixo do tapete. Você paga para não se preocupar — e não há problema nenhum nisso. Mas quando você quer *entender*, quer *experimentar*, quer *quebrar e consertar*, ter o controle total do hardware e do sistema operacional é insubstituível.

### Por que montar um homelab?

**Aprendizado prático.** Nada substitui a experiência de configurar um servidor do zero. Rede, firewall, DNS, virtualização, armazenamento, monitoramento — cada serviço que você sobe ensina algo que nenhum tutorial teórico consegue transmitir.

**Economia real.** Serviços gerenciados são convenientes, mas o custo escala rápido. Um VPS básico com 2 GB de RAM custa algo entre US$ 10 e US$ 20 por mês. Um servidor dedicado com 16 GB de RAM e armazenamento NVMe passa fácil de US$ 60 mensais. Em um ano, você já gastou o suficiente para comprar uma máquina boa. Com um homelab, o custo é basicamente a energia elétrica e a internet — uma fração do valor.

**Privacidade e controle.** Seus dados, suas regras. Nenhum terceiro acessa seus arquivos, seus logs, suas aplicações. Você decide quem pode entrar e o que pode ser exposto.

**Disponibilidade.** Dependência de internet para acesso externo é uma limitação real, mas para serviços locais (arquivos, automação residencial, desenvolvimento), um servidor em casa é tão ou mais rápido que qualquer cloud.

Este artigo é o primeiro de uma série onde vou documentar a montagem completa do meu homelab. Aqui vamos cobrir a base: instalação do sistema operacional, criação do usuário, configuração de acesso SSH e a primeira execução do playbook Ansible que automatiza todo o resto.

---

## Parte 1: A Base

### O Hardware

O servidor é um desktop comum que sobrou aqui em casa:

- **CPU:** Intel Core i5 (12th gen)
- **RAM:** 16 GB DDR4
- **Armazenamento:** SSD NVMe 512 GB + HDD 2 TB
- **Rede:** Gigabit Ethernet

Nada especial, mas mais do que suficiente para rodar dezenas de containers, serviços web, bancos de dados e automações. A regra é simples: se você tem um computador velho ou um mini PC (tipo um Dell OptiPlex ou um Intel NUC), você tem um servidor.

### Instalação do Debian

A escolha do sistema operacional foi o Debian 13 "Trixie". Por que Debian?

- **Estabilidade lendária.** O Debian não quebra. Você faz `apt upgrade` mesmo depois de meses sem atualizar e ele continua funcionando.
- **Leve.** Um servidor não precisa de interface gráfica, navegador, suíte de escritório. O Debian Server ocupa menos de 1 GB de RAM ociosa.
- **Comunidade enorme.** Qualquer problema que você tiver, alguém já teve antes. A documentação é vasta.
- **APT.** O gerenciador de pacotes do Debian é maduro, seguro e simples.

O processo de instalação é direto:

1. Baixei a ISO do Debian 13 (netinstall) do site oficial
2. Criei um pendrive bootável com `dd`
3. Iniciei o servidor pelo pendrive
4. Durante a instalação, selecionei apenas "Servidor SSH" e "Utilitários padrão do sistema" — sem interface gráfica
5. Configurei o nome do host como `guiosoft-info`
6. Participei o disco com uma única partição ext4 + swap (depois substituímos a swap por um arquivo gerenciado pelo Ansible)

A instalação completa levou cerca de 10 minutos.

### Primeiro Usuário e Acesso SSH

Durante a instalação do Debian, criei o usuário `guionardo` com uma senha temporária. O primeiro passo após o sistema estar rodando foi configurar o acesso por chave SSH:

```bash
# No meu notebook (máquina de controle):
ssh-copy-id guionardo@192.168.88.9
```

Isso copia minha chave pública para `~/.ssh/authorized_keys` no servidor. A partir desse momento, acesso sem senha.

Depois desabilitei o login por senha no SSH para aumentar a segurança:

```bash
# No servidor:
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

E também desabilitei o login como root:

```bash
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

Com isso, o servidor já está acessível e minimamente seguro.

### Verificação Final

```bash
ssh guionardo@192.168.88.9

# Deve entrar sem pedir senha
# Depois testar o sudo:
sudo whoami
# Deve retornar: root
```

### O Playbook Ansible

Com o servidor básico funcionando, o resto da configuração é 100% automatizada com Ansible. O playbook principal (`playbooks/site.yml`) orquestra 8 roles:

| Role | O que faz |
|------|-----------|
| **common** | Atualiza o sistema, instala pacotes base (helix, starship, lm-sensors, ufw, mc, git, etc.), configura hostname, timezone, NTP e diretórios |
| **swapfile** | Cria um arquivo de swap de 4 GB com swappiness baixo |
| **kernel** | Adiciona o repositório Zabbly e instala o kernel mainline mais recente |
| **docker** | Instala Docker CE, Docker Compose v2, Buildx e adiciona usuários ao grupo docker |
| **cockpit** | Instala o Cockpit + plugins (sensors, dockermanager, navigator, benchmark, compose, cloudflared, file-sharing) |
| **cloudflare-tunnel** | Instala o cloudflared e configura o túnel Cloudflare |
| **smartmontools** | Ativa monitoramento SMART em todos os discos e agenda testes |
| **mail-server** | Configura Postfix local para entrega de e-mails do sistema |

### Executando o Ansible

Antes da primeira execução, precisei garantir que o notebook de controle tinha o Ansible instalado:

```bash
pip install ansible
```

Depois, configurei o inventário em `inventory/production/hosts.yml`:

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

E a variável com o token do Cloudflare Tunnel foi criptografada com Ansible Vault para não ficar exposta no repositório:

```bash
ansible-vault encrypt_string "meu-token-aqui" --name cloudflare_tunnel_token
```

A execução completa é feita com um comando:

```bash
cd ansible-homelab
./scripts/setup-homelab.sh full
```

O script primeiro testa a conectividade, verifica os pré-requisitos e então executa todas as roles em sequência. Durante a execução, ele pede a senha do sudo (que não está armazenada em lugar nenhum) e usa o arquivo `.vault_pass` para descriptografar o token do Cloudflare.

O resultado final é um servidor pronto para uso, com:

- Kernel moderno e drivers atualizados
- Docker + Compose para rodar containers
- Cockpit para gerenciamento via web
- Cloudflare Tunnel para expor serviços com segurança, sem abrir portas no roteador
- Monitoramento SMART para prevenir falhas de disco
- Servidor de e-mail local para alertas do sistema
- Ambiente de desenvolvimento com Helix editor e Starship prompt

E tudo versionado em Git, documentado e reproduzível. Se o disco queimar amanhã, em 30 minutos o servidor está de pé de novo.

---

Na segunda parte, vou mostrar como configurar os serviços que rodam em cima dessa base: automação com Docker Compose, monitoramento com Grafana, backup automatizado e muito mais.
