import logging
from multiprocessing import Event
from pathlib import Path
from time import time
from typing import Dict, List

from rich.columns import Columns
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from CrackerCore.HashGroup import HashGroup
from CrackerCore.Hasher import Hasher
from CrackerCore.utilities.pipeline import build_pipeline
from CrackerCore.utilities.utility import export_results
from CrackerCore.WordSource import WordSource
from CrackerCore.WorkerPool import WorkerPool


def build_recent_words_table(words: List[str]):
    columns = Columns(words, equal=True, expand=True, width=20)
    return columns


def build_worker_table(worker_pool: WorkerPool):
    worker_table = Table()
    worker_table.add_column("Worker", width=10)
    worker_table.add_column("Status", width=38)
    worker_table.add_column("Processed", width=12)

    statuses = {
        'Not Started': 'orange',
        'Terminating': 'orange',
        'Running': 'cyan',
        'Finished': 'green',
    }

    for worker in worker_pool.workers:
        color = statuses[worker[1]]
        worker_table.add_row(f'[{color}]{worker[0]}', f'[{color}]{worker[1]}', f'{worker[2]}')

    return worker_table


def build_match_table(hasher: Hasher):
    match_table = Table()

    matches = hasher.matches()
    for hash_set in matches:
        match_table.add_column(hash_set)
    match_table.add_row(*['\n'.join([match[0] for match in matches[hash_set]]) for hash_set in matches])

    return match_table


def build_ui(progress, wordlist, worker_table, match_table):
    progress_grid = Table.grid()
    progress_grid.add_row(progress)
    progress_grid.add_row(worker_table)

    progress_panel = Panel.fit(progress_grid, title="Progress", border_style="green", padding=(1, 1), width=70)
    words_panel = Panel.fit(wordlist, title="Recent Words", border_style="yellow", padding=(1, 1), width=70)
    match_panel = Panel.fit(match_table, title="Matches", border_style="cyan", padding=(1, 1), width=70)

    main_layout = Table.grid()
    main_layout.add_row(progress_panel)
    main_layout.add_row(words_panel)
    main_layout.add_row(match_panel)

    return main_layout


def tui(config: Dict) -> None:
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

    progress = Progress()
    main_task = progress.add_task("Words processed:", total=word_source.length)

    start_time = time()
    worker_pool.start()

    recent_words = ['' for _ in range(9)]
    dyn_ui = lambda: build_ui(progress, build_recent_words_table(recent_words), build_worker_table(worker_pool), build_match_table(hasher))
    with Live(dyn_ui(), refresh_per_second=1) as live:
        try:
            ui = dyn_ui()
            event = Event()
            while not event.wait(timeout=1):
                recent_words.insert(0, hasher.recent_word)
                recent_words.pop(-1)
                
                progress.update(main_task, completed=word_source.progress)
                live.update(ui)
                ui = dyn_ui()

                if not word_source.words_left:
                    progress.update(main_task, completed=word_source.length)
                    event.set()

        except KeyboardInterrupt:
            logging.info("Process was aborted")
            worker_pool.stop()

    output_file_name = export_results(config, hasher.matches(), time()-start_time)
    logging.info(f'The process has been completed and results stored in file {output_file_name}')
