import logging
from threading import Thread

from CrackerCore.WordSource import WordSource
from CrackerCore.utilities.exceptions import TryAgain, WordSourceEmpty


class Worker:
    def __init__(self, name: str, word_source: WordSource) -> None:
        self.__name = name
        self.__word_source = word_source
        self.__thread = Thread(name=self.__name, target=self.__run)
        self.__active = False

    def __run(self) -> None:
        logging.info('Workloop was started')
        while self.__active:
            try:
                self.__word_source.push(100)
            except TryAgain:
                logging.warning('Failed to push words to the pipeline')
            except WordSourceEmpty:
                logging.info('No more words to process, thread marked for termination')
                self.__active = False
        logging.info('Workloop has terminated')

    def start(self) -> None:
        self.__active = True
        self.__thread.start()

    def stop(self) -> None:
        self.__active = False

class WorkerPool:
    def __init__(self, threads: int, word_source: WordSource) -> None:
        self.__workers = [Worker(f'Worker {w}', word_source) for w in range(1, threads+1)]

    def start(self):
        logging.info('Starting workpool')
        for worker in self.__workers:
            worker.start()

    def stop(self):
        logging.info('Signaling all workers to stop')
        for worker in self.__workers:
            worker.stop()
