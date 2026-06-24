from src.shell import run_shell
import tempfile
import logging
import os

# "{crontab -l}[crontab.txt]"


class OtherFile:
    def __init__(self, filename: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._tmp = None
        self.filename = ''
        self.realname = ''
        if (
            filename.startswith('{')
            and '}' in filename
            and '[' in filename
            and filename.endswith(']')
        ):
            cmd = os.path.expandvars(filename.split('}')[0].replace('{', ''))
            dest = os.path.abspath(
                os.path.expandvars(filename.split('[')[1].replace(']', ''))
            )
            content, ok = run_shell(cmd)
            if ok:
                self._tmp = tempfile.NamedTemporaryFile(
                    prefix=dest, suffix='', delete=True, mode='wb'
                )
                self.filename = self._tmp.name
                self.realname = dest
                self._tmp.write(content.encode('utf-8'))
                self._tmp.flush()
                self.logger.info('Created file %s from %s', dest, cmd)

            else:
                self.logger.warning('Failed creating file %s from %s', dest, cmd)

        else:
            self.filename = os.path.expandvars(filename)
            self.realname = self.filename

        self.exists = os.path.isfile(self.filename)

    def __del__(self):
        if self._tmp:
            self._tmp.close()
