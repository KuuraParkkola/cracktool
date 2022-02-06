import json
import logging
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Dict

from CrackerCore.user_interfaces.cli import cli
from CrackerCore.utilities.utility import flatten_nested_list, print_pipeline_help

try:
    from CrackerCore.user_interfaces.tui import tui
except ImportError:
    def tui(config: Dict):
        raise ModuleNotFoundError('Cannot use advanced interface, \'Rich\' library is likely not installed')


if __name__ == '__main__':
    #
    # Define commandline arguments
    #
    parser = ArgumentParser(
        prog='cracktool',
        description='Run various password cracking approaches'
    )

    parser.add_argument('-c', '--config', dest='config', metavar='path', type=Path, default=Path.cwd()/'config.json',
                        help='Use a custom config file path')
    parser.add_argument('-g', '--graphical', dest='ui', action='store_const', const=tui, default=cli,
                        help='Use a graphical UI (Rich library required)')
    parser.add_argument('-t', '--threads', metavar='T', type=int, required=False, default=4,
                        help="How many threads to use, defaults to four")
    parser.add_argument('-d', '--dictionary', dest='dict', metavar='id', help="Select the dictionary used, defaults to first available")

    group = parser.add_argument_group('Add variators to the given pipeline')
    group.add_argument('-p', '--pipeline', dest='pipeline', action='append', nargs='*', metavar='V', help='add variators (see formatting help below)')
    group.add_argument('-s', '--source', dest='hash_sources', metavar='indices', help='Define which variators are hash sources (defaults to all). 0 refers to the word source')
    group.add_argument('--sym', dest='pipeline_help', action='append_const', const='sym', help='add symbols: sym $count s=$syms o=$ord')
    group.add_argument('--subs', dest='pipeline_help', action='append_const', const='subs', help='make substitutions: subs s=$syms g=$greedy')
    group.add_argument('--numr', dest='pipeline_help', action='append_const', const='numr', help='add number range: numr $range o=$ord')
    group.add_argument('--numd', dest='pipeline_help', action='append_const', const='numd', help='add digits: numd $count o=$ord')
    group.add_argument('--caps', dest='pipeline_help', action='append_const', const='caps', help='capitalize characters: caps $mode')

    group = parser.add_argument_group('Use approaches')
    group.add_argument('selected_hash_sets', nargs='*', metavar='S', default=[], help='Try to solve the given hash sets as defined in the configuration')
    group.add_argument('--all', action='store_true', dest='all_hash_sets', help="Try to solve all available hashes")

    #
    # Load arguments and configuration
    #
    args = parser.parse_args()

    # Print help for the variator arguments
    if args.pipeline_help:
        print_pipeline_help(args.pipeline_help)
        exit(0)

    with args.config.open('r') as config_file:
        config = json.load(config_file)

    #
    # Parse and validate configuration
    #
    if args.threads > 0:
        config['threads'] = args.threads
    else:
        print('At least one thread is required', sys.stderr)
        exit(-1)

    if args.dict is not None:
        option = list(filter(lambda e: e['key'] == args.dict, config['dictionaries']))
        config['dict'] = config['dictionaries'][0] if not option else option[0]
    else:
        config['dict'] = config['dictionaries'][0]

    if args.selected_hash_sets or args.all_hash_sets:
        config['selected_hash_sets'] = [hg['key'] for hg in config['hash_sets']] if args.all_hash_sets \
            else [hg['key'] for hg in config['hash_sets'] if hg['key'] in args.selected_hash_sets]
    else:
        print('At least one hash set is required', sys.stderr)
        exit(-1)

    #
    # Parse the pipeline
    #
    config['pipeline'] = { 'variators': [] }
    variator_ids = {'sym', 'subs', 'numr', 'numd', 'caps'}

    arg_set = []
    for arg in flatten_nested_list(args.pipeline or []):
        if arg in variator_ids:
            if arg_set: config['pipeline']['variators'].append(arg_set)
            arg_set = [arg]
        else:
            arg_set.append(arg)
    if arg_set: config['pipeline']['variators'].append(arg_set)
    config['pipeline']['hash_sources'] = \
        list(range(len(config['pipeline']['variators']) + 1)) if args.hash_sources is None \
            else [int(s) for s in args.hash_sources]

    #
    # Configure logging
    #
    log_dir = Path.cwd()/'logs'
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    logFormatter = logging.Formatter('%(asctime)s [%(threadName)-9s] %(message)s')
    fileLogger = logging.FileHandler(log_dir/f'cracktool_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    fileLogger.setFormatter(logFormatter)
    logging.getLogger().addHandler(fileLogger)
    logging.getLogger().setLevel(logging.INFO)

    #
    # Launch the application
    #
    args.ui(config)
