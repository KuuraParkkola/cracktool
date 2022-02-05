from typing import List, Set, Union


def capitalize(source: bytes, idx: int) -> bytes:
    nxt = idx+1
    return source[:idx] + source[idx:nxt if nxt else None].upper() + (source[nxt:] if nxt else b'')


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
