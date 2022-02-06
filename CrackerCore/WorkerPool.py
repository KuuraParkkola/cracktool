import logging
from threading import Thread
from typing import Tuple

from CrackerCore.WordSource import WordSource
from CrackerCore.utilities.exceptions import TryAgain, WordSourceEmpty


class Worker:
    def __init__(self, name: str, word_source: WordSource) -> None:
        self.__name = name
        self.__word_source = word_source
        self.__thread = Thread(name=self.__name, target=self.__run)
        self.__active = False
        self.__status = 'Not Started'
        self.__processed = 0

    def __run(self) -> None:
        self.__status = 'Running'
        logging.info('Workloop was started')

        # While running:
        while self.__active:
            try:
                # Make the word source push guesses into the processing pipeline
                self.__word_source.push(100)
                self.__processed += 100
            except TryAgain:
                logging.warning('Failed to push words to the pipeline')
            except WordSourceEmpty:
                logging.info('No more words to process, thread marked for termination')
                self.__active = False
        self.__status = 'Finished'
        logging.info('Workloop has terminated')

    @property
    def name(self) -> str:
        return self.__name

    @property
    def status(self) -> str:
        return self.__status

    @property
    def processed(self) -> str:
        return self.__processed

    def start(self) -> None:
        self.__active = True
        self.__thread.start()

    def stop(self) -> None:
        self.__status = 'Terminating'
        self.__active = False

class WorkerPool:
    def __init__(self, threads: int, word_source: WordSource) -> None:
        # Create a number of workers
        self.__workers = [Worker(f'Worker {w}', word_source) for w in range(1, threads+1)]

    @property
    def workers(self) -> Tuple[Tuple[str, str, str]]:
        # Get some status information from the worker threads
        return ((w.name, w.status, w.processed) for w in self.__workers)

    def start(self):
        logging.info('Starting workpool')
        for worker in self.__workers:
            worker.start()

    def stop(self):
        logging.info('Signaling all workers to stop')
        for worker in self.__workers:
            worker.stop()
