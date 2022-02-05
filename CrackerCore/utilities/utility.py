from typing import Any, Callable, List, Set, Union


def encoded_arg(source: str) -> bytes:
    try:
        return source.encode('utf8')
    except UnicodeError:
        raise TypeError('All characters should be utf-8 compatible')


def flatten_nested_list(tree: Union[List, str]) -> List[str]:
    if isinstance(tree, str):
        return [tree]
    else:
        new_elems = []
        for elem in tree:
            new_elems.extend(flatten_nested_list(elem))
        return new_elems


def generate_range(start: int, stop: int) -> List[bytes]:
    return [str(v).encode('utf8') for v in range(start, stop+1)]


def generate_sequences(count: int, symbols: bytes) -> List[bytes]:
    sequences = []
    for _ in range(count):
        new_seq = []
        for seq in sequences or [b'']:
            for sym_idx in range(len(symbols)):
                new_seq.append(seq + symbols[sym_idx:sym_idx+1])
        sequences.extend(new_seq)
    return sequences


def select_appender(order: str):
    def postfix_appender(source: bytes, appendix: bytes) -> Set[bytes]:
        return set([source + appendix])
    def prefix_appender(source: bytes, appendix: bytes) -> Set[bytes]:
        return set([appendix + source])
    def both_appender(source: bytes, appendix: bytes) -> Set[bytes]:
        return set([appendix + source, source + appendix])
    
    return postfix_appender if order == 'post' else \
           prefix_appender if order == 'pre' else \
           both_appender if order == 'both' else \
           None

def variable_arg(*arg_type) -> Callable[[str], Any]:
    def converter(args: str) -> Any:
        parsed = []
        for arg_idx in range(len(args)):
            parsed.append(arg_type[arg_idx](args[arg_idx]))
        return tuple(parsed)
    
    return converter
