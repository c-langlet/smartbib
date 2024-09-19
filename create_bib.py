import os
import glob
import pdf2bib
import pdf2doi
import json
from config import read_base_dir

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
base_dir = read_base_dir(config_path)
default_path = os.path.join(base_dir, 'raw', 'read')
#default_path = os.path.join(base_dir, 'raw')
path_biblio = os.path.join(default_path, 'biblio')


def add_doi(filename):
    with open(filename, 'r') as file:
        for line in file.readlines():
            identifier, doi = line.split(' ')
            regex = os.path.join(os.path.dirname(filename), identifier.strip('.pdf') + '*.pdf')
            try:
                path = glob.glob(regex)[0] 
                pdf2doi.add_found_identifier_to_metadata(path, doi)
            except IndexError:
                print('Pdf file not found for identifier:', identifier)


def generate_bib(path):
    pdf2bib.config.set('verbose', False)
    result = pdf2bib.pdf2bib(path)
    return result


def get_id(entry, suffix=''):
    try:
        name = entry['metadata']['author'][0]['family'].replace(' ', '')
        year = str(entry['metadata']['year'])
        identifier = name + year + suffix
        return identifier
    except IndexError:
        with open(os.path.join(base_dir, 'logs', 'get_id.log'), 'a+') as file:
            file.write(entry)


#Not really used at this time, more of a safety function
def increment_id(identifier):
    print('Converting', identifier)
    for i, c in enumerate(identifier):
        if c.isdigit():
            idx = i
            break

    name, date = identifier[:idx], identifier[idx:]
    if len(date) == 4:
        identifier = name + date + 'a'
    else:
        identifier = name + date + chr(ord(date[5]) + 1)
    print('into', identifier)
    return identifier


def reformat_bib_entry(bib, identifier):
    #Replace bad characters for bibtex format
    bib = bib.replace("ejournal", "journal")
    bib = bib.replace(",,", ",")

    #Reformat month
    biblist = bib.split(',')
    for b in biblist:
        if '\n\tmonth = {' in b:
            month = b.replace('\n\tmonth = {', '').replace('}', '')
            if len(month) == 1:
                old_month = '\n\tmonth = {'
                new_month = '\n\tmonth = {0'
                bib = bib.replace(old_month, new_month)

    #Replace identifer 
    fst = bib.split(',', 1)[0]
    old_id = fst.split('{', 1)[1]
    bib = bib.replace(old_id, identifier)

    return bib


def get_annot(path):
    dirname = os.path.dirname(path)
    basename = os.path.basename(os.path.splitext(path)[0]).split('_')
    basename[1] = basename[1].split('--')[0]
    annot_regex = '_'.join(basename[:2]) + '*.annot'
    try:
        annot_file = glob.glob(os.path.join(dirname, annot_regex))[0]
        with open(annot_file, 'r') as file:
            annot = file.readline().strip('\n')
        return annot
    except IndexError:
        #print('No annot file for:', path)
        return ''


def add_annot(annot, bib):
    biblist = bib.split(',')
    biblist[-1] = biblist[-1].replace('\n}', '')
    biblist.append('\n\tannote = {' + annot + '}\n}')
    return ','.join(biblist)


def write_bib(result, path_to_write):
    with open(os.path.join(path_to_write, 'biblio.bib'), 'w') as file:
        known_ids = []
        for entry in result:
            try:
                identifier = get_id(entry)
                path = entry['path']
                year = os.path.basename(path).split('_')[0]
                if len(year) == 5:
                    identifier = get_id(entry, year[4])
                if identifier in known_ids:
                    identifier = increment_id(identifier)
                bib = reformat_bib_entry(entry['bibtex'], identifier)
                file.write(bib)
                file.write('\n')
                known_ids.append(identifier)
            except TypeError:
                print('TypeError:', entry['path'])
                print('You should try to add doi manually')


def write_annoted_bib(result, path_to_write):
    with open(os.path.join(path_to_write, 'annoted_biblio.bib'), 'w') as file:
        known_ids = []
        for entry in result:
            try:
                identifier = get_id(entry)
                path = entry['path']
                year = os.path.basename(path).split('_')[0]
                if len(year) == 5:
                    identifier = get_id(entry, year[4])
                if (identifier in known_ids):
                    identifier = increment_id(identifier)
                bib = reformat_bib_entry(entry['bibtex'], identifier)
                annot = get_annot(path)
                annoted_bib = add_annot(annot, bib)
                file.write(annoted_bib)
                file.write('\n')
                known_ids.append(identifier)
            except TypeError:
                print('TypeError:', entry['path'])
                print('You should try to add doi manually')


def create(path, use_cache):
    if use_cache == 1:
        print('Skiping biblio generation for:', path)
        with open(os.path.join(path_biblio, 'cached_result.json'), 'r') as file:
            result = json.load(file)
    else:
        print('Generating biblio for:', path, 'in', path_biblio)
        os.makedirs(path_biblio, exist_ok=True)
        if os.path.exists(os.path.join(path, 'doi.txt')):
            add_doi(os.path.join(path, 'doi.txt'))
        result = generate_bib(path)
        with open(os.path.join(path_biblio, 'cached_result.json'), 'w') as file:
             json.dump(result, file, indent=2)
    write_bib(result, path_biblio)
    write_annoted_bib(result, path_biblio)


if __name__ == "__main__":
    create(default_path, 0)
