import os
import shutil
import json
import config
import datetime
import glob

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
base_dir = config.read_base_dir(config_path)
latex_install = config.read_latex_install(config_path)
latex_utils_dir = config.read_latex_utils_dir(config_path)
path_biblio = os.path.join(base_dir, 'raw', 'read', 'biblio')


def clean(base_dir):
    if os.path.exists(os.path.join(base_dir, 'sorted')):
        shutil.rmtree(os.path.join(base_dir, 'sorted'))


def sort(base_dir):
    read_dir = os.path.join(base_dir, 'raw/read')
    articles = [f for f in os.listdir(read_dir) if os.path.splitext(f)[1] == '.pdf']
    for article in articles:
        path_article = os.path.join(read_dir, article)
        filename, ext = os.path.splitext(article)
        parsed_filename = filename.split("_", 2)
        keywords = ''
        if len(parsed_filename) == 2:
            date, authors = parsed_filename
            #author_filename = author + '_' + date + '.pdf'
        else:
            date, authors, keywords = parsed_filename
            #author_filename = author + '_' + date + '_' + keywords + '.pdf'

        for author in authors.split('--'):
            author_dir = os.path.join(base_dir, 'sorted', 'authors', author)
            sort_author = os.path.join(author_dir, article)
            os.makedirs(author_dir, exist_ok=True)
            os.symlink(path_article, sort_author)

        date_dir = os.path.join(base_dir, 'sorted', 'dates', date)
        sort_date = os.path.join(date_dir, article)
        os.makedirs(date_dir, exist_ok=True)
        os.symlink(path_article, sort_date)

        if keywords != '':
            keywords_list = keywords.split("_")
            for keyword in keywords_list:
                keyword_dir = os.path.join(base_dir, 'sorted', 'keywords', keyword)
                os.makedirs(keyword_dir, exist_ok=True)
                sort_keyword = os.path.join(keyword_dir, article)
                os.symlink(path_article, sort_keyword)


def get_id(filename):
    basename = os.path.splitext(filename)[0].split('_')
    return basename[1].split('--')[0] + basename[0]


def get_id_in_cache(path_pdf, cache_path):
    with open(cache_path, 'r') as file:
        result = json.load(file)
    for entry in result:
        if entry['path'] == path_pdf:
            name = entry['metadata']['author'][0]['family'].replace(' ', '')
            year = str(entry['metadata']['year'])
            identifier = name + year
            break
    return identifier


def make_bib_from_path(base_dir, keywords_dir, path_biblio):
    base_bib = os.path.join(path_biblio, 'annoted_biblio.bib')
    if os.path.exists(base_bib):
        with open(base_bib, 'r') as file:
            bib = file.read()
        dict_bib = {}
        for entry in bib.split('@article{')[1:]:
            identifier = entry.split(',', 1)[0]
            dict_bib[identifier] = '@article{' + entry
        keywords = os.listdir(keywords_dir)
        for keyword in keywords:
            keyword_dir = os.path.join(keywords_dir, keyword)
            keyword_bib = []
            pdffiles = [f for f in os.listdir(keyword_dir) if os.path.splitext(f)[1] == '.pdf']
            if os.path.exists(os.path.join(keyword_dir, keyword + '.pdf')):
                pdffiles.remove(keyword + '.pdf')
            for pdffile in pdffiles:
                try:
                    identifier = get_id(pdffile)
                    keyword_bib.append(dict_bib[identifier])
                except KeyError:
                    try:
                       pdf_path = os.path.join(base_dir, 'raw', 'read', pdffile)
                       cache_path = os.path.join(path_biblio, 'cached_result.json')
                       identifier = get_id_in_cache(pdf_path, cache_path)
                       keyword_bib.append(dict_bib[identifier])
                    except UnboundLocalError:
                        print('No identifier:', identifier)
            with open(os.path.join(keyword_dir, keyword + '.bib'), 'w') as file:
                file.write(''.join(keyword_bib))


def make_bib(base_dir, path_biblio):
    keywords_dir = os.path.join(base_dir, 'sorted', 'keywords')
    make_bib_from_path(base_dir, keywords_dir, path_biblio)
    authors_dir = os.path.join(base_dir, 'sorted', 'authors')
    make_bib_from_path(base_dir, authors_dir, path_biblio)
    dates_dir = os.path.join(base_dir, 'sorted', 'dates')
    make_bib_from_path(base_dir, dates_dir, path_biblio)


def make_keyword_pdf(base_dir, path, keyword):
    tmpdir = os.path.join(path, keyword, 'tmp')
    os.makedirs(tmpdir, exist_ok=True)
    print(keyword)
    with open(os.path.join(latex_utils_dir, 'template.tex'), 'r') as file:
        template = file.read()
    template = template.replace('Keyword', 'Keyword: ' + keyword)
    template = template.replace('annoted_biblio', keyword + '.bib')
    texfile  = os.path.join(tmpdir, keyword + '.tex')
    with open(texfile, 'w') as file:
        file.write(template)
    shutil.copy(os.path.join(path, keyword, keyword + '.bib'), tmpdir)
    shutil.copy(os.path.join(latex_utils_dir, 'plain-annot-year.bst'), tmpdir)
    os.chdir(tmpdir)
    os.system(f"{latex_install}pdflatex {keyword}.tex")
    os.system(f"{latex_install}bibtex {keyword}.aux")
    os.system(f"{latex_install}pdflatex {keyword}.tex")
    os.system(f"{latex_install}pdflatex {keyword}.tex")
    if os.path.exists(os.path.join('../', keyword + '.pdf')):
        os.remove(os.path.join('../', keyword + '.pdf'))
    shutil.move(keyword + '.pdf', '../')
    shutil.rmtree(tmpdir)


def make_pdf(base_dir):
    path = os.path.join(base_dir, 'sorted', 'keywords')
    for keyword in os.listdir(path):
        make_keyword_pdf(base_dir, path, keyword)
    path = os.path.join(base_dir, 'sorted', 'authors')
    for author in os.listdir(path):
        make_keyword_pdf(base_dir, path, author)
    path = os.path.join(base_dir, 'sorted', 'dates')
    for date in os.listdir(path):
        make_keyword_pdf(base_dir, path, date)


def make_weekly_report(base_dir, path_biblio):
    annots = glob.glob(os.path.join(base_dir, 'raw', 'read', '*.annot'))
    now = datetime.datetime.now()
    #now = datetime.datetime(2024, 2, 18, 22, 00, 0, 0)
    current_time = now.strftime("%Y-W%W")
    path = os.path.join(base_dir, 'weekly_reports')
    tmp_path = os.path.join(path, current_time)
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    os.makedirs(tmp_path, exist_ok=True)
    for annot in annots:
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(annot))
        delta = now - creation_time
        if creation_time <= now and delta.days <= 7:
            print(annot, os.path.splitext(annot)[0] + '*.pdf')
            pdf = glob.glob(os.path.splitext(annot)[0] + '*.pdf')[0]
            print(pdf)
            sym = os.path.join(tmp_path, os.path.basename(pdf))
            os.symlink(pdf, sym)
    make_bib_from_path(base_dir, path, path_biblio)
    make_keyword_pdf(base_dir, path, current_time)


def sort_articles(base_dir, path_biblio):
    print(base_dir)
    clean(base_dir)
    sort(base_dir)
    make_bib(base_dir, path_biblio)
    make_pdf(base_dir)


if __name__ == "__main__":
    sort_articles(base_dir, path_biblio)
    make_weekly_report(base_dir, path_biblio)
