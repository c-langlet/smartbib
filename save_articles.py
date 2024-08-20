import os
import shutil
import datetime
from config import read_base_dir, read_save_dir

config_path = './config.yaml'
base_dir = read_base_dir(config_path)
raw_dir = os.path.join(base_dir, 'raw')
keywords_dir = os.path.join(base_dir, 'sorted', 'keywords')
save_dir = read_save_dir(config_path)


def save_raw(raw_dir, save_dir):
    raw_save_dir = os.path.join(save_dir, 'save')
    os.makedirs(raw_save_dir, exist_ok=True)
    dirs = sorted(os.listdir(raw_save_dir))
    if len(dirs) > 1:
        for d in dirs[:-2]:
            os.remove(os.path.join(raw_save_dir, d))
    # Create archive
    date = str(datetime.date.today())
    output_filename = os.path.join(raw_save_dir, 'raw_' + date)
    shutil.make_archive(output_filename, 'zip', raw_dir)


if __name__ == '__main__':
    save_raw(raw_dir, save_dir)
