from typing import Callable, Dict, List, Set, Tuple
from CrackerCore.utilities.utility import capitalize

from CrackerCore.variators.Variator import Variator


class CapitalVariator(Variator):
    def __init__(self, arg: str) -> None:
        super().__init__()

        if arg == '*':
            self.__endpoint = self.__each_endpoint()
        elif arg == '**':
            self.__endpoint = self.__all_endpoint()
        else:
            self.__endpoint = self.__index_endpoint(arg)

    @staticmethod
    def __int_substitutor_substitutor(source: bytes, symbol: bytes, substitute: bytes) -> Set[bytes]:
        output_set = set()

        # Capitalize each occurence of the symbol
        pos = source.find(symbol)
        while pos > 0:
            new_source = source[0:pos] + substitute + source[pos+1:]
            output_set |= CapitalVariator.__int_substitutor_substitutor(new_source, symbol, substitute)
            output_set.add(new_source)
            pos = source.find(symbol, pos+1)

        return output_set

    @staticmethod
    def __int_substitutor(substitutes: List[Tuple[bytes]], sources: Set[bytes]) -> Set[bytes]:
        output_set = set()

        # Capitalize each occurence of each symbol
        for word in sources:
            for substitute in substitutes:
                output_set |= CapitalVariator.__int_substitutor_substitutor(word, substitute[0], substitute[1])

        return output_set

    def __all_endpoint(self) -> Callable[[Set[bytes]], None]:
        # Build an endpoint to capitalize all combinations
        substitutes = [(s.encode('utf8'), s.upper().encode('utf8')) for s in 'abcdefghijklmnopqrstuvwxyz']
        then = self._int_then

        def endpoint(sources: Set[bytes]) -> None:
            result_set = set()
            # Make one round of capitalizations and for as long as there are letters to capitalize, go over it again
            new_substituted = CapitalVariator.__int_substitutor(sources)
            while len(new_substituted) > 0:
                result_set |= new_substituted
                new_substituted = CapitalVariator.__int_substitutor(substitutes, new_substituted)
            then(sources, result_set)

        return endpoint

    def __each_endpoint(self) -> Callable[[Set[bytes]], None]:
        # Build an endpoint to capitalize each letter individually
        then = self._int_then

        def endpoint(sources: Set[bytes]) -> None:
            result_set = set()
            for word in sources:
                # Go through the letters and capitalize them
                capitalized = {capitalize(word, i) for i in range(len(word))}
                result_set |= capitalized

            then(sources, result_set)

        return endpoint

    def __index_endpoint(self, indices: int) -> Callable[[Set[bytes]], None]:
        # Build an endpoint to capitalize the given indices

        then = self._int_then
        valid = [abs(idx) for idx in indices]

        def endpoint(sources: Set[bytes]) -> None:
            result_set = set()
            for idx in range(len(indices)):
                # Capitalize a character if the index is not greater than the length of the word
                result_set |= {capitalize(word, indices[idx]) for word in sources if len(word) >= valid[idx]}

            # Pass the new word set forward
            then(sources, result_set)

        return endpoint

    @property
    def endpoint(self) -> Callable[[Set[bytes]], None]:
        return self.__endpoint


def build_caps_variator(args: List[str]) -> CapitalVariator:
    # Parse variator arguments and build the variator
    if args[0] in ('*', '**'):
        arg = args[0]
    else:
        arg = [int(a) for a in args]

    return CapitalVariator(arg)
