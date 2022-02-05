import logging
import sys
from pathlib import Path
from threading import Timer, Event
from typing import Dict

from CrackerCore.HashGroup import HashGroup
from CrackerCore.Hasher import Hasher
from CrackerCore.WordSource import WordSource
from CrackerCore.WorkerPool import WorkerPool
from CrackerCore.utilities.pipeline import build_pipeline


def cli(config: Dict) -> None:
    logFormatter = logging.Formatter('[%(threadName)-9s] %(message)s')
    streamLogger = logging.StreamHandler(sys.stdout)
    streamLogger.setFormatter(logFormatter)
    logging.getLogger().addHandler(streamLogger)
    logging.getLogger().setLevel(logging.INFO)
    
    hasher = Hasher('sha1')
    logging.info(f'Created a hasher')

    for hash_set in filter(lambda e: e['key'] in config['selected_hash_sets'], config['hash_sets']):
        new_hash_set = HashGroup(hash_set['title'], Path(hash_set['path']))
        new_hash_set.notify_on_match(lambda set_name, pw, pw_hash: logging.info(f'A match was registered in {set_name}: {pw} - {pw_hash}'))
        hasher.add_group(new_hash_set)
        logging.info(f'Enabled hash set {new_hash_set.title}')

    word_source = WordSource(Path(config['dict']['path']))
    logging.info(f'Created word source {config["dict"]["key"]} with {word_source.length} words')

    pipeline = build_pipeline(word_source, config['pipeline'], hasher)
    logging.info(f'Created a pipeline with arguments {config["pipeline"]["variators"]}')

    worker_pool = WorkerPool(config['threads'], pipeline)
    logging.info(f'Created a worker pool with {config["threads"]} workers')

    stop = Event()
    def log_update():
        while not stop.wait(timeout=10):
            logging.info(f'Running hashes: {word_source.progress} words out of {word_source.length} tested, {word_source.words_left} left')
    
    def on_finish():
        logging.info(f'Word source has been cleared and the program fill stop shortly')
        stop.set()
    word_source.notify_on_finished(on_finish)

    logging.info('Setup progress tracker and exit handling')

    worker_pool.start()
    log_update()

    logging.info('The process has finished')
