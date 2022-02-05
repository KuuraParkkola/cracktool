from typing import Callable, Dict, List, Set, Tuple

from CrackerCore.variators.Variator import Variator


class SubstitutionVariator(Variator):
    __substitutionTable: Dict[str, Tuple[bytes, bytes]] = {
        '$': (b's', b'$'),
        '@': (b'a', b'@'),
        '!': (b'i', b'!'),
        '1': (b'i', b'1'),
        '3': (b'e', b'3'),
        '4': (b'a', b'4'),
        '5': (b's', b'5'),
        '6': (b'g', b'6'),
        '7': (b't', b'7'),
        '8': (b'b', b'8'),
        '9': (b'g', b'9'),
        '0': (b'o', b'0'),
    }

    def __init__(self, symbols: str, greedy: bool = False) -> None:
        self.__substitutes = [self.__substitutionTable[s] for s in symbols]
        self.__greedy = greedy

    @staticmethod
    def __int_default_substitutor_substitutor(source: bytes, symbol: bytes, substitute: bytes) -> Set[bytes]:
        output_set = set()

        pos = source.find(symbol)
        while pos > 0:
            new_source = source[0:pos] + substitute + source[pos+1:]
            output_set |= SubstitutionVariator.__int_default_substitutor_substitutor(new_source, symbol, substitute)
            output_set.add(new_source)
            pos = source.find(symbol, pos+1)

        return output_set

    def __int_default_substitutor(self, sources: Set[bytes]) -> Set[bytes]:
        output_set = set()

        for word in sources:
            for substitute in self.__substitutes:
                output_set |= SubstitutionVariator.__int_default_substitutor_substitutor(word, substitute[0], substitute[1])

        return output_set

    def __default_endpoint(self, sources: Set[bytes]) -> None:
        result_set = set()
        new_substituted = self.__int_default_substitutor(sources)
        while len(new_substituted) > 0:
            result_set |= new_substituted
            new_substituted = self.__int_default_substitutor(new_substituted)
        self._int_then(result_set)

    def __int_greedy_substitutor(self, sources: Set[bytes]) -> Set[bytes]:
        output_set = set()

        for word in sources:
            for substitute in self.__substitutes:
                symbol = substitute[0]
                if symbol in word:
                    output_set.add(word.replace(symbol, substitute[1]))

        return output_set

    def __greedy_endpoint(self, sources: Set[bytes]) -> None:
        result_set = set()
        new_substituted = self.__int_greedy_substitutor(sources)
        while len(new_substituted) > 0:
            result_set |= new_substituted
            new_substituted = self.__int_greedy_substitutor(new_substituted)
        self._int_then(result_set)

    @property
    def endpoint(self) -> Callable[[Set[bytes]], None]:
        return self.__greedy_endpoint if self.__greedy else self.__default_endpoint


def build_subs_variator(args: List[str]) -> SubstitutionVariator:
    symbols = b'$@!013456789'
    greedy = False

    for arg in args:
        if arg.startswith('s='):
            symbols = arg[2:].encode('utf8')
        elif arg.startswith('g='):
            greedy = True if arg[2:] == 't' else False

    return SubstitutionVariator(symbols, greedy)
