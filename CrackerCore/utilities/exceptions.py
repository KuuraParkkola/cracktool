class TryAgain(Exception):
    def __init__(self, msg='The process cannot be completed right now') -> None:
        super().__init__(msg)


class WordSourceEmpty(Exception):
    def __init__(self, msg='The word source has been depleted') -> None:
        super().__init__(msg)
