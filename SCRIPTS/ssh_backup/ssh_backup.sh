#!/bin/bash

log() {
    # Black        0;30     Dark Gray     1;30
    # Red          0;31     Light Red     1;31
    # Green        0;32     Light Green   1;32
    # Brown/Orange 0;33     Yellow        1;33
    # Blue         0;34     Light Blue    1;34
    # Purple       0;35     Light Purple  1;35
    # Cyan         0;36     Light Cyan    1;36
    # Light Gray   0;37     White         1;37
    case "$1" in
    ERR)
        c0="\e[0;31m"
        shift
        ;;

    SUC)
        c0="\e[0;32m"
        shift
        ;;

    INFO)
        c0="\e[0;34m"
        shift
        ;;

    WARN)
        c0="\e[0;35m"
        shift
        ;;

    *) ;;

    esac
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${c0}" "$*" "\e[0m"
}

log INFO "Starting SSH Backup"

read_configuration() {
    if empty "$1"; then
        config_file="$HOME/.config/ssh_backup.json"
    else
        config_file="$1"
    fi

    # backup_host: str
    # private_key_file: str
    # destiny_base_path: str
    # destiny_dynamic_folder_format: str = '%Y-%m-%d'
    # local_host: str
    # max_backup_count: int = 14
    # paths: List[str]

    if [ -f "$config_file" ]; then
        log "Reading configuration file: $config_file"
        backup_host=$(jq .backup_host "$config_file" | tr -d '"')
        if empty "$backup_host"; then
            log ERR "backup_host is undefined"
            exit 1
        fi
        log SUC "Backup host: $backup_host"

        private_key_file=$(jq .private_key_file "$config_file" | tr -d '"')
        if [ ! -f "$private_key_file" ]; then
            log ERR "Private key file does not exists: $private_key_file"
            exit 1
        fi
        log SUC "Private key file: $private_key_file"

        destiny_base_path=$(jq .destiny_base_path "$config_file" | tr -d '"')
        if empty "$destiny_base_path"; then
            log ERR "destiny_base_path is undefined"
            exit 1
        fi
        log SUC "Destiny base path: $destiny_base_path"

        destiny_dynamic_folder_format=$(jq .destiny_dynamic_folder_format "$config_file" | tr -d '"')
        if empty "$destiny_dynamic_folder_format"; then
            destiny_dynamic_folder_format="%Y-%m-%d"
        fi
        log SUC "Destiny dynamic folder format: $destiny_dynamic_folder_format"

        local_host=$(jq .local_host "$config_file" | tr -d '"')
        if empty "$local_host"; then
            local_host=$(hostname)
        fi
        log SUC "Local host: $local_host"

        max_backup_count=$(jq .max_backup_count "$config_file")
        if empty "$max_backup_count"; then
            max_backup_count=14
        fi
        log SUC "Max backup count: $max_backup_count"
        _paths=$(jq .paths "$config_file")
        if empty "$_paths"; then
            log ERR "paths is undefined"
            exit 1
        fi

        readarray -t paths < <(jq -r '.paths[]' "$config_file")

        for p in "${paths[@]}"; do
            if [ ! -d "$p" ]; then
                log ERR "Path $p not exists"
                exit 1
            fi
        done

        if [ "${#paths[@]}" == "0" ]; then
            log ERR "no paths informed"
            exit 1
        fi

        # paths=$(cat $config_file | jq .paths)
        log SUC "Paths:" "${paths[@]}"

    else
        log WARN "Criando novo arquivo de configuração: $config_file"
        config=$(echo {} | jq '.backup_host="furlan-server" | .private_key_file="id_ed25519" | .destiny_dynamic_folder_format="%Y-%m-%d" | .destiny_base_path="" | .max_backup_count=14')
        _hn=".local_host=\"$(hostname)\""
        config=$(echo "$config" | jq "$_hn" | jq ".paths=[]")
        echo "$config" >"$config_file"

        exit 1
    fi
}

last_backup_read() {
    # Checking last backup
    last_backup=$(ssh -i "$private_key_file" "$backup_host" cat "$base_path/last_run.json")
    if [[ $last_backup == {*} ]]; then
        last_run_timestamp=$(echo "$last_backup" | jq '.timestamp' | tr -d '"')
        last_run_success=$(echo "$last_backup" | jq '.success' | tr -d '"')
        log SUC "Last run: $last_run_timestamp Success=$last_run_success"
    else
        last_run_timestamp="1970-01-01 00:00:00"
        last_run_success="false"
        log WARN "Last run not registered"
    fi
}

last_backup_write() {
    local tmp
    tmp=$(mktemp)
    echo "{\"timestamp\":\"$(date +%Y-%m-%dT%H:%M:%S)\", \"success\":$1}" >"$tmp"
    scp -i "$private_key_file" -q "$tmp" "$backup_host:$base_path/last_run.json"
    rm "$tmp"
    if [ $? ]; then
        log SUC "Saved last run"
    else
        log ERR "Last run not saved"
    fi
}

empty() {
    if [ "$1" == "" ] || [ "$1" == "null" ]; then
        return 0
    fi
    return 1
}

do_sync() {
    local source=$1
    local destiny
    destiny="$destiny_base_path/$local_host/$(date "+$destiny_dynamic_folder_format")"
    ssh -i "$private_key_file" "$backup_host" mkdir -p "$destiny"
    log WARN "Sync: $source -> $destiny"
    send_count=0
    send_size=0
    delete_count=0

    while IFS= read -r line; do
        # Get words
        IFS=' ' read -r -a words <<<"$line"
        case "${words[0]}" in
        sending)
            log INFO "Sending incremental file list"
            ;;

        "del.")
            ((delete_count++))
            log WARN "Delete #$delete_count ${words[2]}"
            ;;

        send)
            ((send_count++))
            size="${words[1]}"
            ((send_size += size))
            log INFO "Send #$send_count ($size / $send_size) ${words[2]}"

            ;;

        *)
            if empty "$line"; then
                line=''
            else
                if [[ $line == *error* ]]; then
                    log ERR "$line"
                else
                    log "$line"
                fi
            fi
            ;;
        esac

    done < <(rsync -avz --delete --exclude "*/.Trash-1000/*" --exclude "*/node_modules/*" --exclude "*/lost+found" --copy-links "--out-format=%o %l %n%L" -e "ssh -i $private_key_file" "$source" "$backup_host:$destiny/")

    log SUC "Sent $send_count ($send_size) | Deleted ($delete_count)"
}

delete_old_backups() {
    path="$destiny_base_path/$local_host"
    readarray -t subfolders < <(ssh -i "$private_key_file" "$backup_host" ls -d "$path/*/")
    if [[ "${#subfolders[@]}" -gt $max_backup_count ]]; then
        l=${#subfolders[@]}
        ei=$((l - max_backup_count))
        to_delete=("${subfolders[@]:0:$ei}")
        for folder in "${to_delete[@]}"; do
            result=$(ssh -i "$private_key_file" "$backup_host" rm -r "$folder")
            if empty "$result"; then
                log INFO "Removed old backup folder $folder"
            else
                log ERR "$result"
            fi
        done
    else
        basenames=()

        # Loop through the original array and extract the basenames
        for path in "${subfolders[@]}"; do
            # Use the basename command to get the basename of each item
            filename=$(basename "$path")
            # Add the basename to the new array
            basenames+=("$filename")
        done

        log INFO "${#subfolders[@]} days of backup: ${basenames[*]}"
    fi
}

do_syncs() {
    for p in "${paths[@]}"; do
        do_clean "$p"        
        do_sync "$p"
    done
    delete_old_backups
}

do_clean() {
    if echo "$last_run_timestamp" | grep $(date +%Y-%m-%d); then
        log INFO "Ignoring clean"
    else
        log INFO "Cleaning before backup"
        clean_csharp "$p"
        clean_git "$p"
        clean_python "$p"
    fi
}

ping_host() {
    out=$(ping -c 1 -q -w 5 "$backup_host" 2>&1)
    if [ $? != 0 ]; then
        log ERR "Backup host $backup_host is unreachable"
    fi
    if echo "$out" | grep "0% packet loss"; then
        log INFO "Backup host $backup_host is OK"
        return
    fi
    log ERR "$out"
    exit
}

if empty "$1"; then
    log WARN "Usage: $0 CONFIGURATION_FILE"
    echo '{
    "backup_host": "furlan-server",
    "private_key_file": "id_ed25519",
    "destiny_dynamic_folder_format": "%Y-%m-%d",
    "destiny_base_path": "/home/guionardo/sdb1",
    "local_host": "guionote-debian",
    "paths": [
        "/home/guionardo/dev"
    ]
}'
    exit 1
fi

clean_csharp() {
    if empty "$1"; then 
        return
    fi
    log INFO "Searching dotnet solutions for cleaning before backup"
    while IFS= read -r solution; do
        log INFO "dotnet clean $solution"
        dotnet clean "$solution"
        solution_dir=$(dirname "$solution")
        while IFS= read -r binobj; do
            log INFO " rm $binobj"
            rm -r "$binobj"
        done < <(find "$solution_dir" -type d \( -name 'bin' -o -name 'obj' \))
    done < <(find "$1" -type f -name '*.sln')      
}

clean_git() {
    if empty "$1"; then 
        return
    fi
    log INFO "Searching .git repositories for cleanup"
    oldcw=$(pwd)
    while IFS= read -r git_repo; do
        log INFO "Cleaning .git: $git_repo"
        cd "$git_repo/.."
        git gc
    done < <(find "$1" -type d -name '.git')
    cd "$oldcw"
}

clean_python() {
    if empty "$1"; then 
        return
    fi
    log INFO "Searching python projects for cleanup"
    while IFS= read -r py_cache; do
        log INFO "Removing $py_cache"
        rm -r "$py_cache"        
    done < <(find "$1" -type d -name '__pycache__')
    -exec rm -r {} \;
}

runfile="$0.run"
touch "$runfile"
trap '{ rm -f -- "$runfile"; }' EXIT

read_configuration "$1"

ping_host

# base_path
base_path="$destiny_base_path/$local_host"

# Saving last backup
last_backup_read

do_syncs

last_backup_write true
