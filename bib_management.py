import os
import subprocess
import argparse
import textwrap
from argparse import RawTextHelpFormatter
from config import read_base_dir

import create_bib
import sort_articles

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
base_dir = read_base_dir(config_path)
path_biblio = os.path.join(base_dir, 'raw', 'read', 'biblio')


DOC = """
---------------------------

Handle the bibliography generation

Command example:
----------------

"""


def get_cmd_line_args():
    parser = argparse.ArgumentParser(
        prog="bib_management.py",
        description=textwrap.dedent(DOC),
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-c", "--use_cache",
        type=int, choices=[0, 1], default=0,
        help="Use cached pdf2bib bibliography result" )
    
    # Create a dict of arguments to pass to the 'main' function
    args = parser.parse_args()
    kwargs = vars(args)
    return kwargs


if __name__ == "__main__":
    inputs = get_cmd_line_args()
    use_cache = inputs['use_cache']

    create_bib.create(os.path.join(base_dir, 'raw', 'read'), use_cache)

    command = ['pybtex-format', '--abbreviate-names', os.path.join(path_biblio, 'biblio.bib'),
               os.path.join(path_biblio, 'biblio_a.txt')]
    subprocess.run(command)
    command = ['pybtex-format', '--abbreviate-names', os.path.join(path_biblio, 'biblio.bib'),
               os.path.join(path_biblio, 'biblio_a.html')]
    subprocess.run(command)
    command = ['pybtex-format', '--abbreviate-names', os.path.join(path_biblio, 'biblio.bib'),
               os.path.join(path_biblio, 'biblio_a.tex')]
    subprocess.run(command)
    command = ['pybtex-format', os.path.join(path_biblio, 'biblio.bib'),
               os.path.join(path_biblio, 'biblio.txt')]
    subprocess.run(command)
    command = ['pybtex-format', os.path.join(path_biblio, 'biblio.bib'),
               os.path.join(path_biblio, 'biblio.html')]
    subprocess.run(command)
    command = ['pybtex-format', os.path.join(path_biblio, 'biblio.bib'),
               os.path.join(path_biblio, 'biblio.tex')]
    subprocess.run(command)
    
    sort_articles.sort_articles(base_dir, path_biblio)
