# Description
This package is a personal tool to manage bibliography and create various annotated pdfs.  
In the actual form it is a bit rigid and not really customizable, this may change if requested.

# Installation
Install [pdf2bib](https://github.com/MicheleCotrufo/pdf2bib) according to `requirements.txt` version.  
Install latex, for example texlive 2022.

# Configuration
Create a configuration file `config.yaml`:
```
BASE_DIR: main workdir where you store pdfs, processing will happend here
SAVE_DIR: where you want your data to be saved
LATEX_INSTALL: latex install path
LATEX_UTILS: latex templates for annotated bibliography
```

# How to use
Right now, you have to put articles you want to process in _$BASE_PATH/raw/read_.  
The pdf name must be separated by `_` and format must be: `year_author.pdf`.  
You can add optional keywords:  `year_author_keyword1_keyword2.pdf`.  
You can add an annotation file with year and author name: `year_author.annot`.  
You can add and ignore folder: _$BASE_PATH/raw/read/ignore_.  
You can force a DOI to an article in a _$BASE_PATH/raw/read/doi.txt_ with format: `year_author doi`.  
Pdf files will be stored in a _$BASE_PATH/sorted_ folder with various orderings.

# Run
Run `bib_management.py` or create your own run file.  
Alternatively, you can run in this order:  
- `save_articles.py`
- `create_bib.py`
- `sort_articles.py`
- `save_keywords.py`
