from dataclasses import dataclass


@dataclass
class PreRunScript:
    """Script executado antes do sync, utilizado para rodar algum comando específico no host.
    Opções: com label
    [Last Backup]cat $HOME/others/backup_datetime.txt

    sem label
    uptime -h
    """

    script: str
    label: str = ""
    command: str = ""

    def __post_init__(self):
        if "[" in self.script and "]" in self.script:
            self.label = self.script.split("]")[0].replace("[", "").strip()
            self.command = self.script.split("]")[1]
        else:
            self.command, self.label = self.script, self.script
