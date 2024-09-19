import os
import shutil
from config import read_base_dir, read_save_dir

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
base_dir = read_base_dir(config_path)
raw_dir = os.path.join(base_dir, 'raw')
keywords_dir = os.path.join(base_dir, 'sorted', 'keywords')
save_dir = read_save_dir(config_path)


def save_keywords(keywords_dir, save_dir):
    os.makedirs(os.path.join(save_dir, 'keywords'), exist_ok=True)
    keywords = os.listdir(keywords_dir)
    for keyword in keywords:
        pdf = os.path.join(keywords_dir, keyword, keyword + '.pdf')
        output_pdf = os.path.join(save_dir, 'keywords', keyword + '.pdf')
        shutil.copy(pdf, output_pdf)


if __name__ == '__main__':
    if os.path.exists(keywords_dir):
        save_keywords(keywords_dir, save_dir)
