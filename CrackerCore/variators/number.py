from typing import Callable, List, Set, Tuple, Union

from CrackerCore.utilities.utility import generate_sequences, generate_range, select_appender
from CrackerCore.variators.Variator import Variator


class NumberVariator(Variator):
    def __init__(self, mode: str, arg: Union[int, Tuple[int, int]], order: str = 'post') -> None:
        super().__init__()
        self.__value_set = generate_range(arg[0], arg[1]) if mode == 'range' else \
                           generate_sequences(arg, b'1234567890') if mode == 'digits' else []
        self.__appender = select_appender(order)

    def __endpoint(self, sources: Set[bytes]) -> None:
        result_set = set()
        for source in sources:
            for appendix in self.__value_set:
                result_set |= self.__appender(source, appendix)
        self._int_then(result_set)

    @property
    def endpoint(self) -> Callable[[Set[bytes]], None]:
        return self.__endpoint


def build_numr_variator(args: List[str]) -> NumberVariator:
    num_range = tuple([int(v) for v in args[0].split(':')])
    order = 'post'
    if len(args) > 1:
        order = args[1]

    return NumberVariator('range', num_range, order)


def build_numd_variator(args: List[str]) -> NumberVariator:
    digits = int(args[0])
    order = 'post'
    if len(args) > 1:
        order = args[1]

    return NumberVariator('digits', digits, order)
