from __future__ import annotations
from typing import Callable, List, Optional, Set, Union

from CrackerCore.Hasher import Hasher


class Variator:
    def __init__(self) -> None:
        self.__next_variator: Optional[Variator] = None
        self.__hasher: Optional[Hasher] = None

    def use_hasher(self, hasher: Hasher) -> None:
        # Send all outputs to a hasher
        self.__hasher = hasher

    def use_variator(self, variator: Variator) -> None:
        # Send all outputs to another variator
        self.__next_variator = variator

    def _int_then(self, sources: Set[bytes], words: Set[bytes]) -> None:
        # Send outputs to the hasher and onward in the pipeline
        if self.__hasher is not None:
            self.__hasher.check(words)
        if self.__next_variator is not None:
            self.__next_variator.endpoint(sources | words)

    @property
    def endpoint(self) -> Callable[[Set[bytes]], None]:
        raise NotImplementedError
