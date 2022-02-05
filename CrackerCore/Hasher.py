import hashlib
from typing import Dict, Set

from CrackerCore.HashGroup import HashGroup


class Hasher:
    __algorithms = {
        'sha1': hashlib.sha1
    }

    def __init__(self, algorithm: str) -> None:
        self.__hash = Hasher.__algorithms[algorithm]
        self.__hashes = set()
        self.__groups: Dict[bytes, HashGroup] = {}

    def hash(self, source: bytes) -> bytes:
        return self.__hash(source).digest()

    def check(self, words: Set[bytes]) -> None:
        hashes = {self.hash(word) for word in words}
        if self.__hashes & hashes:
            for word in words:
                hashed = self.hash(word)
                group = self.__groups.get(hashed, None)
                if group:
                    group.add_match(word, hashed)

    def add_group(self, group: HashGroup) -> None:
        new_hashes = group.hashes
        self.__hashes |= new_hashes
        for hash in new_hashes:
            self.__groups[hash] = group
