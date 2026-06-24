import logging
import os

# "{crontab -l}[crontab.txt]"


class OtherFolder:
    def __init__(self, foldername: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._tmp = None
        self.foldername = ''
        self.realfoldername = ''

        self.foldername = os.path.expandvars(foldername)
        self.realfoldername = self.foldername

        self.exists = os.path.isdir(self.foldername)

    def __del__(self):
        if self._tmp:
            self._tmp.close()
