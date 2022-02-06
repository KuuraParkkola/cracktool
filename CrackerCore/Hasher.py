import hashlib
from typing import Dict, List, Set, Tuple

from CrackerCore.HashGroup import HashGroup


class Hasher:
    __algorithms = {
        'sha1': hashlib.sha1
    }

    def __init__(self, algorithm: str) -> None:
        self.__hash = Hasher.__algorithms[algorithm]
        self.__hashes = set()
        self.__group_objs: List[HashGroup] = []
        self.__groups: Dict[bytes, HashGroup] = {}
        self.__recent: bytes = b''

    def hash(self, source: bytes) -> bytes:
        return self.__hash(source).digest()

    def check(self, words: Set[bytes]) -> None:
        # Check a set of guesses against the hashes
        hashes = {self.hash(word) for word in words}

        # If a match was found, take a closer look
        if self.__hashes & hashes:
            for word in words:
                hashed = self.hash(word)
                group = self.__groups.get(hashed, None)
                if group:
                    # Register password match
                    group.add_match(word, hashed)
        if words:
            # Update a recent hashed password for the ui
            self.__recent = words.pop()

    def add_group(self, group: HashGroup) -> None:
        # Add a set of hashes for checking
        self.__group_objs.append(group)
        new_hashes = group.hashes
        self.__hashes |= new_hashes
        for hash in new_hashes:
            self.__groups[hash] = group

    def matches(self) -> Dict[str, Tuple[Tuple[str, str]]]:
        # Return the matches for each hash set
        result_dict = {}
        for hash_group in self.__group_objs:
            result_dict[hash_group.title] = tuple([tuple(i) for i in hash_group.matches.items()])
        return result_dict

    @property
    def recent_word(self) -> str:
        # Return a recently hashed guess
        return self.__recent.decode('utf8')
