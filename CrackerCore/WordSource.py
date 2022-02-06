from pathlib import Path
from threading import Lock
from typing import Callable, Optional

from CrackerCore.Hasher import Hasher
from CrackerCore.utilities.exceptions import TryAgain, WordSourceEmpty
from CrackerCore.variators.Variator import Variator


class WordSource:
    def __init__(self, path: Path) -> None:
        self.__variator: Optional[Variator] = None
        self.__hasher: Optional[Hasher] = None
        self.__lock = Lock()

        # Load a dictionary
        with path.open('r') as word_file:
            self.__wordlist = word_file.read().encode('utf8').splitlines()

        self.__wordcount = len(self.__wordlist)
        self.__left = self.__wordcount
        self.__progress = 0

    def push(self, count: int) -> None:
        if self.__left <= 0:
            raise WordSourceEmpty()

        # Load a set of guesses
        batch = set()
        if self.__lock.acquire(blocking=True, timeout=1):
            if count < self.__left:
                batch |= set(self.__wordlist[self.__progress : self.__progress + count])
                self.__progress += count
                self.__left -= count
            else:
                batch |= set(self.__wordlist[self.__progress:])
                self.__left = 0
                self.__progress = self.__wordcount
            self.__lock.release()
        else:
            raise TryAgain('Could not ackquire a lock')
        
        # Push the guesses into the pipeline
        if self.__hasher is not None:
            self.__hasher.check(batch)
        if self.__variator is not None:
            self.__variator.endpoint(batch)

    def use_variator(self, variator: Variator) -> None:
        # Send all outputs to a variator
        self.__variator = variator

    def use_hasher(self, hasher: Hasher) -> None:
        # Send all outputs to a hasher
        self.__hasher = hasher

    @property
    def length(self):
        return self.__wordcount

    @property
    def progress(self):
        return self.__progress

    @property
    def words_left(self) -> int:
        return self.__left
