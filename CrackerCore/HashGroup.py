from pathlib import Path
from typing import Callable, Dict, List, Optional, Set


class HashGroup:
    def __init__(self, title: str, path: Path):
        self.__title = title

        # Load the hashes from a file
        with path.open('r') as word_file:
            hex_hashes = word_file.read().splitlines()

        self.__hashes = {bytes.fromhex(hex_hash) for hex_hash in hex_hashes}
        self.__matches: Dict[str, str] = {}
        self.__on_match: Optional[Callable[[str, str, str], None]] = None

    def add_match(self, match: bytes, match_hash: bytes) -> None:
        # Register a match
        self.__matches[match.decode('utf8')] = match_hash.hex()
        self.__on_match(self.__title, match.decode('utf8'), match_hash.hex())

    def notify_on_match(self, callback: Callable[[str, str, str], None]):
        # Callback to call when a match is made
        self.__on_match = callback

    @property
    def title(self) -> str:
        return self.__title

    @property
    def matches(self) -> Dict[str, str]:
        return self.__matches

    @property
    def passwords(self) -> List[str]:
        return self.__matches.keys()

    @property
    def hashes(self) -> Set[bytes]:
        return self.__hashes
