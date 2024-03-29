from typing import Callable, List, Set

from CrackerCore.utilities.utility import generate_sequences, select_appender
from CrackerCore.variators.Variator import Variator


class SymbolVariator(Variator):
    def __init__(self, count: int, symbols: bytes, order: str = 'post') -> None:
        super().__init__()
        # Precompute all pre-/postfixes
        self.__symbol_set = generate_sequences(count, symbols)
        # Select the concatenation order
        self.__appender = select_appender(order)

    def __endpoint(self, sources: Set[bytes]) -> None:
        result_set = set()
        # Apply each pre-/postfix
        for source in sources:
            for appendix in self.__symbol_set:
                result_set |= self.__appender(source, appendix)
        self._int_then(sources, result_set)

    @property
    def endpoint(self) -> Callable[[Set[bytes]], None]:
        return self.__endpoint


def build_sym_variator(args: List[str]) -> SymbolVariator:
    # Parse variator arguments and build the variator

    count = int(args[0])
    symbols = b'!@#$%^&*|_-:;"\'.,+?'
    order = 'post'

    for arg in args:
        if arg.startswith('s='):
            symbols = arg[2:].encode('utf8')
        elif arg.startswith('o='):
            order = arg[2:]

    return SymbolVariator(count, symbols, order)