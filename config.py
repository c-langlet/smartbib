import yaml

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def read_base_dir(file_path):
    config = read_yaml(file_path)
    return config['BASE_DIR']

def read_save_dir(file_path):
    config = read_yaml(file_path)
    return config['SAVE_DIR']
    
def read_latex_install(file_path):
    config = read_yaml(file_path)
    return config['LATEX_INSTALL']

def read_latex_utils_dir(file_path):
    config = read_yaml(file_path)
    return config['LATEX_UTILS']
