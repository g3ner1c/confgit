from os import path, walk, chdir, makedirs
import yaml


from .log_util import *

# FILE SYSTEM UTILITIES


# make any given path as input relative to user's home directory
def path_relative_home(raw_path):
    if raw_path[0] == "~":
        return raw_path
    output = path.abspath(raw_path)
    return output.replace(str(path.expanduser("~")), "~")


# make any given path as input absolute path from root directory
def absolute_path(raw_path):
    return path.abspath(path.expanduser(path.expandvars(raw_path)))


# translate origin file path to path of it's complementary file
def path_in_repo(raw_path, config):
    return absolute_path(raw_path).replace(str(path.expanduser("~")), config["repo_dir"])


# load config file to path on input and return parsed yaml
def load_config(config_file_path):
    try:
        with open(config_file_path, 'r') as stream:
            raw_config = yaml.safe_load(stream)
            raw_config["repo_dir"] = absolute_path(raw_config["repo_dir"])
            if raw_config["include"] is not None:
                parsed = []
                for i in raw_config["include"]:
                    parsed.append(path_relative_home(i))
                raw_config["include"] = parsed
            if raw_config["exclude"] is not None:
                parsed = []
                for e in raw_config["exclude"]:
                    parsed.append(path_relative_home(e))
                raw_config["exclude"] = parsed
            return raw_config
    except yaml.YAMLError:
        print_error(f"Yaml parse of {config_file_path} failed")
        exit(1)
    except IOError:
        print_error(f"File {config_file_path} does not exists")
        exit(1)


# save config to yaml file to path on input
def save_config(config, config_file_path):
    with open(config_file_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


# set current working directory to path on input
def set_cwd_to(dir_path):
    chdir(path.realpath(dir_path))


# return list of paths of all files in directory tree with root on path in input
def mine_files(path_to_mine):
    path_to_mine = absolute_path(path_to_mine)
    if path.isfile(path_to_mine):
        return [path_to_mine]
    list_of_files = []
    for root, directories, files in walk(path_to_mine):
        for filename in files:
            list_of_files.append(absolute_path(path.join(root, filename)))
    return list_of_files


# get pair of all registered files in config file in format:
def get_all_registered_files(config):
    registered_files = []
    if config["include"] is None:
        return []
    for fi in config["include"]:
        registered_files.extend(mine_files(fi))
    if config["exclude"] is not None:
        for fe in config["exclude"]:
            for i in mine_files(fe):
                if i in registered_files:
                    registered_files.remove(i)
    return registered_files


# writes over source file to its destination file
def write_file_to_other_file(source_path, destination_path: str):
    makedirs(path.dirname(destination_path), exist_ok=True)
    with open(source_path, "r") as source:
        with open(destination_path, "w") as destination:
            destination.write(source.read())


# Checks is two files has same content
def have_same_content(file_1_path, file_2_path):
    try:
        with open(file_1_path, "r") as f1:
            with open(file_2_path, "r") as f2:
                return f1.read() == f2.read()
    except IOError:
        return False
