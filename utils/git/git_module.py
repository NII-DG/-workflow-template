import json
import os
from ..common import common
from datalad import api

def exec_git_status():
    """execute 'git status' commands

    RETURN
    ---------------
    Returns output result

    EXCEPTION
    ---------------

    """
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git status')
    result = stdout.decode('utf-8')
    return result

def exec_git_annex_whereis():
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git annex whereis --json', False)
    result = stdout.decode('utf-8')
    return result

def git_annex_add(path:str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git annex add {}'.format(path), False)
    result = stdout.decode('utf-8')
    return result

def git_add(path:str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git add {}'.format(path), False)
    result = stdout.decode('utf-8')
    return result

def git_commmit(msg:str):
    os.chdir(os.environ['HOME'])
    stdout, stderr, rt = common.exec_subprocess('git commit -m "{}"'.format(msg), False)
    result = stdout.decode('utf-8')
    return result

def get_conflict_filepaths() -> list[str]:
    """Get conflict paths in Changes not staged for commit from git status

    Returns:
        list: conflict filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    conflict_filepaths = list[str]()
    is_not_staged = False
    for l in lines:
        if 'Changes not staged for commit:' in l:
            is_not_staged = True
            continue
        if 'both modified' in l and is_not_staged:
            # get conflict filepath
            path = l.split(' ')[4]
            conflict_filepaths.append(path)
    return conflict_filepaths

def get_delete_filepaths() -> list[str]:
    """Get delete file paths in Changes not staged for commit from git status

    Returns:
        list: delete filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    delete_filepaths = list[str]()
    is_not_staged = False
    for l in lines:
        if 'Changes not staged for commit:' in l:
            is_not_staged = True
            continue
        if 'deleted' in l and is_not_staged:
            # get conflict filepath
            path = l.split(' ')[4]
            delete_filepaths.append(path)
    return delete_filepaths

def get_annex_content_file_paht_list()->list[str]:
    """Get git-annex content filepaths

    Returns:
        list: git-annex content filepaths
    """
    result = exec_git_annex_whereis()
    data_list = result.split("\n")
    print(data_list)
    annex_path_list = list[str]()
    data_list = data_list[:-1]
    for data in data_list:
        data_json = json.loads(data)
        annex_path_list.append(data_json['file'])
    return annex_path_list

def get_remote_annex_variant_path(conflict_paths : list[str])-> list[str]:
    """Get git-annex vatiants filepaths

    Returns:
        list: git-annex vatiants filepaths
    """
    result = exec_git_status()
    lines = result.split('\n')
    remote_variant_paths = list[str]()
    for l in lines:
        if 'new file' in l:
            path = l.split(' ')[4]
            for conflict_path in conflict_paths:
                dirpath = os.path.dirname(conflict_path)
                filename_no_extension = os.path.splitext(os.path.basename(conflict_path))[0]
                target_path = '{}/{}.variant-'.format(dirpath, filename_no_extension)
                if path.startswith(target_path):
                    remote_variant_paths.append(path)
    return remote_variant_paths