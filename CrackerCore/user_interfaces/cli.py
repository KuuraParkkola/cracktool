import logging
import sys
from pathlib import Path
from threading import Event
from time import time
from typing import Dict

from CrackerCore.HashGroup import HashGroup
from CrackerCore.Hasher import Hasher
from CrackerCore.WordSource import WordSource
from CrackerCore.WorkerPool import WorkerPool
from CrackerCore.utilities.pipeline import build_pipeline
from CrackerCore.utilities.utility import export_results


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

    start_time = time()
    worker_pool.start()

    try:
        stop = Event()
        while not stop.wait(timeout=5):
            logging.info(f'Running hashes: {word_source.progress} words out of {word_source.length} tested, {word_source.words_left} left. Recent word: {hasher.recent_word}')
            if not word_source.words_left:
                stop.set()
    except KeyboardInterrupt:
        logging.info("Process was aborted")
        worker_pool.stop()

    output_file_name = export_results(config, hasher.matches, time()-start_time)
    logging.info(f'The process has been completed and results stored in file {output_file_name}')
